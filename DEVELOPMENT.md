# Development Guide

## Project Architecture

This Flask application follows the **Application Factory Pattern** with **Blueprint-based routing**.

### Key Components

1. **app.py** - Application factory and configuration
   - Creates Flask app instance
   - Initializes SQLAlchemy and Flask-Login
   - Creates User model and seeds admin user
   - Registers blueprints

2. **models.py** - Data models
   - `create_user_model(db)` - Factory function for User model
   - User attributes: username, email, password_hash, is_admin, timestamps
   - Password hashing with `set_password()` and `check_password()`

3. **routes/** - Route blueprints
   - `auth.py` - Authentication (login/logout)
   - `users.py` - User CRUD operations

4. **templates/** - Jinja2 templates
   - `base.html` - Base template with Bootstrap 5
   - Admin and user-specific views

## Database Schema

### User Table
```
id (Integer, PK)
├── username (String, Unique)
├── email (String, Unique)
├── password_hash (String)
├── is_admin (Boolean)
├── created_at (DateTime)
└── updated_at (DateTime)
```

## Authentication Flow

1. User visits `/auth/login`
2. Submits username and password
3. Check against User model with `check_password()`
4. Create session with `login_user(user)`
5. Redirect to dashboard

## Authorization

### Admin-Only Routes
- `/users/dashboard` (admin view)
- `/users/create`
- `/users/<id>/edit`
- `/users/<id>/delete`

### Protected Routes
- All `/users/*` routes require `@login_required`

### Admin Middleware
```python
@admin_required
def some_view():
    # Only admins can access
    pass
```

## Adding New Features

### Add a New User Attribute

1. **Update models.py**:
```python
class User(...):
    # ...existing fields...
    new_field = db.Column(db.String(100))
```

2. **Reset Database**:
   - Delete `instance/app.db`
   - Run app.py to recreate

3. **Update Templates**:
   - Add form field in create.html and edit.html
   - Display in view.html

4. **Update Routes**:
   - Handle new field in create() and edit() routes

### Add a New Blueprint

1. **Create routes/myfeature.py**:
```python
from flask import Blueprint
myfeature_bp = Blueprint('myfeature', __name__, url_prefix='/myfeature')

@myfeature_bp.route('/')
def index():
    return render_template('myfeature/index.html')
```

2. **Register in app.py**:
```python
from routes.myfeature import myfeature_bp
app.register_blueprint(myfeature_bp)
```

3. **Create templates/myfeature/** directory
4. **Create myfeature/index.html** template

## Testing Checklist

- [ ] Login with admin credentials
- [ ] Create a new user
- [ ] Edit the new user
- [ ] View the user profile
- [ ] Delete the user
- [ ] Login with different user
- [ ] Try accessing admin features (should be denied)
- [ ] Logout

## Code Style

This project follows these conventions:
- PEP 8 style guide
- Blueprint-based routing
- Jinja2 template inheritance
- Bootstrap 5 for styling
- Flask conventions

## Environment Variables

For production, create a `.env` file:
```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

## Database Migrations

For production, use Flask-Migrate:
```bash
pip install Flask-Migrate
flask db init
flask db migrate
flask db upgrade
```

## Deployment

### Production Checklist
- [ ] Change SECRET_KEY
- [ ] Change SQLALCHEMY_DATABASE_URI to PostgreSQL
- [ ] Set FLASK_ENV=production
- [ ] Disable debug mode
- [ ] Use WSGI server (Gunicorn, uWSGI)
- [ ] Enable HTTPS/SSL
- [ ] Set up logging
- [ ] Configure environment variables

### Example Gunicorn Command
```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 app:create_app()
```

## Performance Tips

1. **Add Database Indexes** for frequently searched columns
2. **Pagination** for large user lists
3. **Caching** for admin panel data
4. **Async Tasks** for heavy operations

## Security Enhancements

1. **Password Reset** - Add email-based password reset
2. **Two-Factor Authentication** - Implement 2FA
3. **Rate Limiting** - Prevent brute force attacks
4. **Audit Logging** - Log all user actions
5. **Input Validation** - Validate all user inputs
6. **SQL Injection Prevention** - Use SQLAlchemy ORM (already done)
7. **XSS Prevention** - Use template escaping (Flask default)

## Common Issues & Solutions

### Issue: "The current Flask app is not registered with this 'SQLAlchemy' instance"
**Solution**: Import User model inside app context, use `current_app.config['User']`

### Issue: Circular imports
**Solution**: Use factory functions, late imports, or restructure imports

### Issue: Database locked
**Solution**: Ensure only one Flask instance is running, or use PostgreSQL

## Useful Flask Commands

```bash
# Run with specific host/port
python -c "from app import create_app; create_app().run(host='0.0.0.0', port=8000)"

# Shell access
flask shell

# Check routes
flask routes

# Set environment variable
set FLASK_APP=app.py
set FLASK_ENV=development
```

## File Structure Best Practices

```
project/
├── app.py                    # Factory & config
├── models.py                 # Data models
├── requirements.txt          # Dependencies
├── routes/
│   ├── __init__.py
│   ├── auth.py              # Auth routes
│   └── users.py             # User routes
├── templates/
│   ├── base.html            # Base template
│   ├── auth/                # Auth templates
│   └── users/               # User templates
├── static/                  # CSS, JS, images
├── tests/                   # Test files
├── migrations/              # DB migrations
├── .env                     # Environment vars (local only)
├── .gitignore               # Git ignore
└── README.md                # Documentation
```

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [Werkzeug Documentation](https://werkzeug.palletsprojects.com/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)

---

**Happy developing!** 💻
