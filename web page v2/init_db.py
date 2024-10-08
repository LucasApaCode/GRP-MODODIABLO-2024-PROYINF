# init_db.py
from app import app
from models import db, User

with app.app_context():
    db.create_all()

    # Verificar si ya existe un admin
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", role="admin")
        admin.set_email("admin@gmail.com")
        admin.set_password("admin")  # Cambia esto a una contraseña segura
        db.session.add(admin)
        db.session.commit()
        print("Administrador creado.")
    else:
        print("El administrador ya existe.")
