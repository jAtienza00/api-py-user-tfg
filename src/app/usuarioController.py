import bcrypt
import re
from .models import Usuarios
from flask import request, jsonify
from .db import db
from .schemas import usuario_schema, usuarios_schema
from .auth import Security

def comprobarConexion():
    if Security.verificar(request.headers):
        return jsonify({'success': True}), 200
    return jsonify({'message': 'Token no válido o ausente', 'success': False}), 401

def create_usuario():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Faltan datos en el cuerpo de la solicitud JSON'}), 400
        nombre = data.get('nombre')
        contrasenia = data.get('contrasenia')

        email = data.get('email')
        if not nombre or not email or not contrasenia:
            return jsonify({'message': 'Faltan campos obligatorios'}), 400

        # Validations
        trimmed_nombre = nombre.strip()
        if not trimmed_nombre:
            return jsonify({'message': 'El nombre es obligatorio.'}), 400
        if not re.match(r"^[A-Za-z0-9]+$", trimmed_nombre):
            return jsonify({'message': 'El nombre de usuario solo puede contener letras y números.'}), 400

        trimmed_email = email.strip()
        if not trimmed_email:
            return jsonify({'message': 'El email es obligatorio.'}), 400
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", trimmed_email):
            return jsonify({'message': 'El formato del email no es válido.'}), 400

        if not re.match(r"^(?=(.*\d){2,}).{4,}$", contrasenia):
            return jsonify({'message': 'La contraseña debe tener al menos 4 caracteres y contener al menos dos números.'}), 400

        if Usuarios.query.filter_by(email=trimmed_email).first():
            return jsonify({'message': 'Email en uso.'}), 409

        new_usuario = Usuarios(nombre=trimmed_nombre, contrasenia=contrasenia, email=trimmed_email)
        db.session.add(new_usuario)
        db.session.commit()

        return jsonify({'message': f'Usuario : {new_usuario.nombre} creado exitosamente.', 'token' : Security.generarToken(new_usuario), 'id': new_usuario.id, 'nombre': new_usuario.nombre}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear usuario: {str(e)}") # Replace with proper logging
        return jsonify({'message': 'Error interno al crear el usuario'}), 500

def show_usuarios():
    try:       
        
        email = request.args.get('email')
        contrasenia = request.args.get('contrasenia')

        if email and contrasenia:
            print('buscando')
            data = buscarUsu(email, contrasenia)
            print(data)
            if data['encontrado'] == True:
                return jsonify(token=data['token'], id=data['id']), 200
        
        if not Security.verificar(request.headers):
            return jsonify({'message': 'Token no válido o ausente'}), 401
        usuarios = Usuarios.query.all()
        resultados = usuarios_schema.dump(usuarios)
        return jsonify(resultados), 200
    except Exception as e:
        print(f"Error en show_usuarios: {str(e)}") # Replace with proper logging
        return jsonify({'message': 'Error interno al obtener usuarios'}), 500

def show_usuario(id):
    try:
        if not Security.verificar(request.headers):
            return jsonify({'message': 'Token no válido o ausente'}), 401

        usuario = db.session.get(Usuarios, id)
        if not usuario:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        return usuario_schema.jsonify(usuario)
    except Exception as e:
        print(f"Error al obtener usuario {id}: {str(e)}") # Replace with proper logging
        return jsonify({'message': 'Error interno al obtener el usuario'}), 500

def update_usuario(id):
    try:
        if not Security.verificar(request.headers):
            return jsonify({'message': 'Token no válido o ausente'}), 401


        data = request.get_json()
        data = data.get('data')
        if not data:
            return jsonify({'message': 'Faltan datos en el cuerpo de la solicitud JSON'}), 400

        nombre_nuevo_req = data.get('nombre')
        email_req = data.get('email')
        if data.get('emailNuevo'):
            email_nuevo_req = data.get('emailNuevo')
        else:
            email_nuevo_req = email_req
      
        contrasenia_actual_ingresada = data.get('contrasenia')
        if data.get('contraseniaNueva'):
            contrasenia_nueva_req = data.get('contraseniaNueva')
        else:
            contrasenia_nueva_req = contrasenia_actual_ingresada
        print(email_req + " " + contrasenia_actual_ingresada)
        if buscarUsu(email_req, contrasenia_actual_ingresada)['encontrado'] == False:
            return {'message': 'Usuario no encontrado'}, 403
        
        usuario_actual = db.session.get(Usuarios, id)
        if not usuario_actual:
            return jsonify({'message': 'Usuario no encontrado'}), 404

        if nombre_nuevo_req is None or email_nuevo_req is None or contrasenia_actual_ingresada is None:
            return jsonify({'message': 'Los campos nombre, email y contraseña actual son obligatorios o son incorrectos.'}), 400


        # Validate Nombre
        trimmed_nombre = nombre_nuevo_req.strip()
        if not trimmed_nombre:
            return jsonify({'message': 'El nombre es obligatorio.'}), 400
        if not re.match(r"^[A-Za-z0-9]+$", trimmed_nombre):
            return jsonify({'message': 'El nombre de usuario solo puede contener letras y números.'}), 400
        if trimmed_nombre != usuario_actual.nombre:
            usuario_actual.setNombre(trimmed_nombre)
            
        if usuario_actual.email != email_nuevo_req:
            # Validate Email
            trimmed_email = email_nuevo_req.strip()
            if not trimmed_email:
                return jsonify({'message': 'El email es obligatorio.'}), 400
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", trimmed_email):
                return jsonify({'message': 'El formato del email no es válido.'}), 400
            if trimmed_email != usuario_actual.email:
                if Usuarios.query.filter(Usuarios.email == trimmed_email, Usuarios.id != id).first():
                    return jsonify({'message': f'El email "{trimmed_email}" ya está en uso.'}), 409
            usuario_actual.setEmail(trimmed_email)


        # Validate and set Contraseña Nueva (if provided)
        if contrasenia_nueva_req and contrasenia_nueva_req.strip():
            nueva_contrasenia_val = contrasenia_nueva_req.strip()
            if not re.match(r"^(?=(.*\d){2,}).{4,}$", nueva_contrasenia_val):
                return jsonify({'message': 'La nueva contraseña debe tener al menos 4 caracteres y contener al menos dos números.'}), 400
            usuario_actual.setContrasenia(nueva_contrasenia_val) # Pass plain string
        
        db.session.commit()
        return jsonify({'message' : "Has sido actualizado con exito."}, 200)

    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar usuario {id}: {str(e)}") # Replace with proper logging
        return jsonify({'message': 'Error interno al actualizar el usuario'}), 500

def delete_usuario(id):
    try:
        if not Security.verificar(request.headers):
            return jsonify({'message': 'Token no válido o ausente'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Faltan datos en el cuerpo de la solicitud JSON'}), 400

        email_req = data.get('email')
        contrasenia_ingresada = data.get('contrasenia')
        
        if buscarUsu(email_req, contrasenia_ingresada)['encontrado'] == False:
            return jsonify({'message': 'Email de usuario o contraseña incorrectos'}), 401         
        usuario = db.session.get(Usuarios, id)
        if usuario is None:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error interno al eliminar usuario'}), 500

def buscarUsu(email, contrasenia):
    usuario = Usuarios.query.filter_by(email=email).first()
    print(usuario)
    if usuario and bcrypt.checkpw(contrasenia.encode('utf-8'), usuario.contrasenia.encode('utf-8')):
        token = Security.generarToken(usuario)
        return {"encontrado": True, "id": usuario.id, "token": token}
    
    return {"encontrado": False}