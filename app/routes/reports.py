"""
Reports routes - All report types with filtering.
"""
from flask import Blueprint, render_template, request, redirect, url_for, make_response
from flask_login import login_required
from datetime import datetime, date
from app.utils.helpers import api_response, get_company_id, jwt_required
from app.services.report_service import DashboardService, ReportService
from app.models.party import Party

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports')
@login_required
def index():
    return render_template('reports/index.html')


@reports_bp.route('/analytics')
@login_required
def analytics():
    """Graphical analytics dashboard with comprehensive charts."""
    company_id = get_company_id()
    year = request.args.get('year', date.today().year, type=int)
    data = DashboardService.get_analytics_data(company_id, year)
    return render_template('reports/analytics.html', data=data, year=year)


@reports_bp.route('/reports/sales')
@login_required
def sales_report():
    company_id = get_company_id()
    from_date = request.args.get('from_date', date.today().replace(day=1).isoformat())
    to_date = request.args.get('to_date', date.today().isoformat())

    data = ReportService.sales_report(
        company_id,
        datetime.strptime(from_date, '%Y-%m-%d').date(),
        datetime.strptime(to_date, '%Y-%m-%d').date(),
        party_id=request.args.get('party_id', type=int),
    )
    parties = Party.query.filter_by(company_id=company_id, is_active=True).order_by(Party.name).all()
    return render_template('reports/sales.html', data=data, parties=parties)


@reports_bp.route('/reports/purchases')
@login_required
def purchase_report():
    company_id = get_company_id()
    from_date = request.args.get('from_date', date.today().replace(day=1).isoformat())
    to_date = request.args.get('to_date', date.today().isoformat())

    data = ReportService.purchase_report(
        company_id,
        datetime.strptime(from_date, '%Y-%m-%d').date(),
        datetime.strptime(to_date, '%Y-%m-%d').date(),
    )
    parties = Party.query.filter_by(company_id=company_id, is_active=True).order_by(Party.name).all()
    return render_template('reports/purchases.html', data=data, parties=parties)


@reports_bp.route('/reports/profit-loss')
@login_required
def profit_loss():
    company_id = get_company_id()
    start = request.args.get('start', date.today().replace(month=4 if date.today().month >= 4 else 4,
                                                            day=1,
                                                            year=date.today().year if date.today().month >= 4 else date.today().year - 1).isoformat())
    end = request.args.get('end', date.today().isoformat())

    data = ReportService.profit_and_loss(
        company_id,
        datetime.strptime(start, '%Y-%m-%d').date(),
        datetime.strptime(end, '%Y-%m-%d').date(),
    )
    return render_template('reports/profit_loss.html', data=data, start=start, end=end)


@reports_bp.route('/reports/party-statement')
@login_required
def party_statement_select():
    """Select a party to view their statement."""
    company_id = get_company_id()
    parties = Party.query.filter_by(company_id=company_id, is_active=True).order_by(Party.name).all()
    party_id = request.args.get('party_id', type=int)

    if party_id:
        return redirect(url_for('reports.party_statement', party_id=party_id))

    return render_template('reports/party_statement.html', data=None, parties=parties, party=None, transactions=[])


@reports_bp.route('/reports/party-statement/<int:party_id>')
@login_required
def party_statement(party_id):
    company_id = get_company_id()
    start = request.args.get('start') or request.args.get('from_date')
    end = request.args.get('end') or request.args.get('to_date')
    parties = Party.query.filter_by(company_id=company_id, is_active=True).order_by(Party.name).all()
    party = Party.query.get(party_id)

    data = ReportService.party_statement(
        company_id, party_id,
        datetime.strptime(start, '%Y-%m-%d').date() if start else None,
        datetime.strptime(end, '%Y-%m-%d').date() if end else None,
    )
    return render_template('reports/party_statement.html', data=data, parties=parties,
                           party=party, transactions=data.get('transactions', []))


@reports_bp.route('/reports/gstr1')
@login_required
def gstr1():
    company_id = get_company_id()
    start = request.args.get('start', date.today().replace(day=1).isoformat())
    end = request.args.get('end', date.today().isoformat())

    data = ReportService.gstr1_summary(
        company_id,
        datetime.strptime(start, '%Y-%m-%d').date(),
        datetime.strptime(end, '%Y-%m-%d').date(),
    )
    return render_template('reports/gstr1.html', data=data, start=start, end=end)


@reports_bp.route('/reports/daybook')
@login_required
def daybook():
    """Day Book - all transactions for a given date."""
    company_id = get_company_id()
    target_date = request.args.get('date', date.today().isoformat())
    target = datetime.strptime(target_date, '%Y-%m-%d').date()

    data = ReportService.day_book(company_id, target)
    return render_template('reports/daybook.html', data=data, target_date=target_date)


