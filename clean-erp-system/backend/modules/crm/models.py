# CRM Models - Customer Relationship Management
# Complete CRM data models without Frappe dependencies

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Customer(BaseModel):
    """Customer model for CRM"""
    __tablename__ = 'customers'
    
    # Basic Information
    customer_code = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_type = db.Column(db.String(50), default='Individual')  # Individual, Company
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    
    # Address Information
    address_line_1 = db.Column(db.String(200))
    address_line_2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Business Information
    company_name = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    website = db.Column(db.String(200))
    tax_id = db.Column(db.String(50))
    
    # CRM Fields
    customer_group = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    sales_person = db.Column(db.String(100))
    credit_limit = db.Column(db.Float, default=0.0)
    payment_terms = db.Column(db.String(100))
    
    # Status and Priority
    status = db.Column(db.String(50), default='Active')  # Active, Inactive, Suspended
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High
    health_score = db.Column(db.Float, default=0.0)
    
    # Analytics
    total_orders = db.Column(db.Integer, default=0)
    total_sales = db.Column(db.Float, default=0.0)
    last_order_date = db.Column(db.DateTime)
    last_contact_date = db.Column(db.DateTime)
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    
    # Relationships
    contacts = relationship("Contact", back_populates="customer")
    opportunities = relationship("Opportunity", back_populates="customer")
    accounts = relationship("Account", back_populates="customer")
    
    def to_dict(self):
        """Convert customer to dictionary"""
        data = super().to_dict()
        data.update({
            'customer_code': self.customer_code,
            'customer_name': self.customer_name,
            'customer_type': self.customer_type,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'company_name': self.company_name,
            'industry': self.industry,
            'website': self.website,
            'tax_id': self.tax_id,
            'customer_group': self.customer_group,
            'territory': self.territory,
            'sales_person': self.sales_person,
            'credit_limit': self.credit_limit,
            'payment_terms': self.payment_terms,
            'status': self.status,
            'priority': self.priority,
            'health_score': self.health_score,
            'total_orders': self.total_orders,
            'total_sales': self.total_sales,
            'last_order_date': self.last_order_date.isoformat() if self.last_order_date else None,
            'last_contact_date': self.last_contact_date.isoformat() if self.last_contact_date else None,
            'custom_fields': self.custom_fields,
            'tags': self.tags,
            'notes': self.notes
        })
        return data

class Contact(BaseModel):
    """Contact model for CRM"""
    __tablename__ = 'contacts'
    
    # Basic Information
    contact_code = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(200))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    
    # Professional Information
    job_title = db.Column(db.String(100))
    department = db.Column(db.String(100))
    company = db.Column(db.String(200))
    
    # Address Information
    address_line_1 = db.Column(db.String(200))
    address_line_2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # CRM Fields
    contact_type = db.Column(db.String(50), default='Primary')  # Primary, Secondary, Emergency
    status = db.Column(db.String(50), default='Active')
    source = db.Column(db.String(100))  # Website, Referral, Cold Call, etc.
    lead_source = db.Column(db.String(100))
    
    # Relationships
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="contacts")
    
    # Communication Preferences
    preferred_contact_method = db.Column(db.String(50))  # Email, Phone, SMS
    communication_frequency = db.Column(db.String(50))  # Daily, Weekly, Monthly
    language_preference = db.Column(db.String(10), default='en')
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        """Convert contact to dictionary"""
        data = super().to_dict()
        data.update({
            'contact_code': self.contact_code,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'job_title': self.job_title,
            'department': self.department,
            'company': self.company,
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'contact_type': self.contact_type,
            'status': self.status,
            'source': self.source,
            'lead_source': self.lead_source,
            'customer_id': self.customer_id,
            'preferred_contact_method': self.preferred_contact_method,
            'communication_frequency': self.communication_frequency,
            'language_preference': self.language_preference,
            'custom_fields': self.custom_fields,
            'tags': self.tags,
            'notes': self.notes
        })
        return data

