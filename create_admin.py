from app import db, create_app
from app.models import User

app = create_app()
with app.app_context():
    db.create_all()
    admin = User(nombre="Admin", email="admin@aula.com", password="1234", rol="admin")
    db.session.add(admin)
    db.session.commit()
    print("Admin creado: admin@aula.com / 1234")
