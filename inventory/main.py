# Main application
import sys
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import config
import schemas
from database import Base, engine
from db_dependency import get_db
from stock.api import stock_router
from stock.events import setup_db_events
from warehouse.api import warehouse_router


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


if "pytest" not in sys.modules:
    Base.metadata.create_all(bind=engine)


# Rest the database
@inventory_router.post("/reset", response_model=schemas.DeleteResponse)
def reset(db: Session = Depends(get_db)):
    Base.metadata.drop_all(bind=db.get_bind())
    Base.metadata.create_all(bind=db.get_bind())
    db.commit()
    return schemas.DeleteResponse()


# health
@inventory_router.get("/health")
def ping():
    return "pong"


app.include_router(inventory_router)
