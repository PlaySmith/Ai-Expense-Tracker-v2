from sqlalchemy.orm import Session
from typing import Dict, Any, List

from ..models.models import Expense
from ..schemas.expense_schema import ExpenseCreate
from ..utils.logger import LoggerMixin
from ..utils.error_handlers import DatabaseError
from .ocr_service import OCRService
from .parser_service import ParserService


class ExpenseService(LoggerMixin):
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.ocr = OCRService()
        self.parser = ParserService()

    def process_receipt(self, image_path: str, owner_id: int) -> Dict[str, Any]:
        try:
            self.ocr.validate_image(image_path)
            ocr_data = self.ocr.process_image(image_path)
            parsed = self.parser.parse_receipt(ocr_data)
            amount = parsed['amount'] or 0.01
            merchant = parsed['merchant'] or 'Unknown'
            expense_data = ExpenseCreate(
                amount=amount,
                merchant=merchant,
                category=parsed['category'],
                date=parsed['date'],
                description=f"ET V2 Auto: conf={ocr_data['conf_overall']:.2f}",
                receipt_image_path=image_path,
                ocr_confidence=ocr_data['conf_overall'],
            )
            expense = self._create_expense(expense_data, parsed, owner_id=owner_id)
            if parsed["requires_review"]:
                if parsed.get("date") is None:
                    warnings = [
                        "Receipt date not detected — please verify amount, merchant, and date."
                    ]
                else:
                    warnings = ["Low confidence — please review amount and merchant."]
            else:
                warnings = []
            return {
                "success": True,
                "expense": expense,
                "extracted_data": parsed,
                "warnings": warnings,
            }
        except Exception as e:
            self.logger.error("Process failed: %s", e)
            raise DatabaseError(str(e))

    def _create_expense(self, data: ExpenseCreate, parsed: dict, owner_id: int) -> Expense:
        payload = data.model_dump()
        expense = Expense(**payload, owner_id=owner_id)
        expense.requires_review = parsed["requires_review"]
        expense.extracted_raw = str(parsed["extracted_raw"])
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def get_expenses(self, owner_id: int, limit: int = 50) -> List[Expense]:
        return (
            self.db.query(Expense)
            .filter(Expense.owner_id == owner_id)
            .order_by(Expense.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_stats(self, owner_id: int) -> Dict[str, Any]:
        expenses = self.db.query(Expense).filter(Expense.owner_id == owner_id).all()
        total_count = len(expenses)
        total_amount = sum(e.amount for e in expenses)
        average_amount = total_amount / total_count if total_count > 0 else 0
        review_count = len(
            [e for e in expenses if getattr(e, "requires_review", False)]
        )
        return {
            "total_count": total_count,
            "total_amount": float(total_amount),
            "average_amount": float(average_amount),
            "review_count": review_count,
        }
