# Enhanced CRM Core Models - Core Submodules
# Complete CRM models matching enterprise CRM requirements

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

class LeadStatus(PyEnum):
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    CONVERTED = "Converted"
    LOST = "Lost"

class DealStage(PyEnum):
    PROSPECTING = "Prospecting"
    QUALIFICATION = "Qualification"
    PROPOSAL = "Proposal"
    NEGOTIATION = "Negotiation"
    CLOSED_WON = "Closed Won"
    CLOSED_LOST = "Closed Lost"

class ActivityType(PyEnum):
    CALL = "Call"
    EMAIL = "Email"
    MEETING = "Meeting"
    TASK = "Task"
    NOTE = "Note"

# 1. LEADS: Lead capture, management, and qualification
class Lead(BaseModel):
    """Lead model for CRM - Lead capture, management, and qualification"""
    __tablename__ = 'leads'
    
    # Basic Information
    lead_code = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(200))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    company = db.Column(db.String(200))
    job_title = db.Column(db.String(100))
    website = db.Column(db.String(200))
    
    # Lead Information
    lead_source = db.Column(db.String(100))  # Website, Referral, Cold Call, Social Media
    lead_status = db.Column(db.Enum(LeadStatus), default=LeadStatus.NEW)
    lead_score = db.Column(db.Float, default=0.0)  # AI-powered scoring
    estimated_value = db.Column(db.Float, default=0.0)
    probability = db.Column(db.Float, default=0.0)
    
    # Qualification
    budget = db.Column(db.Float, default=0.0)
    timeline = db.Column(db.String(100))  # Immediate, 1-3 months, 6+ months
    decision_makers = db.Column(db.Integer, default=1)
    pain_points = db.Column(db.Text)
    requirements = db.Column(db.Text)
    
    # Address
    address_line_1 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    
    # Assignment
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    
    # Relationships
    activities = relationship("Activity", back_populates="lead")
    deals = relationship("Deal", back_populates="lead")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'lead_code': self.lead_code,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'company': self.company,
            'job_title': self.job_title,
            'website': self.website,
            'lead_source': self.lead_source,
            'lead_status': self.lead_status.value if self.lead_status else None,
            'lead_score': self.lead_score,
            'estimated_value': self.estimated_value,
            'probability': self.probability,
            'budget': self.budget,
            'timeline': self.timeline,
            'decision_makers': self.decision_makers,
            'pain_points': self.pain_points,
            'requirements': self.requirements,
            'address_line_1': self.address_line_1,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'custom_fields': self.custom_fields,
            'tags': self.tags,
            'notes': self.notes
        })
        return data

# 2. ACCOUNTS: Company/organization management
class Account(BaseModel):
    """Account model for CRM - Company/organization management"""
    __tablename__ = 'accounts'
    
    # Basic Information
    account_code = db.Column(db.String(50), unique=True, nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(50), default='Customer')  # Customer, Prospect, Partner, Competitor
    industry = db.Column(db.String(100))
    website = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Business Information
    annual_revenue = db.Column(db.Float, default=0.0)
    number_of_employees = db.Column(db.Integer, default=0)
    ownership = db.Column(db.String(50))  # Public, Private, Government
    ticker_symbol = db.Column(db.String(20))
    
    # Address
    billing_address = db.Column(db.Text)
    shipping_address = db.Column(db.Text)
    
    # CRM Fields
    account_status = db.Column(db.String(50), default='Active')
    priority = db.Column(db.String(20), default='Medium')
    health_score = db.Column(db.Float, default=0.0)
    
    # Assignment
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    
    # Analytics
    total_deals = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0.0)
    last_activity_date = db.Column(db.DateTime)
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    
    # Relationships
    contacts = relationship("Contact", back_populates="account")
    deals = relationship("Deal", back_populates="account")
    activities = relationship("Activity", back_populates="account")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'account_code': self.account_code,
            'account_name': self.account_name,
            'account_type': self.account_type,
            'industry': self.industry,
            'website': self.website,
            'phone': self.phone,
            'email': self.email,
            'annual_revenue': self.annual_revenue,
            'number_of_employees': self.number_of_employees,
            'ownership': self.ownership,
            'ticker_symbol': self.ticker_symbol,
            'billing_address': self.billing_address,
            'shipping_address': self.shipping_address,
            'account_status': self.account_status,
            'priority': self.priority,
            'health_score': self.health_score,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'total_deals': self.total_deals,
            'total_revenue': self.total_revenue,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'custom_fields': self.custom_fields,
            'tags': self.tags,
            'notes': self.notes
        })
        return data

