from datetime import timedelta
import logging
from celery import Celery
from db_dependency import get_db
from config import CELERY_BROKER_URL, GCS_BUCKET_NAME, GEMINI_API_KEY

from sellers.models import VideoStatusEnum
from sellers.services import (
    get_all_videos_without_analysis,
    get_all_videos_without_recommendations,
    update_video_status,
)
from sellers.video_analyzer import VideoAnalyzer
from sellers.video_recommend_generator import (
    VideoRecommendationGenerator,
)


logger = logging.getLogger(__name__)

celery_app = Celery(
    "video_process",
    broker=CELERY_BROKER_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,  # Limit the number of tasks fetched by each worker at a time
    task_track_started=True,  # Mark tasks as "started" when they start running
    task_reject_on_worker_lost=True,
    broker_transport_options={
        "visibility_timeout": 600
    },  # Set visibility timeout for tasks in seconds
    task_acks_late=True,  # Acknowledge tasks only after they are completed
)

celery_app.conf.beat_schedule = {
    "generate-video-analysis": {
        "task": "sales.workers.generate_video_analysis",
        "schedule": timedelta(minutes=2),
        "options": {
            "queue": "ccp.video_analysis",
            "expires": 300,
        },
    },
    "generate-video-recomendattions": {
        "task": "sales.workers.generate_video_recomendattions",
        "schedule": timedelta(minutes=2),
        "options": {
            "queue": "ccp.video_recomendattions",
            "expires": 300,
        },
    },
}


@celery_app.task(name="sales.workers.generate_video_analysis")
def generate_video_analysis():
    db = next(get_db())

    try:
        analyzer = VideoAnalyzer(GCS_BUCKET_NAME)
        pending_videos = get_all_videos_without_analysis(db)
        for video in pending_videos:
            logger.info(f"Generating analysis for video: {video.id}")
            analysis_results = analyzer.analyze_video(video.url)
            analysis_path = analyzer.save_analysis_to_gcs(
                analysis_results, video.url
            )
            update_video_status(
                db, video.id, VideoStatusEnum.ANALISYS_GENERATED
            )
            logger.info(
                f"Video analysis generated for video: {video.id}. Saved to {analysis_path}"
            )
    except Exception as e:
        logger.error(f"Error generating video analysis: {e}")


@celery_app.task(name="sales.workers.generate_video_recomendattions")
def generate_video_recomendattions():
    db = next(get_db())

    try:
        recommender = VideoRecommendationGenerator(
            gemini_api_key=GEMINI_API_KEY, bucket_name=GCS_BUCKET_NAME
        )
        pending_videos = get_all_videos_without_recommendations(db)
        for video in pending_videos:
            logger.info(f"Generating recommendations for video: {video.id}")
            analysis_results = recommender.read_analysis_from_gcs(video.url)
            recommendations = recommender.generate_recommendations(
                analysis_results
            )
            update_video_status(
                db,
                video.id,
                VideoStatusEnum.RECOMENDATIONS_GENERATED,
                recommendations,
            )
            logger.info(f"Recommendations generated for video: {video.id}")
    except Exception as e:
        logger.error(f"Error generating video recommendations: {e}")
