from .models import User
from .schemas import UserDetailSchema


def user_to_schema(user: User) -> UserDetailSchema:
    """
    Convert a User model instance to a UserDetailSchema instance.

    Args:
        user (User): The User model instance to convert.

    Returns:
        UserDetailSchema: The converted UserDetailSchema instance.
    """
    return UserDetailSchema.model_validate(user)
