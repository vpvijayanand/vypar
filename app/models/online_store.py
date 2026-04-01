"""
Online Store models - Product catalog, orders.
"""
from datetime import datetime, timezone
import uuid
from app.extensions import db


class OnlineStoreProduct(db.Model):
    __tablename__ = 'online_store_products'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    online_price = db.Column(db.Numeric(15, 2))
    description = db.Column(db.Text)
    images = db.Column(db.Text)  # JSON array of image paths
    category = db.Column(db.String(100))
    is_available = db.Column(db.Boolean, default=True)
    shareable_link = db.Column(db.String(200), unique=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('online_products', lazy='dynamic'))
    item = db.relationship('Item', backref=db.backref('online_product', uselist=False))

    def generate_shareable_link(self):
        self.shareable_link = str(uuid.uuid4())[:8]

    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item_name': self.item.item_name if self.item else None,
            'online_price': float(self.online_price) if self.online_price else 0,
            'description': self.description,
            'images': self.images,
            'category': self.category,
            'is_available': self.is_available,
            'shareable_link': self.shareable_link,
        }


class OnlineOrder(db.Model):
    __tablename__ = 'online_orders'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    order_number = db.Column(db.String(50), nullable=False, unique=True)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(20))
    customer_email = db.Column(db.String(120))
    customer_address = db.Column(db.Text)
    grand_total = db.Column(db.Numeric(15, 2), default=0)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, converted, cancelled
    converted_invoice_id = db.Column(db.Integer, db.ForeignKey('sale_invoices.id'), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('online_orders', lazy='dynamic'))
    items = db.relationship('OnlineOrderItem', backref='order', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'grand_total': float(self.grand_total) if self.grand_total else 0,
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class OnlineOrderItem(db.Model):
    __tablename__ = 'online_order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('online_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('online_store_products.id'), nullable=False)
    quantity = db.Column(db.Numeric(15, 3), default=1)
    unit_price = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)

    product = db.relationship('OnlineStoreProduct')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
        }
