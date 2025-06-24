from flask import Blueprint
from app.controllers import admin, auth

votario = Blueprint('votario', __name__)

# Admin routes
votario.add_url_rule('/', view_func=admin.home)
votario.add_url_rule('/admin/seed', view_func=admin.seed_roles, methods=['POST'])

# Auth routes
votario.add_url_rule('/auth/protected', view_func=auth.protected_route, methods=['GET'])
votario.add_url_rule('/auth/register', view_func=auth.register, methods=['POST'])
votario.add_url_rule('/auth/login', view_func=auth.login, methods=['POST'])
votario.add_url_rule('/auth/seed', view_func=auth.seed_users, methods=['POST'])