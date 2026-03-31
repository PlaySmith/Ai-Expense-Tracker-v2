from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from pathlib import Path
import hashlib

from app.models.models import Expense
from app.schemas.expense_schema import ExpenseCreate, ExpenseUpdate
from app.services.ocr_service import OCRService
from app.services.parser_service import ParserService
from app.utils.error_handlers import (
    DatabaseError, 
    OCRError, 
    ParserError, 
    DuplicateExpenseError,
    ValidationError
)
from app.utils.logger import LoggerMixin


class ExpenseService(LoggerMixin):
    """Service for managing expenses"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ocr_service = OCRService()
        self.parser_service = ParserService()
        super().__init__()

    
    def process_receipt(
        self, 
        image_path: str, 
        owner_id: int
    ) -> Dict[str, Any]:

        """
        Process a receipt image end-to-end
        
        Workflow:
        1. Validate image
        2. Perform OCR
        3. Parse extracted text
        4. Check for duplicates
        5. Save to database
        
        Args:
            image_path: Path to receipt image
            owner_id: Optional user ID
            
        Returns:
            Dictionary with expense data and processing results
            
        Raises:
            Various exceptions handled by error handlers
        """
        try:
            self.logger.info(f"Processing receipt for user {owner_id}: {image_path}")

            
            # Step 1: Validate image
            self.ocr_service.validate_image(image_path)
            
            # Step 2: Check for duplicates (using file hash)
            # Check for duplicates (user-specific)
            existing = self.db.query(Expense).filter(
                Expense.owner_id == owner_id,
                Expense.receipt_image_path.like(f"%{Path(image_path).name}%")
            ).first()
            if existing:
                raise DuplicateExpenseError(
                    message="This receipt appears to be a duplicate",
                    details={
                        "existing_expense_id": existing.id,
                        "merchant": existing.merchant,
                        "amount": existing.amount,
                        "date": existing.date.isoformat() if existing.date else None
                    }
                )

            
            # Step 3: Perform OCR (always returns now)
            ocr_result = self.ocr_service.process_image(image_path)
            extracted_text = ocr_result.get('items_text', '') or ocr_result.get('merchant_text', '') + ' ' + ocr_result.get('amount_text', '')
            ocr_confidence = ocr_result.get('conf', 0.0)
            if ocr_confidence < 50.0:
                self.logger.warning(f"Low OCR confidence ({ocr_confidence:.1f}%), flagging for review")
            
            # Step 4: Parse extracted text
            if extracted_text:
                parsed_data = self.parser_service.parse_receipt(extracted_text, ocr_confidence)
            else:
                parsed_data = {
                    "amount": None,
                    "date": None,
                    "merchant": None,
                    "category": None,
                    "confidence_scores": {},
                    "warnings": ["OCR failed - manual entry required"]
                }
            
            # Step 5: Sanitize data for Pydantic validation
            safe_amount = parsed_data.get("amount")
            if safe_amount is None or safe_amount <= 0:
                safe_amount = 0.01
                parsed_data["warnings"] = parsed_data.get("warnings", []) + ["Placeholder amount - requires manual review"]
            
            safe_merchant = (parsed_data.get("merchant") or "")[:255].strip()
            if not safe_merchant:
                safe_merchant = "Unknown Receipt"
            
            requires_review = ocr_confidence < 50.0 or safe_amount <= 0.01 or not safe_merchant or "Unknown Receipt" in safe_merchant
            
            # Step 6: Create expense record
            expense_data = ExpenseCreate(
                amount=safe_amount,
                merchant=safe_merchant,
                category=parsed_data.get("category"),
                date=parsed_data.get("date"),
                description=f"Extracted from receipt. OCR confidence: {ocr_confidence:.1f}% {'[Review Required]' if requires_review else ''}",
                receipt_image_path=image_path,
                ocr_confidence=ocr_confidence
            )

            
            # Step 7: Save to database
            expense = self.create_expense(expense_data, owner_id)
            
            # Prepare response
            result = {
                "success": True,
                "expense": expense,
                "extracted_data": {
                    "text_preview": extracted_text[:200] if extracted_text else "",
                    "parsed_data": parsed_data,
                    "ocr_confidence": ocr_confidence
                },
                "warnings": parsed_data.get("warnings", []),
                "requires_review": requires_review
            }
            
            self.logger.info(f"Receipt processed successfully. Expense ID: {expense.id}")
            return result
            
        except DuplicateExpenseError:
            raise
        except Exception as e:
            self.logger.error(f"Receipt processing failed: {str(e)}", exc_info=True)
            raise DatabaseError(
                message=f"Failed to process receipt: {str(e)}",
                details={"image_path": image_path}
            )
    
    def create_expense(
        self, 
        expense_data: ExpenseCreate, 
        owner_id: Optional[int] = None
    ) -> Expense:
        """Create a new expense record"""
        try:
            db_expense = Expense(
                amount=expense_data.amount,
                merchant=expense_data.merchant,
                category=expense_data.category,
                date=expense_data.date or datetime.utcnow(),
                description=expense_data.description,
                receipt_image_path=expense_data.receipt_image_path,
                ocr_confidence=expense_data.ocr_confidence,
                owner_id=owner_id
            )
            
            self.db.add(db_expense)
            self.db.commit()
            self.db.refresh(db_expense)
            
            self.logger.info(f"Created expense ID: {db_expense.id}")
            return db_expense
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to create expense: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to save expense: {str(e)}")
    
    def get_expense(self, expense_id: int) -> Optional[Expense]:
        """Get a single expense by ID"""
        try:
            return self.db.query(Expense).filter(Expense.id == expense_id).first()
        except Exception as e:
            self.logger.error(f"Failed to get expense {expense_id}: {str(e)}")
            raise DatabaseError(f"Failed to retrieve expense: {str(e)}")
    
    def get_expenses(
        self, 
        skip: int = 0, 
        limit: int = 100,
        owner_id: Optional[int] = None,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Expense]:
        """Get list of expenses with optional filtering"""
        try:
            query = self.db.query(Expense)
            
            # Apply filters
            if owner_id:
                query = query.filter(Expense.owner_id == owner_id)
            if category:
                query = query.filter(Expense.category == category)
            if start_date:
                query = query.filter(Expense.date >= start_date)
            if end_date:
                query = query.filter(Expense.date <= end_date)
            
            # Order by date descending (newest first)
            query = query.order_by(Expense.date.desc())
            
            return query.offset(skip).limit(limit).all()
            
        except Exception as e:
            self.logger.error(f"Failed to get expenses: {str(e)}")
            raise DatabaseError(f"Failed to retrieve expenses: {str(e)}")
    
    def update_expense(
        self, 
        expense_id: int, 
        expense_update: ExpenseUpdate
    ) -> Optional[Expense]:
        """Update an existing expense"""
        try:
            expense = self.get_expense(expense_id)
            if not expense:
                return None
            
            # Update fields
            update_data = expense_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(expense, field, value)
            
            expense.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(expense)
            
            self.logger.info(f"Updated expense ID: {expense_id}")
            return expense
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to update expense {expense_id}: {str(e)}")
            raise DatabaseError(f"Failed to update expense: {str(e)}")
    
    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense"""
        try:
            expense = self.get_expense(expense_id)
            if not expense:
                return False
            
            self.db.delete(expense)
            self.db.commit()
            
            self.logger.info(f"Deleted expense ID: {expense_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to delete expense {expense_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete expense: {str(e)}")
    
    def get_expense_stats(self, owner_id: Optional[int] = None) -> Dict[str, Any]:
        """Get expense statistics"""
        try:
            from sqlalchemy import func
            
            query = self.db.query(
                func.count(Expense.id).label('total_count'),
                func.sum(Expense.amount).label('total_amount'),
                func.avg(Expense.amount).label('avg_amount')
            )
            
            if owner_id:
                query = query.filter(Expense.owner_id == owner_id)
            
            result = query.first()
            
            # Get category breakdown
            category_query = self.db.query(
                Expense.category,
                func.sum(Expense.amount).label('amount'),
                func.count(Expense.id).label('count')
            )
            
            if owner_id:
                category_query = category_query.filter(Expense.owner_id == owner_id)
            
            category_query = category_query.group_by(Expense.category)
            categories = category_query.all()
            
            return {
                "total_count": result.total_count or 0,
                "total_amount": float(result.total_amount or 0),
                "average_amount": float(result.avg_amount or 0),
                "categories": [
                    {
                        "category": cat.category or "Uncategorized",
                        "amount": float(cat.amount or 0),
                        "count": cat.count
                    }
                    for cat in categories
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get stats: {str(e)}")
            raise DatabaseError(f"Failed to retrieve statistics: {str(e)}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file for duplicate detection"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.warning(f"Could not calculate file hash: {str(e)}")
            return ""
    
    def _check_duplicate_by_hash(self, file_hash: str) -> Optional[Expense]:
        """Check if expense with same file hash exists"""
        if not file_hash:
            return None
        
        # Note: This is a simplified check. In production, you'd store file hashes
        # For now, we'll do a basic check on recent expenses
        recent_expenses = self.get_expenses(limit=50)
        
        # In a real implementation, you'd compare stored hashes
        # For MVP, we'll skip this detailed check
        return None
