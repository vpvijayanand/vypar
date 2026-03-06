def seed_admin_user():
    """Seed the database with an admin user if it doesn't exist"""
    from app import db
    from models import User
    
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
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("Admin user already exists!")
