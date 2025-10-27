from flask import Blueprint

# Crear el blueprint con url_prefix para todas las rutas de autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Verificar que el archivo routes.py existe antes de importar
try:
    from . import routes
except ImportError:
    print("Error: Asegúrate de que el archivo routes.py existe en el directorio auth/")

# Opcional: Agregar configuración específica del blueprint
@auth_bp.before_app_request
def before_request():
    """Ejecutar antes de cada solicitud al blueprint"""
    pass
