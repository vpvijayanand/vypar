"""
Sales models - Invoices, Estimates, Sale Orders, Delivery Challans, Sale Returns.
"""
from datetime import datetime, timezone
from app.extensions import db


class SaleInvoice(db.Model):
    __tablename__ = 'sale_invoices'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    invoice_number = db.Column(db.String(50), nullable=False, index=True)
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date)
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False, index=True)
    billing_address = db.Column(db.Text)
    shipping_address = db.Column(db.Text)
    place_of_supply = db.Column(db.String(100))
    payment_type = db.Column(db.String(20), default='credit')  # cash, credit, upi, bank
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    discount_total = db.Column(db.Numeric(15, 2), default=0)
    tax_total = db.Column(db.Numeric(15, 2), default=0)
    round_off = db.Column(db.Numeric(10, 2), default=0)
    grand_total = db.Column(db.Numeric(15, 2), default=0)
    amount_received = db.Column(db.Numeric(15, 2), default=0)
    balance_due = db.Column(db.Numeric(15, 2), default=0)
    notes = db.Column(db.Text)
    terms_conditions = db.Column(db.Text)
    attachment = db.Column(db.String(500))
    status = db.Column(db.String(20), default='unpaid')  # paid, unpaid, partial
    is_cancelled = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    company = db.relationship('Company', backref=db.backref('sale_invoices', lazy='dynamic'))
    party = db.relationship('Party', backref=db.backref('sale_invoices', lazy='dynamic'))
    items = db.relationship('SaleInvoiceItem', backref='invoice', cascade='all, delete-orphan', lazy='dynamic')
    creator = db.relationship('User', backref=db.backref('created_invoices', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'party_id': self.party_id,
            'party_name': self.party.name if self.party else None,
            'billing_address': self.billing_address,
            'shipping_address': self.shipping_address,
            'place_of_supply': self.place_of_supply,
            'payment_type': self.payment_type,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'discount_total': float(self.discount_total) if self.discount_total else 0,
            'tax_total': float(self.tax_total) if self.tax_total else 0,
            'round_off': float(self.round_off) if self.round_off else 0,
            'grand_total': float(self.grand_total) if self.grand_total else 0,
            'amount_received': float(self.amount_received) if self.amount_received else 0,
            'balance_due': float(self.balance_due) if self.balance_due else 0,
            'status': self.status,
            'notes': self.notes,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<SaleInvoice {self.invoice_number}>'


class SaleInvoiceItem(db.Model):
    __tablename__ = 'sale_invoice_items'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('sale_invoices.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item_name = db.Column(db.String(200))  # snapshot at invoice time
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

    item = db.relationship('Item', backref=db.backref('sale_invoice_items', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'hsn_code': self.hsn_code,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit': self.unit,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'discount_percent': float(self.discount_percent) if self.discount_percent else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'gst_rate': float(self.gst_rate) if self.gst_rate else 0,
            'cgst_amount': float(self.cgst_amount) if self.cgst_amount else 0,
            'sgst_amount': float(self.sgst_amount) if self.sgst_amount else 0,
            'igst_amount': float(self.igst_amount) if self.igst_amount else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
        }


class Estimate(db.Model):
    __tablename__ = 'estimates'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    quotation_number = db.Column(db.String(50), nullable=False)
    quotation_date = db.Column(db.Date, nullable=False)
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    validity_date = db.Column(db.Date)
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    tax_total = db.Column(db.Numeric(15, 2), default=0)
    grand_total = db.Column(db.Numeric(15, 2), default=0)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='open')  # open, converted, expired
    converted_invoice_id = db.Column(db.Integer, db.ForeignKey('sale_invoices.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('estimates', lazy='dynamic'))
    party = db.relationship('Party', backref=db.backref('estimates', lazy='dynamic'))
    items = db.relationship('EstimateItem', backref='estimate', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'quotation_number': self.quotation_number,
            'quotation_date': self.quotation_date.isoformat() if self.quotation_date else None,
            'party_id': self.party_id,
            'party_name': self.party.name if self.party else None,
            'validity_date': self.validity_date.isoformat() if self.validity_date else None,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'tax_total': float(self.tax_total) if self.tax_total else 0,
            'grand_total': float(self.grand_total) if self.grand_total else 0,
            'status': self.status,
            'notes': self.notes,
            'items': [item.to_dict() for item in self.items],
        }


class EstimateItem(db.Model):
    __tablename__ = 'estimate_items'

    id = db.Column(db.Integer, primary_key=True)
    estimate_id = db.Column(db.Integer, db.ForeignKey('estimates.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item_name = db.Column(db.String(200))
    quantity = db.Column(db.Numeric(15, 3), default=1)
    unit = db.Column(db.String(20))
    unit_price = db.Column(db.Numeric(15, 2), default=0)
    discount_percent = db.Column(db.Numeric(5, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
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
            'gst_rate': float(self.gst_rate) if self.gst_rate else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
        }


class SaleOrder(db.Model):
    __tablename__ = 'sale_orders'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    order_number = db.Column(db.String(50), nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    expected_delivery_date = db.Column(db.Date)
    grand_total = db.Column(db.Numeric(15, 2), default=0)
    status = db.Column(db.String(20), default='open')  # open, closed, cancelled
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('sale_orders', lazy='dynamic'))
    party = db.relationship('Party', backref=db.backref('sale_orders', lazy='dynamic'))
    items = db.relationship('SaleOrderItem', backref='sale_order', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'party_id': self.party_id,
            'party_name': self.party.name if self.party else None,
            'grand_total': float(self.grand_total) if self.grand_total else 0,
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
        }


class SaleOrderItem(db.Model):
    __tablename__ = 'sale_order_items'

    id = db.Column(db.Integer, primary_key=True)
    sale_order_id = db.Column(db.Integer, db.ForeignKey('sale_orders.id'), nullable=False)
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


class DeliveryChallan(db.Model):
    __tablename__ = 'delivery_challans'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    challan_number = db.Column(db.String(50), nullable=False)
    challan_date = db.Column(db.Date, nullable=False)
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    transport_details = db.Column(db.String(255))
    vehicle_number = db.Column(db.String(50))
    delivery_address = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, delivered
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('delivery_challans', lazy='dynamic'))
    party = db.relationship('Party', backref=db.backref('delivery_challans', lazy='dynamic'))
    items = db.relationship('DeliveryChallanItem', backref='challan', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'challan_number': self.challan_number,
            'challan_date': self.challan_date.isoformat() if self.challan_date else None,
            'party_id': self.party_id,
            'party_name': self.party.name if self.party else None,
            'transport_details': self.transport_details,
            'vehicle_number': self.vehicle_number,
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
        }


class DeliveryChallanItem(db.Model):
    __tablename__ = 'delivery_challan_items'

    id = db.Column(db.Integer, primary_key=True)
    challan_id = db.Column(db.Integer, db.ForeignKey('delivery_challans.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item_name = db.Column(db.String(200))
    quantity = db.Column(db.Numeric(15, 3), default=1)
    unit = db.Column(db.String(20))

    item = db.relationship('Item')

    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'quantity': float(self.quantity) if self.quantity else 0,
        }


class SaleReturn(db.Model):
    __tablename__ = 'sale_returns'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    return_number = db.Column(db.String(50), nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    original_invoice_id = db.Column(db.Integer, db.ForeignKey('sale_invoices.id'), nullable=False)
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    reason = db.Column(db.Text)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    refund_mode = db.Column(db.String(20))  # cash, bank, credit_note
    status = db.Column(db.String(20), default='pending')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('sale_returns', lazy='dynamic'))
    party = db.relationship('Party', backref=db.backref('sale_returns', lazy='dynamic'))
    original_invoice = db.relationship('SaleInvoice', backref=db.backref('returns', lazy='dynamic'))
    items = db.relationship('SaleReturnItem', backref='sale_return', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'return_number': self.return_number,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'original_invoice_id': self.original_invoice_id,
            'party_id': self.party_id,
            'party_name': self.party.name if self.party else None,
            'reason': self.reason,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'refund_mode': self.refund_mode,
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
        }


class SaleReturnItem(db.Model):
    __tablename__ = 'sale_return_items'

    id = db.Column(db.Integer, primary_key=True)
    sale_return_id = db.Column(db.Integer, db.ForeignKey('sale_returns.id'), nullable=False)
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
