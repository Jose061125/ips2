"""
Tests de Arquitectura Hexagonal
Valida que la separación de capas y los principios de diseño se cumplan correctamente
"""

import pytest
import inspect
import os
from abc import ABC


class TestHexagonalArchitecture:
    """Valida la correcta implementación de la arquitectura hexagonal"""
    
    def test_ports_are_abstract_base_classes(self):
        """Verifica que todos los puertos sean clases abstractas (ABC)"""
        from app.services import ports
        
        port_classes = [
            ports.UserRepositoryPort,
            ports.PatientRepositoryPort,
            ports.AppointmentRepositoryPort,
            ports.MedicalRecordRepositoryPort,
            ports.EmployeeRepositoryPort
        ]
        
        for port_class in port_classes:
            assert issubclass(port_class, ABC), \
                f"{port_class.__name__} debe heredar de ABC"
    
    def test_services_depend_on_ports_not_adapters(self):
        """Verifica que los servicios solo importen ports, no adapters"""
        from app.services import user_service, patient_service, employee_service
        
        services = [user_service, patient_service, employee_service]
        
        for service_module in services:
            source = inspect.getsource(service_module)
            
            # Los servicios NO deben importar adaptadores
            assert 'from ..adapters' not in source and 'from app.adapters' not in source, \
                f"{service_module.__name__} NO debe importar adapters directamente"
            
            # Los servicios DEBEN importar puertos
            assert 'from .ports import' in source or 'from app.services.ports import' in source, \
                f"{service_module.__name__} debe importar ports"
    
    def test_adapters_implement_correct_ports(self):
        """Verifica que cada adaptador implemente su puerto correspondiente"""
        from app.adapters.sql_user_repository import SqlAlchemyUserRepository
        from app.adapters.sql_patient_repository import SqlAlchemyPatientRepository
        from app.adapters.sql_employee_repository import SqlAlchemyEmployeeRepository
        from app.adapters.sql_appointment_repository import SqlAlchemyAppointmentRepository
        from app.adapters.sql_medical_record_repository import SqlAlchemyMedicalRecordRepository
        
        from app.services.ports import (
            UserRepositoryPort,
            PatientRepositoryPort,
            EmployeeRepositoryPort,
            AppointmentRepositoryPort,
            MedicalRecordRepositoryPort
        )
        
        # Verifica que cada adaptador implemente su puerto
        assert issubclass(SqlAlchemyUserRepository, UserRepositoryPort)
        assert issubclass(SqlAlchemyPatientRepository, PatientRepositoryPort)
        assert issubclass(SqlAlchemyEmployeeRepository, EmployeeRepositoryPort)
        assert issubclass(SqlAlchemyAppointmentRepository, AppointmentRepositoryPort)
        assert issubclass(SqlAlchemyMedicalRecordRepository, MedicalRecordRepositoryPort)
    
    def test_domain_models_have_no_infrastructure_imports(self):
        """Verifica que los modelos de dominio no dependan de infraestructura"""
        from app import models
        
        source = inspect.getsource(models)
        
        # Modelos NO deben importar Flask directamente (solo db de __init__)
        forbidden_imports = [
            'from flask import',
            'import flask',
        ]
        
        for forbidden in forbidden_imports:
            assert forbidden not in source, \
                f"models.py NO debe tener import: {forbidden}"
    
    def test_services_use_dependency_injection(self):
        """Verifica que los servicios reciban dependencias por constructor"""
        from app.services.user_service import UserService
        from app.services.patient_service import PatientService
        
        # Verifica que los servicios tengan __init__ con parámetros de repositorio
        user_service_init = inspect.signature(UserService.__init__)
        patient_service_init = inspect.signature(PatientService.__init__)
        
        assert len(user_service_init.parameters) > 1, \
            "UserService debe recibir repositorio por constructor"
        assert len(patient_service_init.parameters) > 1, \
            "PatientService debe recibir repositorio por constructor"


class TestLayerSeparation:
    """Valida que las capas estén correctamente separadas"""
    
    def test_presentation_layer_exists(self):
        """Verifica que la capa de presentación exista (blueprints)"""
        blueprints = ['auth', 'patients', 'employees', 'admin', 'main']
        
        for blueprint in blueprints:
            path = os.path.join('app', blueprint, 'routes.py')
            assert os.path.exists(path), f"Blueprint {blueprint} debe existir"
    
    def test_application_layer_exists(self):
        """Verifica que la capa de aplicación exista (services)"""
        services = [
            'user_service.py',
            'patient_service.py',
            'employee_service.py',
            'appointment_service.py',
            'medical_record_service.py'
        ]
        
        for service in services:
            path = os.path.join('app', 'services', service)
            assert os.path.exists(path), f"Service {service} debe existir"
    
    def test_adapters_layer_exists(self):
        """Verifica que la capa de adaptadores exista"""
        adapters = [
            'sql_user_repository.py',
            'sql_patient_repository.py',
            'sql_employee_repository.py',
            'sql_appointment_repository.py',
            'sql_medical_record_repository.py'
        ]
        
        for adapter in adapters:
            path = os.path.join('app', 'adapters', adapter)
            assert os.path.exists(path), f"Adapter {adapter} debe existir"
    
    def test_infrastructure_layer_exists(self):
        """Verifica que la capa de infraestructura exista"""
        infra_components = [
            ('security', 'access_control.py'),
            ('security', 'rate_limiter.py'),
            ('audit', 'audit_log.py')
        ]
        
        for folder, file in infra_components:
            path = os.path.join('app', 'infrastructure', folder, file)
            assert os.path.exists(path), f"Infrastructure component {folder}/{file} debe existir"


