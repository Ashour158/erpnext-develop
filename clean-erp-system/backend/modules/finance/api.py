# Finance API - Complete Financial Management API
# Advanced financial operations without Frappe dependencies

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import token_required, get_current_user
from .models import (
    Company, ChartOfAccounts, JournalEntry, JournalEntryLine, Invoice, InvoiceLine,
    Payment, FinancialStatement, Budget, Currency, BankAccount
)
from datetime import datetime, timedelta
import json

finance_api = Blueprint('finance_api', __name__)

# Company Management
@finance_api.route('/companies', methods=['GET'])
@token_required
def get_companies():
    """Get all companies"""
    try:
        companies = Company.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'data': [company.to_dict() for company in companies]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@finance_api.route('/companies', methods=['POST'])
@token_required
def create_company():
    """Create new company"""
    try:
        data = request.get_json()
        company = Company(
            name=data['name'],
            code=data['code'],
            legal_name=data.get('legal_name'),
            tax_id=data.get('tax_id'),
            email=data.get('email'),
            phone=data.get('phone'),
            base_currency=data.get('base_currency', 'USD')
        )
        db.session.add(company)
        db.session.commit()
        return jsonify({'success': True, 'data': company.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Chart of Accounts
@finance_api.route('/chart-of-accounts', methods=['GET'])
@token_required
def get_chart_of_accounts():
    """Get chart of accounts"""
    try:
        company_id = request.args.get('company_id')
        accounts = ChartOfAccounts.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [account.to_dict() for account in accounts]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@finance_api.route('/chart-of-accounts', methods=['POST'])
@token_required
def create_account():
    """Create new account"""
    try:
        data = request.get_json()
        account = ChartOfAccounts(
            account_code=data['account_code'],
            account_name=data['account_name'],
            account_type=data['account_type'],
            company_id=data['company_id'],
            description=data.get('description'),
            is_group=data.get('is_group', False)
        )
        db.session.add(account)
        db.session.commit()
        return jsonify({'success': True, 'data': account.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Journal Entries
@finance_api.route('/journal-entries', methods=['GET'])
@token_required
def get_journal_entries():
    """Get journal entries"""
    try:
        company_id = request.args.get('company_id')
        entries = JournalEntry.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [entry.to_dict() for entry in entries]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@finance_api.route('/journal-entries', methods=['POST'])
@token_required
def create_journal_entry():
    """Create journal entry"""
    try:
        data = request.get_json()
        entry = JournalEntry(
            entry_number=data['entry_number'],
            entry_date=datetime.fromisoformat(data['entry_date']),
            reference=data.get('reference'),
            description=data.get('description'),
            company_id=data['company_id']
        )
        db.session.add(entry)
        
        # Add journal entry lines
        for line_data in data.get('lines', []):
            line = JournalEntryLine(
                journal_entry=entry,
                account_id=line_data['account_id'],
                description=line_data.get('description'),
                debit_amount=line_data.get('debit_amount', 0),
                credit_amount=line_data.get('credit_amount', 0)
            )
            db.session.add(line)
        
        db.session.commit()
        return jsonify({'success': True, 'data': entry.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Invoices
@finance_api.route('/invoices', methods=['GET'])
@token_required
def get_invoices():
    """Get invoices"""
    try:
        company_id = request.args.get('company_id')
        status = request.args.get('status')
        query = Invoice.query.filter_by(company_id=company_id)
        if status:
            query = query.filter_by(status=status)
        invoices = query.all()
        return jsonify({
            'success': True,
            'data': [invoice.to_dict() for invoice in invoices]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@finance_api.route('/invoices', methods=['POST'])
@token_required
def create_invoice():
    """Create invoice"""
    try:
        data = request.get_json()
        invoice = Invoice(
            invoice_number=data['invoice_number'],
            invoice_date=datetime.fromisoformat(data['invoice_date']),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            customer_id=data.get('customer_id'),
            customer_name=data.get('customer_name'),
            customer_email=data.get('customer_email'),
            customer_address=data.get('customer_address'),
            subtotal=data.get('subtotal', 0),
            tax_amount=data.get('tax_amount', 0),
            total_amount=data.get('total_amount', 0),
            company_id=data['company_id'],
            currency=data.get('currency', 'USD')
        )
        db.session.add(invoice)
        
        # Add invoice lines
        for line_data in data.get('lines', []):
            line = InvoiceLine(
                invoice=invoice,
                item_name=line_data['item_name'],
                description=line_data.get('description'),
                quantity=line_data.get('quantity', 1),
                unit_price=line_data.get('unit_price', 0),
                discount_percentage=line_data.get('discount_percentage', 0),
                tax_percentage=line_data.get('tax_percentage', 0),
                line_total=line_data.get('line_total', 0)
            )
            db.session.add(line)
        
        db.session.commit()
        return jsonify({'success': True, 'data': invoice.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Payments
@finance_api.route('/payments', methods=['GET'])
@token_required
def get_payments():
    """Get payments"""
    try:
        company_id = request.args.get('company_id')
        payments = Payment.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [payment.to_dict() for payment in payments]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@finance_api.route('/payments', methods=['POST'])
@token_required
def create_payment():
    """Create payment"""
    try:
        data = request.get_json()
        payment = Payment(
            payment_number=data['payment_number'],
            payment_date=datetime.fromisoformat(data['payment_date']),
            amount=data['amount'],
            payment_method=data.get('payment_method'),
            reference=data.get('reference'),
            notes=data.get('notes'),
            invoice_id=data.get('invoice_id'),
            company_id=data['company_id']
        )
        db.session.add(payment)
        db.session.commit()
        return jsonify({'success': True, 'data': payment.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Financial Statements
@finance_api.route('/financial-statements', methods=['GET'])
@token_required
def get_financial_statements():
    """Get financial statements"""
    try:
        company_id = request.args.get('company_id')
        statement_type = request.args.get('statement_type')
        query = FinancialStatement.query.filter_by(company_id=company_id)
        if statement_type:
            query = query.filter_by(statement_type=statement_type)
        statements = query.all()
        return jsonify({
            'success': True,
            'data': [statement.to_dict() for statement in statements]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@finance_api.route('/financial-statements/generate', methods=['POST'])
@token_required
def generate_financial_statement():
    """Generate financial statement"""
    try:
        data = request.get_json()
        company_id = data['company_id']
        statement_type = data['statement_type']
        period_start = datetime.fromisoformat(data['period_start'])
        period_end = datetime.fromisoformat(data['period_end'])
        
        # Generate statement data based on type
        statement_data = generate_statement_data(company_id, statement_type, period_start, period_end)
        
        statement = FinancialStatement(
            statement_type=statement_type,
            period_start=period_start,
            period_end=period_end,
            statement_data=statement_data,
            company_id=company_id
        )
        db.session.add(statement)
        db.session.commit()
        return jsonify({'success': True, 'data': statement.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Budget Management
@finance_api.route('/budgets', methods=['GET'])
@token_required
def get_budgets():
    """Get budgets"""
    try:
        company_id = request.args.get('company_id')
        budgets = Budget.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [budget.to_dict() for budget in budgets]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@finance_api.route('/budgets', methods=['POST'])
@token_required
def create_budget():
    """Create budget"""
    try:
        data = request.get_json()
        budget = Budget(
            budget_name=data['budget_name'],
            budget_period=data.get('budget_period'),
            period_start=datetime.fromisoformat(data['period_start']),
            period_end=datetime.fromisoformat(data['period_end']),
            budget_data=data.get('budget_data', {}),
            total_budget=data.get('total_budget', 0),
            company_id=data['company_id']
        )
        db.session.add(budget)
        db.session.commit()
        return jsonify({'success': True, 'data': budget.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Currency Management
@finance_api.route('/currencies', methods=['GET'])
@token_required
def get_currencies():
    """Get currencies"""
    try:
        currencies = Currency.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'data': [currency.to_dict() for currency in currencies]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Bank Accounts
@finance_api.route('/bank-accounts', methods=['GET'])
@token_required
def get_bank_accounts():
    """Get bank accounts"""
    try:
        company_id = request.args.get('company_id')
        accounts = BankAccount.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [account.to_dict() for account in accounts]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@finance_api.route('/bank-accounts', methods=['POST'])
@token_required
def create_bank_account():
    """Create bank account"""
    try:
        data = request.get_json()
        account = BankAccount(
            account_name=data['account_name'],
            account_number=data.get('account_number'),
            bank_name=data.get('bank_name'),
            account_type=data.get('account_type'),
            currency=data.get('currency', 'USD'),
            company_id=data['company_id']
        )
        db.session.add(account)
        db.session.commit()
        return jsonify({'success': True, 'data': account.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Helper Functions
def generate_statement_data(company_id, statement_type, period_start, period_end):
    """Generate financial statement data"""
    if statement_type == 'P&L':
        return generate_profit_loss_data(company_id, period_start, period_end)
    elif statement_type == 'Balance Sheet':
        return generate_balance_sheet_data(company_id, period_start, period_end)
    elif statement_type == 'Cash Flow':
        return generate_cash_flow_data(company_id, period_start, period_end)
    return {}

def generate_profit_loss_data(company_id, period_start, period_end):
    """Generate Profit & Loss statement data"""
    # Implementation for P&L statement
    return {
        'revenue': 0,
        'expenses': 0,
        'net_income': 0
    }

def generate_balance_sheet_data(company_id, period_start, period_end):
    """Generate Balance Sheet data"""
    # Implementation for Balance Sheet
    return {
        'assets': 0,
        'liabilities': 0,
        'equity': 0
    }

def generate_cash_flow_data(company_id, period_start, period_end):
    """Generate Cash Flow statement data"""
    # Implementation for Cash Flow
    return {
        'operating_cash_flow': 0,
        'investing_cash_flow': 0,
        'financing_cash_flow': 0
    }
