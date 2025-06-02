from .db import ma
from .models import Usuarios
from .models import Chat

class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuarios
        fields = ('id', 'nombre', 'email')

class ChatSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Chat
        fields = ('id', 'nombre', 'usuarios', 'max_usu', 'clave', 'usuario_id', 'chats_usuarios_FK')

class ChatResumenSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Chat
        fields = ('id', 'nombre', 'clave')


chat_schema = ChatSchema()
chats_schema = ChatSchema(many=True)
chat_resumen_schema = ChatResumenSchema()
chats_resumen_schema = ChatResumenSchema(many=True)
usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)
