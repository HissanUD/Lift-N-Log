from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.schemas import UserCreate, UserRead, Token, UserLogin
from app.security import hash_password,verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register",status_code=201,response_model=UserRead)
async def register_user(details:UserCreate,db:Session=Depends(get_db)):
    
    duplicate_check = db.query(models.User).filter(models.User.email == details.email).first()
    if duplicate_check:
        raise HTTPException(status_code=409,detail="Email already registered")
    
    user = models.User(
        user_name = details.user_name,
        email = details.email,
        hashed_password = hash_password(details.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login",response_model=Token)
async def login_user(details:UserLogin,db:Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == details.email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect details")
    if user.hashed_password is None:
        raise HTTPException(status_code=401, detail="Incorrect details")
    
    verification = verify_password(details.password,str(user.hashed_password))
    
    if verification is False:
        raise HTTPException(status_code=401, detail="Incorrect details")
    
    verified_user_id = {"sub": str(user.id)}
    token = create_access_token(verified_user_id)
    return {"access_token": token, "token_type": "bearer"}