# 3. CONTACTS: Individual contact management
class Contact(BaseModel):
    """Contact model for CRM - Individual contact management"""
    __tablename__ = 'contacts'
    
    # Basic Information
    contact_code = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(200))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    
    # Professional Information
    job_title = db.Column(db.String(100))
    department = db.Column(db.String(100))
    reporting_to = db.Column(db.String(200))
    
    # Address
    address_line_1 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    
    # CRM Fields
    contact_type = db.Column(db.String(50), default='Primary')  # Primary, Secondary, Emergency
    contact_status = db.Column(db.String(50), default='Active')
    source = db.Column(db.String(100))
    
    # Communication Preferences
    preferred_contact_method = db.Column(db.String(50))  # Email, Phone, SMS
    communication_frequency = db.Column(db.String(50))  # Daily, Weekly, Monthly
    language_preference = db.Column(db.String(10), default='en')
    
    # Assignment
    assigned_to = db.Column(db.String(100))
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    
    # Relationships
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    account = relationship("Account", back_populates="contacts")
    activities = relationship("Activity", back_populates="contact")
    
    def to_dict(self):
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
            'reporting_to': self.reporting_to,
            'address_line_1': self.address_line_1,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'contact_type': self.contact_type,
            'contact_status': self.contact_status,
            'source': self.source,
            'preferred_contact_method': self.preferred_contact_method,
            'communication_frequency': self.communication_frequency,
            'language_preference': self.language_preference,
            'assigned_to': self.assigned_to,
            'account_id': self.account_id,
            'custom_fields': self.custom_fields,
            'tags': self.tags,
            'notes': self.notes
        })
        return data

# 4. DEALS: Opportunity and pipeline management
class Deal(BaseModel):
    """Deal model for CRM - Opportunity and pipeline management"""
    __tablename__ = 'deals'
    
    # Basic Information
    deal_code = db.Column(db.String(50), unique=True, nullable=False)
    deal_name = db.Column(db.String(200), nullable=False)
    deal_stage = db.Column(db.Enum(DealStage), default=DealStage.PROSPECTING)
    deal_value = db.Column(db.Float, default=0.0)
    probability = db.Column(db.Float, default=0.0)
    expected_close_date = db.Column(db.DateTime)
    actual_close_date = db.Column(db.DateTime)
    
    # Deal Information
    deal_type = db.Column(db.String(50))  # New Business, Upsell, Cross-sell, Renewal
    lead_source = db.Column(db.String(100))
    competitor = db.Column(db.String(100))
    next_step = db.Column(db.String(200))
    
    # Financial Information
    currency = db.Column(db.String(3), default='USD')
    discount_percentage = db.Column(db.Float, default=0.0)
    commission_rate = db.Column(db.Float, default=0.0)
    
    # Assignment
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    
    # Relationships
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    account = relationship("Account", back_populates="deals")
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    lead = relationship("Lead", back_populates="deals")
    activities = relationship("Activity", back_populates="deal")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'deal_code': self.deal_code,
            'deal_name': self.deal_name,
            'deal_stage': self.deal_stage.value if self.deal_stage else None,
            'deal_value': self.deal_value,
            'probability': self.probability,
            'expected_close_date': self.expected_close_date.isoformat() if self.expected_close_date else None,
            'actual_close_date': self.actual_close_date.isoformat() if self.actual_close_date else None,
            'deal_type': self.deal_type,
            'lead_source': self.lead_source,
            'competitor': self.competitor,
            'next_step': self.next_step,
            'currency': self.currency,
            'discount_percentage': self.discount_percentage,
            'commission_rate': self.commission_rate,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'account_id': self.account_id,
            'lead_id': self.lead_id,
            'custom_fields': self.custom_fields,
            'tags': self.tags,
            'notes': self.notes
        })
        return data

