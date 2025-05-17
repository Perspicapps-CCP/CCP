from google.cloud import videointelligence
from google.cloud import storage
import json
import numpy as np
from collections import defaultdict


class VideoAnalyzer:
    """
    Class for analyzing retail shelf videos using Video Intelligence API.
    """

    def __init__(self, bucket_name: str):
        """
        Initialize the video analyzer.
        """
        self.bucket_name = bucket_name

        # Set up Video Intelligence client
        self.video_client = videointelligence.VideoIntelligenceServiceClient()

        # Set up Storage client
        self.storage_client = storage.Client()

    def analyze_video(self, video_path: str, features=None):
        """
        Analyze a video using Video Intelligence API.

        Args:
            video_path (str): Local path or GCS URI of the video.
            features (list, optional): List of features to analyze.

        Returns:
            dict: Analysis results.
        """
        if features is None:
            features = [
                videointelligence.Feature.OBJECT_TRACKING,
                videointelligence.Feature.LABEL_DETECTION,
                videointelligence.Feature.TEXT_DETECTION,
                videointelligence.Feature.LOGO_RECOGNITION,
            ]

        # Configure request
        request = videointelligence.AnnotateVideoRequest(
            input_uri=video_path,
            features=features,
        )

        print("Starting video analysis with Video Intelligence API...")
        operation = self.video_client.annotate_video(request=request)
        print("Processing video...")

        # Wait for analysis to complete
        result = operation.result(timeout=300)

        # Process results
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
        """Process object detection annotations."""
        objects = []

        for obj in object_annotations:
            object_info = {
                "entity": obj.entity.description,
                "confidence": round(obj.confidence, 2),
                "instances": [],
            }

            # Only take key frames to simplify
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
        """Process label/category annotations."""
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
        """Process detected text annotations."""
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
        """Process recognized logo annotations."""
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
        Analyze the vertical distribution of products on the shelf.

        Args:
            object_annotations: Detected object annotations.
            shelf_levels (int): Number of levels to divide the shelf into.

        Returns:
            dict: Vertical distribution analysis by levels.
        """
        # Define shelf levels (top, middle, bottom)
        level_boundaries = np.linspace(0, 1, shelf_levels + 1)

        # Dictionary to store objects by level
        objects_by_level = {i: [] for i in range(shelf_levels)}

        # Analyze each object and assign it to a level
        for obj in object_annotations:
            # Get average vertical position of each object
            vertical_positions = []

            for frame in obj.frames:
                if frame.normalized_bounding_box:
                    box = frame.normalized_bounding_box
                    # Calculate vertical midpoint of the object
                    mid_y = (box.top + box.bottom) / 2
                    vertical_positions.append(mid_y)

            if vertical_positions:
                # Calculate average vertical position of the object throughout the video
                avg_vertical_position = sum(vertical_positions) / len(
                    vertical_positions
                )

                # Determine which shelf level it belongs to
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

        # Count objects by type at each level
        level_distribution = {}

        for level, objects in objects_by_level.items():
            # Define level names
            level_names = {
                0: "Nivel Superior",
                1: "Nivel Medio",
                2: "Nivel Inferior",
            }

            level_name = level_names.get(level, f"Nivel {level+1}")

            # Count objects by type
            object_counts = defaultdict(int)
            for obj in objects:
                object_counts[obj["entity"]] += 1

            # Store results
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

        # Add metrics and conclusions
        result = {
            "distribution_by_level": level_distribution,
            "metrics": self._calculate_vertical_distribution_metrics(
                level_distribution
            ),
        }

        return result

    def _calculate_vertical_distribution_metrics(self, level_distribution):
        """
        Calculate metrics for vertical distribution.

        Args:
            level_distribution (dict): Object distribution by level.

        Returns:
            dict: Vertical distribution metrics.
        """
        metrics = {}

        # Calculate level with highest product density
        max_density_level = max(
            level_distribution.items(), key=lambda x: x[1]["total_objects"]
        )
        metrics["highest_density_level"] = {
            "level": max_density_level[0],
            "count": max_density_level[1]["total_objects"],
        }

        # Calculate level with lowest product density
        min_density_level = min(
            level_distribution.items(), key=lambda x: x[1]["total_objects"]
        )
        metrics["lowest_density_level"] = {
            "level": min_density_level[0],
            "count": min_density_level[1]["total_objects"],
        }

        # Calculate distribution index (how even the distribution is)
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
                ),  # Normalized between 0 and 1
                "interpretation": "Valor cercano a 1 indica distribución uniforme, cercano a 0 indica concentración en ciertos niveles",
            }
        else:
            metrics["distribution_evenness"] = {
                "value": 0,
                "interpretation": "No hay suficientes objetos para calcular la uniformidad",
            }

        return metrics

    def save_analysis_to_gcs(self, analysis_results, video_path: str) -> str:
        """
        Save analysis results to GCS.

        Args:
            analysis_results (dict): Analysis results.
            video_path (str): Path of the analyzed video.

        Returns:
            str: GCS URI of the saved analysis file.
        """

        # Extract filename from video_path
        if video_path.startswith("gs://"):
            filename = video_path.split("/")[-1]
            video_folder = "/".join(video_path.split("/")[:-1])
        else:
            raise ValueError("Invalid video path. Must start with 'gs://'.")

        analysis_filename = f"analysis_{filename}.json"
        analysis_path = f"{video_folder}/{analysis_filename}"

        # Remove gs:// and bucket name to get the blob path
        if analysis_path.startswith(f"gs://{self.bucket_name}/"):
            blob_path = analysis_path[len(f"gs://{self.bucket_name}/") :]
        else:
            # Ensure we have a valid blob path
            blob_path = analysis_path.replace("gs://", "").split("/", 1)[1]

        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(blob_path)

        blob.upload_from_string(
            json.dumps(analysis_results, ensure_ascii=False, indent=2),
            content_type="application/json",
        )

        print(f"Analysis saved to {analysis_path}")
        return analysis_path
