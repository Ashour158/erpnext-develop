# Advanced Finance Models
# Comprehensive financial management with multi-currency, budgeting, and investment tracking

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

class Currency(enum.Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"
    INR = "INR"
    BRL = "BRL"

class AccountType(enum.Enum):
    ASSET = "Asset"
    LIABILITY = "Liability"
    EQUITY = "Equity"
    REVENUE = "Revenue"
    EXPENSE = "Expense"

class TransactionType(enum.Enum):
    DEBIT = "Debit"
    CREDIT = "Credit"

class InvestmentType(enum.Enum):
    STOCK = "Stock"
    BOND = "Bond"
    MUTUAL_FUND = "Mutual Fund"
    ETF = "ETF"
    REAL_ESTATE = "Real Estate"
    COMMODITY = "Commodity"
    CRYPTOCURRENCY = "Cryptocurrency"
    OTHER = "Other"

class BudgetStatus(enum.Enum):
    DRAFT = "Draft"
    APPROVED = "Approved"
    ACTIVE = "Active"
    CLOSED = "Closed"

# Multi-Currency Support
class CurrencyRate(BaseModel):
    """Currency exchange rate model"""
    __tablename__ = 'currency_rates'
    
    # Currency Information
    from_currency = db.Column(db.Enum(Currency), nullable=False)
    to_currency = db.Column(db.Enum(Currency), nullable=False)
    exchange_rate = db.Column(db.Numeric(15, 6), nullable=False)
    rate_date = db.Column(db.Date, default=date.today)
    
    # Rate Source
    source = db.Column(db.String(100), default='Manual')  # Manual, API, Bank
    is_active = db.Column(db.Boolean, default=True)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'from_currency': self.from_currency.value if self.from_currency else None,
            'to_currency': self.to_currency.value if self.to_currency else None,
            'exchange_rate': float(self.exchange_rate),
            'rate_date': self.rate_date.isoformat() if self.rate_date else None,
            'source': self.source,
            'is_active': self.is_active,
            'company_id': self.company_id
        })
        return data

# Advanced Chart of Accounts
class ChartOfAccounts(BaseModel):
    """Enhanced chart of accounts model"""
    __tablename__ = 'chart_of_accounts'
    
    # Account Information
    account_code = db.Column(db.String(50), unique=True, nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.Enum(AccountType), nullable=False)
    description = db.Column(db.Text)
    
    # Account Hierarchy
    parent_account_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id'))
    parent_account = relationship("ChartOfAccounts", remote_side=[id])
    child_accounts = relationship("ChartOfAccounts", back_populates="parent_account")
    
    # Account Settings
    is_active = db.Column(db.Boolean, default=True)
    is_system_account = db.Column(db.Boolean, default=False)
    requires_reconciliation = db.Column(db.Boolean, default=False)
    
    # Multi-Currency Support
    base_currency = db.Column(db.Enum(Currency), default=Currency.USD)
    allow_foreign_currency = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    journal_entries = relationship("JournalEntryLine", back_populates="account")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'account_code': self.account_code,
            'account_name': self.account_name,
            'account_type': self.account_type.value if self.account_type else None,
            'description': self.description,
            'parent_account_id': self.parent_account_id,
            'is_active': self.is_active,
            'is_system_account': self.is_system_account,
            'requires_reconciliation': self.requires_reconciliation,
            'base_currency': self.base_currency.value if self.base_currency else None,
            'allow_foreign_currency': self.allow_foreign_currency,
            'company_id': self.company_id
        })
        return data

# Enhanced Journal Entries
class JournalEntry(BaseModel):
    """Enhanced journal entry model"""
    __tablename__ = 'journal_entries'
    
    # Entry Information
    entry_number = db.Column(db.String(50), unique=True, nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    reference = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    # Entry Details
    total_debit = db.Column(db.Numeric(15, 2), default=0.0)
    total_credit = db.Column(db.Numeric(15, 2), default=0.0)
    is_balanced = db.Column(db.Boolean, default=False)
    
    # Multi-Currency Support
    base_currency = db.Column(db.Enum(Currency), default=Currency.USD)
    exchange_rate = db.Column(db.Numeric(15, 6), default=1.0)
    
    # Entry Status
    status = db.Column(db.String(50), default='Draft')  # Draft, Posted, Cancelled
    posted_date = db.Column(db.DateTime)
    posted_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    posted_by = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    entry_lines = relationship("JournalEntryLine", back_populates="journal_entry")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'entry_number': self.entry_number,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'reference': self.reference,
            'description': self.description,
            'total_debit': float(self.total_debit),
            'total_credit': float(self.total_credit),
            'is_balanced': self.is_balanced,
            'base_currency': self.base_currency.value if self.base_currency else None,
            'exchange_rate': float(self.exchange_rate),
            'status': self.status,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'posted_by_id': self.posted_by_id,
            'company_id': self.company_id
        })
        return data