# 5. SALES FORECASTING: Revenue prediction and planning
class SalesForecast(BaseModel):
    """Sales Forecast model for CRM - Revenue prediction and planning"""
    __tablename__ = 'sales_forecasts'
    
    # Basic Information
    forecast_code = db.Column(db.String(50), unique=True, nullable=False)
    forecast_name = db.Column(db.String(200), nullable=False)
    forecast_period = db.Column(db.String(50))  # Monthly, Quarterly, Annual
    forecast_start_date = db.Column(db.DateTime)
    forecast_end_date = db.Column(db.DateTime)
    
    # Forecast Data
    forecasted_revenue = db.Column(db.Float, default=0.0)
    actual_revenue = db.Column(db.Float, default=0.0)
    variance = db.Column(db.Float, default=0.0)
    confidence_level = db.Column(db.Float, default=0.0)
    
    # Territory and Assignment
    territory = db.Column(db.String(100))
    assigned_to = db.Column(db.String(100))
    
    # Forecast Details
    forecast_method = db.Column(db.String(50))  # AI, Historical, Manual
    forecast_notes = db.Column(db.Text)
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'forecast_code': self.forecast_code,
            'forecast_name': self.forecast_name,
            'forecast_period': self.forecast_period,
            'forecast_start_date': self.forecast_start_date.isoformat() if self.forecast_start_date else None,
            'forecast_end_date': self.forecast_end_date.isoformat() if self.forecast_end_date else None,
            'forecasted_revenue': self.forecasted_revenue,
            'actual_revenue': self.actual_revenue,
            'variance': self.variance,
            'confidence_level': self.confidence_level,
            'territory': self.territory,
            'assigned_to': self.assigned_to,
            'forecast_method': self.forecast_method,
            'forecast_notes': self.forecast_notes,
            'custom_fields': self.custom_fields,
            'tags': self.tags
        })
        return data

# 6. TERRITORY-BASED FORECASTING: Geographic sales planning
class TerritoryForecast(BaseModel):
    """Territory Forecast model for CRM - Geographic sales planning"""
    __tablename__ = 'territory_forecasts'
    
    # Basic Information
    territory_code = db.Column(db.String(50), unique=True, nullable=False)
    territory_name = db.Column(db.String(200), nullable=False)
    territory_type = db.Column(db.String(50))  # Geographic, Industry, Product
    territory_manager = db.Column(db.String(100))
    
    # Geographic Information
    country = db.Column(db.String(100))
    state = db.Column(db.String(100))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    
    # Forecast Data
    forecasted_revenue = db.Column(db.Float, default=0.0)
    actual_revenue = db.Column(db.Float, default=0.0)
    variance = db.Column(db.Float, default=0.0)
    
    # Territory Metrics
    number_of_accounts = db.Column(db.Integer, default=0)
    number_of_deals = db.Column(db.Integer, default=0)
    average_deal_size = db.Column(db.Float, default=0.0)
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'territory_code': self.territory_code,
            'territory_name': self.territory_name,
            'territory_type': self.territory_type,
            'territory_manager': self.territory_manager,
            'country': self.country,
            'state': self.state,
            'city': self.city,
            'postal_code': self.postal_code,
            'forecasted_revenue': self.forecasted_revenue,
            'actual_revenue': self.actual_revenue,
            'variance': self.variance,
            'number_of_accounts': self.number_of_accounts,
            'number_of_deals': self.number_of_deals,
            'average_deal_size': self.average_deal_size,
            'custom_fields': self.custom_fields,
            'tags': self.tags,
            'notes': self.notes
        })
        return data

