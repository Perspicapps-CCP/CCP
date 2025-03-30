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
