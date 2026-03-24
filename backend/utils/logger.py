"""
Logging utility using loguru for the financial risk analysis system.
"""
import sys
from loguru import logger as loguru_logger
from functools import lru_cache
from .config import get_settings


def get_logger(name: str = "finvis"):
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name/module identifier
        
    Returns:
        Configured loguru logger
    """
    settings = get_settings()
    
    # Configure logger
    loguru_logger.remove()  # Remove default handler
    
    # Add console handler with appropriate level
    loguru_logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        filter=lambda record: record["extra"].get("name") == name or not record["extra"].get("name")
    )
    
    # Add file handler for persistence
    loguru_logger.add(
        "logs/finvis.log",
        rotation="500 MB",
        retention="10 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        filter=lambda record: record["extra"].get("name") == name or not record["extra"].get("name")
    )
    
    return loguru_logger.bind(name=name)


# Create logs directory if it doesn't exist
import os
os.makedirs("logs", exist_ok=True)