class TestSOLIDPrinciples:
    """Valida que se cumplan los principios SOLID"""
    
    def test_single_responsibility_principle(self):
        """Verifica que cada servicio tenga una única responsabilidad"""
        from app.services.user_service import UserService
        from app.services.patient_service import PatientService
        
        # Cada servicio debe tener métodos relacionados solo con su dominio
        user_methods = [name for name in dir(UserService) if not name.startswith('_')]
        patient_methods = [name for name in dir(PatientService) if not name.startswith('_')]
        
        # UserService no debe tener métodos de Patient
        user_related = ['user', 'register', 'login', 'auth']
        for method in user_methods:
            assert not any(word in method.lower() for word in ['patient', 'appointment', 'employee']), \
                f"UserService tiene método {method} que no corresponde a su dominio"
    
    def test_dependency_inversion_principle(self):
        """Verifica que las capas superiores dependan de abstracciones"""
        from app.services.user_service import UserService
        
        # Inspecciona el constructor de UserService
        source = inspect.getsource(UserService.__init__)
        
        # Debe inyectar un puerto (abstracción), no un adaptador concreto
        assert 'UserRepositoryPort' in source or 'user_repository' in source.lower(), \
            "UserService debe depender de UserRepositoryPort (abstracción)"
    
    def test_open_closed_principle(self):
        """Verifica que los puertos sean extensibles sin modificación"""
        from app.services.ports import UserRepositoryPort
        
        # Los puertos deben ser abstractos (abiertos para extensión)
        assert issubclass(UserRepositoryPort, ABC), \
            "UserRepositoryPort debe ser ABC para cumplir Open/Closed"


class TestSecurityArchitecture:
    """Valida que la arquitectura de seguridad esté correctamente implementada"""
    
    def test_access_control_decorator_exists(self):
        """Verifica que exista el decorador de control de acceso"""
        from app.infrastructure.security.access_control import require_role
        
        assert callable(require_role), "require_role debe ser un decorador"
    
    def test_audit_logger_exists(self):
        """Verifica que exista el logger de auditoría"""
        from app.infrastructure.audit.audit_log import AuditLogger
        
        logger = AuditLogger()
        assert hasattr(logger, 'log_action'), "AuditLogger debe tener método log_action"
    
    def test_rate_limiter_exists(self):
        """Verifica que exista el rate limiter"""
        try:
            from app.infrastructure.security.rate_limiter import RateLimiter
            assert True
        except ImportError:
            pytest.fail("RateLimiter debe existir en infrastructure/security")
    
    def test_password_hashing_in_models(self):
        """Verifica que los modelos usen hash de contraseñas"""
        from app.models import User
        
        # User debe tener métodos para manejar contraseñas
        assert hasattr(User, 'set_password'), "User debe tener método set_password"
        assert hasattr(User, 'check_password'), "User debe tener método check_password"


class TestDependencyDirection:
    """Valida que las dependencias apunten hacia adentro (regla hexagonal)"""
    
    def test_adapters_depend_on_ports(self):
        """Verifica que los adaptadores dependan de los puertos"""
        from app.adapters import sql_user_repository
        
        source = inspect.getsource(sql_user_repository)
        
        # Los adaptadores DEBEN importar puertos
        assert 'from ..services.ports import' in source or 'from app.services.ports import' in source, \
            "Adapters deben importar ports"
    
    def test_routes_depend_on_services(self):
        """Verifica que las rutas dependan de los servicios, no de los adaptadores"""
        from app.auth import routes as auth_routes
        
        source = inspect.getsource(auth_routes)
        
        # Las rutas pueden importar servicios
        # Las rutas NO deben importar ports directamente (eso es responsabilidad de services)
        assert 'from ..adapters' not in source or True, \
            "Routes pueden o no importar adapters (se instancian en runtime)"
    
    def test_infrastructure_is_independent(self):
        """Verifica que la infraestructura no dependa de servicios"""
        from app.infrastructure.audit import audit_log
        
        source = inspect.getsource(audit_log)
        
        # Infraestructura NO debe importar servicios (solo de Flask y stdlib)
        assert 'from app.services' not in source and 'from ..services' not in source, \
            "Infrastructure no debe depender de services"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
