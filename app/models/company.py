"""
Company model - Business details and settings.
"""
from datetime import datetime, timezone
from app.extensions import db


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    business_type = db.Column(db.String(100))  # Retail, Wholesale, Manufacturing, Service
    gstin = db.Column(db.String(15), unique=True, nullable=True)
    pan_number = db.Column(db.String(10))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(200))
    address_line1 = db.Column(db.String(255))
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    country = db.Column(db.String(100), default='India')
    logo = db.Column(db.String(500))  # file path
    financial_year_start = db.Column(db.Date)
    currency = db.Column(db.String(10), default='INR')
    date_format = db.Column(db.String(20), default='dd/mm/yyyy')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'business_type': self.business_type,
            'gstin': self.gstin,
            'pan_number': self.pan_number,
            'phone_number': self.phone_number,
            'email': self.email,
            'website': self.website,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'country': self.country,
            'logo': self.logo,
            'financial_year_start': self.financial_year_start.isoformat() if self.financial_year_start else None,
            'currency': self.currency,
            'date_format': self.date_format,
        }

    def __repr__(self):
        return f'<Company {self.company_name}>'
