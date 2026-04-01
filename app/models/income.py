"""
Other Income models - Secondary income tracking.
"""
from datetime import datetime, timezone
from app.extensions import db


class IncomeCategory(db.Model):
    __tablename__ = 'income_categories'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('income_categories', lazy='dynamic'))

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}


class OtherIncome(db.Model):
    __tablename__ = 'other_income'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    income_date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('income_categories.id'), nullable=True)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    payment_mode = db.Column(db.String(20), default='cash')
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=True)
    reference = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('other_incomes', lazy='dynamic'))
    category = db.relationship('IncomeCategory', backref=db.backref('incomes', lazy='dynamic'))
    bank_account = db.relationship('BankAccount', backref=db.backref('other_incomes', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'income_date': self.income_date.isoformat() if self.income_date else None,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'amount': float(self.amount) if self.amount else 0,
            'payment_mode': self.payment_mode,
            'reference': self.reference,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
