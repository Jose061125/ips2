# 🚀 SPRINT 2: PRUEBAS Y OPTIMIZACIÓN

**Sistema de Gestión IPS - Performance, Seguridad y Usabilidad**

---

## 📋 OBJETIVO DEL SPRINT

Ejecutar pruebas exhaustivas de **rendimiento, seguridad y usabilidad**, implementando optimizaciones basadas en retroalimentación del equipo y métricas objetivas.

---

## 🎯 OBJETIVOS ESPECÍFICOS

| Área | Objetivo | Métrica Objetivo | Estado |
|------|----------|------------------|--------|
| **Rendimiento** | Optimizar tiempos de respuesta | < 200ms en endpoints CRUD | 🔄 |
| **Seguridad** | Validar OWASP Top 10 | 10/10 controles | 🔄 |
| **Usabilidad** | Mejorar experiencia de usuario | Accessibility score > 90 | 🔄 |
| **Código** | Incrementar calidad | Pylint > 8.5/10 | 🔄 |
| **Cobertura** | Aumentar tests | > 80% coverage | 🔄 |

---

## 📊 MÉTRICAS BASELINE (Sprint 1)

| Métrica | Valor Actual | Objetivo Sprint 2 |
|---------|--------------|-------------------|
| Tests totales | 52/52 (100%) | 80+ tests |
| Cobertura de código | 66% | 80%+ |
| Pylint score | 6.93/10 | 8.5/10 |
| Vulnerabilidades | 0 | 0 |
| Response time | No medido | < 200ms |
| Load capacity | No medido | 100 usuarios concurrentes |
| Accessibility | No medido | 90+ Lighthouse |

---

## 🔬 1. PRUEBAS DE RENDIMIENTO

### 1.1 Tests de Performance

**Archivo:** `tests/test_performance.py`

#### Queries de Base de Datos
```python
def test_patient_query_performance(benchmark):
    """Query de pacientes debe ser < 50ms"""
    result = benchmark(lambda: Patient.query.all())
    assert benchmark.stats.stats.mean < 0.05  # 50ms

def test_appointment_query_with_joins(benchmark):
    """Query con JOINs debe ser < 100ms"""
    # Test con eager loading optimizado
```

#### Endpoints HTTP
```python
def test_endpoint_login_performance(benchmark, client):
    """Login debe responder en < 200ms"""
    def do_login():
        return client.post('/auth/login', data={...})
    
    result = benchmark(do_login)
    assert benchmark.stats.stats.mean < 0.2
```

#### Operaciones Bulk
```python
def test_bulk_patient_creation(benchmark):
    """Crear 100 pacientes debe ser < 5s"""
    patients = [Patient(...) for _ in range(100)]
    result = benchmark(lambda: db.session.bulk_save_objects(patients))
```

---

### 1.2 Load Testing

**Archivo:** `tests/locustfile.py`

```python
from locust import HttpUser, task, between

class IPSUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_patients(self):
        """Simula consulta de pacientes"""
        self.client.get("/patients/")
    
    @task(2)
    def create_appointment(self):
        """Simula creación de cita"""
        self.client.post("/appointments/create", {...})
    
    @task(1)
    def login(self):
        """Simula login"""
        self.client.post("/auth/login", {...})
```

**Comando:**
```bash
locust -f tests/locustfile.py --host=http://localhost:5000 --users=100 --spawn-rate=10
```

**Métricas a capturar:**
- Requests per second (RPS)
- Response time (p50, p95, p99)
- Error rate
- CPU/Memory usage

---

### 1.3 Profiling de Código

**Herramientas:**
- `py-spy` - CPU profiler
- `memory_profiler` - Memory profiler
- `Flask-Profiler` - Request profiler

**Scripts:**

```bash
# CPU profiling
py-spy record -o profile.svg -- python run.py

# Memory profiling
python -m memory_profiler scripts/profile_memory.py

# Flask request profiling (integrado)
# Endpoint: /_profiler
```

---

## 🔒 2. PRUEBAS DE SEGURIDAD AVANZADAS

### 2.1 OWASP Top 10 Tests

**Archivo:** `tests/test_security_owasp.py`

#### A1 - Injection

```python
def test_sql_injection_prevention(client):
    """Prevención de SQL Injection"""
    # Test con payload malicioso
    response = client.post('/auth/login', data={
        'username': "admin' OR '1'='1",
        'password': "anything"
    })
    assert response.status_code != 200
    # Verificar que no se bypassea autenticación

def test_nosql_injection_prevention(client):
    """Prevención de NoSQL Injection (si aplica)"""
    # Test con payload NoSQL
```

