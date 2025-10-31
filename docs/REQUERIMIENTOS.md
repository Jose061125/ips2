# Requerimientos del Sistema IPS

## Información del Proyecto

**Nombre:** Sistema de Gestión IPS  
**Versión:** 1.2.0 (Sprint 2: Testing y Optimización)  
**Fecha:** Octubre 2025 (Actualizado: 30/Oct/2025)  
**Arquitectura:** Monolito Hexagonal (Puertos y Adaptadores) + DDD  
**Framework:** Flask 3.x + Python 3.13  
**Quality Assurance:** OWASP Top 10, WCAG 2.1 Level AA, Performance SLAs

---

## 📐 Arquitectura del Sistema

### Patrón Arquitectónico: Monolito Hexagonal

El sistema implementa una **arquitectura monolítica modular** con principios de **arquitectura hexagonal (Puertos y Adaptadores)**, combinando lo mejor de ambos mundos:

#### 🏛️ **Monolito Modular**

El sistema se despliega como una **aplicación única** con las siguientes características:

- **Proceso único:** Todo el sistema corre en un solo proceso Flask
- **Base de datos unificada:** SQLite/PostgreSQL compartida
- **Despliegue simplificado:** Un solo `run.py` para ejecutar la aplicación
- **Módulos por dominio:** Organización interna clara (pacientes, citas, empleados, etc.)

**Ventajas para este MVP:**
- ✅ Desarrollo rápido y simplicidad operacional
- ✅ Fácil debugging y testing
- ✅ Sin complejidad de comunicación entre servicios
- ✅ Menor overhead de infraestructura

#### ⬡ **Arquitectura Hexagonal (Puertos y Adaptadores)**

Implementa separación de responsabilidades mediante capas bien definidas:

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTACIÓN (UI)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Auth    │  │ Patients │  │Employees │  │  Admin  │ │
│  │ Routes   │  │  Routes  │  │  Routes  │  │ Routes  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
└───────┼─────────────┼─────────────┼──────────────┼──────┘
        │             │             │              │
┌───────▼─────────────▼─────────────▼──────────────▼──────┐
│              CAPA DE APLICACIÓN (Services)              │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────┐ │
│  │  UserService   │  │ PatientService  │  │ Employee │ │
│  │ (Casos de Uso) │  │ (Casos de Uso)  │  │ Service  │ │
│  └───────┬────────┘  └────────┬────────┘  └────┬─────┘ │
└──────────┼────────────────────┼─────────────────┼───────┘
           │                    │                 │
           │          ┌─────────▼────────┐        │
           │          │   PUERTOS (ABC)  │        │
           │          │  ┌──────────────┐│        │
           └──────────┼─►│ Repository   ││────────┘
                      │  │   Ports      ││
                      │  └──────────────┘│
                      └─────────┬────────┘
┌─────────────────────────────┬─▼──────────────────────────┐
│              ADAPTADORES (Implementaciones)              │
│  ┌─────────────────────┐  ┌─────────────────────────┐   │
│  │ SqlAlchemyUser      │  │ SqlAlchemyPatient       │   │
│  │ Repository          │  │ Repository              │   │
│  └──────────┬──────────┘  └───────────┬─────────────┘   │
└─────────────┼─────────────────────────┼─────────────────┘
              │                         │
┌─────────────▼─────────────────────────▼─────────────────┐
│              INFRAESTRUCTURA (DB, Logs, etc.)           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │SQLAlchemy│  │  Audit   │  │  Rate    │              │
│  │   DB     │  │  Logger  │  │ Limiter  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

### Componentes Clave

#### 1️⃣ **Dominio (Domain Layer)**
**Ubicación:** `app/domain/`, `app/models.py`

- **Modelos de dominio:** `User`, `Patient`, `Appointment`, `MedicalRecord`, `Employee`
- **Validadores:** `app/domain/validators.py` (lógica de negocio pura)
- **Sin dependencias externas:** No conoce Flask, SQLAlchemy ni infraestructura

```python
# Ejemplo: app/models.py
class User(UserMixin, db.Model):
    def set_password(self, password):
        # Lógica de dominio pura
        self.password_hash = generate_password_hash(password)
```

#### 2️⃣ **Puertos (Ports)**
**Ubicación:** `app/services/ports.py`

Definen **interfaces abstractas** (contratos) que el dominio necesita:

```python
class UserRepositoryPort(ABC):
    @abstractmethod
    def add(self, user: User) -> User:
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        pass
```

**Puertos definidos:**
- `UserRepositoryPort`
- `PatientRepositoryPort`
- `AppointmentRepositoryPort`
- `MedicalRecordRepositoryPort`
- `EmployeeRepositoryPort`

#### 3️⃣ **Servicios de Aplicación (Application Services)**
**Ubicación:** `app/services/`

Contienen **casos de uso** y **lógica de negocio**. Dependen de **puertos**, no de implementaciones:

```python
# Ejemplo: app/services/user_service.py
class UserService:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repo = user_repository  # ← Depende del puerto
    
    def register_user(self, username, password, role):
        # Caso de uso: registrar usuario
        if self.user_repo.get_by_username(username):
            raise ValueError("Usuario ya existe")
        # ... lógica de negocio
```

#### 4️⃣ **Adaptadores (Adapters)**
**Ubicación:** `app/adapters/`

Implementaciones **concretas** de los puertos:

```python
# Ejemplo: app/adapters/sql_user_repository.py
class SqlAlchemyUserRepository(UserRepositoryPort):
    def add(self, user: User) -> User:
        db.session.add(user)
        db.session.commit()
        return user
```

