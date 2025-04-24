from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from rpc_clients.schemas import AddressSchema, UserSchema


class StopSchema(BaseModel):
    """
    Schema for a stop in a route.
    """

    id: UUID
    client: UserSchema
    address: AddressSchema
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class RouteDetailSchema(BaseModel):
    """
    Schema for a route with its stops.
    """

    id: UUID
    date: date
    stops: List[StopSchema]
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class ListRoutesFilterSchema(BaseModel):
    """
    Schema for filtering routes.
    """

    seller_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    address: Optional[str] = None
