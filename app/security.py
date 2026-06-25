from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jose import jwt



load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM= os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES_RAW=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

if SECRET_KEY is None or ALGORITHM is None or ACCESS_TOKEN_EXPIRE_MINUTES_RAW is None:
    raise RuntimeError("ENV VALUES NOT LOADED")

ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES_RAW)

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