# 7. MACROS: Automated action sequences
class Macro(BaseModel):
    """Macro model for CRM - Automated action sequences"""
    __tablename__ = 'macros'
    
    # Basic Information
    macro_code = db.Column(db.String(50), unique=True, nullable=False)
    macro_name = db.Column(db.String(200), nullable=False)
    macro_description = db.Column(db.Text)
    macro_type = db.Column(db.String(50))  # Lead, Deal, Contact, Account
    
    # Macro Configuration
    trigger_condition = db.Column(db.Text)  # JSON condition
    actions = db.Column(db.JSON)  # List of actions to execute
    is_active = db.Column(db.Boolean, default=True)
    
    # Execution
    execution_count = db.Column(db.Integer, default=0)
    last_executed = db.Column(db.DateTime)
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'macro_code': self.macro_code,
            'macro_name': self.macro_name,
            'macro_description': self.macro_description,
            'macro_type': self.macro_type,
            'trigger_condition': self.trigger_condition,
            'actions': self.actions,
            'is_active': self.is_active,
            'execution_count': self.execution_count,
            'last_executed': self.last_executed.isoformat() if self.last_executed else None,
            'custom_fields': self.custom_fields,
            'tags': self.tags
        })
        return data

# 8. FEEDS: Activity streams and updates
class Feed(BaseModel):
    """Feed model for CRM - Activity streams and updates"""
    __tablename__ = 'feeds'
    
    # Basic Information
    feed_type = db.Column(db.String(50))  # Activity, Update, Notification
    feed_title = db.Column(db.String(200))
    feed_description = db.Column(db.Text)
    
    # Feed Data
    feed_data = db.Column(db.JSON)
    feed_metadata = db.Column(db.JSON)
    
    # Assignment
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_important = db.Column(db.Boolean, default=False)
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'feed_type': self.feed_type,
            'feed_title': self.feed_title,
            'feed_description': self.feed_description,
            'feed_data': self.feed_data,
            'feed_metadata': self.feed_metadata,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'is_read': self.is_read,
            'is_important': self.is_important,
            'custom_fields': self.custom_fields,
            'tags': self.tags
        })
        return data

# 9. SALES SIGNALS: Intelligent sales insights
class SalesSignal(BaseModel):
    """Sales Signal model for CRM - Intelligent sales insights"""
    __tablename__ = 'sales_signals'
    
    # Basic Information
    signal_code = db.Column(db.String(50), unique=True, nullable=False)
    signal_name = db.Column(db.String(200), nullable=False)
    signal_type = db.Column(db.String(50))  # Lead, Deal, Account, Contact
    signal_category = db.Column(db.String(50))  # Positive, Negative, Neutral
    
    # Signal Data
    signal_data = db.Column(db.JSON)
    signal_metadata = db.Column(db.JSON)
    confidence_score = db.Column(db.Float, default=0.0)
    
    # Assignment
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    
    # Status
    is_processed = db.Column(db.Boolean, default=False)
    is_important = db.Column(db.Boolean, default=False)
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'signal_code': self.signal_code,
            'signal_name': self.signal_name,
            'signal_type': self.signal_type,
            'signal_category': self.signal_category,
            'signal_data': self.signal_data,
            'signal_metadata': self.signal_metadata,
            'confidence_score': self.confidence_score,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'is_processed': self.is_processed,
            'is_important': self.is_important,
            'custom_fields': self.custom_fields,
            'tags': self.tags
        })
        return data

# 10. DOCUMENT LIBRARY: Sales document management
class Document(BaseModel):
    """Document model for CRM - Sales document management"""
    __tablename__ = 'documents'
    
    # Basic Information
    document_code = db.Column(db.String(50), unique=True, nullable=False)
    document_name = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(50))  # Proposal, Contract, Presentation, etc.
    document_category = db.Column(db.String(50))
    
    # Document Information
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    version = db.Column(db.String(20), default='1.0')
    
    # Access Control
    is_public = db.Column(db.Boolean, default=False)
    access_level = db.Column(db.String(50), default='Private')
    
    # Assignment
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'document_code': self.document_code,
            'document_name': self.document_name,
            'document_type': self.document_type,
            'document_category': self.document_category,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'version': self.version,
            'is_public': self.is_public,
            'access_level': self.access_level,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'custom_fields': self.custom_fields,
            'tags': self.tags,
            'notes': self.notes
        })
        return data

