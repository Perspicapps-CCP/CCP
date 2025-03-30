from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from . import models, schemas


def create_manufacturer(
    db: Session, manufacturer: schemas.ManufacturerCreateSchema
) -> models.Manufacturer:
    """Create a new manufacturer in the database."""
    db_manufacturer = models.Manufacturer(
        id=uuid4(),
        name=manufacturer.manufacturer_name,
        identification_type=models.IdentificationType(
            manufacturer.identification_type
        ),
        identification_number=manufacturer.identification_number,
        address=manufacturer.address,
        contact_phone=manufacturer.contact_phone,
        email=manufacturer.email,
    )
    db.add(db_manufacturer)
    db.flush()
    db.commit()
    db.refresh(db_manufacturer)
    return db_manufacturer


def get_manufacturer_by_id_type(
    db: Session, manufacturer: models.Manufacturer
) -> Optional[models.Manufacturer]:
    return (
        db.query(models.Manufacturer)
        .filter(
            models.Manufacturer.identification_type
            == manufacturer.identification_type,
            models.Manufacturer.identification_number
            == manufacturer.identification_number,
        )
        .first()
    )


def get_manufacturer(
    db: Session, manufacturer_id: UUID
) -> Optional[models.Manufacturer]:
    return (
        db.query(models.Manufacturer)
        .filter(models.Manufacturer.id == manufacturer_id)
        .first()
    )


def get_manufacturers(
    db: Session, skip: int = 0, limit: int = 10
) -> List[models.Manufacturer]:
    return (
        db.query(models.Manufacturer)
        .order_by(models.Manufacturer.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
