# forms.py
import hashlib
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional
from models import User


class SignupForm(FlaskForm):
    username = StringField("Nombre de Usuario", validators=[DataRequired()])
    email = StringField("Correo Electrónico", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirmar Contraseña", validators=[DataRequired(), EqualTo("password")]
    )
    role = SelectField(
        "Rol",
        choices=[("specialist", "Especialista Médico"), ("patient", "Paciente")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Registrarse")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "Este nombre de usuario ya está en uso. Por favor, elige otro."
            )

    def validate_email(self, email):
        user = User.query.filter_by(
            email_hash=hashlib.sha256(email.data.encode()).hexdigest()
        ).first()
        if user:
            raise ValidationError("Este correo electrónico ya está registrado.")


class SignupFormEspecialist(FlaskForm):
    username = StringField("Nombre de Usuario", validators=[DataRequired()])
    email = StringField("Correo Electrónico", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirmar Contraseña", validators=[DataRequired(), EqualTo("password")]
    )
    role = SelectField(
        "Rol",
        choices=[("patient", "Paciente")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Registrarse")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "Este nombre de usuario ya está en uso. Por favor, elige otro."
            )

    def validate_email(self, email):
        user = User.query.filter_by(
            email_hash=hashlib.sha256(email.data.encode()).hexdigest()
        ).first()
        if user:
            raise ValidationError("Este correo electrónico ya está registrado.")


class LoginForm(FlaskForm):
    username = StringField("Nombre de Usuario", validators=[DataRequired()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Iniciar Sesión")


class SearchForm(FlaskForm):
    search_term = StringField("Término de Búsqueda", validators=[Optional()])
    specific_key = SelectField("Clave Específica", choices=[], validators=[Optional()])
    data_type = SelectField(
        "Tipo de Dato",
        choices=[
            ("all", "Todos"),
            ("Str", "String"),
            ("Int", "Entero"),
            ("Float", "Flotante"),
            ("Date", "Fecha"),
            ("Time", "Hora"),
            # Añade más tipos de datos según sea necesario
        ],
        default="all",
    )
    min_value = FloatField("Valor Mínimo", validators=[Optional()])
    max_value = FloatField("Valor Máximo", validators=[Optional()])
    submit = SubmitField("Buscar")
