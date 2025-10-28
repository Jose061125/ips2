from typing import Tuple, Optional
from datetime import datetime
from ..models import Appointment
from .ports import AppointmentRepositoryPort


class AppointmentService:
    def __init__(self, repo: AppointmentRepositoryPort):
        self.repo = repo

    def schedule(self, patient_id: int, scheduled_at: datetime, reason: str | None = None) -> Tuple[bool, str, Optional[Appointment]]:
        appt = Appointment(patient_id=patient_id, scheduled_at=scheduled_at, reason=reason or "")
        self.repo.add(appt)
        return True, "Cita creada correctamente.", appt

    def cancel(self, appointment_id: int) -> Tuple[bool, str]:
        appt = self.repo.get(appointment_id)
        if not appt:
            return False, "Cita no encontrada."
        appt.status = 'cancelled'
        self.repo.update(appt)
        return True, "Cita cancelada."

    def complete(self, appointment_id: int) -> Tuple[bool, str]:
        appt = self.repo.get(appointment_id)
        if not appt:
            return False, "Cita no encontrada."
        appt.status = 'completed'
        self.repo.update(appt)
        return True, "Cita completada."

    def list(self) -> list[Appointment]:
        return self.repo.list()

    def list_by_patient(self, patient_id: int) -> list[Appointment]:
        return self.repo.list_by_patient(patient_id)
