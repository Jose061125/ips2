from typing import Tuple, Optional, List
from ..models import Employee
from .ports import EmployeeRepositoryPort


class EmployeeService:
    def __init__(self, employee_repository: EmployeeRepositoryPort):
        self.employee_repository = employee_repository

    def create_employee(self, first_name: str, last_name: str, document: str, 
                        position: str, hire_date=None, phone: str = None, 
                        email: str = None) -> Tuple[bool, str, Optional[Employee]]:
        """Create a new employee"""
        # Check for duplicate document
        existing = self.employee_repository.get_by_document(document)
        if existing:
            return False, f"Ya existe un empleado con el documento {document}", None

        employee = Employee(
            first_name=first_name,
            last_name=last_name,
            document=document,
            position=position,
            hire_date=hire_date,
            phone=phone,
            email=email
        )
        self.employee_repository.add(employee)
        return True, "Empleado creado exitosamente", employee

    def update_employee(self, employee_id: int, first_name: str, last_name: str,
                        document: str, position: str, hire_date=None, 
                        phone: str = None, email: str = None) -> Tuple[bool, str, Optional[Employee]]:
        """Update an existing employee"""
        employee = self.employee_repository.get(employee_id)
        if not employee:
            return False, "Empleado no encontrado", None

        # Check for duplicate document (excluding this employee)
        existing = self.employee_repository.get_by_document(document)
        if existing and existing.id != employee_id:
            return False, f"Ya existe un empleado con el documento {document}", None

        employee.first_name = first_name
        employee.last_name = last_name
        employee.document = document
        employee.position = position
        employee.hire_date = hire_date
        employee.phone = phone
        employee.email = email

        self.employee_repository.update(employee)
        return True, "Empleado actualizado exitosamente", employee

    def delete_employee(self, employee_id: int) -> Tuple[bool, str]:
        """Delete an employee"""
        employee = self.employee_repository.get(employee_id)
        if not employee:
            return False, "Empleado no encontrado"

        self.employee_repository.delete(employee_id)
        return True, f"Empleado {employee.full_name()} eliminado exitosamente"

    def get_employee(self, employee_id: int) -> Optional[Employee]:
        """Get an employee by ID"""
        return self.employee_repository.get(employee_id)

    def list_employees(self) -> List[Employee]:
        """List all employees"""
        return self.employee_repository.list()
