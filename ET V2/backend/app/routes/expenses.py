from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from pathlib import Path
import os
import shutil
from datetime import datetime

from ..database import get_db
from ..services.expense_service import ExpenseService
from ..schemas.expense_schema import (
    ExpenseResponse, ExpenseCreate, ExpenseListResponse, UploadResponse
)
# from ..utils.error_handlers import FileUploadError

router = APIRouter(prefix="/expenses", tags=["expenses"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload", response_model=UploadResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload receipt → OCR → Parse → Save.
    Returns structured data + flags.
    """
    if not file.filename:
        raise HTTPException(400, "No file")
    
    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    safe_name = f"receipt_{timestamp}{Path(file.filename).suffix}"
    file_path = UPLOAD_DIR / safe_name
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    service = ExpenseService(db)
    result = service.process_receipt(str(file_path))
    
    return UploadResponse(
        success=result['success'],
        message=result.get('message', 'Receipt processed'),
        expense=result['expense'],
        extracted_data=result.get('extracted_data'),
        warnings=result.get('warnings', [])
    )

@router.get("/", response_model=ExpenseListResponse)
async def list_expenses(db: Session = Depends(get_db)):
    service = ExpenseService(db)
    expenses = service.get_expenses()
    from ..models.models import Expense
    return ExpenseListResponse(expenses=[ExpenseResponse.model_validate(e) for e in expenses], total=len(expenses), page=1, page_size=50)

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    service = ExpenseService(db)
    return service.get_stats()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "expense-tracker-v2", "version": "2.0.0"}

@router.post("/manual")
async def create_manual(expense: ExpenseCreate, db: Session = Depends(get_db)):
    service = ExpenseService(db)
    # Simple manual create
    from ..models.models import Expense
    expense_manual = Expense(**expense.dict(), requires_review=False, ocr_confidence=1.0, extracted_raw="manual entry")
    db.add(expense_manual)
    db.commit()
    db.refresh(expense_manual)
    return {"success": True, "expense": expense_manual}

