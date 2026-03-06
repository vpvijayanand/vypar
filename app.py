from flask import Flask, redirect, url_for
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration from environment variables
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # PostgreSQL Database URI
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'wl_web_scraper')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    with app.app_context():
        # Import and create User model AFTER db is bound to app
        from models import init_db_models
        User = init_db_models(db)
        
        # Store User model and db in app config for blueprint access
        app.config['User'] = User
        app.config['db'] = db
        
        # Define user loader
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # Create tables
        db.create_all()
        
        # Seed admin user if it doesn't exist
        admin_exists = User.query.filter_by(username='admin').first()
        if not admin_exists:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("✓ Admin user created successfully!")
            print("  Username: admin")
            print("  Password: admin123")
        else:
            print("✓ Admin user already exists!")
    
    # Home route
    @app.route('/')
    def home():
        """Home page - redirect based on authentication status"""
        if current_user.is_authenticated:
            return redirect(url_for('users.dashboard'))
        return redirect(url_for('auth.login'))
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.users import users_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("\n🚀 Flask Admin Dashboard is running!")
    print("📍 Open http://localhost:5000 in your browser")
    print("🔓 Login with admin / admin123\n")
    app.run(debug=True)
