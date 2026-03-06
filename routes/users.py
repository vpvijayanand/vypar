from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

users_bp = Blueprint('users', __name__, url_prefix='/users')

def get_user_model():
    """Get the User model from current app config"""
    return current_app.config.get('User')

def get_db():
    """Get the SQLAlchemy instance from current app"""
    return current_app.config.get('db')

# Middleware to check if user is admin
def admin_required(f):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('users.dashboard'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@users_bp.route('/dashboard')
@login_required
def dashboard():
    """Display dashboard with list of users (admin only) or user profile"""
    User = get_user_model()
    if current_user.is_admin:
        users = User.query.all()
        return render_template('users/dashboard.html', users=users)
    else:
        return render_template('users/profile.html', user=current_user)

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create a new user (admin only)"""
    User = get_user_model()
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'on'
        
        # Validate input
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return redirect(url_for('users.create'))
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('users.create'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('users.create'))
        
        # Create new user
        new_user = User(username=username, email=email, is_admin=is_admin)
        new_user.set_password(password)
        
        db = get_db()
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'User {username} created successfully', 'success')
        return redirect(url_for('users.dashboard'))
    
    return render_template('users/create.html')

@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(user_id):
    """Edit a user (admin only)"""
    User = get_user_model()
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        is_admin = request.form.get('is_admin') == 'on'
        
        # Validate input
        if not username or not email:
            flash('All fields are required', 'danger')
            return redirect(url_for('users.edit', user_id=user_id))
        
        # Check if username or email already exists (excluding current user)
        existing_username = User.query.filter_by(username=username).first()
        if existing_username and existing_username.id != user_id:
            flash('Username already exists', 'danger')
            return redirect(url_for('users.edit', user_id=user_id))
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != user_id:
            flash('Email already exists', 'danger')
            return redirect(url_for('users.edit', user_id=user_id))
        
        # Prevent removing admin role from the last admin
        if user.is_admin and not is_admin:
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count == 1:
                flash('Cannot remove admin role from the last admin', 'danger')
                return redirect(url_for('users.edit', user_id=user_id))
        
        # Update user
        user.username = username
        user.email = email
        user.is_admin = is_admin
        
        db = get_db()
        db.session.commit()
        
        flash(f'User {username} updated successfully', 'success')
        return redirect(url_for('users.dashboard'))
    
    return render_template('users/edit.html', user=user)

@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(user_id):
    """Delete a user (admin only)"""
    User = get_user_model()
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the last admin
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count == 1:
            flash('Cannot delete the last admin user', 'danger')
            return redirect(url_for('users.dashboard'))
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('users.dashboard'))
    
    username = user.username
    db = get_db()
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} deleted successfully', 'success')
    return redirect(url_for('users.dashboard'))

@users_bp.route('/<int:user_id>')
@login_required
def view(user_id):
    """View user details"""
    User = get_user_model()
    user = User.query.get_or_404(user_id)
    
    # Users can only view their own profile unless they are admin
    if user.id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this profile', 'danger')
        return redirect(url_for('users.dashboard'))
    
    return render_template('users/view.html', user=user)
