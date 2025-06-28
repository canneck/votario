from flask import Blueprint
from app.controllers import admin, auth, votes, events, sections, options, voting_locations

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
votario.add_url_rule('/events', view_func=events.create, methods=['POST'], endpoint='create_event')
votario.add_url_rule('/events', view_func=events.get_all, methods=['GET'], endpoint='get_all_event')
votario.add_url_rule('/events/<int:event_id>', view_func=events.get_by_id, methods=['GET'], endpoint='get_event_by_id')
votario.add_url_rule('/events/<int:event_id>', view_func=events.update, methods=['PUT'], endpoint='update_event')
votario.add_url_rule('/events/<int:event_id>/status', view_func=events.update_status, methods=['PATCH'], endpoint='update_status_event')
votario.add_url_rule('/events/<int:event_id>', view_func=events.delete, methods=['DELETE'], endpoint='delete_event')

# sections
votario.add_url_rule('/sections', view_func=sections.create, methods=['POST'], endpoint='create_section')
votario.add_url_rule('/sections', view_func=sections.get_all, methods=['GET'], endpoint='get_all_section')
votario.add_url_rule('/sections/<int:section_id>', view_func=sections.get_by_id, methods=['GET'], endpoint='get_section_by_id')
votario.add_url_rule('/sections/<int:section_id>', view_func=sections.update, methods=['PUT'], endpoint='update_section')
votario.add_url_rule('/sections/<int:section_id>/status', view_func=sections.update_status, methods=['PATCH'], endpoint='update_status_section')
votario.add_url_rule('/sections/<int:section_id>', view_func=sections.delete, methods=['DELETE'], endpoint='delete_section')

# options
votario.add_url_rule('/options', view_func=options.create, methods=['POST'], endpoint='create_option')
votario.add_url_rule('/options', view_func=options.get_all, methods=['GET'], endpoint='get_all_option')
votario.add_url_rule('/options/<int:option_id>', view_func=options.get_by_id, methods=['GET'], endpoint='get_option_by_id')
votario.add_url_rule('/options/<int:option_id>', view_func=options.update, methods=['PUT'], endpoint='update_option')
votario.add_url_rule('/options/<int:option_id>/status', view_func=options.update_status, methods=['PATCH'], endpoint='update_status_option')
votario.add_url_rule('/options/<int:option_id>', view_func=options.delete, methods=['DELETE'], endpoint='delete_option')

# voting locations
votario.add_url_rule('/locations', view_func=voting_locations.create, methods=['POST'], endpoint='create_voting_location')
votario.add_url_rule('/locations', view_func=voting_locations.get_all, methods=['GET'], endpoint='get_all_voting_location')
votario.add_url_rule('/locations/<int:option_id>', view_func=voting_locations.get_by_id, methods=['GET'], endpoint='get_voting_location')
votario.add_url_rule('/locations/<int:option_id>', view_func=voting_locations.update, methods=['PUT'], endpoint='update_voting_location')
votario.add_url_rule('/locations/<int:option_id>/status', view_func=voting_locations.update_status, methods=['PATCH'], endpoint='update_status_voting_location')
votario.add_url_rule('/locations/<int:option_id>', view_func=voting_locations.delete, methods=['DELETE'], endpoint='delete_voting_location')