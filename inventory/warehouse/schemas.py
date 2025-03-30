
from datetime import datetime
import re
from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator

uuid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
only_strings = r'^[a-zA-Z0-9_ñÑ]+$'

class WarehouseSchema(BaseModel):
    warehouse_name: str 
    country: str
    city: str
    address: str
    phone: str = Field(min_length=7, max_length=10, pattern=r'^\d*$')

class WarehouseCreateResponseSchema(WarehouseSchema):
    warehouse_id: str 
    created_at: datetime

class WarehouseGetResponseSchema(WarehouseSchema):
    warehouse_id: str 
    last_update: datetime

    @model_validator(mode='before')
    def check_warehouse_empty(self)->'WarehouseGetResponseSchema':
        if self is None:
            raise HTTPException(status_code=404, detail="The warehouse with these id has not exist.")     
        return self  

class ParamsRequest(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None

    @field_validator('id', mode='before')
    def validate_id_param(cls, v):      
        if v is not None and not re.match(uuid_pattern, v):
            raise HTTPException(status_code=400, detail="The id parameter had not a valid format value")
        return v
    
    @field_validator('name', mode='before')
    def validate_name_param(cls, v):     
        if v is not None and not re.match(only_strings, v):
            raise HTTPException(status_code=400, detail="The name parameter had not a valid format value")
        return v