class JournalEntryLine(BaseModel):
    """Journal entry line model"""
    __tablename__ = 'journal_entry_lines'
    
    # Line Information
    line_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    debit_amount = db.Column(db.Numeric(15, 2), default=0.0)
    credit_amount = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Account Association
    account_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id'), nullable=False)
    account = relationship("ChartOfAccounts", back_populates="journal_entries")
    
    # Journal Entry Association
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    journal_entry = relationship("JournalEntry", back_populates="entry_lines")
    
    # Multi-Currency Support
    currency = db.Column(db.Enum(Currency), default=Currency.USD)
    exchange_rate = db.Column(db.Numeric(15, 6), default=1.0)
    base_amount = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'line_number': self.line_number,
            'description': self.description,
            'debit_amount': float(self.debit_amount),
            'credit_amount': float(self.credit_amount),
            'account_id': self.account_id,
            'journal_entry_id': self.journal_entry_id,
            'currency': self.currency.value if self.currency else None,
            'exchange_rate': float(self.exchange_rate),
            'base_amount': float(self.base_amount),
            'company_id': self.company_id
        })
        return data

# Budget Management
class Budget(BaseModel):
    """Budget model"""
    __tablename__ = 'budgets'
    
    # Budget Information
    budget_name = db.Column(db.String(200), nullable=False)
    budget_year = db.Column(db.Integer, nullable=False)
    budget_period = db.Column(db.String(50), default='Annual')  # Annual, Quarterly, Monthly
    description = db.Column(db.Text)
    
    # Budget Status
    status = db.Column(db.Enum(BudgetStatus), default=BudgetStatus.DRAFT)
    approved_date = db.Column(db.Date)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    approved_by = relationship("Employee")
    
    # Budget Totals
    total_budget = db.Column(db.Numeric(15, 2), default=0.0)
    total_actual = db.Column(db.Numeric(15, 2), default=0.0)
    total_variance = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    budget_items = relationship("BudgetItem", back_populates="budget")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'budget_name': self.budget_name,
            'budget_year': self.budget_year,
            'budget_period': self.budget_period,
            'description': self.description,
            'status': self.status.value if self.status else None,
            'approved_date': self.approved_date.isoformat() if self.approved_date else None,
            'approved_by_id': self.approved_by_id,
            'total_budget': float(self.total_budget),
            'total_actual': float(self.total_actual),
            'total_variance': float(self.total_variance),
            'company_id': self.company_id
        })
        return data

class BudgetItem(BaseModel):
    """Budget item model"""
    __tablename__ = 'budget_items'
    
    # Item Information
    account_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id'), nullable=False)
    account = relationship("ChartOfAccounts")
    
    # Budget Association
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    budget = relationship("Budget", back_populates="budget_items")
    
    # Budget Amounts
    budget_amount = db.Column(db.Numeric(15, 2), default=0.0)
    actual_amount = db.Column(db.Numeric(15, 2), default=0.0)
    variance_amount = db.Column(db.Numeric(15, 2), default=0.0)
    variance_percentage = db.Column(db.Numeric(5, 2), default=0.0)
    
    # Period Breakdown
    period_amounts = db.Column(db.JSON)  # Monthly/Quarterly breakdown
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'account_id': self.account_id,
            'budget_id': self.budget_id,
            'budget_amount': float(self.budget_amount),
            'actual_amount': float(self.actual_amount),
            'variance_amount': float(self.variance_amount),
            'variance_percentage': float(self.variance_percentage),
            'period_amounts': self.period_amounts,
            'company_id': self.company_id
        })
        return data

