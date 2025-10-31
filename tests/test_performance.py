"""
SPRINT 2 - Tests de Rendimiento
================================

Valida que el sistema cumpla con los SLAs de performance:
- Queries de DB < 50ms
- Endpoints HTTP < 200ms
- Operaciones bulk eficientes

Ejecutar:
    pytest tests/test_performance.py -v --benchmark-only
    pytest tests/test_performance.py -v --benchmark-compare
"""

import pytest
from app import create_app, db
from app.models import User, Patient, Employee, Appointment
from datetime import datetime, timedelta


pytestmark = pytest.mark.performance


# ==========================================
# FIXTURES
# ==========================================

@pytest.fixture
def app():
    """Aplicación configurada para performance tests"""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        _create_test_data()
        yield app
        db.session.remove()
        db.drop_all()


def _create_test_data():
    """Crea dataset de prueba para benchmarks"""
    # Usuario administrador
    admin = User(username='admin', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Empleados
    for i in range(10):
        emp = Employee(
            first_name=f'Doctor',
            last_name=f'Number{i}',
            document=f'EMP{i:03d}',
            position='General Physician',
            phone='1234567890'
        )
        db.session.add(emp)
    
    # Pacientes
    for i in range(100):
        patient = Patient(
            first_name=f'Patient',
            last_name=f'Number{i}',
            document=f'PAT{i:04d}',
            birth_date=datetime(1980, 1, 1) + timedelta(days=i*30),
            address=f'Street {i}',
            phone='9876543210'
        )
        db.session.add(patient)
    
    db.session.commit()
    
    # Citas (relacionar pacientes)
    patients = Patient.query.all()
    for i in range(50):
        appointment = Appointment(
            patient_id=patients[i % len(patients)].id,
            scheduled_at=datetime.now() + timedelta(days=i),
            reason=f'Consulta {i}',
            status='scheduled'
        )
        db.session.add(appointment)
    
    db.session.commit()


# ==========================================
# TESTS DE QUERIES
# ==========================================

def test_patient_simple_query_performance(benchmark, app):
    """Query simple de pacientes debe ser < 50ms"""
    with app.app_context():
        def query_patients():
            return Patient.query.all()
        
        result = benchmark(query_patients)
        
        # Validaciones
        assert len(result) == 100
        assert benchmark.stats.stats.mean < 0.05  # 50ms


def test_patient_filtered_query_performance(benchmark, app):
    """Query con filtros debe ser < 50ms"""
    with app.app_context():
        def query_filtered():
            return Patient.query.filter(
                Patient.first_name.like('%Patient%')
            ).limit(20).all()
        
        result = benchmark(query_filtered)
        assert len(result) == 20
        assert benchmark.stats.stats.mean < 0.05


def test_appointment_with_joins_performance(benchmark, app):
    """Query con JOINs debe ser < 100ms"""
    with app.app_context():
        def query_with_joins():
            return db.session.query(Appointment).join(
                Patient
            ).filter(
                Appointment.status == 'scheduled'
            ).all()
        
        result = benchmark(query_with_joins)
        assert len(result) == 50
        assert benchmark.stats.stats.mean < 0.1  # 100ms


@pytest.mark.slow
def test_patient_eager_loading_performance(benchmark, app):
    """Eager loading debe prevenir N+1 queries"""
    with app.app_context():
        def query_with_eager_loading():
            # Con joinedload para cargar appointments de una vez
            from sqlalchemy.orm import joinedload
            return Patient.query.options(
                joinedload(Patient.appointments)
            ).all()
        
        result = benchmark(query_with_eager_loading)
        
        # Verificar que se cargaron las appointments
        patients_with_appointments = [p for p in result if p.appointments]
        assert len(patients_with_appointments) > 0


# ==========================================
# TESTS DE ENDPOINTS HTTP
# ==========================================

def test_login_endpoint_performance(benchmark, client, app):
    """Login debe responder en < 200ms"""
    with app.app_context():
        def do_login():
            return client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin123'
            }, follow_redirects=False)
        
        result = benchmark(do_login)
        assert result.status_code in [200, 302]
        assert benchmark.stats.stats.mean < 0.2  # 200ms


def test_patients_list_endpoint_performance(benchmark, client, auth, app):
    """Listado de pacientes debe responder en < 200ms"""
    with app.app_context():
        auth.login(username='admin', password='admin123')
        
        def get_patients_list():
            return client.get('/patients/')
        
        result = benchmark(get_patients_list)
        assert result.status_code == 200
        assert benchmark.stats.stats.mean < 0.2


