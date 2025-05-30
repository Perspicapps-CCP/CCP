from warehouse import models, schemas


def warehouse_created_to_schema(
    warehouse: models.Warehouse,
) -> schemas.WarehouseCreateResponseSchema:
    """Convert a Warehouse model to a WarehouseCreateResponseSchema."""
    return schemas.WarehouseCreateResponseSchema(
        warehouse_id=warehouse.id,
        warehouse_name=warehouse.name,
        country=warehouse.address.country,
        state=warehouse.address.state,
        city=warehouse.address.city,
        street=warehouse.address.street,
        address=f"{warehouse.address.street}, {warehouse.address.city}, {warehouse.address.state}, {warehouse.address.country}",
        latitude=warehouse.address.latitude,
        longitude=warehouse.address.longitude,
        phone=warehouse.phone,
        created_at=warehouse.created_at,
    )


def warehouse_list_to_schema(
    warehouses: list[models.Warehouse],
) -> list[schemas.WarehouseGetResponseSchema]:
    """Convert a list of Warehouse models to a list of WarehouseGetResponseSchema."""
    return [
        schemas.WarehouseGetResponseSchema(
            warehouse_id=warehouse.id,
            warehouse_name=warehouse.name,
            country=warehouse.address.country,
            state=warehouse.address.state,
            city=warehouse.address.city,
            street=warehouse.address.street,
            address=f"{warehouse.address.street}, {warehouse.address.city}, {warehouse.address.state}, {warehouse.address.country}",
            latitude=warehouse.address.latitude,
            longitude=warehouse.address.longitude,
            phone=warehouse.phone,
            last_update=warehouse.updated_at,
        )
        for warehouse in warehouses
    ]


def warehouse_get_to_schema(
    warehouse: models.Warehouse,
) -> schemas.WarehouseGetResponseSchema:
    """Convert a Warehouse model to a WarehouseGetResponseSchema."""
    return schemas.WarehouseGetResponseSchema(
        warehouse_id=warehouse.id,
        warehouse_name=warehouse.name,
        country=warehouse.address.country,
        state=warehouse.address.state,
        city=warehouse.address.city,
        street=warehouse.address.street,
        address=f"{warehouse.address.street}, {warehouse.address.city}, {warehouse.address.state}, {warehouse.address.country}",
        latitude=warehouse.address.latitude,
        longitude=warehouse.address.longitude,
        phone=warehouse.phone,
        last_update=warehouse.updated_at,
    )
