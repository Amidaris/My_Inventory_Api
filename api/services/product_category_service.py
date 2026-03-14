from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.models.db_product_category import ProductCategoryDB
from api.models.product_category import ProductCategoryCreate, ProductCategoryUpdate
from api.models.db_product import ProductDB


def create_category(db: Session, user_id: int, data: ProductCategoryCreate):
    # Check if category with the same name already exists for this user
    existing = (
        db.query(ProductCategoryDB)
        .filter(
            ProductCategoryDB.user_id == user_id,
            ProductCategoryDB.name == data.name
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    new_category = ProductCategoryDB(
        user_id=user_id,
        name=data.name
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


def get_categories_for_user(db: Session, user_id: int):
    return (
        db.query(ProductCategoryDB)
        .filter(ProductCategoryDB.user_id == user_id)
        .order_by(ProductCategoryDB.created_at.desc())
        .all()
    )


def get_category_by_id(db: Session, category_id: int, user_id: int):
    category = (
        db.query(ProductCategoryDB)
        .filter(
            ProductCategoryDB.id == category_id,
            ProductCategoryDB.user_id == user_id
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


def update_category(db: Session, category: ProductCategoryDB, data: ProductCategoryUpdate, user_id: int):

    # Update name only if provided
    if data.name is not None:

        # Check uniqueness
        existing = (
            db.query(ProductCategoryDB)
            .filter(
                ProductCategoryDB.user_id == user_id,
                ProductCategoryDB.name == data.name,
                ProductCategoryDB.id != category.id
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another category with this name already exists"
            )
        category.name = data.name

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: ProductCategoryDB, user_id: int):
    # Check if category contains products
    products_count = (
        db.query(ProductDB)
        .filter(ProductDB.category_id == category.id)
        .count()
    )

    if products_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category that contains products"
        )

    db.delete(category)
    db.commit()