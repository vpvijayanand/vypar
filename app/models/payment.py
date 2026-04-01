"""
Payment models - Payment In (receipts) and Payment Out (disbursements).
"""
from datetime import datetime, timezone
from app.extensions import db


class PaymentIn(db.Model):
    __tablename__ = 'payments_in'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    payment_number = db.Column(db.String(50), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    reference_invoice_id = db.Column(db.Integer, db.ForeignKey('sale_invoices.id'), nullable=True)
    amount_received = db.Column(db.Numeric(15, 2), nullable=False)
    payment_mode = db.Column(db.String(20), default='cash')  # cash, bank, upi, cheque
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=True)
    reference_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('payments_in', lazy='dynamic'))
    party = db.relationship('Party', backref=db.backref('payments_in', lazy='dynamic'))
    reference_invoice = db.relationship('SaleInvoice', backref=db.backref('payments', lazy='dynamic'))
    bank_account = db.relationship('BankAccount', backref=db.backref('payments_in', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'payment_number': self.payment_number,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'party_id': self.party_id,
            'party_name': self.party.name if self.party else None,
            'reference_invoice_id': self.reference_invoice_id,
            'amount_received': float(self.amount_received) if self.amount_received else 0,
            'payment_mode': self.payment_mode,
            'bank_account_id': self.bank_account_id,
            'reference_number': self.reference_number,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<PaymentIn {self.payment_number}>'


class PaymentOut(db.Model):
    __tablename__ = 'payments_out'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    payment_number = db.Column(db.String(50), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    reference_bill_id = db.Column(db.Integer, db.ForeignKey('purchase_bills.id'), nullable=True)
    amount_paid = db.Column(db.Numeric(15, 2), nullable=False)
    payment_mode = db.Column(db.String(20), default='cash')
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=True)
    reference_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('payments_out', lazy='dynamic'))
    supplier = db.relationship('Party', backref=db.backref('payments_out', lazy='dynamic'))
    reference_bill = db.relationship('PurchaseBill', backref=db.backref('payments', lazy='dynamic'))
    bank_account = db.relationship('BankAccount', backref=db.backref('payments_out', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'payment_number': self.payment_number,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'reference_bill_id': self.reference_bill_id,
            'amount_paid': float(self.amount_paid) if self.amount_paid else 0,
            'payment_mode': self.payment_mode,
            'bank_account_id': self.bank_account_id,
            'reference_number': self.reference_number,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<PaymentOut {self.payment_number}>'
