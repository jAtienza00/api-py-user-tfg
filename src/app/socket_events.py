from flask_socketio import emit, join_room, leave_room
from flask import request
import logging
from .socket_auth import authenticated_only, check_token_on_connect

logger = logging.getLogger(__name__)

# Lista para almacenar mensajes
mensajes_por_room = {}

def configure_socket_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        
        # Verificar el token JWT al conectarse
        if not check_token_on_connect():
            logger.warning(f"Conexión rechazada para {request.sid}")
            return False
        
        logger.info(f"Cliente conectado: {request.sid}")
        
        # Confirmar conexión exitosa con datos del usuario
        user_info = getattr(request, 'user_info', {})
        user_id = user_info.get('sub', 'unknown')
        
        room_id = request.args.get('room')
        if room_id:
            join_room(room_id)
            logger.info(f"Cliente {request.sid} se unió automáticamente a la sala {room_id} al conectar.")
            if room_id in mensajes_por_room:
                for mensaje in mensajes_por_room[room_id]:
                    emit('recibir_mensaje', mensaje, to=request.sid)
            emit('room_joined', {'room': room_id}, to=request.sid)
            
        emit('conexion_exitosa', {
            'status': 'connected',
            'user_id': user_id
        })

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f"Cliente desconectado: {request.sid}")
        
        
    @socketio.on('join_room')
    @authenticated_only
    def handle_join_room(data):
        if not isinstance(data, dict) or 'room' not in data:
            emit('error', {"error": "Datos de sala incompletos"}, to=request.sid)
            return
        room = data['room']
        join_room(room)
        logger.info(f"Cliente {request.sid} se unió a la sala {room} (vía evento).")
        if room in mensajes_por_room:
            for mensaje in mensajes_por_room[room]:
                emit('recibir_mensaje', mensaje, to=request.sid)
        emit('room_joined', {'room': room}, to=request.sid)

    @socketio.on('enviar_mensaje')
    @authenticated_only
    def handle_message(data):
        logger.info(f"Mensaje recibido: {data}")
        
        # Validar datos del mensaje
        if not isinstance(data, dict) or \
           'usuario' not in data or \
           'texto' not in data or \
           'room' not in data:  # Asegurarse que salaId (o el nombre que elijas) esté en el payload
            logger.error(f"Formato de mensaje inválido o salaId faltante: {data}")
            emit('error', {"error": "Datos incompletos o salaId faltante en el mensaje"}, to=request.sid)
            return
        
        # Usar salaId del payload del mensaje como la sala de destino
        sala = data['room'] 
        
        # Guardar el mensaje en la lista, inicializando la lista para la sala si es nueva
        mensajes_por_room.setdefault(sala, []).append(data)
        # Emitir el mensaje a todos los clientes en la 'sala' especificada, excepto al emisor
        emit('recibir_mensaje', data, broadcast=True, include_self=False, to=sala)
        
        logger.info(f"Mensaje enviado a la sala '{sala}' (excepto al emisor): {data}")
