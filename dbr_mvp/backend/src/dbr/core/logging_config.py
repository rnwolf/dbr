# src/dbr/core/logging_config.py
import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'organization_id'):
            log_entry['organization_id'] = record.organization_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'method'):
            log_entry['method'] = record.method
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        if hasattr(record, 'duration_ms'):
            log_entry['duration_ms'] = record.duration_ms
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


def get_logging_config(log_level: str = "INFO", log_file: str = None) -> Dict[str, Any]:
    """Get logging configuration dictionary"""
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s"
            },
            "json": {
                "()": JSONFormatter,
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": sys.stdout
            },
            "console_detailed": {
                "class": "logging.StreamHandler", 
                "level": "DEBUG",
                "formatter": "detailed",
                "stream": sys.stdout
            }
        },
        "loggers": {
            # DBR application loggers
            "dbr": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "dbr.api": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "dbr.auth": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "dbr.database": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            # Third-party loggers
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "WARNING",  # Set to INFO to see SQL queries
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console"]
        }
    }
    
    # Add file handler if log file specified
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "json",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
        
        # Add file handler to all loggers
        for logger_config in config["loggers"].values():
            if "handlers" in logger_config:
                logger_config["handlers"].append("file")
        config["root"]["handlers"].append("file")
    
    return config


def setup_logging(log_level: str = "INFO", log_file: str = None, enable_sql_logging: bool = False):
    """Setup application logging"""
    
    config = get_logging_config(log_level, log_file)
    
    # Enable SQL query logging if requested
    if enable_sql_logging:
        config["loggers"]["sqlalchemy.engine"]["level"] = "INFO"
    
    logging.config.dictConfig(config)
    
    # Get the main application logger
    logger = logging.getLogger("dbr")
    logger.info("Logging configured", extra={
        "log_level": log_level,
        "log_file": log_file,
        "sql_logging": enable_sql_logging
    })
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name"""
    return logging.getLogger(f"dbr.{name}")


# Context manager for adding request context to logs
class LogContext:
    """Context manager for adding request-specific context to logs"""
    
    def __init__(self, **context):
        self.context = context
        self.old_factory = logging.getLogRecordFactory()
    
    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)


# Decorator for logging function calls
def log_function_call(logger: logging.Logger = None):
    """Decorator to log function entry and exit"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_logger = logger or get_logger("function_calls")
            func_logger.debug(f"Entering {func.__name__}", extra={
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys())
            })
            
            try:
                result = func(*args, **kwargs)
                func_logger.debug(f"Exiting {func.__name__} successfully")
                return result
            except Exception as e:
                func_logger.error(f"Error in {func.__name__}: {str(e)}", extra={
                    "function": func.__name__,
                    "error": str(e)
                })
                raise
        
        return wrapper
    return decorator