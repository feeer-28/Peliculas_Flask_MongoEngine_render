from flask import request, render_template, redirect, session, Blueprint
from models.pelicula import Pelicula
from models.genero import Genero
from bson.objectid import ObjectId

pelicula_bp = Blueprint('pelicula', __name__)

@pelicula_bp.route("/pelicula/", methods=['GET'])
def listPelicula():
    try:   
        mensaje=None     
        peliculas= Pelicula.objects()  
    except Exception as error:
        mensaje=str(error)
    
    return {"mensaje": mensaje, "peliculas":peliculas}

@pelicula_bp.route("/pelicula/", methods=['POST'])
def addPelicula():
    try:
        mensaje=None
        estado=False
        if request.method=="POST":
            datos= request.get_json(force=True)           
            genero= Genero.objects(id=datos['genero']).first() 
            if genero is None:
                mensaje="Genero no existe no se puede crear la pelicula"
            else: 
                datos['genero'] = genero     
                pelicula = Pelicula(**datos)
                pelicula.save()
                estado=True
                mensaje="Pelicula agregada correctamente" 
        else:
            mensaje="No permitido"   
    except Exception as error:
        mensaje=str(error) 
        mensaje="Ya exsite película con ese código revisar."
        
    return {"estado":estado, "mensaje":mensaje}


@pelicula_bp.route("/pelicula/", methods=['PUT'])
def updatePelicula():
    try:
        mensaje=None
        estado=False
        if request.method=='PUT':
            datos= request.get_json(force=True)
            #obtener pelicula por id
            pelicula = Pelicula.objects(id=datos['id']).first()
            #actualizar sus atributos
            pelicula.codigo = datos['codigo']
            pelicula.titulo=datos['titulo']
            pelicula.protagonista= datos['protagonista']
            pelicula.resumen = datos['resumen']
            pelicula.foto=datos['foto']
            genero = Genero.objects(id=datos['genero']).first()
            if genero is None:
                mensaje="No se actualizó el genero."
            else:
                pelicula.genero=genero
            pelicula.save()
            mensaje = f"{mensaje} Pelicula Actualizada"
            estado=True            
        else:
            mensaje="No permitido" 
    except Exception as error:
        mensaje=str(error)
        mensaje="No es posible actualizar ya exsite película con ese código."
        
    return {"estado":estado, "mensaje": mensaje}

@pelicula_bp.route("/pelicula/", methods=['DELETE'])
def deletePelicula():
    try:
        mensaje=None
        estado=True
        if request.method=="DELETE":
            datos=request.get_json(force=True)
            pelicula=Pelicula.objects(id=datos['id']).first()
            if(pelicula is None):
                mensaje="No es posible eliminar pelicula con ese id"
            else:
                pelicula.delete()
                estado=True
                mensaje="Pelicula Eliminada correctamente"            
        else:
            mensaje="No permitido"  
    except Exception as error:
        mensaje=str(error)
        
    return {"estado": estado, "mensaje": mensaje}

#vistas

@pelicula_bp.route("/peliculas/", methods=['GET'])
def listarPeliculas():
    if ("user" in session):
        peliculas = Pelicula.objects()
        generos = Genero.objects()
        print(generos)
        return render_template("listarPeliculas.html", 
                            peliculas=peliculas,
                            generos=generos)
    else:
        mensaje="Debe primero ingresar con credenciales válidas"
        return render_template("frmIniciarSesion.html", mensaje=mensaje)
        

@pelicula_bp.route("/vistaAgregarPelicula/", methods=['GET'])
def vistaAgregarPelicula():
    if ("user" in session):
        generos = Genero.objects()
        return render_template("frmAgregarPelicula.html", generos=generos)
    else:
        mensaje="Debe primero ingresar con credenciales válidas"
        return render_template("frmIniciarSesion.html", mensaje=mensaje)
        

@pelicula_bp.route("/vistaEditarPelicula/<string:id>/", methods=['GET'])
def mostrarVistaEditarPelicula(id):  
    if ("user" in session):  
        pelicula = Pelicula.objects(id=ObjectId(id)).first()
        generos = Genero.objects()
        return render_template("frmEditarPelicula.html",
                               pelicula=pelicula, generos=generos) 
    else:
        mensaje="Debe primero ingresar con credenciales válidas"
        return render_template("frmIniciarSesion.html", mensaje=mensaje)     
   
