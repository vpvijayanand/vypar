"""
Expense & Income routes.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date
from decimal import Decimal
from app.extensions import db
from app.models.expense import Expense, ExpenseCategory
from app.models.income import OtherIncome, IncomeCategory
from app.utils.helpers import (
    api_response, api_error, get_company_id, jwt_required, get_json_or_form
)

expenses_bp = Blueprint('expenses', __name__)


# ─── Expense Web Routes ──────────────────────────────────────────────────────

@expenses_bp.route('/expenses')
@login_required
def list_expenses():
    company_id = get_company_id()
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id', type=int)

    query = Expense.query.filter_by(company_id=company_id)
    if category_id:
        query = query.filter_by(category_id=category_id)

    expenses = query.order_by(Expense.expense_date.desc()).paginate(
        page=page, per_page=20, error_out=False)
    categories = ExpenseCategory.query.filter_by(company_id=company_id).all()

    # Total for current month
    month_start = date.today().replace(day=1)
    from sqlalchemy import func
    monthly_total = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.company_id == company_id,
        Expense.expense_date >= month_start
    ).scalar()

    return render_template('expenses/list.html', expenses=expenses,
                           categories=categories, monthly_total=float(monthly_total))


@expenses_bp.route('/expenses/<int:expense_id>')
@login_required
def view_expense(expense_id):
    """View expense details."""
    company_id = get_company_id()
    expense = Expense.query.filter_by(id=expense_id, company_id=company_id).first_or_404()
    return render_template('expenses/view.html', expense=expense)


@expenses_bp.route('/expenses/create', methods=['GET', 'POST'])
@login_required
def create_expense():
    company_id = get_company_id()

    if request.method == 'POST':
        expense = Expense(
            company_id=company_id,
            expense_date=datetime.strptime(
                request.form.get('expense_date', date.today().isoformat()), '%Y-%m-%d').date(),
            category_id=request.form.get('category_id') or None,
            party_id=request.form.get('party_id') or None,
            amount=Decimal(request.form.get('amount', '0') or '0'),
            gst_applicable=request.form.get('gst_applicable') == 'on',
            gst_rate=Decimal(request.form.get('gst_rate', '0') or '0'),
            tax_amount=Decimal(request.form.get('tax_amount', '0') or '0'),
            payment_mode=request.form.get('payment_mode', 'cash'),
            bank_account_id=request.form.get('bank_account_id') or None,
            notes=request.form.get('notes'),
            created_by=current_user.id,
        )
        db.session.add(expense)
        db.session.commit()

        flash('Expense recorded.', 'success')
        return redirect(url_for('expenses.list_expenses'))

    categories = ExpenseCategory.query.filter_by(company_id=company_id).all()
    return render_template('expenses/form.html', expense=None, categories=categories)


@expenses_bp.route('/expenses/<int:expense_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    company_id = get_company_id()
    expense = Expense.query.filter_by(id=expense_id, company_id=company_id).first_or_404()

    if request.method == 'POST':
        expense.expense_date = datetime.strptime(
            request.form.get('expense_date'), '%Y-%m-%d').date()
        expense.category_id = request.form.get('category_id') or None
        expense.amount = Decimal(request.form.get('amount', '0') or '0')
        expense.gst_applicable = request.form.get('gst_applicable') == 'on'
        expense.gst_rate = Decimal(request.form.get('gst_rate', '0') or '0')
        expense.payment_mode = request.form.get('payment_mode', 'cash')
        expense.notes = request.form.get('notes')
        db.session.commit()
        flash('Expense updated.', 'success')
        return redirect(url_for('expenses.list_expenses'))

    categories = ExpenseCategory.query.filter_by(company_id=company_id).all()
    return render_template('expenses/form.html', expense=expense, categories=categories)


@expenses_bp.route('/expenses/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete_expense(expense_id):
    company_id = get_company_id()
    expense = Expense.query.filter_by(id=expense_id, company_id=company_id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted.', 'success')
    return redirect(url_for('expenses.list_expenses'))


# ─── Expense Category Routes ─────────────────────────────────────────────────

@expenses_bp.route('/expense-categories', methods=['GET', 'POST'])
@login_required
def manage_expense_categories():
    company_id = get_company_id()
    if request.method == 'POST':
        cat = ExpenseCategory(
            company_id=company_id,
            name=request.form.get('name'),
            description=request.form.get('description'),
        )
        db.session.add(cat)
        db.session.commit()
        flash(f'Category "{cat.name}" created.', 'success')

    categories = ExpenseCategory.query.filter_by(company_id=company_id).all()
    return render_template('expenses/categories.html', categories=categories)


# ─── Other Income Routes ─────────────────────────────────────────────────────

@expenses_bp.route('/income')
@login_required
def list_income():
    company_id = get_company_id()
    page = request.args.get('page', 1, type=int)
    incomes = OtherIncome.query.filter_by(company_id=company_id).order_by(
        OtherIncome.income_date.desc()).paginate(page=page, per_page=20, error_out=False)
    categories = IncomeCategory.query.filter_by(company_id=company_id).all()
    return render_template('income/list.html', incomes=incomes, categories=categories)


@expenses_bp.route('/income/<int:income_id>')
@login_required
def view_income(income_id):
    """View income details."""
    company_id = get_company_id()
    income = OtherIncome.query.filter_by(id=income_id, company_id=company_id).first_or_404()
    return render_template('income/view.html', income=income)


@expenses_bp.route('/income/create', methods=['GET', 'POST'])
@login_required
def create_income():
    company_id = get_company_id()

    if request.method == 'POST':
        income = OtherIncome(
            company_id=company_id,
            income_date=datetime.strptime(
                request.form.get('income_date', date.today().isoformat()), '%Y-%m-%d').date(),
            category_id=request.form.get('category_id') or None,
            amount=Decimal(request.form.get('amount', '0') or '0'),
            payment_mode=request.form.get('payment_mode', 'cash'),
            bank_account_id=request.form.get('bank_account_id') or None,
            reference=request.form.get('reference'),
            notes=request.form.get('notes'),
            created_by=current_user.id,
        )
        db.session.add(income)
        db.session.commit()
        flash('Income recorded.', 'success')
        return redirect(url_for('expenses.list_income'))

    categories = IncomeCategory.query.filter_by(company_id=company_id).all()
    return render_template('income/form.html', income=None, categories=categories)


@expenses_bp.route('/expenses/csv')
@login_required
def expenses_csv_download():
    """Download expenses as CSV."""
    company_id = get_company_id()
    expenses_list = Expense.query.filter_by(company_id=company_id).order_by(
        Expense.expense_date.desc()).all()
    from app.utils.export import expenses_csv
    return expenses_csv(expenses_list)


@expenses_bp.route('/income/csv')
@login_required
def income_csv_download():
    """Download other income as CSV."""
    company_id = get_company_id()
    incomes_list = OtherIncome.query.filter_by(company_id=company_id).order_by(
        OtherIncome.income_date.desc()).all()
    from app.utils.export import income_csv
    return income_csv(incomes_list)


# ─── Mobile API Routes ───────────────────────────────────────────────────────

@expenses_bp.route('/api/expenses', methods=['GET'])
@jwt_required
def api_list_expenses():
    user = request.jwt_user
    page = request.args.get('page', 1, type=int)
    expenses = Expense.query.filter_by(company_id=user.company_id).order_by(
        Expense.expense_date.desc()).paginate(page=page, per_page=20, error_out=False)
    return api_response([e.to_dict() for e in expenses.items], pagination=expenses)


@expenses_bp.route('/api/expenses', methods=['POST'])
@jwt_required
def api_create_expense():
    user = request.jwt_user
    data = get_json_or_form()

    expense = Expense(
        company_id=user.company_id,
        expense_date=datetime.strptime(data.get('expense_date', date.today().isoformat()), '%Y-%m-%d').date(),
        category_id=data.get('category_id'),
        party_id=data.get('party_id'),
        amount=Decimal(str(data.get('amount', 0))),
        gst_applicable=data.get('gst_applicable', False),
        gst_rate=Decimal(str(data.get('gst_rate', 0))),
        tax_amount=Decimal(str(data.get('tax_amount', 0))),
        payment_mode=data.get('payment_mode', 'cash'),
        notes=data.get('notes'),
        created_by=user.id,
    )
    db.session.add(expense)
    db.session.commit()
    return api_response(expense.to_dict(), 'Expense created', 201)


@expenses_bp.route('/api/income', methods=['GET'])
@jwt_required
def api_list_income():
    user = request.jwt_user
    page = request.args.get('page', 1, type=int)
    incomes = OtherIncome.query.filter_by(company_id=user.company_id).order_by(
        OtherIncome.income_date.desc()).paginate(page=page, per_page=20, error_out=False)
    return api_response([i.to_dict() for i in incomes.items], pagination=incomes)


@expenses_bp.route('/api/income', methods=['POST'])
@jwt_required
def api_create_income():
    user = request.jwt_user
    data = get_json_or_form()

    income = OtherIncome(
        company_id=user.company_id,
        income_date=datetime.strptime(data.get('income_date', date.today().isoformat()), '%Y-%m-%d').date(),
        category_id=data.get('category_id'),
        amount=Decimal(str(data.get('amount', 0))),
        payment_mode=data.get('payment_mode', 'cash'),
        reference=data.get('reference'),
        notes=data.get('notes'),
        created_by=user.id,
    )
    db.session.add(income)
    db.session.commit()
    return api_response(income.to_dict(), 'Income created', 201)
