from sqlalchemy import Column,Integer,String,Boolean
from sqlalchemy.orm import relationship

from app.database.connection import Base

class Warehouse(Base):
    __tablename__="warehouses"
    
    id=Column(Integer,primary_key=True)
    name=Column(String(100),nullable=False,unique=True)
    location=Column(String(200),nullable=False)
    is_active=Column(Boolean,default=True)
    
    stocks=relationship("WarehouseStock",back_populates="warehouse")