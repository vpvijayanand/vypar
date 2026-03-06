<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Flask Admin Dashboard - Custom Instructions

This is a Flask web application project with the following key features:

## Project Overview
- **Type**: Python Flask Web Application
- **Purpose**: Admin panel with user authentication and CRUD operations
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with password hashing

## Architecture
- **app.py**: Main application factory using Flask application factory pattern
- **models.py**: SQLAlchemy User model with password hashing
- **routes/**: Blueprint-based route organization (auth.py, users.py)
- **templates/**: Jinja2 templates with Bootstrap 5 styling
- **seeds.py**: Database seeding for admin user

## Key Implementation Details

### Authentication
- Uses Flask-Login for session management
- Passwords hashed with Werkzeug
- Admin role-based access control
- User decorator for @login_required protection

### CRUD Operations
- **Create**: Admin can create users with custom roles
- **Read**: View user profiles and list all users
- **Update**: Edit user details and permissions
- **Delete**: Remove users with validation (prevent deleting last admin)

### Database
- SQLite database (app.db)
- User model with timestamps
- Password hashing with check_password method

## Development Guidelines

1. **Routing**: Use blueprints for modular route organization
2. **Templates**: Extend base.html for consistent styling
3. **Authentication**: Always use @login_required for protected routes
4. **Admin Check**: Use @admin_required decorator for admin-only features
5. **Error Handling**: Display flash messages for user feedback

## Default Credentials
- Username: `admin`
- Password: `admin123`
- Auto-seeded on application startup

## Common Tasks

### Adding a New Route
1. Create route in appropriate file under `routes/`
2. Use appropriate decorators (@login_required, @admin_required)
3. Create corresponding template in `templates/`
4. Add navigation link to base.html if needed

### Adding a New Model
1. Define in models.py
2. Update app.py to create tables
3. Create migration if needed
4. Add corresponding routes

### Modifying Styling
- Edit templates directly
- Use Bootstrap 5 classes (already included via CDN)
- Modify CSS in base.html style tags if needed

## Security Notes
- Change SECRET_KEY in production
- Use PostgreSQL for production databases
- Implement password reset functionality
- Add HTTPS in production
- Consider adding 2FA for admin accounts
