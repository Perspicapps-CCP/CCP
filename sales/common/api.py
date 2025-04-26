from fastapi import Depends, HTTPException, Request

from rpc_clients.schemas import UserAuthSchema
from rpc_clients.users_client import UsersClient

UNAUTHENTICATED = HTTPException(status_code=401, detail="Not authenticated")
UNAUTHORIZED = HTTPException(status_code=403, detail="Forbidden")


def get_auth_user(request: Request) -> UserAuthSchema:
    """
    Get user from request.
    """
    header = request.headers.get("Authorization")
    if not header or not header.startswith("Bearer "):
        raise UNAUTHENTICATED
    token = header.split(" ")[1]
    if not token:
        raise UNAUTHENTICATED
    user = UsersClient().auth_user(token)
    if not user:
        raise UNAUTHENTICATED
    return user


def get_auth_seller(auth_user=Depends(get_auth_user)) -> UserAuthSchema:
    """
    Get seller from request.
    """
    if not auth_user.is_seller:
        raise UNAUTHORIZED
    return auth_user
