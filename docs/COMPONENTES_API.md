# 📚 DOCUMENTACIÓN DE COMPONENTES Y APIs INTERNAS

**Sistema IPS - Arquitectura Hexagonal**

---

## 🔌 PUERTOS (INTERFACES)

### UserRepositoryPort

**Ubicación:** `app/services/ports.py`

```python
class UserRepositoryPort(ABC):
    """
    Puerto para operaciones de persistencia de usuarios.
    ISO 27001: A.9.2.1, A.9.2.6
    """
    
    @abstractmethod
    def add(self, user: User) -> User:
        """
        Guarda un nuevo usuario en el sistema.
        
        Args:
            user (User): Instancia de User con datos validados
        
        Returns:
            User: Usuario guardado con ID asignado
        
        Raises:
            IntegrityError: Si el username ya existe
        """
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        """
        Busca un usuario por su nombre de usuario.
        
        Args:
            username (str): Nombre de usuario único
        
        Returns:
            User | None: Usuario encontrado o None
        """
        pass
```

---

### PatientRepositoryPort

```python
class PatientRepositoryPort(ABC):
    """
    Puerto para operaciones CRUD de pacientes.
    ISO 27001: A.18.1.3 (Protección de datos personales)
    """
    
    @abstractmethod
    def add(self, patient: Patient) -> Patient:
        """Crea un nuevo paciente"""
        pass
    
    @abstractmethod
    def update(self, patient: Patient) -> Patient:
        """Actualiza datos de un paciente existente"""
        pass
    
    @abstractmethod
    def delete(self, patient_id: int) -> None:
        """Elimina un paciente (soft delete recomendado)"""
        pass
    
    @abstractmethod
    def get(self, patient_id: int) -> Patient | None:
        """Obtiene un paciente por ID"""
        pass
    
    @abstractmethod
    def get_by_document(self, document: str) -> Patient | None:
        """Busca paciente por documento de identidad"""
        pass
    
    @abstractmethod
    def list(self) -> List[Patient]:
        """Lista todos los pacientes activos"""
        pass
```

---

### AppointmentRepositoryPort

```python
class AppointmentRepositoryPort(ABC):
    """Puerto para gestión de citas médicas"""
    
    @abstractmethod
    def add(self, appointment: Appointment) -> Appointment:
        """Crea una nueva cita"""
        pass
    
    @abstractmethod
    def get(self, appointment_id: int) -> Appointment | None:
        """Obtiene una cita por ID"""
        pass
    
    @abstractmethod
    def update(self, appointment: Appointment) -> Appointment:
        """Actualiza una cita existente"""
        pass
    
    @abstractmethod
    def list(self) -> List[Appointment]:
        """Lista todas las citas"""
        pass
    
    @abstractmethod
    def list_by_patient(self, patient_id: int) -> List[Appointment]:
        """Lista citas de un paciente específico"""
        pass
```

---

### MedicalRecordRepositoryPort

```python
class MedicalRecordRepositoryPort(ABC):
    """
    Puerto para historiales clínicos.
    ISO 27001: A.18.1.3 (Protección de datos sensibles)
    """
    
    @abstractmethod
    def add(self, record: MedicalRecord) -> MedicalRecord:
        """Crea un nuevo registro médico"""
        pass
    
    @abstractmethod
    def list_by_patient(self, patient_id: int) -> List[MedicalRecord]:
        """Lista todos los registros médicos de un paciente"""
        pass
```

---

### EmployeeRepositoryPort