# Investment Management
class Investment(BaseModel):
    """Investment model"""
    __tablename__ = 'investments'
    
    # Investment Information
    investment_name = db.Column(db.String(200), nullable=False)
    investment_type = db.Column(db.Enum(InvestmentType), nullable=False)
    symbol = db.Column(db.String(20))  # Stock symbol, ticker
    description = db.Column(db.Text)
    
    # Investment Details
    purchase_date = db.Column(db.Date)
    purchase_price = db.Column(db.Numeric(15, 4), default=0.0)
    quantity = db.Column(db.Numeric(15, 4), default=0.0)
    total_cost = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Current Values
    current_price = db.Column(db.Numeric(15, 4), default=0.0)
    current_value = db.Column(db.Numeric(15, 2), default=0.0)
    gain_loss = db.Column(db.Numeric(15, 2), default=0.0)
    gain_loss_percentage = db.Column(db.Numeric(5, 2), default=0.0)
    
    # Currency
    currency = db.Column(db.Enum(Currency), default=Currency.USD)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    investment_transactions = relationship("InvestmentTransaction", back_populates="investment")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'investment_name': self.investment_name,
            'investment_type': self.investment_type.value if self.investment_type else None,
            'symbol': self.symbol,
            'description': self.description,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'purchase_price': float(self.purchase_price),
            'quantity': float(self.quantity),
            'total_cost': float(self.total_cost),
            'current_price': float(self.current_price),
            'current_value': float(self.current_value),
            'gain_loss': float(self.gain_loss),
            'gain_loss_percentage': float(self.gain_loss_percentage),
            'currency': self.currency.value if self.currency else None,
            'company_id': self.company_id
        })
        return data

class InvestmentTransaction(BaseModel):
    """Investment transaction model"""
    __tablename__ = 'investment_transactions'
    
    # Transaction Information
    transaction_type = db.Column(db.String(50), nullable=False)  # Buy, Sell, Dividend, Split
    transaction_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Numeric(15, 4), default=0.0)
    price = db.Column(db.Numeric(15, 4), default=0.0)
    amount = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Investment Association
    investment_id = db.Column(db.Integer, db.ForeignKey('investments.id'), nullable=False)
    investment = relationship("Investment", back_populates="investment_transactions")
    
    # Fees and Costs
    commission = db.Column(db.Numeric(15, 2), default=0.0)
    fees = db.Column(db.Numeric(15, 2), default=0.0)
    total_cost = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'transaction_type': self.transaction_type,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'quantity': float(self.quantity),
            'price': float(self.price),
            'amount': float(self.amount),
            'investment_id': self.investment_id,
            'commission': float(self.commission),
            'fees': float(self.fees),
            'total_cost': float(self.total_cost),
            'company_id': self.company_id
        })
        return data

# Cash Flow Management
class CashFlow(BaseModel):
    """Cash flow model"""
    __tablename__ = 'cash_flows'
    
    # Cash Flow Information
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    period_type = db.Column(db.String(50), default='Monthly')  # Daily, Weekly, Monthly, Quarterly, Annual
    
    # Operating Cash Flow
    operating_cash_flow = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Investing Cash Flow
    investing_cash_flow = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Financing Cash Flow
    financing_cash_flow = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Net Cash Flow
    net_cash_flow = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Beginning and Ending Cash
    beginning_cash = db.Column(db.Numeric(15, 2), default=0.0)
    ending_cash = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'period_type': self.period_type,
            'operating_cash_flow': float(self.operating_cash_flow),
            'investing_cash_flow': float(self.investing_cash_flow),
            'financing_cash_flow': float(self.financing_cash_flow),
            'net_cash_flow': float(self.net_cash_flow),
            'beginning_cash': float(self.beginning_cash),
            'ending_cash': float(self.ending_cash),
            'company_id': self.company_id
        })
        return data

# Tax Management
class TaxRate(BaseModel):
    """Tax rate model"""
    __tablename__ = 'tax_rates'
    
    # Tax Information
    tax_name = db.Column(db.String(200), nullable=False)
    tax_type = db.Column(db.String(100), nullable=False)  # Income, Sales, VAT, etc.
    tax_rate = db.Column(db.Numeric(5, 4), nullable=False)  # Rate as decimal (0.15 for 15%)
    
    # Tax Settings
    is_active = db.Column(db.Boolean, default=True)
    effective_date = db.Column(db.Date, default=date.today)
    expiry_date = db.Column(db.Date)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'tax_name': self.tax_name,
            'tax_type': self.tax_type,
            'tax_rate': float(self.tax_rate),
            'is_active': self.is_active,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'company_id': self.company_id
        })
        return data
