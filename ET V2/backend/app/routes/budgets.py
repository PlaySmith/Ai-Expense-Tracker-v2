from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.budget_service import BudgetService
from ..services.auth_service import AuthService
from ..models.models import User
from ..schemas.budget_schema import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
    BudgetListResponse,
    BudgetWithProgress
)

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("/", response_model=BudgetResponse)
async def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Create a new budget for user"""
    service = BudgetService(db)
    budget = service.create_budget(
        user_id=current_user.id,
        category=budget_data.category,
        budget_amount=budget_data.budget_amount,
        period=budget_data.period
    )
    return budget


@router.get("/", response_model=BudgetListResponse)
async def list_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get all budgets for current user with spending progress"""
    service = BudgetService(db)
    result = service.get_budgets_with_progress(current_user.id)
    return BudgetListResponse(**result)


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get single budget by ID"""
    service = BudgetService(db)
    budget = service.get_budget(budget_id, current_user.id)
    return budget


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Update budget"""
    service = BudgetService(db)
    budget = service.update_budget(
        budget_id=budget_id,
        user_id=current_user.id,
        budget_amount=budget_data.budget_amount,
        period=budget_data.period
    )
    return budget


@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Delete a budget"""
    service = BudgetService(db)
    service.delete_budget(budget_id, current_user.id)
    return {"success": True, "message": "Budget deleted"}


@router.get("/{budget_id}/status")
async def get_budget_status(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get budget status with spending info"""
    service = BudgetService(db)
    budget = service.get_budget(budget_id, current_user.id)
    status = service.get_budget_status(
        current_user.id,
        budget.category,
        budget.budget_amount,
        budget.period
    )
    return {
        "budget_id": budget.id,
        "category": budget.category,
        "budget_amount": budget.budget_amount,
        "period": budget.period,
        **status
    }
