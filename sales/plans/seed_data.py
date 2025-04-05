import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session

from .auth import get_password_hash
from .models import RoleEnum, User


def create_users(db: Session):
    """
    Create three users with hardcoded data and add them to the database.

    Args:
        db (Session): The database session.
    """
    if db.query(func.count(User.id)).scalar() > 0:
        return
    users = [
        User(
            id=uuid.uuid4(),
            username="staff_user",
            hashed_password=get_password_hash("staff_user_password"),
            full_name="Staff User",
            is_active=True,
            role=RoleEnum.STAFF,
            email="staff_user@test.com",
        ),
        User(
            id=uuid.uuid4(),
            username="seller_user",
            hashed_password=get_password_hash("seller_user_password"),
            full_name="Seller User",
            is_active=True,
            role=RoleEnum.SELLER,
            email="seller_user@test.com",
            phone="2345678901",
        ),
        User(
            id=uuid.uuid4(),
            username="buyer_user",
            hashed_password=get_password_hash("buyer_user_password"),
            full_name="Buyer User",
            is_active=True,
            role=RoleEnum.BUYER,
            email="buyer_user@test.com",
            phone="3456789012",
        ),
    ]

    db.add_all(users)
    db.commit()
