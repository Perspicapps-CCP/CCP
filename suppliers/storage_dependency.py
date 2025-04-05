from fastapi import HTTPException
from google.cloud import storage

from config import GCS_BUCKET_NAME


def get_storage_bucket() -> storage.Bucket:
    try:
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        return bucket
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize Google Cloud Storage client: {str(e)}",
        )
