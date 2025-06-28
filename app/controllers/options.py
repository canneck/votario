from flask import request, jsonify, g
from app.models import db, Option, Section, Event
from app.utils.security import require_api_key, jwt_required, role_required, active_user_required
from datetime import datetime

@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def create():
    data = request.get_json()

    required_fields = ['label', 'image_url', 'section_id']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    new_option = Option(
        label = data['label'],
        description = data.get('description'),
        image_url = data['image_url'],
        section_id = data['section_id'],
        created_by = g.user['user_id']
    )

    db.session.add(new_option)
    db.session.commit()

    return jsonify({
        "message": "Option created successfully",
        "option_id": new_option.id
    }), 201


@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def get_all():
    options = db.session.query(Option, Section, Event).\
        join(Section, Option.section_id == Section.id).\
        join(Event, Section.event_id == Event.id).\
        filter(
            Option.status != 'deleted',
            Section.status != 'deleted',
            Event.status != 'deleted'
        ).all()

    return jsonify([
        {
            "id": option.id,
            "label": option.label,
            "description": option.description,
            "image_url": option.image_url,
            "status": option.status,
            "section_name": section.name,
            "event_name": event.name
        }
        for option, section, event in options
    ]), 200


@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def get_by_id(option_id):
    option = Option.query.get(option_id)
    if not option or option.status == 'deleted':
        return jsonify({"error": "Option not found"}), 404

    return jsonify({
        "id": option.id,
        "label": option.label,
        "description": option.description,
        "image_url": option.image_url,
        "status": option.status
    }), 200


@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def update(option_id):
    data = request.get_json()
    option = Option.query.get(option_id)

    if not option or option.status == 'deleted':
        return jsonify({"error": "Option not found"}), 404

    # Campos opcionales para actualizar
    for field in ['label', 'description', 'image_url']:
        if field in data:
            setattr(option, field, data[field])

    db.session.commit()
    return jsonify({"message": "Option updated"}), 200


@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def update_status(option_id):
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['active', 'inactive', 'deleted']:
        return jsonify({"error": "Invalid status value"}), 400

    option = Option.query.get(option_id)
    if not option or option.status == 'deleted':
        return jsonify({"error": "Option not found"}), 404

    option.status = new_status
    db.session.commit()

    return jsonify({"message": f"Option status updated to '{new_status}'"}), 200


@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def delete(option_id):
    option = Option.query.get(option_id)

    if not option or option.status == 'deleted':
        return jsonify({"error": "Option not found"}), 404

    option.status = 'deleted'
    db.session.commit()
    return jsonify({"message": "Option deleted (soft)"}), 200