#### A2 - Broken Authentication

```python
def test_session_fixation_prevention(client):
    """Prevención de Session Fixation"""
    # Obtener session ID antes de login
    response1 = client.get('/')
    session_before = client.get_cookie('session')
    
    # Login
    client.post('/auth/login', data={...})
    
    # Session ID debe cambiar
    session_after = client.get_cookie('session')
    assert session_before != session_after

def test_concurrent_session_handling(client):
    """Manejo de sesiones concurrentes"""
    # Verificar política de sesiones
```

#### A3 - Sensitive Data Exposure

```python
def test_password_storage_hashing(app):
    """Contraseñas deben estar hasheadas"""
    user = User(username='test')
    user.set_password('plaintext')
    
    assert user.password_hash != 'plaintext'
    assert user.password_hash.startswith('pbkdf2:sha256:')

def test_sensitive_data_in_logs(app, caplog):
    """Logs no deben contener datos sensibles"""
    # Ejecutar operación
    # Verificar que logs no contengan passwords, tokens, etc.
```

#### A4 - XML External Entities (XXE)

```python
def test_xxe_prevention(client):
    """Prevención de XXE attacks"""
    # Si la app procesa XML, validar sanitización
```

#### A5 - Broken Access Control

```python
def test_idor_prevention(client, auth):
    """Prevención de IDOR (Insecure Direct Object References)"""
    # Usuario A crea recurso
    auth.login(username='userA', password='pass')
    response = client.post('/patients/create', data={...})
    patient_id = extract_id(response)
    
    # Usuario B intenta acceder
    auth.logout()
    auth.login(username='userB', password='pass')
    response = client.get(f'/patients/{patient_id}')
    
    # Debe estar bloqueado si no tiene permisos
    assert response.status_code == 403

def test_forced_browsing_prevention(client):
    """Prevención de Forced Browsing"""
    # Sin autenticación
    response = client.get('/admin/users')
    assert response.status_code in [302, 401, 403]
```

#### A6 - Security Misconfiguration

```python
def test_debug_mode_disabled_production(app):
    """Debug mode debe estar OFF en producción"""
    assert app.config.get('DEBUG') == False

def test_error_pages_dont_leak_info(client):
    """Páginas de error no deben exponer stack traces"""
    response = client.get('/nonexistent')
    assert b'Traceback' not in response.data
    assert b'File "' not in response.data
```

#### A7 - Cross-Site Scripting (XSS)

```python
def test_xss_prevention_in_templates(client):
    """Prevención de XSS en templates"""
    # Crear paciente con payload XSS
    malicious_name = "<script>alert('XSS')</script>"
    client.post('/patients/create', data={
        'nombre': malicious_name,
        ...
    })
    
    # Verificar que se escape en el HTML
    response = client.get('/patients/')
    assert b'<script>' not in response.data
    assert b'&lt;script&gt;' in response.data or malicious_name.encode() not in response.data

def test_xss_prevention_in_json_responses(client):
    """Prevención de XSS en respuestas JSON"""
    # Test con API endpoints si existen
```

#### A8 - Insecure Deserialization

```python
def test_secure_session_handling(client):
    """Sessions deben ser seguras"""
    # Verificar que sessions no sean manipulables
```

#### A9 - Using Components with Known Vulnerabilities

```python
def test_dependencies_security_check():
    """Dependencies deben estar actualizadas y sin CVEs"""
    # Ejecutar: safety check
    # Este test se ejecuta en CI/CD
```

#### A10 - Insufficient Logging & Monitoring

```python
def test_security_events_are_logged(client, app):
    """Eventos de seguridad deben ser auditados"""
    # Intento de login fallido
    client.post('/auth/login', data={
        'username': 'nonexistent',
        'password': 'wrong'
    })
    
    # Verificar que se loguea en audit.log
    with open('logs/audit.log') as f:
        logs = f.read()
        assert 'login_failure' in logs
```

---

### 2.2 Security Headers

**Archivo:** `tests/test_security_headers.py`

```python
def test_security_headers_present(client):
    """Headers de seguridad deben estar configurados"""
    response = client.get('/')
    
    # Verificar headers críticos
    assert 'X-Content-Type-Options' in response.headers
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    
    assert 'X-Frame-Options' in response.headers
    assert response.headers['X-Frame-Options'] in ['DENY', 'SAMEORIGIN']
    
    assert 'X-XSS-Protection' in response.headers
    
    # Content Security Policy (recomendado)
    assert 'Content-Security-Policy' in response.headers

def test_https_only_cookies(app):
    """Cookies deben ser Secure en producción"""
    assert app.config['SESSION_COOKIE_SECURE'] == True  # Producción
    assert app.config['SESSION_COOKIE_HTTPONLY'] == True
```

