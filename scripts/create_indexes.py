"""
Script para crear índices en la base de datos
==============================================

Mejora el rendimiento de queries comunes agregando índices estratégicos.

Ejecutar:
    python scripts/create_indexes.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app import create_app, db


def create_indexes():
    """Crea índices estratégicos en las tablas principales"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("CREANDO ÍNDICES DE BASE DE DATOS")
        print("=" * 60)
        print()
        
        indexes = [
            # User table
            ("idx_user_username", "user", "username"),
            ("idx_user_email", "user", "email"),
            
            # Patients table
            ("idx_patient_documento", "patients", "documento"),
            ("idx_patient_nombre", "patients", "nombre"),
            
            # Employees table
            ("idx_employee_documento", "employees", "documento"),
            ("idx_employee_nombre", "employees", "nombre"),
            ("idx_employee_especialidad", "employees", "especialidad"),
            
            # Appointments table
            ("idx_appointment_patient", "appointments", "patient_id"),
            ("idx_appointment_employee", "appointments", "employee_id"),
            ("idx_appointment_date", "appointments", "scheduled_at"),
            ("idx_appointment_estado", "appointments", "estado"),
            
            # Medical Records table
            ("idx_medical_record_patient", "medical_records", "patient_id"),
            ("idx_medical_record_employee", "medical_records", "employee_id"),
            ("idx_medical_record_date", "medical_records", "fecha_registro"),
        ]
        
        created = 0
        skipped = 0
        
        for idx_name, table_name, column_name in indexes:
            try:
                sql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({column_name})"
                db.session.execute(db.text(sql))
                print(f"✅ Creado: {idx_name} en {table_name}({column_name})")
                created += 1
            except Exception as e:
                print(f"⚠️  Omitido: {idx_name} - {str(e)}")
                skipped += 1
        
        db.session.commit()
        
        print()
        print("=" * 60)
        print(f"✅ Proceso completado")
        print(f"   Índices creados: {created}")
        print(f"   Índices omitidos: {skipped}")
        print("=" * 60)


def analyze_indexes():
    """Analiza los índices existentes en la base de datos"""
    app = create_app()
    
    with app.app_context():
        print()
        print("=" * 60)
        print("ÍNDICES EXISTENTES")
        print("=" * 60)
        print()
        
        # Query para SQLite
        result = db.session.execute(db.text("""
            SELECT 
                m.name as table_name,
                il.name as index_name,
                GROUP_CONCAT(ii.name, ', ') as columns
            FROM sqlite_master m
            JOIN pragma_index_list(m.name) il
            JOIN pragma_index_info(il.name) ii
            WHERE m.type = 'table'
            GROUP BY m.name, il.name
            ORDER BY m.name, il.name
        """))
        
        current_table = None
        for row in result:
            table_name, index_name, columns = row
            
            if table_name != current_table:
                print(f"\n📋 Tabla: {table_name}")
                print("-" * 60)
                current_table = table_name
            
            print(f"   🔍 {index_name}: {columns}")
        
        print()


def estimate_query_improvements():
    """Estima mejoras de rendimiento con los índices"""
    app = create_app()
    
    with app.app_context():
        print()
        print("=" * 60)
        print("ESTIMACIÓN DE MEJORAS")
        print("=" * 60)
        print()
        
        # Contar registros para estimar impacto
        from app.models import Patient, Employee, Appointment
        
        patient_count = Patient.query.count()
        employee_count = Employee.query.count()
        appointment_count = Appointment.query.count()
        
        print(f"📊 Registros actuales:")
        print(f"   - Pacientes: {patient_count}")
        print(f"   - Empleados: {employee_count}")
        print(f"   - Citas: {appointment_count}")
        print()
        
        print(f"⚡ Impacto estimado de índices:")
        print(f"   - Búsqueda por documento: ~{max(2, patient_count // 100)}x más rápido")
        print(f"   - Filtrado de citas por paciente: ~{max(2, appointment_count // 50)}x más rápido")
        print(f"   - Búsqueda por nombre: ~{max(2, patient_count // 100)}x más rápido")
        print()


if __name__ == '__main__':
    print()
    create_indexes()
    analyze_indexes()
    estimate_query_improvements()
    
    print("=" * 60)
    print("💡 RECOMENDACIONES")
    print("=" * 60)
    print("""
    1. Los índices mejoran SELECT/WHERE/JOIN pero ralentizan INSERT/UPDATE
    2. Monitorear uso con: EXPLAIN QUERY PLAN SELECT ...
    3. Revisar índices periódicamente según patrones de uso
    4. Considerar índices compuestos para queries complejas
    """)
    print("=" * 60)
