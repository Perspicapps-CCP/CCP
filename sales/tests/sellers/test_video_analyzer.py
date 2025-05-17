import pytest
from unittest.mock import MagicMock, patch
import json
from google.cloud import videointelligence

from sellers.video_analyzer import VideoAnalyzer



@pytest.fixture
def video_analyzer():
    """Fixture to create a VideoAnalyzer instance with mocked clients."""
    with patch("google.cloud.videointelligence.VideoIntelligenceServiceClient"), \
         patch("google.cloud.storage.Client"):
        analyzer = VideoAnalyzer(bucket_name="test-bucket")
        yield analyzer


@pytest.fixture
def sample_object_annotations():
    """Create sample object annotations for testing."""
    # Create mock object annotations
    obj1 = MagicMock()
    obj1.entity.description = "soda"
    obj1.confidence = 0.95
    
    # Create frames for object 1
    frame1 = MagicMock()
    frame1.normalized_bounding_box.left = 0.1
    frame1.normalized_bounding_box.top = 0.2
    frame1.normalized_bounding_box.right = 0.3
    frame1.normalized_bounding_box.bottom = 0.4
    
    frame2 = MagicMock()
    frame2.normalized_bounding_box.left = 0.15
    frame2.normalized_bounding_box.top = 0.25
    frame2.normalized_bounding_box.right = 0.35
    frame2.normalized_bounding_box.bottom = 0.45
    
    obj1.frames = [frame1, frame2]
    
    # Create another object annotation
    obj2 = MagicMock()
    obj2.entity.description = "chips"
    obj2.confidence = 0.88
    
    # Create frame for object 2
    frame3 = MagicMock()
    frame3.normalized_bounding_box.left = 0.6
    frame3.normalized_bounding_box.top = 0.7
    frame3.normalized_bounding_box.right = 0.8
    frame3.normalized_bounding_box.bottom = 0.9
    
    obj2.frames = [frame3]
    
    return [obj1, obj2]


@pytest.fixture
def sample_label_annotations():
    """Create sample label annotations for testing."""
    label1 = MagicMock()
    label1.entity.description = "grocery"
    segment1 = MagicMock()
    segment1.confidence = 0.92
    label1.segments = [segment1]
    
    label2 = MagicMock()
    label2.entity.description = "retail"
    segment2 = MagicMock()
    segment2.confidence = 0.85
    label2.segments = [segment2]
    
    return [label1, label2]


@pytest.fixture
def sample_text_annotations():
    """Create sample text annotations for testing."""
    text1 = MagicMock()
    text1.text = "SALE"
    segment1 = MagicMock()
    segment1.confidence = 0.98
    text1.segments = [segment1]
    
    text2 = MagicMock()
    text2.text = "50% OFF"
    segment2 = MagicMock()
    segment2.confidence = 0.94
    text2.segments = [segment2]
    
    return [text1, text2]


@pytest.fixture
def sample_logo_annotations():
    """Create sample logo annotations for testing."""
    logo1 = MagicMock()
    logo1.entity.description = "CocaCola"
    track1 = MagicMock()
    track1.confidence = 0.99
    logo1.tracks = [track1]
    
    logo2 = MagicMock()
    logo2.entity.description = "Pepsi"
    track2 = MagicMock()
    track2.confidence = 0.97
    logo2.tracks = [track2]
    
    return [logo1, logo2]


@pytest.fixture
def mock_annotation_result(sample_object_annotations, sample_label_annotations, 
                          sample_text_annotations, sample_logo_annotations):
    """Create a mock annotation result."""
    result = MagicMock()
    annotation_result = MagicMock()
    annotation_result.object_annotations = sample_object_annotations
    annotation_result.segment_label_annotations = sample_label_annotations
    annotation_result.text_annotations = sample_text_annotations
    annotation_result.logo_recognition_annotations = sample_logo_annotations
    result.annotation_results = [annotation_result]
    return result


def test_init(video_analyzer):
    """Test the initialization of VideoAnalyzer."""
    assert video_analyzer.bucket_name == "test-bucket"
    assert video_analyzer.video_client is not None
    assert video_analyzer.storage_client is not None


def test_process_object_annotations(video_analyzer, sample_object_annotations):
    """Test processing of object annotations."""
    processed = video_analyzer._process_object_annotations(sample_object_annotations)
    
    assert len(processed) == 2
    assert processed[0]["entity"] == "soda"
    assert processed[0]["confidence"] == 0.95
    assert len(processed[0]["instances"]) == 2  # Should have two key frames
    
    assert processed[1]["entity"] == "chips"
    assert processed[1]["confidence"] == 0.88
    assert len(processed[1]["instances"]) == 1  # Should have one key frame


def test_process_label_annotations(video_analyzer, sample_label_annotations):
    """Test processing of label annotations."""
    processed = video_analyzer._process_label_annotations(sample_label_annotations)
    
    assert len(processed) == 2
    assert processed[0]["description"] == "grocery"
    assert processed[0]["confidence"] == 0.92
    
    assert processed[1]["description"] == "retail"
    assert processed[1]["confidence"] == 0.85


def test_process_text_annotations(video_analyzer, sample_text_annotations):
    """Test processing of text annotations."""
    processed = video_analyzer._process_text_annotations(sample_text_annotations)
    
    assert len(processed) == 2
    assert processed[0]["text"] == "SALE"
    assert processed[0]["confidence"] == 0.98
    
    assert processed[1]["text"] == "50% OFF"
    assert processed[1]["confidence"] == 0.94


def test_process_logo_annotations(video_analyzer, sample_logo_annotations):
    """Test processing of logo annotations."""
    processed = video_analyzer._process_logo_annotations(sample_logo_annotations)
    
    assert len(processed) == 2
    assert processed[0]["description"] == "CocaCola"
    assert processed[0]["confidence"] == 0.99
    
    assert processed[1]["description"] == "Pepsi"
    assert processed[1]["confidence"] == 0.97


