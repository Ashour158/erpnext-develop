# Help Desk Models
# Comprehensive customer service and support system

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class TicketStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class TicketPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class TicketType(enum.Enum):
    INCIDENT = "incident"
    REQUEST = "request"
    PROBLEM = "problem"
    CHANGE = "change"
    QUESTION = "question"
    COMPLAINT = "complaint"
    FEATURE_REQUEST = "feature_request"

class TicketSource(enum.Enum):
    EMAIL = "email"
    PHONE = "phone"
    WEB = "web"
    CHAT = "chat"
    SOCIAL_MEDIA = "social_media"
    MOBILE_APP = "mobile_app"
    API = "api"
    WALK_IN = "walk_in"

class SatisfactionRating(enum.Enum):
    VERY_DISSATISFIED = "very_dissatisfied"
    DISSATISFIED = "dissatisfied"
    NEUTRAL = "neutral"
    SATISFIED = "satisfied"
    VERY_SATISFIED = "very_satisfied"

# Support Tickets
class SupportTicket(Base):
    __tablename__ = 'support_tickets'
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    
    # Ticket Details
    ticket_subject = Column(String(255), nullable=False)
    ticket_description = Column(Text, nullable=False)
    ticket_type = Column(Enum(TicketType), nullable=False)
    ticket_source = Column(Enum(TicketSource), nullable=False)
    
    # Ticket Status
    ticket_status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    ticket_priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    ticket_category = Column(String(100))
    ticket_subcategory = Column(String(100))
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey('users.id'))
    assigned_team = Column(Integer, ForeignKey('teams.id'))
    assigned_at = Column(DateTime)
    
    # SLA Management
    sla_deadline = Column(DateTime)
    sla_response_time = Column(Integer)  # Minutes
    sla_resolution_time = Column(Integer)  # Minutes
    sla_breach = Column(Boolean, default=False)
    sla_breach_reason = Column(Text)
    
    # Resolution
    resolution_notes = Column(Text)
    resolution_category = Column(String(100))
    resolution_subcategory = Column(String(100))
    resolution_time = Column(Integer)  # Minutes to resolve
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey('users.id'))
    
    # Customer Satisfaction
    satisfaction_rating = Column(Enum(SatisfactionRating))
    satisfaction_score = Column(Float)  # 0-100
    satisfaction_feedback = Column(Text)
    satisfaction_survey_sent = Column(Boolean, default=False)
    satisfaction_survey_sent_at = Column(DateTime)
    
    # Ticket Metrics
    first_response_time = Column(Integer)  # Minutes to first response
    resolution_time = Column(Integer)  # Minutes to resolution
    reopen_count = Column(Integer, default=0)
    escalation_count = Column(Integer, default=0)
    
    # Ticket Context
    ticket_tags = Column(JSON)  # Ticket tags
    ticket_custom_fields = Column(JSON)  # Custom fields
    ticket_attachments = Column(JSON)  # File attachments
    ticket_related_tickets = Column(JSON)  # Related ticket IDs
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    customer = relationship("Customer")
    contact = relationship("Contact")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    assigned_team_rel = relationship("Team")
    resolver = relationship("User", foreign_keys=[resolved_by])
    creator = relationship("User", foreign_keys=[created_by])
    comments = relationship("TicketComment", back_populates="ticket")
    activities = relationship("TicketActivity", back_populates="ticket")

# Ticket Comments
class TicketComment(Base):
    __tablename__ = 'ticket_comments'
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey('support_tickets.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Comment Details
    comment_text = Column(Text, nullable=False)
    comment_type = Column(String(50), default='comment')  # comment, note, internal
    is_internal = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    
    # Comment Attachments
    attachments = Column(JSON)  # File attachments
    mentions = Column(JSON)  # User mentions
    
    # Comment Status
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime)
    edited_by = Column(Integer, ForeignKey('users.id'))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    ticket = relationship("SupportTicket", back_populates="comments")
    user = relationship("User", foreign_keys=[user_id])
    editor = relationship("User", foreign_keys=[edited_by])

