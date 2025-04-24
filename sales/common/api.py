from fastapi import HTTPException, Request

from rpc_clients.schemas import UserSchema
from rpc_clients.users_client import UsersClient

UNAUTHORIZED = HTTPException(status_code=401, detail="Unauthorized")


def get_auth_user(request: Request) -> UserSchema:
    """
    Get user from request.
    """
    header = request.headers.get("Authorization")
    if not header or not header.startswith("Bearer "):
        raise UNAUTHORIZED
    token = header.split(" ")[1]
    if not token:
        raise UNAUTHORIZED
    user = UsersClient().auth_user(token)
    if not user:
        raise UNAUTHORIZED
    return user