---

### 2.3 Penetration Testing Checklist

**Manual Testing:**

- [ ] Intentar bypass de autenticación
- [ ] Intentar escalación de privilegios
- [ ] Intentar acceso a recursos de otros usuarios
- [ ] Intentar inyección en todos los formularios
- [ ] Intentar CSRF en operaciones críticas
- [ ] Intentar fuerza bruta en login
- [ ] Verificar timeout de sesión
- [ ] Verificar logout completo (borrado de sesión)

---

## 👥 3. PRUEBAS DE USABILIDAD

### 3.1 Tests de Formularios

**Archivo:** `tests/test_usability.py`

```python
def test_form_validation_messages_are_clear(client):
    """Mensajes de validación deben ser claros y útiles"""
    response = client.post('/auth/register', data={
        'username': 'a',  # Muy corto
        'password': '123'  # Muy corto
    })
    
    # Verificar mensajes específicos
    assert b'usuario debe tener al menos' in response.data.lower()
    assert b'8 caracteres' in response.data

def test_error_handling_is_user_friendly(client):
    """Errores deben ser comprensibles para usuarios"""
    response = client.get('/patients/99999')  # No existe
    
    # No debe mostrar stack trace
    assert b'Traceback' not in response.data
    # Debe mostrar mensaje amigable
    assert b'no encontrado' in response.data.lower() or b'not found' in response.data.lower()
```

---

### 3.2 Tests de Navegación

```python
def test_navigation_consistency(client, auth):
    """Navegación debe ser consistente en todas las páginas"""
    auth.login()
    
    pages = [
        '/',
        '/patients/',
        '/employees/',
        '/appointments/'
    ]
    
    for page in pages:
        response = client.get(page)
        # Verificar que navbar esté presente
        assert b'navbar' in response.data or b'nav' in response.data
        # Verificar enlaces comunes
        assert b'Pacientes' in response.data
        assert b'Empleados' in response.data

def test_breadcrumbs_present(client, auth):
    """Breadcrumbs para orientación del usuario"""
    auth.login()
    response = client.get('/patients/create')
    
    # Debe mostrar ruta: Inicio > Pacientes > Crear
    assert b'Inicio' in response.data or b'Home' in response.data
```

---

### 3.3 Tests de Accesibilidad (WCAG)

```python
def test_forms_have_labels(client):
    """Todos los inputs deben tener labels"""
    response = client.get('/auth/login')
    html = response.data.decode()
    
    # Parsear HTML y verificar labels
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    inputs = soup.find_all('input', type=['text', 'password', 'email'])
    for input_tag in inputs:
        input_id = input_tag.get('id')
        assert input_id, "Input debe tener ID"
        
        label = soup.find('label', attrs={'for': input_id})
        assert label, f"Input {input_id} debe tener label asociado"

def test_images_have_alt_text(client):
    """Imágenes deben tener texto alternativo"""
    response = client.get('/')
    html = response.data.decode()
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    images = soup.find_all('img')
    for img in images:
        assert img.get('alt'), "Imagen debe tener atributo alt"

def test_color_contrast_sufficient():
    """Contraste de colores debe cumplir WCAG AA"""
    # Test manual o con herramienta automatizada
    # Ratio mínimo: 4.5:1 para texto normal
    # Ratio mínimo: 3:1 para texto grande
```

---

### 3.4 Tests E2E con Selenium

**Archivo:** `tests/test_e2e_user_flows.py`

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_complete_patient_registration_flow():
    """Flujo completo: Registrar usuario > Login > Crear paciente"""
    driver = webdriver.Chrome()
    try:
        # 1. Ir a registro
        driver.get('http://localhost:5000/auth/register')
        
        # 2. Llenar formulario
        driver.find_element(By.ID, 'username').send_keys('testuser')
        driver.find_element(By.ID, 'password').send_keys('password123')
        driver.find_element(By.ID, 'password2').send_keys('password123')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # 3. Verificar redirect a login
        WebDriverWait(driver, 5).until(
            EC.url_contains('/auth/login')
        )
        
        # 4. Login
        driver.find_element(By.ID, 'username').send_keys('testuser')
        driver.find_element(By.ID, 'password').send_keys('password123')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # 5. Crear paciente
        driver.get('http://localhost:5000/patients/create')
        driver.find_element(By.ID, 'nombre').send_keys('Juan Pérez')
        # ... llenar formulario
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # 6. Verificar éxito
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
        
    finally:
        driver.quit()
