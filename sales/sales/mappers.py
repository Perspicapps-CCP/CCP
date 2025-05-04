from typing import Dict, List
from uuid import UUID

import faker

from rpc_clients.schemas import ProductSchema, UserSchema
from rpc_clients.suppliers_client import SuppliersClient
from rpc_clients.users_client import UsersClient

from .models import Sale
from .schemas import SaleDetailSchema, SaleItemSchema

fake = faker.Faker()


def _sale_to_schema(
    sale: Sale,
    sellers: Dict[UUID, UserSchema],
    clients: Dict[UUID, UserSchema],
    products: Dict[UUID, ProductSchema],
) -> SaleDetailSchema:
    """
    Map a Sale model to a SaleDetailSchema.
    """

    client = clients.get(sale.client_id)

    return SaleDetailSchema(
        id=sale.id,
        seller=sellers.get(sale.seller_id),
        client=client,
        order_number=sale.order_number,
        address=client.address if client else None,
        total_value=sale.total_value,
        currency=sale.currency,
        created_at=sale.created_at,
        updated_at=sale.updated_at,
        items=[
            SaleItemSchema(
                id=item.id,
                product=products.get(item.product_id),
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_value=item.total_value,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in sale.items
        ],
        deliveries=[],
    )


def sale_to_schema(sale: Sale) -> SaleDetailSchema:
    """
    Map a Sale model to a SaleDetailSchema.
    """
    return sales_to_schema([sale])[0]


def sales_to_schema(sales: List[Sale]) -> List[SaleDetailSchema]:
    """
    Map a list of Sale models to a list of SaleDetailSchema.
    """
    sellers = UsersClient().get_sellers(
        list({sale.seller_id for sale in sales}),
    )
    products = SuppliersClient().get_products(
        list({item.product_id for sale in sales for item in sale.items}),
    )
    clients = UsersClient().get_clients(
        list({sale.client_id for sale in sales}),
    )
    sellers = {seller.id: seller for seller in sellers}
    products = {product.id: product for product in products}
    clients = {client.id: client for client in clients}
    return [
        _sale_to_schema(
            sale,
            sellers,
            clients,
            products,
        )
        for sale in sales
    ]
