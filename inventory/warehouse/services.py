from uuid import UUID
from sqlalchemy.orm import Session
from warehouse import models, schemas
from typing import Optional
from sqlalchemy import func


def create_warehouse(
    db: Session, warehouse: schemas.WarehouseSchema
) -> models.Warehouse:
    """Create a new warehouse in the database."""
    db_warehouse = models.Warehouse(
        name=warehouse.warehouse_name,
        country=warehouse.country,
        city=warehouse.city,
        address=warehouse.address,
        phone=warehouse.phone,
    )
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


def get_warehouse(db: Session, warehouse_id: str) -> models.Warehouse:
    """Get warehouse from id."""
    return (
        db.query(models.Warehouse)
        .filter(models.Warehouse.id == UUID(warehouse_id))
        .first()
    )


def get_warehouses(
    db: Session,
    warehouse_id: Optional[str] = None,
    warehouse_name: Optional[str] = None,
) -> list[models.Warehouse]:
    """Get all warehouses filtered from parameters."""
    query = db.query(models.Warehouse)
    if warehouse_id:
        query = query.filter(models.Warehouse.id == UUID(warehouse_id))
    if warehouse_name:
        query = query.filter(
            func.lower(models.Warehouse.name) == warehouse_name.lower()
        )
    return query.all()
