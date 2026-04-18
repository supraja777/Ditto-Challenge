import os
import logging
from datetime import datetime

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_matchmaking_loggers():
    """Returns two logger instances: one for system, one for AI reasoning."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    sys_handler = logging.FileHandler(os.path.join(LOG_DIR, f"system_logs_{timestamp}.log"))
    sys_handler.setFormatter(formatter)
    system_logger = logging.getLogger("system_logger")
    system_logger.setLevel(logging.INFO)
    system_logger.addHandler(sys_handler)

    ai_handler = logging.FileHandler(os.path.join(LOG_DIR, f"ai_logs_{timestamp}.log"))
    ai_handler.setFormatter(formatter)
    ai_logger = logging.getLogger("ai_logger")
    ai_logger.setLevel(logging.INFO)
    ai_logger.addHandler(ai_handler)

    return system_logger, ai_logger