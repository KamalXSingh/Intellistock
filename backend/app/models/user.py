from sqlalchemy import Column,Integer,String,Boolean,DateTime,CheckConstraint
from sqlalchemy.sql import func
from app.database.connection import Base

class User(Base):
    __tablename__="users"
    
    __table_args__=(
        CheckConstraint(
            "role IN ('admin','manager','staff')",
            name="ck_users_role"
        ),
    )
    
    id=Column(Integer,primary_key=True)
    name=Column(String,nullable=False)
    email=Column(String,nullable=False,unique=True,index=True)
    hashed_password=Column(String,nullable=False)
    role=Column(String,nullable=False,default='staff')
    is_active=Column(Boolean,nullable=False,default=True)
    created_at=Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )