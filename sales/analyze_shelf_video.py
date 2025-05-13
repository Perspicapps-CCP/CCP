import os
from google import genai
from google.genai import types
from google.cloud import videointelligence
from google.cloud import storage
import json
from datetime import datetime
import numpy as np
from collections import defaultdict


class ShelfAnalyzer:
    """
    Clase para analizar videos de estanterías y generar recomendaciones comerciales
    utilizando Video Intelligence API y Gemini.
    """

    def __init__(self, project_id, gemini_api_key, bucket_name=None):
        """
        Inicializa el analizador de estanterías.

        Args:
            project_id (str): ID del proyecto de Google Cloud.
            gemini_api_key (str): API key para Gemini.
            bucket_name (str, opcional): Nombre del bucket de GCS para almacenar videos.
        """
        self.project_id = project_id
        self.bucket_name = bucket_name or f"{project_id}-shelf-videos"

        # Configurar cliente de Video Intelligence
        self.video_client = videointelligence.VideoIntelligenceServiceClient()

        # Configurar cliente de Storage
        self.storage_client = storage.Client(project=project_id)

        # Asegurarse de que el bucket existe
        self._ensure_bucket_exists()

        # Configurar Gemini
        self.gemini_model = genai.Client(api_key=gemini_api_key)
        # self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')

    def _ensure_bucket_exists(self):
        """Crea el bucket de GCS si no existe."""
        try:
            if not self.storage_client.lookup_bucket(self.bucket_name):
                self.storage_client.create_bucket(self.bucket_name)
                print(f"Bucket {self.bucket_name} creado correctamente.")
            else:
                print(f"Bucket {self.bucket_name} ya existe.")
        except Exception as e:
            print(f"Error creando/verificando bucket: {e}")

    def upload_video_to_gcs(self, local_path):
        """
        Sube un video a GCS.

        Args:
            local_path (str): Ruta local del archivo de video.

        Returns:
            str: URI de GCS del video.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(local_path)
        gcs_path = f"videos/{timestamp}_{filename}"

        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)

        gcs_uri = f"gs://{self.bucket_name}/{gcs_path}"
        print(f"Video subido a {gcs_uri}")
        return gcs_uri

    def analyze_video(self, video_path, features=None):
        """
        Analiza un video usando Video Intelligence API.

        Args:
            video_path (str): Ruta local o URI de GCS del video.
            features (list, opcional): Lista de características a analizar.

        Returns:
            dict: Resultados del análisis.
        """
        if features is None:
            features = [
                videointelligence.Feature.OBJECT_TRACKING,
                videointelligence.Feature.LABEL_DETECTION,
                videointelligence.Feature.TEXT_DETECTION,
                videointelligence.Feature.LOGO_RECOGNITION,
            ]

        # Si es una ruta local, subir a GCS primero
        if not video_path.startswith("gs://"):
            video_path = self.upload_video_to_gcs(video_path)

        # Configurar solicitud
        request = videointelligence.AnnotateVideoRequest(
            input_uri=video_path,
            features=features,
        )

        print("Iniciando análisis de video con Video Intelligence API...")
        operation = self.video_client.annotate_video(request=request)
        print("Procesando video...")

        # Esperar a que termine el análisis
        result = operation.result(timeout=300)

        # Procesar resultados
        annotation_results = result.annotation_results[0]

        analysis_results = {
            "objects": self._process_object_annotations(
                annotation_results.object_annotations
            ),
            "labels": self._process_label_annotations(
                annotation_results.segment_label_annotations
            ),
            "text": self._process_text_annotations(
                annotation_results.text_annotations
            ),
            "logos": self._process_logo_annotations(
                annotation_results.logo_recognition_annotations
            ),
            "vertical_distribution": self.analyze_vertical_distribution(
                annotation_results.object_annotations
            ),
        }

        return analysis_results

    def _process_object_annotations(self, object_annotations):
        """Procesa anotaciones de objetos detectados."""
        objects = []

        for obj in object_annotations:
            object_info = {
                "entity": obj.entity.description,
                "confidence": round(obj.confidence, 2),
                "instances": [],
            }

            # Tomar solo los frames clave para simplificar
            if obj.frames:
                keyframes = (
                    [obj.frames[0], obj.frames[-1]]
                    if len(obj.frames) > 1
                    else [obj.frames[0]]
                )

                for frame in keyframes:
                    if frame.normalized_bounding_box:
                        box = frame.normalized_bounding_box
                        position = {
                            "time_offset": frame.time_offset.total_seconds(),
                            "box": {
                                "left": round(box.left, 2),
                                "top": round(box.top, 2),
                                "right": round(box.right, 2),
                                "bottom": round(box.bottom, 2),
                            },
                        }
                        object_info["instances"].append(position)

            objects.append(object_info)

        return objects

    def _process_label_annotations(self, label_annotations):
        """Procesa anotaciones de etiquetas/categorías."""
        labels = []

        for label in label_annotations:
            label_info = {
                "description": label.entity.description,
                "confidence": (
                    round(label.segments[0].confidence, 2)
                    if label.segments
                    else 0
                ),
            }
            labels.append(label_info)

        return labels

    def _process_text_annotations(self, text_annotations):
        """Procesa anotaciones de texto detectado."""
        texts = []

        for text in text_annotations:
            text_info = {
                "text": text.text,
                "confidence": (
                    round(text.segments[0].confidence, 2)
                    if text.segments
                    else 0
                ),
            }
            texts.append(text_info)

        return texts

    def _process_logo_annotations(self, logo_annotations):
        """Procesa anotaciones de logos reconocidos."""
        logos = []

        for logo in logo_annotations:
            logo_info = {
                "description": logo.entity.description,
                "confidence": (
                    round(logo.tracks[0].confidence, 2) if logo.tracks else 0
                ),
            }
            logos.append(logo_info)

        return logos

    def analyze_vertical_distribution(
        self, object_annotations, shelf_levels=3
    ):
        """
        Analiza la distribución vertical de productos en la estantería.

        Args:
            object_annotations: Anotaciones de objetos detectados.
            shelf_levels (int): Número de niveles para dividir la estantería.

        Returns:
            dict: Análisis de distribución vertical por niveles.
        """
        # Definir niveles de estantería (superior, medio, inferior)
        level_boundaries = np.linspace(0, 1, shelf_levels + 1)

        # Diccionario para almacenar objetos por nivel
        objects_by_level = {i: [] for i in range(shelf_levels)}

        # Analizar cada objeto y asignarlo a un nivel
        for obj in object_annotations:
            # Obtener posición vertical media de cada objeto
            vertical_positions = []

            for frame in obj.frames:
                if frame.normalized_bounding_box:
                    box = frame.normalized_bounding_box
                    # Calcular punto medio vertical del objeto
                    mid_y = (box.top + box.bottom) / 2
                    vertical_positions.append(mid_y)

            if vertical_positions:
                # Calcular posición vertical media del objeto a lo largo del video
                avg_vertical_position = sum(vertical_positions) / len(
                    vertical_positions
                )

                # Determinar el nivel de estantería al que pertenece
                for level in range(shelf_levels):
                    if (
                        level_boundaries[level]
                        <= avg_vertical_position
                        < level_boundaries[level + 1]
                    ):
                        objects_by_level[level].append(
                            {
                                "entity": obj.entity.description,
                                "confidence": round(obj.confidence, 2),
                                "position": avg_vertical_position,
                            }
                        )
                        break

        # Contar objetos por tipo en cada nivel
        level_distribution = {}

        for level, objects in objects_by_level.items():
            # Definir nombres de niveles
            level_names = {
                0: "Nivel Superior",
                1: "Nivel Medio" if shelf_levels == 3 else f"Nivel {level+1}",
                2: "Nivel Inferior",
            }

            level_name = level_names.get(level, f"Nivel {level+1}")

            # Contar objetos por tipo
            object_counts = defaultdict(int)
            for obj in objects:
                object_counts[obj["entity"]] += 1

            # Almacenar resultados
            level_distribution[level_name] = {
                "objects": dict(object_counts),
                "total_objects": len(objects),
                "percentage": (
                    round(
                        len(objects)
                        / sum(len(objs) for objs in objects_by_level.values())
                        * 100,
                        2,
                    )
                    if sum(len(objs) for objs in objects_by_level.values())
                    > 0
                    else 0
                ),
            }

        # Agregar métricas y conclusiones
        result = {
            "distribution_by_level": level_distribution,
            "metrics": self._calculate_vertical_distribution_metrics(
                level_distribution
            ),
        }

        return result

    def _calculate_vertical_distribution_metrics(self, level_distribution):
        """
        Calcula métricas para la distribución vertical.

        Args:
            level_distribution (dict): Distribución de objetos por nivel.

        Returns:
            dict: Métricas de distribución vertical.
        """
        metrics = {}

        # Calcular nivel con mayor densidad de productos
        max_density_level = max(
            level_distribution.items(), key=lambda x: x[1]["total_objects"]
        )
        metrics["highest_density_level"] = {
            "level": max_density_level[0],
            "count": max_density_level[1]["total_objects"],
        }

        # Calcular nivel con menor densidad de productos
        min_density_level = min(
            level_distribution.items(), key=lambda x: x[1]["total_objects"]
        )
        metrics["lowest_density_level"] = {
            "level": min_density_level[0],
            "count": min_density_level[1]["total_objects"],
        }

        # Calcular índice de distribución (qué tan equitativa es la distribución)
        counts = [
            data["total_objects"] for data in level_distribution.values()
        ]
        if sum(counts) > 0:
            avg_count = sum(counts) / len(counts)
            variance = sum(
                (count - avg_count) ** 2 for count in counts
            ) / len(counts)
            metrics["distribution_evenness"] = {
                "value": round(
                    1 - (variance / (avg_count**2 + 1)), 2
                ),  # Normalizado entre 0 y 1
                "interpretation": "Valor cercano a 1 indica distribución uniforme, cercano a 0 indica concentración en ciertos niveles",
            }
        else:
            metrics["distribution_evenness"] = {
                "value": 0,
                "interpretation": "No hay suficientes objetos para calcular la uniformidad",
            }

        return metrics

    def generate_recommendations(self, analysis_results):
        """
        Genera recomendaciones basadas en el análisis usando Gemini.

        Args:
            analysis_results (dict): Resultados del análisis de Video Intelligence.

        Returns:
            dict: Recomendaciones generadas.
        """
        # Formatear los resultados del análisis para Gemini
        prompt = self._create_recommendation_prompt(analysis_results)

        # Generar recomendaciones con Gemini
        response = self.gemini_model.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=2800, temperature=0.1
            ),
        )

        return {"error_parsing": True, "raw_response": response.text}

    def _create_recommendation_prompt(self, analysis_results):
        """Crea un prompt para Gemini basado en los resultados del análisis."""
        # Extraer información relevante
        top_objects = sorted(
            analysis_results["objects"],
            key=lambda x: x["confidence"],
            reverse=True,
        )[:10]

        top_labels = sorted(
            analysis_results["labels"],
            key=lambda x: x["confidence"],
            reverse=True,
        )[:10]

        detected_text = [t["text"] for t in analysis_results["text"]]
        detected_logos = [l["description"] for l in analysis_results["logos"]]

        # Obtener información de distribución vertical
        vertical_info = ""
        if "vertical_distribution" in analysis_results:
            vertical_data = analysis_results["vertical_distribution"]
            vertical_info = "DISTRIBUCIÓN VERTICAL DE PRODUCTOS:\n"

            # Información por nivel
            for level_name, level_data in vertical_data[
                "distribution_by_level"
            ].items():
                vertical_info += f"- {level_name}: {level_data['total_objects']} productos ({level_data['percentage']}%)\n"
                top_products = sorted(
                    level_data["objects"].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:3]
                if top_products:
                    vertical_info += f"  Productos principales: {', '.join([f'{p[0]} ({p[1]})' for p in top_products])}\n"

            # Métricas relevantes
            metrics = vertical_data["metrics"]
            vertical_info += f"- Nivel más denso: {metrics['highest_density_level']['level']} ({metrics['highest_density_level']['count']} productos)\n"
            vertical_info += f"- Uniformidad de distribución: {metrics['distribution_evenness']['value']} ({metrics['distribution_evenness']['interpretation']})\n"

        # Crear prompt
        prompt = f"""
        Actúa como un consultor experto en retail que analiza estanterías de tiendas.
        
        Basado en el siguiente análisis de video de una estantería, genera recomendaciones 
        específicas para mejorar la presentación, organización y estrategia de ventas.
        
        ANÁLISIS DEL VIDEO:
        - Objetos principales detectados: {", ".join([f"{obj['entity']} ({obj['confidence']})" for obj in top_objects])}
        - Categorías/etiquetas: {", ".join([f"{label['description']} ({label['confidence']})" for label in top_labels])}
        - Texto detectado: {", ".join(detected_text) if detected_text else "Ninguno"}
        - Logos reconocidos: {", ".join(detected_logos) if detected_logos else "Ninguno"}
        
        {vertical_info}
        
        Genera un análisis detallado y recomendaciones que incluyan:
        1. Optimización de la distribución vertical (qué productos deberían ir en cada nivel según principios de merchandising)
        2. Mejoras en la presentación visual y organización
        3. Estrategias para aumentar ventas basadas en la distribución actual
        
        Se conciso, máximo 5 párrafos.
        """

        return prompt

    def _extract_json_from_text(self, text):
        """Extrae el contenido JSON de un texto."""
        start = text.find("{")
        end = text.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("No se encontró contenido JSON en el texto")

        return text[start:end]

    def process_shelf_video(self, video_path):
        """
        Procesa un video de estantería y genera recomendaciones.

        Args:
            video_path (str): Ruta local o URI de GCS del video.

        Returns:
            dict: Recomendaciones generadas.
        """
        # 1. Analizar el video
        analysis_results = self.analyze_video(video_path)

        # 2. Generar recomendaciones
        recommendations = self.generate_recommendations(analysis_results)

        # 3. Guardar resultados (opcional)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = (
            os.path.basename(video_path)
            if not video_path.startswith("gs://")
            else video_path.split("/")[-1]
        )
        result_path = f"resultados_{timestamp}_{filename}.json"

        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "video_path": video_path,
                    "analysis_results": analysis_results,
                    "recommendations": recommendations,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(f"Resultados guardados en {result_path}")

        return recommendations


if __name__ == "__main__":
    PROJECT_ID = "ccp-perspicapps"
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

    analyzer = ShelfAnalyzer(
        project_id=PROJECT_ID,
        gemini_api_key=GEMINI_API_KEY,
        bucket_name="ccp-files-storage",
    )

    video_path = "/home/tamino/Descargas/videoplayback.mp4"
    recommendations = analyzer.process_shelf_video(video_path)

    print("\nRecomendaciones generadas:")
    print(json.dumps(recommendations, indent=2, ensure_ascii=False))
