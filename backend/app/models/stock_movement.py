from sqlalchemy import Column,Integer,String,ForeignKey, DateTime,CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base

class StockMovement(Base):
    __tablename__ ="stock_movements"
    
    __table_args__ = (
    CheckConstraint(
        "quantity > 0",
        name="ck_stock_movement_quantity"
    ),
    CheckConstraint(
        "movement_type IN ('STOCK_IN', 'STOCK_OUT', 'TRANSFER_IN', 'TRANSFER_OUT')",
        name="ck_stock_movement_type"
    )
)
    
    id=Column(Integer,primary_key=True)
    
    product_id=Column(Integer,ForeignKey("products.id"),nullable=False)
    warehouse_id=Column(Integer,ForeignKey("warehouses.id"),nullable=False)
    
    movement_type=Column(String(20),nullable=False)
    quantity=Column(Integer,nullable=False)
    
    created_at=Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    product = relationship("Product")
    warehouse = relationship("Warehouse")