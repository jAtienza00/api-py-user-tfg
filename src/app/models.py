import bcrypt
from .db import db

salt = bcrypt.gensalt()

class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    contrasenia = db.Column(db.String(60), nullable=False)

    def __init__(self, nombre, contrasenia):
        self.setNombre(nombre)
        self.setContrasenia(contrasenia.encode('utf-8'))
        
    def setNombre(self, nombre):
        self.nombre = nombre
        
    def setContrasenia(self, contrasenia):
        self.contrasenia = bcrypt.hashpw(contrasenia, salt).decode('utf-8')
