# Main application
import sys

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import config
import schemas
from database import Base, SessionLocal, engine
from db_dependency import get_db
from plans.api import plans_router
from routes.api import routes_router
from routes.seed_data import seed_routes
from sales.api import sales_router
from sales.seed_data import seed_sales
from sellers.api import sellers_router
from sellers.seed_data import seed_selle_clients

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
prefix_router.include_router(sales_router)
prefix_router.include_router(routes_router)
prefix_router.include_router(sellers_router)


def seed_database(db: Session = None):
    db = db or SessionLocal()
    try:
        seed_selle_clients(db)
        seed_sales(db)
        seed_routes(db)
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
