# Finance Module - Complete Financial Management
# Advanced accounting, invoicing, and financial reporting

from flask import Blueprint
from .models import (
    Company, ChartOfAccounts, JournalEntry, Invoice, Payment,
    FinancialStatement, Budget, Tax, Currency, BankAccount
)
from .api import finance_api

# Create Finance blueprint
finance_bp = Blueprint('finance', __name__)

# Register API routes
finance_bp.register_blueprint(finance_api, url_prefix='')

# Module information
FINANCE_MODULE_INFO = {
    'name': 'Finance',
    'version': '1.0.0',
    'description': 'Complete Financial Management System',
    'features': [
        'Multi-Company Support',
        'Multi-Currency Support',
        'Chart of Accounts',
        'Journal Entries',
        'Invoicing System',
        'Payment Processing',
        'Financial Statements',
        'Budget Management',
        'Tax Management',
        'Bank Reconciliation',
        'AI Financial Analytics',
        'Automated Reporting',
        'Compliance Management'
    ]
}
