import datetime
import pytz
import jwt

class Security():
    
    tz = pytz.timezone('US/Eastern')
    
    @classmethod
    def generarToken(cls, usuario):
        payload={
            'iat': datetime.datetime.now(tz = cls.tz),
            'exp': datetime.datetime.now(tz = cls.tz) + datetime.timedelta(minutes=30),
            'id': usuario.id
        }
        return jwt.encode(payload, 'D5*F?_1?-d$f*1', algorithm='HS256')
    
    @classmethod
    def verificar(cls, headers):
        if 'Authorization' in headers.keys():
          auth = headers['Authorization'].split(" ")[1]
          try:
            payload = jwt.decode(auth, 'D5*F?_1?-d$f*1', algorithms=['HS256'])
            return True
          except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return False
        return False