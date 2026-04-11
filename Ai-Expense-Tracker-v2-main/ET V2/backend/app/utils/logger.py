import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

# File handler
file_handler = RotatingFileHandler(
    BASE_DIR / "logs/app.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

# Console handler
console_handler = logging.StreamHandler()

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Logger class (mixin)
class LoggerMixin:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.propagate = False

# Root logger setup
logging.basicConfig(handlers=[console_handler], level=logging.INFO)
logger = logging.getLogger("ET_V2")
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

# Ensure logs dir
logs_dir = BASE_DIR / "logs"
logs_dir.mkdir(exist_ok=True)
file_handler = RotatingFileHandler(
    logs_dir / "app.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


