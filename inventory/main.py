# Main application
from contextlib import asynccontextmanager
import sys

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import config
import schemas
from database import Base, SessionLocal, engine
from db_dependency import get_db
from stock.api import stock_router
from stock.events import setup_db_events
from stock.seed_data import seed_stock
from warehouse.api import warehouse_router
from warehouse.seed_data import seed_warehouses


def seed_database(db: Session = None):
    db = db or SessionLocal()
    try:
        seed_warehouses(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load
    setup_db_events()
    yield
    # Clean up


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

inventory_router = APIRouter(prefix="/inventory")
inventory_router.include_router(stock_router)
inventory_router.include_router(warehouse_router)


def seed_database(db: Session = None):
    db = db or SessionLocal()
    try:
        seed_warehouses(db)
        seed_stock(db)
    finally:
        db.close()


if "pytest" not in sys.modules:
    Base.metadata.create_all(bind=engine)
    # Seeding the database with initial data
    seed_database()


# Rest the database
@inventory_router.post("/reset", response_model=schemas.DeleteResponse)
def reset(db: Session = Depends(get_db)):
    Base.metadata.drop_all(bind=db.get_bind())
    Base.metadata.create_all(bind=db.get_bind())
    db.commit()
    seed_database(db)
    return schemas.DeleteResponse()


# health
@inventory_router.get("/health")
def ping():
    return "pong"


app.include_router(inventory_router)