```python
class EmployeeRepositoryPort(ABC):
    """Puerto para gestión de empleados de la IPS"""
    
    @abstractmethod
    def add(self, employee: Employee) -> Employee:
        """Registra un nuevo empleado"""
        pass
    
    @abstractmethod
    def update(self, employee: Employee) -> Employee:
        """Actualiza datos de un empleado"""
        pass
    
    @abstractmethod
    def delete(self, employee_id: int) -> None:
        """Elimina un empleado"""
        pass
    
    @abstractmethod
    def get(self, employee_id: int) -> Employee | None:
        """Obtiene un empleado por ID"""
        pass
    
    @abstractmethod
    def get_by_document(self, document: str) -> Employee | None:
        """Busca empleado por documento de identidad"""
        pass
    
    @abstractmethod
    def list(self) -> List[Employee]:
        """Lista todos los empleados activos"""
        pass
```

---

## 💼 SERVICIOS DE APLICACIÓN (CASOS DE USO)

### UserService

**Ubicación:** `app/services/user_service.py`

```python
class UserService:
    """
    Servicio de gestión de usuarios.
    Implementa casos de uso relacionados con autenticación y autorización.
    """
    
    def __init__(self, user_repository: UserRepositoryPort):
        """
        Constructor con inyección de dependencias.
        
        Args:
            user_repository: Implementación del puerto UserRepositoryPort
        """
        self.user_repo = user_repository
    
    def register_user(self, username: str, password: str, role: str) -> Tuple[bool, str]:
        """
        Caso de uso: Registrar nuevo usuario en el sistema.
        ISO 27001: A.9.2.1 - User registration
        
        Args:
            username (str): Nombre de usuario único
            password (str): Contraseña (será hasheada)
            role (str): Rol del usuario ('admin', 'medico', 'usuario')
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        
        Business Rules:
            - Username debe ser único
            - Password debe tener mínimo 8 caracteres
            - Role debe ser válido
        """
        # Validación de negocio
        if self.user_repo.get_by_username(username):
            return False, "Usuario ya existe"
        
        if len(password) < 8:
            return False, "Contraseña debe tener al menos 8 caracteres"
        
        if role not in ['admin', 'medico', 'usuario']:
            return False, "Rol inválido"
        
        # Crear y persistir
        user = User(username=username, role=role)
        user.set_password(password)
        self.user_repo.add(user)
        
        return True, "Usuario registrado exitosamente"
```

---

### PatientService

**Ubicación:** `app/services/patient_service.py`

```python
class PatientService:
    """Servicio de gestión de pacientes"""
    
    def __init__(self, patient_repository: PatientRepositoryPort):
        self.patient_repo = patient_repository
    
    def create_patient(self, nombre: str, documento: str, 
                      fecha_nacimiento: datetime, **kwargs) -> Tuple[bool, str, Patient | None]:
        """
        Caso de uso: Registrar nuevo paciente.
        ISO 27001: A.18.1.3 - Protección de datos personales
        
        Args:
            nombre (str): Nombre completo del paciente
            documento (str): Documento de identidad único
            fecha_nacimiento (datetime): Fecha de nacimiento
            **kwargs: Datos adicionales (dirección, teléfono, etc.)
        
        Returns:
            Tuple[bool, str, Patient | None]: (éxito, mensaje, paciente creado)
        
        Business Rules:
            - Documento debe ser único
            - Fecha de nacimiento debe ser válida (no futura)
            - Nombre no puede estar vacío
        """
        # Validaciones de negocio
        if self.patient_repo.get_by_document(documento):
            return False, "Ya existe un paciente con ese documento", None
        
        if fecha_nacimiento > datetime.now():
            return False, "Fecha de nacimiento no puede ser futura", None
        
        if not nombre or len(nombre) < 3:
            return False, "Nombre inválido", None
        
        # Crear paciente
        patient = Patient(
            nombre=nombre,
            documento=documento,
            fecha_nacimiento=fecha_nacimiento,
            **kwargs
        )
        
        saved_patient = self.patient_repo.add(patient)
        return True, "Paciente registrado exitosamente", saved_patient
    
    def update_patient(self, patient_id: int, **kwargs) -> Tuple[bool, str]:
        """
        Caso de uso: Actualizar datos de paciente.
        
        Args:
            patient_id (int): ID del paciente
            **kwargs: Campos a actualizar
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        patient = self.patient_repo.get(patient_id)
        
        if not patient:
            return False, "Paciente no encontrado"
        
        # Actualizar campos
        for key, value in kwargs.items():
            if hasattr(patient, key):
                setattr(patient, key, value)
        
        self.patient_repo.update(patient)
        return True, "Paciente actualizado exitosamente"
    
    def list_all_patients(self) -> List[Patient]:
        """
        Caso de uso: Listar todos los pacientes.
        
        Returns:
            List[Patient]: Lista de pacientes activos
        """
        return self.patient_repo.list()
```

