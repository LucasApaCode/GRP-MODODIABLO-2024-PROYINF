# app.py
import matplotlib
matplotlib.use('Agg') 
import os
import plotly.graph_objects as go
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
import cv2
import numpy as np
import pydicom
import matplotlib.pyplot as plt
from scipy.ndimage import rotate
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
        flash(
            "No te han asignado imágenes médicas aún. Contáctate con tu especialista si crees que es un error.",
            "danger",
        )
        return redirect(url_for("logout"))

    if current_user.role == "admin":
        return render_template("admin_dashboard.html")
    else:
        return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    if current_user.role != "specialist" and current_user.role != "admin":
        flash(
            "No te han asignado imágenes médicas aún. Contáctate con tu especialista si crees que es un error.",
            "danger",
        )
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

                # Extraer y guardar la imagen DICOM
                imagen = dicom_data.pixel_array
                plt.imshow(imagen, cmap=plt.cm.gray)
                plt.axis("off")
                image_filename = filename.rsplit(".", 1)[0] + ".png"
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
                plt.savefig(image_path, bbox_inches="tight", pad_inches=0)
                plt.close()

                flash("Archivo DICOM subido y procesado correctamente.", "success")
                return redirect(
                    url_for("display", filename=filename, image_filename=image_filename)
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


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/display/<filename>/<image_filename>")
@login_required
def display(filename, image_filename):
    if current_user.role != "specialist" and current_user.role != "admin":
        flash(
            "No tienes acceso a esta función. Solo los especialistas y administradores pueden ver imágenes.",
            "danger",
        )
        return redirect(url_for("logout"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    try:
        dicom_data = pydicom.dcmread(filepath)
        header = {elem.keyword: str(elem.value) for elem in dicom_data if elem.keyword}
    except Exception as e:
        flash(f"Error al procesar el archivo DICOM: {e}", "danger")
        return redirect(url_for("upload_file"))

    search_form = SearchForm()
    search_form.specific_key.choices = [("all", "Todas las Claves")] + [
        (key, key) for key in COMMON_DICOM_KEYS
    ]

    return render_template(
        "display.html",
        header=header,
        filename=filename,
        form=search_form,
        image_filename=image_filename,
    )


@app.route("/volume_view/<filename>/<image_filename>/<study_id>")
@login_required
def volume_view(filename, image_filename, study_id):
    if current_user.role != "specialist" and current_user.role != "admin":
        flash(
            "No tienes acceso a esta función. Solo los especialistas y administradores pueden ver imágenes.",
            "danger",
        )
        return redirect(url_for("logout"))

    folder_path = app.config["UPLOAD_FOLDER"]
    try:
        # Leer todos los archivos DICOM en la carpeta y filtrar por el identificador del estudio
        dicom_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.endswith(".dcm") and f"IMG-{study_id}-" in f
        ]
        dicom_files.sort()  # Ordenar los archivos si es necesario

        # Leer las imágenes DICOM y combinarlas en un volumen 3D
        slices = [pydicom.dcmread(dicom_file).pixel_array for dicom_file in dicom_files]
        volume = np.stack(slices, axis=0)

        # Guardar las imágenes de las tres vistas ortogonales
        sagittal = np.transpose(volume, (1, 0, 2))[:, :, volume.shape[2] // 2]
        coronal = np.transpose(volume, (2, 0, 1))[:, :, volume.shape[1] // 2]
        axial = volume[volume.shape[0] // 2, :, :]

        sagittal_path = os.path.join(
            app.config["UPLOAD_FOLDER"], f"sagittal_{study_id}.png"
        )
        coronal_path = os.path.join(
            app.config["UPLOAD_FOLDER"], f"coronal_{study_id}.png"
        )
        axial_path = os.path.join(app.config["UPLOAD_FOLDER"], f"axial_{study_id}.png")

        plt.imsave(sagittal_path, sagittal, cmap="gray")
        plt.imsave(coronal_path, coronal, cmap="gray")
        plt.imsave(axial_path, axial, cmap="gray")

        return render_template(
            "volume_view.html",
            sagittal_image=f"sagittal_{study_id}.png",
            coronal_image=f"coronal_{study_id}.png",
            axial_image=f"axial_{study_id}.png",
            filename=filename,
            image_filename=image_filename,
        )
    except Exception as e:
        flash(f"Error al procesar el archivo DICOM: {e}", "danger")
        return redirect(url_for("upload_file"))

@app.route("/mip_view/<filename>/<image_filename>/<study_id>", methods=["GET", "POST"])
@login_required
def mip_view(filename, image_filename, study_id):
    if current_user.role != "specialist" and current_user.role != "admin":
        flash(
            "No tienes acceso a esta función. Solo los especialistas y administradores pueden ver imágenes.",
            "danger",
        )
        return redirect(url_for("logout"))

    folder_path = app.config["UPLOAD_FOLDER"]
    rotation_angle_x = 0  # Ángulo de rotación predeterminado en X
    rotation_angle_y = 0  # Ángulo de rotación predeterminado en Y
    rotation_angle_z = 0  # Ángulo de rotación predeterminado en Z

    if request.method == "POST":
        rotation_angle_x = int(request.form.get("rotation_angle_x", 0))
        rotation_angle_y = int(request.form.get("rotation_angle_y", 0))
        rotation_angle_z = int(request.form.get("rotation_angle_z", 0))

    try:
        # Leer todos los archivos DICOM en la carpeta y filtrar por el identificador del estudio
        dicom_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.endswith(".dcm") and f"IMG-{study_id}-" in f
        ]

        # Ordenar los archivos DICOM por InstanceNumber
        dicom_files.sort(key=lambda f: pydicom.dcmread(f).InstanceNumber)

        # Leer las imágenes DICOM y combinarlas en un volumen 3D
        slices = [pydicom.dcmread(dicom_file).pixel_array for dicom_file in dicom_files]
        volume = np.stack(slices, axis=0)

        # Rotar el volumen 3D según los ángulos proporcionados
        rotated_volume = rotate(volume, angle=rotation_angle_x, axes=(1, 2), reshape=False)
        rotated_volume = rotate(rotated_volume, angle=rotation_angle_y, axes=(0, 2), reshape=False)
        rotated_volume = rotate(rotated_volume, angle=rotation_angle_z, axes=(0, 1), reshape=False)

        # Crear la imagen MIP
        mip = np.max(rotated_volume, axis=0)
        mip_path = os.path.join(folder_path, 'mip.png')
        plt.imshow(mip, cmap='gray')
        plt.axis('off')
        plt.savefig(mip_path, bbox_inches='tight', pad_inches=0)
        plt.close()

        # Crear la visualización 3D interactiva con plotly usando Volume
        fig = go.Figure(data=go.Volume(
            x=np.arange(rotated_volume.shape[0]),
            y=np.arange(rotated_volume.shape[1]),
            z=np.arange(rotated_volume.shape[2]),
            value=rotated_volume.flatten(),
            opacity=0.1,  # Opacidad del volumen
            surface_count=20,  # Número de superficies
            colorscale='Gray',  # Escala de colores para que coincida con la imagen MIP
        ))

        # Guardar la visualización interactiva como un archivo HTML
        rotation_html = os.path.join(folder_path, 'rotation.html')
        fig.write_html(rotation_html)

        flash("Reconstrucción MIP satisfactoria.", "success")
        return render_template(
            "mip_view.html",
            mip_image='mip.png',
            rotation_html='rotation.html',
            filename=filename,
            image_filename=image_filename,
            study_id=study_id,
        )
    except Exception as e:
        flash(f"Error al procesar el archivo DICOM: {e}", "danger")
        return redirect(url_for("upload_file"))

@app.route("/search", methods=["POST"])
@login_required
def search():
    if current_user.role != "specialist" and current_user.role != "admin":
        flash(
            "No te han asignado imágenes médicas aún. Contáctate con tu especialista si crees que es un error.",
            "danger",
        )
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
        return redirect(
            url_for(
                "display",
                header=filtered_header,
                filename=filename,
                search_term=search_term,
                image_filename=filename.rsplit(".", 1)[0] + ".png",
            )
        )
    except Exception as e:
        flash(f"Error al buscar en el archivo DICOM: {e}", "danger")
        return redirect(url_for("upload_file"))


@app.route(
    "/edit_image/<filename>/<image_filename>/<processed_filename>",
    methods=["GET", "POST"],
)
@login_required
def edit_image(filename, image_filename, processed_filename):
    if current_user.role != "specialist" and current_user.role != "admin":
        flash(
            "No tienes acceso a esta función. Solo los especialistas y administradores pueden editar imágenes.",
            "danger",
        )
        return redirect(url_for("logout"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
    image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)

    if request.method == "POST":
        filter_type = request.form.get("filter_type")
        color_map = request.form.get("color_map")
        # Aplicar filtro
        if filter_type == "negative":
            image = cv2.bitwise_not(image)

        # Aplicar mapa de color
        if color_map == "jet":
            image = cv2.applyColorMap(image, cv2.COLORMAP_JET)
        elif color_map == "hot":
            image = cv2.applyColorMap(image, cv2.COLORMAP_HOT)
        elif color_map == "bone":
            image = cv2.applyColorMap(image, cv2.COLORMAP_BONE)
        elif color_map == "winter":
            image = cv2.applyColorMap(image, cv2.COLORMAP_WINTER)

        # Guardar la imagen procesada
        processed_filename = f"processed_{image_filename}"
        processed_filepath = os.path.join(
            app.config["UPLOAD_FOLDER"], processed_filename
        )
        cv2.imwrite(processed_filepath, image)
        flash("Filtros aplicados correctamente.", "success")
        return redirect(
            url_for(
                "edit_image",
                filename=filename,
                image_filename=image_filename,
                processed_filename=processed_filename,
            )
        )

    return render_template(
        "edit_image.html",
        filename=filename,
        image_filename=image_filename,
        processed_filename=processed_filename,
    )


@app.route(
    "/medir/<filename>/<image_filename>/<processed_filename>",
    methods=["GET", "POST"],
)
@login_required
def medir(filename, image_filename, processed_filename):
    if current_user.role != "specialist" and current_user.role != "admin":
        flash(
            "No tienes acceso a esta función. Solo los especialistas y administradores pueden editar imágenes.",
            "danger",
        )
        return redirect(url_for("logout"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
    image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)

    if request.method == "POST":
        # Guardar la imagen procesada
        processed_filename = f"processed_{image_filename}"
        processed_filepath = os.path.join(
            app.config["UPLOAD_FOLDER"], processed_filename
        )
        cv2.imwrite(processed_filepath, image)
        flash("Medición aplicada correctamente.", "success")
        return redirect(
            url_for(
                "medir",
                filename=filename,
                image_filename=image_filename,
                processed_filename=processed_filename,
            )
        )

    return render_template(
        "medir.html",
        filename=filename,
        image_filename=image_filename,
        processed_filename=processed_filename,
    )

# Función para calcular la distancia entre dos puntos
def calculate_distance(point1, point2):
    distance = np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    return distance

# Función para medir el área de un polígono
def calculate_polygon_area(points):
    contour = np.array(points, dtype=np.int32)
    area = cv2.contourArea(contour)
    return area



# Ruta para realizar la medición (línea, polígono)
@app.route('/measure', methods=['POST'])
def measure():
    data = request.json
    measure_type = data.get('type')
    points = data.get('points')
    
    if measure_type == 'line':
        point1, point2 = points
        distance = calculate_distance(point1, point2)
        return jsonify({'measurement': distance, 'units': 'pixels'})
    
    elif measure_type == 'polygon':
        area = calculate_polygon_area(points)
        return jsonify({'measurement': area, 'units': 'pixels²'})
    
    return jsonify({'status': 'failed', 'message': 'Measurement type not supported'})


@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash(
            "Acceso denegado. Solo los administradores pueden acceder a esta función.",
            "danger",
        )
        return redirect(url_for("logout"))
    return render_template("admin_dashboard.html")


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
        new_user.set_password(form.password.data)
        new_user.set_email(form.email.data)
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
        if user and user.check_password(form.password.data) and user.role != "patient":
            login_user(user)
            flash("Inicio de sesión exitoso.", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        elif user.role != "patient":
            flash("Nombre de usuario o contraseña inválidos.", "danger")
        else:
            flash(
                "No te han asignado imágenes médicas aún. Contáctate con tu especialista si crees que es un error.",
                "danger",
            )
    return render_template("login.html", form=form)


@app.route("/advanced_search", methods=["POST"])
@login_required
def advanced_search():
    if current_user.role != "specialist" and current_user.role != "admin":
        flash(
            "No te han asignado imágenes médicas aún. Contáctate con tu especialista si crees que es un error.",
            "danger",
        )
        return redirect(url_for("logout"))

    form = SearchForm()
    form.specific_key.choices = [("all", "Todas las Claves")] + [
        (key, key) for key in COMMON_DICOM_KEYS
    ]

    if form.validate_on_submit():
        search_term = form.search_term.data.lower()
        specific_key = form.specific_key.data
        data_type = form.data_type.data
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
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return render_template(
                    "partials/_dicom_header_table.html",
                    header=filtered_header,
                    filename=filename,
                    image_filename=filename.rsplit(".", 1)[0] + ".png",
                )
            else:
                return render_template("display.html", header=header)
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
    app.run(debug=False)
