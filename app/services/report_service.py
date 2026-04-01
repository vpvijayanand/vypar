"""
Dashboard / Reports Service - Analytics and reporting business logic.
Aggregation queries for dashboard KPIs and all report types.
"""
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import func, extract, case
from app.extensions import db
from app.models.invoice import SaleInvoice
from app.models.invoice import SaleInvoiceItem
from app.models.purchase import PurchaseBill
from app.models.expense import Expense
from app.models.income import OtherIncome
from app.models.payment import PaymentIn, PaymentOut
from app.models.party import Party
from app.models.bank import BankAccount, CashInHand
from app.models.item import Item, ItemCategory
from app.models.expense import Expense, ExpenseCategory
from app.services.inventory_service import InventoryService


class DashboardService:
    """Dashboard KPIs and analytics."""

    @staticmethod
    def get_dashboard_data(company_id, period_start=None, period_end=None):
        """Get all dashboard KPIs."""
        if not period_start:
            period_start = date.today().replace(day=1)
        if not period_end:
            period_end = date.today()

        return {
            'cash_in_hand': DashboardService._get_cash_in_hand(company_id),
            'bank_balance': DashboardService._get_total_bank_balance(company_id),
            'stock_value': InventoryService.get_stock_value(company_id),
            'total_sales': DashboardService._get_total_sales(company_id, period_start, period_end),
            'total_purchases': DashboardService._get_total_purchases(company_id, period_start, period_end),
            'total_expenses': DashboardService._get_total_expenses(company_id, period_start, period_end),
            'total_receivables': DashboardService._get_total_receivables(company_id),
            'total_payables': DashboardService._get_total_payables(company_id),
            'profit': DashboardService._get_profit(company_id, period_start, period_end),
            'stock_summary': InventoryService.get_stock_summary(company_id),
            'recent_sales': DashboardService._get_recent_sales(company_id, 5),
            'recent_purchases': DashboardService._get_recent_purchases(company_id, 5),
            'low_stock_items': DashboardService._get_low_stock_items(company_id),
            'out_of_stock_items': DashboardService._get_out_of_stock_items(company_id),
            'top_selling_items': DashboardService._get_top_selling_items(company_id, period_start, period_end),
            'daily_sales': DashboardService.get_daily_sales(company_id, period_start, period_end),
        }

    @staticmethod
    def _get_cash_in_hand(company_id):
        cash = CashInHand.query.filter_by(company_id=company_id).first()
        return float(cash.current_balance) if cash else 0

    @staticmethod
    def _get_total_bank_balance(company_id):
        result = db.session.query(
            func.coalesce(func.sum(BankAccount.current_balance), 0)
        ).filter_by(company_id=company_id, is_active=True).scalar()
        return float(result)

    @staticmethod
    def _get_total_sales(company_id, start, end):
        result = db.session.query(
            func.coalesce(func.sum(SaleInvoice.grand_total), 0)
        ).filter(
            SaleInvoice.company_id == company_id,
            SaleInvoice.is_cancelled == False,
            SaleInvoice.invoice_date >= start,
            SaleInvoice.invoice_date <= end,
        ).scalar()
        return float(result)

    @staticmethod
    def _get_total_purchases(company_id, start, end):
        result = db.session.query(
            func.coalesce(func.sum(PurchaseBill.grand_total), 0)
        ).filter(
            PurchaseBill.company_id == company_id,
            PurchaseBill.is_cancelled == False,
            PurchaseBill.bill_date >= start,
            PurchaseBill.bill_date <= end,
        ).scalar()
        return float(result)

    @staticmethod
    def _get_total_expenses(company_id, start, end):
        result = db.session.query(
            func.coalesce(func.sum(Expense.amount), 0)
        ).filter(
            Expense.company_id == company_id,
            Expense.expense_date >= start,
            Expense.expense_date <= end,
        ).scalar()
        return float(result)

    @staticmethod
    def _get_total_receivables(company_id):
        result = db.session.query(
            func.coalesce(func.sum(SaleInvoice.balance_due), 0)
        ).filter(
            SaleInvoice.company_id == company_id,
            SaleInvoice.is_cancelled == False,
            SaleInvoice.balance_due > 0,
        ).scalar()
        return float(result)

    @staticmethod
    def _get_total_payables(company_id):
        result = db.session.query(
            func.coalesce(func.sum(PurchaseBill.balance_due), 0)
        ).filter(
            PurchaseBill.company_id == company_id,
            PurchaseBill.is_cancelled == False,
            PurchaseBill.balance_due > 0,
        ).scalar()
        return float(result)

    @staticmethod
    def _get_profit(company_id, start, end):
        sales = DashboardService._get_total_sales(company_id, start, end)
        purchases = DashboardService._get_total_purchases(company_id, start, end)
        expenses = DashboardService._get_total_expenses(company_id, start, end)

        other_income = db.session.query(
            func.coalesce(func.sum(OtherIncome.amount), 0)
        ).filter(
            OtherIncome.company_id == company_id,
            OtherIncome.income_date >= start,
            OtherIncome.income_date <= end,
        ).scalar()

        return round(sales + float(other_income) - purchases - expenses, 2)

    @staticmethod
    def _get_recent_sales(company_id, limit=5):
        invoices = SaleInvoice.query.filter_by(
            company_id=company_id, is_cancelled=False
        ).order_by(SaleInvoice.invoice_date.desc()).limit(limit).all()
        return [inv.to_dict() for inv in invoices]

    @staticmethod
    def _get_recent_purchases(company_id, limit=5):
        bills = PurchaseBill.query.filter_by(
            company_id=company_id, is_cancelled=False
        ).order_by(PurchaseBill.bill_date.desc()).limit(limit).all()
        return [bill.to_dict() for bill in bills]

    @staticmethod
    def _get_low_stock_items(company_id, limit=10):
        """Get items that are low on stock (current_stock <= min_stock_alert and > 0)."""
        items = Item.query.filter(
            Item.company_id == company_id,
            Item.is_active == True,
            Item.current_stock > 0,
            Item.current_stock <= Item.min_stock_alert,
        ).order_by(Item.current_stock.asc()).limit(limit).all()
        return [{
            'id': i.id, 'item_name': i.item_name, 'item_code': i.item_code,
            'current_stock': float(i.current_stock or 0),
            'min_stock_alert': float(i.min_stock_alert or 0),
            'unit': i.unit,
        } for i in items]

    @staticmethod
    def _get_out_of_stock_items(company_id, limit=10):
        """Get items that are completely out of stock."""
        items = Item.query.filter(
            Item.company_id == company_id,
            Item.is_active == True,
            Item.current_stock <= 0,
        ).order_by(Item.item_name).limit(limit).all()
        return [{
            'id': i.id, 'item_name': i.item_name, 'item_code': i.item_code,
            'unit': i.unit,
        } for i in items]

    @staticmethod
    def _get_top_selling_items(company_id, start, end, limit=5):
        """Get top selling items by quantity in the period."""
        results = db.session.query(
            SaleInvoiceItem.item_name,
            func.sum(SaleInvoiceItem.quantity).label('total_qty'),
            func.sum(SaleInvoiceItem.total_amount).label('total_amount'),
        ).join(
            SaleInvoice, SaleInvoice.id == SaleInvoiceItem.invoice_id
        ).filter(
            SaleInvoice.company_id == company_id,
            SaleInvoice.is_cancelled == False,
            SaleInvoice.invoice_date >= start,
            SaleInvoice.invoice_date <= end,
        ).group_by(
            SaleInvoiceItem.item_name
        ).order_by(
            func.sum(SaleInvoiceItem.total_amount).desc()
        ).limit(limit).all()

        return [{
            'item_name': r[0],
            'total_qty': float(r[1]),
            'total_amount': float(r[2]),
        } for r in results]

    @staticmethod
    def get_daily_sales(company_id, start, end):
        """Get day-wise sales totals for chart data."""
        results = db.session.query(
            SaleInvoice.invoice_date,
            func.coalesce(func.sum(SaleInvoice.grand_total), 0)
        ).filter(
            SaleInvoice.company_id == company_id,
            SaleInvoice.is_cancelled == False,
            SaleInvoice.invoice_date >= start,
            SaleInvoice.invoice_date <= end,
        ).group_by(SaleInvoice.invoice_date).order_by(SaleInvoice.invoice_date).all()

        return [{'date': r[0].isoformat(), 'amount': float(r[1])} for r in results]

    @staticmethod
    def get_monthly_sales(company_id, year):
        """Get month-wise sales for a year."""
        results = db.session.query(
            extract('month', SaleInvoice.invoice_date).label('month'),
            func.coalesce(func.sum(SaleInvoice.grand_total), 0)
        ).filter(
            SaleInvoice.company_id == company_id,
            SaleInvoice.is_cancelled == False,
            extract('year', SaleInvoice.invoice_date) == year,
        ).group_by('month').order_by('month').all()

        return [{'month': int(r[0]), 'amount': float(r[1])} for r in results]

    @staticmethod
    def get_analytics_data(company_id, year=None):
        """Get comprehensive analytics data for the graphical dashboard."""
        from datetime import date as dt_date
        if not year:
            year = dt_date.today().year

        today = dt_date.today()
        month_start = today.replace(day=1)

        # Monthly sales & purchases (all 12 months)
        monthly_sales = db.session.query(
            extract('month', SaleInvoice.invoice_date).label('month'),
            func.coalesce(func.sum(SaleInvoice.grand_total), 0)
        ).filter(
            SaleInvoice.company_id == company_id,
            SaleInvoice.is_cancelled == False,
            extract('year', SaleInvoice.invoice_date) == year,
        ).group_by('month').all()

        monthly_purchases = db.session.query(
            extract('month', PurchaseBill.bill_date).label('month'),
            func.coalesce(func.sum(PurchaseBill.grand_total), 0)
        ).filter(
            PurchaseBill.company_id == company_id,
            PurchaseBill.is_cancelled == False,
            extract('year', PurchaseBill.bill_date) == year,
        ).group_by('month').all()

        monthly_expenses = db.session.query(
            extract('month', Expense.expense_date).label('month'),
            func.coalesce(func.sum(Expense.amount), 0)
        ).filter(
            Expense.company_id == company_id,
            extract('year', Expense.expense_date) == year,
        ).group_by('month').all()

        # Build monthly arrays (12 months)
        month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        sales_by_month = [0]*12
        purchases_by_month = [0]*12
        expenses_by_month = [0]*12

        for r in monthly_sales:
            sales_by_month[int(r[0])-1] = float(r[1])
        for r in monthly_purchases:
            purchases_by_month[int(r[0])-1] = float(r[1])
        for r in monthly_expenses:
            expenses_by_month[int(r[0])-1] = float(r[1])

        profit_by_month = [round(s - p - e, 2) for s, p, e in zip(sales_by_month, purchases_by_month, expenses_by_month)]

        # Expense breakdown by category
        expense_cats = db.session.query(
            ExpenseCategory.name,
            func.coalesce(func.sum(Expense.amount), 0)
        ).join(ExpenseCategory, Expense.category_id == ExpenseCategory.id).filter(
            Expense.company_id == company_id,
            extract('year', Expense.expense_date) == year,
        ).group_by(ExpenseCategory.name).order_by(func.sum(Expense.amount).desc()).all()

        # Invoice status distribution
        status_dist = db.session.query(
            SaleInvoice.status,
            func.count(SaleInvoice.id),
            func.coalesce(func.sum(SaleInvoice.grand_total), 0)
        ).filter(
            SaleInvoice.company_id == company_id,
            SaleInvoice.is_cancelled == False,
        ).group_by(SaleInvoice.status).all()

        # Payment mode distribution
        payment_modes = db.session.query(
            PaymentIn.payment_mode,
            func.coalesce(func.sum(PaymentIn.amount_received), 0)
        ).filter(
            PaymentIn.company_id == company_id,
        ).group_by(PaymentIn.payment_mode).all()

        # Top 10 customers by revenue
        top_customers = db.session.query(
            Party.name,
            func.coalesce(func.sum(SaleInvoice.grand_total), 0)
        ).join(SaleInvoice, SaleInvoice.party_id == Party.id).filter(
            SaleInvoice.company_id == company_id,
            SaleInvoice.is_cancelled == False,
        ).group_by(Party.name).order_by(func.sum(SaleInvoice.grand_total).desc()).limit(10).all()

        # Top 10 items by revenue
        top_items = db.session.query(
            SaleInvoiceItem.item_name,
            func.sum(SaleInvoiceItem.quantity).label('qty'),
            func.sum(SaleInvoiceItem.total_amount).label('amount'),
        ).join(SaleInvoice, SaleInvoice.id == SaleInvoiceItem.invoice_id).filter(
            SaleInvoice.company_id == company_id,
            SaleInvoice.is_cancelled == False,
        ).group_by(SaleInvoiceItem.item_name).order_by(
            func.sum(SaleInvoiceItem.total_amount).desc()
        ).limit(10).all()

        # Stock category distribution
        stock_cats = db.session.query(
            func.coalesce(ItemCategory.name, 'Uncategorized'),
            func.sum(Item.current_stock * Item.purchase_price),
        ).outerjoin(ItemCategory, Item.category_id == ItemCategory.id).filter(
            Item.company_id == company_id,
            Item.is_active == True,
        ).group_by(ItemCategory.name).all()

        # Receivables aging
        from sqlalchemy import and_
        overdue_count = SaleInvoice.query.filter(
            SaleInvoice.company_id == company_id,
            SaleInvoice.is_cancelled == False,
            SaleInvoice.balance_due > 0,
            SaleInvoice.due_date < today,
        ).count()

        current_count = SaleInvoice.query.filter(
            SaleInvoice.company_id == company_id,
            SaleInvoice.is_cancelled == False,
            SaleInvoice.balance_due > 0,
            SaleInvoice.due_date >= today,
        ).count()

        return {
            'year': year,
            'month_names': month_names,
            'sales_by_month': sales_by_month,
            'purchases_by_month': purchases_by_month,
            'expenses_by_month': expenses_by_month,
            'profit_by_month': profit_by_month,
            'expense_categories': [{'name': r[0], 'amount': float(r[1])} for r in expense_cats],
            'status_distribution': [{'status': r[0], 'count': r[1], 'amount': float(r[2])} for r in status_dist],
            'payment_modes': [{'mode': r[0], 'amount': float(r[1])} for r in payment_modes],
            'top_customers': [{'name': r[0], 'amount': float(r[1])} for r in top_customers],
            'top_items': [{'name': r[0], 'qty': float(r[1]), 'amount': float(r[2])} for r in top_items],
            'stock_categories': [{'name': r[0] or 'Uncategorized', 'value': float(r[1] or 0)} for r in stock_cats],
            'overdue_invoices': overdue_count,
            'current_invoices': current_count,
            'total_sales_year': sum(sales_by_month),
            'total_purchases_year': sum(purchases_by_month),
            'total_expenses_year': sum(expenses_by_month),
            'total_profit_year': sum(profit_by_month),
        }


