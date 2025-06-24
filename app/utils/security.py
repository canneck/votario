import os
from functools import wraps
from flask import request, jsonify, g
import jwt
import datetime
import os
from app.models import User

def require_api_key(env_key_name='ADMIN_API_KEY'):
    """
    Protege rutas usando una clave API tomada del .env.
    Puedes usar distintas claves según el tipo de ruta.
    Ejemplo: @require_api_key('AUTH_API_KEY')
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            api_key = request.headers.get('x-api-key')
            expected_key = os.getenv(env_key_name)

            if not api_key or api_key != expected_key:
                return jsonify({'message': 'Unauthorized: Invalid or missing API Key'}), 401

            return f(*args, **kwargs)
        return decorated
    return decorator


def generate_jwt(user_id, role_name, expires_in=360):
    """
    Genera un JWT con el ID de usuario y rol.
    - expires_in se mide en segundos (por defecto 1 hora).
    """
    user_agent = request.headers.get('User-Agent', 'unknown')
    payload = {
        'user_id': user_id,
        'role': role_name,
        "user_agent": user_agent,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
    }

    secret = os.getenv('JWT_SECRET_KEY', 'default-secret')
    token = jwt.encode(payload, secret, algorithm='HS256')

    return token


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid Authorization header'}), 401

        token = auth_header.split(' ')[1]
        secret_key = os.getenv('JWT_SECRET_KEY', 'default-secret')

        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])

            # Comparar el User-Agent actual con el del token
            current_ua = request.headers.get('User-Agent', 'unknown')
            if payload.get('user_agent') != current_ua:
                return jsonify({'error': 'User-Agent mismatch'}), 401

            g.user = payload  # Guardamos el usuario actual
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated


def active_user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = g.user.get('user_id')
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404
        if user.status != 'active':
            return jsonify({'error': 'User is not active'}), 403

        g.user_db = user  # opcional: guarda el objeto completo si lo necesitas en la vista

        return f(*args, **kwargs)
    return decorated


def role_required(*allowed_roles):
    """
    Asegura que el usuario tenga uno de los roles permitidos.
    Debe usarse después de @jwt_required.
    Ejemplo: @role_required('admin', 'moderator')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user'):
                return jsonify({'error': 'User context not found'}), 403

            user_role = g.user.get('role')
            if user_role not in allowed_roles:
                return jsonify({'error': f'Unauthorized: role "{user_role}" not allowed'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
