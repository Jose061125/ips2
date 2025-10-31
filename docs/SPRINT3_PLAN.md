# 🚀 Sprint 3: Expansión del Prototipo

Integración de funcionalidades avanzadas y mejoras en la arquitectura seleccionada.

## 1. Objetivos del Sprint

- Consolidar la arquitectura hexagonal con prácticas de producción.
- Exponer una API REST básica para integración.
- Mejorar performance con caching y optimización de consultas.
- Añadir migraciones de base de datos (Alembic) para control de esquemas.
- Preparar despliegue con Docker y CI/CD.
- Introducir tareas asíncronas para procesos costosos.
- Elevar la calidad del código (Pylint ≥ 8.5, cobertura ≥ 75%).

## 2. Alcance y Entregables

- CI/CD: Workflow de GitHub Actions ejecutando lint + tests + cobertura.
- Contenedores: Dockerfile y docker-compose con servicio app y Redis.
- API REST (v1): endpoints de salud y pacientes (listar/crear) — blueprint separado.
- Caching: Configuración base de Flask-Caching (in-memory) + hooks para Redis.
- Migraciones: Inicialización de Alembic y primera migración.
- Tareas asíncronas: Setup inicial con Celery + Redis (task demo).
- Documentación: Guías SPRINT3_PLAN.md y SPRINT3_ARQUITECTURA.md.

## 3. KPI / Criterios de Éxito

- P95 endpoints públicos < 200 ms (medido)
- 0 vulnerabilidades críticas (Safety/Bandit)
- Pylint ≥ 8.5, Black/Isort sin diffs
- Cobertura global ≥ 75%
- Docker build y tests exitosos en CI

## 4. Backlog (Historias y Tareas)

- Arquitectura
  - [ ] Separar capa API (`app/api`) con blueprint versionado `/api/v1`
  - [ ] Configuración de CORS y serialización con Marshmallow
  - [ ] Centralizar configuración por entorno (dev, test, prod)
- Performance
  - [ ] Integrar Flask-Caching en endpoints listados (pacientes)
  - [ ] Crear índice compuesto sugerido para consultas frecuentes
- Persistencia
  - [ ] Inicializar Alembic y crear migración inicial
  - [ ] Script de datos seed para entornos locales
- Asíncrono
  - [ ] Setup Celery + Redis; tarea demo (enviar reporte)
- DevEx
  - [ ] Dockerfile y docker-compose con app+redis
  - [ ] GitHub Actions: lint + pytest + cobertura
  - [ ] Makefile o scripts para tareas comunes (opcional)

## 5. Riesgos y Mitigaciones

- Complejidad de Alembic con metadata: usar import explícito del `db` de Flask.
- Redis no disponible en local: fallback a SimpleCache en dev.
- Inestabilidad por cambios de esquema: feature flags/branches.

## 6. Definición de Hecho (DoD)

- Pipelines en verde en `main`
- Contenedores levantan `app` y `redis` (compose up)
- API `/api/v1/health` responde 200 con metadatos
- Caching activo (hit/miss visible en logs)
- Migraciones aplicadas sin errores (alembic upgrade head)
- Task Celery ejecuta y registra en logs

## 7. Plan de Validación

- Tests unitarios y de integración actualizados (pytest)
- Seguridad: Bandit + Safety (dependabot en GitHub opcional)
- Performance: re-ejecutar suite de benchmarks clave

## 8. Cronograma Tentativo (1-1.5 semanas)

- Día 1-2: CI/CD + Docker + requisitos
- Día 3-4: API v1 + CORS + Marshmallow
- Día 5: Caching + índices
- Día 6: Alembic + migraciones
- Día 7: Celery + validación final
