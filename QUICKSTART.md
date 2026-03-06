# Quick Start Guide

## Installation & Setup

### Step 1: Prerequisites
- Python 3.8+ installed
- Virtual environment already configured (.venv)

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python app.py
```

The app will:
- Create the database (app.db)
- Automatically seed an admin user
- Start the Flask development server

### Step 4: Access the Application
Open your browser and navigate to:
```
http://localhost:5000
```

## Default Login Credentials

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change the admin password after first login!

## Features

### For Admin Users
1. **View All Users**: See a list of all registered users
2. **Create Users**: Add new users with custom roles
3. **Edit Users**: Modify user information and permissions
4. **Delete Users**: Remove users from the system
5. **Manage Roles**: Grant/revoke admin privileges

### For Regular Users
1. **Login**: Access their profile
2. **View Profile**: See their account information
3. **Limited Access**: Cannot access user management features

## Common Tasks

### Create a New User
1. Click "Create User" in the dashboard
2. Enter username, email, and password
3. Optionally check "Make this user an admin"
4. Click "Create User"

### Edit a User
1. Go to Dashboard
2. Click "Edit" next to the user
3. Modify details as needed
4. Click "Save Changes"

### Delete a User
1. Go to Dashboard
2. Click "Delete" next to the user
3. Confirm the deletion

### Change Your Password
Currently, password changes must be done by:
- Deleting and recreating the user, or
- Direct database modification (advanced)

## Project Files

```
c:\apps\wl_web_scraper\
├── app.py                 # Main application
├── models.py             # User model definition
├── requirements.txt      # Python dependencies
├── README.md            # Full documentation
├── routes/
│   ├── auth.py          # Authentication routes
│   └── users.py         # User CRUD routes
├── templates/
│   ├── base.html        # Base template
│   ├── auth/
│   │   └── login.html   # Login page
│   └── users/
│       ├── dashboard.html
│       ├── create.html
│       ├── edit.html
│       ├── view.html
│       └── profile.html
└── .vscode/
    └── tasks.json       # VS Code tasks
```

## VS Code Tasks

Run tasks from VS Code Command Palette (Ctrl+Shift+P):

- **Flask: Run App** - Start the development server
- **Flask: Install Dependencies** - Install required packages
- **Flask: Reset Database** - Delete app.db to start fresh

## Troubleshooting

### Port Already in Use
If port 5000 is already in use:
1. Open app.py
2. Change the last line to: `app.run(debug=True, port=5001)`
3. Access at http://localhost:5001

### Database Issues
To reset the database:
1. Run the "Flask: Reset Database" task in VS Code, or
2. Delete app.db manually
3. Restart the app

### Cannot Login
- Verify username and password (default: admin / admin123)
- Check that the database file (app.db) exists
- Restart the app

## Security Reminders

1. **Change SECRET_KEY** in app.py before deploying
2. **Change admin password** after first login
3. **Use PostgreSQL** instead of SQLite for production
4. **Enable HTTPS** in production
5. **Set strong passwords** for all users

## Next Steps

1. Customize the admin password
2. Create test users
3. Explore the user management features
4. Modify styling in templates/base.html as needed
5. Add additional features as required

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review the code comments in app.py, models.py, and routes/
3. Ensure all dependencies are installed correctly

---

**Happy coding!** 🚀
