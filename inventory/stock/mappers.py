from . import models, schemas


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
