from pydantic import BaseModel
from datetime import datetime


class LocationBase(BaseModel):
    name: str
    address: str
    city: str
    postal_code: str
    country: str
    note: str | None = None


class LocationInternal(LocationBase):
    id: int
    client_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LocationRead(LocationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


LocationCreate = LocationBase


class LocationListResponse(BaseModel):
    items: list[LocationRead]
