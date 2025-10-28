from ..services.ports import MedicalRecordRepositoryPort
from ..models import MedicalRecord, db


class SqlAlchemyMedicalRecordRepository(MedicalRecordRepositoryPort):
    def add(self, record: MedicalRecord) -> MedicalRecord:
        db.session.add(record)
        db.session.commit()
        return record

    def list_by_patient(self, patient_id: int) -> list[MedicalRecord]:
        return MedicalRecord.query.filter_by(patient_id=patient_id).order_by(MedicalRecord.created_at.desc()).all()
