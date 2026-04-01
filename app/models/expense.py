"""
Expense models - Categories and expense tracking.
"""
from datetime import datetime, timezone
from app.extensions import db


class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('expense_categories', lazy='dynamic'))

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}

    def __repr__(self):
        return f'<ExpenseCategory {self.name}>'


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    expense_date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'), nullable=True)
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=True)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    gst_applicable = db.Column(db.Boolean, default=False)
    gst_rate = db.Column(db.Numeric(5, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    payment_mode = db.Column(db.String(20), default='cash')
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=True)
    notes = db.Column(db.Text)
    attachment = db.Column(db.String(500))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('expenses', lazy='dynamic'))
    category = db.relationship('ExpenseCategory', backref=db.backref('expenses', lazy='dynamic'))
    party = db.relationship('Party', backref=db.backref('expenses', lazy='dynamic'))
    bank_account = db.relationship('BankAccount', backref=db.backref('expenses', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'party_id': self.party_id,
            'amount': float(self.amount) if self.amount else 0,
            'gst_applicable': self.gst_applicable,
            'gst_rate': float(self.gst_rate) if self.gst_rate else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'payment_mode': self.payment_mode,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Expense {self.id} - {self.amount}>'
