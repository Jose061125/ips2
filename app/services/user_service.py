from typing import Tuple, Optional
from ..models import User
from .ports import UserRepositoryPort

class UserService:
    def __init__(self, user_repository: UserRepositoryPort):
        """
        El servicio se inicializa con una implementación del puerto de repositorio.
        Esto se conoce como Inyección de Dependencias.
        """
        self.user_repository = user_repository

    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Lógica de negocio pura para registrar un usuario. No contiene código
        de Flask ni de SQLAlchemy directamente.
        """
        if self.user_repository.get_by_username(username):
            return (False, "El nombre de usuario ya existe.")

        new_user = User(username=username)
        new_user.set_password(password)
        self.user_repository.add(new_user)

        return (True, "¡Felicidades, ahora eres un usuario registrado!")

    def login(self, username: str, password: str) -> Optional[User]:
        """
        Lógica de negocio para autenticar a un usuario.
        Devuelve el objeto User si tiene éxito, o None si falla.
        """
        user = self.user_repository.get_by_username(username)
        if not user or not user.check_password(password):
            return None
        return user
