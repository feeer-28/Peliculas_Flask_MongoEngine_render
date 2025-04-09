from mongoengine import *
from models.genero import Genero

# crear la clase que representa la colección Pelicula en la base de datos
class Pelicula(Document):
    codigo = IntField(unique=True,required=True)
    titulo = StringField(max_length=80,required=True)
    protagonista = StringField(max_length=50,required=True)
    duracion = IntField(min_value=30, max_value=200,required=True)
    resumen = StringField(required=True)
    foto = StringField()
    genero = ReferenceField(Genero, required=True)
    
    def __repr__(self):
        return self.titulo
    

