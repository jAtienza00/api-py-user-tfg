from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from flask_socketio import SocketIO
from .config import Config
from .db import db, ma
from .routes import api_blueprint
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialización de SocketIO fuera de la función create_app
socketio = SocketIO(cors_allowed_origins="*", logger=True, engineio_logger=True)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "clave-secreta-predeterminada")
    
    CORS(app, supports_credentials=True, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
    }})
    Swagger(app)
    db.init_app(app)
    ma.init_app(app)

    # Inicialización de SocketIO con la app
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Configuración de eventos de Socket
    from .socket_events import configure_socket_events
    configure_socket_events(socketio)

    with app.app_context():
        db.create_all()

    app.register_blueprint(api_blueprint)
    
    logger.info("Aplicación Flask creada con SocketIO configurado")
    return app
