from functools import wraps
from flask_login import current_user
from flask import abort, flash, redirect, url_for

def require_role(role):
    """
    Decorator to restrict access to routes based on user role.
    ISO 27001 A.9.2 - User access management
    
    Usage:
        @require_role('admin')
        def admin_only_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor inicia sesión para acceder.')
                return redirect(url_for('auth.login'))
            if not current_user.has_role(role):
                flash(f'Acceso denegado. Se requiere rol: {role}')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_any_role(*roles):
    """
    Decorator to restrict access to routes requiring any of the specified roles.
    ISO 27001 A.9.2 - User access management
    
    Usage:
        @require_any_role('admin', 'medico')
        def medical_staff_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor inicia sesión para acceder.')
                return redirect(url_for('auth.login'))
            if not current_user.has_any_role(*roles):
                flash(f'Acceso denegado. Se requiere uno de los roles: {", ".join(roles)}')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator