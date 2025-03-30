# Main application
import sys

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

import schemas
from database import Base, engine
from db_dependency import get_db
from inventory.api import inventory_router
from warehouse.api import warehouse_router

app = FastAPI()


if "pytest" not in sys.modules:
    Base.metadata.create_all(bind=engine)

inventory_router.include_router(warehouse_router)

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
