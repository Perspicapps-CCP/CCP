from . import models, schemas


def manufacturer_to_schema(
    manufacturer: models.Manufacturer,
) -> schemas.ManufacturerDetailSchema:
    return schemas.ManufacturerDetailSchema(
        id=manufacturer.id,
        manufacturer_name=manufacturer.name,
        identification_type=manufacturer.identification_type,
        identification_number=manufacturer.identification_number,
        address=manufacturer.address,
        contact_phone=manufacturer.contact_phone,
        email=manufacturer.email,
        created_at=manufacturer.created_at,
        updated_at=manufacturer.updated_at
    )
