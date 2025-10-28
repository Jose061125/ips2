from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from . import auth_bp
from ..forms import LoginForm, RegistrationForm
from ..services.user_service import UserService
from ..adapters.sql_user_repository import SqlAlchemyUserRepository
from ..infrastructure.security.password_policy import PasswordPolicy
from ..infrastructure.security.rate_limiter import rate_limit
from ..infrastructure.audit.audit_log import AuditLogger
from ..models import db

user_repository = SqlAlchemyUserRepository()
user_service = UserService(user_repository)
audit_logger = AuditLogger()

@auth_bp.route('/login', methods=['GET', 'POST'])
@rate_limit
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = user_repository.get_by_username(form.username.data)
        
        # Check if account is locked (ISO 27001 - A.9.4.2)
        if user and user.is_locked():
            audit_logger.log_action('login_attempt_locked', {
                'username': form.username.data,
                'locked_until': user.locked_until.isoformat() if user.locked_until else None
            })
            flash('Cuenta bloqueada temporalmente. Intente más tarde.')
            return render_template('login.html', form=form, title='Login')
        
        # Verify credentials
        authenticated_user = user_service.login(
            username=form.username.data,
            password=form.password.data
        )
        
        if authenticated_user:
            # Reset failed attempts on successful login
            authenticated_user.reset_failed_attempts()
            db.session.commit()
            
            login_user(authenticated_user)
            audit_logger.log_action('login_success', {
                'username': form.username.data,
                'user_id': authenticated_user.id
            })
            flash('Has iniciado sesión correctamente')
            return redirect(url_for('main.index'))
        else:
            # Increment failed attempts
            if user:
                user.increment_failed_attempts(lockout_duration_minutes=15, max_attempts=5)
                db.session.commit()
                
                if user.is_locked():
                    flash('Demasiados intentos fallidos. Cuenta bloqueada temporalmente.')
                else:
                    remaining = 5 - user.failed_login_attempts
                    flash(f'Usuario o contraseña inválidos. Intentos restantes: {remaining}')
            else:
                flash('Usuario o contraseña inválidos')
            
            audit_logger.log_action('login_failure', {
                'username': form.username.data,
                'user_exists': user is not None,
                'attempts': user.failed_login_attempts if user else 0
            })
    
    return render_template('login.html', form=form, title='Login')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@rate_limit
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Validate password strength
        is_valid, msg = PasswordPolicy.validate_password(form.password.data)
        if not is_valid:
            return render_template('register.html', form=form, title='Registro', error=msg)

        success, message = user_service.register_user(
            username=form.username.data,
            password=form.password.data,
            role=form.role.data
        )
        
        flash(message)
        if success:
            return redirect(url_for('auth.login'))
            
    return render_template('register.html', form=form, title='Registro')
