from typing import List, Optional
from uuid import UUID, uuid4
from fastapi import HTTPException

from sqlalchemy.orm import Session

from . import models, schemas


def create_manufacturer(
    db: Session, manufacturer: schemas.ManufacturerCreateSchema
) -> models.Manufacturer:
    """Create a new manufacturer in the database."""
    db_manufacturer = models.Manufacturer(
        id=uuid4(),
        name=manufacturer.manufacturer_name,
        identification_type=models.IdentificationType(manufacturer.identification_type),
        identification_number=manufacturer.identification_number,
        address=manufacturer.address,
        contact_phone=manufacturer.contact_phone,
        email=manufacturer.email
    )
    db.add(db_manufacturer)
    db.flush()
    db.commit()
    db.refresh(db_manufacturer)
    return db_manufacturer


