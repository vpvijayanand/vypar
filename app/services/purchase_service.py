"""
Purchase Service - Purchase bill business logic.
"""
from datetime import date
from decimal import Decimal
from app.extensions import db
from app.models.purchase import PurchaseBill, PurchaseBillItem
from app.models.party import Party
from app.models.settings import InvoiceSettings
from app.services.gst_service import GSTCalculator
from app.services.inventory_service import InventoryService


class PurchaseService:
    """Business logic for purchase bills."""

    @staticmethod
    def generate_bill_number(company_id):
        """Generate next purchase bill number."""
        settings = InvoiceSettings.query.filter_by(company_id=company_id).first()
        if not settings:
            settings = InvoiceSettings(company_id=company_id)
            db.session.add(settings)
            db.session.flush()

        prefix = settings.purchase_prefix or 'PUR-'
        number = settings.next_purchase_number or 1
        bill_number = f"{prefix}{number:05d}"
        settings.next_purchase_number = number + 1
        return bill_number

    @staticmethod
    def create_purchase(company_id, data, user_id=None):
        """
        Create a purchase bill with items, GST, and stock update.
        """
        from app.services.invoice_service import InvoiceService
        inter_state = InvoiceService.is_inter_state(company_id, data['supplier_id'])

        calculated_items = []
        for item_data in data.get('items', []):
            calc = GSTCalculator.calculate_line_item(
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                discount_percent=item_data.get('discount_percent', 0),
                discount_amount=item_data.get('discount_amount', 0),
                gst_rate=item_data.get('gst_rate', 0),
                cess_rate=item_data.get('cess_rate', 0),
                is_inter_state=inter_state,
            )
            calc['item_data'] = item_data
            calculated_items.append(calc)

        totals = GSTCalculator.calculate_invoice_totals(calculated_items)
        bill_number = data.get('bill_number') or PurchaseService.generate_bill_number(company_id)

        bill = PurchaseBill(
            company_id=company_id,
            bill_number=bill_number,
            bill_date=data.get('bill_date', date.today()),
            due_date=data.get('due_date'),
            supplier_id=data['supplier_id'],
            subtotal=Decimal(str(totals['subtotal'])),
            discount_total=Decimal(str(totals['discount_total'])),
            tax_total=Decimal(str(totals['tax_total'])),
            round_off=Decimal(str(totals['round_off'])),
            grand_total=Decimal(str(totals['grand_total'])),
            amount_paid=Decimal(str(data.get('amount_paid', 0))),
            notes=data.get('notes', ''),
            created_by=user_id,
        )

        bill.balance_due = bill.grand_total - bill.amount_paid
        if bill.balance_due <= 0:
            bill.payment_status = 'paid'
        elif bill.amount_paid > 0:
            bill.payment_status = 'partial'
        else:
            bill.payment_status = 'unpaid'

        db.session.add(bill)
        db.session.flush()

        stock_items = []
        for calc in calculated_items:
            item_data = calc['item_data']
            bill_item = PurchaseBillItem(
                bill_id=bill.id,
                item_id=item_data['item_id'],
                item_name=item_data.get('item_name', ''),
                hsn_code=item_data.get('hsn_code', ''),
                quantity=Decimal(str(item_data['quantity'])),
                unit=item_data.get('unit', 'pcs'),
                unit_price=Decimal(str(item_data['unit_price'])),
                discount_percent=Decimal(str(item_data.get('discount_percent', 0))),
                discount_amount=Decimal(str(calc['discount'])),
                gst_rate=Decimal(str(item_data.get('gst_rate', 0))),
                cgst_amount=Decimal(str(calc['cgst_amount'])),
                sgst_amount=Decimal(str(calc['sgst_amount'])),
                igst_amount=Decimal(str(calc['igst_amount'])),
                cess_amount=Decimal(str(calc['cess_amount'])),
                tax_amount=Decimal(str(calc['tax_amount'])),
                total_amount=Decimal(str(calc['total_amount'])),
            )
            db.session.add(bill_item)
            stock_items.append({
                'item_id': item_data['item_id'],
                'quantity': item_data['quantity'],
                'unit_price': item_data['unit_price'],
                'bill_id': bill.id,
            })

        # Update stock (purchase increases stock)
        InventoryService.process_purchase_stock(company_id, stock_items, user_id)

        # Update party balance
        supplier = Party.query.get(data['supplier_id'])
        if supplier:
            supplier.current_balance = Decimal(str(float(supplier.current_balance or 0))) + bill.balance_due

        db.session.commit()
        return bill

    @staticmethod
    def list_purchases(company_id, page=1, per_page=20, status=None,
                       supplier_id=None, date_from=None, date_to=None):
        """List purchase bills with filtering and pagination."""
        query = PurchaseBill.query.filter_by(company_id=company_id, is_cancelled=False)

        if status:
            query = query.filter_by(payment_status=status)
        if supplier_id:
            query = query.filter_by(supplier_id=supplier_id)
        if date_from:
            query = query.filter(PurchaseBill.bill_date >= date_from)
        if date_to:
            query = query.filter(PurchaseBill.bill_date <= date_to)

        query = query.order_by(PurchaseBill.bill_date.desc(), PurchaseBill.id.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def record_payment(bill_id, company_id, amount):
        """Record a payment against a purchase bill."""
        bill = PurchaseBill.query.filter_by(
            id=bill_id, company_id=company_id, is_cancelled=False
        ).first()
        if not bill:
            raise ValueError("Purchase bill not found")

        bill.amount_paid = Decimal(str(float(bill.amount_paid or 0))) + Decimal(str(amount))
        bill.balance_due = bill.grand_total - bill.amount_paid

        if bill.balance_due <= 0:
            bill.payment_status = 'paid'
            bill.balance_due = Decimal('0')
        else:
            bill.payment_status = 'partial'

        db.session.commit()
        return bill
