"""
Utility decorators and helpers for routes.
"""
from functools import wraps
from flask import jsonify, request, current_app
from flask_login import current_user, login_required
import jwt
from datetime import datetime, timezone, timedelta
from app.models.user import User


def admin_required(f):
    """Decorator to restrict access to admin users."""
    @wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return wrapper


def get_company_id():
    """Get company_id from current user context."""
    if current_user and current_user.is_authenticated:
        return current_user.company_id
    return None


def api_response(data=None, message='Success', status=200, pagination=None):
    """Standard API response format for mobile-ready JSON."""
    response = {
        'success': 200 <= status < 300,
        'message': message,
    }
    if data is not None:
        response['data'] = data
    if pagination:
        response['pagination'] = {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        }
    return jsonify(response), status


def api_error(message='An error occurred', status=400, errors=None):
    """Standard API error response."""
    response = {
        'success': False,
        'message': message,
    }
    if errors:
        response['errors'] = errors
    return jsonify(response), status


# ─── JWT Token Helpers (for mobile API) ──────────────────────────────────────

def generate_jwt_token(user_id):
    """Generate JWT token for mobile API authentication."""
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(
            seconds=current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 86400)
        ),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def jwt_required(f):
    """Decorator for JWT-authenticated mobile API endpoints."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')

        if auth_header.startswith('Bearer '):
            token = auth_header[7:]

        if not token:
            return api_error('Authentication token required', 401)

        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user = User.query.get(payload['user_id'])
            if not user or not user.is_active:
                return api_error('Invalid or expired token', 401)
            # Attach user to request context
            request.jwt_user = user
        except jwt.ExpiredSignatureError:
            return api_error('Token has expired', 401)
        except jwt.InvalidTokenError:
            return api_error('Invalid token', 401)

        return f(*args, **kwargs)
    return wrapper


def get_json_or_form():
    """Get request data from JSON body or form data (mobile + web compatible)."""
    if request.is_json:
        return request.get_json()
    return request.form.to_dict()
