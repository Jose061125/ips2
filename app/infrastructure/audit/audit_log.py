import logging
from datetime import datetime
from typing import Any, Dict
from flask import request
from flask_login import current_user

class AuditLogger:
    def __init__(self):
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('audit')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('logs/audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    def log_action(self, action: str, details: Dict[str, Any]) -> None:
        user_id = getattr(current_user, 'id', 'anonymous')
        ip_address = request.remote_addr
        timestamp = datetime.now().isoformat()
        
        self.logger.info(
            f"[{timestamp}] User:{user_id} IP:{ip_address} "
            f"Action:{action} Details:{details}"
        )