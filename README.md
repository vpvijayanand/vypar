# Flask Admin Dashboard

A modern Flask web application with admin user authentication and comprehensive CRUD operations for user management.

## Features

✨ **User Authentication**
- Secure login system with password hashing
- Session-based authentication using Flask-Login
- Admin and regular user roles

👥 **User Management (CRUD)**
- **Create**: Admin can create new users with custom roles
- **Read**: View user profiles and user list
- **Update**: Edit user information and roles
- **Delete**: Remove users (with safety checks for the last admin)

🔐 **Security Features**
- Password hashing with Werkzeug
- Admin-only access control
- Prevention of deleting the last admin user
- Prevention of self-deletion
- CSRF protection with Flask-WTF

🎨 **Modern UI**
- Bootstrap 5 responsive design
- Clean and intuitive navigation
- Professional styling with gradient backgrounds
- Alert notifications for user feedback

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd c:\apps\wl_web_scraper
   ```

2. **Create and activate a virtual environment** (already done)
   ```bash
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
.
├── app.py                 # Main Flask application factory
├── models.py             # Database models (User model)
├── seeds.py              # Database seeding (admin user)
├── requirements.txt      # Python dependencies
├── app.db                # SQLite database (created on first run)
├── routes/
│   ├── __init__.py
│   ├── auth.py          # Authentication routes (login, logout)
│   └── users.py         # User management routes (CRUD operations)
└── templates/
    ├── base.html        # Base template with navigation
    ├── auth/
    │   └── login.html   # Login page
    └── users/
        ├── dashboard.html # Dashboard (admin view)
        ├── create.html    # Create user form
        ├── edit.html      # Edit user form
        ├── view.html      # View user profile
        └── profile.html   # Current user profile
```

## Running the Application

1. **Activate the virtual environment**
   ```bash
   .venv\Scripts\activate
   ```

2. **Run the Flask application**
   ```bash
   python app.py
   ```

3. **Open your browser and navigate to**
   ```
   http://localhost:5000
   ```

## Default Admin Credentials

The application automatically creates an admin user on first run:

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change the admin password after first login in production!

## Usage Guide

### For Admin Users

1. **Login** with admin credentials
2. **View Dashboard**: See all users in the system
3. **Create User**: Click "Create User" button
   - Enter username, email, and password
   - Optionally grant admin privileges
4. **Edit User**: Click "Edit" on any user
   - Modify username, email, and role
5. **Delete User**: Click "Delete" on any user
   - Confirmation required
   - Cannot delete the last admin user

### For Regular Users

1. **Login** with your credentials
2. **View Profile**: See your account information
3. **Limited Access**: Cannot access user management features

## Database Schema

### User Model
```python
- id (Integer, Primary Key)
- username (String, Unique)
- email (String, Unique)
- password_hash (String)
- is_admin (Boolean)
- created_at (DateTime)
- updated_at (DateTime)
```

## API Endpoints

### Authentication
- `GET/POST /auth/login` - User login
- `GET /auth/logout` - User logout

### User Management (Admin Only)
- `GET /users/dashboard` - View all users (admin) or user profile (regular)
- `GET/POST /users/create` - Create new user
- `GET/POST /users/<user_id>/edit` - Edit user details
- `POST /users/<user_id>/delete` - Delete user
- `GET /users/<user_id>` - View user profile

## Security Considerations

1. **Change Secret Key**: In production, update `SECRET_KEY` in `app.py`
2. **Database**: Use PostgreSQL instead of SQLite for production
3. **Password Policy**: Implement minimum password requirements
4. **HTTPS**: Enable HTTPS in production
5. **Environment Variables**: Use `.env` file for sensitive configurations

## Development

### Adding New Features

1. **New Database Model**: Add to `models.py` and update database
2. **New Routes**: Create in appropriate file under `routes/`
3. **New Templates**: Add to `templates/` directory
4. **Database Migrations**: Consider using Flask-Migrate for production

### Testing

To test the application:
1. Login with admin credentials
2. Create a test user
3. Edit the test user
4. Delete the test user
5. Logout and login with the new user

## Troubleshooting

### Database Issues
- Delete `app.db` to reset the database
- Admin user will be recreated on next run

### Port Already in Use
- Change the port in `app.py`: `app.run(debug=True, port=5001)`

### Import Errors
- Ensure virtual environment is activated
- Verify all packages installed: `pip install -r requirements.txt`

## Dependencies

- **Flask** (3.0.0) - Web framework
- **Flask-SQLAlchemy** (3.1.1) - ORM for database
- **Flask-Login** (0.6.3) - User session management
- **Flask-WTF** (1.2.1) - CSRF protection
- **Werkzeug** (3.0.1) - Password hashing utilities

## License

This project is provided as-is for educational purposes.

## Author

Created: March 6, 2026

---

**Happy coding!** 🚀
