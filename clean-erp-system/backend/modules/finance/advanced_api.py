# Advanced Finance API Endpoints
# Comprehensive financial management with multi-currency, budgeting, and investment tracking

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import require_auth, get_current_user
from .advanced_models import (
    CurrencyRate, ChartOfAccounts, JournalEntry, JournalEntryLine,
    Budget, BudgetItem, Investment, InvestmentTransaction, CashFlow, TaxRate
)
from datetime import datetime, date
from decimal import Decimal
import json

# Create blueprint
advanced_finance_bp = Blueprint('advanced_finance', __name__, url_prefix='/advanced-finance')

# Currency Management Endpoints
@advanced_finance_bp.route('/currency-rates', methods=['GET'])
@require_auth
def get_currency_rates():
    """Get all currency exchange rates"""
    try:
        rates = CurrencyRate.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [rate.to_dict() for rate in rates]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_finance_bp.route('/currency-rates', methods=['POST'])
@require_auth
def create_currency_rate():
    """Create a new currency exchange rate"""
    try:
        data = request.get_json()
        rate = CurrencyRate(
            from_currency=data['from_currency'],
            to_currency=data['to_currency'],
            exchange_rate=Decimal(str(data['exchange_rate'])),
            rate_date=datetime.strptime(data['rate_date'], '%Y-%m-%d').date() if data.get('rate_date') else date.today(),
            source=data.get('source', 'Manual'),
            is_active=data.get('is_active', True),
            company_id=get_current_user().company_id
        )
        db.session.add(rate)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': rate.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_finance_bp.route('/currency-rates/convert', methods=['POST'])
