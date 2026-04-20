from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date
from calendar import monthrange
from ..models.models import Budget, Expense
from ..utils.logger import LoggerMixin
from ..utils.error_handlers import BudgetError


class BudgetService(LoggerMixin):
    def __init__(self, db: Session):
        super().__init__()
        self.db = db

    def create_budget(self, user_id: int, category: str, budget_amount: float, period: str) -> Budget:
        """Create a new budget for user"""
        try:
            # Check for duplicate budget (same user, same category, same period)
            existing = self.db.query(Budget).filter(
                and_(
                    Budget.owner_id == user_id,
                    Budget.category == category,
                    Budget.period == period
                )
            ).first()

            if existing:
                raise BudgetError(f"Budget already exists for {category} ({period})")

            budget = Budget(
                category=category,
                budget_amount=budget_amount,
                period=period,
                owner_id=user_id
            )
            self.db.add(budget)
            self.db.commit()
            self.db.refresh(budget)
            self.logger.info(f"Budget created: {category} - {budget_amount} ({period})")
            return budget
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Create budget failed: {e}")
            raise

    def get_budgets(self, user_id: int) -> list[Budget]:
        """Get all budgets for user"""
        try:
            budgets = self.db.query(Budget).filter(Budget.owner_id == user_id).all()
            return budgets
        except Exception as e:
            self.logger.error(f"Get budgets failed: {e}")
            raise

    def get_budget(self, budget_id: int, user_id: int) -> Budget:
        """Get single budget by ID (verify ownership)"""
        try:
            budget = self.db.query(Budget).filter(
                and_(Budget.id == budget_id, Budget.owner_id == user_id)
            ).first()
            if not budget:
                raise BudgetError("Budget not found")
            return budget
        except Exception as e:
            self.logger.error(f"Get budget failed: {e}")
            raise

    def update_budget(self, budget_id: int, user_id: int, budget_amount: float = None, period: str = None) -> Budget:
        """Update budget amount or period"""
        try:
            budget = self.get_budget(budget_id, user_id)
            
            if budget_amount is not None:
                budget.budget_amount = budget_amount
            if period is not None:
                budget.period = period
            
            budget.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(budget)
            self.logger.info(f"Budget updated: {budget.category}")
            return budget
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Update budget failed: {e}")
            raise

    def delete_budget(self, budget_id: int, user_id: int) -> None:
        """Delete a budget"""
        try:
            budget = self.get_budget(budget_id, user_id)
            self.db.delete(budget)
            self.db.commit()
            self.logger.info(f"Budget deleted: {budget.category}")
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Delete budget failed: {e}")
            raise

    def _get_period_dates(self, period: str) -> tuple[date, date]:
        """Get start and end dates for period (monthly/yearly)"""
        today = date.today()
        
        if period == "monthly":
            # Current month: 1st to last day
            start = date(today.year, today.month, 1)
            last_day = monthrange(today.year, today.month)[1]
            end = date(today.year, today.month, last_day)
        elif period == "yearly":
            # Current year: Jan 1 to Dec 31
            start = date(today.year, 1, 1)
            end = date(today.year, 12, 31)
        else:
            raise BudgetError(f"Invalid period: {period}")
        
        return start, end

    def get_spent_amount(self, user_id: int, category: str, period: str) -> float:
        """Calculate spent amount for category in period"""
        try:
            start_date, end_date = self._get_period_dates(period)
            
            spent = self.db.query(Expense).filter(
                and_(
                    Expense.owner_id == user_id,
                    Expense.category == category,
                    Expense.date >= start_date,
                    Expense.date <= end_date
                )
            ).with_entities(func.sum(Expense.amount)).scalar()
            
            return float(spent or 0)
        except Exception as e:
            self.logger.error(f"Calculate spent failed: {e}")
            raise

    def get_budget_status(self, user_id: int, category: str, budget_amount: float, period: str) -> dict:
        """Get budget status with spending info"""
        try:
            spent = self.get_spent_amount(user_id, category, period)
            remaining = budget_amount - spent
            percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
            
            # Determine status
            if percentage > 100:
                status = "exceeded"
            elif percentage >= 80:
                status = "critical"
            elif percentage >= 50:
                status = "warning"
            else:
                status = "safe"
            
            return {
                "spent_amount": spent,
                "remaining_amount": remaining,  # Can be negative if overspent
                "percentage": min(100, percentage) if percentage <= 100 else percentage,
                "status": status
            }
        except Exception as e:
            self.logger.error(f"Get budget status failed: {e}")
            raise

    def get_budgets_with_progress(self, user_id: int) -> dict:
        """Get all budgets with spending progress"""
        try:
            budgets = self.get_budgets(user_id)
            budget_list = []
            total_budget = 0
            total_spent = 0
            
            for budget in budgets:
                status_info = self.get_budget_status(
                    user_id, budget.category, budget.budget_amount, budget.period
                )
                
                budget_dict = {
                    "id": budget.id,
                    "category": budget.category,
                    "budget_amount": budget.budget_amount,
                    "period": budget.period,
                    "spent_amount": status_info["spent_amount"],
                    "remaining_amount": status_info["remaining_amount"],
                    "percentage": status_info["percentage"],
                    "status": status_info["status"],
                    "created_at": budget.created_at,
                    "updated_at": budget.updated_at
                }
                budget_list.append(budget_dict)
                total_budget += budget.budget_amount
                total_spent += status_info["spent_amount"]
            
            return {
                "budgets": budget_list,
                "total_budget": total_budget,
                "total_spent": total_spent,
                "total_remaining": max(0, total_budget - total_spent)
            }
        except Exception as e:
            self.logger.error(f"Get budgets with progress failed: {e}")
            raise


# Import at end to avoid circular imports
from sqlalchemy import func