# Ticket Activities
class TicketActivity(Base):
    __tablename__ = 'ticket_activities'
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey('support_tickets.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Activity Details
    activity_type = Column(String(50), nullable=False)  # created, assigned, status_changed, priority_changed
    activity_description = Column(Text, nullable=False)
    activity_data = Column(JSON)  # Activity-specific data
    
    # Activity Context
    old_value = Column(String(255))
    new_value = Column(String(255))
    activity_reason = Column(Text)
    
    # Metadata
    activity_date = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    ticket = relationship("SupportTicket", back_populates="activities")
    user = relationship("User")

# Knowledge Base
class KnowledgeBase(Base):
    __tablename__ = 'knowledge_base'
    
    id = Column(Integer, primary_key=True, index=True)
    article_title = Column(String(255), nullable=False)
    article_slug = Column(String(255), unique=True, nullable=False)
    article_content = Column(Text, nullable=False)
    article_summary = Column(Text)
    
    # Article Classification
    article_category = Column(String(100), nullable=False)
    article_subcategory = Column(String(100))
    article_tags = Column(JSON)  # Article tags
    article_keywords = Column(JSON)  # SEO keywords
    
    # Article Status
    article_status = Column(String(50), default='draft')  # draft, published, archived
    article_visibility = Column(String(50), default='public')  # public, internal, restricted
    article_featured = Column(Boolean, default=False)
    
    # Article Metrics
    article_views = Column(Integer, default=0)
    article_helpful = Column(Integer, default=0)
    article_not_helpful = Column(Integer, default=0)
    article_rating = Column(Float, default=0.0)  # 0-5 rating
    
    # Article SEO
    seo_title = Column(String(255))
    seo_description = Column(Text)
    seo_keywords = Column(JSON)
    
    # Article Versioning
    article_version = Column(Integer, default=1)
    article_parent_id = Column(Integer, ForeignKey('knowledge_base.id'))
    article_author = Column(Integer, ForeignKey('users.id'))
    article_editor = Column(Integer, ForeignKey('users.id'))
    
    # Article Dates
    published_at = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    parent_article = relationship("KnowledgeBase", remote_side=[id])
    author = relationship("User", foreign_keys=[article_author])
    editor = relationship("User", foreign_keys=[article_editor])

# FAQ Management
class FAQ(Base):
    __tablename__ = 'faqs'
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    
    # FAQ Classification
    faq_category = Column(String(100), nullable=False)
    faq_subcategory = Column(String(100))
    faq_tags = Column(JSON)  # FAQ tags
    faq_keywords = Column(JSON)  # Search keywords
    
    # FAQ Status
    faq_status = Column(String(50), default='active')  # active, inactive, archived
    faq_featured = Column(Boolean, default=False)
    faq_priority = Column(Integer, default=0)  # Display priority
    
    # FAQ Metrics
    faq_views = Column(Integer, default=0)
    faq_helpful = Column(Integer, default=0)
    faq_not_helpful = Column(Integer, default=0)
    faq_rating = Column(Float, default=0.0)  # 0-5 rating
    
    # FAQ Management
    faq_author = Column(Integer, ForeignKey('users.id'))
    faq_editor = Column(Integer, ForeignKey('users.id'))
    faq_approver = Column(Integer, ForeignKey('users.id'))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    author = relationship("User", foreign_keys=[faq_author])
    editor = relationship("User", foreign_keys=[faq_editor])
    approver = relationship("User", foreign_keys=[faq_approver])

# Customer Feedback
class CustomerFeedback(Base):
    __tablename__ = 'customer_feedback'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    ticket_id = Column(Integer, ForeignKey('support_tickets.id'))
    
    # Feedback Details
    feedback_type = Column(String(50), nullable=False)  # satisfaction, complaint, suggestion, compliment
    feedback_rating = Column(Enum(SatisfactionRating), nullable=False)
    feedback_score = Column(Float, nullable=False)  # 0-100
    feedback_text = Column(Text)
    
    # Feedback Categories
    feedback_category = Column(String(100))
    feedback_subcategory = Column(String(100))
    feedback_tags = Column(JSON)  # Feedback tags
    
    # Feedback Response
    feedback_response = Column(Text)
    feedback_response_by = Column(Integer, ForeignKey('users.id'))
    feedback_response_at = Column(DateTime)
    feedback_action_taken = Column(Text)
    
    # Feedback Status
    feedback_status = Column(String(50), default='new')  # new, reviewed, responded, closed
    feedback_priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    feedback_escalated = Column(Boolean, default=False)
    
    # Metadata
    feedback_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    customer = relationship("Customer")
    ticket = relationship("SupportTicket")
    responder = relationship("User")

# Service Level Agreements
class ServiceLevelAgreement(Base):
    __tablename__ = 'service_level_agreements'
    
    id = Column(Integer, primary_key=True, index=True)
    sla_name = Column(String(255), nullable=False)
    sla_description = Column(Text)
    
    # SLA Configuration
    sla_type = Column(String(50), nullable=False)  # response, resolution, availability
    sla_priority = Column(Enum(TicketPriority), nullable=False)
    sla_category = Column(String(100))
    
    # SLA Metrics
    sla_response_time = Column(Integer, nullable=False)  # Minutes
    sla_resolution_time = Column(Integer, nullable=False)  # Minutes
    sla_availability = Column(Float, default=99.9)  # Percentage
    
    # SLA Conditions
    sla_conditions = Column(JSON)  # SLA conditions
    sla_exceptions = Column(JSON)  # SLA exceptions
    sla_escalation_rules = Column(JSON)  # Escalation rules
    
    # SLA Performance
    sla_target_performance = Column(Float, default=95.0)  # Target performance percentage
    sla_actual_performance = Column(Float, default=0.0)  # Actual performance percentage
    sla_breach_count = Column(Integer, default=0)
    sla_breach_percentage = Column(Float, default=0.0)
    
    # SLA Status
    sla_status = Column(String(50), default='active')  # active, inactive, archived
    sla_effective_date = Column(DateTime, nullable=False)
    sla_expiry_date = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Support Teams
class SupportTeam(Base):
    __tablename__ = 'support_teams'
    
    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String(255), nullable=False)
    team_description = Column(Text)
    
    # Team Configuration
    team_leader = Column(Integer, ForeignKey('users.id'))
    team_size = Column(Integer, default=0)
    team_skills = Column(JSON)  # Team skills
    team_specialties = Column(JSON)  # Team specialties
    
    # Team Performance
    team_performance_score = Column(Float, default=0.0)  # 0-100
    team_satisfaction_score = Column(Float, default=0.0)  # 0-100
    team_resolution_rate = Column(Float, default=0.0)  # Percentage
    team_response_time = Column(Float, default=0.0)  # Average response time
    
    # Team Metrics
    team_tickets_assigned = Column(Integer, default=0)
    team_tickets_resolved = Column(Integer, default=0)
    team_tickets_escalated = Column(Integer, default=0)
    team_tickets_reopened = Column(Integer, default=0)
    
    # Team Settings
    team_working_hours = Column(JSON)  # Working hours
    team_availability = Column(JSON)  # Availability settings
    team_escalation_rules = Column(JSON)  # Escalation rules
    
    # Team Status
    team_status = Column(String(50), default='active')  # active, inactive, archived
    team_created_at = Column(DateTime, default=datetime.utcnow)
    team_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    leader = relationship("User")

