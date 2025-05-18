import json
import uuid
from itertools import cycle

import faker
from sqlalchemy import func
from sqlalchemy.orm import Session

from .auth import get_password_hash
from .models import Address, RoleEnum, User, IdTypeEnum

fake = faker.Faker()
faker.Faker.seed(0)


def seed_other_clients(db: Session, total=10):

    with open("users/seed_addresses.json", "r") as file:
        data = json.load(file)
    users = []
    addresses_data = cycle(data)
    addresses = []
    for _i in range(total):
        user = User(
            id=fake.uuid4(cast_to=None),
            username=fake.user_name(),
            hashed_password=get_password_hash("client_password"),
            full_name=fake.name(),
            is_active=True,
            role=RoleEnum.CLIENT,
            email=fake.email(),
            phone=fake.phone_number(),
            identification=fake.ssn(),
            id_type=IdTypeEnum.NIT,
        )
        users.append(user)
    db.add_all(users)
    db.commit()
    users = db.query(User).filter(User.role == RoleEnum.CLIENT).all()
    for user in users:
        address_data = next(addresses_data)
        address = Address(
            id=fake.uuid4(cast_to=None),
            user_id=user.id,
            line=address_data["line"],
            neighborhood=address_data["neighborhood"],
            city=address_data["city"],
            state=address_data["state"],
            country=address_data["country"],
            latitude=address_data["latitude"],
            longitude=address_data["longitude"],
        )
        addresses.append(address)
    db.add_all(addresses)
    db.commit()


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
            id=fake.uuid4(cast_to=None),
            username="staff_user",
            hashed_password=get_password_hash("staff_user_password"),
            full_name="Staff User",
            is_active=True,
            role=RoleEnum.STAFF,
            email="staff_user@test.com",
        ),
        User(
            id=fake.uuid4(cast_to=None),
            username="seller_user",
            hashed_password=get_password_hash("seller_user_password"),
            full_name="Seller User",
            is_active=True,
            role=RoleEnum.SELLER,
            email="seller_user@test.com",
            phone="2345678901",
            identification=fake.ssn(),
            id_type=IdTypeEnum.NIT,
        ),
        User(
            id=fake.uuid4(cast_to=None),
            username="client_user",
            hashed_password=get_password_hash("client_user_password"),
            full_name="client User",
            is_active=True,
            role=RoleEnum.CLIENT,
            email="client_user@test.com",
            phone="3456789012",
            identification="123456789",
            id_type=IdTypeEnum.NIT,
        ),
    ]

    db.add_all(users)
    db.commit()
    seed_other_clients(db)
