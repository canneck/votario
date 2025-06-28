from flask import request, jsonify, g
from app.models import db, VotingLocation
from app.utils.security import require_api_key, jwt_required, role_required, active_user_required
import secrets

@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def create():
    data = request.get_json()

    required_fields = ['name', 'region', 'province', 'district']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    api_key = data.get('api_key') or secrets.token_hex(32)

    new_location = VotingLocation(
        name=data['name'],
        coordinates=data.get('coordinates'),
        address=data.get('address'),
        region=data['region'],
        province=data['province'],
        district=data['district'],
        api_key=api_key,
        created_by=g.user['user_id']
    )

    db.session.add(new_location)
    db.session.commit()

    return jsonify({
        "message": "Voting location created",
        "id": new_location.id,
        "api_key": api_key
    }), 201

@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def get_all():
    locations = VotingLocation.query.all()
    return jsonify([
        {
            "id": loc.id,
            "name": loc.name,
            "coordinates": loc.coordinates,
            "address": loc.address,
            "region": loc.region,
            "province": loc.province,
            "district": loc.district,
            "api_key": loc.api_key
        } for loc in locations
    ]), 200

@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def get_by_id(location_id):
    loc = VotingLocation.query.get(location_id)
    if not loc:
        return jsonify({"error": "Voting location not found"}), 404

    return jsonify({
        "id": loc.id,
        "name": loc.name,
        "coordinates": loc.coordinates,
        "address": loc.address,
        "region": loc.region,
        "province": loc.province,
        "district": loc.district,
        "api_key": loc.api_key
    }), 200

@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def update(location_id):
    loc = VotingLocation.query.get(location_id)
    if not loc:
        return jsonify({"error": "Voting location not found"}), 404

    data = request.get_json()
    for field in ['name', 'coordinates', 'address', 'region', 'province', 'district']:
        if field in data:
            setattr(loc, field, data[field])

    loc.modified_by = g.user['user_id']
    db.session.commit()
    return jsonify({"message": "Voting location updated"}), 200

@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def update_status(location_id):
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['active', 'inactive', 'deleted']:
        return jsonify({"error": "Invalid status value"}), 400

    location = VotingLocation.query.get(location_id)
    if not location or location.status == 'deleted':
        return jsonify({"error": "Location not found"}), 404

    location.status = new_status
    location.modified_by = g.user['user_id']
    db.session.commit()

    return jsonify({"message": f"Location status updated to '{new_status}'"}), 200


@require_api_key('ADMIN_API_KEY')
@jwt_required
@active_user_required
@role_required('admin')
def delete(location_id):
    loc = VotingLocation.query.get(location_id)
    if not loc:
        return jsonify({"error": "Voting location not found"}), 404

    db.session.delete(loc)
    db.session.commit()
    return jsonify({"message": "Voting location deleted"}), 200
