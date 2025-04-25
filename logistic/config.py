import os

from dotenv import load_dotenv

load_dotenv()

# Environment variables
DB_USER = os.getenv("DB_USER", "logistic")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "logistic_db")
USERS_PATH = os.getenv("USERS_PATH")
BROKER_HOST = os.getenv("BROKER_HOST", "localhost")
GMAPS_API_KEY = os.getenv("GMAPS_API_KEY","MY_GMAPS_API_KEY")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", f"pyamqp://guest:guest@{BROKER_HOST}:5672/")
DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