**Adaptadores implementados:**
- `SqlAlchemyUserRepository`
- `SqlAlchemyPatientRepository`
- `SqlAlchemyAppointmentRepository`
- `SqlAlchemyMedicalRecordRepository`
- `SqlAlchemyEmployeeRepository`

#### 5️⃣ **Infraestructura (Infrastructure)**
**Ubicación:** `app/infrastructure/`

Servicios técnicos transversales:

- **Seguridad:** `security/password_policy.py`, `security/rate_limiter.py`, `security/access_control.py`
- **Auditoría:** `audit/audit_log.py`
- **Logging:** `logging/logger.py`
- **Persistencia:** `persistence/sql_repository.py`

#### 6️⃣ **Presentación (UI Layer)**
**Ubicación:** `app/auth/routes.py`, `app/patients/routes.py`, etc.

Controladores Flask que:
- Reciben requests HTTP
- Validan formularios
- Invocan servicios de aplicación
- Retornan respuestas (HTML/JSON)

```python
# Ejemplo: app/auth/routes.py
@auth_bp.route('/register', methods=['POST'])
def register():
    # Validar formulario
    # Llamar al servicio
    service = UserService(SqlAlchemyUserRepository())
    service.register_user(username, password, role)
    # Retornar respuesta
```

### Flujo de Datos (Ejemplo: Registro de Usuario)

```
1. Usuario completa formulario → POST /auth/register
                                         │
2. Routes valida formulario ────────────┤
   (app/auth/routes.py)                  │
                                         ▼
3. Invoca UserService.register_user() ──┤
   (app/services/user_service.py)        │
                                         ▼
4. UserService usa UserRepositoryPort ──┤ (interfaz abstracta)
                                         │
                                         ▼
5. SqlAlchemyUserRepository implementa ─┤
   el puerto (app/adapters/)             │
                                         ▼
6. Guarda en DB vía SQLAlchemy ─────────┤
   (app/models.py, db.session.commit)    │
                                         ▼
7. Retorna éxito → flash + redirect ────┘
```

### Ventajas de esta Arquitectura

#### ✅ **Testabilidad**
- Tests unitarios con **repositorios falsos** (sin DB real)
- Ejemplo: `tests/test_user_service.py` usa `FakeUserRepository`

```python
class FakeUserRepository(UserRepositoryPort):
    def __init__(self):
        self.users = []  # En memoria, sin DB
```

#### ✅ **Desacoplamiento**
- Lógica de negocio **independiente** de Flask y SQLAlchemy
- Fácil migrar de SQLite a PostgreSQL (solo cambiar adaptador)
- Posible cambiar de Flask a FastAPI sin tocar servicios

#### ✅ **Mantenibilidad**
- Responsabilidades claras por capa
- Código organizado por dominio (pacientes, citas, empleados)
- Fácil localizar bugs y agregar features

#### ✅ **Escalabilidad Futura**
- Si el sistema crece, módulos pueden **extraerse** a microservicios
- Los puertos ya definen contratos para comunicación
- Ejemplo: `PatientService` podría ser un microservicio independiente

### Tecnologías por Capa

| Capa | Tecnologías |
|------|-------------|
| **Presentación** | Flask Blueprints, Jinja2, WTForms, Bootstrap 5 |
| **Aplicación** | Python 3.13, Servicios puros |
| **Dominio** | Python nativo (sin frameworks) |
| **Adaptadores** | SQLAlchemy, Werkzeug (hashing) |
| **Infraestructura** | Flask-Login, Flask-WTF, logging, auditoría |

### Convenciones de Código

#### Nombres de Archivos
- Puertos: `app/services/ports.py` (interfaces ABC)
- Servicios: `app/services/*_service.py` (casos de uso)
- Adaptadores: `app/adapters/sql_*_repository.py` (implementaciones)
- Rutas: `app/<modulo>/routes.py` (controladores)

#### Inyección de Dependencias
Manual mediante constructores:

```python
# En routes.py
user_repo = SqlAlchemyUserRepository()
user_service = UserService(user_repo)
```

En tests:
```python
# En test_user_service.py
fake_repo = FakeUserRepository()
user_service = UserService(fake_repo)
```

### Decisiones Arquitectónicas

#### ¿Por qué Monolito?
- **MVP:** Velocidad de desarrollo y simplicidad
- **Equipo pequeño:** Un solo desarrollador o equipo reducido
- **Requisitos claros:** Dominio bien definido (gestión IPS)

#### ¿Por qué Hexagonal?
- **Calidad de código:** Tests unitarios sin DB
- **Flexibilidad:** Cambiar DB/framework sin dolor
- **Preparación futura:** Migración a microservicios facilitada

#### ¿Cuándo escalar?
El monolito puede manejar **miles de usuarios** con:
- PostgreSQL en producción
- Caché con Redis
- Load balancer (múltiples instancias Flask)

Considerar microservicios solo si:
- Equipos independientes por módulo
- Escala diferenciada (ej: citas >> empleados)
- Tecnologías heterogéneas necesarias

---

## 1. REQUERIMIENTOS FUNCIONALES

### 1.1 Módulo de Autenticación y Seguridad

#### RF-001: Registro de Usuarios
**Descripción:** El sistema debe permitir el registro de nuevos usuarios con asignación de rol.

**Criterios de Aceptación:**
- El usuario debe proporcionar: username, contraseña, confirmación de contraseña, y rol
- La contraseña debe cumplir con la política de seguridad (mínimo 8 caracteres, mayúscula, minúscula, número, símbolo especial)
- El username debe ser único en el sistema
- El rol puede ser: admin, médico, enfermero, o recepcionista
- El sistema debe validar que las contraseñas coincidan
- Debe mostrar mensajes de error específicos si la validación falla
- Al completar el registro, redirige al login

