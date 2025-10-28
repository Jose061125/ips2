# Copilot Instructions for ips2

These guidelines help AI coding agents work effectively in this Flask project.

## Arquitectura y flujo principal
- Patrón: App Factory (ver `app/__init__.py`) + Blueprints (`app/auth`, `app/main`).
- Dominio y puertos: Hexagonal/DDD ligero.
  - Puerto de repositorio de usuarios: `app/services/ports.py` (`UserRepositoryPort`).
  - Servicio de dominio: `app/services/user_service.py` (métodos `register_user`, `login`).
  - Adaptador SQLAlchemy: `app/adapters/sql_user_repository.py`.
- Modelos y DB: `app/models.py` define `db = SQLAlchemy()` y `User` con `set_password`/`check_password`.
- Seguridad:
  - CSRF: `Flask-WTF` inicializado en `create_app`.
  - Login: `Flask-Login` con `login_manager.login_view = 'auth.login'`.
  - Política de contraseñas: `app/infrastructure/security/password_policy.py` (mensajes en inglés; min 8, mayúscula, minúscula, número, símbolo).
  - Rate limiting: decorador `@rate_limit` de `app/infrastructure/security/rate_limiter.py` por IP (30 req/60s por defecto).
  - Auditoría: `app/infrastructure/audit/audit_log.py` escribe en `logs/audit.log`.

## Rutas y patrones de uso
- `app/auth/routes.py` ejemplifica el estilo:
  - Formularios con `FlaskForm` en `app/forms.py`.
  - Validar contraseña con `PasswordPolicy.validate_password` ANTES de usar el servicio.
  - Lógica de negocio vía `UserService` (inyecta `SqlAlchemyUserRepository`).
  - Autenticación con `login_user`, mensajes `flash` en español y redirecciones.
  - Aplica `@rate_limit` en endpoints sensibles (`/auth/login`, `/auth/register`).
- `app/main/routes.py` define `GET /` y renderiza `templates/index.html`.

## Configuración
- `config.py` (`Config`): lee `.env` (SECRET_KEY, DATABASE_URL, etc.). Defaults: SQLite `app.db`, CSRF habilitado.
- `create_app(test_config=None)` admite override para pruebas (e.g., `WTF_CSRF_ENABLED=False`, `SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'`).

## Flujo de datos clave (registro)
1) POST `/auth/register` → valida `PasswordPolicy` →
2) `UserService.register_user` verifica duplicados vía `UserRepositoryPort` →
3) `SqlAlchemyUserRepository.add` guarda y `commit` →
4) `flash(message)` y redirect a login.

## Pruebas
- Framework: `pytest` + `pytest-flask`.
- Fixtures en `tests/conftest.py`:
  - `app()` usa `create_app` con SQLite en memoria y CSRF deshabilitado.
  - `client`, `test_user`, `auth_client` para flujos de autenticación.
- Cobertura de UI y dominio:
  - `tests/test_auth.py` prueba vistas `/auth/register`, `/auth/login`, `/auth/logout` y mensajes `flash`.
  - `tests/test_user_service.py` usa un `FakeUserRepository` implementando `UserRepositoryPort` para probar el servicio sin DB.

## Comandos (Windows PowerShell)
- Crear entorno e instalar deps:
  - `python -m venv venv`
  - `.\venv\Scripts\Activate.ps1`
  - `pip install -r requirements.txt`
- Ejecutar tests:
  - `python -m pytest -q`
- Ejecutar servidor de desarrollo:
  - `python run.py`

## Convenciones del proyecto
- Mensajes al usuario en español (e.g., "Has iniciado sesión correctamente"). Las validaciones de `PasswordPolicy` retornan texto en inglés para compatibilidad con tests.
- Usa el servicio de dominio (no accedas DB desde rutas directamente). Implementa nuevos repositorios extendiendo `UserRepositoryPort`.
- Endpoints sensibles deben usar `@rate_limit` y registrar acciones relevantes con `AuditLogger` cuando aplique.
- En pruebas de formularios, deshabilitar CSRF vía `test_config` (ver `conftest.py`).

## Extensiones y puntos de integración
- Logging rotativo opcional: `app/infrastructure/logging/logger.py` (`setup_logging(app)`), crea `logs/ips.log`.
- Otro ejemplo de infraestructura/DDD: `app/infrastructure/persistence/sql_repository.py` y `app/domain/*` (empleados) muestran el patrón de puertos/adaptadores replicable.

## Añadir nuevas funcionalidades (ejemplos rápidos)
- Nueva ruta de auth: crea handler en `app/auth/routes.py` usando `auth_bp.route`, valida con formularios y, si aplica, `@rate_limit`.
- Nuevo almacén de usuarios: crea adaptador que implemente `UserRepositoryPort` y pásalo a `UserService`.
- Nueva validación de contraseñas: añade regla en `PasswordPolicy.PASSWORD_RULES` (actualiza tests si cambia el texto).
