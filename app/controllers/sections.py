from flask import request, jsonify, g
from app.models import db, Section
from app.utils.security import require_api_key, jwt_required, role_required, active_user_required
from datetime import datetime

@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def create():
    data = request.get_json()
    
    required_fields = ['name', 'event_id']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    new_section = Section(
        name = data['name'],
        description = data.get('description'),
        event_id = data['event_id'],
        created_by = g.user['user_id']
    )
    
    db.session.add(new_section)
    db.session.commit()
    
    return jsonify ({
        "message": "Section created successfully",
        "event_id": new_section.id
    }), 201
    
    
@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def get_all():
    sections = Section.query.filter(Section.status != 'deleted').all()
    return jsonify([
        {
            "id": e.id,
            "name": e.name,
            "description": e.description,
            "status": e.status
        }
        for e in sections
    ]), 200
    
    
@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def get_by_id(section_id):
    section = Section.query.get(section_id)
    if not section or section.status == 'deleted':
        return jsonify({"error": "Section not found"}), 404

    return jsonify({
        "id": section.id,
        "name": section.name,
        "description": section.description,
        "status": section.status
    }), 200
    
    
@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def update(section_id):
    data = request.get_json()
    section = Section.query.get(section_id)

    if not section or section.status == 'deleted':
        return jsonify({"error": "Section not found"}), 404

    # Campos opcionales para actualizar
    for field in ['name', 'description']:
        if field in data:
            setattr(section, field, data[field])

    section.modified_by = g.user['user_id']

    db.session.commit()
    return jsonify({"message": "Section updated"}), 200


@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def update_status(section_id):
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['active', 'inactive', 'deleted']:
        return jsonify({"error": "Invalid status value"}), 400

    section = Section.query.get(section_id)
    if not section or section.status == 'deleted':
        return jsonify({"error": "Section not found"}), 404
    
    section.status = new_status
    section.modified_by = g.user['user_id']
    db.session.commit()

    return jsonify({"message": f"Section status updated to '{new_status}'"}), 200


@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def delete(section_id):
    section = Section.query.get(section_id)

    if not section or section.status == 'deleted':
        return jsonify({"error": "Section not found"}), 404

    section.status = 'deleted'
    section.modified_by = g.user['user_id']
    db.session.commit()
    return jsonify({"message": "Section deleted (soft)"}), 200