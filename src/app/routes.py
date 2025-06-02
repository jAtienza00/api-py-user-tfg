from flask import Blueprint, request, jsonify, render_template
from .usuarioController import comprobarConexion, create_usuario, show_usuarios, show_usuario, update_usuario, delete_usuario
from .auth import Security
from .chatsController import mostrarChats, crearChat, eliminarChat, mostrarChat, actualizarChat, unirseAChat, buscarChat

api_blueprint = Blueprint('api', __name__)

api_blueprint.route('/', methods=['GET'])(comprobarConexion)
api_blueprint.route('/usuarios', methods=['POST'])(create_usuario)
api_blueprint.route('/usuarios', methods=['GET'])(show_usuarios)
api_blueprint.route('/usuarios/<int:id>', methods=['GET'])(show_usuario)
api_blueprint.route('/usuarios/<int:id>', methods=['PUT'])(update_usuario)
api_blueprint.route('/usuarios/<int:id>', methods=['DELETE'])(delete_usuario)
api_blueprint.route('/chats/cargar', methods=['POST'])(mostrarChats) 
api_blueprint.route('/chats/crear', methods=['POST'])(crearChat) 
api_blueprint.route('/chats/eliminar/<int:chat_id>', methods=['POST'])(eliminarChat)
api_blueprint.route('/chats/mostrar/<int:chat_id>', methods=['POST'])(mostrarChat)
api_blueprint.route('/chats/actualizar/<int:chat_id>', methods=['POST'])(actualizarChat)
api_blueprint.route('/chats/unirse', methods=['POST'])(unirseAChat) 
api_blueprint.route('/chats/buscar', methods=['POST'])(buscarChat) 

