from sqlalchemy import Column, Integer, String
from app.database.connection import Base
from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(300), nullable=True)
    products=relationship("Product",back_populates="category")