---

### EmployeeService

**Ubicación:** `app/services/employee_service.py`

```python
class EmployeeService:
    """Servicio de gestión de empleados"""
    
    def __init__(self, employee_repository: EmployeeRepositoryPort):
        self.employee_repo = employee_repository
    
    def create_employee(self, nombre: str, documento: str, 
                       cargo: str, **kwargs) -> Tuple[bool, str, Employee | None]:
        """
        Caso de uso: Registrar nuevo empleado.
        
        Args:
            nombre (str): Nombre completo
            documento (str): Documento de identidad único
            cargo (str): Cargo/posición
            **kwargs: Datos adicionales
        
        Returns:
            Tuple[bool, str, Employee | None]: (éxito, mensaje, empleado)
        """
        # Validar unicidad de documento
        if self.employee_repo.get_by_document(documento):
            return False, "Ya existe un empleado con ese documento", None
        
        employee = Employee(
            nombre=nombre,
            documento=documento,
            cargo=cargo,
            **kwargs
        )
        
        saved = self.employee_repo.add(employee)
        return True, "Empleado registrado exitosamente", saved
```

---

## 🔧 ADAPTADORES (IMPLEMENTACIONES)

### SqlAlchemyUserRepository

**Ubicación:** `app/adapters/sql_user_repository.py`

```python
from ..services.ports import UserRepositoryPort
from ..models import User, db

class SqlAlchemyUserRepository(UserRepositoryPort):
    """
    Adaptador SQLAlchemy para persistencia de usuarios.
    Implementa UserRepositoryPort usando SQLAlchemy + SQLite.
    """
    
    def add(self, user: User) -> User:
        """
        Guarda un usuario en la base de datos.
        
        Implementation Details:
            - Usa SQLAlchemy session
            - Maneja transacciones automáticamente
            - Asigna ID automáticamente (autoincrement)
        
        Raises:
            IntegrityError: Si hay violación de constraint (ej: username duplicado)
        """
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)  # Actualiza con ID generado
        return user
    
    def get_by_username(self, username: str) -> User | None:
        """
        Busca usuario por username usando SQLAlchemy query.
        
        Implementation Details:
            - Usa filter_by para igualdad exacta
            - Retorna None si no encuentra
            - Case-sensitive por defecto
        """
        return User.query.filter_by(username=username).first()
```

---

### SqlAlchemyPatientRepository

**Ubicación:** `app/adapters/sql_patient_repository.py`

```python
class SqlAlchemyPatientRepository(PatientRepositoryPort):
    """Adaptador para pacientes"""
    
    def add(self, patient: Patient) -> Patient:
        db.session.add(patient)
        db.session.commit()
        db.session.refresh(patient)
        return patient
    
    def update(self, patient: Patient) -> Patient:
        """
        Actualiza un paciente existente.
        
        Implementation Details:
            - SQLAlchemy detecta cambios automáticamente (dirty tracking)
            - Solo requiere commit()
        """
        db.session.commit()
        return patient
    
    def delete(self, patient_id: int) -> None:
        """
        Elimina un paciente.
        
        Note: Considera implementar soft delete en producción
        para mantener historial.
        """
        patient = self.get(patient_id)
        if patient:
            db.session.delete(patient)
            db.session.commit()
    
    def get(self, patient_id: int) -> Patient | None:
        return Patient.query.get(patient_id)
    
    def get_by_document(self, document: str) -> Patient | None:
        return Patient.query.filter_by(documento=document).first()
    
    def list(self) -> List[Patient]:
        """
        Lista todos los pacientes.
        
        Implementation Details:
            - Ordena por fecha de creación (más recientes primero)
            - Retorna lista vacía si no hay pacientes
        """
        return Patient.query.order_by(Patient.id.desc()).all()
```

