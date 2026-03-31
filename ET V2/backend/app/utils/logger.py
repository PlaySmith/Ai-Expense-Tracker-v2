import logging
import logging.config
from logging.handlers import RotatingFileHandler
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
logs_dir = BASE_DIR / "logs"
logs_dir.mkdir(exist_ok=True)

# Clean uvicorn-compatible logging config
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": str(logs_dir / "app.log"),
            "maxBytes": 10*1024*1024,  # 10MB
            "backupCount": 5,
            "level": "INFO",
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    },
    "loggers": {
        "ET_V2": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        }
    }
}

# Init once
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("ET_V2")

class LoggerMixin:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)


