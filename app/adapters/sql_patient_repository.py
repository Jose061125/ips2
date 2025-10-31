from typing import List, Tuple
from ..services.ports import PatientRepositoryPort
from ..models import Patient, db
from sqlalchemy import or_


class SqlAlchemyPatientRepository(PatientRepositoryPort):
    def add(self, patient: Patient) -> Patient:
        db.session.add(patient)
        db.session.commit()
        return patient

    def update(self, patient: Patient) -> Patient:
        db.session.commit()
        return patient

    def delete(self, patient_id: int) -> None:
        patient = Patient.query.get(patient_id)
        if patient:
            db.session.delete(patient)
            db.session.commit()

    def get(self, patient_id: int) -> Patient | None:
        return Patient.query.get(patient_id)

    def get_by_document(self, document: str) -> Patient | None:
        return Patient.query.filter_by(document=document).first()

    def list(self) -> List[Patient]:
        return Patient.query.order_by(Patient.created_at.desc()).all()

    def search_paginated(self, q: str | None, page: int, per_page: int) -> Tuple[List[Patient], int]:
        query = Patient.query
        if q:
            like = f"%{q}%"
            query = query.filter(
                or_(
                    Patient.first_name.ilike(like),
                    Patient.last_name.ilike(like),
                    Patient.document.ilike(like),
                )
            )
        total = query.count()
        items = (
            query.order_by(Patient.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return items, total