---

## 🗄️ INFRAESTRUCTURA

### AccessControl (RBAC)

**Ubicación:** `app/infrastructure/security/access_control.py`

```python
def require_role(role: str):
    """
    Decorador para control de acceso basado en roles (RBAC).
    ISO 27001: A.9.2.2 - User access management
    
    Usage:
        @require_role('admin')
        def admin_only_route():
            return "Solo admins"
    
    Args:
        role (str): Rol requerido ('admin', 'medico', 'usuario')
    
    Returns:
        function: Decorador que valida el rol antes de ejecutar la función
    
    Behavior:
        - Si no está autenticado: redirect a login
        - Si no tiene el rol: abort(403)
        - Si tiene el rol: ejecuta la función normalmente
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor inicia sesión')
                return redirect(url_for('auth.login'))
            
            if not current_user.has_role(role):
                flash(f'Acceso denegado. Requiere rol: {role}')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_any_role(*roles: str):
    """
    Decorador para acceso con múltiples roles permitidos.
    
    Usage:
        @require_any_role('admin', 'medico')
        def medical_staff_route():
            return "Admins y médicos"
    """
    # Similar implementation...
```

---

### AuditLogger

**Ubicación:** `app/infrastructure/audit/audit_log.py`

```python
class AuditLogger:
    """
    Logger de auditoría para eventos de seguridad.
    ISO 27001: A.12.4.1 - Event logging
    """
    
    def __init__(self):
        """
        Inicializa el logger de auditoría.
        
        Configuration:
            - Log level: INFO
            - Format: %(asctime)s - %(levelname)s - %(message)s
            - Output: logs/audit.log (rotación manual recomendada)
        """
        self.logger = self._setup_logger()
    
    def log_action(self, action: str, details: Dict[str, Any]) -> None:
        """
        Registra un evento de auditoría.
        
        Args:
            action (str): Tipo de acción (ej: 'USER_LOGIN', 'PATIENT_CREATED')
            details (dict): Detalles adicionales del evento
        
        Log Format:
            [timestamp] User:{user_id} IP:{ip_address} Action:{action} Details:{details}
        
        Example:
            logger.log_action('USER_LOGIN', {'username': 'admin', 'success': True})
            
            Output:
            [2025-10-30T15:21:11] User:1 IP:127.0.0.1 Action:USER_LOGIN 
            Details:{'username': 'admin', 'success': True}
        """
        user_id = getattr(current_user, 'id', 'anonymous')
        ip_address = request.remote_addr
        timestamp = datetime.now().isoformat()
        
        self.logger.info(
            f"[{timestamp}] User:{user_id} IP:{ip_address} "
            f"Action:{action} Details:{details}"
        )
```

---

### RateLimiter

**Ubicación:** `app/infrastructure/security/rate_limiter.py`

