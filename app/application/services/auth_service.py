from typing import Tuple, Optional
from ...domain.models.user import User
from ...domain.ports.repositories import UserRepositoryPort
import logging

class AuthService:
    """Servicio de autenticación (ISO 27001: A.9.4)"""
    
    def __init__(self, user_repository: UserRepositoryPort):
        self.repository = user_repository
        self.logger = logging.getLogger(__name__)

    def register(self, username: str, password: str) -> Tuple[bool, str]:
        if self.repository.find_by_username(username):
            self.logger.warning(f"Registration attempt with existing username: {username}")
            return False, "Username already exists"
        
        user = User.create(username=username, password=password)
        self.repository.save(user)
        self.logger.info(f"New user registered: {username}")
        return True, "Registration successful"

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.repository.find_by_username(username)
        if not user or not user.check_password(password):
            self.logger.warning(f"Failed login attempt for user: {username}")
            return None
            
        self.logger.info(f"Successful login: {username}")
        self.repository.audit_action(user.id, "login")
        return user