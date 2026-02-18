import logging
import sys
from app.core.config import settings

def setup_logger():
    logger = logging.getLogger(settings.SYSTEM_NAME)
    logger.setLevel(settings.LOG_LEVEL)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    return logger

logger = setup_logger()