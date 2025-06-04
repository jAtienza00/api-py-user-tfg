from .models import Chat
from flask import request, jsonify, current_app
from .schemas import chats_resumen_schema, chat_schema, chat_resumen_schema
from .auth import Security # Keep Security import
from sqlalchemy.exc import IntegrityError # Import SQLAlchemy's IntegrityError
from .db import db
import random
import string

def comprobarRequest(request_obj):
    if not Security.verificar(request_obj.headers):
        return jsonify({'message': 'Token no válido o ausente'}), 401
    
    json_data = request_obj.get_json()
    if not json_data:
        return jsonify({'message': 'Faltan datos en el cuerpo de la solicitud JSON'}), 400
    
    user_id_from_json = json_data.get('id')
    if user_id_from_json is None:
         return jsonify({'message': 'Falta el campo "id" en el JSON de la solicitud'}), 400
    return user_id_from_json

def mostrarChats():
    auth_result = comprobarRequest(request)
    if isinstance(auth_result, tuple): # Es una tupla (response, status_code)
        return auth_result
    user_id_to_find = auth_result 

    chats = Chat.query.filter(
        (db.literal(';') + Chat.usuarios + db.literal(';')).like('%;' + str(user_id_to_find) + ';%')
    ).all()
    result = chats_resumen_schema.dump(chats)
    return jsonify({"chats": result}), 200

def mostrarChat(chat_id):
    auth_result = comprobarRequest(request)
    if isinstance(auth_result, tuple):
        return auth_result
    user_id_solicitante = auth_result 

    chat = Chat.query.get(chat_id)
    if chat is None:
        return jsonify({'message': 'Chat no encontrado'}), 404
    
    if chat.usuarios.split(";").count(f";{user_id_solicitante};") != str(user_id_solicitante):
        return jsonify({'message': 'No tienes permiso para ver este chat'}), 403

    return chat_schema.jsonify(chat), 200


def buscarChat():
    auth_result = comprobarRequest(request)
    if isinstance(auth_result, tuple):
        return auth_result
    user_id_solicitante = auth_result 
    
    json_data = request.get_json()
    clave = json_data.get('clave')
    if clave is None:
        return jsonify({'message': 'Falta el campo "clave" en el JSON de la solicitud'}), 400
    
    chat = Chat.query.filter_by(clave=clave).first()
    if chat is None:
        return jsonify({'message': 'Chat no encontrado'}), 404
    
    if chat.usuarios.split(";").count(f";{user_id_solicitante};") == str(user_id_solicitante):
        return jsonify({'message': 'No tienes permiso para ver este chat'}), 403
    
    result = chat_schema.dump(chat)
    return jsonify({'id': result['id'], 'nombre': result['nombre'], 'max_usu': result['max_usu'], 'clave': result['clave'], 'chats_usuarios_FK': result['usuario_id'], 'usuarios': result['usuarios']}), 200


def crearChat():
    auth_result = comprobarRequest(request)
    if isinstance(auth_result, tuple):
        return auth_result
    user_id = auth_result

    json_data = request.get_json()
    nombre = json_data.get('nombre')
    max_usu = json_data.get('max_usu')
    if None in (nombre, max_usu):
        return jsonify({'message': 'Faltan campos requeridos (nombre, max_usu, clave, id)'}), 400
    clave_generada = generar_clave_random()
    intentos_maximos = 5 
    for intento in range(intentos_maximos):
        try:
            new_chat = Chat(
                nombre=nombre,
                max_usu=max_usu,
                clave=clave_generada, # Usar la clave generada
                usuario_id=user_id,
                usuarios=f';{user_id};' 
            )
            db.session.add(new_chat)
            db.session.commit()
            return jsonify({'message': 'Chat creado exitosamente', 'clave': new_chat.clave, 'nombre': new_chat.nombre, 'id': new_chat.id}), 201
        except IntegrityError as e: # This will catch sqlalchemy.exc.IntegrityError
            db.session.rollback()
            # Check for PostgreSQL unique violation (pgcode '23505')
            # e.orig should be the DBAPI exception (e.g., from psycopg2)
            is_pg_unique_violation = hasattr(e.orig, 'pgcode') and e.orig.pgcode == '23505'
            
            # Check if the violation is related to the 'clave' column.
            # The constraint name might be 'chat_clave_key' or similar.
            # Checking 'clave' in the error message is a general approach.
            if is_pg_unique_violation and "clave" in str(e.orig).lower():
                clave_generada_anterior = clave_generada # Store for logging
                if intento < intentos_maximos - 1:
                    clave_generada = generar_clave_random()
                    current_app.logger.warning(
                        f"Clave duplicada '{clave_generada_anterior}' para el chat. "
                        f"Reintentando con nueva clave '{clave_generada}'. Intento {intento + 2}/{intentos_maximos}"
                    )
                    continue 
                else:
                    current_app.logger.error(
                        f"No se pudo generar una clave única para el chat después de {intentos_maximos} intentos. "
                        f"Última clave intentada (duplicada): '{clave_generada_anterior}'."
                    )
                    return jsonify({'message': 'Error al generar una clave única para el chat después de varios intentos'}), 500
            else:
                current_app.logger.error(f"Error de integridad al crear chat (no por clave duplicada o error no reconocido): {e}")
                current_app.logger.error(f"Detalles del error original: {e.orig}")
                return jsonify({'message': 'Error de integridad en la base de datos al crear el chat'}), 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error general al crear chat: {e}")
            return jsonify({'message': 'Error interno al crear el chat'}), 500
    
