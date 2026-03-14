from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.config.db import get_db
from api.services.auth_service import get_current_active_user
from api.services.product_category_service import create_category, get_categories_for_user, get_category_by_id, update_category, delete_category
from api.models.product_category import ProductCategory, ProductCategoryCreate, ProductCategoryUpdate
from api.models.db_user import UserDB

router = APIRouter(prefix="/product-categories", tags=["Product Categories"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductCategory,
    summary="Create a new product category",
    description="""
Create a new category for grouping products.

- Requires JWT authentication.
- Category name must be unique per user.
- Returns 201 with the created category.
"""
)
def create_new_category(
    category_data: ProductCategoryCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    return create_category(db, current_user.id, category_data)


@router.get(
    "/",
    response_model=list[ProductCategory],
    status_code=status.HTTP_200_OK,
    summary="Get all product categories for the authenticated user",
    description="""
Returns all categories belonging to the logged-in user.

- Requires JWT authentication.
- Returns an empty list if no categories exist.
- Prepared for future pagination.
"""
)
def list_categories(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    return get_categories_for_user(db, current_user.id)


@router.put(
    "/{category_id}",
    response_model=ProductCategory,
    status_code=status.HTTP_200_OK,
    summary="Update a product category",
    description="""
Update an existing category belonging to the authenticated user.

- Requires JWT authentication.
- Category name must remain unique per user.
- Returns 200 with the updated category.
"""
)
def update_existing_category(
    category_id: int,
    data: ProductCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    # 1. Fetch category and ensure it belongs to the user
    category = get_category_by_id(db, category_id, current_user.id)

    # 2. Update category
    updated = update_category(db, category, data, current_user.id)

    return updated


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product category",
    description="""
Delete a category belonging to the authenticated user.

- Requires JWT authentication.
- Cannot delete a category that contains products.
- Returns 204 on success.
"""
)
def delete_existing_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    # 1. Fetch category and ensure it belongs to the user
    category = get_category_by_id(db, category_id, current_user.id)

    # 2. Delete category (with validation)
    delete_category(db, category, current_user.id)

    # 3. Return 204 (no content)
    return None