# 11. ACTIVITIES: Task and event management
class Activity(BaseModel):
    """Activity model for CRM - Task and event management"""
    __tablename__ = 'activities'
    
    # Basic Information
    activity_code = db.Column(db.String(50), unique=True, nullable=False)
    activity_title = db.Column(db.String(200), nullable=False)
    activity_type = db.Column(db.Enum(ActivityType), default=ActivityType.TASK)
    activity_description = db.Column(db.Text)
    
    # Scheduling
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # in minutes
    
    # Status
    activity_status = db.Column(db.String(50), default='Not Started')  # Not Started, In Progress, Completed, Cancelled
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Urgent
    completion_percentage = db.Column(db.Float, default=0.0)
    
    # Assignment
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    
    # Relationships
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    lead = relationship("Lead", back_populates="activities")
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    account = relationship("Account", back_populates="activities")
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    contact = relationship("Contact", back_populates="activities")
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'))
    deal = relationship("Deal", back_populates="activities")
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'activity_code': self.activity_code,
            'activity_title': self.activity_title,
            'activity_type': self.activity_type.value if self.activity_type else None,
            'activity_description': self.activity_description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'duration': self.duration,
            'activity_status': self.activity_status,
            'priority': self.priority,
            'completion_percentage': self.completion_percentage,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'lead_id': self.lead_id,
            'account_id': self.account_id,
            'contact_id': self.contact_id,
            'deal_id': self.deal_id,
            'custom_fields': self.custom_fields,
            'tags': self.tags,
            'notes': self.notes
        })
        return data

# 12. REMINDERS: Automated notifications
class Reminder(BaseModel):
    """Reminder model for CRM - Automated notifications"""
    __tablename__ = 'reminders'
    
    # Basic Information
    reminder_code = db.Column(db.String(50), unique=True, nullable=False)
    reminder_title = db.Column(db.String(200), nullable=False)
    reminder_description = db.Column(db.Text)
    reminder_type = db.Column(db.String(50))  # Email, SMS, Push, In-app
    
    # Scheduling
    reminder_date = db.Column(db.DateTime)
    reminder_frequency = db.Column(db.String(50))  # Once, Daily, Weekly, Monthly
    is_recurring = db.Column(db.Boolean, default=False)
    
    # Status
    reminder_status = db.Column(db.String(50), default='Pending')  # Pending, Sent, Failed
    is_active = db.Column(db.Boolean, default=True)
    
    # Assignment
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'reminder_code': self.reminder_code,
            'reminder_title': self.reminder_title,
            'reminder_description': self.reminder_description,
            'reminder_type': self.reminder_type,
            'reminder_date': self.reminder_date.isoformat() if self.reminder_date else None,
            'reminder_frequency': self.reminder_frequency,
            'is_recurring': self.is_recurring,
            'reminder_status': self.reminder_status,
            'is_active': self.is_active,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'custom_fields': self.custom_fields,
            'tags': self.tags
        })
        return data

