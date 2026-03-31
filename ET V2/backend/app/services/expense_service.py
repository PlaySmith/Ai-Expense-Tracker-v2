from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import hashlib
import shutil
import os

from ..models.models import Expense
from ..schemas.expense_schema import ExpenseCreate
from ..utils.logger import LoggerMixin
from ..utils.error_handlers import (
    DatabaseError, OCRError, ParserError, 
    FileUploadError, DuplicateExpenseError
)
from .ocr_service import OCRService
from .parser_service import ParserService


class ExpenseService(LoggerMixin):
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.ocr = OCRService()
        self.parser = ParserService()


    def process_receipt(self, image_path: str) -> Dict[str, Any]:
        
        # V2 Workflow:
        # 1. Validate/save image
        # 2. OCR regions
        # 3. Parse structured
        # 4. Create expense with flags
        
        try:
            # 1. Validate
            self.ocr.validate_image(image_path)
            
            # 2. OCR
            ocr_data = self.ocr.process_image(image_path)
            
            # 3. Parse
            parsed = self.parser.parse_receipt(ocr_data)
            
            # 4. Sanitize
            amount = parsed['amount'] or 0.01
            merchant = parsed['merchant'] or 'Unknown'
            
            expense_data = ExpenseCreate(
                amount=amount,
                merchant=merchant,
                category=parsed['category'],
                date=parsed['date'],
                description=f"ET V2 Auto: conf={ocr_data['conf_overall']:.2f}",
                receipt_image_path=image_path,
                ocr_confidence=ocr_data['conf_overall']
            )
            
            # 5. Save
            expense = self._create_expense(expense_data, parsed)
            
            return {
                'success': True,
                'expense': expense,
                'extracted_data': parsed,
                'warnings': [] if not parsed['requires_review'] else ['Low confidence - please review']
            }
            
        except Exception as e:
            self.logger.error(f"Process failed: {e}")
            raise DatabaseError(str(e))

    def _create_expense(self, data: ExpenseCreate, parsed: dict) -> Expense:
        expense = Expense(**data.dict())
        expense.requires_review = parsed['requires_review']
        expense.extracted_raw = str(parsed['extracted_raw'])
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    # Reuse get/list/update/delete from V1 patterns (simplified here)
    def get_expenses(self, limit: int = 50) -> List[Expense]:
        return self.db.query(Expense).limit(limit).all()

    def get_stats(self) -> Dict[str, Any]:
        """
        Stats for dashboard
        """
        expenses = self.db.query(Expense).all()
        total_count = len(expenses)
        total_amount = sum(e.amount for e in expenses)
        average_amount = total_amount / total_count if total_count > 0 else 0
        review_count = len([e for e in expenses if getattr(e, 'requires_review', False)])
        return {
            'total_count': total_count,
            'total_amount': float(total_amount),
            'average_amount': float(average_amount),
            'review_count': review_count
        }

