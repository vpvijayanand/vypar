from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin):
    """User model - database columns will be set by db after app initialization"""
    
    def __init__(self, username=None, email=None, is_admin=False):
        self.username = username
        self.email = email
        self.is_admin = is_admin
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

def init_db_models(db):
    """Initialize database models after db is created"""
    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        is_admin = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def set_password(self, password):
            """Hash and set the password"""
            self.password_hash = generate_password_hash(password)
        
        def check_password(self, password):
            """Check if the provided password matches the hash"""
            return check_password_hash(self.password_hash, password)
        
        def __repr__(self):
            return f'<User {self.username}>'
    
    return User

def create_user_model(db):
    """Alias for init_db_models for backward compatibility"""
    return init_db_models(db)
