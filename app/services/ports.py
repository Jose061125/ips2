from abc import ABC, abstractmethod
from ..models import User

class UserRepositoryPort(ABC):
    """
    Un puerto que define las operaciones de persistencia para los usuarios.
    El núcleo de la aplicación dependerá de esta abstracción, no de una
    implementación concreta de base de datos.
    """
    @abstractmethod
    def add(self, user: User) -> User:
        """Guarda un nuevo usuario."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        """Busca un usuario por su nombre."""
        pass
