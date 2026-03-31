from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from .user_schema import UserResponse



class ExpenseBase(BaseModel):
    """Base expense schema"""
    amount: float = Field(..., gt=0, description="Expense amount must be greater than 0")
    merchant: Optional[str] = Field(None, max_length=255, description="Merchant name")
    category: Optional[str] = Field(None, max_length=100, description="Expense category")
    date: Optional[datetime] = Field(None, description="Expense date")
    description: Optional[str] = Field(None, max_length=500, description="Additional description")


class ExpenseCreate(ExpenseBase):
    """Schema for creating a new expense"""
    receipt_image_path: Optional[str] = Field(None, description="Path to uploaded receipt image")
    ocr_confidence: Optional[float] = Field(None, ge=0, le=100, description="OCR confidence score")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return round(v, 2)  # Round to 2 decimal places


class ExpenseUpdate(BaseModel):
    """Schema for updating an existing expense"""
    amount: Optional[float] = Field(None, gt=0)
    merchant: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    date: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=500)
    
    @validator('amount')
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Amount must be greater than 0')
        return round(v, 2) if v else v


class ExpenseResponse(ExpenseBase):
    """Schema for expense response"""
    id: int
    receipt_image_path: Optional[str] = None
    ocr_confidence: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models


class UploadResponse(BaseModel):
    """Schema for receipt upload response"""
    success: bool
    message: str
    expense: Optional[ExpenseResponse] = None
    extracted_data: Optional[dict] = None
    warnings: Optional[list] = []
    errors: Optional[list] = []
    
    class Config:
        from_attributes = True


class ExpenseListResponse(BaseModel):
    """Schema for list of expenses"""
    expenses: list[ExpenseResponse]
    total: int
    page: int = 1
    page_size: int = 10
