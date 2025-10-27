from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from .models import db, User

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
    
    # Registrar blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    # Registrar blueprint "main" para que exista main.index
    from .main import main_bp
    app.register_blueprint(main_bp)
    
    # Crear tablas
    with app.app_context():
        db.create_all()
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app