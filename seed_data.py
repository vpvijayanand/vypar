"""
Vypar - Comprehensive Seed Data Generator
==========================================
Seeds data across March AND April 2026 of realistic Indian business data
across ALL modules: Company, Parties, Items, Sales Invoices, Purchase Bills,
Expenses, Income, Payments, Bank Accounts, Cash-in-Hand, Cheques, Loans.

Run:  python seed_data.py
"""
import os, sys, random
from datetime import date, datetime, timedelta
from decimal import Decimal

# ── Bootstrap Flask app ──────────────────────────────────────────────────────
os.environ.setdefault('FLASK_ENV', 'development')

# Import create_app from the app.py file (not the app package)
import importlib.util
spec = importlib.util.spec_from_file_location("app_module", os.path.join(os.path.dirname(__file__), "app.py"))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
create_app = app_module.create_app

from app.extensions import db
from app.models.company import Company
from app.models.user import User
from app.models.party import Party
from app.models.item import Item, ItemCategory
from app.models.invoice import SaleInvoice, SaleInvoiceItem
from app.models.purchase import PurchaseBill, PurchaseBillItem
from app.models.expense import Expense, ExpenseCategory
from app.models.income import OtherIncome, IncomeCategory
from app.models.payment import PaymentIn, PaymentOut
from app.models.bank import BankAccount, CashInHand, Cheque, LoanAccount
from app.models.settings import InvoiceSettings, GSTSettings

app = create_app()

# ── Seed data months: March & April 2026 ─────────────────────────────────
MONTH_START = date(2026, 3, 1)
MONTH_END   = date(2026, 3, 31)
APR_START   = date(2026, 4, 1)
APR_END     = date(2026, 4, 1)  # today

def random_date(start=MONTH_START, end=MONTH_END):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(0, delta)))

def D(v):
    return Decimal(str(round(v, 2)))


def clear_old_data(company_id):
    """Delete all existing seed data for a clean slate."""
    print("🗑️  Clearing old data …")
    # Delete in order of foreign-key dependencies
    SaleInvoiceItem.query.filter(
        SaleInvoiceItem.invoice_id.in_(
            db.session.query(SaleInvoice.id).filter_by(company_id=company_id)
        )
    ).delete(synchronize_session=False)
    PurchaseBillItem.query.filter(
        PurchaseBillItem.bill_id.in_(
            db.session.query(PurchaseBill.id).filter_by(company_id=company_id)
        )
    ).delete(synchronize_session=False)
    PaymentIn.query.filter_by(company_id=company_id).delete()
    PaymentOut.query.filter_by(company_id=company_id).delete()
    SaleInvoice.query.filter_by(company_id=company_id).delete()
    PurchaseBill.query.filter_by(company_id=company_id).delete()
    Expense.query.filter_by(company_id=company_id).delete()
    OtherIncome.query.filter_by(company_id=company_id).delete()
    Cheque.query.filter_by(company_id=company_id).delete()
    LoanAccount.query.filter_by(company_id=company_id).delete()
    BankAccount.query.filter_by(company_id=company_id).delete()
    CashInHand.query.filter_by(company_id=company_id).delete()
    Item.query.filter_by(company_id=company_id).delete()
    ItemCategory.query.filter_by(company_id=company_id).delete()
    ExpenseCategory.query.filter_by(company_id=company_id).delete()
    IncomeCategory.query.filter_by(company_id=company_id).delete()
    Party.query.filter_by(company_id=company_id).delete()
    db.session.commit()


def seed_company(company):
    """Update company with full Indian business details."""
    company.company_name = 'Sharma Electronics & Traders'
    company.business_type = 'Retail'
    company.gstin = '27AABCS1234F1ZN'
    company.pan_number = 'AABCS1234F'
    company.phone_number = '022-28501234'
    company.email = 'info@sharmaelectronics.in'
    company.website = 'www.sharmaelectronics.in'
    company.address_line1 = 'Shop No. 12, Patel Market'
    company.address_line2 = 'Andheri East'
    company.city = 'Mumbai'
    company.state = 'Maharashtra'
    company.pincode = '400069'
    company.country = 'India'
    company.financial_year_start = date(2025, 4, 1)
    company.currency = 'INR'

    # GST settings
    gst = GSTSettings.query.filter_by(company_id=company.id).first()
    if gst:
        gst.enable_gst = True
        gst.company_state = 'Maharashtra'
        gst.gst_type = 'intra'

    # Invoice settings
    inv_settings = InvoiceSettings.query.filter_by(company_id=company.id).first()
    if inv_settings:
        inv_settings.invoice_prefix = 'INV-'
        inv_settings.next_invoice_number = 1
        inv_settings.purchase_prefix = 'PUR-'
        inv_settings.next_purchase_number = 1
        inv_settings.default_terms = 'Goods once sold will not be returned. E.&O.E.'
        inv_settings.default_notes = 'Thank you for your business!'

    db.session.commit()
    print(f"✅ Company: {company.company_name} (GSTIN: {company.gstin})")
    return company


