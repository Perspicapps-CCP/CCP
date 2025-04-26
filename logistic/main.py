# Main application
import sys
from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy.orm import Session

import schemas
from database import Base, engine
from db_dependency import get_db
from delivery.api import deliveries_router, routes_router
from delivery.seed_data import seed_delivery_data

app = FastAPI()

prefix_router = APIRouter(prefix="/logistic")

prefix_router.include_router(deliveries_router)
prefix_router.include_router(routes_router)

if "pytest" not in sys.modules:
    Base.metadata.create_all(bind=engine)


# Rest the database
@prefix_router.post("/reset", response_model=schemas.DeleteResponse)
def reset(db: Session = Depends(get_db)):
    Base.metadata.drop_all(bind=db.get_bind())
    Base.metadata.create_all(bind=db.get_bind())
    db.commit()
    if "pytest" not in sys.modules:
        seed_delivery_data(db)
    return schemas.DeleteResponse()


# health
@prefix_router.get("/health")
def ping():
    return "pong"


app.include_router(prefix_router)