```python
class RateLimiter:
    """
    Limitador de intentos de login para prevenir fuerza bruta.
    ISO 27001: A.9.4.3 - Password management system
    """
    
    MAX_ATTEMPTS = 3
    LOCKOUT_TIME = 900  # 15 minutos en segundos
    
    @staticmethod
    def increment_failed_attempts(user: User) -> None:
        """
        Incrementa el contador de intentos fallidos.
        
        Args:
            user (User): Usuario que falló el login
        
        Behavior:
            - Incrementa failed_login_attempts
            - Si alcanza MAX_ATTEMPTS: establece locked_until
        """
        user.failed_login_attempts += 1
        
        if user.failed_login_attempts >= RateLimiter.MAX_ATTEMPTS:
            user.locked_until = datetime.now() + timedelta(
                seconds=RateLimiter.LOCKOUT_TIME
            )
        
        db.session.commit()
    
    @staticmethod
    def reset_failed_attempts(user: User) -> None:
        """Resetea el contador tras login exitoso"""
        user.failed_login_attempts = 0
        user.locked_until = None
        db.session.commit()
    
    @staticmethod
    def is_locked(user: User) -> bool:
        """
        Verifica si la cuenta está bloqueada.
        
        Returns:
            bool: True si está bloqueada y el tiempo no ha expirado
        """
        if user.locked_until is None:
            return False
        
        if datetime.now() < user.locked_until:
            return True
        
        # Tiempo expirado, desbloquear automáticamente
        RateLimiter.reset_failed_attempts(user)
        return False
```

---

## 🌐 ENDPOINTS (RUTAS)

### Auth Module

**Ubicación:** `app/auth/routes.py`

```python
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Endpoint: Registro de nuevos usuarios
    ISO 27001: A.9.2.1 - User registration
    
    Method: GET, POST
    URL: /auth/register
    
    Form Data (POST):
        - username (str, required): Nombre de usuario único
        - password (str, required): Contraseña (min 8 chars)
        - password2 (str, required): Confirmación de contraseña
        - role (str, optional): Rol del usuario (default: 'usuario')
    
    Returns:
        - GET: Formulario de registro (register.html)
        - POST (success): Redirect a /auth/login
        - POST (error): Re-render formulario con mensaje de error
    
    Security:
        - CSRF protection enabled (WTForms)
        - Password hasheado con pbkdf2:sha256
        - Validación de unicidad de username
    """
    # Implementation...


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Endpoint: Inicio de sesión
    ISO 27001: A.9.4.2 - Secure logon procedures
    
    Method: GET, POST
    URL: /auth/login
    
    Form Data (POST):
        - username (str, required)
        - password (str, required)
        - remember (bool, optional): Mantener sesión activa
    
    Returns:
        - GET: Formulario de login (login.html)
        - POST (success): Redirect a dashboard
        - POST (locked): Error de cuenta bloqueada
        - POST (invalid): Error de credenciales inválidas
    
    Security:
        - Rate limiting (3 intentos, 15 min lockout)
        - Audit logging de intentos
        - Session management con Flask-Login
    """
    # Implementation...
```

---

### Patients Module

```python
@patients_bp.route('/')
@login_required
def list_patients():
    """
    Endpoint: Lista de pacientes
    
    Method: GET
    URL: /patients/
    
    Auth: Login requerido
    
    Returns:
        - HTML: Lista de pacientes (patients/list.html)
    
    Security:
        - @login_required: Solo usuarios autenticados
    """
    # Implementation...


@patients_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_patient():
    """
    Endpoint: Crear nuevo paciente
    ISO 27001: A.18.1.3 - Protection of personal data
    
    Method: GET, POST
    URL: /patients/create
    
    Auth: Login requerido
    
    Form Data (POST):
        - nombre (str, required)
        - documento (str, required, unique)
        - fecha_nacimiento (date, required)
        - direccion (str, optional)
        - telefono (str, optional)
    
    Returns:
        - GET: Formulario (patients/create.html)
        - POST (success): Redirect a /patients/
        - POST (error): Re-render con errores
    
    Security:
        - CSRF protection
        - Input validation
        - Audit log: PATIENT_CREATED
    """
    # Implementation...
```

---

### Admin Module

