from functools import wraps
from flask import request, jsonify, g
from datetime import datetime, timedelta
from app.models import db, RequestLog

def rate_limit(limit=5, seconds=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            route = request.path
            user_id = getattr(g.user, 'user_id', None) if hasattr(g, 'user') else None
            window_start = datetime.utcnow() - timedelta(seconds=seconds)

            query = RequestLog.query.filter(
                RequestLog.ip == ip,
                RequestLog.route == route,
                RequestLog.timestamp >= window_start
            )

            if user_id:
                query = query.filter(RequestLog.user_id == user_id)

            recent_requests = query.count()

            if recent_requests >= limit:
                return jsonify({
                    'error': 'Too many requests. Please wait before trying again.'
                }), 429

            # Log this request
            log = RequestLog(ip=ip, route=route, user_id=user_id, timestamp=datetime.utcnow())
            db.session.add(log)
            db.session.commit()

            return f(*args, **kwargs)
        return decorated_function
    return decorator
