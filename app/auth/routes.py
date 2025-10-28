from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from . import auth_bp
from ..forms import LoginForm, RegistrationForm
from ..services.user_service import UserService
from ..adapters.sql_user_repository import SqlAlchemyUserRepository
from ..infrastructure.security.password_policy import PasswordPolicy
from ..infrastructure.security.rate_limiter import rate_limit
from ..infrastructure.audit.audit_log import AuditLogger

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
        user = user_service.login(
            username=form.username.data,
            password=form.password.data
        )
        if user:
            login_user(user)
            audit_logger.log_action('login_attempt', {
                'username': form.username.data,
                'success': user is not None
            })
            flash('Has iniciado sesión correctamente')
            return redirect(url_for('main.index'))
        flash('Usuario o contraseña inválidos')
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
            password=form.password.data
        )
        
        flash(message)
        if success:
            return redirect(url_for('auth.login'))
            
    return render_template('register.html', form=form, title='Registro')
