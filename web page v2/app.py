# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
import pydicom
from werkzeug.utils import secure_filename
from models import db, User
from forms import SignupForm, LoginForm, SearchForm, SignupFormEspecialist

COMMON_DICOM_KEYS = [
    "PatientName",
    "PatientID",
    "StudyDate",
    "Modality",
    "Manufacturer",
    "InstitutionName",
    "SeriesDescription",
    "SliceThickness",
    "PixelSpacing",
    "ImageType",
    "Rows",
    "Columns",
    # Añadir más claves si es necesario
]

app = Flask(__name__)
app.secret_key = "tu_clave_secreta"  # Cambia esto por una clave segura

# Configuración de la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar la base de datos
db.init_app(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = ""  # Sin mensaje por defecto
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Configuración de la carpeta de subida y extensiones permitidas
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"dcm"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
@login_required
def index():
    if current_user.role != "specialist" and current_user.role != "admin":
        flash("Acceso restringido solo a especialistas médicos.", "danger")
        return redirect(url_for("logout"))

    if current_user.role == "admin":
        return render_template("admin_dashboard.html")
    else:
        return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    if current_user.role != "specialist" and current_user.role != "admin":
        flash("Acceso restringido solo a especialistas médicos.", "danger")
        return redirect(url_for("logout"))

    if request.method == "POST":
        # Verificar si se ha enviado un archivo
        if "file" not in request.files:
            flash("No se ha seleccionado ningún archivo.", "warning")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No se ha seleccionado ningún archivo.", "warning")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            try:
                dicom_data = pydicom.dcmread(filepath)
                header = {
                    elem.keyword: str(elem.value) for elem in dicom_data if elem.keyword
                }
                flash("Archivo DICOM subido y procesado correctamente.", "success")
                search_form = SearchForm()
                search_form.specific_key.choices = [("all", "Todas las Claves")] + [
                    (key, key) for key in COMMON_DICOM_KEYS
                ]
                return render_template(
                    "display.html", header=header, filename=filename, form=search_form
                )
            except Exception as e:
                flash(f"Error al procesar el archivo DICOM: {e}", "danger")
                return redirect(request.url)
        else:
            flash(
                "Tipo de archivo no permitido. Por favor, sube un archivo .dcm",
                "warning",
            )
            return redirect(request.url)
    return render_template("upload.html")


def admin_dashboard():
    return render_template("admin_dashboard.html")


@app.route("/search", methods=["POST"])
@login_required
def search():
    if current_user.role != "specialist" and current_user.role != "admin":
        flash("Acceso restringido solo a especialistas médicos.", "danger")
        return redirect(url_for("logout"))

    search_term = request.form.get("search_term", "").lower()
    filename = request.form.get("filename")
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    try:
        dicom_data = pydicom.dcmread(filepath)
        header = {elem.keyword: str(elem.value) for elem in dicom_data if elem.keyword}
        # Filtrar los datos según el término de búsqueda
        filtered_header = {
            k: v
            for k, v in header.items()
            if search_term in k.lower() or search_term in v.lower()
        }
        flash("Búsqueda completada.", "info")
        return render_template(
            "display.html",
            header=filtered_header,
            filename=filename,
            search_term=search_term,
        )
    except Exception as e:
        flash(f"Error al buscar en el archivo DICOM: {e}", "danger")
        return redirect(url_for("upload_file"))


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if (
        not current_user.is_authenticated
        and current_user.role != "admin"
        and current_user.role != "specialist"
    ):
        flash(
            "Acceso denegado. Solo los administradores y especialistas pueden registrar nuevos usuarios.",
            "danger",
        )
        return redirect(url_for("login"))

    if current_user.role == "admin":
        form = SignupForm()
    elif current_user.role == "specialist":
        form = SignupFormEspecialist()

    if form.validate_on_submit():
        new_user = User(username=form.username.data, role=form.role.data)
        new_user.set_email(form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("¡Registro exitoso!", "success")
    return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("Ya has iniciado sesión.", "info")
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Inicio de sesión exitoso.", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash("Nombre de usuario o contraseña inválidos.", "danger")
    return render_template("login.html", form=form)


@app.route("/advanced_search", methods=["POST"])
@login_required
def advanced_search():
    if current_user.role != "specialist" and current_user.role != "admin":
        flash("Acceso restringido solo a especialistas médicos.", "danger")
        return redirect(url_for("logout"))

    form = SearchForm()
    form.specific_key.choices = [("all", "Todas las Claves")] + [
        (key, key) for key in COMMON_DICOM_KEYS
    ]

    if form.validate_on_submit():
        search_term = form.search_term.data.lower()
        specific_key = form.specific_key.data
        data_type = form.data_type.data
        min_value = form.min_value.data
        max_value = form.max_value.data
        filename = request.form.get("filename")
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        try:
            dicom_data = pydicom.dcmread(filepath)
            header = {
                elem.keyword: str(elem.value) for elem in dicom_data if elem.keyword
            }

            # Aplicar filtros
            filtered_header = {}
            for key, value in header.items():
                # Filtrar por clave específica
                if specific_key != "all" and key != specific_key:
                    continue

                # Filtrar por tipo de dato
                if data_type != "all":
                    # Determinar el tipo de dato del valor
                    try:
                        if data_type == "Str" and not isinstance(value, str):
                            continue
                        elif data_type == "Int":
                            int(value)
                        elif data_type == "Float":
                            float(value)
                        elif data_type == "Date":
                            # pydicom maneja fechas como strings, por simplicidad
                            pass
                        elif data_type == "Time":
                            # pydicom maneja tiempos como strings, por simplicidad
                            pass
                    except ValueError:
                        continue

                # Filtrar por rango de valores (solo para tipos numéricos)
                if data_type in ["Int", "Float"]:
                    try:
                        numeric_value = float(value)
                        if min_value is not None and numeric_value < min_value:
                            continue
                        if max_value is not None and numeric_value > max_value:
                            continue
                    except ValueError:
                        continue

                # Filtrar por término de búsqueda en clave o valor
                if search_term:
                    if (
                        search_term not in key.lower()
                        and search_term not in value.lower()
                    ):
                        continue

                # Si pasa todos los filtros, añadir al diccionario filtrado
                filtered_header[key] = value

            flash("Búsqueda avanzada completada.", "info")
            search_form = SearchForm()
            search_form.specific_key.choices = [("all", "Todas las Claves")] + [
                (key, key) for key in COMMON_DICOM_KEYS
            ]
            return render_template(
                "display.html",
                header=filtered_header,
                filename=filename,
                form=search_form,
            )
        except Exception as e:
            flash(f"Error al realizar la búsqueda avanzada: {e}", "danger")
            return redirect(url_for("upload_file"))

    flash("Formulario de búsqueda inválido.", "danger")
    return redirect(url_for("upload_file"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