**Prioridad:** Alta  
**Estado:** Implementado

---

#### RF-002: Inicio de Sesión
**Descripción:** El sistema debe permitir a usuarios registrados autenticarse con sus credenciales.

**Criterios de Aceptación:**
- El usuario debe proporcionar username y contraseña
- El sistema debe validar las credenciales contra la base de datos
- Si las credenciales son correctas, crear sesión y redirigir al dashboard
- Si son incorrectas, mostrar mensaje de error
- Implementar bloqueo de cuenta después de 5 intentos fallidos (15 minutos)
- Mostrar intentos restantes después de cada fallo
- Registrar todos los intentos de login en el log de auditoría

**Prioridad:** Alta  
**Estado:** Implementado

---

#### RF-003: Cierre de Sesión
**Descripción:** El sistema debe permitir a los usuarios cerrar su sesión activa.

**Criterios de Aceptación:**
- Destruir la sesión del usuario
- Redirigir a la página de inicio
- Mostrar mensaje de confirmación
- Limpiar todos los datos de sesión

**Prioridad:** Alta  
**Estado:** Implementado

---

#### RF-004: Control de Acceso Basado en Roles (RBAC)
**Descripción:** El sistema debe restringir el acceso a funcionalidades según el rol del usuario.

**Criterios de Aceptación:**
- **Admin:** Acceso total a todas las funcionalidades
- **Recepcionista:** CRUD pacientes, empleados (sin eliminar), citas completas
- **Médico:** Ver pacientes, gestionar citas, CRUD historias clínicas
- **Enfermero:** Ver pacientes, ver historias clínicas (solo lectura)
- Bloquear acceso no autorizado con código HTTP 403
- Mostrar mensaje de error cuando se intenta acceso no permitido
- Ocultar enlaces a funcionalidades no disponibles en la UI

**Prioridad:** Alta  
**Estado:** Implementado

---

### 1.2 Módulo de Gestión de Usuarios (Administración)

#### RF-005: Listar Usuarios del Sistema
**Descripción:** Los administradores deben poder ver todos los usuarios registrados.

**Criterios de Aceptación:**
- Solo accesible por usuarios con rol "admin"
- Mostrar: ID, username, rol actual
- Mostrar estadísticas por rol (contadores)
- Incluir opción para editar rol de cada usuario
- Usar badges de colores para identificar roles visualmente

**Prioridad:** Media  
**Estado:** Implementado

---

#### RF-006: Editar Rol de Usuario
**Descripción:** Los administradores deben poder cambiar el rol de cualquier usuario.

**Criterios de Aceptación:**
- Solo accesible por usuarios con rol "admin"
- Mostrar formulario con username (readonly) y selector de rol
- Permitir cambiar entre: admin, médico, enfermero, recepcionista
- Registrar cambio de rol en log de auditoría
- Mostrar mensaje de confirmación al guardar
- El cambio debe ser inmediato y afectar permisos del usuario

**Prioridad:** Media  
**Estado:** Implementado

---

### 1.3 Módulo de Gestión de Pacientes

#### RF-007: Listar Pacientes
**Descripción:** El sistema debe mostrar todos los pacientes registrados.

**Criterios de Aceptación:**
- Accesible por todos los usuarios autenticados
- Mostrar: nombre completo, documento, teléfono, email
- Incluir barra de búsqueda en tiempo real (nombre o documento)
- Mostrar contador total de pacientes
- Incluir botones de acción según permisos del usuario
- Mostrar estado vacío informativo si no hay pacientes

**Prioridad:** Alta  
**Estado:** Implementado

---

#### RF-008: Crear Paciente
**Descripción:** El sistema debe permitir registrar nuevos pacientes.

**Criterios de Aceptación:**
- Accesible por admin y recepcionista
- Campos requeridos: nombre, apellido, documento
- Campos opcionales: fecha de nacimiento, teléfono, email, dirección
- El documento debe ser único en el sistema
- Validar formato de email si se proporciona
- Registrar fecha de creación automáticamente
- Mostrar mensaje de éxito y redirigir a lista de pacientes

**Prioridad:** Alta  
**Estado:** Implementado

---

#### RF-009: Editar Paciente
**Descripción:** El sistema debe permitir actualizar información de pacientes existentes.

**Criterios de Aceptación:**
- Accesible por admin y recepcionista
- Pre-cargar datos actuales en el formulario
- Validar que el documento sea único (excepto el paciente actual)
- Permitir actualizar todos los campos
- Registrar cambios en log de auditoría
- Mostrar mensaje de éxito al guardar

**Prioridad:** Alta  
**Estado:** Implementado

---

#### RF-010: Eliminar Paciente
**Descripción:** El sistema debe permitir eliminar pacientes del sistema.

**Criterios de Aceptación:**
- Accesible solo por admin
- Solicitar confirmación antes de eliminar
- Eliminar en cascada: citas y registros médicos asociados
- Registrar eliminación en log de auditoría
- Mostrar mensaje de confirmación
- Redirigir a lista de pacientes

**Prioridad:** Media  
**Estado:** Implementado

---

### 1.4 Módulo de Gestión de Citas

#### RF-011: Listar Citas
**Descripción:** El sistema debe mostrar todas las citas médicas.

**Criterios de Aceptación:**
- Accesible por usuarios autenticados
- Mostrar: paciente, fecha/hora, motivo, estado
- Usar código de colores por estado (programada=azul, completada=verde, cancelada=gris)
- Incluir filtros por estado (todas, programadas, completadas, canceladas)
- Mostrar contadores por estado
- Vista de tarjetas (cards) para mejor visualización

**Prioridad:** Alta  
**Estado:** Implementado