```python
@admin_bp.route('/users')
@require_role('admin')
def list_users():
    """
    Endpoint: Gestión de usuarios (solo admins)
    ISO 27001: A.9.2.2 - User access management
    
    Method: GET
    URL: /admin/users
    
    Auth: Requiere rol 'admin'
    
    Returns:
        - HTML: Lista de usuarios con opciones de gestión
    
    Security:
        - @require_role('admin'): Control de acceso RBAC
        - Audit log: ADMIN_USERS_VIEWED
    """
    # Implementation...
```

---

## 🔄 FLUJO DE DATOS COMPLETO

### Ejemplo: Crear Paciente

```
1. HTTP POST /patients/create
   └─ Form Data: {nombre, documento, fecha_nacimiento}

2. patients/routes.py::create_patient()
   ├─ Validar CSRF token (WTForms)
   ├─ Validar autenticación (@login_required)
   └─ Instanciar servicio y adaptador:
       patient_repo = SqlAlchemyPatientRepository()
       patient_service = PatientService(patient_repo)

3. PatientService.create_patient()
   ├─ Validar reglas de negocio:
   │  ├─ Documento único?
   │  ├─ Fecha válida?
   │  └─ Nombre no vacío?
   ├─ Crear entidad: Patient(...)
   └─ Llamar al puerto: patient_repo.add(patient)

4. SqlAlchemyPatientRepository.add()
   ├─ db.session.add(patient)
   ├─ db.session.commit()
   └─ Retorna patient con ID asignado

5. SQLite Database
   └─ INSERT INTO patients (...) VALUES (...)

6. Audit Logger (paralelo)
   └─ Log: [timestamp] User:1 Action:PATIENT_CREATED Details:{id:5}

7. HTTP Response
   ├─ Flash message: "Paciente registrado"
   └─ Redirect: /patients/
```

---

## 📊 MATRIZ DE COMPONENTES

| Componente | Tipo | Responsabilidad | Dependencias |
|------------|------|----------------|--------------|
| `User` | Modelo | Entidad de dominio | None (puro) |
| `UserRepositoryPort` | Puerto | Abstracción de persistencia | `User` |
| `SqlAlchemyUserRepository` | Adaptador | Persistencia SQLAlchemy | `UserRepositoryPort`, `db` |
| `UserService` | Servicio | Casos de uso de usuarios | `UserRepositoryPort` |
| `auth/routes.py` | Controlador | Endpoints HTTP | `UserService`, Flask |
| `AccessControl` | Infraestructura | RBAC decorators | Flask-Login |
| `AuditLogger` | Infraestructura | Logging de eventos | stdlib logging |

---

## 🧪 TESTING DE COMPONENTES

### Test de Puerto

```python
def test_user_repository_port_is_abstract():
    from app.services.ports import UserRepositoryPort
    from abc import ABC
    
    assert issubclass(UserRepositoryPort, ABC)
    
    # No se puede instanciar directamente
    with pytest.raises(TypeError):
        UserRepositoryPort()
```

### Test de Servicio (con Mock)

```python
def test_register_user_with_mock_repository():
    # Crear repositorio fake
    class FakeUserRepository(UserRepositoryPort):
        def __init__(self):
            self.users = []
        
        def add(self, user):
            self.users.append(user)
            return user
        
        def get_by_username(self, username):
            return next((u for u in self.users if u.username == username), None)
    
    # Test del servicio
    fake_repo = FakeUserRepository()
    service = UserService(fake_repo)
    
    success, msg = service.register_user('test', 'password123', 'usuario')
    
    assert success == True
    assert len(fake_repo.users) == 1
```

---

## 📖 REFERENCIAS

- **Arquitectura Hexagonal:** Alistair Cockburn - "Hexagonal Architecture"
- **SOLID Principles:** Robert C. Martin - "Clean Architecture"
- **ISO 27001:2013:** Controles A.9, A.10, A.12, A.18
- **Domain-Driven Design:** Eric Evans
- **Flask Documentation:** https://flask.palletsprojects.com/

---

**Versión:** 1.0  
**Última Actualización:** Octubre 2025  
**Autor:** Jose Luis