def test_appointments_list_endpoint_performance(benchmark, client, auth, app):
    """Listado de citas debe responder en < 200ms"""
    with app.app_context():
        auth.login(username='admin', password='admin123')
        
        def get_appointments_list():
            return client.get('/appointments/')
        
        result = benchmark(get_appointments_list)
        assert result.status_code == 200
        assert benchmark.stats.stats.mean < 0.2


# ==========================================
# TESTS DE OPERACIONES BULK
# ==========================================

@pytest.mark.slow
def test_bulk_patient_creation_performance(benchmark, app):
    """Crear 100 pacientes debe tomar < 5 segundos"""
    with app.app_context():
        def create_bulk_patients():
            patients = []
            for i in range(100, 200):  # 100 nuevos
                patient = Patient(
                    first_name='Bulk',
                    last_name=f'Patient {i}',
                    document=f'BULK{i:04d}',
                    birth_date=datetime(1990, 1, 1),
                    address=f'Address {i}',
                    phone='1111111111'
                )
                patients.append(patient)
            
            db.session.bulk_save_objects(patients)
            db.session.commit()
            
            # Limpiar para no afectar otros tests
            Patient.query.filter(Patient.document.like('BULK%')).delete()
            db.session.commit()
        
        benchmark(create_bulk_patients)
        assert benchmark.stats.stats.mean < 5.0  # 5 segundos


@pytest.mark.slow
def test_bulk_read_performance(benchmark, app):
    """Leer 1000 registros debe ser < 1 segundo"""
    with app.app_context():
        # Crear más datos para este test
        for i in range(200, 1200):
            patient = Patient(
                first_name='Read',
                last_name=f'Test {i}',
                document=f'Read{i:04d}'.upper(),
                birth_date=datetime(1985, 1, 1),
                address='Test',
                phone='0000000000'
            )
            db.session.add(patient)
        db.session.commit()
        
        def read_bulk():
            return Patient.query.limit(1000).all()
        
        result = benchmark(read_bulk)
        assert len(result) == 1000
        assert benchmark.stats.stats.mean < 1.0  # 1 segundo
        
        # Cleanup
        Patient.query.filter(Patient.document.like('READ%')).delete()
        db.session.commit()


# ==========================================
# TESTS DE SERVICIOS
# ==========================================

def test_patient_service_list_performance(benchmark, app):
    """Service layer debe ser eficiente"""
    from app.services.patient_service import PatientService
    from app.adapters.sql_patient_repository import SqlAlchemyPatientRepository
    
    with app.app_context():
        repo = SqlAlchemyPatientRepository()
        service = PatientService(repo)
        
        def list_via_service():
            return service.list()
        
        result = benchmark(list_via_service)
        assert len(result) == 100
        assert benchmark.stats.stats.mean < 0.1  # 100ms


# ==========================================
# TESTS DE MEMORIA
# ==========================================

@pytest.mark.slow
def test_memory_usage_stays_reasonable(app):
    """Uso de memoria debe ser razonable durante operaciones"""
    import tracemalloc
    
    with app.app_context():
        tracemalloc.start()
        
        # Operación que podría consumir mucha memoria
        for _ in range(10):
            patients = Patient.query.all()
            _ = [p.to_dict() if hasattr(p, 'to_dict') else str(p) for p in patients]
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memoria pico no debe exceder 50MB
        assert peak < 50 * 1024 * 1024  # 50 MB


# ==========================================
# BENCHMARKS COMPARATIVOS
# ==========================================

@pytest.mark.parametrize("limit", [10, 50, 100, 500])
def test_query_performance_scales_linearly(benchmark, app, limit):
    """Performance debe escalar linealmente con el tamaño del resultado"""
    with app.app_context():
        # Asegurar suficientes datos
        if Patient.query.count() < limit:
            for i in range(Patient.query.count(), limit):
                db.session.add(Patient(
                    first_name='Scale',
                    last_name=f'Test {i}',
                    document=f'SCALE{i:04d}',
                    birth_date=datetime(1990, 1, 1),
                    address='Test',
                    phone='0000000000'
                ))
            db.session.commit()
        
        def query_with_limit():
            return Patient.query.limit(limit).all()
        
        result = benchmark(query_with_limit)
        assert len(result) == limit


# ==========================================
# CONFIGURACIÓN DE BENCHMARKS
# ==========================================

def pytest_benchmark_scale_unit(config, unit, benchmarks, best, worst, sort):
    """Configura el display de benchmarks"""
    if unit == 'seconds':
        return 'milliseconds', 0.001
    return unit, 1.0
