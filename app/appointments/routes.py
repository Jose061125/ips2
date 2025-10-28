from datetime import datetime
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import appointments_bp
from ..forms import AppointmentForm
from ..adapters.sql_appointment_repository import SqlAlchemyAppointmentRepository
from ..adapters.sql_patient_repository import SqlAlchemyPatientRepository
from ..services.appointment_service import AppointmentService
from ..infrastructure.audit.audit_log import AuditLogger
from ..infrastructure.security.rate_limiter import rate_limit
from ..infrastructure.security.access_control import require_any_role

appt_repo = SqlAlchemyAppointmentRepository()
patient_repo = SqlAlchemyPatientRepository()
service = AppointmentService(appt_repo)
audit = AuditLogger()


@appointments_bp.route('/')
@login_required
def index():
    appointments = service.list()
    return render_template('appointments/index.html', appointments=appointments, title='Citas')


@appointments_bp.route('/create', methods=['GET', 'POST'])
@login_required
@require_any_role('admin', 'recepcionista', 'medico')
@rate_limit
def create():
    form = AppointmentForm()
    # fill choices dynamically
    patients = patient_repo.list()
    form.patient_id.choices = [(p.id, f"{p.full_name()} ({p.document})") for p in patients]

    if form.validate_on_submit():
        try:
            scheduled_at = datetime.strptime(form.scheduled_at.data, '%Y-%m-%d %H:%M')
        except ValueError:
            flash('Formato de fecha inválido. Use YYYY-MM-DD HH:MM')
            return render_template('appointments/form.html', form=form, title='Agendar Cita')

        ok, msg, appt = service.schedule(
            patient_id=form.patient_id.data,
            scheduled_at=scheduled_at,
            reason=form.reason.data,
        )
        flash(msg)
        audit.log_action('appointment_create', {'patient_id': form.patient_id.data, 'success': ok})
        if ok:
            return redirect(url_for('appointments.index'))
    return render_template('appointments/form.html', form=form, title='Agendar Cita')


@appointments_bp.route('/<int:appointment_id>/cancel', methods=['POST'])
@login_required
@require_any_role('admin', 'recepcionista', 'medico')
@rate_limit
def cancel(appointment_id):
    ok, msg = service.cancel(appointment_id)
    flash(msg)
    audit.log_action('appointment_cancel', {'appointment_id': appointment_id, 'success': ok})
    return redirect(url_for('appointments.index'))
