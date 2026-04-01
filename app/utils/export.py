"""
Export Utilities - CSV downloads and PDF invoice/bill generation.
Uses only Python stdlib (csv, io) and reportlab for PDFs.
"""
import csv
import io
from datetime import date, datetime
from flask import make_response


def indian_number_format(value):
    """Format number in Indian numbering system for CSV/PDF."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return '0.00'
    is_negative = value < 0
    value = abs(value)
    integer_part = int(value)
    decimal_part = f"{value - integer_part:.2f}"[1:]
    s = str(integer_part)
    if len(s) <= 3:
        formatted = s
    else:
        last3 = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted = ','.join(groups) + ',' + last3
    result = formatted + decimal_part
    return f"-{result}" if is_negative else result


# ═════════════════════════════════════════════════════════════════════════════
#  CSV EXPORTS
# ═════════════════════════════════════════════════════════════════════════════

def make_csv_response(rows, headers, filename):
    """Create a CSV download response from list of dicts/tuples."""
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(headers)
    for row in rows:
        if isinstance(row, dict):
            writer.writerow([row.get(h, '') for h in headers])
        else:
            writer.writerow(row)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"
    output.headers["Content-type"] = "text/csv"
    return output


def sales_csv(invoices, filename='sales_report.csv'):
    """Generate CSV for sales invoices list."""
    headers = ['Invoice #', 'Date', 'Party', 'GSTIN', 'Subtotal', 'Discount',
               'Tax', 'Grand Total', 'Received', 'Balance Due', 'Status']
    rows = []
    for inv in invoices:
        if hasattr(inv, 'invoice_number'):
            rows.append([
                inv.invoice_number,
                inv.invoice_date.strftime('%d-%m-%Y') if inv.invoice_date else '',
                inv.party.name if inv.party else '',
                inv.party.gstin if inv.party and inv.party.gstin else '',
                float(inv.subtotal or 0),
                float(inv.discount_total or 0),
                float(inv.tax_total or 0),
                float(inv.grand_total or 0),
                float(inv.amount_received or 0),
                float(inv.balance_due or 0),
                inv.status,
            ])
        else:
            # dict format from report service
            rows.append([
                inv.get('invoice_number', ''),
                inv.get('invoice_date', ''),
                inv.get('party_name', ''),
                '',
                inv.get('subtotal', 0),
                inv.get('discount_total', 0),
                inv.get('tax_total', 0),
                inv.get('grand_total', 0),
                inv.get('amount_received', 0),
                inv.get('balance_due', 0),
                inv.get('status', ''),
            ])
    return make_csv_response(rows, headers, filename)


def purchases_csv(bills, filename='purchase_report.csv'):
    """Generate CSV for purchase bills list."""
    headers = ['Bill #', 'Date', 'Supplier', 'GSTIN', 'Subtotal', 'Discount',
               'Tax', 'Grand Total', 'Paid', 'Balance Due', 'Status']
    rows = []
    for bill in bills:
        if hasattr(bill, 'bill_number'):
            rows.append([
                bill.bill_number,
                bill.bill_date.strftime('%d-%m-%Y') if bill.bill_date else '',
                bill.supplier.name if bill.supplier else '',
                bill.supplier.gstin if bill.supplier and bill.supplier.gstin else '',
                float(bill.subtotal or 0),
                float(bill.discount_total or 0),
                float(bill.tax_total or 0),
                float(bill.grand_total or 0),
                float(bill.amount_paid or 0),
                float(bill.balance_due or 0),
                bill.payment_status,
            ])
        else:
            rows.append([
                bill.get('bill_number', ''),
                bill.get('bill_date', ''),
                bill.get('supplier_name', ''),
                '',
                bill.get('subtotal', 0),
                bill.get('discount_total', 0),
                bill.get('tax_total', 0),
                bill.get('grand_total', 0),
                bill.get('amount_paid', 0),
                bill.get('balance_due', 0),
                bill.get('payment_status', ''),
            ])
    return make_csv_response(rows, headers, filename)


def expenses_csv(expenses, filename='expenses_report.csv'):
    """Generate CSV for expenses."""
    headers = ['Date', 'Category', 'Amount', 'GST Rate', 'Tax Amount',
               'Payment Mode', 'Notes']
    rows = []
    for e in expenses:
        rows.append([
            e.expense_date.strftime('%d-%m-%Y') if e.expense_date else '',
            e.category.name if e.category else 'Uncategorized',
            float(e.amount or 0),
            float(e.gst_rate or 0),
            float(e.tax_amount or 0),
            e.payment_mode or '',
            e.notes or '',
        ])
    return make_csv_response(rows, headers, filename)


def parties_csv(parties, filename='parties.csv'):
    """Generate CSV for parties."""
    headers = ['Name', 'Type', 'Phone', 'Email', 'GSTIN', 'City', 'State',
               'Current Balance', 'Balance Type']
    rows = []
    for p in parties:
        rows.append([
            p.name, p.party_type, p.phone or '', p.email or '',
            p.gstin or '', p.city or '', p.state or '',
            float(p.current_balance or 0), p.balance_type or '',
        ])
    return make_csv_response(rows, headers, filename)


def items_csv(items, filename='items.csv'):
    """Generate CSV for items/inventory."""
    headers = ['Item Code', 'Item Name', 'HSN', 'Category', 'Unit',
               'Sale Price', 'Purchase Price', 'GST %', 'Current Stock', 'Stock Value']
    rows = []
    for item in items:
        rows.append([
            item.item_code or '', item.item_name, item.hsn_code or '',
            item.category.name if item.category else '',
            item.unit or 'pcs',
            float(item.sale_price or 0), float(item.purchase_price or 0),
            float(item.gst_rate or 0), float(item.current_stock or 0),
            item.stock_value,
        ])
    return make_csv_response(rows, headers, filename)


def cheques_csv(cheques, filename='cheques.csv'):
    """Generate CSV for cheques."""
    headers = ['Cheque #', 'Type', 'Party', 'Bank', 'Date', 'Amount', 'Status']
    rows = []
    for c in cheques:
        rows.append([
            c.cheque_number, c.cheque_type,
            c.party.name if c.party else '-',
            c.bank_name or '-',
            c.issue_date.strftime('%d-%m-%Y') if c.issue_date else '',
            float(c.amount or 0), c.status,
        ])
    return make_csv_response(rows, headers, filename)


def income_csv(incomes, filename='other_income.csv'):
    """Generate CSV for other income."""
    headers = ['Date', 'Category', 'Amount', 'Payment Mode', 'Reference', 'Notes']
    rows = []
    for inc in incomes:
        rows.append([
            inc.income_date.strftime('%d-%m-%Y') if inc.income_date else '',
            inc.category.name if inc.category else 'Uncategorized',
            float(inc.amount or 0),
            inc.payment_mode or '',
            inc.reference or '',
            inc.notes or '',
        ])
    return make_csv_response(rows, headers, filename)


def profit_loss_csv(data, filename='profit_loss.csv'):
    """Generate CSV for P&L statement."""
    headers = ['Particulars', 'Amount (₹)']
    rows = [
        ['INCOME', ''],
        ['Sales Revenue', data.get('total_sales', 0)],
        ['Other Income', data.get('other_income', 0)],
        ['', ''],
        ['EXPENSES', ''],
        ['Purchase Cost', data.get('total_purchases', 0)],
        ['Operating Expenses', data.get('total_expenses', 0)],
        ['', ''],
        ['Gross Profit', data.get('gross_profit', 0)],
        ['Net Profit', data.get('net_profit', 0)],
    ]
    return make_csv_response(rows, headers, filename)


def gstr1_csv(data, filename='gstr1_summary.csv'):
    """Generate CSV for GSTR-1 summary."""
    headers = ['Invoice #', 'Date', 'Party', 'GSTIN', 'Taxable Amount', 'Tax Amount', 'Total']
    rows = []
    for entry in data.get('b2b', []) + data.get('b2c', []):
        rows.append([
            entry.get('invoice_number', ''),
            entry.get('invoice_date', ''),
            entry.get('party_name', ''),
            entry.get('gstin', ''),
            entry.get('taxable_amount', 0),
            entry.get('tax_amount', 0),
            entry.get('total', 0),
        ])
    return make_csv_response(rows, headers, filename)


# ═════════════════════════════════════════════════════════════════════════════
#  PDF INVOICE / BILL GENERATION (using reportlab)
# ═════════════════════════════════════════════════════════════════════════════

def generate_invoice_pdf(invoice, company):
    """Generate a professional GST invoice PDF."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title2', parent=styles['Title'], fontSize=16,
                                  spaceAfter=2*mm, textColor=colors.HexColor('#1a237e'))
    subtitle_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=8,
                                     textColor=colors.grey)
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=9,
                                 fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('Norm', parent=styles['Normal'], fontSize=9)
    right_style = ParagraphStyle('Right', parent=styles['Normal'], fontSize=9,
                                  alignment=TA_RIGHT)
    center_style = ParagraphStyle('Center', parent=styles['Normal'], fontSize=9,
                                   alignment=TA_CENTER)
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=7,
                                  textColor=colors.grey)

    elements = []

    # ── Header ───────────────────────────────────────────────────────────────
    header_data = [
        [Paragraph(f"<b>{company.company_name}</b>", title_style),
         Paragraph("<b>TAX INVOICE</b>", ParagraphStyle('TaxInv', parent=styles['Normal'],
                    fontSize=14, alignment=TA_RIGHT, fontName='Helvetica-Bold',
                    textColor=colors.HexColor('#1a237e')))],
    ]
    header_table = Table(header_data, colWidths=[120*mm, 60*mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)

    # Company details
    company_addr = ', '.join(filter(None, [
        company.address_line1, company.address_line2, company.city,
        company.state, company.pincode
    ]))
    comp_info = f"GSTIN: {company.gstin or 'N/A'} | PAN: {company.pan_number or 'N/A'}<br/>"
    comp_info += f"{company_addr}<br/>"
    comp_info += f"Phone: {company.phone_number or ''} | Email: {company.email or ''}"
    elements.append(Paragraph(comp_info, small_style))
    elements.append(Spacer(1, 4*mm))

    # ── Invoice Info + Party ─────────────────────────────────────────────────
    party = invoice.party
    inv_date = invoice.invoice_date.strftime('%d-%m-%Y') if invoice.invoice_date else ''
    due_date = invoice.due_date.strftime('%d-%m-%Y') if invoice.due_date else 'N/A'

    info_data = [
        [Paragraph("<b>Bill To:</b>", bold_style),
         Paragraph(f"<b>Invoice #:</b> {invoice.invoice_number}", bold_style)],
        [Paragraph(f"<b>{party.name}</b>", bold_style),
         Paragraph(f"Date: {inv_date}", normal_style)],
        [Paragraph(f"GSTIN: {party.gstin or 'N/A'}", normal_style),
         Paragraph(f"Due Date: {due_date}", normal_style)],
        [Paragraph(f"{party.billing_address or ''}", normal_style),
         Paragraph(f"Payment: {invoice.payment_type.title()}", normal_style)],
        [Paragraph(f"{party.city or ''}, {party.state or ''} - {party.pincode or ''}", normal_style),
         Paragraph(f"Place of Supply: {invoice.place_of_supply or ''}", normal_style)],
    ]
    info_table = Table(info_data, colWidths=[100*mm, 80*mm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.grey),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.grey),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 4*mm))

    # ── Items Table ──────────────────────────────────────────────────────────
    item_header = ['#', 'Item', 'HSN', 'Qty', 'Rate (₹)', 'Disc%', 'GST%',
                   'CGST (₹)', 'SGST (₹)', 'Total (₹)']
    item_rows = [item_header]

    for idx, item in enumerate(invoice.items, 1):
        item_rows.append([
            str(idx),
            Paragraph(item.item_name or '', normal_style),
            item.hsn_code or '',
            f"{float(item.quantity):.0f}",
            indian_number_format(item.unit_price),
            f"{float(item.discount_percent):.0f}",
            f"{float(item.gst_rate):.0f}",
            indian_number_format(item.cgst_amount),
            indian_number_format(item.sgst_amount),
            indian_number_format(item.total_amount),
        ])

    items_table = Table(item_rows,
                         colWidths=[8*mm, 42*mm, 14*mm, 12*mm, 22*mm, 12*mm, 12*mm, 18*mm, 18*mm, 22*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 4*mm))

    # ── Totals ───────────────────────────────────────────────────────────────
    totals_data = [
        ['Subtotal', f'₹ {indian_number_format(invoice.subtotal)}'],
        ['Discount', f'- ₹ {indian_number_format(invoice.discount_total)}'],
        ['Tax (GST)', f'₹ {indian_number_format(invoice.tax_total)}'],
    ]
    if float(invoice.round_off or 0) != 0:
        totals_data.append(['Round Off', f'₹ {indian_number_format(invoice.round_off)}'])
    totals_data.append(['GRAND TOTAL', f'₹ {indian_number_format(invoice.grand_total)}'])
    totals_data.append(['Amount Received', f'₹ {indian_number_format(invoice.amount_received)}'])
    totals_data.append(['Balance Due', f'₹ {indian_number_format(invoice.balance_due)}'])

    totals_table = Table(totals_data, colWidths=[130*mm, 50*mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -3), (-1, -3), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTSIZE', (0, -3), (-1, -3), 11),
        ('LINEABOVE', (0, -3), (-1, -3), 1, colors.HexColor('#1a237e')),
        ('LINEBELOW', (0, -3), (-1, -3), 1, colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, -3), (-1, -3), colors.HexColor('#1a237e')),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 8*mm))

    # ── Footer ───────────────────────────────────────────────────────────────
    if invoice.terms_conditions:
        elements.append(Paragraph("<b>Terms & Conditions:</b>", bold_style))
        elements.append(Paragraph(invoice.terms_conditions, small_style))
        elements.append(Spacer(1, 3*mm))

    if invoice.notes:
        elements.append(Paragraph("<b>Notes:</b>", bold_style))
        elements.append(Paragraph(invoice.notes, small_style))
        elements.append(Spacer(1, 3*mm))

    # Signature area
    sig_data = [
        ['', Paragraph(f"For <b>{company.company_name}</b>", right_style)],
        ['', ''],
        ['', Paragraph("Authorised Signatory", right_style)],
    ]
    sig_table = Table(sig_data, colWidths=[120*mm, 60*mm], rowHeights=[6*mm, 15*mm, 6*mm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (1, -1), (1, -1), 0.5, colors.grey),
    ]))
    elements.append(sig_table)

    # Computer generated notice
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph("This is a computer generated invoice.", center_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_purchase_pdf(bill, company):
    """Generate a professional purchase bill PDF."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title2', parent=styles['Title'], fontSize=16,
                                  spaceAfter=2*mm, textColor=colors.HexColor('#0d47a1'))
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=9,
                                 fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('Norm', parent=styles['Normal'], fontSize=9)
    right_style = ParagraphStyle('Right', parent=styles['Normal'], fontSize=9,
                                  alignment=TA_RIGHT)
    center_style = ParagraphStyle('Center', parent=styles['Normal'], fontSize=9,
                                   alignment=TA_CENTER)
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=7,
                                  textColor=colors.grey)

    elements = []

    # Header
    header_data = [
        [Paragraph(f"<b>{company.company_name}</b>", title_style),
         Paragraph("<b>PURCHASE BILL</b>", ParagraphStyle('PurBill', parent=styles['Normal'],
                    fontSize=14, alignment=TA_RIGHT, fontName='Helvetica-Bold',
                    textColor=colors.HexColor('#0d47a1')))],
    ]
    header_table = Table(header_data, colWidths=[120*mm, 60*mm])
    header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(header_table)

    company_addr = ', '.join(filter(None, [
        company.address_line1, company.address_line2, company.city,
        company.state, company.pincode
    ]))
    elements.append(Paragraph(
        f"GSTIN: {company.gstin or 'N/A'} | {company_addr} | Phone: {company.phone_number or ''}",
        small_style))
    elements.append(Spacer(1, 4*mm))

    # Supplier + Bill Info
    supplier = bill.supplier
    bill_date = bill.bill_date.strftime('%d-%m-%Y') if bill.bill_date else ''
    due_date = bill.due_date.strftime('%d-%m-%Y') if bill.due_date else 'N/A'

    info_data = [
        [Paragraph("<b>Supplier:</b>", bold_style),
         Paragraph(f"<b>Bill #:</b> {bill.bill_number}", bold_style)],
        [Paragraph(f"<b>{supplier.name}</b>", bold_style),
         Paragraph(f"Date: {bill_date}", normal_style)],
        [Paragraph(f"GSTIN: {supplier.gstin or 'N/A'}", normal_style),
         Paragraph(f"Due Date: {due_date}", normal_style)],
        [Paragraph(f"{supplier.billing_address or ''}", normal_style),
         Paragraph(f"Status: {bill.payment_status.title()}", normal_style)],
    ]
    info_table = Table(info_data, colWidths=[100*mm, 80*mm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.grey),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.grey),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 4*mm))

    # Items
    item_header = ['#', 'Item', 'HSN', 'Qty', 'Rate (₹)', 'GST%', 'Tax (₹)', 'Total (₹)']
    item_rows = [item_header]
    for idx, item in enumerate(bill.items, 1):
        item_rows.append([
            str(idx),
            Paragraph(item.item_name or '', normal_style),
            item.hsn_code or '',
            f"{float(item.quantity):.0f}",
            indian_number_format(item.unit_price),
            f"{float(item.gst_rate):.0f}",
            indian_number_format(item.tax_amount),
            indian_number_format(item.total_amount),
        ])

    items_table = Table(item_rows,
                         colWidths=[8*mm, 55*mm, 16*mm, 14*mm, 25*mm, 14*mm, 22*mm, 26*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d47a1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 4*mm))

    # Totals
    totals_data = [
        ['Subtotal', f'₹ {indian_number_format(bill.subtotal)}'],
        ['Tax (GST)', f'₹ {indian_number_format(bill.tax_total)}'],
        ['GRAND TOTAL', f'₹ {indian_number_format(bill.grand_total)}'],
        ['Amount Paid', f'₹ {indian_number_format(bill.amount_paid)}'],
        ['Balance Due', f'₹ {indian_number_format(bill.balance_due)}'],
    ]
    totals_table = Table(totals_data, colWidths=[130*mm, 50*mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTSIZE', (0, 2), (-1, 2), 11),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.HexColor('#0d47a1')),
        ('LINEBELOW', (0, 2), (-1, 2), 1, colors.HexColor('#0d47a1')),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#0d47a1')),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("This is a computer generated document.", center_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
