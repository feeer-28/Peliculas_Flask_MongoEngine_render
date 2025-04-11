from flask import render_template, request, session, redirect, Blueprint
from models.usuario import Usuario
from dotenv import load_dotenv
import os
import yagmail
import threading
import secrets
import string
import logging

usuario_bp = Blueprint('usuario', __name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv(override=True)

# Obtener credenciales de correo del archivo .env
CORREO = os.getenv("CORREO")
PASSWORD_CORREO = os.getenv("PASSWORD-ENVIAR-CORREO")

# Verificar que las credenciales estén presentes
if not CORREO or not PASSWORD_CORREO:
    logger.error("No se encontraron las credenciales de correo en el archivo .env")
    logger.error(f"CORREO: {CORREO}")
    logger.error(f"PASSWORD_CORREO: {'Presente' if PASSWORD_CORREO else 'Ausente'}")
    raise ValueError("Las credenciales de correo son requeridas")

logger.info(f"Credenciales cargadas - Correo: {CORREO}")

# Inicializar yagmail una sola vez
try:
    yag = yagmail.SMTP(CORREO, PASSWORD_CORREO, encoding="utf-8")
    logger.info(f"Yagmail inicializado correctamente con el correo: {CORREO}")
except Exception as e:
    logger.error(f"Error al inicializar yagmail: {str(e)}")
    raise

@usuario_bp.route("/")
def inicio():
    return render_template("frmIniciarSesion.html")

def enviarCorreo(email=None, destinatario=None, asunto=None, mensaje=None, adjuntos=None):
    try:
        logger.info(f"Intentando enviar correo a: {destinatario}")
        logger.info(f"Asunto: {asunto}")
        logger.info(f"Correo remitente: {CORREO}")
        
        # Verificar que todos los parámetros necesarios estén presentes
        if not all([destinatario, asunto, mensaje]):
            logger.error("Faltan parámetros necesarios para enviar el correo")
            return False
            
        # Usar la instancia global de yagmail si no se proporciona una
        email_to_use = email if email else yag
        
        # Enviar el correo
        try:
            if adjuntos:
                email_to_use.send(to=destinatario, subject=asunto, contents=mensaje, attachments=adjuntos)
            else:
                email_to_use.send(to=destinatario, subject=asunto, contents=mensaje)
            
            logger.info("Correo enviado exitosamente")
            return True
        except Exception as send_error:
            logger.error(f"Error al enviar el correo: {str(send_error)}")
            return False
    except Exception as error:
        logger.error(f"Error en la función enviarCorreo: {str(error)}")
        return False

@usuario_bp.route("/iniciarSesion/",  methods=['POST'])
def iniciarSesion():   
    mensaje = ""
    try:    
        if request.method=='POST':               
            from app import recaptcha  # Importar aquí para evitar ciclo
            if recaptcha.verify():           
                username=request.form['txtUser']
                password=request.form['txtPassword'] 
                usuario = Usuario.objects(usuario=username,password=password).first()
                if usuario:
                    session['user']=username
                    session['name_user']=f"{usuario.nombres} {usuario.apellidos}"
                    email = yagmail.SMTP(CORREO, PASSWORD_CORREO, encoding="utf-8")
                    asunto = "Ingreso al Sistema"
                    mensaje = f"Cordial saludo <b>{usuario.nombres} {usuario.apellidos}.</b> \
                            Bienvenido a nuestro aplicativo Gestión peliculas. \
                            Enviamos Manual de usuario del aplicativo en formato pdf.<br><br>\
                            Cordialmente,<br><br><br> \
                            <b>Administración<br>Aplicativo Gestión Películas.</b>"
                    thread = threading.Thread(target=enviarCorreo,
                                            args=(email, [usuario.correo,CORREO], 
                                                  asunto, [mensaje,"Informe de estructura y diccionario de datos (1).pdf"]))
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

@usuario_bp.route("/usuario/", methods=['POST'])
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

@usuario_bp.route("/home/")
def home():
    if("user" in session):
        return render_template("contenido.html")
    else:
        mensaje="Debe primero ingresar con credenciales válidas"
        return render_template("frmIniciarSesion.html", mensaje=mensaje)

@usuario_bp.route("/salir/")
def exit():
    session.clear()
    mensaje="Ha cerrado la sesión de forma"
    return render_template("frmIniciarSesion.html",mensaje=mensaje)

@usuario_bp.route("/usuario/",methods=["GET"])
def listarUsuario():
    try:
        mensaje=None
        usuarios=Usuario.objects()
    except Exception as error:
        mensaje=str(error)
    return {"mensaje": mensaje,"usuarios": usuarios}

@usuario_bp.route("/recuperarContrasena/", methods=["GET", "POST"])
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
            try:
                asunto = "Recuperación de contraseña"
                mensaje_correo = f"""
                <html>
                <body>
                <p>Cordial saludo <b>{usuario.nombres} {usuario.apellidos}.</b></p>
                <p>Hemos recibido una solicitud para restablecer tu contraseña.</p>
                <p>Tu nueva contraseña temporal es: <b>{nueva_contrasena}</b></p>
                <p>Por seguridad, te recomendamos cambiar esta contraseña después de iniciar sesión.</p>
                <p>Cordialmente,</p>
                <p><b>Administración<br>Aplicativo Gestión Películas.</b></p>
                </body>
                </html>
                """
                
                # Enviar el correo usando la instancia global de yagmail
                if enviarCorreo(None, usuario.correo, asunto, mensaje_correo):
                    mensaje = "Se ha enviado una nueva contraseña a tu correo electrónico."
                    return render_template("frmRecuperarContrasena.html", mensaje=mensaje)
                else:
                    mensaje = "La contraseña se actualizó pero hubo un error al enviar el correo. Por favor, contacta al administrador."
                    return render_template("frmRecuperarContrasena.html", mensaje=mensaje)
                    
            except Exception as email_error:
                logger.error(f"Error al configurar el envío de correo: {str(email_error)}")
                mensaje = "La contraseña se actualizó pero hubo un error al enviar el correo. Por favor, contacta al administrador."
                return render_template("frmRecuperarContrasena.html", mensaje=mensaje)
        else:
            mensaje = "Usuario o correo electrónico no encontrados."
    
    except Exception as error:
        logger.error(f"Error general en recuperarContrasena: {str(error)}")
        mensaje = f"Error al recuperar contraseña: {str(error)}"
    
    return render_template("frmRecuperarContrasena.html", mensaje=mensaje)