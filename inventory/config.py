import os

from dotenv import load_dotenv

load_dotenv()

# Environment variables
DB_USER = os.getenv("DB_USER", "inventory")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "inventory_db")
USERS_PATH = os.getenv("USERS_PATH")
BROKER_HOST = os.getenv("BROKER_HOST", "localhost")
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost,"
    "http://localhost:4200,"
    "http://127.0.0.1:5500,"
    "https://appstaff-dot-ccp-perspicapps.uc.r.appspot.com,"
    "*",
).split(",")
DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
