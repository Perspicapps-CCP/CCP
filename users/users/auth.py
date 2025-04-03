from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import SECRET_KEY
from db_dependency import get_db

from .crud import get_user
from .models import RoleEnum, User

# Security configuration
SECRET_KEY = SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


CREDENTIALS_EXPIRED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token.",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password using bcrypt.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password (str): The plain text password.

    Returns:
        str: The hashed password.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(
    user: User,
    expires_delta: Optional[timedelta] = None,
) -> Tuple[str, datetime]:
    """
    Create a JWT access token.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (Optional[timedelta]): The expiration time delta.

    Returns:
        Tuple[str, datetime]: The encoded JWT and its expiration time.
    """
    expires_delta = expires_delta or timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {"sub": user.username}
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise CREDENTIALS_EXPIRED
    except JWTError:
        raise CREDENTIALS_EXPIRED
    user = get_user(db, username=username)
    if user is None:
        raise CREDENTIALS_EXPIRED
    return user


def get_current_active_user(current_user=Depends(get_current_user)):
    if not current_user.is_active:
        raise CREDENTIALS_EXPIRED
    return current_user


def require_roles(allowed_roles: List[str]):
    """
    Dependency to check if the current user has one of the allowed roles.

    Args:
        allowed_roles (List[str]):
          A list of roles allowed to access the endpoint.

    Returns:
        Callable: A dependency function that validates the user's role.

    Raises:
        HTTPException: If the user does not have the required role.
    """

    def role_checker(
        current_user: User = Depends(get_current_active_user),
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return role_checker


def require_staff():
    """
    Dependency to check if the current user is a staff member.

    Returns:
        Callable: A dependency function that validates the user's role.

    Raises:
        HTTPException: If the user is not a staff member.
    """
    return require_roles([RoleEnum.STAFF])
