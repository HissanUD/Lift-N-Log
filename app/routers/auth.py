from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import models
from app.db.database import get_db
from app.schemas import UserCreate, UserRead, Token
from app.core.security import hash_password,verify_password, create_access_token
from app.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm

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
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db),):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect details")
    if user.hashed_password is None:
        raise HTTPException(status_code=401, detail="Incorrect details")
    
    verification = verify_password(form_data.password,str(user.hashed_password))
    
    if verification is False:
        raise HTTPException(status_code=401, detail="Incorrect details")
    
    verified_user_id = {"sub": str(user.id)}
    token = create_access_token(verified_user_id)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me",response_model=UserRead)
async def get_me(current_user:models.User=Depends(get_current_user)):
    return current_user
