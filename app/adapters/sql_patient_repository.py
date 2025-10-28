from ..services.ports import PatientRepositoryPort
from ..models import Patient, db


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

    def list(self) -> list[Patient]:
        return Patient.query.order_by(Patient.created_at.desc()).all()