@reports_bp.route('/reports/sales/csv')
@login_required
def sales_report_csv():
    """Download sales report as CSV."""
    company_id = get_company_id()
    from_date = request.args.get('from_date', date.today().replace(day=1).isoformat())
    to_date = request.args.get('to_date', date.today().isoformat())
    data = ReportService.sales_report(
        company_id,
        datetime.strptime(from_date, '%Y-%m-%d').date(),
        datetime.strptime(to_date, '%Y-%m-%d').date(),
        party_id=request.args.get('party_id', type=int),
    )
    from app.utils.export import sales_csv
    return sales_csv(data.get('invoices', []), filename='sales_report.csv')


@reports_bp.route('/reports/purchases/csv')
@login_required
def purchases_report_csv():
    """Download purchases report as CSV."""
    company_id = get_company_id()
    from_date = request.args.get('from_date', date.today().replace(day=1).isoformat())
    to_date = request.args.get('to_date', date.today().isoformat())
    data = ReportService.purchase_report(
        company_id,
        datetime.strptime(from_date, '%Y-%m-%d').date(),
        datetime.strptime(to_date, '%Y-%m-%d').date(),
    )
    from app.utils.export import purchases_csv
    return purchases_csv(data.get('bills', []), filename='purchase_report.csv')


@reports_bp.route('/reports/profit-loss/csv')
@login_required
def profit_loss_csv_download():
    """Download P&L as CSV."""
    company_id = get_company_id()
    start = request.args.get('start', date.today().replace(day=1).isoformat())
    end = request.args.get('end', date.today().isoformat())
    data = ReportService.profit_and_loss(
        company_id,
        datetime.strptime(start, '%Y-%m-%d').date(),
        datetime.strptime(end, '%Y-%m-%d').date(),
    )
    from app.utils.export import profit_loss_csv
    return profit_loss_csv(data)


@reports_bp.route('/reports/gstr1/csv')
@login_required
def gstr1_csv_download():
    """Download GSTR-1 as CSV."""
    company_id = get_company_id()
    start = request.args.get('start', date.today().replace(day=1).isoformat())
    end = request.args.get('end', date.today().isoformat())

    data = ReportService.gstr1_summary(
        company_id,
        datetime.strptime(start, '%Y-%m-%d').date(),
        datetime.strptime(end, '%Y-%m-%d').date(),
    )
    from app.utils.export import gstr1_csv
    return gstr1_csv(data)


# ─── Mobile API ──────────────────────────────────────────────────────────────

@reports_bp.route('/api/reports/profit-loss', methods=['GET'])
@jwt_required
def api_profit_loss():
    user = request.jwt_user
    start = request.args.get('start', date.today().replace(day=1).isoformat())
    end = request.args.get('end', date.today().isoformat())

    data = ReportService.profit_and_loss(
        user.company_id,
        datetime.strptime(start, '%Y-%m-%d').date(),
        datetime.strptime(end, '%Y-%m-%d').date(),
    )
    return api_response(data)


@reports_bp.route('/api/reports/sales', methods=['GET'])
@jwt_required
def api_sales_report():
    user = request.jwt_user
    start = request.args.get('start', date.today().replace(day=1).isoformat())
    end = request.args.get('end', date.today().isoformat())

    data = ReportService.sales_report(
        user.company_id,
        datetime.strptime(start, '%Y-%m-%d').date(),
        datetime.strptime(end, '%Y-%m-%d').date(),
        party_id=request.args.get('party_id', type=int),
    )
    return api_response(data)


@reports_bp.route('/api/reports/purchases', methods=['GET'])
@jwt_required
def api_purchase_report():
    user = request.jwt_user
    start = request.args.get('start', date.today().replace(day=1).isoformat())
    end = request.args.get('end', date.today().isoformat())

    data = ReportService.purchase_report(
        user.company_id,
        datetime.strptime(start, '%Y-%m-%d').date(),
        datetime.strptime(end, '%Y-%m-%d').date(),
    )
    return api_response(data)


@reports_bp.route('/api/reports/gstr1', methods=['GET'])
@jwt_required
def api_gstr1():
    user = request.jwt_user
    start = request.args.get('start', date.today().replace(day=1).isoformat())
    end = request.args.get('end', date.today().isoformat())

    data = ReportService.gstr1_summary(
        user.company_id,
        datetime.strptime(start, '%Y-%m-%d').date(),
        datetime.strptime(end, '%Y-%m-%d').date(),
    )
    return api_response(data)


@reports_bp.route('/api/reports/party-statement/<int:party_id>', methods=['GET'])
@jwt_required
def api_party_statement(party_id):
    user = request.jwt_user
    start = request.args.get('start')
    end = request.args.get('end')

    data = ReportService.party_statement(
        user.company_id, party_id,
        datetime.strptime(start, '%Y-%m-%d').date() if start else None,
        datetime.strptime(end, '%Y-%m-%d').date() if end else None,
    )
    return api_response(data)
