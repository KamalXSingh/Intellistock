from sqlalchemy import Column,Integer,String,Text 
from app.database.connection import Base
from sqlalchemy.orm import relationship

class Supplier(Base):
    __tablename__ ="suppliers"
    
    
    id=Column(Integer,primary_key=True)
    name=Column(String,nullable=False)
    products=relationship("Product",back_populates='supplier')
    