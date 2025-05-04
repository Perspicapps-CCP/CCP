from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from rpc_clients.inventory_client import InventoryClient
from rpc_clients.logistic_client import LogisticClient
from rpc_clients.schemas import (
    UserAuthSchema,
)
from rpc_clients.suppliers_client import SuppliersClient
from rpc_clients.users_client import UsersClient

from . import crud, exceptions, models, schemas


def get_all_sales(
    db: Session, filters: schemas.ListSalesQueryParamsSchema
) -> List[models.Sale]:
    """
    Retrieve all sales from the database.

    Args:
        db (Session): The database session.

    Returns:
        List[Sale]: A list of Sale objects.
    """
    return crud.get_all_sales(db, filters)


def get_sale_by_id(db: Session, sale_id: UUID) -> models.Sale:
    """
    Retrieve a sale by its ID.

    Args:
        db (Session): The database session.
        sale_id (UUID): The ID of the sale.

    Returns:
        Sale: The Sale object if found, otherwise None.
    """
    return crud.get_sale_by_id(db, sale_id)


def create_sale(
    db: Session,
    user: UserAuthSchema,
    create_sale_schema: schemas.CreateSaleSchema,
) -> models.Sale:
    """
    Create a new sale in the database.

    Args:
        db (Session): The database session.
        user (UserSchema): The user creating the sale.
        create_sale_schema (CreateSaleSchema): The schema for the sale.

    Returns:
        Sale: The created Sale object.
    """
    seller_id = user.id if user.is_seller else None
    client_id = create_sale_schema.client_id
    client = (
        UsersClient().get_clients([client_id])[0] if user.is_seller else user
    )
    products = {
        p.id: p
        for p in SuppliersClient().get_products(
            {item.product_id for item in create_sale_schema.items}
        )
    }
    sale = models.Sale(
        seller_id=seller_id,
        client_id=client_id,
        address_id=client.address.id,
        total_value=0,
        currency="COP",
    )
    sale = crud.create_sale(db, sale)

    # Create the sale items
    sale_items = []
    for item in create_sale_schema.items:
        unit_price = products[item.product_id].price
        sale_item = models.SaleItem(
            sale_id=sale.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=unit_price,
            total_value=unit_price * item.quantity,
        )
        crud.create_sale_item(db, sale_item)
        sale_items.append(sale_item)

    inventory_order = InventoryClient().reserve_stock(
        {
            "order_number": sale.order_number,
            "sale_id": str(sale.id),
            "items": [
                {
                    "product_id": str(item.product_id),
                    "quantity": item.quantity,
                }
                for item in create_sale_schema.items
            ],
        }
    )
    if "error" in inventory_order:
        # If the inventory order fails, we need to rollback the sale
        # and raise an exception.
        db.rollback()
        raise exceptions.SaleCantBeCreated(
            inventory_order,
        )
    sale_items_by_id = {str(item.product_id): item for item in sale_items}
    # Create the deliveries
    logistic_client = LogisticClient()
    result = logistic_client.send_pending_sales_to_delivery(
        {
            "sales_id": str(sale.id),
            "order_number": sale.order_number,
            "address": {
                "id": str(client.address.id),
                "street": client.address.line,
                "city": client.address.city,
                "state": client.address.state,
                "postal_code": "110110",
                "country": client.address.country,
            },
            "sales_items": [
                {
                    "sales_item_id": str(
                        sale_items_by_id[item["product_id"]].id
                    ),
                    "product_id": item["product_id"],
                    "warehouse_id": item["warehouse_id"],
                    "quantity": item["quantity"],
                }
                for item in inventory_order["items"]
            ],
        }
    )
    if result.get("status") != "success":
        # If the logistic order fails, we need to rollback the sale
        # and raise an exception.
        db.rollback()
        raise exceptions.SaleCantBeCreated(
            "Logistic order failed",
        )

    return sale
