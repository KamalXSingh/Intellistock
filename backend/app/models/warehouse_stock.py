from sqlalchemy import(
    Column,Integer,ForeignKey,
    UniqueConstraint,CheckConstraint
)

from sqlalchemy.orm import relationship
from app.database.connection import Base

class WarehouseStock(Base):
    __tablename__="warehouse_stock"
    
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "warehouse_id",
            name="uq_product_warehouse"
        ),
        CheckConstraint(
            "quantity >= 0",
            name="ck_warehouse_stock_quantity"
        )
    )
    
    id=Column(Integer,primary_key=True)
    
    product_id=Column(Integer,ForeignKey("products.id"),nullable=False)
    warehouse_id=Column(Integer,ForeignKey("warehouses.id"),nullable=False)
    
    quantity=Column(Integer,nullable=False,default=0)
    reorder_level=Column(Integer,nullable=False,default=10)
    
    product=relationship("Product",back_populates="warehouse_stocks")
    warehouse=relationship("Warehouse",back_populates="stocks")