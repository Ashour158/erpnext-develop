# Advanced CRM Models
# Enhanced CRM functionality with sales pipeline, marketing automation, and customer service

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

class PipelineStage(enum.Enum):
    LEAD = "Lead"
    QUALIFIED = "Qualified"
    PROPOSAL = "Proposal"
    NEGOTIATION = "Negotiation"
    CLOSED_WON = "Closed Won"
    CLOSED_LOST = "Closed Lost"

class LeadSource(enum.Enum):
    WEBSITE = "Website"
    REFERRAL = "Referral"
    SOCIAL_MEDIA = "Social Media"
    EMAIL_CAMPAIGN = "Email Campaign"
    TRADE_SHOW = "Trade Show"
    ADVERTISING = "Advertising"
    OTHER = "Other"

class CampaignStatus(enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class TicketPriority(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class TicketStatus(enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    PENDING = "Pending"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

# Sales Pipeline Models
class SalesPipeline(BaseModel):
    """Sales pipeline model"""
    __tablename__ = 'sales_pipelines'
    
    # Pipeline Information
    pipeline_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Pipeline Configuration
    stages = db.Column(db.JSON)  # Pipeline stages configuration
    stage_probabilities = db.Column(db.JSON)  # Stage success probabilities
    stage_durations = db.Column(db.JSON)  # Average stage durations
    
    # Pipeline Settings
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    opportunities = relationship("Opportunity", back_populates="pipeline")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'pipeline_name': self.pipeline_name,
            'description': self.description,
            'stages': self.stages,
            'stage_probabilities': self.stage_probabilities,
            'stage_durations': self.stage_durations,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'company_id': self.company_id
        })
        return data

class Opportunity(BaseModel):
    """Enhanced opportunity model"""
    __tablename__ = 'opportunities'
    
    # Opportunity Information
    opportunity_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Customer Information
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = relationship("Customer")
    
    # Sales Information
    expected_revenue = db.Column(db.Float, default=0.0)
    probability = db.Column(db.Float, default=0.0)
    weighted_revenue = db.Column(db.Float, default=0.0)
    expected_close_date = db.Column(db.Date)
    actual_close_date = db.Column(db.Date)
    
    # Pipeline Information
    pipeline_id = db.Column(db.Integer, db.ForeignKey('sales_pipelines.id'))
    pipeline = relationship("SalesPipeline", back_populates="opportunities")
    current_stage = db.Column(db.Enum(PipelineStage), default=PipelineStage.LEAD)
    
    # Sales Team
    sales_rep_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    sales_rep = relationship("Employee")
    sales_team = db.Column(db.JSON)  # Additional team members
    
    # Lead Information
    lead_source = db.Column(db.Enum(LeadSource))
    lead_score = db.Column(db.Integer, default=0)
    lead_qualification = db.Column(db.JSON)  # Qualification criteria
    
    # Competition
    competitors = db.Column(db.JSON)  # Competitor information
    competitive_advantages = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    activities = relationship("SalesActivity", back_populates="opportunity")
    quotes = relationship("Quote", back_populates="opportunity")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'opportunity_name': self.opportunity_name,
            'description': self.description,
            'customer_id': self.customer_id,
            'expected_revenue': self.expected_revenue,
            'probability': self.probability,
            'weighted_revenue': self.weighted_revenue,
            'expected_close_date': self.expected_close_date.isoformat() if self.expected_close_date else None,
            'actual_close_date': self.actual_close_date.isoformat() if self.actual_close_date else None,
            'pipeline_id': self.pipeline_id,
            'current_stage': self.current_stage.value if self.current_stage else None,
            'sales_rep_id': self.sales_rep_id,
            'sales_team': self.sales_team,
            'lead_source': self.lead_source.value if self.lead_source else None,
            'lead_score': self.lead_score,
            'lead_qualification': self.lead_qualification,
            'competitors': self.competitors,
            'competitive_advantages': self.competitive_advantages,
            'company_id': self.company_id
        })
        return data

