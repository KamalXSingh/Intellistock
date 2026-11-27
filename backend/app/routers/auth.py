from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.user import UserCreate,UserResponse,UserResponseEnvelope,TokenResponse,UserLogin
from app.core.security import hash_password,verify_password,create_access_token

router=APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register",response_model=UserResponseEnvelope)
def register_user(
    user_data:UserCreate,
    db:Session=Depends(get_db)
):
    existing_user=db.query(User).filter(
        User.email==user_data.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )
    
    new_user=User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role="staff"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return{
        "success":True,
        "message":"User registered successfully",
        "data":new_user
    }
    
@router.post("/login",response_model=TokenResponse)
def login_user(
    user_data:UserLogin,
    db:Session=Depends(get_db)
):
    user=db.query(User).filter(
        User.email==user_data.email
    ).first()
    
    if not user or not verify_password(user_data.password,user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )
        
    access_token=create_access_token({
        "sub":str(user.id),
        "role":user.role
    })
    
    return{
        "access_token":access_token,
        "token_type":"bearer"
    }
    
    





