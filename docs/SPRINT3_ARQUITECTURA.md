# 🧭 Sprint 3: Mejoras de Arquitectura

Este documento describe las mejoras progresivas sobre el monolito hexagonal actual, priorizando mantenibilidad, rendimiento y despliegue.

## 1. Capas y Módulos

- API (nuevo): `app/api/` Blueprint versionado `/api/v1`.
- Servicios (existente): `app/services/` mantiene puertos/casos de uso.
- Adaptadores (existente): `app/adapters/` repositorios SQLAlchemy.
- Infra (existente): `app/infrastructure/` (audit, security).

## 2. Configuración por Entornos

- `config.py` amplía perfiles: Development, Testing, Production.
- Variables de entorno: `FLASK_ENV`, `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`.
- Caching: `CACHE_TYPE` = `SimpleCache` (dev) o `RedisCache` (prod).

## 3. API REST (v1)

- Salud: `GET /api/v1/health` → status, version, timestamp.
- Pacientes (MVP): `GET /api/v1/patients` (paginado), `POST /api/v1/patients`.
- Serialización: Marshmallow Schemas.
- CORS: `flask-cors` restringido por origen.

## 4. Caching Estratégico

- Capa de caché en listados frecuentes (pacientes, citas).
- Invalidación por escritura creativa (post/put/delete) → `cache.delete_memoized`.
- TTL por endpoint (ej. 60s) y cache key por parámetros de búsqueda/paginado.

## 5. Persistencia y Migraciones (Alembic)

- Inicializar `alembic/` con `env.py` apuntando a `db.metadata`.
- Flujo: `alembic revision --autogenerate -m "<msg>"` → `alembic upgrade head`.
- Reglas: cambios de modelos se reflejan en migraciones.

## 6. Asíncrono con Celery

- Broker/result backend: Redis.
- Ejemplos: envío de reportes, generación de informes, tareas de consolidación.
- Estructura: `app/tasks/` con decoradores `@celery.task`.

## 7. Observabilidad

- Logging estructurado (JSON opcional) para API y tasks.
- Métricas: hooks para Prometheus/Grafana en siguiente sprint.

## 8. Despliegue y Contenedores

- Dockerfile multi-stage opcional (build + runtime slim).
- docker-compose para dev: `app`, `redis`.
- CI: build + tests + coverage; artifacts opcionales (htmlcov).

## 9. Guías de Código

- Tipado gradual con `typing` y `mypy` (opcional).
- Lint: Pylint ≥ 8.5, formateo Black, isort.
- Manejo de errores: excepciones de dominio mapeadas a HTTP 4xx/5xx.
