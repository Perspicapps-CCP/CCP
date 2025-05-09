from typing import List, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from warehouse.models import Warehouse

from . import exceptions, models, schemas


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


def allocate_stock_products(
    db: Session,
    allocation: schemas.AllocateStockSchema,
) -> list[models.StockMovement]:
    """Allocate products in stock."""
    products = {item.product_id: item.quantity for item in allocation.items}

    stock_list = (
        db.query(models.Stock)
        .with_for_update()
        .filter(models.Stock.product_id.in_(products.keys()))
        .filter(models.Stock.quantity > 0)
        .order_by(
            models.Stock.product_id.asc(),
            models.Stock.quantity.desc(),
            models.Stock.warehouse_id.asc(),
        )
        .all()
    )

    avalaible_stock = {product_id: 0 for product_id in products.keys()}

    for stock in stock_list:
        avalaible_stock[stock.product_id] += stock.quantity

    # Validate there is enough stock to allocate
    if any(
        avalaible_stock[product_id] < products[product_id]
        for product_id in products.keys()
    ):
        raise exceptions.InsufficientStockToAllocateException(
            avalaible_stock, products
        )
    # Allocate stock.
    movements = []
    for product_id, quantity in products.items():
        stocks = [
            stock for stock in stock_list if stock.product_id == product_id
        ]
        for stock in stocks:
            quantity_moved = 0
            if stock.quantity >= quantity:
                stock.quantity -= quantity
                quantity_moved = quantity
                quantity = 0
            else:
                quantity -= stock.quantity
                quantity_moved = stock.quantity
                stock.quantity = 0
            movements.append(
                models.StockMovement(
                    stock_product_id=stock.product_id,
                    stock_warehouse_id=stock.warehouse_id,
                    quantity=quantity_moved,
                    sale_id=allocation.sale_id,
                    order_number=allocation.order_number,
                )
            )
            if quantity == 0:
                break
    db.add_all(movements)
    db.commit()
    return movements
