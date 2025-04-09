from mongoengine import *

# Crear clase que representa la colección Genero en la base de datos
class Genero(Document):
    nombre = StringField(max_length=50, unique=True,required=True)
          

    def __repr__(self):
        return self.nombre

