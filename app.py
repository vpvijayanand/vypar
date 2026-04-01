"""
Vypar - GST Billing, Inventory & Accounting Application
Main application entry point with factory pattern.
"""
import os
from flask import Flask, redirect, url_for
from flask_login import current_user
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()


def indian_number_format(value):
    """Format number in Indian numbering system: 1,23,45,678.00"""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return '0.00'

    is_negative = value < 0
    value = abs(value)
    integer_part = int(value)
    decimal_part = f"{value - integer_part:.2f}"[1:]  # ".XX"

    s = str(integer_part)
    if len(s) <= 3:
        formatted = s
    else:
        last3 = s[-3:]
        remaining = s[:-3]
        # Group remaining digits in pairs from right
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted = ','.join(groups) + ',' + last3

    result = formatted + decimal_part
    return f"-{result}" if is_negative else result


def create_app(config_name=None):
    """Application factory - creates and configures the Flask app."""
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Register custom Jinja2 filters
    app.jinja_env.filters['ind'] = indian_number_format

    # Load configuration
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')

    from config import config_by_name
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Enable CORS for mobile API
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure upload folder exists
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)

    # Initialize extensions
    from app.extensions import db, login_manager
    db.init_app(app)
    login_manager.init_app(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    with app.app_context():
        # Import all models so SQLAlchemy knows about them
        from app.models import (  # noqa: F401
            User, Company, Party, Item, ItemCategory,
            SaleInvoice, SaleInvoiceItem, Estimate, EstimateItem,
            SaleOrder, SaleOrderItem, DeliveryChallan, DeliveryChallanItem,
            SaleReturn, SaleReturnItem,
            PurchaseBill, PurchaseBillItem, PurchaseOrder, PurchaseOrderItem,
            PurchaseReturn, PurchaseReturnItem,
            PaymentIn, PaymentOut,
            Expense, ExpenseCategory, OtherIncome, IncomeCategory,
            BankAccount, CashInHand, Cheque, LoanAccount,
            StockLog,
            OnlineStoreProduct, OnlineOrder, OnlineOrderItem,
            InvoiceSettings, GSTSettings, NotificationSettings,
            AuditLog,
        )

        # Create all tables
        db.create_all()

        # Seed default admin user if no users exist
        _seed_admin(db, User, Company)

    # ─── Register Blueprints ─────────────────────────────────────────────
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.parties import party_bp
    from app.routes.items import items_bp
    from app.routes.sales import sales_bp
    from app.routes.purchases import purchases_bp
    from app.routes.expenses import expenses_bp
    from app.routes.bank import bank_bp
    from app.routes.reports import reports_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(party_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(bank_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    # ─── Root Route ──────────────────────────────────────────────────────
    @app.route('/')
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    return app


def _seed_admin(db, User, Company):
    """Create default admin user and company if none exist."""
    from app.models.settings import InvoiceSettings, GSTSettings, NotificationSettings

    if User.query.first() is None:
        # Create default company
        company = Company(
            company_name='My Business',
            business_type='Retail',
            country='India',
            currency='INR',
        )
        db.session.add(company)
        db.session.flush()

        # Create admin user
        admin = User(
            username='admin',
            email='admin@vypar.local',
            full_name='Administrator',
            role='admin',
            company_id=company.id,
        )
        admin.set_password('admin123')
        db.session.add(admin)

        # Create default settings
        db.session.add(InvoiceSettings(company_id=company.id))
        db.session.add(GSTSettings(company_id=company.id))
        db.session.add(NotificationSettings(company_id=company.id))

        db.session.commit()
        print("✅ Default admin user created!")
        print("   Username: admin")
        print("   Password: admin123")
    else:
        print("✅ Database ready - users exist.")


if __name__ == '__main__':
    app = create_app()
    print("\n🚀 Vypar - GST Billing & Accounting")
    print("📍 Open http://localhost:5000")
    print("🔓 Login: admin / admin123\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
