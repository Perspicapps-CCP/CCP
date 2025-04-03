from typing import Optional

from sqlalchemy.orm import Session

from . import models


def get_user(db: Session, username: str) -> Optional[models.User]:
    """
    Retrieve a user from the database by username.
    Args:
        db (Session): The database session to use for the query.
        username (str): The username of the user to retrieve.
    Returns:
        Optional[models.User]: The user object if found, otherwise None.
    """

    return (
        db.query(models.User).filter(models.User.username == username).first()
    )


def create_user(db: Session, user: models.User) -> models.User:
    """
    Create a new user in the database.
    Args:
        db (Session): The database session to use for the query.
        user (models.User): The user object to create.
    Returns:
        models.User: The created user object.
    """
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def is_username_taken(db: Session, username: str) -> bool:
    """
    Check if a username is already taken in the database.
    Args:
        db (Session): The database session to use for the query.
        username (str): The username to check.
    Returns:
        bool: True if the username is taken, False otherwise.
    """
    return (
        db.query(models.User).filter(models.User.username == username).count()
        > 0
    )


def is_email_taken(db: Session, email: str) -> bool:
    """
    Check if an email is already taken in the database.
    Args:
        db (Session): The database session to use for the query.
        email (str): The email to check.
    Returns:
        bool: True if the email is taken, False otherwise.
    """
    return db.query(models.User).filter(models.User.email == email).count() > 0


def is_phone_taken(db: Session, phone: str) -> bool:
    """
    Check if a phone number is already taken in the database.
    Args:
        db (Session): The database session to use for the query.
        phone (str): The phone number to check.
    Returns:
        bool: True if the phone number is taken, False otherwise.
    """
    return db.query(models.User).filter(models.User.phone == phone).count() > 0


def get_all_users(
    db: Session,
    role: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
) -> list[models.User]:
    """
    Get all users from the database.
    Args:
        db (Session): The database session to use for the query.
        role (Optional[str]): The role of the users to filter by.
          Defaults to None.
        limit (Optional[int]): The maximum number of records to return.
          Defaults to None.
        skip (Optional[int]): The number of records to skip.
          Defaults to None.
    Returns:
        list[models.User]: A list of user objects.
    """
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    if skip:
        query = query.offset(skip)
    if limit:
        query = query.limit(limit)
    return query.all()
