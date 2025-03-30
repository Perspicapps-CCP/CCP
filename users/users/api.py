from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db_dependency import get_db

from . import auth, models, schemas, services

users_router = APIRouter(prefix="")


@users_router.post(
    "/login",
    response_model=schemas.LoginResponseSchema,
    responses={
        401: {
            "model": schemas.ErrorResponseSchema,
            "description": "Invalid credentials",
        },
    },
)
def login(
    login_data: schemas.LoginSchema,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return an access token and user details.

    Args:
        login_data (schemas.LoginSchema): The login data containing
        username and password.
        db (Session, optional): The database session. Defaults to
        Depends(get_db).

    Returns:
        schemas.LoginResponseSchema: The access token and user details.

    Raises:
        HTTPException: If the user is not found or the password is incorrect.
    """

    user = services.login_user(
        db=db,
        username=login_data.username,
        password=login_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token, expires_at = auth.create_access_token(user)

    return schemas.LoginResponseSchema(
        access_token=access_token,
        expires_at=expires_at,
        user=user,
        token_type="bearer",
    )


@users_router.get(
    "/profile",
    response_model=schemas.UserDetailSchema,
    responses={
        401: {
            "model": schemas.ErrorResponseSchema,
            "description": "Unauthorized",
        },
    },
)
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    """
    Get the profile of the currently authenticated user.

    Args:
        db (Session, optional): The database session. Defaults
        to Depends(get_db).
        current_user (schemas.UserDetailSchema, optional): The currently
        authenticated user. Defaults to Depends(auth.get_current_user).

    Returns:
        schemas.UserDetailSchema: The details of the current user.
    """
    return current_user
