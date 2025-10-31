from typing import Tuple, Optional, List
from ..models import Patient
from .ports import PatientRepositoryPort


class PatientService:
    def __init__(self, repo: PatientRepositoryPort):
        self.repo = repo

    def create(self, first_name: str, last_name: str, document: str, **kwargs) -> Tuple[bool, str, Optional[Patient]]:
        if self.repo.get_by_document(document):
            return False, "El documento ya existe.", None
        patient = Patient(
            first_name=first_name,
            last_name=last_name,
            document=document,
            birth_date=kwargs.get("birth_date"),
            phone=kwargs.get("phone"),
            email=kwargs.get("email"),
            address=kwargs.get("address"),
        )
        self.repo.add(patient)
        return True, "Paciente creado correctamente.", patient

    def update(self, patient_id: int, **kwargs) -> Tuple[bool, str, Optional[Patient]]:
        patient = self.repo.get(patient_id)
        if not patient:
            return False, "Paciente no encontrado.", None
        for field in ["first_name","last_name","document","birth_date","phone","email","address"]:
            if field in kwargs and kwargs[field] is not None:
                setattr(patient, field, kwargs[field])
        self.repo.update(patient)
        return True, "Paciente actualizado correctamente.", patient

    def delete(self, patient_id: int) -> Tuple[bool, str]:
        patient = self.repo.get(patient_id)
        if not patient:
            return False, "Paciente no encontrado."
        self.repo.delete(patient_id)
        return True, "Paciente eliminado correctamente."

    def get(self, patient_id: int) -> Optional[Patient]:
        return self.repo.get(patient_id)

    def list(self) -> List[Patient]:
        return self.repo.list()

    def list_paginated(self, q: str | None, page: int, per_page: int) -> Tuple[List[Patient], int]:
        q = (q or "").strip()
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10
        return self.repo.search_paginated(q or None, page, per_page)
