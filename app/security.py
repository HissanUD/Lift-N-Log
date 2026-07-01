from passlib.context import CryptContext
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES,SECRET_KEY,ALGORITHM
from datetime import datetime, timedelta, timezone
from jose import jwt



pwd_context = CryptContext(schemes=["bcrypt"],deprecated= "auto")

def hash_password(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password:str,hashed_password:str) -> bool:
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data:dict)->str:
    to_encode = data.copy()
    expiry = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expiry})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt