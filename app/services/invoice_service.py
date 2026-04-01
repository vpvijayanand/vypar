"""
Invoice Service - Sales invoice business logic.
Handles invoice creation, GST calculation, payment tracking, and number generation.
"""
from datetime import date
from decimal import Decimal
from app.extensions import db
from app.models.invoice import SaleInvoice, SaleInvoiceItem
from app.models.party import Party
from app.models.settings import InvoiceSettings, GSTSettings
from app.services.gst_service import GSTCalculator
from app.services.inventory_service import InventoryService


class InvoiceService:
    """Business logic for sales invoicing."""

    @staticmethod
    def generate_invoice_number(company_id):
        """Generate next invoice number based on settings."""
        settings = InvoiceSettings.query.filter_by(company_id=company_id).first()
        if not settings:
            settings = InvoiceSettings(company_id=company_id)
            db.session.add(settings)
            db.session.flush()

        prefix = settings.invoice_prefix or 'INV-'
        number = settings.next_invoice_number or 1
        invoice_number = f"{prefix}{number:05d}"
        settings.next_invoice_number = number + 1
        return invoice_number

    @staticmethod
    def is_inter_state(company_id, party_id):
        """Determine if transaction is inter-state based on party and company state."""
        gst_settings = GSTSettings.query.filter_by(company_id=company_id).first()
        party = Party.query.get(party_id)

        if not gst_settings or not party:
            return False

        company_state = (gst_settings.company_state or '').strip().lower()
        party_state = (party.state or '').strip().lower()

        if not company_state or not party_state:
            return False

        return company_state != party_state

    @staticmethod
    def create_invoice(company_id, data, user_id=None):
        """
        Create a complete sale invoice with items, GST calculation, and stock update.

        Args:
            company_id: company context
            data: dict with invoice fields and 'items' list
            user_id: creating user

        Returns: SaleInvoice object
        """
        inter_state = InvoiceService.is_inter_state(company_id, data['party_id'])

        # Calculate line items
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

        # Calculate invoice totals
        totals = GSTCalculator.calculate_invoice_totals(calculated_items)

        # Generate invoice number
        invoice_number = data.get('invoice_number') or InvoiceService.generate_invoice_number(company_id)

        # Create invoice
        invoice = SaleInvoice(
            company_id=company_id,
            invoice_number=invoice_number,
            invoice_date=data.get('invoice_date', date.today()),
            due_date=data.get('due_date'),
            party_id=data['party_id'],
            billing_address=data.get('billing_address', ''),
            shipping_address=data.get('shipping_address', ''),
            place_of_supply=data.get('place_of_supply', ''),
            payment_type=data.get('payment_type', 'credit'),
            subtotal=Decimal(str(totals['subtotal'])),
            discount_total=Decimal(str(totals['discount_total'])),
            tax_total=Decimal(str(totals['tax_total'])),
            round_off=Decimal(str(totals['round_off'])),
            grand_total=Decimal(str(totals['grand_total'])),
            amount_received=Decimal(str(data.get('amount_received', 0))),
            notes=data.get('notes', ''),
            terms_conditions=data.get('terms_conditions', ''),
            created_by=user_id,
        )

        # Calculate balance
        invoice.balance_due = invoice.grand_total - invoice.amount_received
        if invoice.balance_due <= 0:
            invoice.status = 'paid'
        elif invoice.amount_received > 0:
            invoice.status = 'partial'
        else:
            invoice.status = 'unpaid'

        db.session.add(invoice)
        db.session.flush()  # Get invoice.id

        # Create invoice items
        stock_items = []
        for calc in calculated_items:
            item_data = calc['item_data']
            inv_item = SaleInvoiceItem(
                invoice_id=invoice.id,
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
            db.session.add(inv_item)
            stock_items.append({
                'item_id': item_data['item_id'],
                'quantity': item_data['quantity'],
                'unit_price': item_data['unit_price'],
                'invoice_id': invoice.id,
            })

        # Update stock
        InventoryService.process_sale_stock(company_id, stock_items, user_id)

        # Update party balance
        party = Party.query.get(data['party_id'])
        if party:
            party.current_balance = Decimal(str(float(party.current_balance or 0))) + invoice.balance_due

        db.session.commit()
        return invoice

    @staticmethod
    def get_invoice(invoice_id, company_id):
        """Get an invoice by ID with validation."""
        return SaleInvoice.query.filter_by(
            id=invoice_id, company_id=company_id, is_cancelled=False
        ).first()

    @staticmethod
    def list_invoices(company_id, page=1, per_page=20, status=None,
                      party_id=None, date_from=None, date_to=None):
        """List invoices with filtering and pagination."""
        query = SaleInvoice.query.filter_by(
            company_id=company_id, is_cancelled=False
        )

        if status:
            query = query.filter_by(status=status)
        if party_id:
            query = query.filter_by(party_id=party_id)
        if date_from:
            query = query.filter(SaleInvoice.invoice_date >= date_from)
        if date_to:
            query = query.filter(SaleInvoice.invoice_date <= date_to)

        query = query.order_by(SaleInvoice.invoice_date.desc(), SaleInvoice.id.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def record_payment(invoice_id, company_id, amount):
        """Record a payment against an invoice and update status."""
        invoice = InvoiceService.get_invoice(invoice_id, company_id)
        if not invoice:
            raise ValueError("Invoice not found")

        invoice.amount_received = Decimal(str(float(invoice.amount_received or 0))) + Decimal(str(amount))
        invoice.balance_due = invoice.grand_total - invoice.amount_received

        if invoice.balance_due <= 0:
            invoice.status = 'paid'
            invoice.balance_due = Decimal('0')
        else:
            invoice.status = 'partial'

        db.session.commit()
        return invoice
