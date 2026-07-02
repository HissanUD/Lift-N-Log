from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db import models
from app.errors import AuthenticationError, ConflictError
from app.schemas import UserCreate


def register_user(details: UserCreate, db: Session) -> models.User:
    duplicate_check = db.query(models.User).filter(models.User.email == details.email).first()

    if duplicate_check:
        raise ConflictError("Email already registered")

    user = models.User(
        user_name=details.user_name,
        email=details.email,
        hashed_password=hash_password(details.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login_user(email: str, password: str, db: Session) -> dict[str, str]:
    user = db.query(models.User).filter(models.User.email == email).first()

    if user is None or user.hashed_password is None:
        raise AuthenticationError("Incorrect details")

    verification = verify_password(password, str(user.hashed_password))

    if verification is False:
        raise AuthenticationError("Incorrect details")

    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}
