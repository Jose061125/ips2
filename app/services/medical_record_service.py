from typing import Tuple
from ..models import MedicalRecord
from .ports import MedicalRecordRepositoryPort


class MedicalRecordService:
    def __init__(self, repo: MedicalRecordRepositoryPort):
        self.repo = repo

    def add_entry(self, patient_id: int, title: str, notes: str | None = None) -> Tuple[bool, str, MedicalRecord]:
        record = MedicalRecord(patient_id=patient_id, title=title, notes=notes or "")
        self.repo.add(record)
        return True, "Entrada agregada al historial clínico.", record

    def list_by_patient(self, patient_id: int) -> list[MedicalRecord]:
        return self.repo.list_by_patient(patient_id)
