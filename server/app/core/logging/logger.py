import logging
import sys
import os
from logging.handlers import RotatingFileHandler

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Log level mapping
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}


def setup_logging(
    log_level: str = "info",
    log_file: str = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    console_output: bool = True
):
    """
    Setup global logging configuration
    
    Args:
        log_level: Logging level (debug, info, warning, error, critical)
        log_file: Path to log file (if None, only console logging is used)
        log_format: Log format string
        max_bytes: Maximum size of each log file for rotation
        backup_count: Number of backup log files to keep
        console_output: Whether to output logs to console
    """
    root_logger = logging.getLogger()
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set the root log level
    level = LOG_LEVELS.get(log_level.lower(), logging.INFO)
    root_logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler if log_file is provided
    if log_file:
        # Create the directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=max_bytes, 
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Log the setup completion
    root_logger.info(f"Logging system initialized with level {log_level}")
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name
    
    Args:
        name: Name of the logger (typically the module name)
        
    Returns:
        A logger instance
    """
    return logging.getLogger(name)