from flask import request, jsonify, g
from app.models import db, Event, Section, Option, Vote
from app.utils.security import require_api_key, jwt_required, role_required
from datetime import datetime

@require_api_key('VOTES_API_KEY')
@jwt_required
@role_required('voter')
def cast_vote():
    data = request.get_json()

    required_fields = ['event_id', 'section_id', 'option_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing voting data'}), 400

    # Validar estado del usuario
    if g.user.get('status') != 'active':
        return jsonify({'error': 'User is not active'}), 403

    event = Event.query.get(data['event_id'])
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    now = datetime.utcnow()
    if not (event.start_datetime <= now <= event.end_datetime):
        return jsonify({'error': 'Voting is closed for this event'}), 403

    section = Section.query.filter_by(id=data['section_id'], event_id=event.id).first()
    if not section:
        return jsonify({'error': 'Section not found in this event'}), 404

    option = Option.query.filter_by(id=data['option_id'], section_id=section.id).first()
    if not option:
        return jsonify({'error': 'Option not found in this section'}), 404

    # Validar si ya votó
    existing_vote = Vote.query.filter_by(user_id=g.user['user_id'], section_id=section.id).first()
    if existing_vote:
        return jsonify({'error': 'You have already voted in this section'}), 409

    vote = Vote(
        user_id=g.user['user_id'],
        option_id=option.id,
        section_id=section.id
    )
    db.session.add(vote)
    db.session.commit()

    return jsonify({'message': 'Vote cast successfully'}), 201
