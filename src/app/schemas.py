from .db import ma
from .models import Usuarios

class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuarios
        fields = ('id', 'nombre', 'contrasenia')

usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)
