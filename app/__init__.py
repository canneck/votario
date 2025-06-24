from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

from .models import db  # Ya contiene la instancia de SQLAlchemy

load_dotenv()  # Cargar variables de entorno desde .env

def create_app():
    app = Flask(__name__)

    # Configuración desde variables de entorno
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'changeme-in-production')

    # Inicializar base de datos
    db.init_app(app)

    # Registrar blueprint (después de configurar todo)
    from .routes import votario
    app.register_blueprint(votario)


    return app
