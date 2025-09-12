# models.py
from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    rol = db.Column(db.String(50))  # admin, profesor, alumno
    cursos = db.relationship("Curso", backref="profesor", lazy=True)


class Archivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    ruta = db.Column(db.String(255), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey("curso.id"), nullable=False)


class Examen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey("curso.id"), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)

    preguntas = db.relationship("Pregunta", backref="examen", lazy=True)

class Pregunta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    examen_id = db.Column(db.Integer, db.ForeignKey("examen.id"), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # 'abierta' o 'multiple'

    opciones = db.relationship("Opcion", backref="pregunta", lazy=True)

class Opcion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pregunta_id = db.Column(db.Integer, db.ForeignKey("pregunta.id"), nullable=False)
    texto = db.Column(db.String(255), nullable=False)
    es_correcta = db.Column(db.Boolean, default=False)

class RespuestaAlumno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey("pregunta.id"), nullable=False)
    respuesta_texto = db.Column(db.String, nullable=True)
    respuesta_opciones = db.Column(db.String, nullable=True)

curso_alumno = db.Table(
    "curso_alumno",
    db.Column("curso_id", db.Integer, db.ForeignKey("curso.id"), primary_key=True),
    db.Column("alumno_id", db.Integer, db.ForeignKey("user.id"), primary_key=True)
)
class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    profesor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    archivos = db.relationship("Archivo", backref="curso", lazy=True)
    examenes = db.relationship("Examen", backref="curso", lazy=True)

    # Relación muchos a muchos alumnos-cursos
    alumnos = db.relationship(
        "User",
        secondary=curso_alumno,
        backref="cursos_inscriptos",
        lazy="dynamic"
    )

    def __repr__(self):
        return f"<Curso {self.nombre}>"