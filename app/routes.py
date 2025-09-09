from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Curso
from . import db, login_manager

main = Blueprint("main", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------------
# DASHBOARD ADMIN
# ------------------------
@main.route("/admin/crear_usuario", methods=["GET", "POST"])
@login_required
def crear_usuario():
    if current_user.rol != "admin":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        rol = request.form.get("rol")  # "profesor" o "alumno"

        # Validar que no exista ya ese correo
        if User.query.filter_by(email=email).first():
            flash("El email ya está registrado.", "warning")
        else:
            nuevo_usuario = User(nombre=nombre, email=email, password=password, rol=rol)
            db.session.add(nuevo_usuario)
            db.session.commit()

            # 🚀 Enviar email con credenciales
            from flask_mail import Message
            from . import mail

            msg = Message(
                "Tus credenciales de Aula Virtual",
                recipients=[email]
            )
            msg.body = f"""
            Hola {nombre},

            Tu cuenta en el Aula Virtual ha sido creada.

            Usuario: {email}
            Contraseña: {password}
            Rol: {rol}

            Inicia sesión en: http://127.0.0.1:5000/login
            """
            mail.send(msg)

            flash(f"Usuario {rol} creado y correo enviado a {email}.", "success")
            return redirect(url_for("main.dashboard"))

    return render_template("crear_usuario.html")


# ------------------- PÁGINAS BÁSICAS -------------------

@main.route("/")
def index():
    return render_template("main.login")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:  # ⚠️ En producción usa hashing
            login_user(user)
            return redirect(url_for("main.dashboard"))
        else:
            flash("Credenciales incorrectas", "danger")
    return render_template("login.html")

@main.route("/dashboard")
@login_required
def dashboard():
    if current_user.rol == "admin":
        cursos = Curso.query.all()
        return render_template("dashboard_admin.html", cursos=cursos)
    elif current_user.rol == "profesor":
        cursos = Curso.query.filter_by(profesor_id=current_user.id).all()
        return render_template("dashboard_profesor.html", cursos=cursos)
    elif current_user.rol == "alumno":
        cursos = Curso.query.all()  # ⚠️ luego filtrar solo cursos asignados
        return render_template("dashboard_alumno.html", cursos=cursos)
    return redirect(url_for("main.index"))

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))

# ------------------- GESTIÓN DE CURSOS -------------------

@main.route("/cursos")
@login_required
def cursos():
    cursos = Curso.query.all()
    return render_template("cursos.html", cursos=cursos)

@main.route("/curso/crear", methods=["GET", "POST"])
@login_required
def crear_curso():
    if current_user.rol != "admin":
        flash("Solo el ADMIN puede crear cursos", "danger")
        return redirect(url_for("main.cursos"))

    if request.method == "POST":
        nombre = request.form.get("nombre")
        descripcion = request.form.get("descripcion")
        profesor_id = request.form.get("profesor_id")

        curso = Curso(nombre=nombre, descripcion=descripcion, profesor_id=profesor_id)
        db.session.add(curso)
        db.session.commit()
        flash("Curso creado con éxito", "success")
        return redirect(url_for("main.cursos"))

    profesores = User.query.filter_by(rol="profesor").all()
    return render_template("crear_curso.html", profesores=profesores)

@main.route("/curso/<int:curso_id>")
@login_required
def ver_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    return render_template("curso_detalle.html", curso=curso)

@main.route("/curso/<int:curso_id>/eliminar", methods=["POST"])
@login_required
def eliminar_curso(curso_id):
    if current_user.rol != "admin":
        flash("Solo el ADMIN puede eliminar cursos", "danger")
        return redirect(url_for("main.cursos"))

    curso = Curso.query.get_or_404(curso_id)
    db.session.delete(curso)
    db.session.commit()
    flash("Curso eliminado", "info")
    return redirect(url_for("main.cursos"))

# ------------------- PUBLICACIÓN DE CONTENIDOS -------------------

@main.route("/curso/<int:curso_id>/contenido", methods=["GET", "POST"])
@login_required
def contenido(curso_id):
    curso = Curso.query.get_or_404(curso_id)

    if request.method == "POST" and current_user.rol == "profesor":
        archivo = request.files["archivo"]
        archivo.save(f"app/static/{archivo.filename}")
        flash("Contenido subido con éxito", "success")
        # ⚠️ aquí deberías guardar en DB una referencia al archivo
    return render_template("contenido.html", curso=curso)

# ------------------- SISTEMA DE EVALUACIONES -------------------

@main.route("/curso/<int:curso_id>/examen/crear", methods=["GET", "POST"])
@login_required
def crear_examen(curso_id):
    if current_user.rol != "profesor":
        flash("Solo los PROFESORES pueden crear exámenes", "danger")
        return redirect(url_for("main.cursos"))

    if request.method == "POST":
        pregunta = request.form.get("pregunta")
        respuesta = request.form.get("respuesta")
        flash("Examen creado (ejemplo)", "success")
        # ⚠️ Guardar examen en DB
        return redirect(url_for("main.ver_curso", curso_id=curso_id))
    return render_template("crear_examen.html", curso_id=curso_id)

@main.route("/curso/<int:curso_id>/examen/<int:examen_id>/resolver", methods=["GET", "POST"])
@login_required
def resolver_examen(curso_id, examen_id):
    if request.method == "POST":
        respuesta = request.form.get("respuesta")
        flash("Respuesta enviada (ejemplo)", "info")
        # ⚠️ Guardar respuesta en DB
        return redirect(url_for("main.ver_curso", curso_id=curso_id))
    return render_template("resolver_examen.html", curso_id=curso_id, examen_id=examen_id)
