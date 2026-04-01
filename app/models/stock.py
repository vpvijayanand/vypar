"""
Stock log model - Tracks every stock movement.
"""
from datetime import datetime, timezone
from app.extensions import db


class StockLog(db.Model):
    __tablename__ = 'stock_logs'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, index=True)
    transaction_type = db.Column(db.String(30), nullable=False)
    # Types: sale, purchase, sale_return, purchase_return, adjustment, opening
    reference_type = db.Column(db.String(30))  # invoice, bill, return, manual
    reference_id = db.Column(db.Integer)
    quantity_change = db.Column(db.Numeric(15, 3), nullable=False)  # positive=in, negative=out
    quantity_before = db.Column(db.Numeric(15, 3), default=0)
    quantity_after = db.Column(db.Numeric(15, 3), default=0)
    unit_cost = db.Column(db.Numeric(15, 2), default=0)
    notes = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('stock_logs', lazy='dynamic'))
    item = db.relationship('Item', backref=db.backref('stock_logs', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item_name': self.item.item_name if self.item else None,
            'transaction_type': self.transaction_type,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'quantity_change': float(self.quantity_change) if self.quantity_change else 0,
            'quantity_before': float(self.quantity_before) if self.quantity_before else 0,
            'quantity_after': float(self.quantity_after) if self.quantity_after else 0,
            'unit_cost': float(self.unit_cost) if self.unit_cost else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
