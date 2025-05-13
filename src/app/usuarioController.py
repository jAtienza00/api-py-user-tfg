import bcrypt
from .models import Usuarios
from .schemas import usuarios_schema
from flask import request, jsonify
from .db import db
from .models import Usuarios
from .schemas import usuario_schema, usuarios_schema
from .auth import Security

def comprobarConexion():
    if Security.verificar(request.headers):
        return jsonify({'success': True}), 200
    return jsonify({'success': False}), 401

def create_usuario():
    try:
        comprobarToken(request.headers)
        data = request.get_json()
        if not data or 'nombre' not in data or 'contrasenia' not in data:
            return {'creado': False}, 400
        
        nombre = data['nombre']
        contrasenia = data['contrasenia']

        buscar = buscarUsu(nombre, contrasenia)
        if buscar["encontrado"]:
            return {'creado': True}, 200

        new_usuario = Usuarios(nombre, contrasenia)
        db.session.add(new_usuario)
        db.session.commit()

        return {'creado': True}, 200
    except tokenNoValido as e:
        return {'message': str(e)}, 401
    except Exception as e:
        print(e)
        return {'creado': False}, 500

def show_usuarios():
    try:
        nombre = request.args.get('nombre')
        contrasenia = request.args.get('contrasenia')

        if nombre and contrasenia:
            return buscarUsu(nombre, contrasenia), 200
        comprobarToken(request.headers)
        usuarios = Usuarios.query.all()
        resultados = usuarios_schema.dump(usuarios)

        return jsonify(resultados), 200
    except tokenNoValido as e:
        return {'message': str(e)}, 401
    except:
        return {'message': 'Error'}, 500

def show_usuario(id):
    try:
        comprobarToken(request.headers)
        usuario = db.session.get(Usuarios, id)
        return usuario_schema.jsonify(usuario)
    except tokenNoValido as e:
        return {'message': str(e)}, 401
    except:
        return {'message': 'Error al obtener el usuario'}, 500

def update_usuario(id):
    try:
        comprobarToken(request.headers)
        usuario = db.session.get(Usuarios, id)
        if not usuario:
            return {'message': 'Usuario no encontrado'}, 404

        data = request.get_json()
        nombre = data.get("nombre")
        contrasenia = data.get("contrasenia")

        if not nombre or not contrasenia:
            return {'message': 'Nombre y contraseña son requeridos'}, 400

        contrasenia = contrasenia.encode('utf-8')
        buscar = buscarUsu(nombre, contrasenia)

        if buscar.get("encontrado") and buscar.get("id") == id:
            return {'encontrado': True}, 200

        usuario.nombre = nombre
        usuario.setContrasenia(contrasenia)
        db.session.commit()

        return usuario_schema.jsonify(usuario)
    except tokenNoValido as e:
        return {'message': str(e)}, 401
    except Exception as e:
        return {'message': 'Error al actualizar el usuario'}, 500

def delete_usuario(id):
    try:
        usuario = db.session.get(Usuarios, id)
        if usuario is None:
            return {'message': 'Eliminado'}, 200
        db.session.delete(usuario)
        db.session.commit()

        return {'message': 'Eliminado'}, 200
    except tokenNoValido as e:
        return {'message': str(e)}, 401
    except:
        return {'message': 'Error al eliminar usuario'}, 500

def buscarUsu(nombre, contrasenia):
    usuario = Usuarios.query.filter_by(nombre=nombre).first()

    if usuario and bcrypt.checkpw(contrasenia.encode('utf-8'), usuario.contrasenia.encode('utf-8')):
        token = Security.generarToken(usuario)
        return {"encontrado": True, "id": usuario.id, "token": token}
    
    return {"encontrado": False}


def comprobarToken(header):
    if Security.verificar(header) == False:
        raise tokenNoValido()
    return True

class tokenNoValido(Exception):
    def __init__(self, mensaje="Token no válido"):
        super().__init__(mensaje)