# 13. RECURRING ACTIVITIES: Scheduled recurring tasks
class RecurringActivity(BaseModel):
    """Recurring Activity model for CRM - Scheduled recurring tasks"""
    __tablename__ = 'recurring_activities'
    
    # Basic Information
    recurring_activity_code = db.Column(db.String(50), unique=True, nullable=False)
    recurring_activity_name = db.Column(db.String(200), nullable=False)
    recurring_activity_description = db.Column(db.Text)
    
    # Recurrence Pattern
    recurrence_pattern = db.Column(db.String(50))  # Daily, Weekly, Monthly, Yearly
    recurrence_interval = db.Column(db.Integer, default=1)
    recurrence_days = db.Column(db.JSON)  # Days of week for weekly recurrence
    recurrence_date = db.Column(db.Integer)  # Day of month for monthly recurrence
    
    # Scheduling
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    next_occurrence = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    total_occurrences = db.Column(db.Integer, default=0)
    
    # Assignment
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'recurring_activity_code': self.recurring_activity_code,
            'recurring_activity_name': self.recurring_activity_name,
            'recurring_activity_description': self.recurring_activity_description,
            'recurrence_pattern': self.recurrence_pattern,
            'recurrence_interval': self.recurrence_interval,
            'recurrence_days': self.recurrence_days,
            'recurrence_date': self.recurrence_date,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'next_occurrence': self.next_occurrence.isoformat() if self.next_occurrence else None,
            'is_active': self.is_active,
            'total_occurrences': self.total_occurrences,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'custom_fields': self.custom_fields,
            'tags': self.tags
        })
        return data

# 14. CALENDAR BOOKING: Meeting scheduling
class CalendarBooking(BaseModel):
    """Calendar Booking model for CRM - Meeting scheduling"""
    __tablename__ = 'calendar_bookings'
    
    # Basic Information
    booking_code = db.Column(db.String(50), unique=True, nullable=False)
    booking_title = db.Column(db.String(200), nullable=False)
    booking_description = db.Column(db.Text)
    booking_type = db.Column(db.String(50))  # Meeting, Call, Demo, Presentation
    
    # Scheduling
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # in minutes
    timezone = db.Column(db.String(50))
    
    # Location
    location = db.Column(db.String(200))
    meeting_url = db.Column(db.String(500))
    meeting_id = db.Column(db.String(100))
    
    # Participants
    organizer = db.Column(db.String(100))
    attendees = db.Column(db.JSON)  # List of attendees
    required_attendees = db.Column(db.JSON)
    optional_attendees = db.Column(db.JSON)
    
    # Status
    booking_status = db.Column(db.String(50), default='Scheduled')  # Scheduled, Confirmed, Cancelled, Completed
    is_recurring = db.Column(db.Boolean, default=False)
    
    # Assignment
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'booking_code': self.booking_code,
            'booking_title': self.booking_title,
            'booking_description': self.booking_description,
            'booking_type': self.booking_type,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'timezone': self.timezone,
            'location': self.location,
            'meeting_url': self.meeting_url,
            'meeting_id': self.meeting_id,
            'organizer': self.organizer,
            'attendees': self.attendees,
            'required_attendees': self.required_attendees,
            'optional_attendees': self.optional_attendees,
            'booking_status': self.booking_status,
            'is_recurring': self.is_recurring,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'custom_fields': self.custom_fields,
            'tags': self.tags,
            'notes': self.notes
        })
        return data

# 15. MULTIPLE CURRENCIES: International sales support
class Currency(BaseModel):
    """Currency model for CRM - International sales support"""
    __tablename__ = 'currencies'
    
    # Basic Information
    currency_code = db.Column(db.String(3), unique=True, nullable=False)  # USD, EUR, GBP, etc.
    currency_name = db.Column(db.String(100), nullable=False)
    currency_symbol = db.Column(db.String(10))
    
    # Exchange Rates
    base_currency = db.Column(db.String(3), default='USD')
    exchange_rate = db.Column(db.Float, default=1.0)
    last_updated = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_base_currency = db.Column(db.Boolean, default=False)
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'currency_code': self.currency_code,
            'currency_name': self.currency_name,
            'currency_symbol': self.currency_symbol,
            'base_currency': self.base_currency,
            'exchange_rate': self.exchange_rate,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'is_active': self.is_active,
            'is_base_currency': self.is_base_currency,
            'custom_fields': self.custom_fields,
            'tags': self.tags
        })
        return data

