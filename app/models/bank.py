"""
Bank & Cash models - Bank accounts, cash-in-hand, cheques, loans.
"""
from datetime import datetime, timezone
from app.extensions import db


class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    account_name = db.Column(db.String(200), nullable=False)
    account_number = db.Column(db.String(50))
    bank_name = db.Column(db.String(200))
    ifsc_code = db.Column(db.String(20))
    opening_balance = db.Column(db.Numeric(15, 2), default=0)
    current_balance = db.Column(db.Numeric(15, 2), default=0)
    account_type = db.Column(db.String(30), default='savings')  # savings, current, overdraft
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('bank_accounts', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'account_name': self.account_name,
            'account_number': self.account_number,
            'bank_name': self.bank_name,
            'ifsc_code': self.ifsc_code,
            'opening_balance': float(self.opening_balance) if self.opening_balance else 0,
            'current_balance': float(self.current_balance) if self.current_balance else 0,
            'account_type': self.account_type,
            'is_active': self.is_active,
        }

    def __repr__(self):
        return f'<BankAccount {self.account_name}>'


class CashInHand(db.Model):
    __tablename__ = 'cash_in_hand'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, unique=True)
    opening_balance = db.Column(db.Numeric(15, 2), default=0)
    current_balance = db.Column(db.Numeric(15, 2), default=0)
    last_updated = db.Column(db.Date)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('cash_in_hand', uselist=False))

    def to_dict(self):
        return {
            'id': self.id,
            'opening_balance': float(self.opening_balance) if self.opening_balance else 0,
            'current_balance': float(self.current_balance) if self.current_balance else 0,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
        }


class Cheque(db.Model):
    __tablename__ = 'cheques'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    cheque_number = db.Column(db.String(50), nullable=False)
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=True)
    bank_name = db.Column(db.String(200))
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    clearance_date = db.Column(db.Date)
    cheque_type = db.Column(db.String(20), default='received')  # received, issued
    status = db.Column(db.String(20), default='pending')  # pending, cleared, bounced, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('cheques', lazy='dynamic'))
    party = db.relationship('Party', backref=db.backref('cheques', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'cheque_number': self.cheque_number,
            'party_id': self.party_id,
            'party_name': self.party.name if self.party else None,
            'bank_name': self.bank_name,
            'amount': float(self.amount) if self.amount else 0,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'clearance_date': self.clearance_date.isoformat() if self.clearance_date else None,
            'cheque_type': self.cheque_type,
            'status': self.status,
        }


class LoanAccount(db.Model):
    __tablename__ = 'loan_accounts'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    lender_name = db.Column(db.String(200), nullable=False)
    loan_amount = db.Column(db.Numeric(15, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), default=0)
    emi_amount = db.Column(db.Numeric(15, 2), default=0)
    start_date = db.Column(db.Date)
    tenure_months = db.Column(db.Integer)
    outstanding_balance = db.Column(db.Numeric(15, 2), default=0)
    loan_type = db.Column(db.String(30), default='term')  # term, overdraft, working_capital
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('loan_accounts', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'lender_name': self.lender_name,
            'loan_amount': float(self.loan_amount) if self.loan_amount else 0,
            'interest_rate': float(self.interest_rate) if self.interest_rate else 0,
            'emi_amount': float(self.emi_amount) if self.emi_amount else 0,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'tenure_months': self.tenure_months,
            'outstanding_balance': float(self.outstanding_balance) if self.outstanding_balance else 0,
            'loan_type': self.loan_type,
            'is_active': self.is_active,
        }
