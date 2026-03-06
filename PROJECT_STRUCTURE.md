# Project Structure

## Flask Admin Dashboard - Complete File Structure

```
c:\apps\wl_web_scraper\
├── .github/
│   └── copilot-instructions.md    # Custom instructions for Copilot
│
├── .vscode/
│   └── tasks.json                 # VS Code task definitions
│
├── routes/
│   ├── __init__.py               # Package initializer
│   ├── auth.py                   # Authentication routes (login/logout)
│   └── users.py                  # User management CRUD routes
│
├── templates/
│   ├── base.html                 # Base template with navigation
│   ├── auth/
│   │   └── login.html            # Login page
│   └── users/
│       ├── dashboard.html        # Admin dashboard / user profile
│       ├── create.html           # Create new user form
│       ├── edit.html             # Edit user details form
│       ├── view.html             # View user profile
│       └── profile.html          # Current user profile page
│
├── app.py                        # Flask application factory & main entry point
├── models.py                     # SQLAlchemy User model definition
├── requirements.txt              # Python package dependencies
├── .gitignore                    # Git ignore rules
├── README.md                     # Complete documentation
├── QUICKSTART.md                 # Quick start guide
└── app.db                        # SQLite database (auto-created)
```

## File Descriptions

### Core Application Files

**app.py** (Main Application)
- Flask application factory function
- Database and authentication initialization
- Admin user seeding
- Blueprint registration
- Home route that redirects to login/dashboard

**models.py** (Database Models)
- User model definition with SQLAlchemy
- Password hashing methods
- Model factory function to avoid circular imports

### Routing & Views

**routes/auth.py** (Authentication)
- `/auth/login` - GET/POST login page
- `/auth/logout` - Logout current user
- User loader function for session management

**routes/users.py** (User Management CRUD)
- `/users/dashboard` - View all users (admin) or own profile
- `/users/create` - GET/POST create new user form
- `/users/<id>/edit` - GET/POST edit user details
- `/users/<id>/delete` - POST delete user
- `/users/<id>` - GET view user profile
- `@admin_required` decorator for admin-only routes

### Templates

**templates/base.html** (Layout)
- Bootstrap 5 styling
- Navigation bar with user menu
- Flash message display area
- Responsive design
- Dark purple gradient background

**templates/auth/login.html** (Authentication)
- Simple login form
- Username and password fields
- Demo credentials display

**templates/users/dashboard.html** (Admin Dashboard)
- User management table
- Create user button
- Edit/view/delete actions per user
- User role badges
- Responsive table design

**templates/users/create.html** (User Creation)
- Username input
- Email input
- Password input
- Admin checkbox
- Form validation messages

**templates/users/edit.html** (User Editing)
- Editable username and email
- Admin role checkbox
- Read-only timestamps
- Password change note

**templates/users/view.html** (User Profile)
- User information display
- Role badge
- Account creation date
- Last updated timestamp

**templates/users/profile.html** (User Home)
- Welcome message
- Profile card with user info
- Account type indicator
- Quick info sidebar

### Configuration Files

**requirements.txt**
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
WTForms==3.1.1
Werkzeug==3.0.1
```

**.vscode/tasks.json**
- Flask: Run App - Start the development server
- Flask: Install Dependencies - Install Python packages
- Flask: Reset Database - Delete app.db for fresh start

**.github/copilot-instructions.md**
- Custom instructions for GitHub Copilot
- Architecture guidelines
- Common tasks reference
- Security notes

### Documentation

**README.md** - Full project documentation
- Project overview and features
- Installation instructions
- Project structure
- Usage guide
- Database schema
- API endpoints
- Security considerations
- Dependencies list

**QUICKSTART.md** - Quick reference guide
- Running the application
- Default credentials
- Features overview
- CRUD operations guide
- Navigation structure
- Troubleshooting
- Development tips

## Database Schema

### User Table
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME,
    updated_at DATETIME
);
```

## Technology Stack

- **Web Framework**: Flask 3.0.0
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with Werkzeug password hashing
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Python Version**: 3.8+

## Environment Setup

```
Virtual Environment: .venv/
Python Executable: .venv/Scripts/python.exe
Database File: app.db
```

## Running the Application

### Development Server
```bash
python app.py
```

### Access Points
- Web Interface: http://localhost:5000
- Admin Login: admin / admin123
- Debugger PIN: 643-299-823

## Key Features

✅ User Authentication with Flask-Login
✅ Admin Dashboard with User Management
✅ CRUD Operations (Create, Read, Update, Delete)
✅ Role-Based Access Control (Admin vs User)
✅ Password Hashing with Werkzeug
✅ Responsive Bootstrap 5 UI
✅ SQLite Database with SQLAlchemy
✅ Jinja2 Templating Engine
✅ Flash Messages for User Feedback
✅ Auto-Seeded Admin User

## Security Features

🔐 Password hashing with Werkzeug
🔐 CSRF protection with Flask-WTF
🔐 Session-based authentication
🔐 Admin-only access control
🔐 Prevention of deleting last admin
🔐 Prevention of self-deletion
