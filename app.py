from flask import Flask
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from dotenv import load_dotenv
import os
from google_recaptcha_flask import ReCaptcha

load_dotenv()

app = Flask(__name__)
app.secret_key = "1234567890aeiou"

load_dotenv()

app.config['MONGODB_SETTINGS'] = {
    'host': os.environ.get('URI')
}


#configurar recaptcha
app.config['GOOGLE_RECAPTCHA_ENABLED'] =True
app.config['GOOGLE_RECAPTCHA_SITE_KEY'] = os.environ.get("CLAVEDESITIO")  # Sustituye por tu clave pública
app.config['GOOGLE_RECAPTCHA_SECRET_KEY'] = os.environ.get("CLAVESECRETA") # Sustituye por tu clave secreta

#crear objeto detipo Recaptcha
recaptcha = ReCaptcha(app)

#Crear objeto de tipo MonoEngine
db = MongoEngine(app)


from routes.usuario import *
from routes.genero import *
from routes.pelicula import *

if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", debug=True)


