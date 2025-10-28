from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from . import admin_bp
from ..models import User, db
from ..forms import UserManagementForm
from ..infrastructure.security.access_control import require_role
from ..infrastructure.audit.audit_log import AuditLogger

audit_logger = AuditLogger()

@admin_bp.route('/users')
@login_required
@require_role('admin')
def list_users():
    """Lista todos los usuarios del sistema"""
    users = User.query.order_by(User.username).all()
    return render_template('admin/users.html', users=users, title='Gestión de Usuarios')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def edit_user(user_id):
    """Edita el rol de un usuario"""
    user = User.query.get_or_404(user_id)
    form = UserManagementForm()
    
    if form.validate_on_submit():
        old_role = user.role
        user.role = form.role.data
        db.session.commit()
        
        audit_logger.log_action('role_change', {
            'user_id': user.id,
            'username': user.username,
            'old_role': old_role,
            'new_role': user.role
        })
        
        flash(f'Rol de {user.username} actualizado a {user.role}')
        return redirect(url_for('admin.list_users'))
    
    # Pre-poblar el formulario con datos actuales
    if not form.is_submitted():
        form.username.data = user.username
        form.role.data = user.role
    
    return render_template('admin/edit_user.html', form=form, user=user, title='Editar Usuario')
