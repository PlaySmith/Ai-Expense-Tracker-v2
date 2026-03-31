from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.user_schema import UserCreate, UserResponse, TokenData
from app.utils.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    ALGORITHM,
    SECRET_KEY
)
from app.utils.logger import LoggerMixin
import logging

logger = logging.getLogger(__name__)

class AuthService(LoggerMixin):
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

    def __init__(self, db: Session):
        self.db = db
        super().__init__()

    def create_user(self, user: UserCreate) -> User:
        """Create new user"""
        try:
            # Hash password (automatically truncated to 72 chars by security.py)
            hashed_password = get_password_hash(user.password)
            
            # Check if user exists
            existing = self.db.query(User).filter(User.email == user.email).first()
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )
            
            # Create user
            db_user = User(
                email=user.email,
                hashed_password=hashed_password
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            self.logger.info(f"Created user: {db_user.email}")
            return db_user
            
        except HTTPException:
            raise
        except ValueError as e:
            self.db.rollback()
            self.logger.error(f"Validation error creating user: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid input data")
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to create user: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create user")

    def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate user and return if valid"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user

    @staticmethod
    def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        """Get current user from token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        
        return user

