import os
import jwt
from functools import wraps
from flask import request, current_app
from flask_socketio import disconnect
import logging
from dotenv import load_dotenv
from .auth import Security

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

def get_token_from_request():
    """Obtener el token JWT de los parámetros de consulta o los headers de la solicitud."""
    # Intentar obtener el token desde query string
    token = request.args.get('token')
    
    # Si no está en query string, intentar obtenerlo de los headers
    if not token and request.headers.get('Authorization'):
        auth_header = request.headers.get('Authorization')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    # Si no está en headers, intentar obtenerlo del objeto auth
    if not token and hasattr(request, 'auth') and request.auth and 'token' in request.auth:
        token = request.auth.get('token')
    
    # Intentar obtenerlo de los cookies (algunos clientes los envían así)
    if not token and request.cookies and 'token' in request.cookies:
        token = request.cookies.get('token')
        
    if token:
        logger.info(f"Token obtenido de la solicitud: {token[:20]}... (truncado)")
    return token

def authenticated_only(f):
    """Decorador para proteger eventos de socket y requieren autenticación."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            logger.warning("No se proporcionó token de autenticación")
            disconnect()
            return False
        
        decoded_token = Security.decode_token(token)
        if not decoded_token:
            logger.warning("Token de autenticación inválido")
            disconnect()
            return False
        
        # Agregar información del usuario al request para uso en el controlador
        request.user_info = decoded_token
        
        return f(*args, **kwargs)
    return wrapped

def check_token_on_connect(token=None):
    """Verificar el token JWT al conectarse al socket."""
    # Si se proporciona el token directamente, usarlo
    if not token:
        token = get_token_from_request()
    
    logger.info(f"Verificando token en conexión")
    
    if not token:
        logger.warning("Intento de conexión sin token")
        return False
    
    decoded_token = Security.decode_token(token)
    if not decoded_token:
        logger.warning("Intento de conexión con token inválido")
        return False
    
    # Almacenar información del usuario en request para uso futuro
    request.user_info = decoded_token
    
    logger.info(f"Usuario autenticado: {decoded_token}")
    return True 