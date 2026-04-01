"""
Authentication routes - Login, Logout, Register, JWT token for mobile.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timezone
from app.extensions import db
from app.models.user import User
from app.models.company import Company
from app.utils.helpers import api_response, api_error, generate_jwt_token, get_json_or_form

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# ─── Web Routes ──────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Web login page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account is deactivated. Contact admin.', 'danger')
                return render_template('auth/login.html')

            login_user(user)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Web registration - creates user + company."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        company_name = request.form.get('company_name')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('auth/register.html')

        # Create company
        company = Company(company_name=company_name or f"{username}'s Business")
        db.session.add(company)
        db.session.flush()

        # Create admin user for this company
        user = User(username=username, email=email, role='admin', company_id=company.id)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


# ─── Mobile API Routes (JWT) ─────────────────────────────────────────────────

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """JWT login for mobile apps."""
    data = get_json_or_form()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return api_error('Username and password required', 400)

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return api_error('Invalid credentials', 401)

    if not user.is_active:
        return api_error('Account deactivated', 403)

    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    token = generate_jwt_token(user.id)
    return api_response({
        'token': token,
        'user': user.to_dict(),
        'company': user.company.to_dict() if user.company else None,
    }, 'Login successful')


@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    """JWT registration for mobile apps."""
    data = get_json_or_form()

    required = ['username', 'email', 'password']
    for field in required:
        if not data.get(field):
            return api_error(f'{field} is required', 400)

    if User.query.filter_by(username=data['username']).first():
        return api_error('Username already exists', 409)

    if User.query.filter_by(email=data['email']).first():
        return api_error('Email already exists', 409)

    company = Company(company_name=data.get('company_name', f"{data['username']}'s Business"))
    db.session.add(company)
    db.session.flush()

    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data.get('full_name'),
        phone=data.get('phone'),
        role='admin',
        company_id=company.id,
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    token = generate_jwt_token(user.id)
    return api_response({
        'token': token,
        'user': user.to_dict(),
        'company': company.to_dict(),
    }, 'Registration successful', 201)
