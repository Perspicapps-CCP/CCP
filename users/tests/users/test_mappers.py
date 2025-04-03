import datetime
import uuid

from users import mappers
from users.models import RoleEnum, User
from users.schemas import UserDetailSchema


def test_user_to_schema():
    """
    Test the user_to_schema function.
    """
    user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        phone="123-456-789",
        role=RoleEnum.STAFF,
        id=uuid.uuid4(),
        created_at=datetime.datetime.now(),
        is_active=True,
    )
    schema = mappers.user_to_schema(user)
    assert isinstance(schema, UserDetailSchema)
    assert schema.id == user.id
    assert schema.username == user.username
    assert schema.email == user.email
    assert schema.full_name == user.full_name
    assert schema.phone == user.phone
    assert schema.role == user.role
