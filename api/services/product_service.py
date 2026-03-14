from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from api.models.db_product import ProductDB
from api.models.db_product_category import ProductCategoryDB
from api.models.product import ProductUpdate

def get_products_for_user(db: Session, user_id: int): 
    """ 
    Fetch all products belonging to a specific user. 
    """ 
    return ( 
        db.query(ProductDB) 
        .filter(ProductDB.user_id == user_id) 
        .all() 
    ) 


def create_product(db: Session, user_id: int, name: str, sku: str, unit: str, base_price: float, vat: float, category_id: int | None):

    # 1. Validate category
    if category_id is not None:
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category does not exist or does not belong to the user"
            )

    # 2. Check if product with same SKU exists
    existing = (
        db.query(ProductDB)
        .filter(
            ProductDB.user_id == user_id,
            ProductDB.sku == sku
        )
        .first()
    )

    if existing:
        existing.stock += 1
        db.commit()
        db.refresh(existing)
        return existing

    # 3. Create new product
    new_product = ProductDB(
        user_id=user_id,
        name=name,
        sku=sku,
        unit=unit,
        base_price=base_price,
        vat=vat,
        category_id=category_id,
        stock=1
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


def get_product_by_id(db: Session, product_id: int, user_id: int):
    """
    Fetch a single product by ID, ensuring it belongs to the given user.
    """
    product = (
        db.query(ProductDB)
        .filter(ProductDB.id == product_id, ProductDB.user_id == user_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


def update_product(db: Session, product: ProductDB, data: ProductUpdate, user_id: int):
    """
    Update an existing product with provided fields.
    """
    # Validate category if provided
    if data.category_id is not None:
        category = (
            db.query(ProductCategoryDB)
            .filter(
                ProductCategoryDB.id == data.category_id,
                ProductCategoryDB.user_id == user_id
            )
            .first()
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category does not exist"
            )

    update_data = data.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: ProductDB):
    db.delete(product)
    db.commit()



