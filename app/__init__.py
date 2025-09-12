from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate  

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()  

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)  

    login_manager.login_view = "main.login"

    from . import routes, models   
    app.register_blueprint(routes.main)

    return app
