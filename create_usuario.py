from app import db, create_app, mail
from app.models import User
from flask_mail import Message

app = create_app()
mail.init_app(app)

with app.app_context():
    nombre = input("Nombre completo: ")
    email = input("Email: ")
    rol = input("Rol (profesor/alumno): ").lower()
    password = "1234"  # Puede generarse aleatorio

    usuario = User(nombre=nombre, email=email, password=password, rol=rol)
    db.session.add(usuario)
    db.session.commit()

    msg = Message("Tus credenciales de Aula Virtual",
                  sender=app.config["MAIL_USERNAME"],
                  recipients=[email])
    msg.body = f"""
Hola {nombre},

Has sido habilitado como {rol.upper()} en el Aula Virtual.

Email: {email}
Contraseña: {password}

Inicia sesión en http://127.0.0.1:5000/login

Saludos,
El Administrador
    """
    mail.send(msg)
    print(f"{rol.capitalize()} creado y mail enviado a {email}")
