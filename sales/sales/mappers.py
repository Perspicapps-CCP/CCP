from typing import Dict, List
from uuid import UUID

import faker

from rpc_clients.schemas import ProductSchema, SellerSchema
from rpc_clients.suppliers_client import SuppliersClient
from rpc_clients.users_client import UsersClient

from .models import Sale
from .schemas import AddressSchema, SaleDetailSchema, SaleItemSchema

fake = faker.Faker()


def _sale_to_schema(
    sale: Sale,
    sellers: Dict[UUID, SellerSchema],
    products: Dict[UUID, ProductSchema],
) -> SaleDetailSchema:
    """
    Map a Sale model to a SaleDetailSchema.
    """

    return SaleDetailSchema(
        id=sale.id,
        seller=sellers.get(sale.seller_id),
        order_number=sale.order_number,
        address=AddressSchema(
            id=sale.address_id,
            street=fake.street_address(),
            city=fake.city(),
            state=fake.state(),
            country=fake.country(),
            postal_code=fake.postalcode(),
        ),
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
    )


def sale_to_schema(sale: Sale) -> SaleDetailSchema:
    """
    Map a Sale model to a SaleDetailSchema.
    """
    sellers = UsersClient().get_sellers(
        [sale.seller_id],
    )
    products = SuppliersClient().get_products(
        [item.product_id for item in sale.items],
    )
    sellers = {seller.id: seller for seller in sellers}
    products = {product.id: product for product in products}
    return _sale_to_schema(
        sale,
        sellers,
        products,
    )


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
    sellers = {seller.id: seller for seller in sellers}
    products = {product.id: product for product in products}
    return [
        _sale_to_schema(
            sale,
            sellers,
            products,
        )
        for sale in sales
    ]
