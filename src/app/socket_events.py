from flask_socketio import emit
from flask import request
import logging
from .socket_auth import authenticated_only, check_token_on_connect

logger = logging.getLogger(__name__)

# Lista para almacenar mensajes
mensajes = []

def configure_socket_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        logger.info(f"Intento de conexión desde {request.sid}")
        
        # Verificar el token JWT al conectarse
        if not check_token_on_connect():
            logger.warning(f"Conexión rechazada para {request.sid}")
            return False
        
        logger.info(f"Cliente conectado: {request.sid}")
        # Enviar mensajes existentes al cliente que se conecta
        if mensajes:
            for mensaje in mensajes:
                emit('recibir_mensaje', mensaje, to=request.sid)
        
        # Confirmar conexión exitosa con datos del usuario
        user_info = getattr(request, 'user_info', {})
        user_id = user_info.get('sub', 'unknown')
        
        emit('conexion_exitosa', {
            'status': 'connected',
            'user_id': user_id
        })

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f"Cliente desconectado: {request.sid}")

    @socketio.on('enviar_mensaje')
    @authenticated_only
    def handle_message(data):
        logger.info(f"Mensaje recibido: {data}")
        
        # Validar datos del mensaje
        if not isinstance(data, dict) or 'usuario' not in data or 'texto' not in data:
            logger.error(f"Formato de mensaje inválido: {data}")
            emit('error', {"error": "Datos incompletos"})
            return
        
        # Guardar el mensaje en la lista
        mensajes.append(data)
        
        # Limitar la cantidad de mensajes almacenados
        if len(mensajes) > 100:
            mensajes.pop(0)
        
        # Emitir el mensaje a todos los clientes excepto al emisor
        emit('recibir_mensaje', data, broadcast=True, include_self=False)
        
        # Confirmar al emisor que su mensaje fue enviado
        emit('mensaje_enviado', data)
        
        logger.info(f"Mensaje enviado a todos excepto al emisor: {data}") 