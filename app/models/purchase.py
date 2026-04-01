"""
Purchase models - Bills, Orders, Returns.
"""
from datetime import datetime, timezone
from app.extensions import db


class PurchaseBill(db.Model):
    __tablename__ = 'purchase_bills'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    bill_number = db.Column(db.String(50), nullable=False, index=True)
    bill_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date)
    supplier_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False, index=True)
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    discount_total = db.Column(db.Numeric(15, 2), default=0)
    tax_total = db.Column(db.Numeric(15, 2), default=0)
    round_off = db.Column(db.Numeric(10, 2), default=0)
    grand_total = db.Column(db.Numeric(15, 2), default=0)
    amount_paid = db.Column(db.Numeric(15, 2), default=0)
    balance_due = db.Column(db.Numeric(15, 2), default=0)
    payment_status = db.Column(db.String(20), default='unpaid')  # paid, unpaid, partial
    notes = db.Column(db.Text)
    attachment = db.Column(db.String(500))
    is_cancelled = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('purchase_bills', lazy='dynamic'))
    supplier = db.relationship('Party', backref=db.backref('purchase_bills', lazy='dynamic'))
    items = db.relationship('PurchaseBillItem', backref='bill', cascade='all, delete-orphan', lazy='dynamic')
    creator = db.relationship('User', backref=db.backref('created_purchases', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'bill_number': self.bill_number,
            'bill_date': self.bill_date.isoformat() if self.bill_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'discount_total': float(self.discount_total) if self.discount_total else 0,
            'tax_total': float(self.tax_total) if self.tax_total else 0,
            'grand_total': float(self.grand_total) if self.grand_total else 0,
            'amount_paid': float(self.amount_paid) if self.amount_paid else 0,
            'balance_due': float(self.balance_due) if self.balance_due else 0,
            'payment_status': self.payment_status,
            'notes': self.notes,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<PurchaseBill {self.bill_number}>'


class PurchaseBillItem(db.Model):
    __tablename__ = 'purchase_bill_items'

    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('purchase_bills.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item_name = db.Column(db.String(200))
    hsn_code = db.Column(db.String(20))
    quantity = db.Column(db.Numeric(15, 3), default=1)
    unit = db.Column(db.String(20))
    unit_price = db.Column(db.Numeric(15, 2), default=0)
    discount_percent = db.Column(db.Numeric(5, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    gst_rate = db.Column(db.Numeric(5, 2), default=0)
    cgst_amount = db.Column(db.Numeric(15, 2), default=0)
    sgst_amount = db.Column(db.Numeric(15, 2), default=0)
    igst_amount = db.Column(db.Numeric(15, 2), default=0)
    cess_amount = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)

    item = db.relationship('Item', backref=db.backref('purchase_bill_items', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'hsn_code': self.hsn_code,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'gst_rate': float(self.gst_rate) if self.gst_rate else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
        }


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    po_number = db.Column(db.String(50), nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    expected_delivery_date = db.Column(db.Date)
    grand_total = db.Column(db.Numeric(15, 2), default=0)
    status = db.Column(db.String(20), default='open')  # open, closed, cancelled
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('purchase_orders', lazy='dynamic'))
    supplier = db.relationship('Party', backref=db.backref('purchase_orders', lazy='dynamic'))
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'po_number': self.po_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'grand_total': float(self.grand_total) if self.grand_total else 0,
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
        }


class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'

    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item_name = db.Column(db.String(200))
    quantity = db.Column(db.Numeric(15, 3), default=1)
    unit_price = db.Column(db.Numeric(15, 2), default=0)
    gst_rate = db.Column(db.Numeric(5, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)

    item = db.relationship('Item')

    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
        }


class PurchaseReturn(db.Model):
    __tablename__ = 'purchase_returns'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    return_number = db.Column(db.String(50), nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    original_purchase_id = db.Column(db.Integer, db.ForeignKey('purchase_bills.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    reason = db.Column(db.Text)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    status = db.Column(db.String(20), default='pending')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('purchase_returns', lazy='dynamic'))
    supplier = db.relationship('Party', backref=db.backref('purchase_returns', lazy='dynamic'))
    original_purchase = db.relationship('PurchaseBill', backref=db.backref('returns', lazy='dynamic'))
    items = db.relationship('PurchaseReturnItem', backref='purchase_return', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'return_number': self.return_number,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'original_purchase_id': self.original_purchase_id,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'reason': self.reason,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
        }


class PurchaseReturnItem(db.Model):
    __tablename__ = 'purchase_return_items'

    id = db.Column(db.Integer, primary_key=True)
    purchase_return_id = db.Column(db.Integer, db.ForeignKey('purchase_returns.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item_name = db.Column(db.String(200))
    quantity = db.Column(db.Numeric(15, 3), default=1)
    unit_price = db.Column(db.Numeric(15, 2), default=0)
    gst_rate = db.Column(db.Numeric(5, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)

    item = db.relationship('Item')

    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
        }