class ReportService:
    """Report generation for all report types."""

    @staticmethod
    def profit_and_loss(company_id, start, end):
        """Generate Profit & Loss statement."""
        sales = DashboardService._get_total_sales(company_id, start, end)
        purchases = DashboardService._get_total_purchases(company_id, start, end)
        expenses = DashboardService._get_total_expenses(company_id, start, end)

        other_income = float(db.session.query(
            func.coalesce(func.sum(OtherIncome.amount), 0)
        ).filter(
            OtherIncome.company_id == company_id,
            OtherIncome.income_date >= start,
            OtherIncome.income_date <= end,
        ).scalar())

        # Expense breakdown by category
        expense_breakdown = db.session.query(
            Expense.category_id,
            func.coalesce(func.sum(Expense.amount), 0)
        ).filter(
            Expense.company_id == company_id,
            Expense.expense_date >= start,
            Expense.expense_date <= end,
        ).group_by(Expense.category_id).all()

        gross_profit = sales - purchases
        net_profit = gross_profit + other_income - expenses

        return {
            'period_start': start.isoformat(),
            'period_end': end.isoformat(),
            'total_sales': sales,
            'total_purchases': purchases,
            'gross_profit': round(gross_profit, 2),
            'other_income': other_income,
            'total_expenses': expenses,
            'net_profit': round(net_profit, 2),
            'expense_breakdown': [
                {'category_id': e[0], 'amount': float(e[1])} for e in expense_breakdown
            ],
        }

    @staticmethod
    def party_statement(company_id, party_id, start=None, end=None):
        """Generate statement for a party showing all transactions."""
        transactions = []

        # Sales
        sales_query = SaleInvoice.query.filter_by(
            company_id=company_id, party_id=party_id, is_cancelled=False)
        if start:
            sales_query = sales_query.filter(SaleInvoice.invoice_date >= start)
        if end:
            sales_query = sales_query.filter(SaleInvoice.invoice_date <= end)

        for inv in sales_query.all():
            transactions.append({
                'date': inv.invoice_date,
                'type': 'Sale Invoice',
                'ref_number': inv.invoice_number,
                'debit': float(inv.grand_total),
                'credit': 0,
            })

        # Payments In
        payments_query = PaymentIn.query.filter_by(
            company_id=company_id, party_id=party_id)
        if start:
            payments_query = payments_query.filter(PaymentIn.payment_date >= start)
        if end:
            payments_query = payments_query.filter(PaymentIn.payment_date <= end)

        for pay in payments_query.all():
            transactions.append({
                'date': pay.payment_date,
                'type': 'Payment Received',
                'ref_number': pay.payment_number,
                'debit': 0,
                'credit': float(pay.amount_received),
            })

        # Purchases
        purchases_query = PurchaseBill.query.filter_by(
            company_id=company_id, supplier_id=party_id, is_cancelled=False)
        if start:
            purchases_query = purchases_query.filter(PurchaseBill.bill_date >= start)
        if end:
            purchases_query = purchases_query.filter(PurchaseBill.bill_date <= end)

        for bill in purchases_query.all():
            transactions.append({
                'date': bill.bill_date,
                'type': 'Purchase Bill',
                'ref_number': bill.bill_number,
                'debit': 0,
                'credit': float(bill.grand_total),
            })

        # Payments Out
        payments_out_query = PaymentOut.query.filter_by(
            company_id=company_id, supplier_id=party_id)
        if start:
            payments_out_query = payments_out_query.filter(PaymentOut.payment_date >= start)
        if end:
            payments_out_query = payments_out_query.filter(PaymentOut.payment_date <= end)

        for pay in payments_out_query.all():
            transactions.append({
                'date': pay.payment_date,
                'type': 'Payment Made',
                'ref_number': pay.payment_number,
                'debit': float(pay.amount_paid),
                'credit': 0,
            })

        # Sort by date
        transactions.sort(key=lambda x: (x['date'] or date.min, x['type']))

        # Calculate running balance
        running = 0
        for t in transactions:
            running += t['debit'] - t['credit']
            t['running_balance'] = round(running, 2)

        party = Party.query.get(party_id)
        return {
            'party': party.to_dict() if party else {},
            'transactions': transactions,
            'total_debit': sum(t['debit'] for t in transactions),
            'total_credit': sum(t['credit'] for t in transactions),
            'closing_balance': running,
            'total_receivable': sum(t['debit'] for t in transactions if t['type'] == 'Sale Invoice'),
            'total_payable': sum(t['credit'] for t in transactions if t['type'] == 'Purchase Bill'),
        }

    @staticmethod
    def gstr1_summary(company_id, start, end):
        """Generate GSTR-1 summary (outward supplies)."""
        invoices = SaleInvoice.query.filter(
            SaleInvoice.company_id == company_id,
            SaleInvoice.is_cancelled == False,
            SaleInvoice.invoice_date >= start,
            SaleInvoice.invoice_date <= end,
        ).all()

        b2b = []  # Business to Business (with GSTIN)
        b2c = []  # Business to Consumer (without GSTIN)

        for inv in invoices:
            party = inv.party
            entry = {
                'invoice_number': inv.invoice_number,
                'invoice_date': inv.invoice_date.isoformat(),
                'party_name': party.name if party else '',
                'gstin': party.gstin if party else '',
                'taxable_amount': float(inv.subtotal - inv.discount_total),
                'tax_amount': float(inv.tax_total),
                'total': float(inv.grand_total),
            }
            if party and party.gstin:
                b2b.append(entry)
            else:
                b2c.append(entry)

        return {
            'period_start': start.isoformat(),
            'period_end': end.isoformat(),
            'b2b': b2b,
            'b2c': b2c,
            'total_taxable': sum(e['taxable_amount'] for e in b2b + b2c),
            'total_tax': sum(e['tax_amount'] for e in b2b + b2c),
            'total_invoices': len(invoices),
        }

    @staticmethod
    def sales_report(company_id, start, end, party_id=None):
        """Detailed sales report."""
        query = SaleInvoice.query.filter(
            SaleInvoice.company_id == company_id,
            SaleInvoice.is_cancelled == False,
            SaleInvoice.invoice_date >= start,
            SaleInvoice.invoice_date <= end,
        )
        if party_id:
            query = query.filter_by(party_id=party_id)

        invoices = query.order_by(SaleInvoice.invoice_date.desc()).all()

        return {
            'invoices': [inv.to_dict() for inv in invoices],
            'total_amount': sum(float(inv.grand_total) for inv in invoices),
            'total_tax': sum(float(inv.tax_total) for inv in invoices),
            'total_received': sum(float(inv.amount_received) for inv in invoices),
            'total_outstanding': sum(float(inv.balance_due) for inv in invoices),
            'count': len(invoices),
        }

    @staticmethod
    def purchase_report(company_id, start, end, supplier_id=None):
        """Detailed purchase report."""
        query = PurchaseBill.query.filter(
            PurchaseBill.company_id == company_id,
            PurchaseBill.is_cancelled == False,
            PurchaseBill.bill_date >= start,
            PurchaseBill.bill_date <= end,
        )
        if supplier_id:
            query = query.filter_by(supplier_id=supplier_id)

        bills = query.order_by(PurchaseBill.bill_date.desc()).all()

        return {
            'bills': [bill.to_dict() for bill in bills],
            'total_amount': sum(float(bill.grand_total) for bill in bills),
            'total_tax': sum(float(bill.tax_total) for bill in bills),
            'total_paid': sum(float(bill.amount_paid) for bill in bills),
            'total_outstanding': sum(float(bill.balance_due) for bill in bills),
            'count': len(bills),
        }

    @staticmethod
    def day_book(company_id, target_date):
        """Generate Day Book - all transactions for a given date."""
        transactions = []

        # Sales
        sales = SaleInvoice.query.filter(
            SaleInvoice.company_id == company_id,
            SaleInvoice.is_cancelled == False,
            SaleInvoice.invoice_date == target_date,
        ).order_by(SaleInvoice.invoice_number).all()

        for inv in sales:
            transactions.append({
                'type': 'Sale',
                'icon': 'bi-receipt-cutoff',
                'color': 'primary',
                'number': inv.invoice_number,
                'party': inv.party.name if inv.party else '',
                'amount': float(inv.grand_total),
                'tax': float(inv.tax_total),
                'payment_mode': inv.payment_type,
                'status': inv.status,
                'url': f'/sales/{inv.id}',
            })

        # Purchases
        purchases = PurchaseBill.query.filter(
            PurchaseBill.company_id == company_id,
            PurchaseBill.is_cancelled == False,
            PurchaseBill.bill_date == target_date,
        ).order_by(PurchaseBill.bill_number).all()

        for bill in purchases:
            transactions.append({
                'type': 'Purchase',
                'icon': 'bi-cart3',
                'color': 'danger',
                'number': bill.bill_number,
                'party': bill.supplier.name if bill.supplier else '',
                'amount': float(bill.grand_total),
                'tax': float(bill.tax_total),
                'payment_mode': 'credit',
                'status': bill.payment_status,
                'url': f'/purchases/{bill.id}',
            })

        # Payments In
        payments_in = PaymentIn.query.filter(
            PaymentIn.company_id == company_id,
            PaymentIn.payment_date == target_date,
        ).all()

        for pay in payments_in:
            transactions.append({
                'type': 'Payment In',
                'icon': 'bi-arrow-down-circle',
                'color': 'success',
                'number': pay.payment_number,
                'party': pay.party.name if pay.party else '',
                'amount': float(pay.amount_received),
                'tax': 0,
                'payment_mode': pay.payment_mode,
                'status': 'received',
                'url': f'/sales/{pay.reference_invoice_id}' if pay.reference_invoice_id else '#',
            })

        # Payments Out
        from app.models.payment import PaymentOut
        payments_out = PaymentOut.query.filter(
            PaymentOut.company_id == company_id,
            PaymentOut.payment_date == target_date,
        ).all()

        for pay in payments_out:
            transactions.append({
                'type': 'Payment Out',
                'icon': 'bi-arrow-up-circle',
                'color': 'warning',
                'number': pay.payment_number,
                'party': pay.supplier.name if pay.supplier else '',
                'amount': float(pay.amount_paid),
                'tax': 0,
                'payment_mode': pay.payment_mode,
                'status': 'paid',
                'url': f'/purchases/{pay.reference_bill_id}' if pay.reference_bill_id else '#',
            })

        # Expenses
        expenses = Expense.query.filter(
            Expense.company_id == company_id,
            Expense.expense_date == target_date,
        ).all()

        for exp in expenses:
            transactions.append({
                'type': 'Expense',
                'icon': 'bi-cash',
                'color': 'secondary',
                'number': f'EXP-{exp.id}',
                'party': exp.category.name if exp.category else 'Uncategorized',
                'amount': float(exp.amount),
                'tax': float(exp.tax_amount or 0),
                'payment_mode': exp.payment_mode,
                'status': 'recorded',
                'url': f'/expenses/{exp.id}',
            })

        # Other Income
        incomes = OtherIncome.query.filter(
            OtherIncome.company_id == company_id,
            OtherIncome.income_date == target_date,
        ).all()

        for inc in incomes:
            transactions.append({
                'type': 'Income',
                'icon': 'bi-cash-coin',
                'color': 'success',
                'number': f'INC-{inc.id}',
                'party': inc.category.name if inc.category else 'Uncategorized',
                'amount': float(inc.amount),
                'tax': 0,
                'payment_mode': inc.payment_mode,
                'status': 'recorded',
                'url': f'/income/{inc.id}',
            })

        total_inflow = sum(t['amount'] for t in transactions if t['type'] in ('Sale', 'Payment In', 'Income'))
        total_outflow = sum(t['amount'] for t in transactions if t['type'] in ('Purchase', 'Payment Out', 'Expense'))

        return {
            'date': target_date.isoformat(),
            'transactions': transactions,
            'total_transactions': len(transactions),
            'total_inflow': round(total_inflow, 2),
            'total_outflow': round(total_outflow, 2),
            'net_flow': round(total_inflow - total_outflow, 2),
            'total_sales': sum(t['amount'] for t in transactions if t['type'] == 'Sale'),
            'total_purchases': sum(t['amount'] for t in transactions if t['type'] == 'Purchase'),
            'total_expenses': sum(t['amount'] for t in transactions if t['type'] == 'Expense'),
            'total_income': sum(t['amount'] for t in transactions if t['type'] == 'Income'),
            'total_payments_in': sum(t['amount'] for t in transactions if t['type'] == 'Payment In'),
            'total_payments_out': sum(t['amount'] for t in transactions if t['type'] == 'Payment Out'),
        }
