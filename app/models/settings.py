"""
Settings models - Invoice, GST, and notification configuration.
"""
from datetime import datetime, timezone
from app.extensions import db


class InvoiceSettings(db.Model):
    __tablename__ = 'invoice_settings'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, unique=True)
    invoice_prefix = db.Column(db.String(20), default='INV-')
    invoice_format = db.Column(db.String(50), default='sequential')  # sequential, year-based
    next_invoice_number = db.Column(db.Integer, default=1)
    estimate_prefix = db.Column(db.String(20), default='EST-')
    next_estimate_number = db.Column(db.Integer, default=1)
    purchase_prefix = db.Column(db.String(20), default='PUR-')
    next_purchase_number = db.Column(db.Integer, default=1)
    show_logo = db.Column(db.Boolean, default=True)
    show_signature = db.Column(db.Boolean, default=False)
    signature_image = db.Column(db.String(500))
    default_terms = db.Column(db.Text)
    default_notes = db.Column(db.Text)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('invoice_settings', uselist=False))

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_prefix': self.invoice_prefix,
            'invoice_format': self.invoice_format,
            'next_invoice_number': self.next_invoice_number,
            'estimate_prefix': self.estimate_prefix,
            'purchase_prefix': self.purchase_prefix,
            'show_logo': self.show_logo,
            'show_signature': self.show_signature,
            'default_terms': self.default_terms,
            'default_notes': self.default_notes,
        }


class GSTSettings(db.Model):
    __tablename__ = 'gst_settings'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, unique=True)
    enable_gst = db.Column(db.Boolean, default=True)
    gst_type = db.Column(db.String(20), default='intra')  # intra (CGST+SGST), inter (IGST)
    company_state = db.Column(db.String(100))
    enable_cess = db.Column(db.Boolean, default=False)
    enable_reverse_charge = db.Column(db.Boolean, default=False)
    enable_composition = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('gst_settings', uselist=False))

    def to_dict(self):
        return {
            'id': self.id,
            'enable_gst': self.enable_gst,
            'gst_type': self.gst_type,
            'company_state': self.company_state,
            'enable_cess': self.enable_cess,
            'enable_reverse_charge': self.enable_reverse_charge,
            'enable_composition': self.enable_composition,
        }


class NotificationSettings(db.Model):
    __tablename__ = 'notification_settings'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, unique=True)
    sms_enabled = db.Column(db.Boolean, default=False)
    whatsapp_enabled = db.Column(db.Boolean, default=False)
    email_enabled = db.Column(db.Boolean, default=False)
    payment_reminder_enabled = db.Column(db.Boolean, default=False)
    reminder_days_before = db.Column(db.Integer, default=3)
    low_stock_alert_enabled = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref=db.backref('notification_settings', uselist=False))

    def to_dict(self):
        return {
            'id': self.id,
            'sms_enabled': self.sms_enabled,
            'whatsapp_enabled': self.whatsapp_enabled,
            'email_enabled': self.email_enabled,
            'payment_reminder_enabled': self.payment_reminder_enabled,
            'reminder_days_before': self.reminder_days_before,
            'low_stock_alert_enabled': self.low_stock_alert_enabled,
        }
