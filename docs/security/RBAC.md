# Role-Based Access Control (RBAC) - ISO 27001 Implementation

## Roles definidos

El sistema implementa los siguientes roles para cumplir con ISO 27001 A.9.1, A.9.2 y A.5.2:

### 1. **admin** (Administrador)
- Acceso completo al sistema
- Puede crear, editar y **eliminar** pacientes
- Puede gestionar citas y cancelarlas
- Acceso completo a historias clínicas
- Puede gestionar empleados (cuando se implemente)
- Puede gestionar usuarios y roles

### 2. **medico** (Médico)
- Puede ver pacientes
- Puede crear y cancelar citas
- **Acceso completo** a historias clínicas (lectura y escritura)
- NO puede eliminar pacientes

### 3. **enfermero** (Enfermería)
- Puede ver pacientes
- Puede ver citas
- Puede **leer** historias clínicas
- NO puede escribir en historias clínicas
- NO puede eliminar pacientes

### 4. **recepcionista** (Recepción)
- Puede crear, editar pacientes (NO eliminar)
- Puede crear y cancelar citas
- **NO tiene acceso** a historias clínicas
- Gestión administrativa básica

## Matriz de permisos

| Operación | admin | medico | enfermero | recepcionista |
|-----------|-------|---------|-----------|---------------|
| Ver pacientes | ✓ | ✓ | ✓ | ✓ |
| Crear pacientes | ✓ | ✗ | ✗ | ✓ |
| Editar pacientes | ✓ | ✗ | ✗ | ✓ |
| Eliminar pacientes | ✓ | ✗ | ✗ | ✗ |
| Ver citas | ✓ | ✓ | ✓ | ✓ |
| Crear citas | ✓ | ✓ | ✗ | ✓ |
| Cancelar citas | ✓ | ✓ | ✗ | ✓ |
| Ver historia clínica | ✓ | ✓ | ✓ | ✗ |
| Escribir historia clínica | ✓ | ✓ | ✗ | ✗ |

## Implementación técnica

### Decoradores disponibles

```python
from app.infrastructure.security.access_control import require_role, require_any_role

# Requiere un rol específico
@require_role('admin')
def admin_only_route():
    pass

# Requiere cualquiera de los roles especificados
@require_any_role('admin', 'medico')
def medical_staff_route():
    pass
```

### Métodos del modelo User

```python
user.has_role('admin')  # Verifica si tiene un rol específico
user.has_any_role('admin', 'medico')  # Verifica si tiene alguno de los roles
```

## Separación de funciones (Segregation of Duties)

Cumplimiento de ISO 27001 A.9.2:

1. **Principio de mínimo privilegio**: Cada rol solo tiene los permisos necesarios para sus funciones
2. **Separación clínica-administrativa**: 
   - Recepción NO accede a historias clínicas
   - Personal médico NO puede eliminar registros administrativos
3. **Trazabilidad**: Todas las acciones sensibles se auditan con el rol del usuario

## Migraciones

Para aplicar el campo `role` a usuarios existentes:

```python
# En una migración o script de actualización
from app.models import db, User

# Asignar rol por defecto a usuarios existentes
users_without_role = User.query.filter_by(role=None).all()
for user in users_without_role:
    user.role = 'recepcionista'  # o el rol apropiado
db.session.commit()
```

## Testing

Los tests utilizan un usuario con rol `admin` por defecto para no afectar la cobertura existente:

```python
@pytest.fixture
def test_user(app):
    user = User(username='testuser', role='admin')
    user.set_password('testpass')
    # ...
```

Para probar restricciones de roles específicos:

```python
def test_non_admin_cannot_delete_patient(client):
    # Crear usuario con rol limitado
    user = User(username='receptionist', role='recepcionista')
    user.set_password('pass')
    db.session.add(user)
    db.session.commit()
    
    # Intentar acceso denegado
    response = client.post('/patients/1/delete')
    assert response.status_code == 403
```

## Próximos pasos

1. Añadir interfaz de gestión de usuarios y roles (solo admin)
2. Implementar campo de rol en formulario de registro (con validación)
3. Añadir vista de auditoría filtrada por rol
4. Considerar roles más granulares si es necesario (ej: `admin_clinico`, `admin_sistemas`)
