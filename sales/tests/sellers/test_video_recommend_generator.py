import pytest
from unittest.mock import MagicMock, patch
import json

from sellers.video_recommend_generator import VideoRecommendationGenerator


@pytest.fixture
def recommendation_generator():
    """Fixture to create a VideoRecommendationGenerator instance with mocked clients."""
    with patch("google.genai.Client"), patch("google.cloud.storage.Client"):
        generator = VideoRecommendationGenerator(
            gemini_api_key="test-api-key", bucket_name="test-bucket"
        )
        yield generator


@pytest.fixture
def sample_analysis_results():
    """Create sample video analysis results for testing."""
    return {
        "objects": [
            {"entity": "soda", "confidence": 0.95, "instances": []},
            {"entity": "chips", "confidence": 0.88, "instances": []},
            {"entity": "candy", "confidence": 0.75, "instances": []},
        ],
        "labels": [
            {"description": "grocery", "confidence": 0.92},
            {"description": "retail", "confidence": 0.85},
        ],
        "text": [
            {"text": "SALE", "confidence": 0.98},
            {"text": "50% OFF", "confidence": 0.94},
        ],
        "logos": [
            {"description": "CocaCola", "confidence": 0.99},
            {"description": "Pepsi", "confidence": 0.97},
        ],
        "vertical_distribution": {
            "distribution_by_level": {
                "Nivel Superior": {
                    "objects": {"soda": 5, "chips": 2},
                    "total_objects": 7,
                    "percentage": 35.0,
                },
                "Nivel Medio": {
                    "objects": {"candy": 5, "chocolate": 3},
                    "total_objects": 8,
                    "percentage": 40.0,
                },
                "Nivel Inferior": {
                    "objects": {"water": 3, "juice": 2},
                    "total_objects": 5,
                    "percentage": 25.0,
                },
            },
            "metrics": {
                "highest_density_level": {"level": "Nivel Medio", "count": 8},
                "lowest_density_level": {
                    "level": "Nivel Inferior",
                    "count": 5,
                },
                "distribution_evenness": {
                    "value": 0.85,
                    "interpretation": "Valor cercano a 1 indica distribución uniforme, cercano a 0 indica concentración en ciertos niveles",
                },
            },
        },
    }


def test_init(recommendation_generator):
    """Test the initialization of VideoRecommendationGenerator."""
    assert recommendation_generator.bucket_name == "test-bucket"
    assert recommendation_generator.storage_client is not None
    assert recommendation_generator.gemini_client is not None


def test_read_analysis_invalid_path(recommendation_generator):
    """Test reading analysis with invalid video path."""
    with pytest.raises(ValueError):
        recommendation_generator.read_analysis_from_gcs("invalid/path.mp4")


@patch("google.cloud.storage.Client")
def test_read_analysis_invalid_gcs_uri(
    mock_storage_client, recommendation_generator
):
    """Test reading analysis with invalid GCS URI format."""
    # Test with a GCS URI that doesn't have enough path components
    with pytest.raises(ValueError, match="Invalid GCS URI format"):
        recommendation_generator.read_analysis_from_gcs(
            "gs://test-bucket/file.mp4"
        )


def test_create_recommendation_prompt(
    recommendation_generator, sample_analysis_results
):
    """Test creation of recommendation prompt."""
    prompt = recommendation_generator._create_recommendation_prompt(
        sample_analysis_results
    )

    # Check that the prompt contains essential elements
    assert "Objetos principales detectados" in prompt
    assert "soda (0.95)" in prompt
    assert "chips (0.88)" in prompt

    assert "Categorías/etiquetas" in prompt
    assert "grocery (0.92)" in prompt

    assert "Texto detectado" in prompt
    assert "SALE" in prompt
    assert "50% OFF" in prompt

    assert "Logos reconocidos" in prompt
    assert "CocaCola" in prompt
    assert "Pepsi" in prompt

    assert "DISTRIBUCIÓN VERTICAL DE PRODUCTOS" in prompt
    assert "Nivel Superior" in prompt
    assert "Nivel Medio" in prompt
    assert "Nivel Inferior" in prompt

    # Check that the prompt includes recommendation areas
    assert "Optimización de la distribución vertical" in prompt
    assert "Mejoras en la presentación visual" in prompt
    assert "Estrategias para aumentar ventas" in prompt
    assert "Sugerencias de productos complementarios" in prompt


def test_create_recommendation_prompt_no_vertical_data(
    recommendation_generator, sample_analysis_results
):
    """Test creating a recommendation prompt without vertical distribution data."""
    # Create a copy of sample results without vertical distribution
    analysis_without_vertical = sample_analysis_results.copy()
    del analysis_without_vertical["vertical_distribution"]

    # Call the method
    prompt = recommendation_generator._create_recommendation_prompt(
        analysis_without_vertical
    )

    # Check that the prompt still contains essential elements
    assert "Objetos principales detectados" in prompt
    assert "Categorías/etiquetas" in prompt
    assert "Texto detectado" in prompt
    assert "Logos reconocidos" in prompt

    # Vertical distribution information should be missing
    assert "DISTRIBUCIÓN VERTICAL DE PRODUCTOS" not in prompt


def test_create_recommendation_prompt_empty_data(recommendation_generator):
    """Test creating a recommendation prompt with empty data fields."""
    empty_analysis = {"objects": [], "labels": [], "text": [], "logos": []}

    # Call the method
    prompt = recommendation_generator._create_recommendation_prompt(
        empty_analysis
    )

    # Check that the prompt handles empty data correctly
    assert "Objetos principales detectados: " in prompt
    assert "Categorías/etiquetas: " in prompt
    assert "Texto detectado: Ninguno" in prompt
    assert "Logos reconocidos: Ninguno" in prompt


def test_full_recommendation_workflow(
    recommendation_generator, sample_analysis_results
):
    """Test the full workflow from reading analysis to generating recommendations."""
    # Mock the storage client
    bucket_mock = MagicMock()
    blob_mock = MagicMock()
    recommendation_generator.storage_client.bucket.return_value = bucket_mock
    bucket_mock.blob.return_value = blob_mock
    blob_mock.download_as_string.return_value = json.dumps(
        sample_analysis_results
    ).encode('utf-8')

    # Mock the Gemini client
    with patch.object(
        recommendation_generator, 'gemini_client'
    ) as mock_gemini:
        response_mock = MagicMock()
        response_mock.text = "Final recommendation text."
        mock_gemini.models.generate_content.return_value = response_mock

        # Run the workflow
        video_path = "gs://test-bucket/videos/retail/test-video.mp4"
        analysis = recommendation_generator.read_analysis_from_gcs(video_path)
        recommendations = recommendation_generator.generate_recommendations(
            analysis
        )

        # Verify results
        assert analysis == sample_analysis_results
        assert recommendations == "Final recommendation text."
        mock_gemini.models.generate_content.assert_called_once()
