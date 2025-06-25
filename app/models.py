from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

# 🔁 Mixin para trazabilidad de creación y modificación
class AuditMixin(object):
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('vt_users.id'), nullable=True)
    modified_by = db.Column(db.Integer, db.ForeignKey('vt_users.id'), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='active')  # 'active', 'inactive', 'deleted'


class Role(db.Model, AuditMixin):
    __tablename__ = 'vt_roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # 'admin', 'voter', 'moderator'
    description = db.Column(db.String(150), nullable=True)

    users = db.relationship('User', backref='role', lazy=True, foreign_keys='User.role_id')

    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model, AuditMixin):
    __tablename__ = 'vt_users'
    id = db.Column(db.Integer, primary_key=True)

    # National ID fields (optional, for integration with RENIEC or similar)
    document_number = db.Column(db.String(15), unique=True, nullable=True)
    document_type = db.Column(db.String(10), nullable=True)  # 'DNI', 'CE', 'PASSPORT', etc.

    # Personal information
    first_name = db.Column(db.String(120), nullable=True)
    last_name = db.Column(db.String(120), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # 'M', 'F', 'Other'

    # Location (for regional voting or stats)
    country = db.Column(db.String(50), default='Peru')
    region = db.Column(db.String(50), nullable=True)     # Departamento
    province = db.Column(db.String(50), nullable=True)
    district = db.Column(db.String(50), nullable=True)
    
    failed_login_attempts = db.Column(db.Integer, default=0)

    # Internal login credentials
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Will be hashed later
    
    role_id = db.Column(db.Integer, db.ForeignKey('vt_roles.id'), nullable=False)

    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<User {self.email}>'


class Event(db.Model, AuditMixin):
    __tablename__ = 'vt_events'
    id = db.Column(db.Integer, primary_key=True)

    # Core information
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)

    # Location scope (optional, useful for regional or local elections)
    country = db.Column(db.String(50), default='Peru')
    region = db.Column(db.String(50), nullable=True)
    province = db.Column(db.String(50), nullable=True)
    district = db.Column(db.String(50), nullable=True)

    # Settings
    is_public = db.Column(db.Boolean, default=True)  # Visible sin login
    require_authentication = db.Column(db.Boolean, default=True)
    allow_multiple_votes = db.Column(db.Boolean, default=False)  # true = votaciones tipo encuesta

    # Relationship
    sections = db.relationship('Section', backref='event', lazy=True)

    def __repr__(self):
        return f'<Event {self.name}>'


class Section(db.Model, AuditMixin):
    __tablename__ = 'vt_sections'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)  # Ej: "Presidencia", "Congreso"
    description = db.Column(db.Text, nullable=True)

    # Relationship
    event_id = db.Column(db.Integer, db.ForeignKey('vt_events.id'), nullable=False)
    options = db.relationship('Option', backref='section', lazy=True)

    def __repr__(self):
        return f'<Section {self.name}>'


class Option(db.Model, AuditMixin):
    __tablename__ = 'vt_options'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    section_id = db.Column(db.Integer, db.ForeignKey('vt_sections.id'), nullable=False)
    votes = db.relationship('Vote', backref='option', lazy=True)

    def __repr__(self):
        return f'<Option {self.label}>'


class Vote(db.Model):
    __tablename__ = 'vt_votes'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('vt_users.id'), nullable=False, index=True)
    option_id = db.Column(db.Integer, db.ForeignKey('vt_options.id'), nullable=False, index=True)
    section_id = db.Column(db.Integer, db.ForeignKey('vt_sections.id'), nullable=False, index=True)

    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'section_id', name='unique_vote_per_user_per_section'),
    )

    def __repr__(self):
        return f'<Vote user={self.user_id} section={self.section_id} option={self.option_id}>'