class SalesActivity(BaseModel):
    """Sales activity model"""
    __tablename__ = 'sales_activities'
    
    # Activity Information
    activity_type = db.Column(db.String(100), nullable=False)  # Call, Email, Meeting, etc.
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Activity Details
    activity_date = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer, default=0)  # minutes
    outcome = db.Column(db.String(100))
    next_action = db.Column(db.String(200))
    next_action_date = db.Column(db.DateTime)
    
    # Relationships
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'))
    opportunity = relationship("Opportunity", back_populates="activities")
    
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    contact = relationship("Contact")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'activity_type': self.activity_type,
            'subject': self.subject,
            'description': self.description,
            'activity_date': self.activity_date.isoformat() if self.activity_date else None,
            'duration': self.duration,
            'outcome': self.outcome,
            'next_action': self.next_action,
            'next_action_date': self.next_action_date.isoformat() if self.next_action_date else None,
            'opportunity_id': self.opportunity_id,
            'contact_id': self.contact_id,
            'company_id': self.company_id
        })
        return data

# Marketing Automation Models
class MarketingCampaign(BaseModel):
    """Marketing campaign model"""
    __tablename__ = 'marketing_campaigns'
    
    # Campaign Information
    campaign_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    campaign_type = db.Column(db.String(100), nullable=False)  # Email, Social, Content, etc.
    
    # Campaign Configuration
    target_audience = db.Column(db.JSON)  # Target audience criteria
    campaign_content = db.Column(db.JSON)  # Campaign content and templates
    schedule_config = db.Column(db.JSON)  # Campaign scheduling
    
    # Campaign Status
    status = db.Column(db.Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    
    # Campaign Metrics
    total_sent = db.Column(db.Integer, default=0)
    total_delivered = db.Column(db.Integer, default=0)
    total_opened = db.Column(db.Integer, default=0)
    total_clicked = db.Column(db.Integer, default=0)
    total_converted = db.Column(db.Integer, default=0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    campaign_recipients = relationship("CampaignRecipient", back_populates="campaign")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'campaign_name': self.campaign_name,
            'description': self.description,
            'campaign_type': self.campaign_type,
            'target_audience': self.target_audience,
            'campaign_content': self.campaign_content,
            'schedule_config': self.schedule_config,
            'status': self.status.value if self.status else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'total_sent': self.total_sent,
            'total_delivered': self.total_delivered,
            'total_opened': self.total_opened,
            'total_clicked': self.total_clicked,
            'total_converted': self.total_converted,
            'company_id': self.company_id
        })
        return data

class CampaignRecipient(BaseModel):
    """Campaign recipient model"""
    __tablename__ = 'campaign_recipients'
    
    # Recipient Information
    email = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    
    # Campaign Association
    campaign_id = db.Column(db.Integer, db.ForeignKey('marketing_campaigns.id'), nullable=False)
    campaign = relationship("MarketingCampaign", back_populates="campaign_recipients")
    
    # Recipient Status
    status = db.Column(db.String(50), default='Pending')  # Pending, Sent, Delivered, Opened, Clicked, Converted, Bounced, Unsubscribed
    sent_date = db.Column(db.DateTime)
    delivered_date = db.Column(db.DateTime)
    opened_date = db.Column(db.DateTime)
    clicked_date = db.Column(db.DateTime)
    converted_date = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'campaign_id': self.campaign_id,
            'status': self.status,
            'sent_date': self.sent_date.isoformat() if self.sent_date else None,
            'delivered_date': self.delivered_date.isoformat() if self.delivered_date else None,
            'opened_date': self.opened_date.isoformat() if self.opened_date else None,
            'clicked_date': self.clicked_date.isoformat() if self.clicked_date else None,
            'converted_date': self.converted_date.isoformat() if self.converted_date else None,
            'company_id': self.company_id
        })
        return data

