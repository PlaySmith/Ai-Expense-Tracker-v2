from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import User
from ..schemas.user_schema import UserRegister
from ..utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
    oauth2_scheme,
)
from ..utils.logger import LoggerMixin


class AuthService(LoggerMixin):
    def __init__(self, db: Session):
        super().__init__()
        self.db = db

    def create_user(self, user: UserRegister) -> User:
        hashed_password = get_password_hash(user.password)
        existing = self.db.query(User).filter(User.email == user.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        phone = (user.phone or "").strip() or None
        db_user = User(
            email=user.email,
            full_name=user.full_name.strip(),
            phone=phone,
            hashed_password=hashed_password,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        self.logger.info("Created user: %s", db_user.email)
        return db_user

    def authenticate_user(self, email: str, password: str) -> User:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    @staticmethod
    def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: Optional[str] = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user

    def update_user_profile(self, user: User, full_name: Optional[str] = None, phone: Optional[str] = None) -> User:
        if full_name is not None:
            user.full_name = full_name.strip()
        if phone is not None:
            user.phone = phone.strip() or None
        self.db.commit()
        self.db.refresh(user)
        self.logger.info("Updated user profile: %s", user.email)
        return user

    def update_user_avatar(self, user: User, image_path: str) -> User:
        user.profile_image_path = image_path
        self.db.commit()
        self.db.refresh(user)
        self.logger.info("Updated user avatar: %s", user.email)
        return user