---

#### RF-012: Crear Cita
**Descripción:** El sistema debe permitir agendar nuevas citas médicas.

**Criterios de Aceptación:**
- Accesible por admin, recepcionista y médico
- Seleccionar paciente de lista desplegable
- Ingresar fecha y hora (formato: YYYY-MM-DD HH:MM)
- Especificar motivo de consulta (opcional)
- Estado inicial: "scheduled"
- Validar que la fecha/hora sea válida
- Registrar creación en log de auditoría
- Mostrar mensaje de confirmación

**Prioridad:** Alta  
**Estado:** Implementado

---

#### RF-013: Cancelar Cita
**Descripción:** El sistema debe permitir cancelar citas programadas.

**Criterios de Aceptación:**
- Accesible por admin, recepcionista y médico
- Solo permitir cancelar citas con estado "scheduled"
- Solicitar confirmación antes de cancelar
- Cambiar estado a "cancelled"
- Registrar cancelación en log de auditoría
- Mantener registro histórico (no eliminar)

**Prioridad:** Media  
**Estado:** Implementado

---

### 1.5 Módulo de Historias Clínicas

#### RF-014: Ver Historia Clínica de Paciente
**Descripción:** El sistema debe mostrar el registro médico completo de un paciente.

**Criterios de Aceptación:**
- Accesible por admin, médico y enfermero
- Mostrar información del paciente en encabezado
- Listar todas las entradas médicas en orden cronológico (más reciente primero)
- Cada entrada debe mostrar: fecha/hora, título, notas
- Incluir contador total de entradas
- Botón para agregar nueva entrada (si tiene permisos)
- Botón para volver a lista de pacientes

**Prioridad:** Alta  
**Estado:** Implementado

---

#### RF-015: Agregar Entrada a Historia Clínica
**Descripción:** El sistema debe permitir agregar nuevos registros médicos.

**Criterios de Aceptación:**
- Accesible solo por admin y médico
- Campos requeridos: título
- Campos opcionales: notas detalladas
- Asociar entrada al paciente correcto
- Registrar fecha/hora de creación automáticamente
- Registrar en log de auditoría
- Mostrar mensaje de confirmación
- Redirigir a vista de historia clínica

**Prioridad:** Alta  
**Estado:** Implementado

---

#### RF-016: Listar Todos los Pacientes con Historias
**Descripción:** El sistema debe mostrar una lista de todos los pacientes para acceder a sus historias.

**Criterios de Aceptación:**
- Accesible por admin, médico y enfermero
- Mostrar lista de pacientes con enlace a su historia clínica
- Búsqueda por nombre o documento
- Indicar cantidad de entradas por paciente (opcional)

**Prioridad:** Media  
**Estado:** Implementado

---

### 1.6 Módulo de Gestión de Empleados

#### RF-017: Listar Empleados
**Descripción:** El sistema debe mostrar todos los empleados de la institución.

**Criterios de Aceptación:**
- Accesible por todos los usuarios autenticados
- Mostrar: nombre completo, documento, cargo, teléfono, email
- Incluir barra de búsqueda en tiempo real
- Mostrar contador total de empleados
- Botones de acción según permisos del usuario

**Prioridad:** Media  
**Estado:** Implementado

---

#### RF-018: Crear Empleado
**Descripción:** El sistema debe permitir registrar nuevos empleados.

**Criterios de Aceptación:**
- Accesible por admin y recepcionista
- Campos requeridos: nombre, apellido, documento, cargo
- Campos opcionales: fecha de contratación, teléfono, email
- El documento debe ser único
- Validar formato de email
- Registrar en log de auditoría
- Mostrar mensaje de éxito

**Prioridad:** Media  
**Estado:** Implementado

---

#### RF-019: Editar Empleado
**Descripción:** El sistema debe permitir actualizar información de empleados.

**Criterios de Aceptación:**
- Accesible por admin y recepcionista
- Pre-cargar datos actuales
- Validar unicidad de documento
- Permitir actualizar todos los campos
- Registrar cambios en auditoría

**Prioridad:** Media  
**Estado:** Implementado

---

#### RF-020: Eliminar Empleado
**Descripción:** El sistema debe permitir eliminar empleados del sistema.

**Criterios de Aceptación:**
- Accesible solo por admin
- Solicitar confirmación
- Registrar eliminación en auditoría
- Mostrar mensaje de confirmación

**Prioridad:** Baja  
**Estado:** Implementado

---

## 2. REQUERIMIENTOS NO FUNCIONALES

### 2.1 Seguridad

#### RNF-001: Política de Contraseñas
**Descripción:** Las contraseñas deben cumplir estándares de seguridad.

**Especificaciones:**
- Longitud mínima: 8 caracteres
- Debe incluir al menos: 1 mayúscula, 1 minúscula, 1 número, 1 símbolo especial
- Almacenamiento: Hash con bcrypt (no texto plano)
- Mensajes de error descriptivos para el usuario

**Estándar:** ISO 27001 - A.9.4.3  
**Estado:** Implementado

---

#### RNF-002: Protección CSRF
**Descripción:** Todos los formularios deben estar protegidos contra ataques CSRF.

**Especificaciones:**
- Uso de Flask-WTF con tokens CSRF
- Token único por sesión
- Validación automática en el servidor
- Tokens embebidos en todos los formularios HTML

**Estándar:** OWASP Top 10  
**Estado:** Implementado

---

#### RNF-003: Sesiones Seguras
**Descripción:** Las sesiones deben ser gestionadas de forma segura.

**Especificaciones:**
- Cookies con flags: HttpOnly, Secure (HTTPS), SameSite=Lax
- Timeout de sesión: 30 minutos de inactividad
- Invalidación de sesión al cerrar sesión
- Regeneración de ID de sesión después del login

