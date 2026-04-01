"""
GST Calculation Engine - Core business logic for tax computation.
Handles CGST, SGST, IGST, cess calculations based on Indian GST rules.
"""
from decimal import Decimal, ROUND_HALF_UP


class GSTCalculator:
    """GST calculation engine following Indian GST rules."""

    VALID_GST_RATES = [Decimal('0'), Decimal('0.25'), Decimal('3'), Decimal('5'),
                       Decimal('12'), Decimal('18'), Decimal('28')]

    @staticmethod
    def calculate_line_item(quantity, unit_price, discount_percent=0, discount_amount=0,
                            gst_rate=0, cess_rate=0, is_inter_state=False):
        """
        Calculate tax and total for a single line item.

        Returns dict with all calculated values:
        - taxable_amount: amount after discount
        - cgst_amount, sgst_amount: for intra-state
        - igst_amount: for inter-state
        - cess_amount
        - tax_amount: total tax
        - total_amount: taxable + tax
        """
        qty = Decimal(str(quantity))
        price = Decimal(str(unit_price))
        gst = Decimal(str(gst_rate))
        cess = Decimal(str(cess_rate))
        disc_pct = Decimal(str(discount_percent))
        disc_amt = Decimal(str(discount_amount))

        # Calculate base amount
        base_amount = (qty * price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Calculate discount
        if disc_pct > 0:
            discount = (base_amount * disc_pct / Decimal('100')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            discount = disc_amt

        taxable_amount = (base_amount - discount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Calculate GST
        cgst_amount = Decimal('0')
        sgst_amount = Decimal('0')
        igst_amount = Decimal('0')

        if is_inter_state:
            # Inter-state: IGST = full GST rate
            igst_amount = (taxable_amount * gst / Decimal('100')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            # Intra-state: CGST + SGST = GST rate / 2 each
            half_rate = gst / Decimal('2')
            cgst_amount = (taxable_amount * half_rate / Decimal('100')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)
            sgst_amount = (taxable_amount * half_rate / Decimal('100')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Calculate cess
        cess_amount = (taxable_amount * cess / Decimal('100')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP)

        tax_amount = cgst_amount + sgst_amount + igst_amount + cess_amount
        total_amount = taxable_amount + tax_amount

        return {
            'base_amount': float(base_amount),
            'discount': float(discount),
            'taxable_amount': float(taxable_amount),
            'cgst_amount': float(cgst_amount),
            'sgst_amount': float(sgst_amount),
            'igst_amount': float(igst_amount),
            'cess_amount': float(cess_amount),
            'tax_amount': float(tax_amount),
            'total_amount': float(total_amount),
        }

    @staticmethod
    def calculate_invoice_totals(line_items, round_off_enabled=True):
        """
        Calculate invoice-level totals from a list of line item results.

        Args:
            line_items: list of dicts from calculate_line_item
            round_off_enabled: whether to round off grand total

        Returns dict with subtotal, discount_total, tax_total, round_off, grand_total
        """
        subtotal = sum(item['base_amount'] for item in line_items)
        discount_total = sum(item['discount'] for item in line_items)
        tax_total = sum(item['tax_amount'] for item in line_items)
        taxable_total = sum(item['taxable_amount'] for item in line_items)

        pre_round_total = taxable_total + tax_total

        if round_off_enabled:
            rounded_total = round(pre_round_total)
            round_off = round(rounded_total - pre_round_total, 2)
            grand_total = rounded_total
        else:
            round_off = 0
            grand_total = round(pre_round_total, 2)

        return {
            'subtotal': round(subtotal, 2),
            'discount_total': round(discount_total, 2),
            'taxable_total': round(taxable_total, 2),
            'tax_total': round(tax_total, 2),
            'round_off': round_off,
            'grand_total': grand_total,
        }

    @staticmethod
    def get_hsn_summary(line_items_with_hsn):
        """
        Generate HSN-wise tax summary for GST returns.

        Args:
            line_items_with_hsn: list of dicts with hsn_code, taxable_amount, gst_rate,
                                 cgst_amount, sgst_amount, igst_amount, cess_amount

        Returns list of HSN summary dicts grouped by HSN code and GST rate.
        """
        summary = {}
        for item in line_items_with_hsn:
            key = (item.get('hsn_code', ''), item.get('gst_rate', 0))
            if key not in summary:
                summary[key] = {
                    'hsn_code': item.get('hsn_code', ''),
                    'gst_rate': item.get('gst_rate', 0),
                    'taxable_amount': 0,
                    'cgst_amount': 0,
                    'sgst_amount': 0,
                    'igst_amount': 0,
                    'cess_amount': 0,
                    'total_tax': 0,
                    'quantity': 0,
                }
            summary[key]['taxable_amount'] += item.get('taxable_amount', 0)
            summary[key]['cgst_amount'] += item.get('cgst_amount', 0)
            summary[key]['sgst_amount'] += item.get('sgst_amount', 0)
            summary[key]['igst_amount'] += item.get('igst_amount', 0)
            summary[key]['cess_amount'] += item.get('cess_amount', 0)
            summary[key]['total_tax'] += item.get('tax_amount', 0)
            summary[key]['quantity'] += item.get('quantity', 0)

        return list(summary.values())
