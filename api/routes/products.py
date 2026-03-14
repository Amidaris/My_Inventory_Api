from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from api.config.db import get_db
from api.services.auth_service import get_current_active_user
from api.services.product_service import get_products_for_user, create_product, get_product_by_id, update_product, delete_product
from api.models.product import Product,ProductCreate, ProductUpdate
from api.models.db_user import UserDB

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Product,
    summary="Create a new product",
    description="""
Create a new product for the authenticated user.

- Requires JWT authentication.
- Product is linked to the logged-in user.
- Returns 201 with the created product.
"""
)
def create_new_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    new_product = create_product(
        db=db,
        user_id=current_user.id,
        name=product_data.name,
        sku=product_data.sku,
        unit=product_data.unit,
        base_price=product_data.base_price,
        vat=product_data.vat,
        category_id=product_data.category_id,
    )

    return new_product


@router.get("/", response_model=List[Product])
def list_products(
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return get_products_for_user(db, current_user.id)


@router.put(
    "/{product_id}",
    response_model=Product,
    status_code=status.HTTP_200_OK,
    summary="Update a product",
    description="""
Update an existing product belonging to the authenticated user.

- Requires JWT authentication.
- Only the owner of the product can update it.
- Allows updating all fields.
- Returns 200 with the updated product.
"""
)
def update_existing_product(
    product_id: int,
    update_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    # 1. Fetch product and ensure it belongs to the user
    product = get_product_by_id(db, product_id, current_user.id)

    # 2. Update product
    updated_product = update_product(db, product, update_data, current_user.id)

    return updated_product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
    description="""
Delete a product belonging to the authenticated user.

- Requires JWT authentication.
- Only the owner of the product can delete it.
- Returns 204 on success.
"""
)
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    # 1. Fetch product and ensure it belongs to the user
    product = get_product_by_id(db, product_id, current_user.id)

    # 2. Delete product
    delete_product(db, product)

    # 3. Return 204 (no content)
    return None
