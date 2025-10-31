from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from .models import db, User
from datetime import timedelta

# Inicializar extensiones
csrf = CSRFProtect()
login_manager = LoginManager()

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Configuración base
    app.config.from_object('config.Config')
    
    # Sobrescribir con configuración de test si se proporciona
    if test_config:
        app.config.update(test_config)
    
    # Inicializar extensiones
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Configurar duración de sesión (ISO 27001 - A.9.4.2)
    app.permanent_session_lifetime = timedelta(seconds=app.config['PERMANENT_SESSION_LIFETIME'])
    
    # Configurar sesiones permanentes
    @app.before_request
    def make_session_permanent():
        session.permanent = True
    
    # Registrar blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    # Registrar blueprint "main" para que exista main.index
    from .main import main_bp
    app.register_blueprint(main_bp)

    # Registrar blueprints IPS (independientemente, con manejo de errores por módulo)
    from importlib import import_module
    for mod, bp_name in [
        ('.patients', 'patients_bp'),
        ('.appointments', 'appointments_bp'),
        ('.records', 'records_bp'),
        ('.admin', 'admin_bp'),
        ('.employees', 'employees_bp'),
    ]:
        try:
            module = import_module(mod, package=__name__)
            bp = getattr(module, bp_name)
            app.register_blueprint(bp)
        except Exception as e:
            app.logger.debug(f"No se pudo registrar {mod}: {e}")
    
    # Crear tablas
    with app.app_context():
        db.create_all()
    
    # Agregar headers de seguridad (ISO 27001 - A.14.1.2, A.14.1.3)
    @app.after_request
    def set_security_headers(response):
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        )
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # XSS Protection (legacy, but still useful for older browsers)
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Permissions Policy (formerly Feature Policy)
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        return response
    
    @login_manager.user_loader
    def load_user(id):
        return db.session.get(User, int(id))

    @app.context_processor
    def utility_processor():
        from flask import url_for
        def has_endpoint(name: str) -> bool:
            try:
                url_for(name)
                return True
            except Exception:
                return False
        return dict(has_endpoint=has_endpoint)
    
    return app