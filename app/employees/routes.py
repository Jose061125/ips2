from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from . import employees_bp
from ..models import Employee
from ..forms import EmployeeForm
from ..services.employee_service import EmployeeService
from ..adapters.sql_employee_repository import SqlAlchemyEmployeeRepository
from ..infrastructure.security.access_control import require_any_role
from ..infrastructure.security.rate_limiter import rate_limit
from ..infrastructure.audit.audit_log import AuditLogger

employee_repository = SqlAlchemyEmployeeRepository()
employee_service = EmployeeService(employee_repository)
audit_logger = AuditLogger()


@employees_bp.route('/')
@login_required
def index():
    """List all employees"""
    employees = employee_service.list_employees()
    return render_template('employees/index.html', employees=employees, title='Empleados')


@employees_bp.route('/create', methods=['GET', 'POST'])
@login_required
@require_any_role('admin', 'recepcionista')
@rate_limit
def create():
    """Create a new employee"""
    form = EmployeeForm()
    if form.validate_on_submit():
        success, message, employee = employee_service.create_employee(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            document=form.document.data,
            position=form.position.data,
            hire_date=form.hire_date.data,
            phone=form.phone.data,
            email=form.email.data
        )
        
        if success:
            audit_logger.log_action('employee_create', {
                'employee_id': employee.id,
                'document': employee.document,
                'name': employee.full_name()
            })
        
        flash(message)
        if success:
            return redirect(url_for('employees.index'))
    
    return render_template('employees/form.html', form=form, title='Nuevo Empleado', mode='create')


@employees_bp.route('/<int:employee_id>/edit', methods=['GET', 'POST'])
@login_required
@require_any_role('admin', 'recepcionista')
@rate_limit
def edit(employee_id):
    """Edit an existing employee"""
    employee = employee_service.get_employee(employee_id)
    if not employee:
        flash('Empleado no encontrado')
        return redirect(url_for('employees.index'))
    
    form = EmployeeForm()
    if form.validate_on_submit():
        success, message, updated_employee = employee_service.update_employee(
            employee_id=employee_id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            document=form.document.data,
            position=form.position.data,
            hire_date=form.hire_date.data,
            phone=form.phone.data,
            email=form.email.data
        )
        
        if success:
            audit_logger.log_action('employee_update', {
                'employee_id': employee_id,
                'document': updated_employee.document
            })
        
        flash(message)
        if success:
            return redirect(url_for('employees.index'))
    
    # Pre-populate form
    if not form.is_submitted():
        form.first_name.data = employee.first_name
        form.last_name.data = employee.last_name
        form.document.data = employee.document
        form.position.data = employee.position
        form.hire_date.data = employee.hire_date
        form.phone.data = employee.phone
        form.email.data = employee.email
    
    return render_template('employees/form.html', form=form, employee=employee, 
                          title='Editar Empleado', mode='edit')


@employees_bp.route('/<int:employee_id>/delete', methods=['POST'])
@login_required
@require_any_role('admin')
@rate_limit
def delete(employee_id):
    """Delete an employee"""
    success, message = employee_service.delete_employee(employee_id)
    
    if success:
        audit_logger.log_action('employee_delete', {'employee_id': employee_id})
    
    flash(message)
    return redirect(url_for('employees.index'))
