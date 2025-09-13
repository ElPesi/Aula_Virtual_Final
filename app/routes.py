from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Curso, Archivo, Examen, Pregunta, Opcion
from . import db, login_manager
import os

main = Blueprint("main", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#  ------------------------DASHBOARD ADMIN ------------------------
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


# ------------------- LOGIN -------------------

# Ahora "/" redirige directo a /login
@main.route("/")
def home():
    return redirect(url_for("main.login"))

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


# ------------------- DASHBOARD -------------------

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

    # fallback
    return redirect(url_for("main.login"))


# ------------------- LOGOUT -------------------

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))

# ------------------- CURSOS -------------------

# Profesor: crear curso
@main.route("/profesor/crear_curso", methods=["GET", "POST"])
@login_required
def crear_curso():
    if current_user.rol != "profesor":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        nombre = request.form.get("nombre")
        descripcion = request.form.get("descripcion")

        nuevo_curso = Curso(nombre=nombre, descripcion=descripcion, profesor_id=current_user.id)
        db.session.add(nuevo_curso)
        db.session.commit()

        flash("Curso creado correctamente", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("crear_curso.html")


# Profesor: editar curso
@main.route("/profesor/editar_curso/<int:curso_id>", methods=["GET", "POST"])
@login_required
def editar_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)

    if current_user.rol != "profesor" or curso.profesor_id != current_user.id:
        flash("Acceso denegado.", "danger")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        curso.nombre = request.form.get("nombre")
        curso.descripcion = request.form.get("descripcion")
        db.session.commit()

        flash("Curso actualizado correctamente", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("editar_curso.html", curso=curso)


# Profesor: eliminar curso
@main.route("/profesor/eliminar_curso/<int:curso_id>", methods=["POST"])
@login_required
def eliminar_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)

    if current_user.rol != "profesor" or curso.profesor_id != current_user.id:
        flash("Acceso denegado.", "danger")
        return redirect(url_for("main.dashboard"))

    db.session.delete(curso)
    db.session.commit()

    flash("Curso eliminado correctamente", "success")
    return redirect(url_for("main.dashboard"))

# Admin: asignar alumnos a un curso
@main.route("/curso/<int:curso_id>/asignar_alumnos", methods=["GET", "POST"])
@login_required
def asignar_alumnos(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    alumnos = User.query.filter_by(rol="alumno").all()

    if request.method == "POST":
        seleccionados = request.form.getlist("alumnos_seleccionados")
        curso.alumnos = [User.query.get(int(a_id)) for a_id in seleccionados]
        db.session.commit()
        flash("Alumnos asignados correctamente.")
        return redirect(url_for("main.dashboard"))

    return render_template("asignar_alumnos.html", curso=curso, alumnos=alumnos)

# ------------------- CONTENIDOS -------------------
@main.route("/curso/<int:curso_id>/contenido", methods=["GET", "POST"])
@login_required
def contenido(curso_id):
    curso = Curso.query.get_or_404(curso_id)

    if request.method == "POST" and current_user.rol == "profesor":
        archivo = request.files["archivo"]
        ruta_guardado = f"uploads/{archivo.filename}"
        archivo.save(os.path.join("app", "static", ruta_guardado))

        nuevo_archivo = Archivo(nombre=archivo.filename, ruta=ruta_guardado, curso_id=curso.id)
        db.session.add(nuevo_archivo)
        db.session.commit()
        flash("Archivo subido con éxito", "success")
        return redirect(url_for("main.contenido", curso_id=curso.id))

    return render_template("contenido.html", curso=curso, archivos=curso.archivos, examenes=curso.examenes)


@main.route("/archivo/<int:archivo_id>/eliminar", methods=["POST"])
@login_required
def eliminar_archivo(archivo_id):
    archivo = Archivo.query.get_or_404(archivo_id)

    if current_user.rol != "profesor" or archivo.curso.profesor_id != current_user.id:
        flash("No tienes permisos para eliminar este archivo", "danger")
        return redirect(url_for("main.dashboard"))

    ruta_completa = os.path.join("app", "static", archivo.ruta)
    if os.path.exists(ruta_completa):
        os.remove(ruta_completa)

    db.session.delete(archivo)
    db.session.commit()
    flash("Archivo eliminado con éxito", "success")
    return redirect(url_for("main.contenido", curso_id=archivo.curso_id))


# ------------------- EXÁMENES -------------------
@main.route("/curso/<int:curso_id>/crear_examen", methods=["GET", "POST"])
@login_required
def crear_examen(curso_id):
    curso = Curso.query.get_or_404(curso_id)

    if current_user.rol != "profesor":
        flash("No tienes permisos para crear exámenes.")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        titulo = request.form.get("titulo")
        examen = Examen(titulo=titulo, curso_id=curso.id)
        db.session.add(examen)
        db.session.commit()

        flash("Examen creado. Ahora añade preguntas.")
        return redirect(url_for("main.editar_examen", examen_id=examen.id))

    return render_template("crear_examen.html", curso=curso)

@main.route("/examen/<int:examen_id>/editar", methods=["GET", "POST"])
@login_required
def editar_examen(examen_id):
    examen = Examen.query.get_or_404(examen_id)

    if current_user.rol != "profesor":
        flash("No tienes permisos para editar exámenes.")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        texto_pregunta = request.form.get("pregunta")
        tipo = request.form.get("tipo")

        nueva_pregunta = Pregunta(texto=texto_pregunta, tipo=tipo, examen_id=examen.id)
        db.session.add(nueva_pregunta)
        db.session.commit()

        if tipo == "multiple":
            opciones = request.form.getlist("opciones[]")
            correctas = request.form.getlist("correctas[]")
            for i, texto_opcion in enumerate(opciones):
                opcion = Opcion(
                    texto=texto_opcion,
                    es_correcta=str(i) in correctas,
                    pregunta_id=nueva_pregunta.id
                )
                db.session.add(opcion)
            db.session.commit()

        flash("Pregunta añadida correctamente.")
        return redirect(url_for("main.editar_examen", examen_id=examen.id))

    return render_template("editar_examen.html", examen=examen)

# Alumno: resolver examen
@main.route("/curso/<int:curso_id>/examen/<int:examen_id>/resolver", methods=["GET", "POST"])
@login_required
def resolver_examen(curso_id, examen_id):
    if current_user.rol != "alumno":
        flash("No tienes permisos para acceder a este examen.", "danger")
        return redirect(url_for("main.dashboard"))

    examen = Examen.query.get_or_404(examen_id)

    if request.method == "POST":
        for pregunta in examen.preguntas:
            if pregunta.tipo == "abierta":
                respuesta_texto = request.form.get(f"pregunta_{pregunta.id}")
                print(f"Respuesta abierta: {respuesta_texto}")  # acá luego guardás en la DB

            elif pregunta.tipo == "multiple":
                seleccionadas = request.form.getlist(f"pregunta_{pregunta.id}")
                print(f"Respuestas multiple: {seleccionadas}")  # acá luego guardás en la DB

        flash("Examen enviado correctamente.")
        return redirect(url_for("main.contenido", curso_id=curso_id))

    return render_template("resolver_examen.html", examen=examen)
