import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-por-defecto-votario')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:tu_contraseña@localhost:5432/votario_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
