from flask import Blueprint, request, jsonify
from .usuarioController import comprobarConexion, create_usuario, show_usuarios, show_usuario, update_usuario, delete_usuario
from .auth import Security

api_blueprint = Blueprint('api', __name__)

api_blueprint.route('/', methods=['GET'])(comprobarConexion)
api_blueprint.route('/usuarios', methods=['POST'])(create_usuario)
api_blueprint.route('/usuarios', methods=['GET'])(show_usuarios)
api_blueprint.route('/usuarios/<int:id>', methods=['GET'])(show_usuario)
api_blueprint.route('/usuarios/<int:id>', methods=['PUT'])(update_usuario)
api_blueprint.route('/usuarios/<int:id>', methods=['DELETE'])(delete_usuario)
