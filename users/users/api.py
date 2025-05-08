from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
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


@users_router.post(
    "/sellers",
    response_model=schemas.UserDetailSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "model": schemas.ErrorResponseSchema,
            "description": "Bad Request",
        },
        401: {
            "model": schemas.ErrorResponseSchema,
            "description": "Unauthorized",
        },
        403: {
            "model": schemas.ErrorResponseSchema,
            "description": "Forbidden",
        },
    },
)
def create_seller(
    payload: dict,
    db: Session = Depends(get_db),
    _staff_user: models.User = Depends(auth.require_staff()),
):
    """
    Create a new seller.

    Args:
        payload (schemas.CreateSellerSchema): The data for creating
          a new seller.
        db (Session, optional): The database session.
          Defaults to Depends(get_db).
        current_user (models.User, optional):
          The currently authenticated user.
        Defaults to Depends(auth.get_current_active_user).

    Returns:
        schemas.UserDetailSchema: The details of the created seller.

    Raises:
        HTTPException: If the user is not authorized to create a seller.
    """
    try:
        payload = schemas.CreateSellerSchema.model_validate(
            payload, context={"db": db}
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=jsonable_encoder(e.errors()),
        )

    return services.create_seller(db=db, payload=payload)


@users_router.get(
    "/sellers",
    response_model=list[schemas.UserDetailSchema],
    responses={
        401: {
            "model": schemas.ErrorResponseSchema,
            "description": "Unauthorized",
        },
        403: {
            "model": schemas.ErrorResponseSchema,
            "description": "Forbidden",
        },
    },
)
def get_all_sellers(
    db: Session = Depends(get_db),
    _staff_user: models.User = Depends(auth.require_staff()),
):
    """
    Get all sellers.

    Args:
        db (Session, optional): The database session.
          Defaults to Depends(get_db).
        current_user (models.User, optional):
          The currently authenticated user.
        Defaults to Depends(auth.get_current_active_user).

    Returns:
        list[schemas.UserDetailSchema]: A list of all sellers.
    """
    return services.get_all_sellers(db=db)


@users_router.post(
    "/clients/",
    response_model=schemas.UserDetailSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "model": schemas.ErrorResponseSchema,
            "description": "Bad Request",
        },
        422: {
            "model": schemas.ErrorResponseSchema,
            "description": "Validation Error",
        },
    },
)
def create_client(
    payload: dict,
    db: Session = Depends(get_db),
):
    """
    Create a new client.

    Args:
        payload (schemas.CreateClientSchema): The data for creating
          a new client.
        db (Session, optional): The database session.
        Defaults to Depends(get_db).

    Returns:
        schemas.CreateClientResponseSchema:
        The details of the created client.
    """
    try:
        payload = schemas.CreateClientSchema.model_validate(
            payload, context={"db": db}
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=jsonable_encoder(e.errors()),
        )

    return services.create_client(db=db, payload=payload)