def test_analyze_vertical_distribution(video_analyzer, sample_object_annotations):
    """Test analysis of vertical distribution."""
    distribution = video_analyzer.analyze_vertical_distribution(sample_object_annotations)
    
    assert "distribution_by_level" in distribution
    assert "metrics" in distribution
    
    levels = distribution["distribution_by_level"]
    assert "Nivel Superior" in levels
    assert "Nivel Medio" in levels
    assert "Nivel Inferior" in levels
    
    metrics = distribution["metrics"]
    assert "highest_density_level" in metrics
    assert "lowest_density_level" in metrics
    assert "distribution_evenness" in metrics


def test_calculate_vertical_distribution_metrics(video_analyzer):
    """Test calculation of vertical distribution metrics."""
    # Mock level distribution
    level_distribution = {
        "Nivel Superior": {"total_objects": 10, "objects": {"soda": 5, "chips": 5}},
        "Nivel Medio": {"total_objects": 5, "objects": {"candy": 5}},
        "Nivel Inferior": {"total_objects": 15, "objects": {"water": 8, "juice": 7}}
    }
    
    metrics = video_analyzer._calculate_vertical_distribution_metrics(level_distribution)
    
    assert metrics["highest_density_level"]["level"] == "Nivel Inferior"
    assert metrics["highest_density_level"]["count"] == 15
    
    assert metrics["lowest_density_level"]["level"] == "Nivel Medio"
    assert metrics["lowest_density_level"]["count"] == 5
    
    assert "distribution_evenness" in metrics
    assert 0 <= metrics["distribution_evenness"]["value"] <= 1


@patch("google.cloud.videointelligence.VideoIntelligenceServiceClient")
def test_analyze_video(mock_video_client, video_analyzer, mock_annotation_result):
    """Test analysis of a video."""
    # Set up the mock
    operation_mock = MagicMock()
    operation_mock.result.return_value = mock_annotation_result
    video_analyzer.video_client.annotate_video.return_value = operation_mock
    
    # Test the analyze_video method
    results = video_analyzer.analyze_video("gs://test-bucket/test-video.mp4")
    
    # Verify the results
    assert "objects" in results
    assert "labels" in results
    assert "text" in results
    assert "logos" in results
    assert "vertical_distribution" in results
    
    # Check that the API was called with the correct parameters
    video_analyzer.video_client.annotate_video.assert_called_once()
    call_args = video_analyzer.video_client.annotate_video.call_args[1]
    assert call_args["request"].input_uri == "gs://test-bucket/test-video.mp4"
    assert videointelligence.Feature.OBJECT_TRACKING in call_args["request"].features


@patch("google.cloud.storage.Client")
def test_save_analysis_to_gcs(mock_storage_client, video_analyzer):
    """Test saving analysis results to GCS."""
    # Mock the storage client and bucket
    bucket_mock = MagicMock()
    blob_mock = MagicMock()
    bucket_mock.blob.return_value = blob_mock
    video_analyzer.storage_client.bucket.return_value = bucket_mock
    
    # Test data
    analysis_results = {"test": "data"}
    video_path = "gs://test-bucket/videos/test-video.mp4"
    
    # Call the method
    result_path = video_analyzer.save_analysis_to_gcs(analysis_results, video_path)
    
    # Verify the result
    assert result_path == "gs://test-bucket/videos/analysis_test-video.mp4.json"
    
    # Check that the storage client was used correctly
    video_analyzer.storage_client.bucket.assert_called_once_with("test-bucket")
    bucket_mock.blob.assert_called_once_with("videos/analysis_test-video.mp4.json")
    blob_mock.upload_from_string.assert_called_once()
    # Check the JSON was formatted correctly
    assert json.loads(blob_mock.upload_from_string.call_args[0][0]) == {"test": "data"}


def test_save_analysis_invalid_path(video_analyzer):
    """Test saving analysis with invalid video path."""
    with pytest.raises(ValueError):
        video_analyzer.save_analysis_to_gcs({"test": "data"}, "invalid/path.mp4")


@patch("google.cloud.videointelligence.VideoIntelligenceServiceClient")
def test_analyze_video_with_custom_features(mock_video_client, video_analyzer, mock_annotation_result):
    """Test analysis of a video with custom features."""
    # Set up the mock
    operation_mock = MagicMock()
    operation_mock.result.return_value = mock_annotation_result
    video_analyzer.video_client.annotate_video.return_value = operation_mock
    
    # Custom features
    custom_features = [videointelligence.Feature.LABEL_DETECTION]
    
    # Test the analyze_video method with custom features
    video_analyzer.analyze_video("gs://test-bucket/test-video.mp4", features=custom_features)
    
    # Check that the API was called with the correct parameters
    call_args = video_analyzer.video_client.annotate_video.call_args[1]
    assert call_args["request"].features == custom_features


def test_analyze_vertical_distribution_levels(video_analyzer, sample_object_annotations):
    """Test vertical distribution analysis of shelf levels."""

    distribution = video_analyzer.analyze_vertical_distribution(sample_object_annotations)
        
    levels = distribution["distribution_by_level"]
    
    # Should have exactly 3 levels with these specific names
    expected_level_names = ["Nivel Superior", "Nivel Medio", "Nivel Inferior"]
    
    # Check that all expected levels are present
    for level_name in expected_level_names:
        assert level_name in levels, f"Expected level '{level_name}' not found in results"
    
    # Check that there are no extra levels
    assert len(levels) == 3, f"Expected exactly 3 levels, but got {len(levels)}"