def seed_parties(company_id):
    """Create realistic Indian customers and suppliers."""
    parties_data = [
        # ─── Customers ──────────────────────────────────────────────
        {'party_type':'customer','name':'Rajesh Kumar','phone':'9820123456','email':'rajesh.kumar@gmail.com',
         'gstin':'27AABCR5678G1ZQ','billing_address':'45, Dadar West, Mumbai','city':'Mumbai',
         'state':'Maharashtra','pincode':'400028','payment_terms_days':30,'credit_limit':200000},
        {'party_type':'customer','name':'Priya Patel Enterprises','phone':'9821234567','email':'priya@patelent.com',
         'gstin':'27AABCP9012H1ZR','billing_address':'12, Vashi, Navi Mumbai','city':'Navi Mumbai',
         'state':'Maharashtra','pincode':'400703','payment_terms_days':15,'credit_limit':500000},
        {'party_type':'customer','name':'Mehta & Sons Electronics','phone':'9833345678','email':'orders@mehtasons.in',
         'gstin':'27AABCM3456I1ZS','billing_address':'78, Bhuleshwar, Mumbai','city':'Mumbai',
         'state':'Maharashtra','pincode':'400002','payment_terms_days':30,'credit_limit':300000},
        {'party_type':'customer','name':'Sanjay Verma (Cash)','phone':'9844456789','email':'',
         'gstin':'','billing_address':'Shop 5, Hill Road, Bandra','city':'Mumbai',
         'state':'Maharashtra','pincode':'400050','payment_terms_days':0,'credit_limit':0},
        {'party_type':'customer','name':'Deepika Trading Co.','phone':'9855567890','email':'deepika@trading.co.in',
         'gstin':'27AABCD7890J1ZT','billing_address':'301, Trade Center, Andheri','city':'Mumbai',
         'state':'Maharashtra','pincode':'400053','payment_terms_days':45,'credit_limit':400000},
        {'party_type':'customer','name':'Amit Deshmukh','phone':'9866678901','email':'amit.d@gmail.com',
         'gstin':'','billing_address':'22, MG Road, Pune','city':'Pune',
         'state':'Maharashtra','pincode':'411001','payment_terms_days':15,'credit_limit':100000},
        {'party_type':'customer','name':'Gupta Infotech Pvt Ltd','phone':'9811234567','email':'purchase@guptainfotech.com',
         'gstin':'07AABCG2345K1ZU','billing_address':'55, Nehru Place, New Delhi','city':'New Delhi',
         'state':'Delhi','pincode':'110019','payment_terms_days':30,'credit_limit':600000},

        # ─── Suppliers ──────────────────────────────────────────────
        {'party_type':'supplier','name':'Samsung India Distributors','phone':'1800123456','email':'orders@samsungindia.com',
         'gstin':'27AABCS9999A1ZA','billing_address':'Samsung Tower, Sector 126, Noida','city':'Noida',
         'state':'Maharashtra','pincode':'201303','payment_terms_days':60,'credit_limit':1000000},
        {'party_type':'supplier','name':'Havells India Ltd','phone':'1800112233','email':'supply@havells.com',
         'gstin':'27AABCH1111B1ZB','billing_address':'QRG Towers, CBD Belapur','city':'Navi Mumbai',
         'state':'Maharashtra','pincode':'400614','payment_terms_days':45,'credit_limit':800000},
        {'party_type':'supplier','name':'Bajaj Electricals Ltd','phone':'1800445566','email':'dist@bajajelec.com',
         'gstin':'27AABCB2222C1ZC','billing_address':'45/47, Veer Nariman Road, Fort','city':'Mumbai',
         'state':'Maharashtra','pincode':'400001','payment_terms_days':30,'credit_limit':500000},
        {'party_type':'supplier','name':'Philips Lighting India','phone':'1800778899','email':'orders@philips.in',
         'gstin':'27AABCP3333D1ZD','billing_address':'Technopolis, Goregaon East','city':'Mumbai',
         'state':'Maharashtra','pincode':'400063','payment_terms_days':30,'credit_limit':400000},
        {'party_type':'supplier','name':'Asian Paints Depot','phone':'022-28765432','email':'depot@asianpaints.com',
         'gstin':'27AABCA4444E1ZE','billing_address':'6A, Shantinagar, Santacruz','city':'Mumbai',
         'state':'Maharashtra','pincode':'400055','payment_terms_days':45,'credit_limit':300000},

        # ─── Both (Customer + Supplier) ────────────────────────────
        {'party_type':'both','name':'Krishna Wholesale Mart','phone':'9877789012','email':'krishna@wholesale.in',
         'gstin':'27AABCK5555F1ZF','billing_address':'102, Crawford Market','city':'Mumbai',
         'state':'Maharashtra','pincode':'400001','payment_terms_days':30,'credit_limit':500000},
    ]

    created = []
    for p in parties_data:
        party = Party(
            company_id=company_id,
            **p,
            balance_type='receivable' if p['party_type'] in ('customer', 'both') else 'payable',
            opening_balance=0,
            current_balance=0,
        )
        db.session.add(party)
        created.append(party)

    db.session.commit()
    print(f"✅ Parties: {len(created)} (Customers/Suppliers/Both)")
    return created


def seed_item_categories(company_id):
    """Create product categories."""
    cats = [
        'LED TVs & Monitors', 'Mobile Phones & Tablets', 'Home Appliances',
        'Electrical Fittings', 'Computer Accessories', 'Cables & Wires',
        'Batteries & Power', 'Audio & Speakers'
    ]
    created = []
    for name in cats:
        cat = ItemCategory(company_id=company_id, name=name)
        db.session.add(cat)
        created.append(cat)
    db.session.commit()
    print(f"✅ Item Categories: {len(created)}")
    return created


