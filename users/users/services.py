from typing import Optional

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
    db: Session, payload: schemas.UserBaseSchema, role: str, password: str
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
        phone_number=payload.phone_number,
        role=role,
        hashed_password=auth.get_password_hash(password),
    )
    return crud.create_user(db, user)


def create_seller(
    db: Session, payload: schemas.CreateStaffSchema
) -> models.User:
    """
    Create a new staff user in the database.
    Args:
        db (Session): The database session to use for the query.
        user (schemas.CreateStaffSchema): The data of the user to create.
    Returns:
        models.User: The created user object.
    """
    return create_user(
        db,
        payload=payload,
        role=models.RoleEnum.SELLER,
        password=payload.password,
    )
