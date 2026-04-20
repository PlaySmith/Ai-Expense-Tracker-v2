from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BudgetCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    budget_amount: float = Field(..., gt=0)
    period: str = Field(..., pattern="^(monthly|yearly)$")

    class Config:
        json_schema_extra = {
            "example": {
                "category": "Food & Dining",
                "budget_amount": 5000.00,
                "period": "monthly"
            }
        }


class BudgetUpdate(BaseModel):
    budget_amount: Optional[float] = Field(None, gt=0)
    period: Optional[str] = Field(None, pattern="^(monthly|yearly)$")


class BudgetResponse(BaseModel):
    id: int
    category: str
    budget_amount: float
    period: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BudgetWithProgress(BaseModel):
    id: int
    category: str
    budget_amount: float
    period: str
    spent_amount: float
    remaining_amount: float
    percentage: float  # 0-100
    status: str  # "safe" (< 50%), "warning" (50-80%), "exceeded" (> 100%), "critical" (80-100%)
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BudgetListResponse(BaseModel):
    budgets: list[BudgetWithProgress]
    total_budget: float
    total_spent: float
    total_remaining: float
