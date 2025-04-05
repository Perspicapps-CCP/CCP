# Main application
import sys

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import config
import schemas
from database import Base, engine
from db_dependency import get_db
from plans.api import plans_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix_router = APIRouter(prefix="/api/v1/sales")
# Include the users router
prefix_router.include_router(plans_router)


if "pytest" not in sys.modules:
    Base.metadata.create_all(bind=engine)
    # Seeding the database with initial data


# Reset the database
@prefix_router.post("/reset-db", response_model=schemas.DeleteResponse)
def reset(db: Session = Depends(get_db)):
    Base.metadata.drop_all(bind=db.get_bind())
    Base.metadata.create_all(bind=db.get_bind())
    db.commit()
    return schemas.DeleteResponse()


# health
@prefix_router.get("/health")
def ping():
    return "pong"


app.include_router(prefix_router)
