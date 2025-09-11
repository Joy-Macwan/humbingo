import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    def __init__(self, log_file: str = "logs/library_system.log"):
        self.log_file = log_file
        self._setup_logger()
    
    def _setup_logger(self):
        """Set up logging configuration."""
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()  # Also log to console
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def info(self, message: str, user_id: Optional[int] = None):
        """Log info message."""
        if user_id:
            message = f"[User {user_id}] {message}"
        self.logger.info(message)
    
    def warning(self, message: str, user_id: Optional[int] = None):
        """Log warning message."""
        if user_id:
            message = f"[User {user_id}] {message}"
        self.logger.warning(message)
    
    def error(self, message: str, user_id: Optional[int] = None):
        """Log error message."""
        if user_id:
            message = f"[User {user_id}] {message}"
        self.logger.error(message)
    
    def critical(self, message: str, user_id: Optional[int] = None):
        """Log critical message."""
        if user_id:
            message = f"[User {user_id}] {message}"
        self.logger.critical(message)

# Global logger instance
logger = Logger()
