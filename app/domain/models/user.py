from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: Optional[int]
    username: str
    password_hash: str
    
    def check_password(self, password: str) -> bool:
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create(username: str, password: str) -> 'User':
        from werkzeug.security import generate_password_hash
        return User(
            id=None,
            username=username,
            password_hash=generate_password_hash(password)
        )