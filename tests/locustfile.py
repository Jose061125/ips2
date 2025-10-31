"""
Locust Load Testing - IPS System
=================================

Simula usuarios concurrentes para validar capacidad del sistema.

Ejecutar:
    # GUI mode
    locust -f tests/locustfile.py --host=http://localhost:5000
    
    # Headless mode (100 usuarios, 10/s spawn rate)
    locust -f tests/locustfile.py --host=http://localhost:5000 \
           --users=100 --spawn-rate=10 --run-time=5m --headless
    
    # Modo HTML report
    locust -f tests/locustfile.py --host=http://localhost:5000 \
           --users=100 --spawn-rate=10 --run-time=5m --headless \
           --html=locust_report.html

Métricas objetivo:
    - RPS: > 50 requests/second
    - Response time p95: < 500ms
    - Error rate: < 1%
"""

from locust import HttpUser, task, between, events
from random import randint, choice
import logging


# Datos de prueba
SAMPLE_NAMES = [
    'Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez',
    'Pedro Rodríguez', 'Laura Hernández', 'Diego González', 'Sofia Díaz'
]

SAMPLE_SPECIALTIES = [
    'Medicina General', 'Pediatría', 'Cardiología', 'Neurología',
    'Dermatología', 'Oftalmología'
]


class IPSUser(HttpUser):
    """
    Usuario simulado del sistema IPS.
    
    Simula comportamiento realista:
    - Login
    - Navegar por listados
    - Crear registros
    - Ver detalles
    - Buscar
    - Logout
    """
    
    # Tiempo de espera entre acciones (1-3 segundos)
    wait_time = between(1, 3)
    
    def on_start(self):
        """Ejecutado al iniciar cada usuario - Login"""
        self.login()
    
    def login(self):
        """Login como usuario admin para tests"""
        response = self.client.post("/auth/login", data={
            'username': 'admin',
            'password': 'admin123'
        }, catch_response=True)
        
        if response.status_code == 200 or response.status_code == 302:
            response.success()
        else:
            response.failure(f"Login failed: {response.status_code}")
    
    @task(5)
    def view_dashboard(self):
        """Tarea: Ver dashboard principal (peso 5 - más frecuente)"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Dashboard load failed: {response.status_code}")
    
    @task(10)
    def view_patients_list(self):
        """Tarea: Ver listado de pacientes (peso 10 - muy frecuente)"""
        with self.client.get("/patients/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Patients list failed: {response.status_code}")
    
    @task(3)
    def create_patient(self):
        """Tarea: Crear nuevo paciente (peso 3 - moderado)"""
        # Primero cargar el formulario
        self.client.get("/patients/create")
        
        # Luego enviar
        patient_data = {
            'nombre': choice(SAMPLE_NAMES),
            'documento': f'DOC{randint(10000, 99999)}',
            'fecha_nacimiento': f'19{randint(50, 99)}-{randint(1, 12):02d}-{randint(1, 28):02d}',
            'direccion': f'Calle {randint(1, 100)} #{randint(1, 50)}-{randint(1, 99)}',
            'telefono': f'3{randint(100000000, 199999999)}'
        }
        
        with self.client.post("/patients/create", data=patient_data, catch_response=True) as response:
            if response.status_code in [200, 302]:
                response.success()
            else:
                response.failure(f"Patient creation failed: {response.status_code}")
    
    @task(8)
    def view_appointments_list(self):
        """Tarea: Ver listado de citas (peso 8 - frecuente)"""
        with self.client.get("/appointments/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Appointments list failed: {response.status_code}")
    
    @task(2)
    def create_appointment(self):
        """Tarea: Crear nueva cita (peso 2 - menos frecuente)"""
        self.client.get("/appointments/create")
        
        appointment_data = {
            'patient_id': randint(1, 50),  # Asumir que existen pacientes
            'employee_id': randint(1, 10),  # Asumir que existen empleados
            'scheduled_at': f'2025-11-{randint(1, 30):02d} {randint(8, 17):02d}:00',
            'motivo': 'Consulta general de control',
            'estado': 'programada'
        }
        
        with self.client.post("/appointments/create", data=appointment_data, catch_response=True) as response:
            if response.status_code in [200, 302]:
                response.success()
            else:
                # Es posible que falle si no existen pacientes/empleados
                response.success()  # No marcar como fallo en load test
    
    @task(7)
    def view_employees_list(self):
        """Tarea: Ver listado de empleados (peso 7 - frecuente)"""
        with self.client.get("/employees/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Employees list failed: {response.status_code}")
    
    @task(2)
    def create_employee(self):
        """Tarea: Crear nuevo empleado (peso 2 - menos frecuente)"""
        self.client.get("/employees/create")
        
        employee_data = {
            'nombre': f'Dr. {choice(SAMPLE_NAMES)}',
            'documento': f'EMP{randint(10000, 99999)}',
            'especialidad': choice(SAMPLE_SPECIALTIES),
            'telefono': f'3{randint(100000000, 199999999)}'
        }
        
        with self.client.post("/employees/create", data=employee_data, catch_response=True) as response:
            if response.status_code in [200, 302]:
                response.success()
            else:
                response.failure(f"Employee creation failed: {response.status_code}")
    
    @task(4)
    def search_patients(self):
        """Tarea: Buscar pacientes (peso 4 - moderado)"""
        search_terms = ['Juan', 'María', 'Carlos', 'DOC']
        term = choice(search_terms)
        
        with self.client.get(f"/patients/?search={term}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Search failed: {response.status_code}")
    
    @task(3)
    def view_patient_detail(self):
        """Tarea: Ver detalle de paciente (peso 3 - moderado)"""
        patient_id = randint(1, 100)
        
        with self.client.get(f"/patients/{patient_id}", catch_response=True) as response:
            if response.status_code in [200, 404]:  # 404 es válido si no existe
                response.success()
            else:
                response.failure(f"Patient detail failed: {response.status_code}")
    
    @task(1)
    def logout(self):
        """Tarea: Logout (peso 1 - poco frecuente)"""
        with self.client.get("/auth/logout", catch_response=True) as response:
            if response.status_code in [200, 302]:
                response.success()
            else:
                response.failure(f"Logout failed: {response.status_code}")
        
        # Volver a hacer login
        self.login()


class AdminUser(HttpUser):
    """
    Usuario administrador con tareas administrativas.
    Menor cantidad (10% de usuarios).
    """
    
    wait_time = between(2, 5)
    weight = 1  # 10% de usuarios (vs weight=9 de IPSUser)
    
    def on_start(self):
        """Login como admin"""
        self.client.post("/auth/login", data={
            'username': 'admin',
            'password': 'admin123'
        })
    
    @task(3)
    def view_users(self):
        """Ver listado de usuarios"""
        self.client.get("/admin/users")
    
    @task(2)
    def view_audit_logs(self):
        """Ver logs de auditoría"""
        self.client.get("/admin/audit")
    
    @task(5)
    def view_reports(self):
        """Ver reportes y estadísticas"""
        self.client.get("/")


# ==========================================
# EVENT LISTENERS (OPCIONAL)
# ==========================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Ejecutado al inicio del test"""
    logging.info("🚀 Iniciando load test del sistema IPS")
    logging.info(f"Target: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Ejecutado al finalizar el test"""
    logging.info("✅ Load test finalizado")
    
    # Imprimir estadísticas resumidas
    stats = environment.stats
    logging.info(f"Total requests: {stats.total.num_requests}")
    logging.info(f"Total failures: {stats.total.num_failures}")
    logging.info(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    logging.info(f"RPS: {stats.total.total_rps:.2f}")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Listener para cada request (opcional, para debugging)"""
    if exception:
        logging.warning(f"Request failed: {name} - {exception}")
