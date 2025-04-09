from app import app, recaptcha
from flask import render_template, request, session, redirect, Blueprint
from models.usuario import Usuario
from dotenv import load_dotenv
import os
import yagmail
import threading
import secrets
import string

usuario_bp = Blueprint('usuario', __name__)

load_dotenv()

@app.route("/")
def inicio():
    return render_template("frmIniciarSesion.html")

def enviarCorreo(email=None, destinatario=None, asunto=None, mensaje=None):
    try:
        email.send(to=destinatario, subject=asunto, contents=mensaje)
    except Exception as error:
        print(str(error))



@app.route("/iniciarSesion/",  methods=['POST'])
def iniciarSesion():   
    mensaje = ""
    try:    
        if request.method=='POST':               
            if recaptcha.verify():           
                username=request.form['txtUser']
                password=request.form['txtPassword'] 
                usuario = Usuario.objects(usuario=username,password=password).first()
                if usuario:
                    session['user']=username
                    session['name_user']=f"{usuario.nombres} {usuario.apellidos}"
                    email = yagmail.SMTP("darcyfernandagonzalez@gmail.com",os.environ.get("PASSWORD-ENVIAR-CORREO"), 
                                     encoding="utf-8")
                    asunto = "Ingreso al Sistema"
                    mensaje = f"Cordial saludo <b>{usuario.nombres} {usuario.apellidos}.</b> \
                            Bienvenido a nuestro aplicativo Gestión peliculas. \
                            Enviamos Manual de usuario del aplicativo en formato pdf.<br><br>\
                            Cordialmente,<br><br><br> \
                            <b>Administración<br>Aplicativo Gestión Películas.</b>"
                    thread = threading.Thread(target=enviarCorreo,
                                            args=(email, [usuario.correo,"darcyfernandagonzalez@gmail.com"], 
                                                  asunto, [mensaje,"Manual.pdf","./static/imagenes/avatar.png"]))
                    thread.start()
                    return redirect("/home/")
                else:
                    mensaje="Credenciales no válidas"
            else:
                mensaje = "Debe validar primero el recaptcha"
        else:
            mensaje="No permitido"
    except Exception as error:
        mensaje=str(error)
    
    return render_template("frmIniciarSesion.html", mensaje=mensaje)

@app.route("/usuario/", methods=['POST'])
def addUsuario():
    try:
        mensaje=None
        estado=False
        datos= request.get_json(force=True)
        usuario = Usuario(**datos)
        usuario.save()
        estado=True
        mensaje="Usuario agregado correctamente"       
        
    except Exception as error:
        mensaje=str(error) 
        
    return {"estado":estado, "mensaje":mensaje}


@app.route("/home/")
def home():
    if("user" in session):
        return render_template("contenido.html")
    else:
        mensaje="Debe primero ingresar con credenciales válidas"
        return render_template("frmIniciarSesion.html", mensaje=mensaje)

@app.route("/salir/")
def exit():
    session.clear()
    mensaje="Ha cerrado la sesión de forma"
    return render_template("frmIniciarSesion.html",mensaje=mensaje)
@app.route("/usuario/",methods=["GET"])
def listarUsuario():
    try:
        mensaje=None
        usuarios=Usuario.objects()
    except Exception as error:
        mensaje=str(error)
    return {"mensaje": mensaje,"usuarios": usuarios}

@app.route("/recuperarContrasena/", methods=["GET", "POST"])
def recuperarContrasena():
    mensaje = ""
    if request.method == "GET":
        return render_template("frmRecuperarContrasena.html")
    
    try:
        user = request.form["txtUser"]
        correo = request.form["txtCorreo"]
        usuario = Usuario.objects(usuario=user, correo=correo).first()
        
        if usuario:
            # Generar contraseña aleatoria de 8 caracteres
            caracteres = string.ascii_letters + string.digits
            nueva_contrasena = ''.join(secrets.choice(caracteres) for _ in range(8))
            
            # Actualizar la contraseña en la base de datos
            usuario.update(set__password=nueva_contrasena)
            
            # Enviar correo con la nueva contraseña
            email = yagmail.SMTP("darcyfernandagonzalez@gmail.com", 
                                os.environ.get("PASSWORD-ENVIAR-CORREO"), 
                                encoding="utf-8")
            asunto = "Recuperación de contraseña"
            mensaje_correo = f"""
            Cordial saludo <b>{usuario.nombres} {usuario.apellidos}.</b><br><br>
            Hemos recibido una solicitud para restablecer tu contraseña.<br><br>
            Tu nueva contraseña temporal es: <b>{nueva_contrasena}</b><br><br>
            Por seguridad, te recomendamos cambiar esta contraseña después de iniciar sesión.<br><br>
            Cordialmente,<br><br>
            <b>Administración<br>Aplicativo Gestión Películas.</b>
            """
            
            thread = threading.Thread(
                target=enviarCorreo,
                args=(email, [usuario.correo], asunto, mensaje_correo)
            )
            thread.start()
            
            mensaje = "Se ha enviado una nueva contraseña a tu correo electrónico."
            return render_template("frmIniciarSesion.html", mensaje=mensaje)
        else:
            mensaje = "Usuario o correo electrónico no encontrados."
    
    except Exception as error:
        mensaje = f"Error al recuperar contraseña: {str(error)}"
    
    return render_template("frmRecuperarContrasena.html", mensaje=mensaje)