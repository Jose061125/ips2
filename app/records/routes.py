from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from . import records_bp
from ..forms import MedicalRecordForm
from ..adapters.sql_medical_record_repository import SqlAlchemyMedicalRecordRepository
from ..adapters.sql_patient_repository import SqlAlchemyPatientRepository
from ..services.medical_record_service import MedicalRecordService
from ..infrastructure.audit.audit_log import AuditLogger
from ..infrastructure.security.rate_limiter import rate_limit
from ..infrastructure.security.access_control import require_any_role

record_repo = SqlAlchemyMedicalRecordRepository()
patient_repo = SqlAlchemyPatientRepository()
service = MedicalRecordService(record_repo)
audit = AuditLogger()


@records_bp.route('/<int:patient_id>')
@login_required
@require_any_role('admin', 'medico', 'enfermero')
def list_by_patient(patient_id: int):
    patient = patient_repo.get(patient_id)
    if not patient:
        flash('Paciente no encontrado')
        return redirect(url_for('patients.index'))
    records = service.list_by_patient(patient_id)
    return render_template('records/list.html', patient=patient, records=records, title='Historial Clínico')


@records_bp.route('/<int:patient_id>/add', methods=['GET', 'POST'])
@login_required
@require_any_role('admin', 'medico')
@rate_limit
def add(patient_id: int):
    patient = patient_repo.get(patient_id)
    if not patient:
        flash('Paciente no encontrado')
        return redirect(url_for('patients.index'))
    form = MedicalRecordForm()
    if form.validate_on_submit():
        ok, msg, record = service.add_entry(patient_id, form.title.data, form.notes.data)
        flash(msg)
        audit.log_action('record_add', {'patient_id': patient_id, 'success': ok})
        return redirect(url_for('records.list_by_patient', patient_id=patient_id))
    return render_template('records/form.html', form=form, patient=patient, title='Agregar Entrada')
