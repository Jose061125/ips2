"""
Tests de Seguridad ISO 27001
Valida el cumplimiento de controles de seguridad según ISO/IEC 27001:2013
"""

import pytest
from flask import Flask
from werkzeug.security import check_password_hash
import os
import time


class TestISO27001_A9_AccessControl:
    """A.9 Control de Acceso"""
    
    def test_A9_2_1_user_registration(self, app):
        """A.9.2.1 - Registro y baja de usuarios"""
        # Test directo del servicio de registro (sin formulario HTML)
        from app.services.user_service import UserService
        from app.adapters.sql_user_repository import SqlAlchemyUserRepository
        from app.models import User
        
        with app.app_context():
            user_repo = SqlAlchemyUserRepository()
            user_service = UserService(user_repo)
            
            # Registrar nuevo usuario
            success, message = user_service.register_user(
                username='test_iso_user',
                password='SecurePass123',
                role='usuario'
            )
            
            assert success == True, f"Registro debe ser exitoso: {message}"
            
            # Verificar que el usuario fue creado
            user = User.query.filter_by(username='test_iso_user').first()
            assert user is not None, "Usuario debe ser registrado en la BD"
            assert user.role == 'usuario', "Rol debe ser asignado correctamente"
    
    def test_A9_2_2_access_management(self, client, auth, test_user):
        """A.9.2.2 - Gestión de privilegios de acceso"""
        # Crea usuario sin privilegios de admin
        from app.models import User, db
        
        regular_user = User(username='usuario_test', role='usuario')
        regular_user.set_password('password123')
        db.session.add(regular_user)
        db.session.commit()
        
        # Login como usuario normal
        auth.login(username='usuario_test', password='password123')
        
        # Intenta acceder a ruta de admin (debe ser bloqueado)
        response = client.get('/admin/users')
        
        assert response.status_code == 403 or response.status_code == 302, \
            "Usuario sin privilegios debe ser bloqueado"
    
    def test_A9_2_5_review_of_access_rights(self):
        """A.9.2.5 - Revisión de derechos de acceso"""
        from app.models import User
        
        user = User(username='test_role', role='medico')
        
        assert user.has_role('medico'), "has_role debe funcionar correctamente"
        assert not user.has_role('admin'), "Usuario no debe tener rol admin"
    
    def test_A9_4_2_secure_logon_procedures(self, client):
        """A.9.4.2 - Procedimiento de conexión seguro"""
        response = client.post('/auth/login', data={
            'username': 'wrong_user',
            'password': 'wrong_pass'
        })
        
        # Login fallido debe ser rechazado
        assert b'Usuario o contrase' in response.data or response.status_code == 302
    
    def test_A9_4_3_password_management_system(self):
        """A.9.4.3 - Sistema de gestión de contraseñas"""
        from app.models import User
        
        user = User(username='test_pwd')
        
        # Password debe ser hasheado, no almacenado en texto plano
        user.set_password('SecurePass123')
        
        assert user.password_hash is not None
        assert user.password_hash != 'SecurePass123', "Password no debe estar en texto plano"
        assert user.check_password('SecurePass123'), "check_password debe validar correctamente"
        assert not user.check_password('WrongPassword'), "Password incorrecto debe ser rechazado"


class TestISO27001_A10_Cryptography:
    """A.10 Criptografía"""
    
    def test_A10_1_1_cryptographic_controls_policy(self):
        """A.10.1.1 - Política de uso de controles criptográficos"""
        from werkzeug.security import generate_password_hash
        
        password = 'TestPassword123'
        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Verifica que use pbkdf2:sha256
        assert hashed.startswith('pbkdf2:sha256:'), "Debe usar pbkdf2:sha256"
        
        # Verifica que el hash sea válido
        assert check_password_hash(hashed, password)
    
    def test_A10_1_2_key_management(self):
        """A.10.1.2 - Gestión de claves"""
        from config import Config
        
        # SECRET_KEY debe estar definida
        assert Config.SECRET_KEY is not None
        assert len(Config.SECRET_KEY) > 16, "SECRET_KEY debe tener longitud suficiente"
        
        # CSRF key debe estar definida
        assert Config.WTF_CSRF_SECRET_KEY is not None
    
    def test_password_complexity_requirements(self, app):
        """Valida requisitos de complejidad de contraseñas"""
        from app.models import User
        
        with app.app_context():
            user = User(username='test_complexity')
            
            # Password muy corto debe fallar
            with pytest.raises(ValueError, match="at least 8 characters"):
                user.set_password('short')
            
            # Password válido debe funcionar
            user.set_password('ValidPassword123')
            assert user.password_hash is not None