# Support Analytics
class SupportAnalytics(Base):
    __tablename__ = 'support_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    analytics_type = Column(String(50), nullable=False)  # ticket, team, agent, customer
    analytics_period = Column(String(50), nullable=False)  # daily, weekly, monthly, quarterly
    analytics_date = Column(DateTime, nullable=False)
    
    # Analytics Data
    analytics_data = Column(JSON, nullable=False)  # Analytics data
    analytics_metrics = Column(JSON, nullable=False)  # Key metrics
    analytics_insights = Column(JSON)  # Analytics insights
    analytics_recommendations = Column(JSON)  # Recommendations
    
    # Performance Metrics
    total_tickets = Column(Integer, default=0)
    resolved_tickets = Column(Integer, default=0)
    pending_tickets = Column(Integer, default=0)
    escalated_tickets = Column(Integer, default=0)
    
    # Performance Rates
    resolution_rate = Column(Float, default=0.0)  # Percentage
    first_response_rate = Column(Float, default=0.0)  # Percentage
    escalation_rate = Column(Float, default=0.0)  # Percentage
    satisfaction_rate = Column(Float, default=0.0)  # Percentage
    
    # Time Metrics
    average_response_time = Column(Float, default=0.0)  # Minutes
    average_resolution_time = Column(Float, default=0.0)  # Minutes
    sla_compliance_rate = Column(Float, default=0.0)  # Percentage
    
    # Customer Metrics
    customer_satisfaction = Column(Float, default=0.0)  # 0-100
    customer_retention = Column(Float, default=0.0)  # Percentage
    customer_churn = Column(Float, default=0.0)  # Percentage
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
