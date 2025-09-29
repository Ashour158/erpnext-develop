# Finance Models - Complete Financial Management
# Advanced accounting models without Frappe dependencies

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# Enums
class AccountType(enum.Enum):
    ASSET = "Asset"
    LIABILITY = "Liability"
    EQUITY = "Equity"
    INCOME = "Income"
    EXPENSE = "Expense"

class TransactionType(enum.Enum):
    DEBIT = "Debit"
    CREDIT = "Credit"

class InvoiceStatus(enum.Enum):
    DRAFT = "Draft"
    SENT = "Sent"
    PAID = "Paid"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"

class PaymentStatus(enum.Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"

# Company Model
class Company(BaseModel):
    """Company model for multi-tenant support"""
    __tablename__ = 'companies'
    
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    legal_name = db.Column(db.String(200))
    tax_id = db.Column(db.String(50))
    registration_number = db.Column(db.String(50))
    
    # Contact Information
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    
    # Address
    address_line_1 = db.Column(db.String(200))
    address_line_2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Financial Settings
    base_currency = db.Column(db.String(3), default='USD')
    fiscal_year_start = db.Column(db.String(10), default='01-01')
    fiscal_year_end = db.Column(db.String(10), default='12-31')
    
    # Company Settings
    logo = db.Column(db.String(255))
    settings = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'name': self.name,
            'code': self.code,
            'legal_name': self.legal_name,
            'tax_id': self.tax_id,
            'registration_number': self.registration_number,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'base_currency': self.base_currency,
            'fiscal_year_start': self.fiscal_year_start,
            'fiscal_year_end': self.fiscal_year_end,
            'logo': self.logo,
            'settings': self.settings,
            'is_active': self.is_active
        })
        return data

# Chart of Accounts
class ChartOfAccounts(BaseModel):
    """Chart of Accounts model"""
    __tablename__ = 'chart_of_accounts'
    
    account_code = db.Column(db.String(50), unique=True, nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.Enum(AccountType), nullable=False)
    parent_account_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id'))
    
    # Account Details
    description = db.Column(db.Text)
    is_group = db.Column(db.Boolean, default=False)
    is_frozen = db.Column(db.Boolean, default=False)
    allow_negative_balance = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Parent-Child Relationship
    parent_account = relationship("ChartOfAccounts", remote_side=[id])
    child_accounts = relationship("ChartOfAccounts", back_populates="parent_account")
    
    # Journal Entry Lines
    journal_entry_lines = relationship("JournalEntryLine", back_populates="account")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'account_code': self.account_code,
            'account_name': self.account_name,
            'account_type': self.account_type.value if self.account_type else None,
            'parent_account_id': self.parent_account_id,
            'description': self.description,
            'is_group': self.is_group,
            'is_frozen': self.is_frozen,
            'allow_negative_balance': self.allow_negative_balance,
            'company_id': self.company_id
        })
        return data

# Journal Entry
class JournalEntry(BaseModel):
    """Journal Entry model"""
    __tablename__ = 'journal_entries'
    
    entry_number = db.Column(db.String(50), unique=True, nullable=False)
    entry_date = db.Column(db.DateTime, nullable=False)
    reference = db.Column(db.String(100))
    description = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Status
    status = db.Column(db.String(20), default='Draft')  # Draft, Posted, Cancelled
    total_debit = db.Column(db.Float, default=0.0)
    total_credit = db.Column(db.Float, default=0.0)
    
    # Relationships
    lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'entry_number': self.entry_number,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'reference': self.reference,
            'description': self.description,
            'company_id': self.company_id,
            'status': self.status,
            'total_debit': self.total_debit,
            'total_credit': self.total_credit,
            'lines': [line.to_dict() for line in self.lines] if self.lines else []
        })
        return data

# Journal Entry Line
class JournalEntryLine(BaseModel):
    """Journal Entry Line model"""
    __tablename__ = 'journal_entry_lines'
    
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    journal_entry = relationship("JournalEntry", back_populates="lines")
    
    account_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id'), nullable=False)
    account = relationship("ChartOfAccounts", back_populates="journal_entry_lines")
    
    description = db.Column(db.Text)
    debit_amount = db.Column(db.Float, default=0.0)
    credit_amount = db.Column(db.Float, default=0.0)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'journal_entry_id': self.journal_entry_id,
            'account_id': self.account_id,
            'description': self.description,
            'debit_amount': self.debit_amount,
            'credit_amount': self.credit_amount
        })
        return data

