"""
Party model - Customers and Suppliers.
"""
from datetime import datetime, timezone
from app.extensions import db


class Party(db.Model):
    __tablename__ = 'parties'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    party_type = db.Column(db.String(20), nullable=False)  # customer, supplier, both
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    gstin = db.Column(db.String(15))
    pan = db.Column(db.String(10))
    billing_address = db.Column(db.Text)
    shipping_address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    opening_balance = db.Column(db.Numeric(15, 2), default=0)
    balance_type = db.Column(db.String(20), default='receivable')  # receivable, payable
    current_balance = db.Column(db.Numeric(15, 2), default=0)
    credit_limit = db.Column(db.Numeric(15, 2), default=0)
    payment_terms_days = db.Column(db.Integer, default=30)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    company = db.relationship('Company', backref=db.backref('parties', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'party_type': self.party_type,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'gstin': self.gstin,
            'pan': self.pan,
            'billing_address': self.billing_address,
            'shipping_address': self.shipping_address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'opening_balance': float(self.opening_balance) if self.opening_balance else 0,
            'balance_type': self.balance_type,
            'current_balance': float(self.current_balance) if self.current_balance else 0,
            'credit_limit': float(self.credit_limit) if self.credit_limit else 0,
            'payment_terms_days': self.payment_terms_days,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Party {self.name} ({self.party_type})>'