class Lead(BaseModel):
    """Lead model for CRM"""
    __tablename__ = 'leads'
    
    # Basic Information
    lead_code = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(200))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(200))
    job_title = db.Column(db.String(100))
    
    # Lead Information
    lead_source = db.Column(db.String(100))  # Website, Referral, Cold Call, etc.
    lead_status = db.Column(db.String(50), default='New')  # New, Contacted, Qualified, Converted, Lost
    lead_score = db.Column(db.Float, default=0.0)
    estimated_value = db.Column(db.Float, default=0.0)
    
    # Address Information
    address_line_1 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    
    # CRM Fields
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        """Convert lead to dictionary"""
        data = super().to_dict()
        data.update({
            'lead_code': self.lead_code,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'job_title': self.job_title,
            'lead_source': self.lead_source,
            'lead_status': self.lead_status,
            'lead_score': self.lead_score,
            'estimated_value': self.estimated_value,
            'address_line_1': self.address_line_1,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'industry': self.industry,
            'custom_fields': self.custom_fields,
            'tags': self.tags,
            'notes': self.notes
        })
        return data

class Opportunity(BaseModel):
    """Opportunity model for CRM"""
    __tablename__ = 'opportunities'
    
    # Basic Information
    opportunity_code = db.Column(db.String(50), unique=True, nullable=False)
    opportunity_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Opportunity Details
    stage = db.Column(db.String(50), default='Prospecting')  # Prospecting, Qualification, Proposal, Negotiation, Closed Won, Closed Lost
    probability = db.Column(db.Float, default=0.0)  # 0-100%
    expected_value = db.Column(db.Float, default=0.0)
    actual_value = db.Column(db.Float, default=0.0)
    
    # Dates
    expected_close_date = db.Column(db.DateTime)
    actual_close_date = db.Column(db.DateTime)
    
    # Relationships
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="opportunities")
    
    # CRM Fields
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    source = db.Column(db.String(100))
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        """Convert opportunity to dictionary"""
        data = super().to_dict()
        data.update({
            'opportunity_code': self.opportunity_code,
            'opportunity_name': self.opportunity_name,
            'description': self.description,
            'stage': self.stage,
            'probability': self.probability,
            'expected_value': self.expected_value,
            'actual_value': self.actual_value,
            'expected_close_date': self.expected_close_date.isoformat() if self.expected_close_date else None,
            'actual_close_date': self.actual_close_date.isoformat() if self.actual_close_date else None,
            'customer_id': self.customer_id,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'source': self.source,
            'custom_fields': self.custom_fields,
            'tags': self.tags,
            'notes': self.notes
        })
        return data

class Account(BaseModel):
    """Account model for CRM"""
    __tablename__ = 'accounts'
    
    # Basic Information
    account_code = db.Column(db.String(50), unique=True, nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(50), default='Customer')  # Customer, Vendor, Partner
    
    # Contact Information
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    
    # Address Information
    address_line_1 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    
    # Business Information
    industry = db.Column(db.String(100))
    company_size = db.Column(db.String(50))
    annual_revenue = db.Column(db.Float, default=0.0)
    
    # CRM Fields
    status = db.Column(db.String(50), default='Active')
    priority = db.Column(db.String(20), default='Medium')
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    
    # Relationships
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="accounts")
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        """Convert account to dictionary"""
        data = super().to_dict()
        data.update({
            'account_code': self.account_code,
            'account_name': self.account_name,
            'account_type': self.account_type,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'address_line_1': self.address_line_1,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'industry': self.industry,
            'company_size': self.company_size,
            'annual_revenue': self.annual_revenue,
            'status': self.status,
            'priority': self.priority,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'customer_id': self.customer_id,
            'custom_fields': self.custom_fields,
            'tags': self.tags,
            'notes': self.notes
        })
        return data
