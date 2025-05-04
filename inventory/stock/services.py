from typing import List, Tuple
from uuid import UUID
from sqlalchemy import func
from sqlalchemy.orm import Session

from warehouse.models import Warehouse
from . import models, schemas


def create_delivery(
    db: Session, delivery: schemas.DeliveryCreateSchema
) -> None:
    raise NotImplementedError("Not implemented yet")


def get_warehouse(db: Session, warehouse_id: UUID) -> Warehouse:
    """Get warehouse from id."""
    return db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()


def get_stock(
    db: Session, warehouse_id: UUID, product_id: UUID
) -> models.Stock:
    """Get stock by warehouse and product id."""
    return (
        db.query(models.Stock)
        .filter(models.Stock.warehouse_id == warehouse_id)
        .filter(models.Stock.product_id == product_id)
        .first()
    )


def get_list_stock(
    db: Session, warehouse_id: UUID, product_id: UUID
) -> list[models.Stock]:
    """Get stock list by filter params."""
    db_stock = db.query(models.Stock)
    if warehouse_id:
        db_stock = db_stock.filter(models.Stock.warehouse_id == warehouse_id)
    if product_id:
        db_stock = db_stock.filter(models.Stock.product_id == product_id)
    return db_stock.all()


def increase_stock(
    db: Session, warehouse_id: UUID, product_id: UUID, quantity: int
) -> models.Stock:
    """Increase stock units for a product in a warehouse."""
    db_stock = get_stock(db, warehouse_id, product_id)
    if db_stock:
        db_stock.quantity += quantity
        db.commit()
        db.refresh(db_stock)
        return db_stock
    else:
        raise ValueError("Stock not found")


def reduce_stock(
    db: Session, warehouse_id: UUID, product_id: UUID, quantity: int
) -> models.Stock:
    """Reduce stock units for a product in a warehouse."""
    db_stock = get_stock(db, warehouse_id, product_id)
    if db_stock:
        if db_stock.quantity >= quantity:
            db_stock.quantity -= quantity
            db.commit()
            db.refresh(db_stock)
            return db_stock
        else:
            raise ValueError("Not enough stock")
    else:
        raise ValueError("Stock not found")


def create_stock(
    db: Session, warehouse_id: UUID, product_id: UUID, quantity: int
) -> models.Stock:
    """Create stock for a product in a warehouse."""
    db_stock = models.Stock(
        warehouse_id=warehouse_id,
        product_id=product_id,
        quantity=quantity,
    )
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock


def create_operation(
    db: Session,
    file_name: str,
    warehouse_id: UUID,
    processed_records: int,
    successful_records: int,
    failed_records: int,
) -> models.Operation:
    """Create an operation."""
    db_operation = models.Operation(
        file_name=file_name,
        warehouse_id=warehouse_id,
        processed_records=processed_records,
        successful_records=successful_records,
        failed_records=failed_records,
    )
    db.add(db_operation)
    db.commit()
    db.refresh(db_operation)
    return db_operation


def get_list_all_products(db: Session) -> list[models.Stock]:
    """Get stock list by filter params."""
    db_stock = db.query(models.Stock)
    return db_stock.all()


def get_stock_aggregated(db: Session) -> List[Tuple[UUID, int]]:
    """
    Get a catalog of aggregated product stock across all warehouses.
    """
    db_stock = db.query(
        models.Stock.product_id,
        func.sum(models.Stock.quantity).label("quantity"),
    ).group_by(models.Stock.product_id)
    return db_stock.all()


def get_product_aggregated(db: Session, product_id: UUID) -> Tuple[UUID, int]:
    """
    Get a product stock aggregated across all warehouses.
    """
    db_stock = (
        db.query(
            models.Stock.product_id,
            func.sum(models.Stock.quantity).label("quantity"),
        )
        .filter(models.Stock.product_id == product_id)
        .group_by(models.Stock.product_id)
    )
    return db_stock.first()
