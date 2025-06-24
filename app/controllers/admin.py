from flask import jsonify, g
from app.models import db, Role
from app.utils.security import require_api_key, jwt_required, role_required

@require_api_key('ADMIN_API_KEY')
def home():
    return {'message': 'Votario is running ✅ - ok'}


@require_api_key('ADMIN_API_KEY')
@jwt_required
@role_required('admin')
def seed_roles():
    from flask import jsonify
    from app.models import db, Role

    roles = ['admin', 'moderator', 'voter']
    created = []

    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name))
            created.append(role_name)

    if created:
        db.session.commit()
        return jsonify({'message': 'Roles created', 'created': created}), 201
    else:
        return jsonify({'message': 'No roles created, all already exist'}), 200