# 16. SOCIAL INTEGRATION: Social media connectivity
class SocialIntegration(BaseModel):
    """Social Integration model for CRM - Social media connectivity"""
    __tablename__ = 'social_integrations'
    
    # Basic Information
    integration_code = db.Column(db.String(50), unique=True, nullable=False)
    integration_name = db.Column(db.String(200), nullable=False)
    integration_type = db.Column(db.String(50))  # LinkedIn, Twitter, Facebook, Instagram
    
    # Integration Configuration
    api_key = db.Column(db.String(500))
    api_secret = db.Column(db.String(500))
    access_token = db.Column(db.String(500))
    refresh_token = db.Column(db.String(500))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_sync = db.Column(db.DateTime)
    sync_frequency = db.Column(db.String(50))  # Real-time, Hourly, Daily
    
    # Assignment
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'integration_code': self.integration_code,
            'integration_name': self.integration_name,
            'integration_type': self.integration_type,
            'is_active': self.is_active,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'sync_frequency': self.sync_frequency,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'custom_fields': self.custom_fields,
            'tags': self.tags
        })
        return data

# 17. SCORING RULES: Lead/deal scoring
class ScoringRule(BaseModel):
    """Scoring Rule model for CRM - Lead/deal scoring"""
    __tablename__ = 'scoring_rules'
    
    # Basic Information
    rule_code = db.Column(db.String(50), unique=True, nullable=False)
    rule_name = db.Column(db.String(200), nullable=False)
    rule_description = db.Column(db.Text)
    rule_type = db.Column(db.String(50))  # Lead, Deal, Contact, Account
    
    # Rule Configuration
    rule_conditions = db.Column(db.JSON)  # List of conditions
    rule_actions = db.Column(db.JSON)  # List of actions
    rule_score = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    execution_count = db.Column(db.Integer, default=0)
    last_executed = db.Column(db.DateTime)
    
    # Assignment
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'rule_code': self.rule_code,
            'rule_name': self.rule_name,
            'rule_description': self.rule_description,
            'rule_type': self.rule_type,
            'rule_conditions': self.rule_conditions,
            'rule_actions': self.rule_actions,
            'rule_score': self.rule_score,
            'is_active': self.is_active,
            'execution_count': self.execution_count,
            'last_executed': self.last_executed.isoformat() if self.last_executed else None,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'custom_fields': self.custom_fields,
            'tags': self.tags
        })
        return data

# 18. MULTIPLE SCORING RULES: Advanced scoring systems
class MultipleScoringRule(BaseModel):
    """Multiple Scoring Rule model for CRM - Advanced scoring systems"""
    __tablename__ = 'multiple_scoring_rules'
    
    # Basic Information
    rule_set_code = db.Column(db.String(50), unique=True, nullable=False)
    rule_set_name = db.Column(db.String(200), nullable=False)
    rule_set_description = db.Column(db.Text)
    rule_set_type = db.Column(db.String(50))  # Lead, Deal, Contact, Account
    
    # Rule Set Configuration
    rule_set_rules = db.Column(db.JSON)  # List of scoring rules
    rule_set_weights = db.Column(db.JSON)  # Weights for each rule
    rule_set_threshold = db.Column(db.Float, default=0.0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    execution_count = db.Column(db.Integer, default=0)
    last_executed = db.Column(db.DateTime)
    
    # Assignment
    assigned_to = db.Column(db.String(100))
    territory = db.Column(db.String(100))
    
    # Custom Fields
    custom_fields = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'rule_set_code': self.rule_set_code,
            'rule_set_name': self.rule_set_name,
            'rule_set_description': self.rule_set_description,
            'rule_set_type': self.rule_set_type,
            'rule_set_rules': self.rule_set_rules,
            'rule_set_weights': self.rule_set_weights,
            'rule_set_threshold': self.rule_set_threshold,
            'is_active': self.is_active,
            'execution_count': self.execution_count,
            'last_executed': self.last_executed.isoformat() if self.last_executed else None,
            'assigned_to': self.assigned_to,
            'territory': self.territory,
            'custom_fields': self.custom_fields,
            'tags': self.tags
        })
        return data
