from flask import request, jsonify
from app.models import db, Event
from app.utils.security import require_api_key, jwt_required, role_required, active_user_required
from datetime import datetime

@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def create():
    data = request.get_json()

    required_fields = ['name', 'start_datetime', 'end_datetime']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        start = datetime.fromisoformat(data['start_datetime'])
        end = datetime.fromisoformat(data['end_datetime'])
        if end <= start:
            return jsonify({"error": "End datetime must be after start datetime"}), 400
    except Exception:
        return jsonify({"error": "Invalid datetime format. Use ISO 8601"}), 400

    new_event = Event(
        name=data['name'],
        description=data.get('description'),
        start_datetime=start,
        end_datetime=end,
        country=data.get('country', 'Peru'),
        region=data.get('region'),
        province=data.get('province'),
        district=data.get('district'),
        is_public=data.get('is_public', False),
        require_authentication=data.get('require_authentication', True),
        allow_multiple_votes=data.get('allow_multiple_votes', False)
    )

    db.session.add(new_event)
    db.session.commit()

    return jsonify({
        "message": "Event created successfully",
        "event_id": new_event.id
    }), 201


@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def get_all():
    events = Event.query.filter(Event.status != 'deleted').all()
    return jsonify([
        {
            "id": e.id,
            "name": e.name,
            "description": e.description,
            "start_datetime": e.start_datetime.isoformat(),
            "end_datetime": e.end_datetime.isoformat(),
            "status": e.status
        }
        for e in events
    ]), 200


@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def get_by_id(event_id):
    event = Event.query.get(event_id)
    if not event or event.status == 'deleted':
        return jsonify({"error": "Event not found"}), 404

    return jsonify({
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "start_datetime": event.start_datetime.isoformat(),
        "end_datetime": event.end_datetime.isoformat(),
        "status": event.status
    }), 200


@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def update(event_id):
    data = request.get_json()
    event = Event.query.get(event_id)

    if not event or event.status == 'deleted':
        return jsonify({"error": "Event not found"}), 404

    # Campos opcionales para actualizar
    for field in ['name', 'description', 'start_datetime', 'end_datetime']:
        if field in data:
            setattr(event, field, data[field])

    db.session.commit()
    return jsonify({"message": "Event updated"}), 200


@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def update_status(event_id):
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['active', 'inactive', 'deleted']:
        return jsonify({"error": "Invalid status value"}), 400

    event = Event.query.get(event_id)
    if not event or event.status == 'deleted':
        return jsonify({"error": "Event not found"}), 404

    event.status = new_status
    db.session.commit()

    return jsonify({"message": f"Event status updated to '{new_status}'"}), 200


@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def delete(event_id):
    event = Event.query.get(event_id)

    if not event or event.status == 'deleted':
        return jsonify({"error": "Event not found"}), 404

    event.status = 'deleted'
    db.session.commit()
    return jsonify({"message": "Event deleted (soft)"}), 200