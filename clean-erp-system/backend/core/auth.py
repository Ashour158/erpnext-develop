# Clean ERP System - Authentication & Authorization
# Complete auth system without Frappe dependencies

from flask import current_app, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
from datetime import datetime, timedelta
import secrets
import string

# Initialize JWT
jwt_manager = JWTManager()

class AuthManager:
    """Complete authentication and authorization system"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize authentication with Flask app"""
        jwt_manager.init_app(app)
        
        # JWT configuration
        app.config['JWT_SECRET_KEY'] = app.config.get('SECRET_KEY', 'your-secret-key')
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
        app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
        app.config['JWT_BLACKLIST_ENABLED'] = True
        app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    
    def hash_password(self, password):
        """Hash password securely"""
        return generate_password_hash(password)
    
    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        return check_password_hash(password_hash, password)
    
    def generate_tokens(self, user_id, username, role=None):
        """Generate access and refresh tokens"""
        access_token = create_access_token(
            identity=user_id,
            additional_claims={
                'username': username,
                'role': role or 'user'
            }
        )
        refresh_token = create_refresh_token(identity=user_id)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_current_user(self):
        """Get current authenticated user"""
        user_id = get_jwt_identity()
        if user_id:
            from .database import User, DatabaseUtils
            return DatabaseUtils.get_by_id(User, user_id)
        return None
    
    def require_auth(self, f):
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'No token provided'}), 401
            
            try:
                if token.startswith('Bearer '):
                    token = token[7:]
                
                payload = self.verify_token(token)
                if not payload:
                    return jsonify({'error': 'Invalid token'}), 401
                
                request.current_user_id = payload['sub']
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Token verification failed'}), 401
        
        return decorated_function
    
    def require_role(self, *roles):
        """Decorator to require specific role"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user = self.get_current_user()
                if not user:
                    return jsonify({'error': 'Authentication required'}), 401
                
                if user.role not in roles:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def require_permission(self, permission):
        """Decorator to require specific permission"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user = self.get_current_user()
                if not user:
                    return jsonify({'error': 'Authentication required'}), 401
                
                if not self.has_permission(user, permission):
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def has_permission(self, user, permission):
        """Check if user has specific permission"""
        if not user or not user.permissions:
            return False
        
        # Check if user has the permission
        if permission in user.permissions:
            return user.permissions[permission]
        
        # Check role-based permissions
        role_permissions = {
            'admin': ['*'],  # Admin has all permissions
            'manager': ['read', 'write', 'update'],
            'user': ['read']
        }
        
        if user.role in role_permissions:
            user_perms = role_permissions[user.role]
            return '*' in user_perms or permission in user_perms
        
        return False
    
    def generate_api_key(self, user_id, name=None):
        """Generate API key for user"""
        api_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        
        # Store API key in database
        from .database import APIKey, DatabaseUtils
        api_key_data = {
            'user_id': user_id,
            'key': api_key,
            'name': name or 'Default API Key',
            'is_active': True
        }
        
        DatabaseUtils.create(APIKey, api_key_data)
        return api_key
    
    def verify_api_key(self, api_key):
        """Verify API key"""
        from .database import APIKey, DatabaseUtils
        key_record = DatabaseUtils.get_by_filters(APIKey, {'key': api_key, 'is_active': True})
        return key_record

# API Key Model
class APIKey(BaseModel):
    """API Key model for programmatic access"""
    __tablename__ = 'api_keys'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """Convert API key to dictionary"""
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'key': self.key,
            'name': self.name,
            'is_active': self.is_active,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        })
        return data

# Session Management
class Session(BaseModel):
    """User session model"""
    __tablename__ = 'sessions'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        """Convert session to dictionary"""
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'session_token': self.session_token,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        })
        return data

# Initialize auth manager
auth_manager = AuthManager()

# Convenience functions
def require_auth(f):
    """Decorator to require authentication"""
    return auth_manager.require_auth(f)

def require_role(*roles):
    """Decorator to require specific role"""
    return auth_manager.require_role(*roles)

def require_permission(permission):
    """Decorator to require specific permission"""
    return auth_manager.require_permission(permission)

def get_current_user():
    """Get current authenticated user"""
    return auth_manager.get_current_user()

def has_permission(user, permission):
    """Check if user has specific permission"""
    return auth_manager.has_permission(user, permission)
