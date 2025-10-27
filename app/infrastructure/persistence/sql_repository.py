from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime
from ...domain.ports.repositories import EmployeeRepository
from ...domain.models.employee import Employee
from flask_sqlalchemy import SQLAlchemy
import logging

# Initialize SQLAlchemy and logger
db = SQLAlchemy()
logger = logging.getLogger(__name__)

class EmployeeModel(db.Model):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    document = Column(String(20), unique=True)
    position = Column(String(100))
    created_at = Column(DateTime, nullable=False)

class SQLEmployeeRepository(EmployeeRepository):
    """Implementación SQLAlchemy del EmployeeRepository"""

    def save(self, employee: Employee) -> Employee:
        db_employee = EmployeeModel(
            name=employee.name,
            document=employee.document,
            position=employee.position,
            created_at=employee.created_at
        )
        db.session.add(db_employee)
        db.session.commit()
        employee.id = db_employee.id
        return employee

    def find_by_id(self, id: int) -> Optional[Employee]:
        db_employee = EmployeeModel.query.get(id)
        if not db_employee:
            return None
        return self._to_domain(db_employee)

    def find_all(self) -> List[Employee]:
        return [self._to_domain(emp) for emp in EmployeeModel.query.all()]

    def find_by_document(self, document: str) -> Optional[Employee]:
        db_employee = EmployeeModel.query.filter_by(document=document).first()
        if not db_employee:
            return None
        return self._to_domain(db_employee)

    def audit_action(self, employee_id: int, action: str) -> None:
        logger.info(f"Employee {employee_id} performed action: {action}")

    def _to_domain(self, db_employee: EmployeeModel) -> Employee:
        """Helper method to convert DB model to domain entity"""
        return Employee(
            id=db_employee.id,
            name=db_employee.name,
            document=db_employee.document,
            position=db_employee.position,
            created_at=db_employee.created_at
        )