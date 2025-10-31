"""
Script de profiling de memoria
===============================

Identifica funciones y operaciones que consumen más memoria.

Ejecutar:
    python -m memory_profiler scripts/profile_memory.py
    
Requisitos:
    pip install memory-profiler
"""

from memory_profiler import profile
import sys
import os

# Agregar app al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app import create_app, db
from app.models import Patient, Employee, Appointment
from datetime import datetime, timedelta


@profile
def create_many_patients(n=1000):
    """Crear muchos pacientes para testear consumo de memoria"""
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    
    with app.app_context():
        db.create_all()
        
        print(f"Creando {n} pacientes...")
        patients = []
        for i in range(n):
            patient = Patient(
                nombre=f'Patient {i}',
                documento=f'DOC{i:06d}',
                fecha_nacimiento=datetime(1980, 1, 1) + timedelta(days=i),
                direccion=f'Address {i}',
                telefono='1234567890'
            )
            patients.append(patient)
            
            # Commit en batches para evitar memory overflow
            if i % 100 == 0 and i > 0:
                db.session.bulk_save_objects(patients)
                db.session.commit()
                patients.clear()
        
        # Commit final
        if patients:
            db.session.bulk_save_objects(patients)
            db.session.commit()
        
        print(f"✅ {n} pacientes creados")


@profile
def query_with_relationships():
    """Query con relaciones que puede consumir mucha memoria"""
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    
    with app.app_context():
        db.create_all()
        
        # Crear datos
        for i in range(100):
            patient = Patient(
                nombre=f'Patient {i}',
                documento=f'DOC{i:03d}',
                fecha_nacimiento=datetime(1990, 1, 1),
                direccion='Test',
                telefono='1234567890'
            )
            db.session.add(patient)
        
        for i in range(50):
            employee = Employee(
                nombre=f'Employee {i}',
                documento=f'EMP{i:03d}',
                especialidad='Test',
                telefono='1234567890'
            )
            db.session.add(employee)
        
        db.session.commit()
        
        # Query con JOINs
        print("Ejecutando query con JOINs...")
        patients = Patient.query.all()
        
        # Acceder a relaciones (puede triggear N+1)
        for patient in patients:
            _ = patient.appointments
        
        print(f"✅ Query completada: {len(patients)} pacientes")


@profile
def convert_to_dicts():
    """Convertir muchos objetos a diccionarios (serialización)"""
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    
    with app.app_context():
        db.create_all()
        
        # Crear pacientes
        for i in range(500):
            patient = Patient(
                nombre=f'Patient {i}',
                documento=f'DOC{i:04d}',
                fecha_nacimiento=datetime(1985, 1, 1),
                direccion='Test',
                telefono='1234567890'
            )
            db.session.add(patient)
        
        db.session.commit()
        
        # Convertir a dict
        print("Convirtiendo a diccionarios...")
        patients = Patient.query.all()
        patients_dicts = []
        
        for patient in patients:
            patient_dict = {
                'id': patient.id,
                'nombre': patient.nombre,
                'documento': patient.documento,
                'fecha_nacimiento': str(patient.fecha_nacimiento),
                'direccion': patient.direccion,
                'telefono': patient.telefono
            }
            patients_dicts.append(patient_dict)
        
        print(f"✅ {len(patients_dicts)} diccionarios creados")


if __name__ == '__main__':
    print("=" * 60)
    print("PROFILING DE MEMORIA - IPS System")
    print("=" * 60)
    print()
    
    print("Test 1: Crear muchos pacientes")
    print("-" * 60)
    create_many_patients(n=1000)
    print()
    
    print("Test 2: Queries con relaciones")
    print("-" * 60)
    query_with_relationships()
    print()
    
    print("Test 3: Serialización a diccionarios")
    print("-" * 60)
    convert_to_dicts()
    print()
    
    print("=" * 60)
    print("✅ Profiling completado")
    print("=" * 60)
