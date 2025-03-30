from typing import Optional

from sqlalchemy.orm import Session

from . import auth, crud, models


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
