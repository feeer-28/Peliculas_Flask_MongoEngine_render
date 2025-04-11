from flask import Flask
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from dotenv import load_dotenv
import os
from google_recaptcha_flask import ReCaptcha

load_dotenv()

app = Flask(__name__)
app.secret_key = "1234567890aeiou"

# Configuración de MongoDB
app.config['MONGODB_SETTINGS'] = {
    'host': os.environ.get('URI')
}

# Configurar recaptcha
app.config['GOOGLE_RECAPTCHA_ENABLED'] = True
app.config['GOOGLE_RECAPTCHA_SITE_KEY'] = os.environ.get("CLAVEDESITIO")
app.config['GOOGLE_RECAPTCHA_SECRET_KEY'] = os.environ.get("CLAVESECRETA")

# Crear objeto de tipo Recaptcha
recaptcha = ReCaptcha(app)

# Crear objeto de tipo MongoEngine
db = MongoEngine(app)

# Importar y registrar blueprints
from routes.usuario import usuario_bp
from routes.genero import genero_bp
from routes.pelicula import pelicula_bp

app.register_blueprint(usuario_bp)
app.register_blueprint(genero_bp)
app.register_blueprint(pelicula_bp)

if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", debug=True)


