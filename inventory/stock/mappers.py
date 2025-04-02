from . import models, schemas


def delivery_to_schema(
    purchase: models.Delivery,
) -> schemas.DeliveryDetailSchema:
    return schemas.DeliveryDetailSchema(
        id=purchase.id,
        purchase_id=purchase.purchase_id,
        address_id=purchase.address_id,
        user_id=purchase.user_id,
        status=purchase.status,
        created_at=purchase.created_at,
        updated_at=purchase.updated_at,
        delivery_date=purchase.delivery_date,
        items=[
            schemas.DeliveryItemResponseSchema(
                product_id=item.product_id,
                quantity=item.quantity,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in purchase.items
        ],
    )
