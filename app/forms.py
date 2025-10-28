from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Optional
from .models import User, Patient

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es requerido'),
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida')
    ])
    submit = SubmitField('Iniciar Sesión')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es requerido'),
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida'),
    ])
    password2 = PasswordField('Repetir Contraseña', validators=[
        DataRequired(message='Por favor repite la contraseña'),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    role = SelectField('Rol', choices=[
        ('recepcionista', 'Recepcionista'),
        ('enfermero', 'Enfermero'),
        ('medico', 'Médico'),
        ('admin', 'Administrador')
    ], default='recepcionista')
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya está en uso.')


class UserManagementForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(message='El usuario es requerido')])
    role = SelectField('Rol', choices=[
        ('recepcionista', 'Recepcionista'),
        ('enfermero', 'Enfermero'),
        ('medico', 'Médico'),
        ('admin', 'Administrador')
    ], validators=[DataRequired()])
    submit = SubmitField('Guardar')


class PatientForm(FlaskForm):
    first_name = StringField('Nombre', validators=[DataRequired(message='El nombre es requerido')])
    last_name = StringField('Apellido', validators=[DataRequired(message='El apellido es requerido')])
    document = StringField('Documento', validators=[DataRequired(message='El documento es requerido')])
    birth_date = DateField('Fecha de nacimiento', validators=[Optional()])
    phone = StringField('Teléfono', validators=[Optional()])
    email = StringField('Email', validators=[Optional()])
    address = StringField('Dirección', validators=[Optional()])
    submit = SubmitField('Guardar')


class AppointmentForm(FlaskForm):
    patient_id = SelectField('Paciente', coerce=int, validators=[DataRequired(message='Seleccione un paciente')])
    scheduled_at = StringField('Fecha y hora (YYYY-MM-DD HH:MM)', validators=[DataRequired(message='La fecha es requerida')])
    reason = StringField('Motivo', validators=[Optional()])
    submit = SubmitField('Agendar')


class MedicalRecordForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(message='El título es requerido')])
    notes = TextAreaField('Notas', validators=[Optional()])
    submit = SubmitField('Agregar')


class EmployeeForm(FlaskForm):
    first_name = StringField('Nombre', validators=[DataRequired(message='El nombre es requerido')])
    last_name = StringField('Apellido', validators=[DataRequired(message='El apellido es requerido')])
    document = StringField('Documento', validators=[DataRequired(message='El documento es requerido')])
    position = StringField('Cargo', validators=[DataRequired(message='El cargo es requerido')])
    hire_date = DateField('Fecha de contratación', validators=[Optional()])
    phone = StringField('Teléfono', validators=[Optional()])
    email = StringField('Email', validators=[Optional()])
    submit = SubmitField('Guardar')
