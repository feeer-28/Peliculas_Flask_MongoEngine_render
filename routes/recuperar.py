from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
from models.usuario import Usuario  # Asegúrate de tener un modelo Usuario
import random
import string

recuperar_bp = Blueprint('recuperar', __name__)

# Configuración de Flask-Mail
mail = Mail()

@recuperar_bp.route('/recuperar', methods=['GET', 'POST'])
def recuperar_contrasena():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')

        # Buscar usuario en la base de datos
        usuario = Usuario.objects(username=username, email=email).first()

        if usuario:
            # Generar nueva contraseña
            nueva_contrasena = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            # Actualizar contraseña en la base de datos
            usuario.update(password=nueva_contrasena)

            # Enviar correo con la nueva contraseña
            msg = Message('Recuperación de contraseña',
                          sender='tu_correo@example.com',
                          recipients=[email])
            msg.body = f"Hola {username}, tu nueva contraseña es: {nueva_contrasena}"
            mail.send(msg)

            flash('Se ha enviado una nueva contraseña a tu correo.', 'success')
            return redirect(url_for('recuperar.recuperar_contrasena'))
        else:
            flash('Usuario o correo no encontrado.', 'danger')

    return render_template('recuperar.html')