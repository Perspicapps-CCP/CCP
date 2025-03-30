# Main application
import sys

from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy.orm import Session

import schemas
from database import Base, SessionLocal, engine
from db_dependency import get_db
from users import seed_data as users_seed_data
from users.api import users_router

app = FastAPI()

prefix_router = APIRouter(prefix="/api/v1/users")
# Include the users router
prefix_router.include_router(users_router)


def seed_database(db: Session = None):
    db = db or SessionLocal()
    try:
        users_seed_data.create_users(db)
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
