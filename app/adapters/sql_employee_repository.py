from typing import List
from ..models import Employee, db
from ..services.ports import EmployeeRepositoryPort


class SqlAlchemyEmployeeRepository(EmployeeRepositoryPort):
    """SQLAlchemy implementation of EmployeeRepositoryPort"""

    def add(self, employee: Employee) -> Employee:
        db.session.add(employee)
        db.session.commit()
        return employee

    def update(self, employee: Employee) -> Employee:
        db.session.commit()
        return employee

    def delete(self, employee_id: int) -> None:
        employee = self.get(employee_id)
        if employee:
            db.session.delete(employee)
            db.session.commit()

    def get(self, employee_id: int) -> Employee | None:
        return Employee.query.get(employee_id)

    def get_by_document(self, document: str) -> Employee | None:
        return Employee.query.filter_by(document=document).first()

    def list(self) -> List[Employee]:
        return Employee.query.order_by(Employee.last_name, Employee.first_name).all()
