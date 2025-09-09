import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecretkey"
    SQLALCHEMY_DATABASE_URI = "sqlite:///aula_virtual.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de correo con Gmail
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "monitozombie0@gmail.com"  # tu cuenta de Gmail del sistema
    MAIL_PASSWORD = "iohm eetd wijd xxdu "      # contraseña de aplicación de Gmail
    MAIL_DEFAULT_SENDER = "monitozombie0@gmail.com"
