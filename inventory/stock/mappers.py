from . import models, schemas
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
) -> list[schemas.StockResponseSchema]:
    result: list[schemas.StockResponseSchema] = []
    product_ids = [stock.product_id for stock in stock_list]
    products = SuppliersClient().get_products(product_ids)
    for stock in stock_list:
        product = next((p for p in products if p.id == stock.product_id), None)

        schema = schemas.StockResponseSchema(
            product_name=product.name if product else None,
            product_code=product.product_code if product else None,
            manufacturer_name=(
                product.manufacturer.manufacturer_name
                if product and product.manufacturer
                else None
            ),
            price=product.price if product else None,
            images=(
                product.images
                if product and isinstance(product.images, list)
                else []
            ),
            warehouse_name=stock.warehouse.name if stock.warehouse else None,
            product_id=stock.product_id,
            warehouse_id=stock.warehouse_id,
            quantity=stock.quantity,
            last_updated=stock.updated_at or stock.created_at,
        )

        result.append(schema)

    return result