**Estándar:** ISO 27001 - A.9.4.2, A.18.1.3  
**Estado:** Implementado

---

#### RNF-004: Bloqueo de Cuenta por Intentos Fallidos
**Descripción:** Proteger contra ataques de fuerza bruta.

**Especificaciones:**
- Máximo 5 intentos fallidos de login
- Bloqueo automático por 15 minutos
- Contador de intentos visible para el usuario
- Reset automático de contador al login exitoso
- Registro en log de auditoría de todos los intentos

**Estándar:** ISO 27001 - A.9.4.2, A.9.4.4  
**Estado:** Implementado

---

#### RNF-005: Rate Limiting
**Descripción:** Limitar solicitudes para prevenir abuso del sistema.

**Especificaciones:**
- Límite: 30 solicitudes por minuto por IP
- Tracking combinado: IP + username (si está autenticado)
- Respuesta HTTP 429 al exceder límite
- Aplicado a endpoints críticos: /auth/login, /auth/register
- Almacenamiento en memoria con limpieza automática

**Estándar:** ISO 27001 - A.9.4.4  
**Estado:** Implementado

---

#### RNF-006: Headers de Seguridad
**Descripción:** Implementar headers HTTP de seguridad.

**Especificaciones:**
- Content-Security-Policy: Prevenir XSS e inyección de código
- X-Frame-Options: SAMEORIGIN (prevenir clickjacking)
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: Bloquear geolocalización, micrófono, cámara

**Estándar:** ISO 27001 - A.14.1.2, A.14.1.3  
**Estado:** Implementado

---

#### RNF-007: Auditoría y Logging
**Descripción:** Registrar todas las acciones críticas del sistema.

**Especificaciones:**
- Eventos registrados: login/logout, cambios de roles, CRUD en todas las entidades
- Información capturada: timestamp, usuario, IP, acción, detalles
- Almacenamiento: logs/audit.log con rotación automática
- Formato: JSON estructurado
- Retención: Logs persistentes (no se eliminan automáticamente)

**Estándar:** ISO 27001 - A.12.4.1, A.12.4.3  
**Estado:** Implementado

---

### 2.2 Rendimiento

#### RNF-008: Tiempo de Respuesta
**Descripción:** El sistema debe responder en tiempo aceptable.

**Especificaciones:**
- Páginas estáticas: < 500ms
- Operaciones CRUD: < 1 segundo
- Búsquedas: < 2 segundos
- Login: < 1 segundo

**Estado:** Implementado (SQLite en desarrollo)

---

#### RNF-009: Capacidad de Usuarios Concurrentes
**Descripción:** Soporte para múltiples usuarios simultáneos.

**Especificaciones:**
- Mínimo: 50 usuarios concurrentes
- Recomendado: 200+ usuarios (con servidor WSGI en producción)
- Sin degradación significativa de rendimiento

**Estado:** Parcial (requiere servidor de producción)

---

### 2.3 Usabilidad

#### RNF-010: Interfaz de Usuario Intuitiva
**Descripción:** La interfaz debe ser fácil de usar y comprender.

**Especificaciones:**
- Diseño responsive (móvil, tablet, desktop)
- Iconos descriptivos (Bootstrap Icons)
- Código de colores consistente por módulo
- Feedback visual en todas las acciones
- Mensajes de error claros y en español
- Navegación consistente con breadcrumbs

**Estado:** Implementado

---

#### RNF-011: Accesibilidad
**Descripción:** El sistema debe ser accesible para usuarios con discapacidades.

**Especificaciones:**
- Etiquetas ARIA en elementos interactivos
- Contraste de colores adecuado (WCAG AA)
- Navegación por teclado funcional
- Formularios con labels asociados
- Mensajes de error descriptivos

**Estado:** Parcial (mejoras continuas)

---

#### RNF-012: Mensajes de Usuario
**Descripción:** Todos los mensajes deben estar en español.

**Especificaciones:**
- Mensajes de éxito/error en español
- Validaciones de formularios en español
- Interfaz completamente en español
- Excepciones: Logs técnicos pueden estar en inglés

**Estado:** Implementado

---

### 2.4 Mantenibilidad

#### RNF-013: Arquitectura Hexagonal
**Descripción:** Separación clara de capas y responsabilidades.

**Especificaciones:**
- **Dominio:** Modelos SQLAlchemy (models.py)
- **Puertos:** Interfaces de repositorio (ports.py)
- **Adaptadores:** Implementaciones SQLAlchemy (adapters/)
- **Servicios:** Lógica de negocio (services/)
- **Presentación:** Blueprints Flask (routes.py)
- Inyección de dependencias manual en rutas

**Estado:** Implementado

---

#### RNF-014: Cobertura de Tests
**Descripción:** El código debe tener tests automatizados.

**Especificaciones:**
- Framework: pytest + pytest-flask
- Tests de autenticación (login, registro, logout)
- Tests de servicios de dominio (UserService)
- Tests con fixtures para aislamiento
- Ejecución: `pytest -q`
- Cobertura actual: 16 tests pasando

**Estado:** Implementado (cobertura parcial)

---

#### RNF-015: Documentación
**Descripción:** El código y la arquitectura deben estar documentados.

**Especificaciones:**
- README.md con instrucciones de instalación y uso
- .github/copilot-instructions.md para guías de AI
- Docstrings en funciones críticas
- Comentarios en código complejo
- Documentación de RBAC (docs/security/RBAC.md)

**Estado:** Implementado

---

### 2.5 Portabilidad

#### RNF-016: Compatibilidad de Base de Datos
**Descripción:** Soporte para múltiples motores de base de datos.

