from fastapi import HTTPException, Request

from rpc_clients.schemas import UserSchema
from rpc_clients.users_client import UsersClient

UNAHITORIZED = HTTPException(status_code=401, detail="Unauthorized")


def get_auth_user(request: Request) -> UserSchema:
    """
    Get user from request.
    """
    header = request.headers.get("Authorization")
    if not header or not header.startswith("Bearer "):
        raise UNAHITORIZED
    token = header.split(" ")[1]
    if not token:
        raise UNAHITORIZED
    user = UsersClient().auth_user(token)
    if not user:
        raise UNAHITORIZED
    return user
