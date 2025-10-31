"""
Script para inicializar la base de datos con esquema correcto y datos de prueba
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, User, Patient
from datetime import date

def init_database():
    """Inicializar base de datos con esquema y datos de prueba"""
    app = create_app()
    
    with app.app_context():
        # Eliminar todas las tablas
        print("🗑️  Eliminando tablas existentes...")
        db.drop_all()
        
        # Crear todas las tablas con esquema actualizado
        print("🔨 Creando tablas con esquema actualizado...")
        db.create_all()
        
        # Crear usuarios de prueba
        print("👤 Creando usuarios de prueba...")
        
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        medico = User(username='doctor', role='medico')
        medico.set_password('doctor123')
        db.session.add(medico)
        
        enfermero = User(username='nurse', role='enfermero')
        enfermero.set_password('nurse123')
        db.session.add(enfermero)
        
        recepcionista = User(username='reception', role='recepcionista')
        recepcionista.set_password('reception123')
        db.session.add(recepcionista)
        
        # Crear pacientes de prueba
        print("🏥 Creando pacientes de prueba...")
        
        patient1 = Patient(
            first_name='Juan',
            last_name='Pérez García',
            document='1234567890',
            birth_date=date(1985, 5, 15),
            address='Calle Principal #123',
            phone='3001234567'
        )
        db.session.add(patient1)
        
        patient2 = Patient(
            first_name='María',
            last_name='González López',
            document='9876543210',
            birth_date=date(1990, 8, 20),
            address='Avenida Central #456',
            phone='3009876543'
        )
        db.session.add(patient2)
        
        patient3 = Patient(
            first_name='Carlos',
            last_name='Rodríguez Martínez',
            document='5555555555',
            birth_date=date(1978, 3, 10),
            address='Carrera 10 #25-30',
            phone='3005555555'
        )
        db.session.add(patient3)
        
        # Guardar cambios
        db.session.commit()
        
        print("\n✅ Base de datos inicializada correctamente!")
        print("\n📋 Usuarios creados:")
        print("   - admin / admin123 (Administrador)")
        print("   - doctor / doctor123 (Médico)")
        print("   - nurse / nurse123 (Enfermero)")
        print("   - reception / reception123 (Recepcionista)")
        print("\n🏥 Pacientes creados: 3")
        print("\n🚀 Ahora puedes iniciar la aplicación con: python run.py")

if __name__ == '__main__':
    init_database()
