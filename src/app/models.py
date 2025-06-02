import bcrypt
from .db import db
from sqlalchemy.dialects.mysql import BIGINT as BigIntegerMySQL 

# salt = bcrypt.gensalt() # REMOVE: Global salt is insecure. Salt should be generated per password.
class Usuarios(db.Model):
    id = db.Column(BigIntegerMySQL(unsigned=True), primary_key=True, autoincrement=True) 
    nombre = db.Column(db.String(100), nullable=False)
    contrasenia = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(60), nullable=False, unique=True)

    def __init__(self, nombre, contrasenia, email):
        self.setNombre(nombre)
        self.setContrasenia(contrasenia) # Pass plain string, setContrasenia will handle encoding & hashing
        self.setEmail(email)
        
    def setNombre(self, nombre):
        self.nombre = nombre
        
    def setContrasenia(self, contrasenia_plain_text: str):
        if not isinstance(contrasenia_plain_text, str):
            # Or handle as an error appropriate for your application
            raise ValueError("Password must be a string.")
        # Hash the plain text password with a new salt each time
        hashed_pw = bcrypt.hashpw(contrasenia_plain_text.encode('utf-8'), bcrypt.gensalt())
        self.contrasenia = hashed_pw.decode('utf-8') # Store the full hash (salt included)
    def setEmail(self, email):
        self.email = email
        


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuarios = db.Column(db.Text, nullable=False)
    max_usu = db.Column(db.Integer, nullable=False)
    clave = db.Column(db.String(100), nullable=False, unique=True) 
    
    usuario_id = db.Column(BigIntegerMySQL(unsigned=True), db.ForeignKey('usuarios.id'), nullable=False) 

    chats_usuarios_FK = db.relationship('Usuarios', backref=db.backref('chats_creados', lazy=True))