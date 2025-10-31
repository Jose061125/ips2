from abc import ABC, abstractmethod
from typing import List, Tuple
from ..models import User, Patient, Appointment, MedicalRecord, Employee

class UserRepositoryPort(ABC):
    """
    Un puerto que define las operaciones de persistencia para los usuarios.
    El núcleo de la aplicación dependerá de esta abstracción, no de una
    implementación concreta de base de datos.
    """
    @abstractmethod
    def add(self, user: User) -> User:
        """Guarda un nuevo usuario."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        """Busca un usuario por su nombre."""
        pass


# --- IPS Ports --- #

class PatientRepositoryPort(ABC):
    @abstractmethod
    def add(self, patient: Patient) -> Patient:
        pass

    @abstractmethod
    def update(self, patient: Patient) -> Patient:
        pass

    @abstractmethod
    def delete(self, patient_id: int) -> None:
        pass

    @abstractmethod
    def get(self, patient_id: int) -> Patient | None:
        pass

    @abstractmethod
    def get_by_document(self, document: str) -> Patient | None:
        pass

    @abstractmethod
    def list(self) -> List[Patient]:
        pass

    @abstractmethod
    def search_paginated(self, q: str | None, page: int, per_page: int) -> Tuple[List[Patient], int]:
        """
        Retorna una tupla (items, total) aplicando filtro opcional por q sobre
        first_name, last_name o document y paginación (page, per_page).
        """
        pass


class AppointmentRepositoryPort(ABC):
    @abstractmethod
    def add(self, appointment: Appointment) -> Appointment:
        pass

    @abstractmethod
    def get(self, appointment_id: int) -> Appointment | None:
        pass

    @abstractmethod
    def update(self, appointment: Appointment) -> Appointment:
        pass

    @abstractmethod
    def list(self) -> List[Appointment]:
        pass

    @abstractmethod
    def list_by_patient(self, patient_id: int) -> List[Appointment]:
        pass


class MedicalRecordRepositoryPort(ABC):
    @abstractmethod
    def add(self, record: MedicalRecord) -> MedicalRecord:
        pass

    @abstractmethod
    def list_by_patient(self, patient_id: int) -> List[MedicalRecord]:
        pass


class EmployeeRepositoryPort(ABC):
    @abstractmethod
    def add(self, employee: Employee) -> Employee:
        pass

    @abstractmethod
    def update(self, employee: Employee) -> Employee:
        pass

    @abstractmethod
    def delete(self, employee_id: int) -> None:
        pass

    @abstractmethod
    def get(self, employee_id: int) -> Employee | None:
        pass

    @abstractmethod
    def get_by_document(self, document: str) -> Employee | None:
        pass

    @abstractmethod
    def list(self) -> List[Employee]:
        pass
