"""
Cash & Bank routes - Bank accounts, cash-in-hand, cheques, loans.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date
from decimal import Decimal
from app.extensions import db
from app.models.bank import BankAccount, CashInHand, Cheque, LoanAccount
from app.models.party import Party
from app.utils.helpers import (
    api_response, api_error, get_company_id, jwt_required, get_json_or_form
)

bank_bp = Blueprint('bank', __name__)


# ─── Bank Account Web Routes ─────────────────────────────────────────────────

@bank_bp.route('/bank')
@login_required
def list_accounts():
    company_id = get_company_id()
    bank_accounts = BankAccount.query.filter_by(company_id=company_id, is_active=True).all()
    cash = CashInHand.query.filter_by(company_id=company_id).first()
    loans = LoanAccount.query.filter_by(company_id=company_id, is_active=True).all()

    total_bank = sum(float(a.current_balance) for a in bank_accounts)
    total_cash = float(cash.current_balance) if cash else 0

    return render_template('bank/list.html',
                           bank_accounts=bank_accounts, cash=cash,
                           loans=loans, total_bank=total_bank, total_cash=total_cash)


@bank_bp.route('/bank/create', methods=['GET', 'POST'])
@login_required
def create_account():
    company_id = get_company_id()

    if request.method == 'POST':
        account = BankAccount(
            company_id=company_id,
            account_name=request.form.get('account_name'),
            account_number=request.form.get('account_number'),
            bank_name=request.form.get('bank_name'),
            ifsc_code=request.form.get('ifsc_code'),
            opening_balance=Decimal(request.form.get('opening_balance', '0') or '0'),
            account_type=request.form.get('account_type', 'savings'),
        )
        account.current_balance = account.opening_balance
        db.session.add(account)
        db.session.commit()

        flash(f'Bank account "{account.account_name}" created.', 'success')
        return redirect(url_for('bank.list_accounts'))

    return render_template('bank/form.html', account=None)


@bank_bp.route('/bank/<int:account_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_account(account_id):
    company_id = get_company_id()
    account = BankAccount.query.filter_by(id=account_id, company_id=company_id).first_or_404()

    if request.method == 'POST':
        account.account_name = request.form.get('account_name', account.account_name)
        account.account_number = request.form.get('account_number')
        account.bank_name = request.form.get('bank_name')
        account.ifsc_code = request.form.get('ifsc_code')
        account.account_type = request.form.get('account_type', 'savings')
        db.session.commit()

        flash('Bank account updated.', 'success')
        return redirect(url_for('bank.list_accounts'))

    return render_template('bank/form.html', account=account)


# ─── Cash in Hand ─────────────────────────────────────────────────────────────

@bank_bp.route('/cash', methods=['GET', 'POST'])
@login_required
def manage_cash():
    company_id = get_company_id()
    cash = CashInHand.query.filter_by(company_id=company_id).first()

    if request.method == 'POST':
        if not cash:
            cash = CashInHand(company_id=company_id)
            db.session.add(cash)

        cash.opening_balance = Decimal(request.form.get('opening_balance', '0') or '0')
        cash.current_balance = Decimal(request.form.get('current_balance',
                                                         str(cash.opening_balance)) or '0')
        cash.last_updated = date.today()
        db.session.commit()
        flash('Cash balance updated.', 'success')
        return redirect(url_for('bank.list_accounts'))

    return render_template('bank/cash.html', cash=cash)


# ─── Cheque Management ────────────────────────────────────────────────────────

@bank_bp.route('/cheques')
@login_required
def list_cheques():
    company_id = get_company_id()
    status = request.args.get('status')
    query = Cheque.query.filter_by(company_id=company_id)
    if status:
        query = query.filter_by(status=status)
    cheques = query.order_by(Cheque.issue_date.desc()).all()
    return render_template('bank/cheques.html', cheques=cheques, status=status)


@bank_bp.route('/cheques/create', methods=['GET', 'POST'])
@login_required
def create_cheque():
    company_id = get_company_id()

    if request.method == 'POST':
        cheque = Cheque(
            company_id=company_id,
            cheque_number=request.form.get('cheque_number'),
            party_id=request.form.get('party_id') or None,
            bank_name=request.form.get('bank_name'),
            amount=Decimal(request.form.get('amount', '0') or '0'),
            issue_date=datetime.strptime(
                request.form.get('issue_date', date.today().isoformat()), '%Y-%m-%d').date(),
            cheque_type=request.form.get('cheque_type', 'received'),
            status='pending',
        )
        db.session.add(cheque)
        db.session.commit()
        flash('Cheque recorded.', 'success')
        return redirect(url_for('bank.list_cheques'))

    parties = Party.query.filter_by(company_id=company_id, is_active=True).all()
    return render_template('bank/cheque_form.html', cheque=None,
                           parties=parties, today=date.today().isoformat())


@bank_bp.route('/cheques/<int:cheque_id>/status', methods=['POST'])
@login_required
def update_cheque_status(cheque_id):
    company_id = get_company_id()
    cheque = Cheque.query.filter_by(id=cheque_id, company_id=company_id).first_or_404()
    new_status = request.form.get('status')
    if new_status in ('cleared', 'bounced', 'cancelled'):
        cheque.status = new_status
        if new_status == 'cleared':
            cheque.clearance_date = date.today()
        db.session.commit()
        flash(f'Cheque #{cheque.cheque_number} marked as {new_status}.', 'success')
    return redirect(url_for('bank.list_cheques'))


@bank_bp.route('/cheques/csv')
@login_required
def cheques_csv_download():
    """Download cheques as CSV."""
    company_id = get_company_id()
    cheques = Cheque.query.filter_by(company_id=company_id).order_by(Cheque.issue_date.desc()).all()
    from app.utils.export import cheques_csv
    return cheques_csv(cheques)


# ─── Loan Accounts ───────────────────────────────────────────────────────────

@bank_bp.route('/loans/create', methods=['GET', 'POST'])
@login_required
def create_loan():
    company_id = get_company_id()

    if request.method == 'POST':
        loan = LoanAccount(
            company_id=company_id,
            lender_name=request.form.get('lender_name'),
            loan_amount=Decimal(request.form.get('loan_amount', '0') or '0'),
            interest_rate=Decimal(request.form.get('interest_rate', '0') or '0'),
            emi_amount=Decimal(request.form.get('emi_amount', '0') or '0'),
            start_date=datetime.strptime(
                request.form.get('start_date', date.today().isoformat()), '%Y-%m-%d').date(),
            tenure_months=int(request.form.get('tenure_months', '12') or '12'),
            loan_type=request.form.get('loan_type', 'term'),
        )
        loan.outstanding_balance = loan.loan_amount
        db.session.add(loan)
        db.session.commit()
        flash('Loan account created.', 'success')
        return redirect(url_for('bank.list_accounts'))

    return render_template('bank/loan_form.html', loan=None, today=date.today().isoformat())


# ─── Mobile API ──────────────────────────────────────────────────────────────

@bank_bp.route('/api/bank-accounts', methods=['GET'])
@jwt_required
def api_list_accounts():
    user = request.jwt_user
    accounts = BankAccount.query.filter_by(company_id=user.company_id, is_active=True).all()
    cash = CashInHand.query.filter_by(company_id=user.company_id).first()
    return api_response({
        'bank_accounts': [a.to_dict() for a in accounts],
        'cash_in_hand': cash.to_dict() if cash else {'current_balance': 0},
    })


@bank_bp.route('/api/bank-accounts', methods=['POST'])
@jwt_required
def api_create_account():
    user = request.jwt_user
    data = get_json_or_form()

    account = BankAccount(
        company_id=user.company_id,
        account_name=data.get('account_name'),
        account_number=data.get('account_number'),
        bank_name=data.get('bank_name'),
        ifsc_code=data.get('ifsc_code'),
        opening_balance=Decimal(str(data.get('opening_balance', 0))),
        account_type=data.get('account_type', 'savings'),
    )
    account.current_balance = account.opening_balance
    db.session.add(account)
    db.session.commit()
    return api_response(account.to_dict(), 'Bank account created', 201)


@bank_bp.route('/api/cheques', methods=['GET'])
@jwt_required
def api_list_cheques():
    user = request.jwt_user
    cheques = Cheque.query.filter_by(company_id=user.company_id).order_by(
        Cheque.issue_date.desc()).all()
    return api_response([c.to_dict() for c in cheques])


@bank_bp.route('/api/loans', methods=['GET'])
@jwt_required
def api_list_loans():
    user = request.jwt_user
    loans = LoanAccount.query.filter_by(company_id=user.company_id, is_active=True).all()
    return api_response([l.to_dict() for l in loans])
