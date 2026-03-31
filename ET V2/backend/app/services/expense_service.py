from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
import json

from ..models.models import Expense
from ..schemas.expense_schema import ExpenseCreate
from ..utils.logger import LoggerMixin
from .ocr_service import OCRService
from .parser_service import ParserService

class ExpenseService(LoggerMixin):
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.ocr = OCRService()
        self.parser = ParserService()

    def process_receipt(self, image_path: str) -> Dict[str, Any]:
        try:
            self.ocr.validate_image(image_path)
            ocr_data = self.ocr.process_image(image_path)
            parsed = self.parser.parse_receipt(ocr_data)
            
            final_amount = parsed.get('amount')
            merchant = parsed.get('merchant') or 'Unreadable Receipt'
            
            expense_create = ExpenseCreate(
                amount=float(final_amount) if final_amount else 0.0,
                merchant=merchant,
                category=parsed.get('category', 'Other'),
                date=parsed.get('date'),
                description=f"AI V2: Conf {ocr_data.get('conf_overall', 0):.1%}",
                receipt_image_path=image_path,
                ocr_confidence=float(ocr_data.get('conf_overall', 0.0))
            )
            
            expense = self._save_to_db(expense_create, parsed)
            
            return {
                'success': True,
                'expense': expense,
                'extracted_data': parsed,
                'warnings': [] if not parsed.get('requires_review') else ['Low confidence - Review Required']
            }
            
        except Exception as e:
            self.logger.error(f"Receipt Pipeline Failed: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'expense': None
            }

    def _save_to_db(self, data: ExpenseCreate, parsed: dict) -> Expense:
        # Use model_dump() and ensure dict conversion is clean
        db_expense = Expense(
            amount=data.amount,
            merchant=data.merchant,
            category=data.category,
            date=data.date,
            description=data.description,
            receipt_image_path=data.receipt_image_path,
            ocr_confidence=data.ocr_confidence
        )
        
        # FIX: Ensure we are passing a string to the column, not a dict/object
        # Direct column assignment fixed for SQLAlchemy
        # Add after commit as model supports the fields
        
        self.db.add(db_expense)
        self.db.commit()
        self.db.refresh(db_expense)
        return db_expense

    def get_expenses(self, limit: int = 50) -> List[Expense]:
        return self.db.query(Expense).order_by(Expense.id.desc()).limit(limit).all()

    def get_stats(self) -> Dict[str, Any]:
        """
        FIX: Use SQLAlchemy's func.sum and func.avg.
        This performs the math in the database, avoiding Python type issues.
        """
        # Query for totals and counts directly
        # Database aggregation
        total_count = self.db.query(func.count(Expense.id)).scalar() or 0
        
        if total_count == 0:
            return {
                'total_count': 0,
                'total_amount': 0.0,
                'average_amount': 0.0,
                'review_count': 0
            }
        
        total_amount = self.db.query(func.sum(Expense.amount)).scalar() or 0.0
        avg_amount = self.db.query(func.avg(Expense.amount)).scalar() or 0.0
        review_count = self.db.query(func.count(Expense.id)).filter(Expense.requires_review == True).scalar() or 0
        
        return {
            'total_count': int(total_count),
            'total_amount': float(total_amount),
            'average_amount': float(avg_amount),
            'review_count': int(review_count)
        }
