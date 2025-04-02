from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

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
    
def get_products(
    db: Session, productsIds: Optional[List[str]] = None, manufacturer_id: Optional[UUID] = None
) -> List[models.ManufacturerProduct]:
    query = db.query(models.ManufacturerProduct)
    if productsIds:
        query = query.filter(models.ManufacturerProduct.id.in_(productsIds))
    if manufacturer_id:
        query = query.filter(models.ManufacturerProduct.manufacturer_id == manufacturer_id)
    return (
        query.order_by(models.ManufacturerProduct.updated_at.desc()).all()
    )
    
def create_bulk_products(manufacturer_id: UUID, db: Session, products: List[schemas.ProductCreateSchema]) -> schemas.BatchProductResponseSchema:
    total_successful_records : int = 0
    total_errors_records: int = 0
    details: List[schemas.ErrorDetailResponseSchema] = []
    for index, product in enumerate(products, start=2):        
        db_product = models.ManufacturerProduct(
                id=uuid4(),
                manufacturer_id=manufacturer_id,
                code=product.product_code,
                name=product.name,
                price=product.price
            )
        try:
            db.add(db_product)
            db.flush()
            db.commit()
            db.refresh(db_product)  
            
            images_data = []
            for image in product.images:
                images_data.append(models.ProductImage(id=uuid4(), product_id=db_product.id, url=image.url))
                    
            if images_data:
                db.add_all(images_data)            
                      
            total_successful_records += 1
        except (Exception, IntegrityError) as e:
            total_errors_records += 1
            db.rollback()  
            error: str                  
            if "code" in str(e.orig):
             error=f"El código '{product.product_code}' ya existe."
            elif "name" in str(e.orig):
             error=f"El nombre '{product.name}' ya existe."
            else:
             error="Error al insertar el producto."
            details.append(schemas.ErrorDetailResponseSchema(row_file = index, detail=error))
    return schemas.BatchProductResponseSchema(total_successful_records= total_successful_records, total_errors_records=total_errors_records, detail=details)
