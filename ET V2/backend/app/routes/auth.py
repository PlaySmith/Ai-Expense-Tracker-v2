from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
from pathlib import Path

from ..database import get_db
from ..schemas.user_schema import UserRegister, UserLogin, UserResponse, Token, UserProfileUpdate
from ..services.auth_service import AuthService
from ..models.models import User
from ..utils.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
def register(user: UserRegister, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    db_user = auth_service.create_user(user)
    access_token = create_access_token(data={"sub": db_user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(user_data.email, user_data.password)
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(AuthService.get_current_user)):
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)
    updated_user = auth_service.update_user_profile(
        current_user,
        full_name=profile_data.full_name,
        phone=profile_data.phone,
    )
    return updated_user


@router.post("/profile/avatar", response_model=UserResponse)
def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only images allowed.")

    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024
    if file.size and file.size > max_size:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB allowed.")

    # Create uploads directory if it doesn't exist
    upload_dir = Path("uploads/avatars")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    import uuid
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename

    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save file")

    # Update user profile with image path (store relative path within uploads directory)
    auth_service = AuthService(db)
    relative_path = f"avatars/{unique_filename}"
    updated_user = auth_service.update_user_avatar(current_user, relative_path)
    return updated_user
