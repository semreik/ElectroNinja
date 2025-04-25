import logging
import os
import sys
from datetime import datetime

def setup_logging():
    """Configure logging for the application"""
    
    # Reconfigure stdout to use UTF-8 encoding
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding='utf-8')
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Generate log file name with timestamp
    log_file = os.path.join(logs_dir, f"electroninja_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Configure logging with UTF-8 for the FileHandler
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Create a logger
    logger = logging.getLogger('electroninja')
    logger.info("Logging initialized")
    
    return logger
