import pytest
from app.services.user_service import UserService
from app.services.ports import UserRepositoryPort
from app.models import User

# --- Creación de un "Adaptador Falso" para las Pruebas --- #

class FakeUserRepository(UserRepositoryPort):
    """
    Una implementación falsa del repositorio de usuarios para usar en las pruebas.
    Simula la base de datos en memoria sin necesidad de SQLAlchemy.
    """
    def __init__(self, initial_users: list[User] = None):
        self._users = {user.username: user for user in initial_users} if initial_users else {}

    def add(self, user: User) -> User:
        self._users[user.username] = user
        return user

    def get_by_username(self, username: str) -> User | None:
        return self._users.get(username)

# --- Pruebas del Servicio del Núcleo --- #

def test_register_new_user_successfully():
    """Verifica que un nuevo usuario se pueda registrar correctamente."""
    # 1. Arrange: Preparamos un repositorio vacío y el servicio
    repo = FakeUserRepository()
    service = UserService(user_repository=repo)

    # 2. Act: Ejecutamos la lógica de negocio
    success, message = service.register_user("testuser", "password123")

    # 3. Assert: Verificamos los resultados
    assert success is True
    assert "¡Felicidades" in message
    assert repo.get_by_username("testuser") is not None

def test_register_existing_user_fails():
    """Verifica que no se puede registrar un usuario que ya existe."""
    # 1. Arrange: Preparamos un repo con un usuario existente
    existing_user = User(username="testuser")
    repo = FakeUserRepository(initial_users=[existing_user])
    service = UserService(user_repository=repo)

    # 2. Act: Intentamos registrar el mismo usuario
    success, message = service.register_user("testuser", "password123")

    # 3. Assert: Verificamos que la operación falló como se esperaba
    assert success is False
    assert message == "El nombre de usuario ya existe."

def test_login_with_valid_credentials():
    """Verifica que un usuario puede iniciar sesión con credenciales válidas."""
    # 1. Arrange
    existing_user = User(username="testuser")
    existing_user.set_password("password123")
    repo = FakeUserRepository(initial_users=[existing_user])
    service = UserService(user_repository=repo)

    # 2. Act
    user = service.login("testuser", "password123")

    # 3. Assert
    assert user is not None
    assert user.username == "testuser"

def test_login_with_invalid_password():
    """Verifica que el inicio de sesión falla con una contraseña incorrecta."""
    # 1. Arrange
    existing_user = User(username="testuser")
    existing_user.set_password("password123")
    repo = FakeUserRepository(initial_users=[existing_user])
    service = UserService(user_repository=repo)

    # 2. Act
    user = service.login("testuser", "wrongpassword")

    # 3. Assert
    assert user is None
