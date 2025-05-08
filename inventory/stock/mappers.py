from typing import List, Tuple
from uuid import UUID
from . import models, schemas
from rpc_clients import schemas as rpc_schemas
from rpc_clients.suppliers_client import SuppliersClient


def delivery_to_schema(
    purchase: models.Delivery,
) -> schemas.DeliveryDetailSchema:
    return schemas.DeliveryDetailSchema(id=purchase.id)


def stock_list_to_schema(
    stock_list: list[models.Stock],
) -> list[schemas.StockResponseSchema]:
    return [
        schemas.StockResponseSchema(
            product_id=stock.product_id,
            warehouse_id=stock.warehouse_id,
            quantity=stock.quantity,
            last_updated=stock.updated_at or stock.created_at,
        )
        for stock in stock_list
    ]


def operation_to_schema(
    operation: models.Operation,
) -> schemas.OperationResponseSchema:
    return schemas.OperationResponseSchema(
        operation_id=operation.id,
        warehouse_id=operation.warehouse_id,
        processed_records=operation.processed_records,
        successful_records=operation.successful_records,
        failed_records=operation.failed_records,
        created_at=operation.created_at,
    )


def stock_product_list_to_schema(
    stock_list: list[models.Stock],
) -> list[schemas.StockProductResponseSchema]:
    result: list[schemas.StockProductResponseSchema] = []
    product_ids = [stock.product_id for stock in stock_list]
    products = SuppliersClient().get_products(product_ids)
    for stock in stock_list:
        product = next((p for p in products if p.id == stock.product_id), None)
        schema = schemas.StockProductResponseSchema(
            product_name=product.name,
            product_code=product.product_code,
            manufacturer_name=(
                product.manufacturer.manufacturer_name
                if product and product.manufacturer
                else None
            ),
            price=product.price,
            images=(
                product.images
                if product and isinstance(product.images, list)
                else []
            ),
            warehouse_name=stock.warehouse.name,
            product_id=stock.product_id,
            warehouse_id=stock.warehouse_id,
            quantity=stock.quantity,
            last_updated=stock.updated_at or stock.created_at,
        )

        result.append(schema)

    return result


def aggr_stock_to_schema(
    aggr_stock: List[Tuple[UUID, int]],
    products: List[rpc_schemas.ProductSchema],
) -> List[schemas.AggrStockResponseSchema]:
    product_dict = {product.id: product for product in products}
    result = []

    for product_id, aggr_quantity in aggr_stock:
        default_product = rpc_schemas.ProductSchema(
            id=product_id,
            name="Unknown Product",
            product_code="N/A",
            manufacturer=rpc_schemas.ManufacturerSchema(
                id=UUID(int=0), manufacturer_name="Unknown"
            ),
            price=0.0,
            images=["https://example.com/default_image.png"],
        )
        product = product_dict.get(product_id, default_product)
        item = schemas.AggrStockResponseSchema(
            product_id=product_id,
            product_name=product.name,
            product_code=product.product_code,
            manufacturer_name=(
                product.manufacturer.manufacturer_name
                if product and product.manufacturer
                else None
            ),
            price=product.price,
            images=(
                product.images
                if product and isinstance(product.images, list)
                else []
            ),
            quantity=aggr_quantity,
        )
        result.append(item)
    return result


def aggr_stock_event_to_schema(
    action: str,
    aggr_stock: Tuple[UUID, int],
) -> schemas.EventSchema:
    return schemas.EventSchema(
        action=action,
        data=schemas.EventDataSchema(
            product_id=aggr_stock[0],
            quantity=aggr_stock[1],
        ),
    )
