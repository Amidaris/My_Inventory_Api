from pydantic import BaseModel
from typing import Optional

class Category(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class Product(BaseModel):
    id: int
    name: str
    sku: str
    unit: str
    base_price: float
    vat: float
    stock: float
    category_id: Optional[int] = None
    category: Optional[Category] = None


    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name: str
    sku: str
    unit: str
    base_price: float
    vat: float
    category_id: Optional[int] = None
    stock: Optional[float] = 1


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    unit: Optional[str] = None
    base_price: Optional[float] = None
    vat: Optional[float] = None
    category_id: Optional[int] = None
    stock: Optional[float] = None

