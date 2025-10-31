# 🚀 Sprint 3: Expansión del Prototipo

**Período Proyectado:** Octubre 31 - Noviembre 15, 2025  
**Duración:** 2 semanas  
**Estado:** 🔄 En Progreso (30% Completado)

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

### Arquitectura (Oct 31 - Nov 2, 2025)
  - [x] Separar capa API (`app/api`) con blueprint versionado `/api/v1` - *Oct 31*
  - [x] Configuración de CORS y serialización con Marshmallow - *Oct 31*
  - [ ] Centralizar configuración por entorno (dev, test, prod) - *Nov 1*

### Performance (Nov 3-5, 2025)
  - [ ] Integrar Flask-Caching en endpoints listados (pacientes) - *Nov 3*
  - [ ] Crear índice compuesto sugerido para consultas frecuentes - *Nov 4*

### Persistencia (Nov 6-8, 2025)
  - [ ] Inicializar Alembic y crear migración inicial - *Nov 6*
  - [ ] Script de datos seed para entornos locales - *Nov 7*

### Asíncrono (Nov 9-11, 2025)
  - [ ] Setup Celery + Redis; tarea demo (enviar reporte) - *Nov 10*

### DevEx - Developer Experience (Oct 31 - Nov 2, 2025)
  - [x] Dockerfile y docker-compose con app+redis - *Oct 31*
  - [x] GitHub Actions: lint + pytest + cobertura - *Oct 31*
  - [ ] Makefile o scripts para tareas comunes (opcional) - *Nov 2*

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

### Tests y Calidad (Nov 12-13, 2025)
- [ ] Tests unitarios y de integración actualizados (pytest) - *Nov 12*
- [ ] Seguridad: Bandit + Safety (dependabot en GitHub opcional) - *Nov 13*
- [ ] Performance: re-ejecutar suite de benchmarks clave - *Nov 13*

## 8. Cronograma Detallado

| Fase | Tareas | Fecha Inicio | Fecha Fin |
|------|--------|--------------|-----------|
| **Fase 1: Infraestructura** | CI/CD + Docker + requisitos | Oct 31 | Nov 1 |
| **Fase 2: API v1** | API + CORS + Marshmallow + Tests | Nov 2 | Nov 4 |
| **Fase 3: Performance** | Caching + índices DB | Nov 5 | Nov 7 |
| **Fase 4: Migraciones** | Alembic + seeds | Nov 8 | Nov 10 |
| **Fase 5: Async** | Celery + Redis worker | Nov 11 | Nov 12 |
| **Fase 6: Validación** | Tests finales + documentación | Nov 13 | Nov 15 |

### Cronograma Original (1-1.5 semanas)
- Día 1-2 (Oct 31 - Nov 1): CI/CD + Docker + requisitos ✅
- Día 3-4 (Nov 2-3): API v1 + CORS + Marshmallow
- Día 5 (Nov 4): Caching + índices
- Día 6 (Nov 5-6): Alembic + migraciones
- Día 7 (Nov 7): Celery + validación final
