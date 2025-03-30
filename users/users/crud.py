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
