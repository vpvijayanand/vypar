"""
Purchase routes - Bills, Orders, Returns.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from datetime import datetime, date
from decimal import Decimal
from app.extensions import db
from app.models.purchase import PurchaseBill, PurchaseOrder, PurchaseReturn
from app.models.party import Party
from app.models.item import Item
from app.models.payment import PaymentOut
from app.utils.helpers import (
    api_response, api_error, get_company_id, jwt_required, get_json_or_form
)
from app.services.purchase_service import PurchaseService
from app.services.audit_service import AuditService

purchases_bp = Blueprint('purchases', __name__)


@purchases_bp.route('/purchases')
@login_required
def list_purchases():
    company_id = get_company_id()
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')

    purchases = PurchaseService.list_purchases(
        company_id, page=page, status=status)

    suppliers = Party.query.filter(
        Party.company_id == company_id,
        Party.is_active == True,
        Party.party_type.in_(['supplier', 'both'])
    ).all()

    return render_template('purchases/list.html', purchases=purchases,
                           suppliers=suppliers, status=status)


@purchases_bp.route('/purchases/create', methods=['GET', 'POST'])
@login_required
def create_purchase():
    company_id = get_company_id()

    if request.method == 'POST':
        try:
            items_data = []
            idx = 0
            while request.form.get(f'items[{idx}][item_id]'):
                item = Item.query.get(int(request.form.get(f'items[{idx}][item_id]')))
                items_data.append({
                    'item_id': int(request.form.get(f'items[{idx}][item_id]')),
                    'item_name': item.item_name if item else '',
                    'hsn_code': item.hsn_code if item else '',
                    'quantity': float(request.form.get(f'items[{idx}][quantity]', 1)),
                    'unit_price': float(request.form.get(f'items[{idx}][unit_price]', 0)),
                    'unit': item.unit if item else 'pcs',
                    'discount_percent': float(request.form.get(f'items[{idx}][discount_percent]', 0)),
                    'gst_rate': float(request.form.get(f'items[{idx}][gst_rate]', item.gst_rate if item else 0)),
                })
                idx += 1

            data = {
                'supplier_id': int(request.form.get('supplier_id')),
                'bill_date': datetime.strptime(
                    request.form.get('bill_date', date.today().isoformat()), '%Y-%m-%d').date(),
                'due_date': datetime.strptime(
                    request.form.get('due_date'), '%Y-%m-%d').date() if request.form.get('due_date') else None,
                'amount_paid': float(request.form.get('amount_paid', 0) or 0),
                'notes': request.form.get('notes', ''),
                'items': items_data,
            }

            bill = PurchaseService.create_purchase(company_id, data, current_user.id)

            AuditService.log(current_user.id, 'create', 'purchase_bill', bill.id,
                             f'Created purchase: {bill.bill_number}', company_id)
            db.session.commit()

            flash(f'Purchase {bill.bill_number} created.', 'success')
            return redirect(url_for('purchases.view_purchase', bill_id=bill.id))

        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    suppliers = Party.query.filter(
        Party.company_id == company_id,
        Party.is_active == True,
        Party.party_type.in_(['supplier', 'both'])
    ).order_by(Party.name).all()
    items = Item.query.filter_by(company_id=company_id, is_active=True).order_by(Item.item_name).all()
    items_json = [i.to_dict() for i in items]
    suppliers_json = [s.to_dict() for s in suppliers]
    return render_template('purchases/form.html', purchase=None, suppliers=suppliers, items=items, items_json=items_json, suppliers_json=suppliers_json)


@purchases_bp.route('/purchases/<int:bill_id>')
@login_required
def view_purchase(bill_id):
    company_id = get_company_id()
    bill = PurchaseBill.query.filter_by(id=bill_id, company_id=company_id).first_or_404()
    return render_template('purchases/view.html', purchase=bill)


@purchases_bp.route('/purchases/<int:bill_id>/payment', methods=['POST'])
@login_required
def record_payment(bill_id):
    company_id = get_company_id()
    amount = float(request.form.get('amount', 0))

    try:
        bill = PurchaseService.record_payment(bill_id, company_id, amount)

        payment = PaymentOut(
            company_id=company_id,
            payment_number=f"PAY-{bill.bill_number}",
            payment_date=date.today(),
            supplier_id=bill.supplier_id,
            reference_bill_id=bill.id,
            amount_paid=Decimal(str(amount)),
            payment_mode=request.form.get('payment_mode', 'cash'),
            bank_account_id=request.form.get('bank_account_id') or None,
            reference_number=request.form.get('reference_number'),
            notes=request.form.get('notes'),
            created_by=current_user.id,
        )
        db.session.add(payment)
        db.session.commit()

        flash(f'Payment of ₹{amount} recorded.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')

    return redirect(url_for('purchases.view_purchase', bill_id=bill_id))


@purchases_bp.route('/purchases/<int:bill_id>/pdf')
@login_required
def purchase_pdf(bill_id):
    """Download purchase bill as PDF."""
    company_id = get_company_id()
    bill = PurchaseBill.query.filter_by(id=bill_id, company_id=company_id).first_or_404()

    from app.models.company import Company
    from app.utils.export import generate_purchase_pdf
    company = Company.query.get(bill.company_id)
    pdf_buffer = generate_purchase_pdf(bill, company)

    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename={bill.bill_number}.pdf'
    return response


@purchases_bp.route('/purchases/csv')
@login_required
def purchases_csv_download():
    """Download purchases list as CSV."""
    company_id = get_company_id()
    bills = PurchaseBill.query.filter_by(
        company_id=company_id, is_cancelled=False
    ).order_by(PurchaseBill.bill_date.desc()).all()

    from app.utils.export import purchases_csv
    return purchases_csv(bills)


# ─── Mobile API ──────────────────────────────────────────────────────────────

@purchases_bp.route('/api/purchases', methods=['GET'])
@jwt_required
def api_list_purchases():
    user = request.jwt_user
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')

    purchases = PurchaseService.list_purchases(user.company_id, page=page, status=status)
    return api_response(
        [b.to_dict() for b in purchases.items],
        pagination=purchases
    )


@purchases_bp.route('/api/purchases', methods=['POST'])
@jwt_required
def api_create_purchase():
    user = request.jwt_user
    data = get_json_or_form()

    if not data.get('supplier_id'):
        return api_error('supplier_id is required', 400)
    if not data.get('items'):
        return api_error('At least one item is required', 400)

    try:
        for item_data in data['items']:
            item = Item.query.get(item_data['item_id'])
            if item:
                item_data['item_name'] = item.item_name
                item_data['hsn_code'] = item.hsn_code
                item_data['unit'] = item.unit
                if 'gst_rate' not in item_data:
                    item_data['gst_rate'] = float(item.gst_rate)

        bill = PurchaseService.create_purchase(user.company_id, data, user.id)
        return api_response(bill.to_dict(), 'Purchase created', 201)
    except ValueError as e:
        return api_error(str(e), 400)


@purchases_bp.route('/api/purchases/<int:bill_id>', methods=['GET'])
@jwt_required
def api_get_purchase(bill_id):
    user = request.jwt_user
    bill = PurchaseBill.query.filter_by(id=bill_id, company_id=user.company_id).first()
    if not bill:
        return api_error('Purchase not found', 404)
    return api_response(bill.to_dict())
