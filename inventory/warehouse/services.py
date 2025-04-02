from uuid import UUID
from sqlalchemy.orm import Session
from warehouse import models, schemas


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
    db: Session, warehouse_id: str, warehouse_name: str
) -> list[models.Warehouse]:
    """Get all warehouses filtered from parameters."""
    query = db.query(models.Warehouse)
    if warehouse_id:
        query = query.filter(models.Warehouse.id == UUID(warehouse_id))
    if warehouse_name:
        query = query.filter(models.Warehouse.name.contains(warehouse_name))
    return query.all()
