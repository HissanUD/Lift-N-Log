from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from app.database import get_db
from sqlalchemy.orm import Session
from app.config import SECRET_KEY,ALGORITHM
from app import models
from jose import JWTError,jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token:str= Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
      status_code=401,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},)
    assert SECRET_KEY is not None
    assert ALGORITHM is not None

    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
      raise credentials_exception
    return user


    
    