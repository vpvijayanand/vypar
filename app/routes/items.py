"""
Item/Inventory routes - Product CRUD and stock management.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from decimal import Decimal
from app.extensions import db
from app.models.item import Item, ItemCategory
from app.utils.helpers import (
    api_response, api_error, get_company_id, jwt_required, get_json_or_form
)
from app.services.inventory_service import InventoryService
from app.services.audit_service import AuditService

items_bp = Blueprint('items', __name__)


# ─── Web Routes ──────────────────────────────────────────────────────────────

@items_bp.route('/items')
@login_required
def list_items():
    company_id = get_company_id()
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', type=int)
    low_stock = request.args.get('low_stock', type=int)

    query = Item.query.filter_by(company_id=company_id, is_active=True)
    if search:
        query = query.filter(
            (Item.item_name.ilike(f'%{search}%')) | (Item.item_code.ilike(f'%{search}%'))
        )
    if category_id:
        query = query.filter_by(category_id=category_id)
    if low_stock:
        query = query.filter(Item.current_stock <= Item.min_stock_alert)

    items = query.order_by(Item.item_name).paginate(page=page, per_page=20, error_out=False)
    categories = ItemCategory.query.filter_by(company_id=company_id).all()
    stock_summary = InventoryService.get_stock_summary(company_id)

    return render_template('items/list.html',
                           items=items, categories=categories,
                           stock_summary=stock_summary, search=search)


@items_bp.route('/items/<int:item_id>')
@login_required
def view_item(item_id):
    """View item details with stock and sales info."""
    company_id = get_company_id()
    item = Item.query.filter_by(id=item_id, company_id=company_id).first_or_404()

    from app.models.invoice import SaleInvoiceItem, SaleInvoice
    from app.models.purchase import PurchaseBillItem, PurchaseBill
    from sqlalchemy import func

    # Recent sales of this item
    recent_sales = db.session.query(
        SaleInvoice.invoice_number, SaleInvoice.invoice_date,
        SaleInvoiceItem.quantity, SaleInvoiceItem.unit_price, SaleInvoiceItem.total_amount
    ).join(SaleInvoice).filter(
        SaleInvoiceItem.item_id == item_id,
        SaleInvoice.is_cancelled == False
    ).order_by(SaleInvoice.invoice_date.desc()).limit(10).all()

    # Total sold
    total_sold = db.session.query(
        func.coalesce(func.sum(SaleInvoiceItem.quantity), 0)
    ).join(SaleInvoice).filter(
        SaleInvoiceItem.item_id == item_id,
        SaleInvoice.is_cancelled == False
    ).scalar()

    # Total purchased
    total_purchased = db.session.query(
        func.coalesce(func.sum(PurchaseBillItem.quantity), 0)
    ).join(PurchaseBill).filter(
        PurchaseBillItem.item_id == item_id,
        PurchaseBill.is_cancelled == False
    ).scalar()

    return render_template('items/view.html', item=item,
                           recent_sales=recent_sales,
                           total_sold=float(total_sold),
                           total_purchased=float(total_purchased))


@items_bp.route('/items/create', methods=['GET', 'POST'])
@login_required
def create_item():
    company_id = get_company_id()

    if request.method == 'POST':
        item = Item(
            company_id=company_id,
            item_name=request.form.get('item_name'),
            item_code=request.form.get('item_code'),
            hsn_code=request.form.get('hsn_code'),
            category_id=request.form.get('category_id') or None,
            unit=request.form.get('unit', 'pcs'),
            sale_price=Decimal(request.form.get('sale_price', '0') or '0'),
            purchase_price=Decimal(request.form.get('purchase_price', '0') or '0'),
            gst_rate=Decimal(request.form.get('gst_rate', '0') or '0'),
            cess=Decimal(request.form.get('cess', '0') or '0'),
            opening_stock_qty=Decimal(request.form.get('opening_stock_qty', '0') or '0'),
            opening_stock_value=Decimal(request.form.get('opening_stock_value', '0') or '0'),
            min_stock_alert=Decimal(request.form.get('min_stock_alert', '0') or '0'),
            batch_tracking=request.form.get('batch_tracking') == 'on',
            serial_tracking=request.form.get('serial_tracking') == 'on',
            barcode=request.form.get('barcode'),
            description=request.form.get('description'),
        )
        item.current_stock = item.opening_stock_qty
        db.session.add(item)
        db.session.flush()

        # Log opening stock
        if float(item.opening_stock_qty) > 0:
            InventoryService.update_stock(
                company_id, item.id,
                float(item.opening_stock_qty),
                'opening', 'manual', None,
                float(item.purchase_price),
                'Opening stock', current_user.id
            )

        AuditService.log(current_user.id, 'create', 'item', item.id,
                         f'Created item: {item.item_name}', company_id)
        db.session.commit()

        flash(f'Item "{item.item_name}" created successfully.', 'success')
        return redirect(url_for('items.list_items'))

    categories = ItemCategory.query.filter_by(company_id=company_id).all()
    return render_template('items/form.html', item=None, categories=categories)


@items_bp.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    company_id = get_company_id()
    item = Item.query.filter_by(id=item_id, company_id=company_id).first_or_404()

    if request.method == 'POST':
        item.item_name = request.form.get('item_name', item.item_name)
        item.item_code = request.form.get('item_code')
        item.hsn_code = request.form.get('hsn_code')
        item.category_id = request.form.get('category_id') or None
        item.unit = request.form.get('unit', 'pcs')
        item.sale_price = Decimal(request.form.get('sale_price', '0') or '0')
        item.purchase_price = Decimal(request.form.get('purchase_price', '0') or '0')
        item.gst_rate = Decimal(request.form.get('gst_rate', '0') or '0')
        item.cess = Decimal(request.form.get('cess', '0') or '0')
        item.min_stock_alert = Decimal(request.form.get('min_stock_alert', '0') or '0')
        item.batch_tracking = request.form.get('batch_tracking') == 'on'
        item.serial_tracking = request.form.get('serial_tracking') == 'on'
        item.barcode = request.form.get('barcode')
        item.description = request.form.get('description')

        AuditService.log(current_user.id, 'update', 'item', item_id,
                         f'Updated item: {item.item_name}', company_id)
        db.session.commit()

        flash(f'Item "{item.item_name}" updated.', 'success')
        return redirect(url_for('items.list_items'))

    categories = ItemCategory.query.filter_by(company_id=company_id).all()
    return render_template('items/form.html', item=item, categories=categories)


@items_bp.route('/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    company_id = get_company_id()
    item = Item.query.filter_by(id=item_id, company_id=company_id).first_or_404()
    item.is_active = False
    db.session.commit()
    flash(f'Item "{item.item_name}" deleted.', 'success')
    return redirect(url_for('items.list_items'))


# ─── Category Management ─────────────────────────────────────────────────────

@items_bp.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    company_id = get_company_id()
    if request.method == 'POST':
        cat = ItemCategory(
            company_id=company_id,
            name=request.form.get('name'),
            parent_id=request.form.get('parent_id') or None,
        )
        db.session.add(cat)
        db.session.commit()
        flash(f'Category "{cat.name}" created.', 'success')

    categories = ItemCategory.query.filter_by(company_id=company_id).all()
    return render_template('items/categories.html', categories=categories)


# ─── Mobile API Routes ───────────────────────────────────────────────────────

@items_bp.route('/api/items', methods=['GET'])
@jwt_required
def api_list_items():
    user = request.jwt_user
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    low_stock = request.args.get('low_stock', type=int)

    query = Item.query.filter_by(company_id=user.company_id, is_active=True)
    if search:
        query = query.filter(
            (Item.item_name.ilike(f'%{search}%')) | (Item.item_code.ilike(f'%{search}%'))
        )
    if low_stock:
        query = query.filter(Item.current_stock <= Item.min_stock_alert)

    items = query.order_by(Item.item_name).paginate(page=page, per_page=20, error_out=False)
    return api_response([i.to_dict() for i in items.items], pagination=items)


@items_bp.route('/api/items', methods=['POST'])
@jwt_required
def api_create_item():
    user = request.jwt_user
    data = get_json_or_form()

    if not data.get('item_name'):
        return api_error('Item name is required', 400)

    item = Item(
        company_id=user.company_id,
        item_name=data['item_name'],
        item_code=data.get('item_code'),
        hsn_code=data.get('hsn_code'),
        category_id=data.get('category_id'),
        unit=data.get('unit', 'pcs'),
        sale_price=Decimal(str(data.get('sale_price', 0))),
        purchase_price=Decimal(str(data.get('purchase_price', 0))),
        gst_rate=Decimal(str(data.get('gst_rate', 0))),
        cess=Decimal(str(data.get('cess', 0))),
        opening_stock_qty=Decimal(str(data.get('opening_stock_qty', 0))),
        min_stock_alert=Decimal(str(data.get('min_stock_alert', 0))),
        barcode=data.get('barcode'),
        description=data.get('description'),
    )
    item.current_stock = item.opening_stock_qty
    db.session.add(item)
    db.session.commit()

    return api_response(item.to_dict(), 'Item created', 201)


@items_bp.route('/api/items/<int:item_id>', methods=['GET'])
@jwt_required
def api_get_item(item_id):
    user = request.jwt_user
    item = Item.query.filter_by(id=item_id, company_id=user.company_id).first()
    if not item:
        return api_error('Item not found', 404)
    return api_response(item.to_dict())


@items_bp.route('/api/items/<int:item_id>', methods=['PUT'])
@jwt_required
def api_update_item(item_id):
    user = request.jwt_user
    data = get_json_or_form()
    item = Item.query.filter_by(id=item_id, company_id=user.company_id).first()
    if not item:
        return api_error('Item not found', 404)

    for field in ['item_name', 'item_code', 'hsn_code', 'unit', 'barcode', 'description']:
        if field in data:
            setattr(item, field, data[field])
    for field in ['sale_price', 'purchase_price', 'gst_rate', 'cess', 'min_stock_alert']:
        if field in data:
            setattr(item, field, Decimal(str(data[field])))
    if 'category_id' in data:
        item.category_id = data['category_id']

    db.session.commit()
    return api_response(item.to_dict(), 'Item updated')


@items_bp.route('/api/items/<int:item_id>', methods=['DELETE'])
@jwt_required
def api_delete_item(item_id):
    user = request.jwt_user
    item = Item.query.filter_by(id=item_id, company_id=user.company_id).first()
    if not item:
        return api_error('Item not found', 404)
    item.is_active = False
    db.session.commit()
    return api_response(None, 'Item deleted')


@items_bp.route('/api/stock/summary', methods=['GET'])
@jwt_required
def api_stock_summary():
    user = request.jwt_user
    return api_response(InventoryService.get_stock_summary(user.company_id))


@items_bp.route('/api/stock/low', methods=['GET'])
@jwt_required
def api_low_stock():
    user = request.jwt_user
    items = InventoryService.get_low_stock_items(user.company_id)
    return api_response([i.to_dict() for i in items])


@items_bp.route('/items/csv')
@login_required
def items_csv_download():
    """Download items/inventory as CSV."""
    company_id = get_company_id()
    items_list = Item.query.filter_by(company_id=company_id, is_active=True).order_by(Item.item_name).all()
    from app.utils.export import items_csv
    return items_csv(items_list)
