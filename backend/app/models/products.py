from sqlalchemy import Column,Integer,String,Numeric,Boolean,Text,ForeignKey
from app.database.connection import Base
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"
    
    id=Column(Integer,primary_key=True)
    name=Column(String(100),nullable=False)
    price=Column(Numeric(10,2),nullable=False)
    sku =  Column(String(30),unique=True,nullable=False)
    description=Column(Text,nullable=True)
    is_active=Column(Boolean,default=True)
    supplier_id=Column(Integer,ForeignKey("suppliers.id"),nullable=True)
    supplier=relationship("Supplier",back_populates='products')
    category = relationship("Category",back_populates="products")
    category_id = Column(Integer,ForeignKey("categories.id"),nullable=False)
    warehouse_stocks = relationship(
    "WarehouseStock",
    back_populates="product"
    )