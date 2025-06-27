from flask import Blueprint
from app.controllers import admin, auth, votes, events

votario = Blueprint('votario', __name__)

# Admin routes
votario.add_url_rule('/', view_func=admin.home)
votario.add_url_rule('/admin/seed', view_func=admin.seed_roles, methods=['POST'])

# Auth routes
votario.add_url_rule('/auth/protected', view_func=auth.protected_route, methods=['GET'])
votario.add_url_rule('/auth/register', view_func=auth.register, methods=['POST'])
votario.add_url_rule('/auth/login', view_func=auth.login, methods=['POST'])
votario.add_url_rule('/auth/seed', view_func=auth.seed_users, methods=['POST'])

# voting routes
votario.add_url_rule('/vote', view_func=votes.cast_vote, methods=['POST'])

# events
votario.add_url_rule('/events', view_func=events.create, methods=['POST'])
votario.add_url_rule('/events', view_func=events.get_all, methods=['GET'])
votario.add_url_rule('/events/<int:event_id>', view_func=events.get_by_id, methods=['GET'])
votario.add_url_rule('/events/<int:event_id>', view_func=events.update, methods=['PUT'])
votario.add_url_rule('/events/<int:event_id>/status', view_func=events.update_status, methods=['PATCH'])
votario.add_url_rule('/events/<int:event_id>', view_func=events.delete, methods=['DELETE'])