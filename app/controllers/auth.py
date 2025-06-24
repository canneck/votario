from flask import request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User
import datetime
from app.utils.security import require_api_key, generate_jwt, jwt_required, active_user_required, role_required

@require_api_key('AUTH_API_KEY')
@jwt_required
@active_user_required
@role_required('admin', 'moderator')
def protected_route():
    return jsonify({
        "message": "Acceso autorizado ✅",
        "user_id": g.user['user_id'],
        "role": g.user['role']
    }), 200

@require_api_key('AUTH_API_KEY')
@jwt_required
def register():
    data = request.get_json()

    required_fields = ['email', 'password', 'role_id']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Verificar si el email ya existe
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 409

    hashed_password = generate_password_hash(data['password'])

    new_user = User(
        email=data['email'],
        password=hashed_password,
        role_id=data['role_id'],
        created_at=datetime.datetime.utcnow()
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@require_api_key('AUTH_API_KEY')
def login():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    # Ahora usamos JWT real
    token = generate_jwt(user.id, user.role.name)

    return jsonify({
        "message": "Login ok",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role.name
        },
        "token": token
    }), 200


@require_api_key('AUTH_API_KEY')
@jwt_required
def seed_users():
    sample_users = [
        {"email": "admin@votario.com", "password": "admin123", "role_id": 1},
        {"email": "mod@votario.com", "password": "mod123", "role_id": 2},
        {"email": "voter@votario.com", "password": "voter123", "role_id": 3}
    ]

    created = []

    for user_data in sample_users:
        existing = User.query.filter_by(email=user_data['email']).first()
        if not existing:
            hashed_pw = generate_password_hash(user_data['password'])
            user = User(
                email=user_data['email'],
                password=hashed_pw,
                role_id=user_data['role_id'],
                created_at=datetime.datetime.utcnow()
            )
            db.session.add(user)
            created.append(user_data['email'])

    if created:
        db.session.commit()
        return jsonify({"message": "Users seeded", "created": created}), 201
    else:
        return jsonify({"message": "No users created, all already exist"}), 200
