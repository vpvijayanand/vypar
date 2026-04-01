"""
Settings routes - Company, Invoice, GST, Notification settings.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.extensions import db
from app.models.company import Company
from app.models.settings import InvoiceSettings, GSTSettings, NotificationSettings
from app.models.user import User
from app.utils.helpers import (
    api_response, api_error, get_company_id, jwt_required, get_json_or_form, admin_required
)

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings')
@login_required
def index():
    company_id = get_company_id()
    company = Company.query.get(company_id) if company_id else None
    inv_settings = InvoiceSettings.query.filter_by(company_id=company_id).first() if company_id else None
    gst_settings = GSTSettings.query.filter_by(company_id=company_id).first() if company_id else None
    notif_settings = NotificationSettings.query.filter_by(company_id=company_id).first() if company_id else None
    users = User.query.filter_by(company_id=company_id).all() if company_id else []

    return render_template('settings/index.html',
                           company=company,
                           inv_settings=inv_settings,
                           gst_settings=gst_settings,
                           notif_settings=notif_settings,
                           users=users)


@settings_bp.route('/settings/company', methods=['GET', 'POST'])
@login_required
def company_settings():
    company_id = get_company_id()

    if not company_id:
        # First-time setup
        if request.method == 'POST':
            company = Company(
                company_name=request.form.get('company_name'),
                business_type=request.form.get('business_type'),
                gstin=request.form.get('gstin'),
                pan_number=request.form.get('pan_number'),
                phone_number=request.form.get('phone_number'),
                email=request.form.get('email'),
                website=request.form.get('website'),
                address_line1=request.form.get('address_line1'),
                address_line2=request.form.get('address_line2'),
                city=request.form.get('city'),
                state=request.form.get('state'),
                pincode=request.form.get('pincode'),
            )
            db.session.add(company)
            db.session.flush()

            current_user.company_id = company.id

            # Create default settings
            db.session.add(InvoiceSettings(company_id=company.id))
            db.session.add(GSTSettings(company_id=company.id, company_state=company.state))
            db.session.add(NotificationSettings(company_id=company.id))
            db.session.commit()

            flash('Company setup complete!', 'success')
            return redirect(url_for('dashboard.index'))

        return render_template('settings/company_form.html', company=None)

    company = Company.query.get(company_id)
    if request.method == 'POST':
        company.company_name = request.form.get('company_name', company.company_name)
        company.business_type = request.form.get('business_type')
        company.gstin = request.form.get('gstin')
        company.pan_number = request.form.get('pan_number')
        company.phone_number = request.form.get('phone_number')
        company.email = request.form.get('email')
        company.website = request.form.get('website')
        company.address_line1 = request.form.get('address_line1')
        company.address_line2 = request.form.get('address_line2')
        company.city = request.form.get('city')
        company.state = request.form.get('state')
        company.pincode = request.form.get('pincode')
        db.session.commit()
        flash('Company details updated.', 'success')
        return redirect(url_for('settings.index'))

    return render_template('settings/company_form.html', company=company)


@settings_bp.route('/settings/invoice', methods=['POST'])
@login_required
def invoice_settings():
    company_id = get_company_id()
    settings = InvoiceSettings.query.filter_by(company_id=company_id).first()
    if not settings:
        settings = InvoiceSettings(company_id=company_id)
        db.session.add(settings)

    settings.invoice_prefix = request.form.get('invoice_prefix', 'INV-')
    settings.estimate_prefix = request.form.get('estimate_prefix', 'EST-')
    settings.purchase_prefix = request.form.get('purchase_prefix', 'PUR-')
    settings.show_logo = request.form.get('show_logo') == 'on'
    settings.show_signature = request.form.get('show_signature') == 'on'
    settings.default_terms = request.form.get('default_terms')
    settings.default_notes = request.form.get('default_notes')
    db.session.commit()

    flash('Invoice settings updated.', 'success')
    return redirect(url_for('settings.index'))


@settings_bp.route('/settings/gst', methods=['POST'])
@login_required
def gst_settings():
    company_id = get_company_id()
    settings = GSTSettings.query.filter_by(company_id=company_id).first()
    if not settings:
        settings = GSTSettings(company_id=company_id)
        db.session.add(settings)

    settings.enable_gst = request.form.get('enable_gst') == 'on'
    settings.gst_type = request.form.get('gst_type', 'intra')
    settings.company_state = request.form.get('company_state')
    settings.enable_cess = request.form.get('enable_cess') == 'on'
    db.session.commit()

    flash('GST settings updated.', 'success')
    return redirect(url_for('settings.index'))


# ─── User Management ─────────────────────────────────────────────────────────

@settings_bp.route('/settings/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        company_id = get_company_id()
        user = User(
            username=request.form.get('username'),
            email=request.form.get('email'),
            full_name=request.form.get('full_name'),
            phone=request.form.get('phone'),
            role=request.form.get('role', 'staff'),
            company_id=company_id,
        )
        user.set_password(request.form.get('password'))
        db.session.add(user)
        db.session.commit()

        flash(f'User "{user.username}" created.', 'success')
        return redirect(url_for('settings.index'))

    return render_template('settings/user_form.html', user=None)


@settings_bp.route('/settings/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.role = request.form.get('role', user.role)
        user.is_active = request.form.get('is_active') == 'on'

        if request.form.get('password'):
            user.set_password(request.form.get('password'))

        db.session.commit()
        flash('User updated.', 'success')
        return redirect(url_for('settings.index'))

    return render_template('settings/user_form.html', user=user)


# ─── Mobile API ──────────────────────────────────────────────────────────────

@settings_bp.route('/api/settings/company', methods=['GET'])
@jwt_required
def api_get_company():
    user = request.jwt_user
    company = Company.query.get(user.company_id) if user.company_id else None
    if not company:
        return api_error('Company not configured', 404)
    return api_response(company.to_dict())


@settings_bp.route('/api/settings/company', methods=['PUT'])
@jwt_required
def api_update_company():
    user = request.jwt_user
    data = get_json_or_form()
    company = Company.query.get(user.company_id)
    if not company:
        return api_error('Company not found', 404)

    for field in ['company_name', 'business_type', 'gstin', 'pan_number',
                   'phone_number', 'email', 'website', 'address_line1',
                   'address_line2', 'city', 'state', 'pincode']:
        if field in data:
            setattr(company, field, data[field])

    db.session.commit()
    return api_response(company.to_dict(), 'Company updated')
