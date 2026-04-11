from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal

class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0)
    merchant: str
    category: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    date: Optional[datetime] = None
    description: Optional[str] = None
    receipt_image_path: Optional[str] = None
    ocr_confidence: Optional[float] = None

class ExpenseUpdate(ExpenseBase):
    date: Optional[datetime] = None
    description: Optional[str] = None
    requires_review: Optional[bool] = False

class ExpenseResponse(ExpenseBase):
    id: int
    date: Optional[datetime] = None
    ocr_confidence: Optional[float]
    requires_review: bool
    extracted_raw: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    success: bool
    message: str
    expense: Optional[ExpenseResponse] = None
    extracted_data: Optional[Dict[str, Any]] = None
    warnings: List[str] = []
    errors: List[str] = []

class ExpenseListResponse(BaseModel):
    expenses: List[ExpenseResponse]
    total: int
    page: int
    page_size: int

