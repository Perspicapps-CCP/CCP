# Main application
import sys

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from users import seed_data as users_seed_data
from users.api import users_router

import config
import schemas
from database import Base, SessionLocal, engine
from db_dependency import get_db

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix_router = APIRouter(prefix="/api/v1/users")
# Include the users router
prefix_router.include_router(users_router)


def seed_database(db: Session = None):
    db = db or SessionLocal()
    try:
        users_seed_data.create_users(db)
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if "pytest" not in sys.modules:
    Base.metadata.create_all(bind=engine)
    # Seeding the database with initial data
    seed_database()


# Reset the database
@prefix_router.post("/reset-db", response_model=schemas.DeleteResponse)
def reset(db: Session = Depends(get_db)):
    Base.metadata.drop_all(bind=db.get_bind())
    Base.metadata.create_all(bind=db.get_bind())
    db.commit()
    seed_database(db)
    return schemas.DeleteResponse()


# health
@prefix_router.get("/health")
def ping():
    return "pong"


app.include_router(prefix_router)