**Especificaciones:**
- Desarrollo: SQLite (app.db)
- Testing: SQLite en memoria
- Producción: PostgreSQL / MySQL (vía SQLAlchemy)
- Migraciones: Alembic (futuro)

**Estado:** SQLite implementado, otros compatibles por SQLAlchemy

---

#### RNF-017: Compatibilidad de Navegadores
**Descripción:** El sistema debe funcionar en navegadores modernos.

**Especificaciones:**
- Chrome/Edge: últimas 2 versiones
- Firefox: últimas 2 versiones
- Safari: últimas 2 versiones
- No soporta: IE 11 o anteriores

**Estado:** Implementado (Bootstrap 5 + ES6)

---

### 2.6 Escalabilidad

#### RNF-018: Escalabilidad Horizontal
**Descripción:** Preparado para escalar con múltiples instancias.

**Especificaciones:**
- Sesiones pueden moverse a Redis/Memcached
- Base de datos centralizada
- Sin estado en servidor (stateless después de usar Redis)
- Balanceo de carga compatible

**Estado:** Diseño permite escalabilidad (implementación futura)

---

#### RNF-019: Almacenamiento de Archivos
**Descripción:** Preparado para almacenar documentos médicos.

**Especificaciones:**
- Actualmente: Solo texto en base de datos
- Futuro: S3/Azure Blob Storage para imágenes y PDFs
- Campo adicional en modelos para URLs de archivos

**Estado:** No implementado (futuro)

---

### 2.7 Configuración y Despliegue

#### RNF-020: Variables de Entorno
**Descripción:** Configuración mediante variables de entorno.

**Especificaciones:**
- Archivo .env para desarrollo local
- Variables: SECRET_KEY, DATABASE_URL, SESSION_TIMEOUT, etc.
- Valores por defecto seguros
- Documentadas en README

**Estado:** Implementado (config.py)

---

#### RNF-021: Modo Debug/Producción
**Descripción:** Comportamiento diferente según entorno.

**Especificaciones:**
- Desarrollo: DEBUG=True, auto-reload, stack traces
- Producción: DEBUG=False, logs detallados, sin stack traces públicos
- TESTING=True para desactivar CSRF en tests

**Estado:** Implementado

---

#### RNF-022: Servidor WSGI para Producción
**Descripción:** No usar servidor de desarrollo en producción.

**Especificaciones:**
- Recomendado: Gunicorn (Linux/Mac) o Waitress (Windows)
- Configuración: workers=4, threads=2
- Reverse proxy: Nginx/Apache
- Certificado SSL en producción

**Estado:** Documentado (no implementado aún)

---

## 3. MATRIZ DE TRAZABILIDAD

| ID | Requerimiento | Módulo | Prioridad | Estado | Pruebas |
|----|---------------|--------|-----------|--------|---------|
| RF-001 | Registro usuarios | Auth | Alta | ✅ | test_auth.py |
| RF-002 | Login | Auth | Alta | ✅ | test_auth.py |
| RF-003 | Logout | Auth | Alta | ✅ | test_auth.py |
| RF-004 | RBAC | Security | Alta | ✅ | Manual |
| RF-005 | Listar usuarios | Admin | Media | ✅ | Manual |
| RF-006 | Editar rol | Admin | Media | ✅ | Manual |
| RF-007 | Listar pacientes | Patients | Alta | ✅ | Manual |
| RF-008 | Crear paciente | Patients | Alta | ✅ | Manual |
| RF-009 | Editar paciente | Patients | Alta | ✅ | Manual |
| RF-010 | Eliminar paciente | Patients | Media | ✅ | Manual |
| RF-011 | Listar citas | Appointments | Alta | ✅ | Manual |
| RF-012 | Crear cita | Appointments | Alta | ✅ | Manual |
| RF-013 | Cancelar cita | Appointments | Media | ✅ | Manual |
| RF-014 | Ver historia | Records | Alta | ✅ | Manual |
| RF-015 | Agregar entrada | Records | Alta | ✅ | Manual |
| RF-016 | Listar pacientes | Records | Media | ✅ | Manual |
| RF-017 | Listar empleados | Employees | Media | ✅ | Manual |
| RF-018 | Crear empleado | Employees | Media | ✅ | Manual |
| RF-019 | Editar empleado | Employees | Media | ✅ | Manual |
| RF-020 | Eliminar empleado | Employees | Baja | ✅ | Manual |

---

## 4. REQUERIMIENTOS DE CALIDAD Y TESTING (Sprint 2)

### 4.1 Requerimientos de Performance

| Requisito | Métrica | Objetivo | Validación |
|-----------|---------|----------|------------|
| **Queries simples** | Tiempo de respuesta | < 50ms | pytest-benchmark |
| **Queries con JOINs** | Tiempo de respuesta | < 100ms | pytest-benchmark |
| **Endpoints API** | Tiempo de respuesta | < 200ms | pytest-benchmark |
| **Bulk operations (100)** | Tiempo de operación | < 5s | pytest-benchmark |
| **Bulk read (1000)** | Tiempo de lectura | < 1s | pytest-benchmark |
| **Memory usage** | Uso de memoria | < 50MB/operación | memory-profiler |
| **Throughput** | Requests por segundo | > 50 RPS | Locust |
| **Response time (p95)** | Percentil 95 | < 500ms | Locust |
| **Error rate** | Tasa de errores | < 1% | Locust |
| **Concurrent users** | Usuarios concurrentes | 100 sin degradación | Locust |

**Herramientas de validación:**
- `pytest-benchmark` - Benchmarking automatizado
- `py-spy` - Profiling de CPU
- `memory-profiler` - Análisis de memoria
- `locust` - Load testing con 100 usuarios concurrentes

