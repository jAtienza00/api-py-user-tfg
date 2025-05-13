import datetime
import os
import pytz
import jwt
import logging

logger = logging.getLogger(__name__)

class Security():
    
    tz = pytz.timezone('US/Eastern')
    
    @classmethod
    def generarToken(cls, usuario):
        payload={
            'iat': datetime.datetime.now(tz = cls.tz),
            'exp': datetime.datetime.now(tz = cls.tz) + datetime.timedelta(minutes=60*24*1),
            'sub': usuario.id
        }
        return jwt.encode(payload, os.environ.get("JWT_SECRET"), algorithm= os.environ.get("JWT_ALGORITHM",'HS256'))
    
    @classmethod
    def verificar(cls, headers):
        if 'Authorization' in headers.keys():
          auth = headers['Authorization'].split(" ")[1]
          try:
            payload = jwt.decode(auth, os.environ.get("JWT_SECRET"), algorithms=[os.environ.get("JWT_ALGORITHM",'HS256')])
            return True
          except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return False
        return False
    
    @classmethod
    def decode_token(cls, token):
        """Decodificar y validar el token JWT.
        
        Args:
            token (str): Token JWT a decodificar
            
        Returns:
            dict: Payload del token si es válido, None en caso contrario
        """
        try:
            # Obtener la clave JWT_SECRET desde las variables de entorno
            secret_key = os.environ.get("JWT_SECRET")
            
            if not secret_key:
                logger.error("JWT_SECRET no está configurado en las variables de entorno")
                return None
                
            # Decodificar el token usando la clave secreta
            decoded = jwt.decode(token, secret_key, algorithms=[os.environ.get("JWT_ALGORITHM",'HS256')])
            logger.info(f"Token decodificado correctamente")
            return decoded
                
        except jwt.ExpiredSignatureError:
            logger.error("Token expirado")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Token inválido: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al decodificar token: {str(e)}")
            return None