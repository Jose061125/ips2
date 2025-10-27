from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from .models import User

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es requerido'),
        Length(min=3, max=50, message='El usuario debe tener entre 3 y 50 caracteres')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida')
    ])
    submit = SubmitField('Iniciar Sesión')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es requerido'),
        Length(min=3, max=50, message='El usuario debe tener entre 3 y 50 caracteres')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    password2 = PasswordField('Repetir Contraseña', validators=[
        DataRequired(message='Por favor repite la contraseña'),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya está en uso.')
