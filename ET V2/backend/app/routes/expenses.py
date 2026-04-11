from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
from datetime import datetime

from ..database import get_db
from ..services.expense_service import ExpenseService
from ..services.auth_service import AuthService
from ..models.models import User, Expense
from ..schemas.expense_schema import (
    ExpenseCreate,
    ExpenseListResponse,
    UploadResponse,
)
from ..utils.error_handlers import FileUploadError

router = APIRouter(prefix="/expenses", tags=["expenses"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload", response_model=UploadResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    if not file.filename:
        raise HTTPException(400, "No file")
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise FileUploadError(f"Invalid file type: {ext}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    safe_name = f"receipt_{timestamp}{ext}"
    file_path = UPLOAD_DIR / safe_name

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    if file_path.stat().st_size > MAX_FILE_SIZE:
        file_path.unlink(missing_ok=True)
        raise FileUploadError("File too large (max 10MB)")

    service = ExpenseService(db)
    result = service.process_receipt(str(file_path), owner_id=current_user.id)

    return UploadResponse(
        success=result["success"],
        message=result.get("message", "Receipt processed"),
        expense=result["expense"],
        extracted_data=result.get("extracted_data"),
        warnings=result.get("warnings", []),
    )


@router.get("/", response_model=ExpenseListResponse)
async def list_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    service = ExpenseService(db)
    expenses = service.get_expenses(current_user.id)
    return ExpenseListResponse(
        expenses=expenses, total=len(expenses), page=1, page_size=50
    )


@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    service = ExpenseService(db)
    return service.get_stats(current_user.id)


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "expense-tracker-v2", "version": "2.0.0"}


@router.post("/manual")
async def create_manual(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    expense_manual = Expense(**expense.model_dump(), owner_id=current_user.id)
    expense_manual.requires_review = False
    expense_manual.ocr_confidence = 1.0
    expense_manual.extracted_raw = "manual entry"
    db.add(expense_manual)
    db.commit()
    db.refresh(expense_manual)
    return {"success": True, "expense": expense_manual}