```

---

## 🔧 4. OPTIMIZACIONES

### 4.1 Optimización de Queries

**Problema identificado:** Queries N+1

```python
# ANTES (N+1 queries)
patients = Patient.query.all()
for patient in patients:
    print(patient.appointments)  # Query adicional por paciente

# DESPUÉS (1 query con JOIN)
patients = Patient.query.options(
    db.joinedload(Patient.appointments)
).all()
```

**Implementación:**

```python
# app/adapters/sql_patient_repository.py
def list_with_appointments(self) -> List[Patient]:
    """Lista pacientes con appointments precargadas"""
    return Patient.query.options(
        db.joinedload(Patient.appointments)
    ).order_by(Patient.id.desc()).all()
```

---

### 4.2 Índices de Base de Datos

**Archivo:** `scripts/create_indexes.py`

```python
from app import create_app, db

app = create_app()

with app.app_context():
    # Índices estratégicos
    db.session.execute('CREATE INDEX IF NOT EXISTS idx_user_username ON user(username)')
    db.session.execute('CREATE INDEX IF NOT EXISTS idx_patient_documento ON patients(documento)')
    db.session.execute('CREATE INDEX IF NOT EXISTS idx_appointment_patient ON appointments(patient_id)')
    db.session.execute('CREATE INDEX IF NOT EXISTS idx_appointment_date ON appointments(scheduled_at)')
    
    db.session.commit()
    print("✅ Índices creados exitosamente")
```

---

### 4.3 Caching

**Instalación:**
```bash
pip install Flask-Caching
```

**Configuración:**

```python
# app/__init__.py
from flask_caching import Cache

cache = Cache()

def create_app(config_overrides=None):
    app = Flask(__name__)
    
    # Configurar cache
    app.config['CACHE_TYPE'] = 'simple'  # O 'redis' en producción
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    
    cache.init_app(app)
    
    return app
```

**Uso:**

```python
# app/patients/routes.py
from app import cache

@patients_bp.route('/')
@login_required
@cache.cached(timeout=60, key_prefix='patients_list')
def list_patients():
    """Lista cacheada por 60 segundos"""
    patients = patient_service.list_all_patients()
    return render_template('patients/list.html', patients=patients)
```

---

### 4.4 Refactorización Pylint

**Issues actuales (6.93/10):**

```bash
# Ver issues detallados
pylint app/ --rcfile=.pylintrc > pylint_report.txt
```

**Correcciones comunes:**

1. **Docstrings faltantes**
```python
# ANTES
def get_by_document(self, document: str):
    return Patient.query.filter_by(documento=document).first()

# DESPUÉS
def get_by_document(self, document: str) -> Patient | None:
    """
    Busca un paciente por su documento de identidad.
    
    Args:
        document: Número de documento único
    
    Returns:
        Paciente encontrado o None
    """
    return Patient.query.filter_by(documento=document).first()
```

2. **Nombres de variables**
```python
# ANTES
def func(p, a, r):
    ...

# DESPUÉS
def create_appointment(patient, appointment_time, reason):
    ...
```

3. **Líneas demasiado largas (> 100 caracteres)**
```python
# ANTES
patient = Patient(nombre=form.nombre.data, documento=form.documento.data, fecha_nacimiento=form.fecha_nacimiento.data, direccion=form.direccion.data)

# DESPUÉS
patient = Patient(
    nombre=form.nombre.data,
    documento=form.documento.data,
    fecha_nacimiento=form.fecha_nacimiento.data,
    direccion=form.direccion.data
)
```

---

### 4.5 Optimización de Templates

**Minificación CSS/JS:**

```python
# config.py
ASSETS_AUTO_BUILD = True
ASSETS_DEBUG = False  # En producción
```

**Lazy loading de imágenes:**

```html
<!-- ANTES -->
<img src="/static/img/logo.png" alt="Logo">

<!-- DESPUÉS -->
<img src="/static/img/logo.png" alt="Logo" loading="lazy">
```

---

## 📦 5. HERRAMIENTAS Y SETUP

### 5.1 Dependencias Adicionales

```bash
# requirements-dev.txt
pytest-benchmark==4.0.0
locust==2.31.0
py-spy==0.3.14
memory-profiler==0.61.0
Flask-Caching==2.3.0
safety==3.2.0
selenium==4.25.0
beautifulsoup4==4.12.3
```

**Instalación:**
```bash
pip install -r requirements-dev.txt
```

---

### 5.2 Configuración de Pytest

**pytest.ini:**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=html
    --cov-report=term-missing
markers =
    performance: Performance tests (deselect with '-m "not performance"')
    security: Security tests
    usability: Usability tests
    e2e: End-to-end tests (require browser)
    slow: Slow tests (> 1s)
```

