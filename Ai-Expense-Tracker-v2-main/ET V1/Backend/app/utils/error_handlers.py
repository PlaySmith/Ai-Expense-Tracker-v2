from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Optional, Any
import traceback


class SmartSpendException(Exception):
    """Base exception for SmartSpend AI"""
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[dict] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class OCRError(SmartSpendException):
    """OCR processing errors"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="OCR_ERROR",
            status_code=422,
            details=details
        )


class OCRLowConfidenceError(OCRError):
    """OCR confidence too low"""
    def __init__(self, confidence: float, details: Optional[dict] = None):
        super().__init__(
            message=f"OCR confidence too low ({confidence:.1f}%). Try a clearer photo.",
            details={"confidence_score": confidence, **(details or {})}
        )


class ParserError(SmartSpendException):
    """Text parsing errors"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="PARSER_ERROR",
            status_code=422,
            details=details
        )


class ValidationError(SmartSpendException):
    """Input validation errors"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class FileUploadError(SmartSpendException):
    """File upload errors"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="UPLOAD_ERROR",
            status_code=400,
            details=details
        )


class DatabaseError(SmartSpendException):
    """Database operation errors"""
    def __init__(self, message: str = "Database operation failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details
        )


class DuplicateExpenseError(SmartSpendException):
    """Duplicate expense detection"""
    def __init__(self, message: str = "Possible duplicate expense detected", details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="DUPLICATE_ERROR",
            status_code=409,
            details=details
        )


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 500,
    details: Optional[dict] = None
) -> dict:
    """Create standardized error response"""
    import time
    return {
        "status": "error",
        "error_code": error_code,
        "message": message,
        "details": details or {},
        "timestamp": time.time()
    }


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers for FastAPI"""
    
    @app.exception_handler(SmartSpendException)
    async def smartspend_exception_handler(request: Request, exc: SmartSpendException):
        """Handle custom SmartSpend exceptions"""
        logger = logging.getLogger("error")
        logger.error(f"{exc.error_code}: {exc.message}", extra={"details": exc.details})
        
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                error_code=exc.error_code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details
            )
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors"""
        logger = logging.getLogger("error")
        logger.warning(f"Validation error: {exc.errors()}")
        
        # Format validation errors
        error_details = []
        for error in exc.errors():
            error_details.append({
                "field": " -> ".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=422,
            content=create_error_response(
                error_code="VALIDATION_ERROR",
                message="Input validation failed",
                status_code=422,
                details={"errors": error_details}
            )
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        """Handle database errors"""
        logger = logging.getLogger("error")
        logger.error(f"Database error: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                error_code="DATABASE_ERROR",
                message="Database operation failed. Please try again later.",
                status_code=500,
                details={"error_type": type(exc).__name__}
            )
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger = logging.getLogger("error")
        logger.critical(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        # In production, don't expose internal details
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                error_code="INTERNAL_ERROR",
                message="An unexpected error occurred. Please try again later.",
                status_code=500,
                details={"error_type": type(exc).__name__}
            )
        )