# Invoice Model
class Invoice(BaseModel):
    """Invoice model"""
    __tablename__ = 'invoices'
    
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime)
    
    # Customer Information
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer_name = db.Column(db.String(200))
    customer_email = db.Column(db.String(120))
    customer_address = db.Column(db.Text)
    
    # Invoice Details
    subtotal = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    paid_amount = db.Column(db.Float, default=0.0)
    balance_amount = db.Column(db.Float, default=0.0)
    
    # Status and Terms
    status = db.Column(db.Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    payment_terms = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Currency
    currency = db.Column(db.String(3), default='USD')
    exchange_rate = db.Column(db.Float, default=1.0)
    
    # Relationships
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'invoice_number': self.invoice_number,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_address': self.customer_address,
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'discount_amount': self.discount_amount,
            'total_amount': self.total_amount,
            'paid_amount': self.paid_amount,
            'balance_amount': self.balance_amount,
            'status': self.status.value if self.status else None,
            'payment_terms': self.payment_terms,
            'notes': self.notes,
            'company_id': self.company_id,
            'currency': self.currency,
            'exchange_rate': self.exchange_rate,
            'lines': [line.to_dict() for line in self.lines] if self.lines else [],
            'payments': [payment.to_dict() for payment in self.payments] if self.payments else []
        })
        return data

# Invoice Line
class InvoiceLine(BaseModel):
    """Invoice Line model"""
    __tablename__ = 'invoice_lines'
    
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    invoice = relationship("Invoice", back_populates="lines")
    
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Float, default=1.0)
    unit_price = db.Column(db.Float, default=0.0)
    discount_percentage = db.Column(db.Float, default=0.0)
    tax_percentage = db.Column(db.Float, default=0.0)
    line_total = db.Column(db.Float, default=0.0)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'invoice_id': self.invoice_id,
            'item_name': self.item_name,
            'description': self.description,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'discount_percentage': self.discount_percentage,
            'tax_percentage': self.tax_percentage,
            'line_total': self.line_total
        })
        return data

# Payment Model
class Payment(BaseModel):
    """Payment model"""
    __tablename__ = 'payments'
    
    payment_number = db.Column(db.String(50), unique=True, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    # Payment Details
    payment_method = db.Column(db.String(50))  # Cash, Bank Transfer, Credit Card, etc.
    reference = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    # Status
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Relationships
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    invoice = relationship("Invoice", back_populates="payments")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'payment_number': self.payment_number,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'reference': self.reference,
            'notes': self.notes,
            'status': self.status.value if self.status else None,
            'invoice_id': self.invoice_id,
            'company_id': self.company_id
        })
        return data

# Financial Statement Model
class FinancialStatement(BaseModel):
    """Financial Statement model"""
    __tablename__ = 'financial_statements'
    
    statement_type = db.Column(db.String(50), nullable=False)  # P&L, Balance Sheet, Cash Flow
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    
    # Statement Data
    statement_data = db.Column(db.JSON)
    total_revenue = db.Column(db.Float, default=0.0)
    total_expenses = db.Column(db.Float, default=0.0)
    net_income = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'statement_type': self.statement_type,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'statement_data': self.statement_data,
            'total_revenue': self.total_revenue,
            'total_expenses': self.total_expenses,
            'net_income': self.net_income,
            'company_id': self.company_id
        })
        return data

# Budget Model
class Budget(BaseModel):
    """Budget model"""
    __tablename__ = 'budgets'
    
    budget_name = db.Column(db.String(200), nullable=False)
    budget_period = db.Column(db.String(50))  # Monthly, Quarterly, Yearly
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    
    # Budget Data
    budget_data = db.Column(db.JSON)
    total_budget = db.Column(db.Float, default=0.0)
    actual_spent = db.Column(db.Float, default=0.0)
    variance = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'budget_name': self.budget_name,
            'budget_period': self.budget_period,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'budget_data': self.budget_data,
            'total_budget': self.total_budget,
            'actual_spent': self.actual_spent,
            'variance': self.variance,
            'company_id': self.company_id
        })
        return data

# Currency Model
class Currency(BaseModel):
    """Currency model"""
    __tablename__ = 'currencies'
    
    currency_code = db.Column(db.String(3), unique=True, nullable=False)
    currency_name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(10))
    exchange_rate = db.Column(db.Float, default=1.0)
    is_base_currency = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'currency_code': self.currency_code,
            'currency_name': self.currency_name,
            'symbol': self.symbol,
            'exchange_rate': self.exchange_rate,
            'is_base_currency': self.is_base_currency,
            'is_active': self.is_active
        })
        return data

# Bank Account Model
class BankAccount(BaseModel):
    """Bank Account model"""
    __tablename__ = 'bank_accounts'
    
    account_name = db.Column(db.String(200), nullable=False)
    account_number = db.Column(db.String(50))
    bank_name = db.Column(db.String(200))
    bank_code = db.Column(db.String(50))
    routing_number = db.Column(db.String(50))
    
    # Account Details
    account_type = db.Column(db.String(50))  # Checking, Savings, etc.
    currency = db.Column(db.String(3), default='USD')
    opening_balance = db.Column(db.Float, default=0.0)
    current_balance = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'account_name': self.account_name,
            'account_number': self.account_number,
            'bank_name': self.bank_name,
            'bank_code': self.bank_code,
            'routing_number': self.routing_number,
            'account_type': self.account_type,
            'currency': self.currency,
            'opening_balance': self.opening_balance,
            'current_balance': self.current_balance,
            'company_id': self.company_id
        })
        return data
