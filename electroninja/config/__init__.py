from electroninja.config.logging_config import setup_logging
from electroninja.config.settings import Config

# Initialize logger
logger = setup_logging()

# Create necessary directories
Config.ensure_directories()