@require_auth
def convert_currency():
    """Convert amount between currencies"""
    try:
        data = request.get_json()
        amount = Decimal(str(data['amount']))
        from_currency = data['from_currency']
        to_currency = data['to_currency']
        
        if from_currency == to_currency:
            converted_amount = amount
        else:
            # Get exchange rate
            rate = CurrencyRate.query.filter_by(
                from_currency=from_currency,
                to_currency=to_currency,
                company_id=get_current_user().company_id,
                is_active=True
            ).order_by(CurrencyRate.rate_date.desc()).first()
            
            if not rate:
                return jsonify({
                    'success': False,
                    'message': f'Exchange rate not found for {from_currency} to {to_currency}'
                }), 404
            
            converted_amount = amount * rate.exchange_rate
        
        return jsonify({
            'success': True,
            'data': {
                'original_amount': float(amount),
                'from_currency': from_currency,
                'to_currency': to_currency,
                'converted_amount': float(converted_amount),
                'exchange_rate': float(rate.exchange_rate) if rate else 1.0
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Chart of Accounts Endpoints
@advanced_finance_bp.route('/chart-of-accounts', methods=['GET'])
@require_auth
def get_chart_of_accounts():
    """Get all chart of accounts"""
    try:
        accounts = ChartOfAccounts.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [account.to_dict() for account in accounts]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_finance_bp.route('/chart-of-accounts', methods=['POST'])
@require_auth
def create_chart_of_account():
    """Create a new chart of account"""
    try:
        data = request.get_json()
        account = ChartOfAccounts(
            account_code=data['account_code'],
            account_name=data['account_name'],
            account_type=data['account_type'],
            description=data.get('description'),
            parent_account_id=data.get('parent_account_id'),
            is_active=data.get('is_active', True),
            is_system_account=data.get('is_system_account', False),
            requires_reconciliation=data.get('requires_reconciliation', False),
            base_currency=data.get('base_currency', 'USD'),
            allow_foreign_currency=data.get('allow_foreign_currency', False),
            company_id=get_current_user().company_id
        )
        db.session.add(account)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': account.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Journal Entry Endpoints
@advanced_finance_bp.route('/journal-entries', methods=['GET'])
@require_auth
def get_journal_entries():
    """Get all journal entries"""
    try:
        entries = JournalEntry.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [entry.to_dict() for entry in entries]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_finance_bp.route('/journal-entries', methods=['POST'])
@require_auth
def create_journal_entry():
    """Create a new journal entry"""
    try:
        data = request.get_json()
        
        # Generate entry number
        entry_number = f"JE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        entry = JournalEntry(
            entry_number=entry_number,
            entry_date=datetime.strptime(data['entry_date'], '%Y-%m-%d').date(),
            reference=data.get('reference'),
            description=data.get('description'),
            base_currency=data.get('base_currency', 'USD'),
            exchange_rate=Decimal(str(data.get('exchange_rate', 1.0))),
            status=data.get('status', 'Draft'),
            company_id=get_current_user().company_id
        )
        
        # Add entry lines
        total_debit = Decimal('0.0')
        total_credit = Decimal('0.0')
        
        for line_data in data.get('entry_lines', []):
            line = JournalEntryLine(
                line_number=line_data['line_number'],
                description=line_data.get('description'),
                debit_amount=Decimal(str(line_data.get('debit_amount', 0.0))),
                credit_amount=Decimal(str(line_data.get('credit_amount', 0.0))),
                account_id=line_data['account_id'],
                currency=line_data.get('currency', 'USD'),
                exchange_rate=Decimal(str(line_data.get('exchange_rate', 1.0))),
                company_id=get_current_user().company_id
            )
            entry.entry_lines.append(line)
            total_debit += line.debit_amount
            total_credit += line.credit_amount
        
        # Check if entry is balanced
        entry.total_debit = total_debit
        entry.total_credit = total_credit
        entry.is_balanced = (total_debit == total_credit)
        
        db.session.add(entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': entry.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_finance_bp.route('/journal-entries/<int:entry_id>/post', methods=['POST'])
@require_auth
def post_journal_entry(entry_id):
    """Post a journal entry"""
    try:
        entry = JournalEntry.query.get_or_404(entry_id)
        
        if not entry.is_balanced:
            return jsonify({
                'success': False,
                'message': 'Journal entry is not balanced'
            }), 400
        
        entry.status = 'Posted'
        entry.posted_date = datetime.utcnow()
        entry.posted_by_id = get_current_user().id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': entry.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Budget Management Endpoints
@advanced_finance_bp.route('/budgets', methods=['GET'])
@require_auth
def get_budgets():
    """Get all budgets"""
    try:
        budgets = Budget.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [budget.to_dict() for budget in budgets]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_finance_bp.route('/budgets', methods=['POST'])
@require_auth
def create_budget():
    """Create a new budget"""
    try:
        data = request.get_json()
        budget = Budget(
            budget_name=data['budget_name'],
            budget_year=data['budget_year'],
            budget_period=data.get('budget_period', 'Annual'),
            description=data.get('description'),
            status=data.get('status', 'Draft'),
            company_id=get_current_user().company_id
        )
        db.session.add(budget)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': budget.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_finance_bp.route('/budgets/<int:budget_id>/items', methods=['POST'])
@require_auth
def add_budget_item(budget_id):
    """Add a budget item"""
    try:
        data = request.get_json()
        item = BudgetItem(
            account_id=data['account_id'],
            budget_id=budget_id,
            budget_amount=Decimal(str(data.get('budget_amount', 0.0))),
            period_amounts=data.get('period_amounts', {}),
            company_id=get_current_user().company_id
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': item.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Investment Management Endpoints
@advanced_finance_bp.route('/investments', methods=['GET'])
@require_auth
def get_investments():
    """Get all investments"""
    try:
        investments = Investment.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [investment.to_dict() for investment in investments]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_finance_bp.route('/investments', methods=['POST'])
@require_auth
def create_investment():
    """Create a new investment"""
    try:
        data = request.get_json()
        investment = Investment(
            investment_name=data['investment_name'],
            investment_type=data['investment_type'],
            symbol=data.get('symbol'),
            description=data.get('description'),
            purchase_date=datetime.strptime(data['purchase_date'], '%Y-%m-%d').date() if data.get('purchase_date') else None,
            purchase_price=Decimal(str(data.get('purchase_price', 0.0))),
            quantity=Decimal(str(data.get('quantity', 0.0))),
            currency=data.get('currency', 'USD'),
            company_id=get_current_user().company_id
        )
        
        # Calculate total cost
        investment.total_cost = investment.purchase_price * investment.quantity
        
        db.session.add(investment)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': investment.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_finance_bp.route('/investments/<int:investment_id>/update-price', methods=['PUT'])
@require_auth
def update_investment_price(investment_id):
    """Update investment current price"""
    try:
        investment = Investment.query.get_or_404(investment_id)
        data = request.get_json()
        
        investment.current_price = Decimal(str(data['current_price']))
        investment.current_value = investment.current_price * investment.quantity
        investment.gain_loss = investment.current_value - investment.total_cost
        investment.gain_loss_percentage = (investment.gain_loss / investment.total_cost * 100) if investment.total_cost > 0 else 0
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': investment.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Cash Flow Management Endpoints
@advanced_finance_bp.route('/cash-flows', methods=['GET'])
@require_auth
def get_cash_flows():
    """Get all cash flows"""
    try:
        cash_flows = CashFlow.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [cash_flow.to_dict() for cash_flow in cash_flows]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_finance_bp.route('/cash-flows', methods=['POST'])
@require_auth
def create_cash_flow():
    """Create a new cash flow entry"""
    try:
        data = request.get_json()
        cash_flow = CashFlow(
            period_start=datetime.strptime(data['period_start'], '%Y-%m-%d').date(),
            period_end=datetime.strptime(data['period_end'], '%Y-%m-%d').date(),
            period_type=data.get('period_type', 'Monthly'),
            operating_cash_flow=Decimal(str(data.get('operating_cash_flow', 0.0))),
            investing_cash_flow=Decimal(str(data.get('investing_cash_flow', 0.0))),
            financing_cash_flow=Decimal(str(data.get('financing_cash_flow', 0.0))),
            beginning_cash=Decimal(str(data.get('beginning_cash', 0.0))),
            company_id=get_current_user().company_id
        )
        
        # Calculate net cash flow and ending cash
        cash_flow.net_cash_flow = cash_flow.operating_cash_flow + cash_flow.investing_cash_flow + cash_flow.financing_cash_flow
        cash_flow.ending_cash = cash_flow.beginning_cash + cash_flow.net_cash_flow
        
        db.session.add(cash_flow)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': cash_flow.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Tax Management Endpoints
@advanced_finance_bp.route('/tax-rates', methods=['GET'])
@require_auth
def get_tax_rates():
    """Get all tax rates"""
    try:
        tax_rates = TaxRate.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [tax_rate.to_dict() for tax_rate in tax_rates]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_finance_bp.route('/tax-rates', methods=['POST'])
@require_auth
def create_tax_rate():
    """Create a new tax rate"""
    try:
        data = request.get_json()
        tax_rate = TaxRate(
            tax_name=data['tax_name'],
            tax_type=data['tax_type'],
            tax_rate=Decimal(str(data['tax_rate'])),
            is_active=data.get('is_active', True),
            effective_date=datetime.strptime(data['effective_date'], '%Y-%m-%d').date() if data.get('effective_date') else date.today(),
            expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data.get('expiry_date') else None,
            company_id=get_current_user().company_id
        )
        db.session.add(tax_rate)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': tax_rate.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Financial Analytics Endpoints
@advanced_finance_bp.route('/analytics/financial-summary', methods=['GET'])
@require_auth
def get_financial_summary():
    """Get financial summary analytics"""
    try:
        # Get total assets, liabilities, equity
        assets = db.session.query(db.func.sum(JournalEntryLine.debit_amount)).join(JournalEntry).join(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Asset',
            JournalEntry.company_id == get_current_user().company_id,
            JournalEntry.status == 'Posted'
        ).scalar() or 0
        
        liabilities = db.session.query(db.func.sum(JournalEntryLine.credit_amount)).join(JournalEntry).join(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Liability',
            JournalEntry.company_id == get_current_user().company_id,
            JournalEntry.status == 'Posted'
        ).scalar() or 0
        
        equity = db.session.query(db.func.sum(JournalEntryLine.credit_amount)).join(JournalEntry).join(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Equity',
            JournalEntry.company_id == get_current_user().company_id,
            JournalEntry.status == 'Posted'
        ).scalar() or 0
        
        # Get revenue and expenses
        revenue = db.session.query(db.func.sum(JournalEntryLine.credit_amount)).join(JournalEntry).join(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Revenue',
            JournalEntry.company_id == get_current_user().company_id,
            JournalEntry.status == 'Posted'
        ).scalar() or 0
        
        expenses = db.session.query(db.func.sum(JournalEntryLine.debit_amount)).join(JournalEntry).join(ChartOfAccounts).filter(
            ChartOfAccounts.account_type == 'Expense',
            JournalEntry.company_id == get_current_user().company_id,
            JournalEntry.status == 'Posted'
        ).scalar() or 0
        
        net_income = revenue - expenses
        
        return jsonify({
            'success': True,
            'data': {
                'assets': float(assets),
                'liabilities': float(liabilities),
                'equity': float(equity),
                'revenue': float(revenue),
                'expenses': float(expenses),
                'net_income': float(net_income),
                'total_equity': float(assets - liabilities)
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_finance_bp.route('/analytics/budget-variance', methods=['GET'])
@require_auth
def get_budget_variance():
    """Get budget variance analysis"""
    try:
        budget_id = request.args.get('budget_id')
        if not budget_id:
            return jsonify({
                'success': False,
                'message': 'Budget ID is required'
            }), 400
        
        budget = Budget.query.get_or_404(budget_id)
        budget_items = BudgetItem.query.filter_by(budget_id=budget_id).all()
        
        variance_data = []
        for item in budget_items:
            variance_data.append({
                'account_id': item.account_id,
                'account_name': item.account.account_name,
                'budget_amount': float(item.budget_amount),
                'actual_amount': float(item.actual_amount),
                'variance_amount': float(item.variance_amount),
                'variance_percentage': float(item.variance_percentage)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'budget_name': budget.budget_name,
                'budget_year': budget.budget_year,
                'total_budget': float(budget.total_budget),
                'total_actual': float(budget.total_actual),
                'total_variance': float(budget.total_variance),
                'items': variance_data
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
