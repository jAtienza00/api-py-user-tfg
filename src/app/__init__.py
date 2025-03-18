from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from .config import Config
from .db import db, ma
from .routes import api_blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={r"/*": {"origins": "*"}})
    Swagger(app)
    app.config.from_object(Config)
    db.init_app(app)
    ma.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(api_blueprint)

    return app
