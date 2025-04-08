import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from . import auth, crud, models, schemas


def login_user(
    db: Session, username: str, password: str
) -> Optional[models.User]:
    """
    Authenticate a user by checking the username and password.
    Args:
        db (Session): The database session to use for the query.
        username (str): The username of the user to authenticate.
        password (str): The password of the user to authenticate.
    Returns:
        Optional[models.User]: The authenticated user object if successful,
        otherwise None.
    """
    user = crud.get_user(db, username)
    if not user or not auth.verify_password(password, user.hashed_password):
        return None
    return user


def create_user(
    db: Session,
    payload: schemas.UserBaseSchema,
    role: str,
) -> models.User:
    """
    Creates a new user in the database.
    Args:
        db (Session): The database session to use for creating the user.
        payload (schemas.UserBaseSchema): The schema containing the
          user's basic information.
        role (str): The role to assign to the user.
        password (str): The plain text password for the user.
    Returns:
        models.User: The newly created user instance.
    """
    user = models.User(
        username=payload.username,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        role=role,
        hashed_password='invalid_value',
    )
    return crud.create_user(db, user)


def create_seller(
    db: Session, payload: schemas.CreateSellerSchema
) -> models.User:
    """
    Create a new seller user in the database.
    Args:
        db (Session): The database session to use for the query.
        user (schemas.CreateStaffSchema): The data of the user to create.
        User schema is already validated.
    Returns:
        models.User: The created user object.
    """
    return create_user(
        db,
        payload=payload,
        role=models.RoleEnum.SELLER,
    )


def get_all_sellers(db: Session) -> list[models.User]:
    """
    Get all sellers from the database.
    Args:
        db (Session): The database session to use for the query.
        skip (int): The number of records to skip. Defaults to 0.
        limit (int): The maximum number of records to return. Defaults to 100.
    Returns:
        list[models.User]: A list of seller user objects.
    """
    return crud.get_all_users(db, role=models.RoleEnum.SELLER)


def get_sellers_with_ids(
    db: Session, seller_ids: List[uuid.UUID]
) -> list[models.User]:
    """
    Get sellers by their IDs.
    Args:
        db (Session): The database session to use for the query.
        seller_ids (list[schemas.UUIDSchema]): A list of seller IDs
          to retrieve.
    Returns:
        list[models.User]: A list of seller user objects.
    """
    return crud.get_users_by_ids(
        db, ids=seller_ids, role=models.RoleEnum.SELLER
    )
