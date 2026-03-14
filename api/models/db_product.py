from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from api.config.db import Base

class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    sku = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    base_price = Column(Float, nullable=False)
    vat = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("product_categories.id"), nullable=True)
    stock = Column(Float, nullable=False, server_default="1")

    category = relationship("ProductCategoryDB", back_populates="products")

