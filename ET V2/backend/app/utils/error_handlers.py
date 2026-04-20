from fastapi import HTTPException
from typing import Dict, Any, Optional
import logging

class AppError(HTTPException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, status_code: int = 400):
        super().__init__(status_code=status_code, detail={
            "error": True,
            "message": message,
            "details": details or {}
        })

class OCRError(AppError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, 422)

class ParserError(AppError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, 422)

class DatabaseError(AppError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, 500)

class FileUploadError(AppError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, 413)

class DuplicateExpenseError(AppError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, 409)

class BudgetError(AppError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, 400)

