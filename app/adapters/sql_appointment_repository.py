from typing import List
from ..services.ports import AppointmentRepositoryPort
from ..models import Appointment, db


class SqlAlchemyAppointmentRepository(AppointmentRepositoryPort):
    def add(self, appointment: Appointment) -> Appointment:
        db.session.add(appointment)
        db.session.commit()
        return appointment

    def get(self, appointment_id: int) -> Appointment | None:
        return Appointment.query.get(appointment_id)

    def update(self, appointment: Appointment) -> Appointment:
        db.session.commit()
        return appointment

    def list(self) -> List[Appointment]:
        return Appointment.query.order_by(Appointment.scheduled_at.asc()).all()

    def list_by_patient(self, patient_id: int) -> List[Appointment]:
        return Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.scheduled_at.desc()).all()
