import os

from dotenv import load_dotenv

load_dotenv()

# Environment variables
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "users")
USERS_PATH = os.getenv("USERS_PATH")
BROKER_HOST = os.getenv("BROKER_HOST", "localhost")
CREATE_DELIVERY_TOPIC = os.getenv(
    "CREATE_DELIVERY_TOPIC", "rpc_create_delivery"
)

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
)