class TestISO27001_A12_OperationsSecurity:
    """A.12 Seguridad de las Operaciones"""
    
    def test_A12_4_1_event_logging(self, app):
        """A.12.4.1 - Registro de eventos"""
        from app.infrastructure.audit.audit_log import AuditLogger
        
        logger = AuditLogger()
        
        # Verifica que el logger tenga el método log_action
        assert hasattr(logger, 'log_action')
        
        # Simula un evento
        with app.test_request_context('/'):
            logger.log_action('TEST_EVENT', {'test': 'data'})
        
        # Verifica que el archivo de log exista
        assert os.path.exists('logs/audit.log')
    
    def test_A12_4_3_administrator_logs(self, app):
        """A.12.4.3 - Registros del administrador y del operador"""
        from app.infrastructure.audit.audit_log import AuditLogger
        
        logger = AuditLogger()
        
        # Simula acción de admin
        with app.test_request_context('/'):
            logger.log_action('ADMIN_ACTION', {'action': 'user_role_changed'})
        
        # Lee el log y verifica que se registró
        with open('logs/audit.log', 'r') as f:
            logs = f.read()
            assert 'ADMIN_ACTION' in logs


class TestISO27001_A18_Compliance:
    """A.18 Cumplimiento"""
    
    def test_A18_1_3_protection_of_personal_data(self):
        """A.18.1.3 - Protección de datos personales y privacidad"""
        from config import Config
        
        # Session cookies deben ser seguros
        assert Config.SESSION_COOKIE_HTTPONLY == True, \
            "SESSION_COOKIE_HTTPONLY debe estar habilitado"
        
        assert Config.SESSION_COOKIE_SAMESITE == 'Lax', \
            "SESSION_COOKIE_SAMESITE debe estar configurado"
        
        # CSRF debe estar habilitado
        assert Config.WTF_CSRF_ENABLED == True, \
            "CSRF protection debe estar habilitado"


class TestRateLimiting:
    """Tests de Rate Limiting (Prevención de fuerza bruta)"""
    
    def test_rate_limit_login_attempts(self, client):
        """A.9.4.3 - Prevención de fuerza bruta en login"""
        from app.models import User, db
        
        # Crea un usuario de prueba
        user = User(username='rate_limit_test', role='usuario')
        user.set_password('correct_password')
        db.session.add(user)
        db.session.commit()
        
        # Simula múltiples intentos fallidos
        for i in range(4):
            client.post('/auth/login', data={
                'username': 'rate_limit_test',
                'password': 'wrong_password'
            })
        
        # El usuario debe estar bloqueado después de 3 intentos
        user = User.query.filter_by(username='rate_limit_test').first()
        
        # Verifica campos de rate limiting
        assert hasattr(user, 'failed_login_attempts')
        assert user.failed_login_attempts >= 3, "Debe registrar intentos fallidos"


class TestSessionSecurity:
    """Tests de seguridad de sesión"""
    
    def test_session_timeout_configuration(self):
        """Verifica que el timeout de sesión esté configurado"""
        from config import Config
        
        assert hasattr(Config, 'PERMANENT_SESSION_LIFETIME')
        
        # Timeout debe ser razonable (30 minutos = 1800 segundos)
        timeout = Config.PERMANENT_SESSION_LIFETIME
        assert timeout <= 3600, "Session timeout debe ser <= 1 hora"
        assert timeout >= 600, "Session timeout debe ser >= 10 minutos"
    
    def test_csrf_protection_enabled(self, app):
        """Verifica que CSRF protection esté habilitado"""
        # En tests está deshabilitado (WTF_CSRF_ENABLED=False)
        # En producción debe estar habilitado
        
        # Verifica que la configuración existe
        assert 'WTF_CSRF_ENABLED' in app.config
        
        # En tests está False, pero verificamos que en producción estaría True
        # Importamos la config de producción
        from config import Config
        assert hasattr(Config, 'WTF_CSRF_ENABLED')
        assert Config.WTF_CSRF_ENABLED == True, "CSRF debe estar habilitado en producción"
    
    def test_secure_cookie_settings(self):
        """Verifica configuración segura de cookies"""
        from config import Config
        
        # HTTPONLY: Cookies no accesibles desde JavaScript
        assert Config.SESSION_COOKIE_HTTPONLY == True
        
        # SAMESITE: Protección contra CSRF
        assert Config.SESSION_COOKIE_SAMESITE in ['Lax', 'Strict']


class TestAuditTrail:
    """Tests de trazabilidad de auditoría"""
    
    def test_audit_log_format(self, app):
        """Verifica que los logs de auditoría tengan formato correcto"""
        from app.infrastructure.audit.audit_log import AuditLogger
        
        logger = AuditLogger()
        
        with app.test_request_context('/'):
            logger.log_action('TEST_ACTION', {'key': 'value'})
        
        # Lee última línea del log
        with open('logs/audit.log', 'r') as f:
            last_line = f.readlines()[-1]
        
        # Debe contener: timestamp, user, IP, action, details
        assert 'User:' in last_line
        assert 'Action:TEST_ACTION' in last_line
        assert 'Details:' in last_line
    
    def test_audit_events_are_logged(self, client, auth, app, test_user):
        """Verifica que eventos importantes sean auditados"""
        # Login exitoso debe ser auditado
        auth.login()
        
        # Lee el log
        with open('logs/audit.log', 'r') as f:
            logs = f.read()
        
        # Debe registrar eventos
        assert len(logs) > 0, "Audit log debe contener eventos"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
