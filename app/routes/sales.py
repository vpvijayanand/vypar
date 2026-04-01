"""
Sales routes - Invoices, Estimates, Sale Orders, Delivery Challans, Returns.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from datetime import datetime, date
from decimal import Decimal
from app.extensions import db
from app.models.invoice import (
    SaleInvoice, SaleInvoiceItem, Estimate, EstimateItem,
    SaleReturn, SaleReturnItem
)
from app.models.party import Party
from app.models.item import Item
from app.models.payment import PaymentIn
from app.utils.helpers import (
    api_response, api_error, get_company_id, jwt_required, get_json_or_form
)
from app.services.invoice_service import InvoiceService
from app.services.gst_service import GSTCalculator
from app.services.audit_service import AuditService

sales_bp = Blueprint('sales', __name__)


# ─── Sale Invoice Web Routes ─────────────────────────────────────────────────

@sales_bp.route('/sales')
@login_required
def list_invoices():
    company_id = get_company_id()
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    party_id = request.args.get('party_id', type=int)

    invoices = InvoiceService.list_invoices(
        company_id, page=page, status=status, party_id=party_id)

    parties = Party.query.filter_by(company_id=company_id, is_active=True).all()
    return render_template('sales/list.html', invoices=invoices, parties=parties, status=status)


@sales_bp.route('/sales/create', methods=['GET', 'POST'])
@login_required
def create_invoice():
    company_id = get_company_id()

    if request.method == 'POST':
        try:
            # Parse items from form
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
                    'cess_rate': float(request.form.get(f'items[{idx}][cess_rate]', 0)),
                })
                idx += 1

            data = {
                'party_id': int(request.form.get('party_id')),
                'invoice_date': datetime.strptime(
                    request.form.get('invoice_date', date.today().isoformat()), '%Y-%m-%d').date(),
                'due_date': datetime.strptime(
                    request.form.get('due_date'), '%Y-%m-%d').date() if request.form.get('due_date') else None,
                'billing_address': request.form.get('billing_address', ''),
                'shipping_address': request.form.get('shipping_address', ''),
                'place_of_supply': request.form.get('place_of_supply', ''),
                'payment_type': request.form.get('payment_type', 'credit'),
                'amount_received': float(request.form.get('amount_received', 0) or 0),
                'notes': request.form.get('notes', ''),
                'terms_conditions': request.form.get('terms_conditions', ''),
                'items': items_data,
            }

            invoice = InvoiceService.create_invoice(company_id, data, current_user.id)

            AuditService.log(current_user.id, 'create', 'sale_invoice', invoice.id,
                             f'Created invoice: {invoice.invoice_number}', company_id)
            db.session.commit()

            flash(f'Invoice {invoice.invoice_number} created successfully.', 'success')
            return redirect(url_for('sales.view_invoice', invoice_id=invoice.id))

        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating invoice: {str(e)}', 'danger')

    parties = Party.query.filter_by(company_id=company_id, is_active=True).order_by(Party.name).all()
    items = Item.query.filter_by(company_id=company_id, is_active=True).order_by(Item.item_name).all()
    items_json = [i.to_dict() for i in items]
    parties_json = [p.to_dict() for p in parties]
    return render_template('sales/form.html', invoice=None, parties=parties, items=items, items_json=items_json, parties_json=parties_json)


@sales_bp.route('/sales/<int:invoice_id>')
@login_required
def view_invoice(invoice_id):
    company_id = get_company_id()
    invoice = InvoiceService.get_invoice(invoice_id, company_id)
    if not invoice:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('sales.list_invoices'))
    return render_template('sales/view.html', invoice=invoice)


@sales_bp.route('/sales/<int:invoice_id>/payment', methods=['POST'])
@login_required
def record_payment(invoice_id):
    """Record payment-in against an invoice."""
    company_id = get_company_id()
    amount = float(request.form.get('amount', 0))

    try:
        invoice = InvoiceService.record_payment(invoice_id, company_id, amount)

        # Create Payment-In record
        payment = PaymentIn(
            company_id=company_id,
            payment_number=f"REC-{invoice.invoice_number}",
            payment_date=date.today(),
            party_id=invoice.party_id,
            reference_invoice_id=invoice.id,
            amount_received=Decimal(str(amount)),
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

    return redirect(url_for('sales.view_invoice', invoice_id=invoice_id))


@sales_bp.route('/sales/<int:invoice_id>/pdf')
@login_required
def invoice_pdf(invoice_id):
    """Download invoice as PDF."""
    company_id = get_company_id()
    invoice = InvoiceService.get_invoice(invoice_id, company_id)
    if not invoice:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('sales.list_invoices'))

    from app.models.company import Company
    from app.utils.export import generate_invoice_pdf
    company = Company.query.get(invoice.company_id)
    pdf_buffer = generate_invoice_pdf(invoice, company)

    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename={invoice.invoice_number}.pdf'
    return response


@sales_bp.route('/sales/csv')
@login_required
def sales_csv_download():
    """Download sales list as CSV."""
    company_id = get_company_id()
    invoices = SaleInvoice.query.filter_by(
        company_id=company_id, is_cancelled=False
    ).order_by(SaleInvoice.invoice_date.desc()).all()

    from app.utils.export import sales_csv
    return sales_csv(invoices)


# ─── Sale Invoice API Routes ─────────────────────────────────────────────────

@sales_bp.route('/api/sales', methods=['GET'])
@jwt_required
def api_list_invoices():
    user = request.jwt_user
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    party_id = request.args.get('party_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    invoices = InvoiceService.list_invoices(
        user.company_id, page=page, status=status, party_id=party_id,
        date_from=datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else None,
        date_to=datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else None,
    )
    return api_response(
        [inv.to_dict() for inv in invoices.items],
        pagination=invoices
    )


@sales_bp.route('/api/sales', methods=['POST'])
@jwt_required
def api_create_invoice():
    user = request.jwt_user
    data = get_json_or_form()

    if not data.get('party_id'):
        return api_error('party_id is required', 400)
    if not data.get('items') or len(data['items']) == 0:
        return api_error('At least one item is required', 400)

    try:
        # Enrich items with names
        for item_data in data['items']:
            item = Item.query.get(item_data['item_id'])
            if item:
                item_data['item_name'] = item.item_name
                item_data['hsn_code'] = item.hsn_code
                item_data['unit'] = item.unit
                if 'gst_rate' not in item_data:
                    item_data['gst_rate'] = float(item.gst_rate)

        invoice = InvoiceService.create_invoice(user.company_id, data, user.id)
        return api_response(invoice.to_dict(), 'Invoice created', 201)
    except ValueError as e:
        return api_error(str(e), 400)


@sales_bp.route('/api/sales/<int:invoice_id>', methods=['GET'])
@jwt_required
def api_get_invoice(invoice_id):
    user = request.jwt_user
    invoice = InvoiceService.get_invoice(invoice_id, user.company_id)
    if not invoice:
        return api_error('Invoice not found', 404)
    return api_response(invoice.to_dict())


@sales_bp.route('/api/sales/<int:invoice_id>/payment', methods=['POST'])
@jwt_required
def api_record_payment(invoice_id):
    user = request.jwt_user
    data = get_json_or_form()
    amount = float(data.get('amount', 0))

    try:
        invoice = InvoiceService.record_payment(invoice_id, user.company_id, amount)
        return api_response(invoice.to_dict(), 'Payment recorded')
    except ValueError as e:
        return api_error(str(e), 400)


# ─── GST Calculator API (used by frontend & mobile) ──────────────────────────

@sales_bp.route('/api/calculate-gst', methods=['POST'])
@jwt_required
def api_calculate_gst():
    """Calculate GST for given items - used by mobile and web forms."""
    data = get_json_or_form()
    items = data.get('items', [])
    is_inter_state = data.get('is_inter_state', False)

    calculated = []
    for item in items:
        calc = GSTCalculator.calculate_line_item(
            quantity=item.get('quantity', 1),
            unit_price=item.get('unit_price', 0),
            discount_percent=item.get('discount_percent', 0),
            gst_rate=item.get('gst_rate', 0),
            cess_rate=item.get('cess_rate', 0),
            is_inter_state=is_inter_state,
        )
        calculated.append(calc)

    totals = GSTCalculator.calculate_invoice_totals(calculated)
    return api_response({'items': calculated, 'totals': totals})
