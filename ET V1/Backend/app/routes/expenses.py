from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
from pathlib import Path
import logging

from app.database import get_db
from app.services.expense_service import ExpenseService
from app.services.auth_service import AuthService
from app.schemas.expense_schema import (
    ExpenseResponse, 
    ExpenseCreate, 
    ExpenseUpdate,
    ExpenseListResponse,
    UploadResponse
)

from app.utils.error_handlers import (
    ValidationError,
    FileUploadError,
    DatabaseError
)

router = APIRouter(prefix="/expenses", tags=["expenses"])

# Setup upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/manual", response_model=ExpenseResponse)
async def create_manual_expense(
    expense_data: ExpenseCreate,
    current_user = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create manual expense (no OCR)
    """
    logger = logging.getLogger("api")
    logger.info(f"Manual expense creation for user {current_user.id}")
    
    expense_service = ExpenseService(db)
    expense = expense_service.create_expense(expense_data, current_user.id)
    
    return expense

@router.post("/upload", response_model=UploadResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    current_user = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):


    """
    Upload and process a receipt image
    
    - **file**: Receipt image file (JPG, PNG, etc.)
    - **owner_id**: Optional user ID
    """
    logger = logging.getLogger("api")
    logger.info(f"Upload request received: {file.filename}")
    
    # Validate file
    if not file.filename:
        raise ValidationError("No file provided")
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise FileUploadError(
            f"Invalid file type: {file_ext}. "
            f"Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Save uploaded file
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"receipt_{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            os.remove(file_path)
            raise FileUploadError(
                f"File too large: {file_size / 1024 / 1024:.1f}MB. "
                f"Maximum: {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
            )
        
        logger.info(f"File saved: {file_path}")
        
        # Process receipt
        expense_service = ExpenseService(db)
        result = expense_service.process_receipt(str(file_path), current_user.id)

        
        # Check if processing failed (e.g., amount not detected)
        if not result.get("success", True):
            # Return user-friendly error without crashing
            return UploadResponse(
                success=False,
                message=result.get("error", "Failed to process receipt"),
                expense=None,
                extracted_data=result.get("extracted_data"),
                warnings=result.get("warnings", []),
                errors=[result.get("error", "Unknown error")]
            )
        
        # Build success response
        return UploadResponse(
            success=True,
            message="Receipt processed successfully",
            expense=result["expense"],
            extracted_data=result["extracted_data"],
            warnings=result.get("warnings", []),
            errors=[]
        )

        
    except FileUploadError:
        raise
    except Exception as e:
        logger.error(f"Upload processing failed: {str(e)}", exc_info=True)
        # Clean up file if it exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise DatabaseError(f"Failed to process receipt: {str(e)}")


@router.get("/", response_model=ExpenseListResponse)
async def list_expenses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    owner_id: Optional[int] = Query(None, description="Filter by owner ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db)
):
    """
    Get list of expenses with optional filtering and pagination
    """
    logger = logging.getLogger("api")
    logger.info(f"List expenses request: skip={skip}, limit={limit}")
    
    expense_service = ExpenseService(db)
    
    expenses = expense_service.get_expenses(
        skip=skip,
        limit=limit,
        owner_id=owner_id,
        category=category,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get total count for pagination
    total = len(expenses)  # Simplified - in production, use count query
    
    return ExpenseListResponse(
        expenses=expenses,
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get("/stats")
async def get_expense_stats(
    owner_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get expense statistics and analytics
    """
    logger = logging.getLogger("api")
    logger.info("Stats request received")
    
    expense_service = ExpenseService(db)
    stats = expense_service.get_expense_stats(owner_id)
    
    return {
        "status": "success",
        "data": stats
    }


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific expense by ID
    """
    logger = logging.getLogger("api")
    logger.info(f"Get expense request: ID={expense_id}")
    
    expense_service = ExpenseService(db)
    expense = expense_service.get_expense(expense_id)
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing expense
    
    Allows manual correction of OCR-extracted data
    """
    logger = logging.getLogger("api")
    logger.info(f"Update expense request: ID={expense_id}")
    
    expense_service = ExpenseService(db)
    updated_expense = expense_service.update_expense(expense_id, expense_update)
    
    if not updated_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return updated_expense


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an expense
    """
    logger = logging.getLogger("api")
    logger.info(f"Delete expense request: ID={expense_id}")
    
    expense_service = ExpenseService(db)
    success = expense_service.delete_expense(expense_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return {
        "status": "success",
        "message": f"Expense {expense_id} deleted successfully"
    }
