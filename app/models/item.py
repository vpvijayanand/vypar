"""
Item/Product models - Inventory master data.
"""
from datetime import datetime, timezone
from app.extensions import db


class ItemCategory(db.Model):
    __tablename__ = 'item_categories'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('item_categories.id'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('item_categories', lazy='dynamic'))
    parent = db.relationship('ItemCategory', remote_side=[id], backref='subcategories')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
        }

    def __repr__(self):
        return f'<ItemCategory {self.name}>'


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    item_name = db.Column(db.String(200), nullable=False)
    item_code = db.Column(db.String(50), index=True)  # SKU
    hsn_code = db.Column(db.String(20))
    category_id = db.Column(db.Integer, db.ForeignKey('item_categories.id'), nullable=True)
    unit = db.Column(db.String(20), default='pcs')  # pcs, kg, ltr, mtr, box, etc.
    sale_price = db.Column(db.Numeric(15, 2), default=0)
    purchase_price = db.Column(db.Numeric(15, 2), default=0)
    gst_rate = db.Column(db.Numeric(5, 2), default=0)  # percentage
    cess = db.Column(db.Numeric(5, 2), default=0)
    opening_stock_qty = db.Column(db.Numeric(15, 3), default=0)
    opening_stock_value = db.Column(db.Numeric(15, 2), default=0)
    current_stock = db.Column(db.Numeric(15, 3), default=0)
    min_stock_alert = db.Column(db.Numeric(15, 3), default=0)
    batch_tracking = db.Column(db.Boolean, default=False)
    serial_tracking = db.Column(db.Boolean, default=False)
    expiry_date = db.Column(db.Date, nullable=True)
    barcode = db.Column(db.String(100))
    description = db.Column(db.Text)
    item_image = db.Column(db.String(500))  # file path
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    company = db.relationship('Company', backref=db.backref('items', lazy='dynamic'))
    category = db.relationship('ItemCategory', backref=db.backref('items', lazy='dynamic'))

    @property
    def stock_value(self):
        return float(self.current_stock or 0) * float(self.purchase_price or 0)

    @property
    def is_low_stock(self):
        return (self.current_stock or 0) <= (self.min_stock_alert or 0)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'item_name': self.item_name,
            'item_code': self.item_code,
            'hsn_code': self.hsn_code,
            'category_id': self.category_id,
            'unit': self.unit,
            'sale_price': float(self.sale_price) if self.sale_price else 0,
            'purchase_price': float(self.purchase_price) if self.purchase_price else 0,
            'gst_rate': float(self.gst_rate) if self.gst_rate else 0,
            'cess': float(self.cess) if self.cess else 0,
            'current_stock': float(self.current_stock) if self.current_stock else 0,
            'min_stock_alert': float(self.min_stock_alert) if self.min_stock_alert else 0,
            'stock_value': self.stock_value,
            'is_low_stock': self.is_low_stock,
            'batch_tracking': self.batch_tracking,
            'serial_tracking': self.serial_tracking,
            'barcode': self.barcode,
            'description': self.description,
            'item_image': self.item_image,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Item {self.item_name}>'
