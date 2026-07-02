from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import models
from app.db.database import get_db
from app.schemas import UserCreate, UserRead, Token
from app.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from app.errors import AuthenticationError, ConflictError
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register",status_code=201,response_model=UserRead)
async def register_user(details:UserCreate,db:Session=Depends(get_db)):
    try:
        return auth_service.register_user(details, db)
    except ConflictError as error:
        raise HTTPException(status_code=409, detail=str(error))

@router.post("/login",response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db),):
    try:
        return auth_service.login_user(form_data.username, form_data.password, db)
    except AuthenticationError as error:
        raise HTTPException(status_code=401, detail=str(error))

@router.get("/me",response_model=UserRead)
async def get_me(current_user:models.User=Depends(get_current_user)):
    return current_user