---

### 5.3 Scripts de Ejecución

**scripts/run_performance_tests.sh:**

```bash
#!/bin/bash
echo "🚀 Ejecutando tests de rendimiento..."
pytest tests/test_performance.py -v --benchmark-only

echo ""
echo "📊 Profiling de memoria..."
python -m memory_profiler scripts/profile_memory.py

echo ""
echo "🔥 Load testing con Locust..."
echo "Ejecutar manualmente: locust -f tests/locustfile.py"
```

**scripts/run_security_tests.sh:**

```bash
#!/bin/bash
echo "🔒 Ejecutando tests de seguridad OWASP..."
pytest tests/test_security_owasp.py -v

echo ""
echo "🔍 Escaneando dependencias..."
safety check --json

echo ""
echo "🛡️ Análisis estático de seguridad..."
bandit -r app/ -f json -o bandit_report.json
```

---

## 📈 6. MÉTRICAS Y REPORTES

### 6.1 Dashboard de Métricas

**Archivo:** `scripts/generate_dashboard.py`

```python
import json
from datetime import datetime

metrics = {
    "sprint": 2,
    "fecha": datetime.now().isoformat(),
    "rendimiento": {
        "response_time_avg": "TBD ms",
        "queries_avg": "TBD ms",
        "load_capacity": "TBD usuarios"
    },
    "seguridad": {
        "owasp_score": "TBD/10",
        "vulnerabilidades": 0,
        "headers_security": "TBD/10"
    },
    "usabilidad": {
        "lighthouse_score": "TBD/100",
        "accessibility_score": "TBD/100",
        "form_errors_clarity": "TBD/10"
    },
    "calidad": {
        "pylint_score": "TBD/10",
        "test_coverage": "TBD%",
        "tests_passing": "TBD/TBD"
    }
}

with open('docs/SPRINT2_METRICS.json', 'w') as f:
    json.dump(metrics, f, indent=2)
```

---

## ✅ CHECKLIST DE VALIDACIÓN

### Pre-Sprint
- [ ] Todas las dependencias instaladas
- [ ] Configuración de pytest correcta
- [ ] Baseline de métricas documentada

### Durante Sprint
- [ ] Tests de rendimiento implementados
- [ ] Tests de seguridad OWASP completos
- [ ] Tests de usabilidad ejecutados
- [ ] Optimizaciones aplicadas
- [ ] Revisión de código en progreso

### Post-Sprint
- [ ] Todos los tests pasando
- [ ] Métricas objetivo alcanzadas
- [ ] Documentación actualizada
- [ ] Reporte de resultados generado
- [ ] Feedback del equipo incorporado
- [ ] Código subido a GitHub

---

## 🎯 CRITERIOS DE ÉXITO

| Criterio | Baseline | Objetivo | Peso |
|----------|----------|----------|------|
| Response time < 200ms | N/A | ✅ | 20% |
| OWASP Top 10 compliance | Parcial | 10/10 | 25% |
| Pylint score | 6.93 | > 8.5 | 15% |
| Test coverage | 66% | > 80% | 15% |
| Lighthouse accessibility | N/A | > 90 | 10% |
| Load capacity | N/A | 100 usuarios | 15% |

**Puntuación mínima para aprobar Sprint 2:** 80%

---

## 📅 CRONOGRAMA SUGERIDO

| Día | Actividad | Entregables |
|-----|-----------|-------------|
| 1-2 | Setup + Tests de rendimiento | test_performance.py, locustfile.py |
| 3-4 | Tests de seguridad OWASP | test_security_owasp.py |
| 5 | Tests de usabilidad | test_usability.py, test_e2e.py |
| 6-7 | Optimizaciones de código | Refactoring, caching, indexes |
| 8 | Ejecución completa + Reporte | SPRINT2_RESULTADOS.md |

---

## 🚀 PRÓXIMOS PASOS

1. Instalar dependencias de desarrollo
2. Configurar pytest con markers
3. Implementar tests de performance
4. Ejecutar baseline y documentar
5. Iterar con optimizaciones

---

**Versión:** 1.0  
**Última Actualización:** Octubre 2025  
**Responsable:** Jose Luis  
**Estado:** 🔄 En Progreso
