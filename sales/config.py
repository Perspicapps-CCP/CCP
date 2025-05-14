import os

from dotenv import load_dotenv

load_dotenv()

# Environment variables
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "sales")
USERS_PATH = os.getenv("USERS_PATH")
BROKER_HOST = os.getenv("BROKER_HOST", "localhost")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "ccp-files-storage")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "my-gemini-api-key")
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost,"
    "http://localhost:4200,"
    "https://appstaff-dot-ccp-perspicapps.uc.r.appspot.com,"
    "*",
).split(",")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL", f"pyamqp://guest:guest@{BROKER_HOST}:5672/"
)
