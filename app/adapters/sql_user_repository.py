from ..services.ports import UserRepositoryPort
from ..models import User, db

class SqlAlchemyUserRepository(UserRepositoryPort):
    """
    La implementación concreta (adaptador) del puerto de repositorio
    usando SQLAlchemy. Este es el único lugar que "sabe" cómo hablar
    con la base de datos de SQLAlchemy para los usuarios.
    """
    def add(self, user: User) -> User:
        db.session.add(user)
        # La confirmación (commit) se puede manejar aquí o en una capa superior
        # para agrupar transacciones. Por ahora, lo dejamos explícito.
        db.session.commit()
        return user

    def get_by_username(self, username: str) -> User | None:
        return User.query.filter_by(username=username).first()
