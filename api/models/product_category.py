from pydantic import BaseModel, field_validator
from datetime import datetime

class ProductCategory(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductCategoryCreate(BaseModel):
    name: str

    @field_validator("name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Category name cannot be empty")
        return v


class ProductCategoryUpdate(BaseModel):
    name: str | None = None

    @field_validator("name")
    def name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Category name cannot be empty")
        return v

