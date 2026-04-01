"""
Party routes - Customer & Supplier CRUD.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from decimal import Decimal
from app.extensions import db
from app.models.party import Party
from app.utils.helpers import (
    api_response, api_error, get_company_id, jwt_required, get_json_or_form
)
from app.services.audit_service import AuditService

party_bp = Blueprint('parties', __name__)


# ─── Web Routes ──────────────────────────────────────────────────────────────

@party_bp.route('/parties')
@login_required
def list_parties():
    """List all parties (customers & suppliers)."""
    company_id = get_company_id()
    party_type = request.args.get('type', '')
    page = request.args.get('page', 1, type=int)

    query = Party.query.filter_by(company_id=company_id, is_active=True)
    if party_type:
        query = query.filter_by(party_type=party_type)

    parties = query.order_by(Party.name).paginate(page=page, per_page=20, error_out=False)
    return render_template('parties/list.html', parties=parties, party_type=party_type)


@party_bp.route('/parties/<int:party_id>')
@login_required
def view_party(party_id):
    """View party details with transaction history."""
    company_id = get_company_id()
    party = Party.query.filter_by(id=party_id, company_id=company_id).first_or_404()

    from app.models.invoice import SaleInvoice
    from app.models.purchase import PurchaseBill
    from app.models.payment import PaymentIn

    sales = SaleInvoice.query.filter_by(
        company_id=company_id, party_id=party_id, is_cancelled=False
    ).order_by(SaleInvoice.invoice_date.desc()).limit(10).all()

    purchases = PurchaseBill.query.filter_by(
        company_id=company_id, supplier_id=party_id, is_cancelled=False
    ).order_by(PurchaseBill.bill_date.desc()).limit(10).all()

    payments = PaymentIn.query.filter_by(
        company_id=company_id, party_id=party_id
    ).order_by(PaymentIn.payment_date.desc()).limit(10).all()

    return render_template('parties/view.html', party=party,
                           sales=sales, purchases=purchases, payments=payments)


@party_bp.route('/parties/create', methods=['GET', 'POST'])
@login_required
def create_party():
    """Create a new party."""
    if request.method == 'POST':
        company_id = get_company_id()
        party = Party(
            company_id=company_id,
            party_type=request.form.get('party_type', 'customer'),
            name=request.form.get('name'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            gstin=request.form.get('gstin'),
            pan=request.form.get('pan'),
            billing_address=request.form.get('billing_address'),
            shipping_address=request.form.get('shipping_address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            pincode=request.form.get('pincode'),
            opening_balance=Decimal(request.form.get('opening_balance', '0') or '0'),
            balance_type=request.form.get('balance_type', 'receivable'),
            credit_limit=Decimal(request.form.get('credit_limit', '0') or '0'),
            payment_terms_days=int(request.form.get('payment_terms_days', '30') or '30'),
            notes=request.form.get('notes'),
        )
        party.current_balance = party.opening_balance
        db.session.add(party)

        AuditService.log(current_user.id, 'create', 'party', None,
                         f'Created party: {party.name}', company_id)
        db.session.commit()

        flash(f'Party "{party.name}" created successfully.', 'success')
        return redirect(url_for('parties.list_parties'))

    return render_template('parties/form.html', party=None)


@party_bp.route('/parties/<int:party_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_party(party_id):
    """Edit an existing party."""
    company_id = get_company_id()
    party = Party.query.filter_by(id=party_id, company_id=company_id).first_or_404()

    if request.method == 'POST':
        party.party_type = request.form.get('party_type', party.party_type)
        party.name = request.form.get('name', party.name)
        party.phone = request.form.get('phone')
        party.email = request.form.get('email')
        party.gstin = request.form.get('gstin')
        party.pan = request.form.get('pan')
        party.billing_address = request.form.get('billing_address')
        party.shipping_address = request.form.get('shipping_address')
        party.city = request.form.get('city')
        party.state = request.form.get('state')
        party.pincode = request.form.get('pincode')
        party.credit_limit = Decimal(request.form.get('credit_limit', '0') or '0')
        party.payment_terms_days = int(request.form.get('payment_terms_days', '30') or '30')
        party.notes = request.form.get('notes')

        AuditService.log(current_user.id, 'update', 'party', party_id,
                         f'Updated party: {party.name}', company_id)
        db.session.commit()

        flash(f'Party "{party.name}" updated successfully.', 'success')
        return redirect(url_for('parties.list_parties'))

    return render_template('parties/form.html', party=party)


@party_bp.route('/parties/<int:party_id>/delete', methods=['POST'])
@login_required
def delete_party(party_id):
    """Soft-delete a party."""
    company_id = get_company_id()
    party = Party.query.filter_by(id=party_id, company_id=company_id).first_or_404()
    party.is_active = False

    AuditService.log(current_user.id, 'delete', 'party', party_id,
                     f'Deleted party: {party.name}', company_id)
    db.session.commit()

    flash(f'Party "{party.name}" deleted.', 'success')
    return redirect(url_for('parties.list_parties'))


@party_bp.route('/parties/csv')
@login_required
def parties_csv_download():
    """Download parties list as CSV."""
    company_id = get_company_id()
    parties_list = Party.query.filter_by(company_id=company_id, is_active=True).order_by(Party.name).all()
    from app.utils.export import parties_csv
    return parties_csv(parties_list)


# ─── Mobile API Routes ───────────────────────────────────────────────────────

@party_bp.route('/api/parties', methods=['GET'])
@jwt_required
def api_list_parties():
    """List parties with filters."""
    user = request.jwt_user
    page = request.args.get('page', 1, type=int)
    party_type = request.args.get('type')
    search = request.args.get('search')

    query = Party.query.filter_by(company_id=user.company_id, is_active=True)
    if party_type:
        query = query.filter_by(party_type=party_type)
    if search:
        query = query.filter(Party.name.ilike(f'%{search}%'))

    parties = query.order_by(Party.name).paginate(page=page, per_page=20, error_out=False)
    return api_response(
        [p.to_dict() for p in parties.items],
        pagination=parties
    )


@party_bp.route('/api/parties', methods=['POST'])
@jwt_required
def api_create_party():
    """Create a party via API."""
    user = request.jwt_user
    data = get_json_or_form()

    if not data.get('name'):
        return api_error('Party name is required', 400)

    party = Party(
        company_id=user.company_id,
        party_type=data.get('party_type', 'customer'),
        name=data['name'],
        phone=data.get('phone'),
        email=data.get('email'),
        gstin=data.get('gstin'),
        pan=data.get('pan'),
        billing_address=data.get('billing_address'),
        shipping_address=data.get('shipping_address'),
        city=data.get('city'),
        state=data.get('state'),
        pincode=data.get('pincode'),
        opening_balance=Decimal(str(data.get('opening_balance', 0))),
        balance_type=data.get('balance_type', 'receivable'),
        credit_limit=Decimal(str(data.get('credit_limit', 0))),
        payment_terms_days=int(data.get('payment_terms_days', 30)),
        notes=data.get('notes'),
    )
    party.current_balance = party.opening_balance
    db.session.add(party)
    db.session.commit()

    return api_response(party.to_dict(), 'Party created', 201)


@party_bp.route('/api/parties/<int:party_id>', methods=['GET'])
@jwt_required
def api_get_party(party_id):
    user = request.jwt_user
    party = Party.query.filter_by(id=party_id, company_id=user.company_id).first()
    if not party:
        return api_error('Party not found', 404)
    return api_response(party.to_dict())


@party_bp.route('/api/parties/<int:party_id>', methods=['PUT'])
@jwt_required
def api_update_party(party_id):
    user = request.jwt_user
    data = get_json_or_form()
    party = Party.query.filter_by(id=party_id, company_id=user.company_id).first()
    if not party:
        return api_error('Party not found', 404)

    for field in ['party_type', 'name', 'phone', 'email', 'gstin', 'pan',
                   'billing_address', 'shipping_address', 'city', 'state',
                   'pincode', 'notes']:
        if field in data:
            setattr(party, field, data[field])

    if 'credit_limit' in data:
        party.credit_limit = Decimal(str(data['credit_limit']))
    if 'payment_terms_days' in data:
        party.payment_terms_days = int(data['payment_terms_days'])

    db.session.commit()
    return api_response(party.to_dict(), 'Party updated')


@party_bp.route('/api/parties/<int:party_id>', methods=['DELETE'])
@jwt_required
def api_delete_party(party_id):
    user = request.jwt_user
    party = Party.query.filter_by(id=party_id, company_id=user.company_id).first()
    if not party:
        return api_error('Party not found', 404)

    party.is_active = False
    db.session.commit()
    return api_response(None, 'Party deleted')