### 4.2 Requerimientos de Seguridad OWASP Top 10 (2021)

| Categoría OWASP | Requisito | Implementación | Validación |
|-----------------|-----------|----------------|------------|
| **A01: Broken Access Control** | Prevenir IDOR, forced browsing | RBAC + verificación IDs | 8 tests automatizados |
| **A02: Cryptographic Failures** | Password hashing, secure cookies | Werkzeug bcrypt | 5 tests automatizados |
| **A03: Injection** | Prevenir SQL/Command injection | Prepared statements | 6 tests automatizados |
| **A04: Insecure Design** | Rate limiting, account lockout | RateLimiter 5/min | 4 tests automatizados |
| **A05: Security Misconfiguration** | Security headers, HTTPS | CSP, X-Frame-Options | 5 tests automatizados |
| **A06: Vulnerable Components** | Sin vulnerabilidades conocidas | Safety check | 2 tests automatizados |
| **A07: Authentication Failures** | Session security, password policy | Lockout 3 intentos | 6 tests automatizados |
| **A08: Integrity Failures** | CSRF protection | WTForms CSRF token | 2 tests automatizados |
| **A09: Logging Failures** | Audit logging completo | AuditLogger | 3 tests automatizados |
| **A10: SSRF** | URL validation | Input sanitization | 2 tests automatizados |

**Total:** 40+ tests automatizados de seguridad en `tests/test_security_owasp.py`

### 4.3 Requerimientos de Usabilidad WCAG 2.1 Level AA

| Criterio | Requisito | Objetivo | Validación |
|----------|-----------|----------|------------|
| **1.1.1 Non-text Content** | Alt text en imágenes | 100% de imágenes | Selenium + BeautifulSoup |
| **1.3.1 Info and Relationships** | Form labels asociados | input[id] + label[for] | pytest HTML parsing |
| **2.1.1 Keyboard** | Navegación por teclado | Tab order lógico | Selenium |
| **2.4.4 Link Purpose** | Enlaces descriptivos | Texto claro (no "click aquí") | pytest HTML parsing |
| **2.5.5 Target Size** | Touch targets | ≥ 44x44px | pytest CSS parsing |
| **3.1.1 Language** | Idioma declarado | `<html lang="es">` | pytest HTML parsing |
| **3.2.1 On Focus** | No cambios inesperados | Focus sin submit | Selenium |
| **3.3.1 Error Identification** | Errores descriptivos | Mensajes claros en español | pytest functional |
| **3.3.2 Labels** | Etiquetas de campos | Todos los inputs | pytest HTML parsing |
| **4.1.2 Name, Role, Value** | ARIA roles | Elementos semánticos | pytest HTML parsing |

**Criterios adicionales:**
- Font size mínimo: 14px
- Line height mínimo: 1.5
- Paragraph width máximo: 80 caracteres
- Color contrast: 4.5:1 para texto normal
- Viewport responsive: meta tag presente
- No horizontal scroll en móvil

**Total:** 30+ tests de usabilidad y accesibilidad en `tests/test_usability.py`

### 4.4 Requerimientos de Cobertura de Tests