def seed_items(company_id, categories):
    """Create products with realistic Indian prices and HSN codes."""
    cat_map = {c.name: c.id for c in categories}

    items_data = [
        # LED TVs
        {'item_name':'Samsung 43" Crystal UHD TV','item_code':'SAM-TV-43','hsn_code':'8528',
         'category':'LED TVs & Monitors','unit':'pcs','sale_price':32990,'purchase_price':26500,'gst_rate':18,'stock':8,'min_alert':5,'barcode':'8806094905632'},
        {'item_name':'LG 55" OLED Smart TV','item_code':'LG-TV-55','hsn_code':'8528',
         'category':'LED TVs & Monitors','unit':'pcs','sale_price':89990,'purchase_price':72000,'gst_rate':18,'stock':4,'min_alert':3,'barcode':'8801031541027'},
        {'item_name':'Samsung 32" HD Monitor','item_code':'SAM-MON-32','hsn_code':'8528',
         'category':'LED TVs & Monitors','unit':'pcs','sale_price':15490,'purchase_price':12200,'gst_rate':18,'stock':15,'min_alert':5,'barcode':'8806094332810'},

        # Mobiles
        {'item_name':'Samsung Galaxy S24 Ultra','item_code':'SAM-S24U','hsn_code':'8517',
         'category':'Mobile Phones & Tablets','unit':'pcs','sale_price':129999,'purchase_price':108000,'gst_rate':12,'stock':6,'min_alert':3,'barcode':'8806095350219'},
        {'item_name':'iPhone 15 Pro Max','item_code':'APL-15PM','hsn_code':'8517',
         'category':'Mobile Phones & Tablets','unit':'pcs','sale_price':159900,'purchase_price':138000,'gst_rate':12,'stock':3,'min_alert':3,'barcode':'1942065920010'},
        {'item_name':'Redmi Note 13 Pro','item_code':'XMI-N13P','hsn_code':'8517',
         'category':'Mobile Phones & Tablets','unit':'pcs','sale_price':24999,'purchase_price':20500,'gst_rate':12,'stock':20,'min_alert':5,'barcode':'6941812739457'},

        # Home Appliances
        {'item_name':'Havells Instanio 25L Geyser','item_code':'HAV-GEY-25','hsn_code':'8516',
         'category':'Home Appliances','unit':'pcs','sale_price':12500,'purchase_price':9800,'gst_rate':18,'stock':10,'min_alert':5,'barcode':'8904004402734'},
        {'item_name':'Bajaj Majesty 750W Mixer','item_code':'BAJ-MIX-750','hsn_code':'8509',
         'category':'Home Appliances','unit':'pcs','sale_price':3999,'purchase_price':3100,'gst_rate':18,'stock':25,'min_alert':8,'barcode':'8901057305181'},
        {'item_name':'Crompton HS Plus Ceiling Fan','item_code':'CRM-FAN-48','hsn_code':'8414',
         'category':'Home Appliances','unit':'pcs','sale_price':2450,'purchase_price':1850,'gst_rate':18,'stock':30,'min_alert':10,'barcode':'8904101913025'},
        {'item_name':'Philips Air Purifier AC1215','item_code':'PHI-AP-1215','hsn_code':'8421',
         'category':'Home Appliances','unit':'pcs','sale_price':9999,'purchase_price':7800,'gst_rate':18,'stock':5,'min_alert':3,'barcode':'8710103856412'},

        # Electrical Fittings
        {'item_name':'Havells MCB 32A SP','item_code':'HAV-MCB-32','hsn_code':'8536',
         'category':'Electrical Fittings','unit':'pcs','sale_price':380,'purchase_price':295,'gst_rate':18,'stock':100,'min_alert':20,'barcode':'8904004407128'},
        {'item_name':'Anchor Roma 6A Switch','item_code':'ANC-SW-6A','hsn_code':'8536',
         'category':'Electrical Fittings','unit':'pcs','sale_price':95,'purchase_price':68,'gst_rate':18,'stock':200,'min_alert':30,'barcode':'8901440001523'},
        {'item_name':'Philips 12W LED Bulb (Pack of 4)','item_code':'PHI-LED-12','hsn_code':'9405',
         'category':'Electrical Fittings','unit':'pack','sale_price':499,'purchase_price':360,'gst_rate':12,'stock':80,'min_alert':15,'barcode':'8719514452725'},

        # Computer Accessories
        {'item_name':'Logitech MK270 Wireless Combo','item_code':'LOG-MK270','hsn_code':'8471',
         'category':'Computer Accessories','unit':'pcs','sale_price':1795,'purchase_price':1350,'gst_rate':18,'stock':20,'min_alert':5,'barcode':'5099206039810'},
        {'item_name':'HP LaserJet M1005 Toner','item_code':'HP-TNR-M1005','hsn_code':'8443',
         'category':'Computer Accessories','unit':'pcs','sale_price':2499,'purchase_price':1900,'gst_rate':18,'stock':15,'min_alert':5,'barcode':'8870982044103'},
        {'item_name':'TP-Link Archer C6 Router','item_code':'TPL-C6','hsn_code':'8517',
         'category':'Computer Accessories','unit':'pcs','sale_price':2999,'purchase_price':2350,'gst_rate':18,'stock':12,'min_alert':4,'barcode':'6935364084318'},

        # Cables
        {'item_name':'Havells FR 1.5 sq mm Wire (90m)','item_code':'HAV-WR-1.5','hsn_code':'8544',
         'category':'Cables & Wires','unit':'roll','sale_price':2650,'purchase_price':2100,'gst_rate':18,'stock':25,'min_alert':8,'barcode':'8904004401935'},
        {'item_name':'Polycab 4 sq mm Cable (90m)','item_code':'POL-CB-4','hsn_code':'8544',
         'category':'Cables & Wires','unit':'roll','sale_price':5200,'purchase_price':4100,'gst_rate':18,'stock':15,'min_alert':5,'barcode':'8906004572039'},
        {'item_name':'Anchor HDMI 2.0 Cable 3m','item_code':'ANC-HDMI-3','hsn_code':'8544',
         'category':'Cables & Wires','unit':'pcs','sale_price':499,'purchase_price':320,'gst_rate':18,'stock':40,'min_alert':10,'barcode':'8901440076218'},

        # Batteries
        {'item_name':'Luminous RC 18000 Inverter Battery','item_code':'LUM-BAT-18','hsn_code':'8507',
         'category':'Batteries & Power','unit':'pcs','sale_price':14999,'purchase_price':12200,'gst_rate':28,'stock':6,'min_alert':3,'barcode':'8906008920582'},
        {'item_name':'APC BX1100 UPS 1100VA','item_code':'APC-UPS-1100','hsn_code':'8504',
         'category':'Batteries & Power','unit':'pcs','sale_price':5999,'purchase_price':4700,'gst_rate':18,'stock':8,'min_alert':3,'barcode':'7319991863810'},

        # Audio
        {'item_name':'JBL Flip 6 Bluetooth Speaker','item_code':'JBL-FLIP6','hsn_code':'8518',
         'category':'Audio & Speakers','unit':'pcs','sale_price':9999,'purchase_price':7800,'gst_rate':18,'stock':10,'min_alert':4,'barcode':'6925281992612'},
        {'item_name':'boAt Airdopes 141 TWS','item_code':'BOAT-141','hsn_code':'8518',
         'category':'Audio & Speakers','unit':'pcs','sale_price':1299,'purchase_price':850,'gst_rate':18,'stock':50,'min_alert':10,'barcode':'8906110849427'},
    ]

    created = []
    for it in items_data:
        item = Item(
            company_id=company_id,
            item_name=it['item_name'],
            item_code=it['item_code'],
            hsn_code=it['hsn_code'],
            category_id=cat_map.get(it['category']),
            unit=it['unit'],
            sale_price=D(it['sale_price']),
            purchase_price=D(it['purchase_price']),
            gst_rate=D(it['gst_rate']),
            opening_stock_qty=D(it['stock']),
            current_stock=D(it['stock']),
            min_stock_alert=D(it.get('min_alert', max(2, it['stock'] // 5))),
            barcode=it.get('barcode', ''),
        )
        db.session.add(item)
        created.append(item)
    db.session.commit()
    print(f"✅ Items: {len(created)} products with stock")
    return created


def seed_expense_categories(company_id):
    cats = ['Rent', 'Electricity', 'Salaries & Wages', 'Internet & Phone',
            'Office Supplies', 'Transport & Delivery', 'Maintenance & Repair',
            'Marketing & Advertising', 'Professional Fees', 'Miscellaneous']
    created = []
    for name in cats:
        c = ExpenseCategory(company_id=company_id, name=name)
        db.session.add(c)
        created.append(c)
    db.session.commit()
    print(f"✅ Expense Categories: {len(created)}")
    return created


def seed_income_categories(company_id):
    cats = ['Interest Income', 'Rental Income', 'Commission', 'Scrap Sale',
            'Discount Received', 'Insurance Claim']
    created = []
    for name in cats:
        c = IncomeCategory(company_id=company_id, name=name)
        db.session.add(c)
        created.append(c)
    db.session.commit()
    print(f"✅ Income Categories: {len(created)}")
    return created


def seed_bank_accounts(company_id):
    """Create bank accounts, cash-in-hand, and a loan."""
    banks = [
        {'account_name':'HDFC Current A/c','account_number':'50200012345678','bank_name':'HDFC Bank',
         'ifsc_code':'HDFC0001234','opening_balance':325000,'account_type':'current'},
        {'account_name':'SBI Savings A/c','account_number':'32145678901','bank_name':'State Bank of India',
         'ifsc_code':'SBIN0005678','opening_balance':125000,'account_type':'savings'},
    ]
    created_banks = []
    for b in banks:
        ba = BankAccount(
            company_id=company_id,
            account_name=b['account_name'],
            account_number=b['account_number'],
            bank_name=b['bank_name'],
            ifsc_code=b['ifsc_code'],
            opening_balance=D(b['opening_balance']),
            current_balance=D(b['opening_balance']),
            account_type=b['account_type'],
        )
        db.session.add(ba)
        created_banks.append(ba)

    # Cash in hand
    cash = CashInHand(
        company_id=company_id,
        opening_balance=D(45000),
        current_balance=D(45000),
        last_updated=MONTH_START,
    )
    db.session.add(cash)

    # Loan
    loan = LoanAccount(
        company_id=company_id,
        lender_name='HDFC Bank',
        loan_amount=D(500000),
        interest_rate=D(11.5),
        emi_amount=D(10950),
        start_date=date(2025, 6, 1),
        tenure_months=60,
        outstanding_balance=D(425000),
        loan_type='term',
    )
    db.session.add(loan)

    db.session.commit()
    print(f"✅ Bank Accounts: {len(created_banks)} | Cash-in-Hand: ₹45,000 | Loan: ₹5,00,000")
    return created_banks, cash


def calc_gst(price, gst_rate, qty=1, discount_pct=0):
    """Calculate GST for a line item (intra-state: CGST+SGST split)."""
    taxable = float(price) * float(qty)
    disc = taxable * float(discount_pct) / 100
    taxable -= disc
    tax = taxable * float(gst_rate) / 100
    half = round(tax / 2, 2)
    return {
        'taxable': round(taxable, 2),
        'discount': round(disc, 2),
        'tax': round(tax, 2),
        'cgst': half,
        'sgst': half,
        'total': round(taxable + tax, 2),
    }


def seed_sale_invoices(company_id, customers, items, user_id):
    """Create ~20 sale invoices spread across March 2026."""
    invoice_defs = [
        # (customer_idx, [(item_idx, qty, disc%)], payment_type, amount_received_pct)
        (0, [(0, 1, 0), (12, 4, 0)],      'credit', 0.6),    # Rajesh – TV + LED bulbs
        (1, [(3, 2, 5), (5, 3, 0)],        'credit', 1.0),    # Priya Patel – Galaxy S24 x2 + Redmi x3
        (2, [(1, 1, 0), (20, 2, 0)],       'credit', 0.0),    # Mehta – LG OLED + JBL
        (3, [(5, 1, 0), (21, 2, 0)],       'cash', 1.0),      # Sanjay (Cash) – Redmi + boAt
        (4, [(2, 5, 10), (13, 5, 5)],      'credit', 0.5),    # Deepika – 5 monitors + 5 keyboards
        (5, [(7, 3, 0), (8, 5, 0)],        'credit', 1.0),    # Amit – Mixers + Fans
        (6, [(4, 1, 0), (15, 3, 0)],       'credit', 0.0),    # Gupta Infotech – iPhone + Routers
        (0, [(10, 20, 0), (11, 50, 0)],    'credit', 0.4),    # Rajesh – MCBs + Switches
        (1, [(6, 2, 0), (9, 1, 10)],       'credit', 1.0),    # Priya – Geysers + Air Purifier
        (12, [(0, 3, 8), (2, 5, 8)],       'credit', 0.3),    # Krishna Wholesale – TVs
        (2, [(16, 10, 0), (17, 5, 0)],     'credit', 0.5),    # Mehta – Wires + Cables
        (4, [(19, 3, 0), (14, 5, 0)],      'credit', 0.7),    # Deepika – UPS + Toners
        (3, [(8, 2, 0), (12, 8, 0)],       'cash', 1.0),      # Sanjay Cash – Fans + Bulbs
        (5, [(18, 5, 0)],                   'credit', 0.0),    # Amit – HDMI cables
        (6, [(3, 1, 0), (21, 10, 5)],      'credit', 0.8),    # Gupta – Galaxy + boAt bulk
        (0, [(7, 2, 0)],                    'credit', 1.0),    # Rajesh – Mixers
        (12, [(5, 10, 10), (21, 20, 10)],  'credit', 0.0),    # Krishna – Redmi bulk + boAt bulk
        (1, [(15, 2, 0), (13, 3, 0)],      'credit', 1.0),    # Priya – Routers + Keyboards
        (2, [(20, 3, 0)],                   'credit', 0.5),    # Mehta – JBL speakers
        (4, [(0, 2, 5), (8, 10, 5)],       'credit', 0.0),    # Deepika – TVs + Fans
    ]

    inv_num = 1
    created = []

    for cust_idx, line_items, pay_type, recv_pct in invoice_defs:
        inv_date = random_date()
        due_date = inv_date + timedelta(days=customers[cust_idx].payment_terms_days or 30)

        subtotal = 0
        disc_total = 0
        tax_total = 0
        inv_items = []

        for item_idx, qty, disc_pct in line_items:
            item = items[item_idx]
            g = calc_gst(item.sale_price, item.gst_rate, qty, disc_pct)
            subtotal += float(item.sale_price) * qty
            disc_total += g['discount']
            tax_total += g['tax']

            inv_items.append({
                'item': item, 'qty': qty, 'disc_pct': disc_pct, 'calc': g
            })

        grand_total = round(subtotal - disc_total + tax_total, 2)
        # Round off to nearest rupee
        round_off = round(round(grand_total) - grand_total, 2)
        grand_total = round(grand_total + round_off, 2)
        amount_received = round(grand_total * recv_pct, 2)
        balance_due = round(grand_total - amount_received, 2)

        status = 'paid' if balance_due <= 0 else ('partial' if amount_received > 0 else 'unpaid')

        invoice = SaleInvoice(
            company_id=company_id,
            invoice_number=f'INV-{inv_num:05d}',
            invoice_date=inv_date,
            due_date=due_date,
            party_id=customers[cust_idx].id,
            billing_address=customers[cust_idx].billing_address,
            place_of_supply='Maharashtra',
            payment_type=pay_type,
            subtotal=D(subtotal),
            discount_total=D(disc_total),
            tax_total=D(tax_total),
            round_off=D(round_off),
            grand_total=D(grand_total),
            amount_received=D(amount_received),
            balance_due=D(balance_due),
            status=status,
            notes='Thank you for your business!',
            terms_conditions='Goods once sold will not be returned. E.&O.E.',
            created_by=user_id,
        )
        db.session.add(invoice)
        db.session.flush()

        for li in inv_items:
            sii = SaleInvoiceItem(
                invoice_id=invoice.id,
                item_id=li['item'].id,
                item_name=li['item'].item_name,
                hsn_code=li['item'].hsn_code,
                quantity=D(li['qty']),
                unit=li['item'].unit,
                unit_price=li['item'].sale_price,
                discount_percent=D(li['disc_pct']),
                discount_amount=D(li['calc']['discount']),
                gst_rate=li['item'].gst_rate,
                cgst_amount=D(li['calc']['cgst']),
                sgst_amount=D(li['calc']['sgst']),
                igst_amount=D(0),
                cess_amount=D(0),
                tax_amount=D(li['calc']['tax']),
                total_amount=D(li['calc']['total']),
            )
            db.session.add(sii)

            # Update stock
            li['item'].current_stock -= D(li['qty'])

        # Payment-In if any amount received
        if amount_received > 0:
            pi = PaymentIn(
                company_id=company_id,
                payment_number=f'REC-INV-{inv_num:05d}',
                payment_date=inv_date,
                party_id=customers[cust_idx].id,
                reference_invoice_id=invoice.id,
                amount_received=D(amount_received),
                payment_mode=pay_type if pay_type == 'cash' else random.choice(['bank', 'upi', 'cash']),
                notes=f'Payment against {invoice.invoice_number}',
                created_by=user_id,
            )
            db.session.add(pi)

        # Update party balance
        customers[cust_idx].current_balance = D(
            float(customers[cust_idx].current_balance or 0) + balance_due)

        created.append(invoice)
        inv_num += 1

    # Update invoice settings counter
    inv_settings = InvoiceSettings.query.filter_by(company_id=company_id).first()
    if inv_settings:
        inv_settings.next_invoice_number = inv_num

    db.session.commit()
    total_sales = sum(float(i.grand_total) for i in created)
    print(f"✅ Sale Invoices: {len(created)} | Total Sales: ₹{total_sales:,.2f}")
    return created


def seed_purchase_bills(company_id, suppliers, items, user_id):
    """Create ~12 purchase bills spread across March 2026."""
    purchase_defs = [
        # (supplier_idx, [(item_idx, qty, disc%)], amount_paid_pct)
        (7, [(0, 10, 0), (1, 5, 0), (2, 15, 0)],  0.5),    # Samsung – TVs + Monitors
        (8, [(6, 15, 0), (10, 100, 5)],             1.0),    # Havells – Geysers + MCBs
        (9, [(7, 30, 0), (8, 40, 0)],               0.0),    # Bajaj – Mixers + Fans
        (10, [(12, 100, 0), (9, 10, 0)],            1.0),    # Philips – LED + Air Purifier
        (11, [(16, 30, 0), (17, 20, 0)],            0.3),    # Asian Paints Depot (as wire supplier) – Wires
        (7, [(3, 8, 0), (5, 25, 0)],                0.6),    # Samsung – Galaxy + Redmi
        (8, [(16, 20, 0)],                          1.0),    # Havells – Wires
        (10, [(12, 80, 0)],                         0.0),    # Philips – LED bulk
        (12, [(21, 60, 10), (20, 15, 5)],           0.5),    # Krishna – boAt + JBL (as both)
        (9, [(8, 50, 5)],                            1.0),    # Bajaj – Fans bulk
        (7, [(4, 5, 0)],                             0.0),    # Samsung – iPhones
        (8, [(6, 10, 0), (10, 50, 0)],               0.7),    # Havells – Geysers + MCBs
    ]

    bill_num = 1
    created = []

    for sup_idx, line_items, paid_pct in purchase_defs:
        bill_date = random_date()
        due_date = bill_date + timedelta(days=suppliers[sup_idx].payment_terms_days or 30)

        subtotal = 0
        disc_total = 0
        tax_total = 0
        bill_items = []

        for item_idx, qty, disc_pct in line_items:
            item = items[item_idx]
            g = calc_gst(item.purchase_price, item.gst_rate, qty, disc_pct)
            subtotal += float(item.purchase_price) * qty
            disc_total += g['discount']
            tax_total += g['tax']
            bill_items.append({'item': item, 'qty': qty, 'disc_pct': disc_pct, 'calc': g})

        grand_total = round(subtotal - disc_total + tax_total, 2)
        round_off = round(round(grand_total) - grand_total, 2)
        grand_total = round(grand_total + round_off, 2)
        amount_paid = round(grand_total * paid_pct, 2)
        balance_due = round(grand_total - amount_paid, 2)
        payment_status = 'paid' if balance_due <= 0 else ('partial' if amount_paid > 0 else 'unpaid')

        bill = PurchaseBill(
            company_id=company_id,
            bill_number=f'PUR-{bill_num:05d}',
            bill_date=bill_date,
            due_date=due_date,
            supplier_id=suppliers[sup_idx].id,
            subtotal=D(subtotal),
            discount_total=D(disc_total),
            tax_total=D(tax_total),
            round_off=D(round_off),
            grand_total=D(grand_total),
            amount_paid=D(amount_paid),
            balance_due=D(balance_due),
            payment_status=payment_status,
            notes='Purchase order received',
            created_by=user_id,
        )
        db.session.add(bill)
        db.session.flush()

        for li in bill_items:
            pbi = PurchaseBillItem(
                bill_id=bill.id,
                item_id=li['item'].id,
                item_name=li['item'].item_name,
                hsn_code=li['item'].hsn_code,
                quantity=D(li['qty']),
                unit=li['item'].unit,
                unit_price=li['item'].purchase_price,
                discount_percent=D(li['disc_pct']),
                discount_amount=D(li['calc']['discount']),
                gst_rate=li['item'].gst_rate,
                cgst_amount=D(li['calc']['cgst']),
                sgst_amount=D(li['calc']['sgst']),
                igst_amount=D(0),
                cess_amount=D(0),
                tax_amount=D(li['calc']['tax']),
                total_amount=D(li['calc']['total']),
            )
            db.session.add(pbi)

            # Update stock (add)
            li['item'].current_stock += D(li['qty'])

        if amount_paid > 0:
            po = PaymentOut(
                company_id=company_id,
                payment_number=f'PAY-PUR-{bill_num:05d}',
                payment_date=bill_date,
                supplier_id=suppliers[sup_idx].id,
                reference_bill_id=bill.id,
                amount_paid=D(amount_paid),
                payment_mode=random.choice(['bank', 'bank', 'cheque']),
                notes=f'Payment against {bill.bill_number}',
                created_by=user_id,
            )
            db.session.add(po)

        # Update supplier balance
        suppliers[sup_idx].current_balance = D(
            float(suppliers[sup_idx].current_balance or 0) + balance_due)

        created.append(bill)
        bill_num += 1

    inv_settings = InvoiceSettings.query.filter_by(company_id=company_id).first()
    if inv_settings:
        inv_settings.next_purchase_number = bill_num

    db.session.commit()
    total_purchases = sum(float(b.grand_total) for b in created)
    print(f"✅ Purchase Bills: {len(created)} | Total Purchases: ₹{total_purchases:,.2f}")
    return created


def seed_expenses(company_id, exp_categories, user_id):
    """Create ~25 expense entries across March 2026."""
    expenses_data = [
        ('Rent', 35000, 'Shop Rent for March 2026', date(2026, 3, 1)),
        ('Electricity', 8500, 'MSEB Bill March', date(2026, 3, 5)),
        ('Salaries & Wages', 65000, 'Staff salary – 2 helpers', date(2026, 3, 1)),
        ('Salaries & Wages', 25000, 'Part-time delivery boy', date(2026, 3, 1)),
        ('Internet & Phone', 2999, 'Jio Fiber + Mobile plan', date(2026, 3, 3)),
        ('Office Supplies', 1250, 'Printer cartridge + paper', date(2026, 3, 4)),
        ('Office Supplies', 850, 'Stationery – bills books, pens', date(2026, 3, 10)),
        ('Transport & Delivery', 3500, 'Courier charges (DTDC)', date(2026, 3, 6)),
        ('Transport & Delivery', 2200, 'Local delivery – autorickshaw', date(2026, 3, 12)),
        ('Transport & Delivery', 4800, 'Goods transport – Andheri to Pune', date(2026, 3, 18)),
        ('Maintenance & Repair', 5500, 'AC servicing – shop', date(2026, 3, 8)),
        ('Maintenance & Repair', 1800, 'Electrical repair work', date(2026, 3, 22)),
        ('Marketing & Advertising', 12000, 'Google Ads – March campaign', date(2026, 3, 1)),
        ('Marketing & Advertising', 5000, 'Pamphlet printing 2000 copies', date(2026, 3, 15)),
        ('Marketing & Advertising', 3500, 'Instagram sponsored post', date(2026, 3, 20)),
        ('Professional Fees', 8000, 'CA quarterly fees', date(2026, 3, 25)),
        ('Professional Fees', 2500, 'Legal consultation', date(2026, 3, 28)),
        ('Miscellaneous', 1200, 'Tea/snacks for shop', date(2026, 3, 7)),
        ('Miscellaneous', 750, 'Drinking water RO filter', date(2026, 3, 14)),
        ('Miscellaneous', 2000, 'Staff uniforms', date(2026, 3, 21)),
        ('Transport & Delivery', 1500, 'Petrol for delivery bike', date(2026, 3, 9)),
        ('Office Supplies', 3200, 'Thermal printer roll x 20', date(2026, 3, 16)),
        ('Electricity', 2100, 'Generator diesel', date(2026, 3, 11)),
        ('Maintenance & Repair', 3000, 'Computer formatting & antivirus', date(2026, 3, 19)),
        ('Miscellaneous', 1500, 'Diwali advance decoration material', date(2026, 3, 30)),
    ]

    cat_map = {c.name: c.id for c in exp_categories}
    created = []
    for cat_name, amount, notes, exp_date in expenses_data:
        exp = Expense(
            company_id=company_id,
            expense_date=exp_date,
            category_id=cat_map.get(cat_name),
            amount=D(amount),
            payment_mode=random.choice(['cash', 'bank', 'upi']),
            notes=notes,
            created_by=user_id,
        )
        db.session.add(exp)
        created.append(exp)

    db.session.commit()
    total = sum(float(e.amount) for e in created)
    print(f"✅ Expenses: {len(created)} entries | Total: ₹{total:,.2f}")
    return created


def seed_other_income(company_id, income_categories, user_id):
    """Create other income entries."""
    cat_map = {c.name: c.id for c in income_categories}
    incomes = [
        ('Interest Income', 1250, 'SBI Savings interest Q4', date(2026, 3, 31)),
        ('Commission', 8500, 'Commission from Samsung on target achievement', date(2026, 3, 15)),
        ('Scrap Sale', 3200, 'Old packaging material sold', date(2026, 3, 10)),
        ('Discount Received', 4500, 'Early payment discount – Havells', date(2026, 3, 20)),
        ('Interest Income', 850, 'HDFC Current A/c interest', date(2026, 3, 31)),
        ('Commission', 3000, 'Referral commission – Bajaj', date(2026, 3, 25)),
        ('Rental Income', 15000, 'Sub-let storage room rent', date(2026, 3, 1)),
    ]

    created = []
    for cat_name, amount, notes, inc_date in incomes:
        inc = OtherIncome(
            company_id=company_id,
            income_date=inc_date,
            category_id=cat_map.get(cat_name),
            amount=D(amount),
            payment_mode=random.choice(['cash', 'bank']),
            notes=notes,
            created_by=user_id,
        )
        db.session.add(inc)
        created.append(inc)

    db.session.commit()
    total = sum(float(i.amount) for i in created)
    print(f"✅ Other Income: {len(created)} entries | Total: ₹{total:,.2f}")
    return created


def seed_cheques(company_id, parties):
    """Create cheque entries – a mix of received, issued, cleared, pending, bounced."""
    cheques_data = [
        ('891234', parties[0].id, 'HDFC Bank', 45000, date(2026, 3, 5),  'received', 'cleared'),
        ('891235', parties[1].id, 'ICICI Bank', 85000, date(2026, 3, 8),  'received', 'cleared'),
        ('891236', parties[2].id, 'SBI',        120000, date(2026, 3, 12), 'received', 'pending'),
        ('891237', parties[4].id, 'Axis Bank',  55000, date(2026, 3, 15), 'received', 'pending'),
        ('891238', parties[6].id, 'HDFC Bank',  200000, date(2026, 3, 18), 'received', 'bounced'),
        ('445501', parties[7].id, 'HDFC Bank',  180000, date(2026, 3, 3),  'issued', 'cleared'),
        ('445502', parties[8].id, 'HDFC Bank',  95000, date(2026, 3, 10), 'issued', 'cleared'),
        ('445503', parties[9].id, 'HDFC Bank',  62000, date(2026, 3, 20), 'issued', 'pending'),
        ('445504', parties[10].id, 'HDFC Bank', 35000, date(2026, 3, 25), 'issued', 'pending'),
    ]

    created = []
    for chq_num, party_id, bank, amount, issue_dt, chq_type, status in cheques_data:
        c = Cheque(
            company_id=company_id,
            cheque_number=chq_num,
            party_id=party_id,
            bank_name=bank,
            amount=D(amount),
            issue_date=issue_dt,
            clearance_date=issue_dt + timedelta(days=3) if status == 'cleared' else None,
            cheque_type=chq_type,
            status=status,
        )
        db.session.add(c)
        created.append(c)

    db.session.commit()
    print(f"✅ Cheques: {len(created)} (received/issued, cleared/pending/bounced)")
    return created


def seed_april_sales(company_id, parties, items, user_id):
    """Create April 2026 sale invoices (today = April 1)."""
    # Get current invoice number
    inv_settings = InvoiceSettings.query.filter_by(company_id=company_id).first()
    inv_num = inv_settings.next_invoice_number if inv_settings else 21

    # April 1 invoices
    april_sales = [
        # (party_idx, [(item_idx, qty, disc%)], payment_type, recv_pct)
        (0, [(0, 2, 0), (5, 3, 5)],      'credit', 0.5),    # Rajesh – 2 TVs + 3 Redmi
        (1, [(3, 1, 0), (20, 2, 0)],      'credit', 1.0),    # Priya – Galaxy S24 + JBL
        (3, [(8, 3, 0), (21, 5, 0)],      'cash',   1.0),    # Sanjay cash – 3 Fans + 5 boAt
        (2, [(2, 3, 0), (13, 2, 0)],      'credit', 0.0),    # Mehta – 3 Monitors + 2 Keyboards
        (4, [(12, 10, 0), (10, 15, 0)],   'credit', 0.3),    # Deepika – 10 LED bulbs + 15 MCBs
        (5, [(7, 2, 0), (6, 1, 0)],       'credit', 1.0),    # Amit – 2 Mixers + 1 Geyser
        (6, [(4, 1, 0), (15, 2, 5)],      'credit', 0.0),    # Gupta – 1 iPhone + 2 Routers
        (12, [(16, 5, 0), (18, 10, 0)],   'credit', 0.4),    # Krishna – 5 Wires + 10 HDMI cables
        (0, [(19, 1, 0), (14, 2, 0)],     'credit', 0.7),    # Rajesh – 1 Battery + 2 Toners
        (1, [(1, 1, 10), (9, 1, 0)],      'credit', 0.8),    # Priya – 1 LG OLED discounted + Air Purifier
    ]

    created = []
    for cust_idx, line_items, pay_type, recv_pct in april_sales:
        inv_date = APR_START
        due_date = inv_date + timedelta(days=parties[cust_idx].payment_terms_days or 30)

        subtotal = 0
        disc_total = 0
        tax_total = 0
        inv_items = []

        for item_idx, qty, disc_pct in line_items:
            item = items[item_idx]
            g = calc_gst(item.sale_price, item.gst_rate, qty, disc_pct)
            subtotal += float(item.sale_price) * qty
            disc_total += g['discount']
            tax_total += g['tax']
            inv_items.append({'item': item, 'qty': qty, 'disc_pct': disc_pct, 'calc': g})

        grand_total = round(subtotal - disc_total + tax_total, 2)
        round_off = round(round(grand_total) - grand_total, 2)
        grand_total = round(grand_total + round_off, 2)
        amount_received = round(grand_total * recv_pct, 2)
        balance_due = round(grand_total - amount_received, 2)
        status = 'paid' if balance_due <= 0 else ('partial' if amount_received > 0 else 'unpaid')

        invoice = SaleInvoice(
            company_id=company_id,
            invoice_number=f'INV-{inv_num:05d}',
            invoice_date=inv_date,
            due_date=due_date,
            party_id=parties[cust_idx].id,
            billing_address=parties[cust_idx].billing_address,
            place_of_supply='Maharashtra',
            payment_type=pay_type,
            subtotal=D(subtotal),
            discount_total=D(disc_total),
            tax_total=D(tax_total),
            round_off=D(round_off),
            grand_total=D(grand_total),
            amount_received=D(amount_received),
            balance_due=D(balance_due),
            status=status,
            notes='Thank you for your business!',
            terms_conditions='Goods once sold will not be returned. E.&O.E.',
            created_by=user_id,
        )
        db.session.add(invoice)
        db.session.flush()

        for li in inv_items:
            sii = SaleInvoiceItem(
                invoice_id=invoice.id,
                item_id=li['item'].id,
                item_name=li['item'].item_name,
                hsn_code=li['item'].hsn_code,
                quantity=D(li['qty']),
                unit=li['item'].unit,
                unit_price=li['item'].sale_price,
                discount_percent=D(li['disc_pct']),
                discount_amount=D(li['calc']['discount']),
                gst_rate=li['item'].gst_rate,
                cgst_amount=D(li['calc']['cgst']),
                sgst_amount=D(li['calc']['sgst']),
                igst_amount=D(0),
                cess_amount=D(0),
                tax_amount=D(li['calc']['tax']),
                total_amount=D(li['calc']['total']),
            )
            db.session.add(sii)
            li['item'].current_stock -= D(li['qty'])

        if amount_received > 0:
            pi = PaymentIn(
                company_id=company_id,
                payment_number=f'REC-INV-{inv_num:05d}',
                payment_date=inv_date,
                party_id=parties[cust_idx].id,
                reference_invoice_id=invoice.id,
                amount_received=D(amount_received),
                payment_mode=pay_type if pay_type == 'cash' else random.choice(['bank', 'upi', 'cash']),
                notes=f'Payment against {invoice.invoice_number}',
                created_by=user_id,
            )
            db.session.add(pi)

        parties[cust_idx].current_balance = D(
            float(parties[cust_idx].current_balance or 0) + balance_due)

        created.append(invoice)
        inv_num += 1

    if inv_settings:
        inv_settings.next_invoice_number = inv_num

    db.session.commit()
    total = sum(float(i.grand_total) for i in created)
    print(f"✅ April Sales: {len(created)} invoices | Total: ₹{total:,.2f}")
    return created


def seed_april_purchases(company_id, parties, items, user_id):
    """Create April 2026 purchase bills (today = April 1)."""
    inv_settings = InvoiceSettings.query.filter_by(company_id=company_id).first()
    bill_num = inv_settings.next_purchase_number if inv_settings else 13

    april_purchases = [
        # (supplier_idx, [(item_idx, qty, disc%)], paid_pct)
        (7, [(0, 5, 0), (3, 3, 0)],  0.4),    # Samsung – 5 TVs + 3 Galaxy
        (8, [(6, 8, 0), (10, 30, 5)], 1.0),    # Havells – 8 Geysers + 30 MCBs
        (9, [(7, 15, 0), (8, 20, 0)], 0.0),    # Bajaj – 15 Mixers + 20 Fans
    ]

    created = []
    for sup_idx, line_items, paid_pct in april_purchases:
        bill_date = APR_START
        due_date = bill_date + timedelta(days=parties[sup_idx].payment_terms_days or 30)

        subtotal = 0
        disc_total = 0
        tax_total = 0
        bill_items = []

        for item_idx, qty, disc_pct in line_items:
            item = items[item_idx]
            g = calc_gst(item.purchase_price, item.gst_rate, qty, disc_pct)
            subtotal += float(item.purchase_price) * qty
            disc_total += g['discount']
            tax_total += g['tax']
            bill_items.append({'item': item, 'qty': qty, 'disc_pct': disc_pct, 'calc': g})

        grand_total = round(subtotal - disc_total + tax_total, 2)
        round_off = round(round(grand_total) - grand_total, 2)
        grand_total = round(grand_total + round_off, 2)
        amount_paid = round(grand_total * paid_pct, 2)
        balance_due = round(grand_total - amount_paid, 2)
        payment_status = 'paid' if balance_due <= 0 else ('partial' if amount_paid > 0 else 'unpaid')

        bill = PurchaseBill(
            company_id=company_id,
            bill_number=f'PUR-{bill_num:05d}',
            bill_date=bill_date,
            due_date=due_date,
            supplier_id=parties[sup_idx].id,
            subtotal=D(subtotal),
            discount_total=D(disc_total),
            tax_total=D(tax_total),
            round_off=D(round_off),
            grand_total=D(grand_total),
            amount_paid=D(amount_paid),
            balance_due=D(balance_due),
            payment_status=payment_status,
            notes='Purchase order received',
            created_by=user_id,
        )
        db.session.add(bill)
        db.session.flush()

        for li in bill_items:
            pbi = PurchaseBillItem(
                bill_id=bill.id,
                item_id=li['item'].id,
                item_name=li['item'].item_name,
                hsn_code=li['item'].hsn_code,
                quantity=D(li['qty']),
                unit=li['item'].unit,
                unit_price=li['item'].purchase_price,
                discount_percent=D(li['disc_pct']),
                discount_amount=D(li['calc']['discount']),
                gst_rate=li['item'].gst_rate,
                cgst_amount=D(li['calc']['cgst']),
                sgst_amount=D(li['calc']['sgst']),
                igst_amount=D(0),
                cess_amount=D(0),
                tax_amount=D(li['calc']['tax']),
                total_amount=D(li['calc']['total']),
            )
            db.session.add(pbi)
            li['item'].current_stock += D(li['qty'])

        if amount_paid > 0:
            po = PaymentOut(
                company_id=company_id,
                payment_number=f'PAY-PUR-{bill_num:05d}',
                payment_date=bill_date,
                supplier_id=parties[sup_idx].id,
                reference_bill_id=bill.id,
                amount_paid=D(amount_paid),
                payment_mode=random.choice(['bank', 'bank', 'cheque']),
                notes=f'Payment against {bill.bill_number}',
                created_by=user_id,
            )
            db.session.add(po)

        parties[sup_idx].current_balance = D(
            float(parties[sup_idx].current_balance or 0) + balance_due)

        created.append(bill)
        bill_num += 1

    if inv_settings:
        inv_settings.next_purchase_number = bill_num

    db.session.commit()
    total = sum(float(b.grand_total) for b in created)
    print(f"✅ April Purchases: {len(created)} bills | Total: ₹{total:,.2f}")
    return created


def seed_april_expenses(company_id, exp_categories, user_id):
    """Create April 1 expense entries."""
    cat_map = {c.name: c.id for c in exp_categories}
    expenses_data = [
        ('Rent', 35000, 'Shop Rent for April 2026', APR_START),
        ('Salaries & Wages', 65000, 'Staff salary – 2 helpers April', APR_START),
        ('Salaries & Wages', 25000, 'Part-time delivery boy April', APR_START),
        ('Internet & Phone', 2999, 'Jio Fiber + Mobile plan April', APR_START),
        ('Transport & Delivery', 1800, 'Local delivery charges', APR_START),
        ('Office Supplies', 950, 'Stationery & printer supplies', APR_START),
        ('Marketing & Advertising', 8000, 'Google Ads – April start', APR_START),
    ]
    created = []
    for cat_name, amount, notes, exp_date in expenses_data:
        exp = Expense(
            company_id=company_id,
            expense_date=exp_date,
            category_id=cat_map.get(cat_name),
            amount=D(amount),
            payment_mode=random.choice(['cash', 'bank', 'upi']),
            notes=notes,
            created_by=user_id,
        )
        db.session.add(exp)
        created.append(exp)

    db.session.commit()
    total = sum(float(e.amount) for e in created)
    print(f"✅ April Expenses: {len(created)} entries | Total: ₹{total:,.2f}")
    return created


def seed_april_income(company_id, income_categories, user_id):
    """Create April 1 income entries."""
    cat_map = {c.name: c.id for c in income_categories}
    incomes = [
        ('Rental Income', 15000, 'Sub-let storage room rent – April', APR_START),
        ('Commission', 5000, 'Commission from Samsung – April target start', APR_START),
    ]
    created = []
    for cat_name, amount, notes, inc_date in incomes:
        inc = OtherIncome(
            company_id=company_id,
            income_date=inc_date,
            category_id=cat_map.get(cat_name),
            amount=D(amount),
            payment_mode=random.choice(['cash', 'bank']),
            notes=notes,
            created_by=user_id,
        )
        db.session.add(inc)
        created.append(inc)

    db.session.commit()
    total = sum(float(i.amount) for i in created)
    print(f"✅ April Income: {len(created)} entries | Total: ₹{total:,.2f}")
    return created


def force_stock_levels(items):
    """Force some items to low stock and out of stock for dashboard visibility."""
    # Items 4 (iPhone) - set to 0 (out of stock)
    items[4].current_stock = D(0)
    items[4].min_stock_alert = D(3)

    # Items 1 (LG OLED TV) - set to 0 (out of stock)
    items[1].current_stock = D(0)
    items[1].min_stock_alert = D(3)

    # Items 9 (Philips Air Purifier) - set to 0 (out of stock)
    items[9].current_stock = D(0)
    items[9].min_stock_alert = D(3)

    # Items 3 (Galaxy S24 Ultra) - low stock (2 left, alert at 3)
    items[3].current_stock = D(2)
    items[3].min_stock_alert = D(3)

    # Items 19 (Luminous Battery) - low stock (1 left, alert at 3)
    items[19].current_stock = D(1)
    items[19].min_stock_alert = D(3)

    # Items 15 (TP-Link Router) - low stock (2 left, alert at 4)
    items[15].current_stock = D(2)
    items[15].min_stock_alert = D(4)

    # Items 14 (HP Toner) - low stock (3 left, alert at 5)
    items[14].current_stock = D(3)
    items[14].min_stock_alert = D(5)

    # Items 20 (JBL Speaker) - low stock (2 left, alert at 4)
    items[20].current_stock = D(2)
    items[20].min_stock_alert = D(4)

    db.session.commit()
    print("✅ Stock levels adjusted: 3 out-of-stock, 5 low-stock items")


def seed_partial_payments(company_id, invoices, parties, user_id):
    """Add multiple partial payments to unpaid/partial invoices to demo payment history."""
    count = 0
    for inv in invoices:
        if inv.status == 'unpaid' and float(inv.balance_due) > 20000:
            # Make 2 partial payments
            pay1_amt = round(float(inv.grand_total) * 0.3, 2)
            pay2_amt = round(float(inv.grand_total) * 0.2, 2)

            for i, (amt, mode, dt_offset) in enumerate([
                (pay1_amt, 'upi', 2),
                (pay2_amt, 'bank', 5),
            ]):
                payment = PaymentIn(
                    company_id=company_id,
                    payment_number=f"REC-PART-{inv.invoice_number}-{i+1}",
                    payment_date=inv.invoice_date + timedelta(days=dt_offset),
                    party_id=inv.party_id,
                    reference_invoice_id=inv.id,
                    amount_received=D(amt),
                    payment_mode=mode,
                    reference_number=f"UTR{random.randint(100000, 999999)}" if mode in ('upi', 'bank') else None,
                    notes=f"Partial payment {i+1} against {inv.invoice_number}",
                    created_by=user_id,
                )
                db.session.add(payment)

            total_paid = pay1_amt + pay2_amt
            inv.amount_received = D(float(inv.amount_received or 0) + total_paid)
            inv.balance_due = D(float(inv.grand_total) - float(inv.amount_received))
            inv.status = 'partial' if float(inv.balance_due) > 0 else 'paid'
            count += 1

            if count >= 4:
                break

    db.session.commit()
    print(f"✅ Partial payments: Added to {count} invoices (2 payments each)")


def update_bank_balances(company_id, bank_accounts, cash):
    """Adjust bank and cash balances based on seeded payments."""
    from sqlalchemy import func

    # Add incoming payments to HDFC (primary)
    total_in = db.session.query(func.coalesce(func.sum(PaymentIn.amount_received), 0)).filter(
        PaymentIn.company_id == company_id,
        PaymentIn.payment_mode == 'bank'
    ).scalar()

    total_out = db.session.query(func.coalesce(func.sum(PaymentOut.amount_paid), 0)).filter(
        PaymentOut.company_id == company_id,
        PaymentOut.payment_mode == 'bank'
    ).scalar()

    # HDFC current account gets the bank transactions
    hdfc = bank_accounts[0]
    hdfc.current_balance = D(float(hdfc.opening_balance) + float(total_in) - float(total_out))

    # Cash balance adjustments
    cash_in = db.session.query(func.coalesce(func.sum(PaymentIn.amount_received), 0)).filter(
        PaymentIn.company_id == company_id,
        PaymentIn.payment_mode == 'cash'
    ).scalar()
    cash_out = db.session.query(func.coalesce(func.sum(PaymentOut.amount_paid), 0)).filter(
        PaymentOut.company_id == company_id,
        PaymentOut.payment_mode == 'cash'
    ).scalar()
    total_expenses_cash = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.company_id == company_id,
        Expense.payment_mode == 'cash'
    ).scalar()

    cash.current_balance = D(
        float(cash.opening_balance) + float(cash_in) - float(cash_out) - float(total_expenses_cash))
    cash.last_updated = MONTH_END

    db.session.commit()
    print(f"✅ Updated balances: HDFC ₹{float(hdfc.current_balance):,.2f} | Cash ₹{float(cash.current_balance):,.2f}")


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════════════════
def run():
    with app.app_context():
        print("\n" + "=" * 60)
        print("   🌱 VYPAR — SEEDING COMPREHENSIVE DEMO DATA")
        print("   📅 Period: March + April 2026")
        print("=" * 60 + "\n")

        # Get company and admin user
        company = Company.query.first()
        admin = User.query.filter_by(role='admin').first()

        if not company or not admin:
            print("❌ No company/admin found. Run the app first to create defaults.")
            sys.exit(1)

        # Clear old data
        clear_old_data(company.id)

        # Seed everything
        company = seed_company(company)
        parties = seed_parties(company.id)
        categories = seed_item_categories(company.id)
        items = seed_items(company.id, categories)
        exp_cats = seed_expense_categories(company.id)
        inc_cats = seed_income_categories(company.id)
        bank_accs, cash = seed_bank_accounts(company.id)

        customers = [p for p in parties if p.party_type in ('customer', 'both')]
        suppliers = parties  # we index by original list position

        invoices = seed_sale_invoices(company.id, parties, items, admin.id)
        bills = seed_purchase_bills(company.id, parties, items, admin.id)
        seed_expenses(company.id, exp_cats, admin.id)
        seed_other_income(company.id, inc_cats, admin.id)
        seed_cheques(company.id, parties)

        # ── April 2026 data (current month) ─────────────────────────
        print("\n── April 2026 (Current Month) ──────────────────")
        apr_invoices = seed_april_sales(company.id, parties, items, admin.id)
        apr_bills = seed_april_purchases(company.id, parties, items, admin.id)
        seed_april_expenses(company.id, exp_cats, admin.id)
        seed_april_income(company.id, inc_cats, admin.id)

        # Add multiple partial payments to some invoices for payment history demo
        seed_partial_payments(company.id, invoices + apr_invoices, parties, admin.id)

        # Force some items to low stock / out of stock
        force_stock_levels(items)

        update_bank_balances(company.id, bank_accs, cash)

        # Summary
        print("\n" + "=" * 60)
        print("   ✅ SEEDING COMPLETE!")
        print("=" * 60)
        print(f"   Company:    {company.company_name}")
        print(f"   Parties:    {len(parties)}")
        print(f"   Items:      {len(items)}")
        print(f"   March Inv:  {len(invoices)} | Apr Inv: {len(apr_invoices)}")
        print(f"   March Pur:  {len(bills)}  | Apr Pur: {len(apr_bills)}")
        print(f"   Login:      admin / admin123")
        print(f"   URL:        http://localhost:5000")
        print("=" * 60 + "\n")


if __name__ == '__main__':
    run()
