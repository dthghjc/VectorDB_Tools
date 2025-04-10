import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
LOG_FILENAME = 'system.log'

# Ensure log directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file_path = os.path.join(LOG_DIR, LOG_FILENAME)

def setup_logging():
    """Configures the root logger for the application."""
    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File Handler (Rotating)
    # Rotates logs when they reach 10MB, keeps 5 backup logs
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO) # Log INFO level and above to file
    
    # Console Handler (Optional, for seeing logs in console during development)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG) # Log DEBUG level and above to console

    # Get the root logger and configure it
    root_logger = logging.getLogger()
    # Set the lowest level to capture (DEBUG for console, INFO for file)
    root_logger.setLevel(logging.DEBUG) 
    
    # Avoid adding handlers multiple times if setup_logging is called again
    if not root_logger.handlers:
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        root_logger.info("Logging configured: File handler added.")
    else:
        # If handlers exist, maybe just update level or check config?
        # For simplicity, assume setup is called once at startup.
        pass

# Call setup automatically when this module is imported?
# Be careful with multiple imports calling this.
# setup_logging()

# Function to get logger instances in other modules
def get_logger(name):
    """Gets a logger instance with the specified name."""
    return logging.getLogger(name) 