| Módulo | Objetivo | Sprint 1 | Sprint 2 | Estado |
|--------|----------|----------|----------|--------|
| **auth/** | > 80% | 83% | - | ✅ |
| **services/** | > 80% | 100% | - | ✅ |
| **infrastructure/security/** | > 80% | 91-100% | - | ✅ |
| **patients/** | > 70% | - | 🔄 | En progreso |
| **appointments/** | > 70% | - | 🔄 | En progreso |
| **employees/** | > 70% | - | 🔄 | En progreso |
| **admin/** | > 70% | - | 🔄 | En progreso |
| **Cobertura global** | > 80% | 66% | 70%+ | 🔄 En progreso |

**Total de tests:** 52 (Sprint 1) + 90+ (Sprint 2) = **142+ tests automatizados**

---

## 5. CUMPLIMIENTO ISO 27001

| Control | Descripción | Implementación |
|---------|-------------|----------------|
| A.9.2.4 | Gestión de información secreta de autenticación | Bcrypt hash, no texto plano |
| A.9.4.2 | Acceso seguro al sistema | Sesiones seguras, timeout, lockout |
| A.9.4.3 | Sistema de gestión de contraseñas | Política de contraseñas fuerte |
| A.9.4.4 | Prevención de fuerza bruta | Rate limiting + lockout |
| A.9.1 | Control de acceso | RBAC con 4 roles |
| A.9.2 | Gestión de usuarios | Panel de administración |
| A.12.4.1 | Registro de eventos | AuditLogger para todas las acciones |
| A.12.4.3 | Logs de administrador | Auditoría de cambios de roles |
| A.14.1.2 | Seguridad en desarrollo | Headers de seguridad, CSP |
| A.14.1.3 | Protección de transacciones | CSRF tokens, HTTPS ready |
| A.18.1.3 | Privacidad de datos | Sesiones cifradas, datos protegidos |

---

## 5. DEPENDENCIAS TÉCNICAS

### 5.1 Backend (Producción)
- **Flask** 3.1.2 - Framework web
- **SQLAlchemy** 3.1.1 - ORM
- **Flask-Login** 0.6.3 - Gestión de sesiones
- **Flask-WTF** 1.2.2 - Formularios y CSRF
- **Flask-Caching** 2.3.0 - Caching layer
- **Werkzeug** 3.1.3 - Utilidades de seguridad
- **python-dotenv** - Variables de entorno

### 5.2 Testing y Quality Assurance
- **pytest** 8.4.2 - Framework de pruebas
- **pytest-flask** 1.3.0 - Extensión Flask
- **pytest-cov** 7.0.0 - Cobertura de código
- **pytest-benchmark** 4.0.0 - Performance testing
- **locust** 2.31.8 - Load testing
- **selenium** 4.25.0 - E2E testing
- **beautifulsoup4** 4.12.3 - HTML parsing

### 5.3 Profiling y Análisis
- **py-spy** 0.3.14 - CPU profiler
- **memory-profiler** 0.61.0 - Memory analysis
- **safety** 3.2.0 - Dependency vulnerability scanner

### 5.4 Code Quality
- **pylint** 3.3.0 - Code quality analysis
- **black** 24.8.0 - Code formatter
- **isort** 5.13.2 - Import sorting
- **bandit** 1.8.6 - Security linter

### 5.5 Frontend
- **Bootstrap** 5.1.3 - Framework CSS
- **Bootstrap Icons** 1.8.0 - Iconografía
- **JavaScript** Vanilla - Interactividad

### 5.6 Base de Datos
- **SQLite** 3.x (desarrollo)
- Compatible con PostgreSQL/MySQL (producción)
- **Índices estratégicos:** 12 índices para optimización

---

## 6. MÉTRICAS DE CALIDAD

| Métrica | Objetivo | Sprint 1 | Sprint 2 | Estado |
|---------|----------|----------|----------|--------|
| **Tests pasando** | 100% | 16/16 (100%) | 52/52 (100%) | ✅ |
| **Tests de seguridad OWASP** | Top 10 completo | - | 40+ tests (100%) | ✅ |
| **Tests de performance** | Suite completa | - | 20 tests | ✅ |
| **Tests de usabilidad** | WCAG 2.1 AA | - | 30+ tests | ✅ |
| **Cobertura de código** | >80% | 66% | 70%+ | 🔄 En progreso |
| **Tiempo de respuesta endpoints** | <200ms | <500ms | <200ms (validado) | ✅ |
| **Tiempo de queries simples** | <50ms | No medido | <50ms (validado) | ✅ |
| **Usuarios concurrentes** | 100 | No medido | 100 (Locust) | ✅ |
| **Throughput** | >50 RPS | No medido | >50 RPS (objetivo) | 🔄 |
| **Error rate** | <1% | - | <1% (objetivo) | 🔄 |
| **Pylint score** | >8.5/10 | 6.93/10 | 8.5+ (objetivo) | 🔄 En progreso |
| **Vulnerabilidades conocidas** | 0 | 0 (Bandit) | 0 (Safety) | ✅ |
| **Uptime** | 99.5% | No aplica (dev) | No aplica (dev) | - |

**Resumen de Testing:**
- **Sprint 1:** 52 tests core (autenticación, servicios, arquitectura)
- **Sprint 2:** 90+ tests adicionales (performance, seguridad, usabilidad)
- **Total:** 142+ tests automatizados
- **Herramientas:** pytest, locust, selenium, safety, pylint, black

---

## 7. ROADMAP FUTURO

### Funcionalidades Pendientes (Post-Sprint 2)
- [ ] Citas recurrentes
- [ ] Notificaciones por email/SMS
- [ ] Calendario visual de citas
- [ ] Reportes y estadísticas con gráficas
- [ ] Exportación de datos (PDF, Excel)
- [ ] Adjuntar archivos a historias clínicas (imágenes, PDFs)
- [ ] Búsqueda avanzada con filtros múltiples
- [ ] Dashboard con gráficas interactivas (Chart.js)
- [ ] API REST para integración externa
- [ ] Aplicación móvil (React Native o Flutter)

### Mejoras Técnicas Pendientes
- [ ] **Caching con Redis:** Implementar Flask-Caching con backend Redis
- [ ] **Migraciones:** Alembic para versionado de base de datos
- [ ] **Tareas asíncronas:** Celery para envío de emails y reportes
- [ ] **WebSockets:** Notificaciones en tiempo real con Socket.IO
- [ ] **Containerización:** Dockerfile y docker-compose
- [ ] **CI/CD pipeline:** GitHub Actions con tests automatizados
- [ ] **Monitoreo:** Prometheus + Grafana para métricas
- [ ] **APM:** Application Performance Monitoring con New Relic/Datadog
- [ ] **Database replication:** PostgreSQL master-slave
- [ ] **CDN:** CloudFlare para assets estáticos

### Mejoras de Calidad (Sprint 3)
- [ ] **Aumentar cobertura a 80%+:** Más tests unitarios e integración
- [ ] **Pylint 8.5+:** Refactorización para mejorar code quality
- [ ] **E2E tests:** Suite completa con Selenium
- [ ] **Mutation testing:** Verificar calidad de tests con mutmut
- [ ] **Security hardening:** Implementar CSP Level 3, SRI
- [ ] **GDPR compliance:** Right to erasure, data portability

### Optimizaciones de Performance Aplicadas (Sprint 2)
- ✅ **Database indexing:** 12 índices estratégicos implementados
- ✅ **Benchmarking:** pytest-benchmark con objetivos claros
- ✅ **Load testing:** Locust con 100 usuarios concurrentes
- ✅ **Memory profiling:** memory-profiler para detectar leaks
- ✅ **N+1 query prevention:** Eager loading en relationships
- 🔄 **Query optimization:** Análisis con EXPLAIN QUERY PLAN (en progreso)
- 🔄 **Flask-Caching:** Instalado, pendiente implementación en endpoints

---

**Documento preparado por:** Sistema IPS Development Team  
**Última actualización:** 30 de Octubre de 2025 (Sprint 2 Testing & Optimization)  
**Versión del documento:** 1.2.0