def eliminarChat(chat_id):
    auth_result = comprobarRequest(request)
    if isinstance(auth_result, tuple):
        return auth_result
    user_id = auth_result 

    chat = Chat.query.get(chat_id)
    if chat is None:
        return jsonify({'message': 'Chat eliminado'}), 200
    
    if str(chat.usuario_id) == str(user_id):
        try:
            db.session.delete(chat)
            db.session.commit()
            return jsonify({'message': 'Chat eliminado'}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar chat: {e}")
            return jsonify({'message': 'Error interno al eliminar el chat'}), 500
    else:
        return jsonify({'message': 'No tienes permiso para eliminar este chat'}), 403
    
def actualizarChat(chat_id):
    auth_result = comprobarRequest(request)
    if isinstance(auth_result, tuple):
        return auth_result
    user_id = auth_result 

    json_data = request.get_json() 
    nombre = json_data.get('nombre')
    max_usu = json_data.get('max_usu')

    if None in (nombre, max_usu):
        return jsonify({'message': 'Faltan campos requeridos (nombre, max_usu, clave)'}), 400
    
    chat = Chat.query.get(chat_id)
    if chat is None:
        return jsonify({'message': 'Chat no encontrado'}), 404

    print(chat.usuario_id)
    print(user_id)
    if str(chat.usuario_id) != str(user_id):
        return jsonify({'message': 'No tienes permiso para actualizar este chat'}), 403

    try:
        chat.nombre = nombre
        chat.max_usu = max_usu
        db.session.commit()
        return jsonify({'message': 'Chat actualizado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar chat: {e}")
        return jsonify({'message': 'Error interno al actualizar el chat'}), 500
    
def unirseAChat():
    auth_result = comprobarRequest(request)
    if isinstance(auth_result, tuple):
        return auth_result
    user_id_to_join = str(auth_result) # Asegurar que es string para consistencia

    json_data = request.get_json()
    # comprobarRequest ya verifica si json_data existe, pero no si 'clave' está.
    if not json_data or 'clave' not in json_data:
        return jsonify({'message': 'Falta el campo requerido (clave) en el JSON'}), 400
    
    clave_proporcionada = json_data.get('clave')

    chat = Chat.query.where(Chat.clave == clave_proporcionada).first()
    if chat is None:
        return jsonify({'message': 'Chat no encontrado'}), 404
    
    if chat.clave != clave_proporcionada:
        return jsonify({'message': 'Clave incorrecta'}), 403 # 403 Forbidden es más apropiado aquí

    # Procesar la lista de usuarios actual en el chat
    # Asumiendo que chat.usuarios es como ";id1;id2;id3;"
    current_user_ids = [uid for uid in chat.usuarios.split(';') if uid] # Filtra cadenas vacías

    # Verificar si el usuario ya está en el chat
    if user_id_to_join in current_user_ids:
        return jsonify({'message': 'Ya estás en este chat'}), 409 # 409 Conflict

    # Verificar si el chat está lleno
    if len(current_user_ids) >= chat.max_usu:
        return jsonify({'message': 'El chat está lleno'}), 403 # 403 Forbidden
    
    # Añadir el nuevo usuario
    try:
        current_user_ids.append(user_id_to_join)
        chat.usuarios = f";{';'.join(current_user_ids)};" # Reconstruye la cadena correctamente

        # db.session.add(chat) # No es estrictamente necesario si el objeto ya está en la sesión y se modifica
        db.session.commit()
        return jsonify({'message': 'Te has unido al chat exitosamente', 'nombre': chat.nombre}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al unirse al chat por usuario {user_id_to_join}: {str(e)}")
        return jsonify({'message': 'Error interno al unirse al chat'}), 500
    
    
def generar_clave_random():
    caracteres = string.ascii_letters + string.digits  # Letras mayúsculas, minúsculas y números
    clave = ''.join(random.choices(caracteres, k=10))
    return clave