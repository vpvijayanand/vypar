"""
Dashboard routes - Business overview and KPIs.
"""
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import date, datetime
from app.utils.helpers import api_response, get_company_id, jwt_required
from app.services.report_service import DashboardService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Web dashboard page."""
    company_id = get_company_id()
    if not company_id:
        return render_template('setup/company.html')

    period_start = date.today().replace(day=1)
    period_end = date.today()
    data = DashboardService.get_dashboard_data(company_id, period_start, period_end)
    return render_template('dashboard/index.html', data=data)


@dashboard_bp.route('/api/dashboard', methods=['GET'])
@jwt_required
def api_dashboard():
    """Mobile API - Dashboard data."""
    user = request.jwt_user
    company_id = user.company_id

    start = request.args.get('start', date.today().replace(day=1).isoformat())
    end = request.args.get('end', date.today().isoformat())

    data = DashboardService.get_dashboard_data(
        company_id,
        datetime.strptime(start, '%Y-%m-%d').date(),
        datetime.strptime(end, '%Y-%m-%d').date(),
    )
    return api_response(data)


@dashboard_bp.route('/api/dashboard/daily-sales', methods=['GET'])
@jwt_required
def api_daily_sales():
    """Mobile API - Daily sales chart data."""
    user = request.jwt_user
    start = request.args.get('start', date.today().replace(day=1).isoformat())
    end = request.args.get('end', date.today().isoformat())

    data = DashboardService.get_daily_sales(
        user.company_id,
        datetime.strptime(start, '%Y-%m-%d').date(),
        datetime.strptime(end, '%Y-%m-%d').date(),
    )
    return api_response(data)
