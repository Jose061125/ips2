from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import patients_bp
from ..forms import PatientForm
from ..adapters.sql_patient_repository import SqlAlchemyPatientRepository
from ..services.patient_service import PatientService
from ..infrastructure.audit.audit_log import AuditLogger
from ..infrastructure.security.rate_limiter import rate_limit
from ..infrastructure.security.access_control import require_any_role

repo = SqlAlchemyPatientRepository()
service = PatientService(repo)
audit = AuditLogger()


@patients_bp.route('/')
@login_required
def index():
    patients = service.list()
    return render_template('patients/index.html', patients=patients, title='Pacientes')


@patients_bp.route('/create', methods=['GET', 'POST'])
@login_required
@require_any_role('admin', 'recepcionista')
@rate_limit
def create():
    form = PatientForm()
    if form.validate_on_submit():
        ok, msg, patient = service.create(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            document=form.document.data,
            birth_date=form.birth_date.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
        )
        flash(msg)
        audit.log_action('patient_create', {'document': form.document.data, 'success': ok})
        if ok:
            return redirect(url_for('patients.index'))
    return render_template('patients/form.html', form=form, title='Nuevo Paciente')


@patients_bp.route('/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
@require_any_role('admin', 'recepcionista')
@rate_limit
def edit(patient_id):
    patient = service.get(patient_id)
    if not patient:
        flash('Paciente no encontrado')
        return redirect(url_for('patients.index'))
    form = PatientForm(obj=patient)
    if form.validate_on_submit():
        ok, msg, _ = service.update(
            patient_id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            document=form.document.data,
            birth_date=form.birth_date.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
        )
        flash(msg)
        audit.log_action('patient_update', {'patient_id': patient_id, 'success': ok})
        if ok:
            return redirect(url_for('patients.index'))
    return render_template('patients/form.html', form=form, title='Editar Paciente')


@patients_bp.route('/<int:patient_id>/delete', methods=['POST'])
@login_required
@require_any_role('admin')
@rate_limit
def delete(patient_id):
    ok, msg = service.delete(patient_id)
    flash(msg)
    audit.log_action('patient_delete', {'patient_id': patient_id, 'success': ok})
    return redirect(url_for('patients.index'))
