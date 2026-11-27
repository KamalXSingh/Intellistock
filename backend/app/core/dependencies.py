from fastapi import Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import jwt
from jwt.exceptions import InvalidTokenError

from app.database.connection import get_db
from app.models.user import User
from app.core.security import SECRET_KEY,ALGORITHM

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token:str=Depends(oauth2_scheme),
    db:Session=Depends(get_db)
):
    credentials_exception=HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        header={"WWW-Authentication":"Bearer"}
    )
    
    try:
        payload=jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        user_id=payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
        
    except InvalidTokenError:
        raise credentials_exception

    user=db.query(User).filter(
        User.id==int(user_id)
    ).first()
    
    if not isinstance(user_id, str) or not user_id.isdigit():
        raise credentials_exception
    
    
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )
        
    return user
