from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    # Campo de email para compatibilidad con tests y formularios
    email = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(50), default='recepcionista', nullable=False)  # admin, medico, recepcionista, enfermero
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        """
        Set user password with validation.
        ISO 27001: A.9.4.3 - Password management
        
        Args:
            password (str): Plain text password
        
        Raises:
            ValueError: If password doesn't meet requirements
        """
        if len(password) < 8:
            # Mensaje en español para alinear con tests (contiene 'menos de 8')
            raise ValueError("La contraseña no puede tener menos de 8 caracteres")

        # Forzar algoritmo pbkdf2:sha256 para alinear con tests
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role"""
        return self.role == role
    
    def has_any_role(self, *roles) -> bool:
        """Check if user has any of the specified roles"""
        return self.role in roles
    
    def is_locked(self) -> bool:
        """Check if account is locked"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def reset_failed_attempts(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def increment_failed_attempts(self, lockout_duration_minutes: int = 15, max_attempts: int = 5):
        """Increment failed login attempts and lock account if threshold reached"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=lockout_duration_minutes)


# --- IPS Core Models --- #

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    document = db.Column(db.String(20), unique=True, nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    appointments = db.relationship('Appointment', backref='patient', lazy=True, cascade="all, delete-orphan")
    records = db.relationship('MedicalRecord', backref='patient', lazy=True, cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        # Permitir aliases en español para compatibilidad con tests
        if 'nombre' in kwargs:
            # Asumimos que 'nombre' contiene el nombre completo o solo first_name
            nombre = kwargs.pop('nombre')
            if ' ' in nombre:
                parts = nombre.split(' ', 1)
                kwargs['first_name'] = parts[0]
                kwargs['last_name'] = parts[1]
            else:
                kwargs['first_name'] = nombre
                kwargs.setdefault('last_name', '')
        
        if 'documento' in kwargs:
            kwargs['document'] = kwargs.pop('documento')
        
        if 'fecha_nacimiento' in kwargs:
            fn = kwargs.pop('fecha_nacimiento')
            # Convertir string a date si es necesario
            if isinstance(fn, str):
                try:
                    kwargs['birth_date'] = datetime.strptime(fn, '%Y-%m-%d').date()
                except ValueError:
                    kwargs['birth_date'] = None
            else:
                kwargs['birth_date'] = fn
        
        if 'direccion' in kwargs:
            kwargs['address'] = kwargs.pop('direccion')
        
        if 'telefono' in kwargs:
            kwargs['phone'] = kwargs.pop('telefono')
        
        super(Patient, self).__init__(**kwargs)

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __init__(self, **kwargs):
        """
        Acepta aliases en español para compatibilidad con pruebas y formularios heredados.
        Aliases soportados:
          - nombre -> first_name
          - apellido -> last_name
          - documento -> document
          - fecha_nacimiento -> birth_date (YYYY-MM-DD)
          - telefono -> phone
          - direccion -> address
          - correo -> email
        """
        mapping = {
            'nombre': 'first_name',
            'apellido': 'last_name',
            'documento': 'document',
            'fecha_nacimiento': 'birth_date',
            'telefono': 'phone',
            'direccion': 'address',
            'correo': 'email',
        }
        # Convertir y extraer valores en español
        for es_key, en_key in list(mapping.items()):
            if es_key in kwargs and en_key not in kwargs:
                val = kwargs.pop(es_key)
                # Parseo simple de fecha si viene como str
                if en_key == 'birth_date' and isinstance(val, str):
                    try:
                        # YYYY-MM-DD
                        year, month, day = map(int, val.split('-'))
                        val = date(year, month, day)
                    except Exception:
                        pass
                kwargs[en_key] = val
        # Defaults para columnas NOT NULL si no se suministran
        kwargs.setdefault('first_name', '')
        kwargs.setdefault('last_name', '')
        super().__init__(**kwargs)


class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='scheduled', nullable=False)  # scheduled|cancelled|completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    document = db.Column(db.String(20), unique=True, nullable=False)
    position = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.Date, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