# Customer Service Models
class SupportTicket(BaseModel):
    """Support ticket model"""
    __tablename__ = 'support_tickets'
    
    # Ticket Information
    ticket_number = db.Column(db.String(50), unique=True, nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Customer Information
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = relationship("Customer")
    
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    contact = relationship("Contact")
    
    # Ticket Details
    priority = db.Column(db.Enum(TicketPriority), default=TicketPriority.MEDIUM)
    status = db.Column(db.Enum(TicketStatus), default=TicketStatus.OPEN)
    category = db.Column(db.String(100))
    subcategory = db.Column(db.String(100))
    
    # Assignment
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    assigned_to = relationship("Employee")
    
    # Dates
    due_date = db.Column(db.DateTime)
    resolved_date = db.Column(db.DateTime)
    closed_date = db.Column(db.DateTime)
    
    # SLA Information
    sla_deadline = db.Column(db.DateTime)
    sla_status = db.Column(db.String(50))  # On Time, Overdue, etc.
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    ticket_comments = relationship("TicketComment", back_populates="ticket")
    ticket_attachments = relationship("TicketAttachment", back_populates="ticket")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'ticket_number': self.ticket_number,
            'subject': self.subject,
            'description': self.description,
            'customer_id': self.customer_id,
            'contact_id': self.contact_id,
            'priority': self.priority.value if self.priority else None,
            'status': self.status.value if self.status else None,
            'category': self.category,
            'subcategory': self.subcategory,
            'assigned_to_id': self.assigned_to_id,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'resolved_date': self.resolved_date.isoformat() if self.resolved_date else None,
            'closed_date': self.closed_date.isoformat() if self.closed_date else None,
            'sla_deadline': self.sla_deadline.isoformat() if self.sla_deadline else None,
            'sla_status': self.sla_status,
            'company_id': self.company_id
        })
        return data

class TicketComment(BaseModel):
    """Ticket comment model"""
    __tablename__ = 'ticket_comments'
    
    # Comment Information
    comment_text = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)
    
    # Ticket Association
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'), nullable=False)
    ticket = relationship("SupportTicket", back_populates="ticket_comments")
    
    # Author
    author_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    author = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'comment_text': self.comment_text,
            'is_internal': self.is_internal,
            'ticket_id': self.ticket_id,
            'author_id': self.author_id,
            'company_id': self.company_id
        })
        return data

class TicketAttachment(BaseModel):
    """Ticket attachment model"""
    __tablename__ = 'ticket_attachments'
    
    # Attachment Information
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    file_type = db.Column(db.String(100))
    
    # Ticket Association
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'), nullable=False)
    ticket = relationship("SupportTicket", back_populates="ticket_attachments")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'ticket_id': self.ticket_id,
            'company_id': self.company_id
        })
        return data

# Quote and Proposal Models
class Quote(BaseModel):
    """Quote model"""
    __tablename__ = 'quotes'
    
    # Quote Information
    quote_number = db.Column(db.String(50), unique=True, nullable=False)
    quote_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Customer Information
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = relationship("Customer")
    
    # Opportunity Association
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'))
    opportunity = relationship("Opportunity", back_populates="quotes")
    
    # Quote Details
    quote_date = db.Column(db.Date, default=date.today)
    valid_until = db.Column(db.Date)
    status = db.Column(db.String(50), default='Draft')  # Draft, Sent, Accepted, Rejected, Expired
    
    # Financial Information
    subtotal = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    
    # Terms and Conditions
    payment_terms = db.Column(db.String(200))
    delivery_terms = db.Column(db.String(200))
    notes = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    quote_items = relationship("QuoteItem", back_populates="quote")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'quote_number': self.quote_number,
            'quote_name': self.quote_name,
            'description': self.description,
            'customer_id': self.customer_id,
            'opportunity_id': self.opportunity_id,
            'quote_date': self.quote_date.isoformat() if self.quote_date else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'status': self.status,
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'discount_amount': self.discount_amount,
            'total_amount': self.total_amount,
            'payment_terms': self.payment_terms,
            'delivery_terms': self.delivery_terms,
            'notes': self.notes,
            'company_id': self.company_id
        })
        return data

class QuoteItem(BaseModel):
    """Quote item model"""
    __tablename__ = 'quote_items'
    
    # Item Information
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Float, default=1.0)
    unit_price = db.Column(db.Float, default=0.0)
    discount_percentage = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    line_total = db.Column(db.Float, default=0.0)
    
    # Quote Association
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    quote = relationship("Quote", back_populates="quote_items")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'item_name': self.item_name,
            'description': self.description,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'discount_percentage': self.discount_percentage,
            'discount_amount': self.discount_amount,
            'line_total': self.line_total,
            'quote_id': self.quote_id,
            'company_id': self.company_id
        })
        return data
