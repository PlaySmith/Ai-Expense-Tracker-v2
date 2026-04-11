import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


def setup_logging():
    """Setup application logging with rotation"""
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Formatters
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s\n'
        '  - File: %(pathname)s:%(lineno)d\n'
        '  - Function: %(funcName)s()',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Root logger setup
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handlers with rotation
    
    # App log - all logs
    app_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(logging.DEBUG)
    app_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(app_handler)
    
    # API log - API requests/responses
    api_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "api.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(simple_formatter)
    api_logger = logging.getLogger("api")
    api_logger.addHandler(api_handler)
    api_logger.propagate = False  # Don't double log
    
    # OCR log - OCR processing
    ocr_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "ocr.log",
        maxBytes=5*1024*1024,
        backupCount=3
    )
    ocr_handler.setLevel(logging.DEBUG)
    ocr_handler.setFormatter(detailed_formatter)
    ocr_logger = logging.getLogger("ocr")
    ocr_logger.addHandler(ocr_handler)
    ocr_logger.propagate = False
    
    # Error log - errors only
    error_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "error.log",
        maxBytes=10*1024*1024,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    error_logger = logging.getLogger("error")
    error_logger.addHandler(error_handler)
    error_logger.propagate = False
    
    # Log startup
    logger = logging.getLogger("app")
    logger.info("Logging system initialized")
    logger.info(f"Log files location: {logs_dir.absolute()}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin to add logging capability to classes"""
    
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        super().__init__()
    
    @property
    def logger(self) -> logging.Logger:
        return self._logger
