# Desk Module Models
# Integrated Help Desk and Maintenance Management

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from clean_erp_system.backend.core.database import Base
import enum

class TicketType(enum.Enum):
    SUPPORT = "support"
    MAINTENANCE = "maintenance"
    INCIDENT = "incident"
    REQUEST = "request"
    COMPLAINT = "complaint"

class TicketStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class Priority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"

class TicketCategory(enum.Enum):
    TECHNICAL = "technical"
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    SECURITY = "security"
    USER_ACCOUNT = "user_account"
    ACCESS = "access"
    TRAINING = "training"
    OTHER = "other"

# Help Desk Models
class SupportTicket(Base):
    __tablename__ = 'support_tickets'
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Ticket Classification
    ticket_type = Column(Enum(TicketType), nullable=False)
    category = Column(Enum(TicketCategory), nullable=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    
    # Ticket Assignment
    requester_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    assignee_id = Column(Integer, ForeignKey('users.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    
    # Ticket Details
    resolution_notes = Column(Text)
    resolution_time = Column(DateTime)
    due_date = Column(DateTime)
    estimated_time = Column(Integer)  # Minutes
    actual_time = Column(Integer)  # Minutes
    
    # Ticket Metrics
    first_response_time = Column(DateTime)
    resolution_time_minutes = Column(Integer)
    customer_satisfaction_score = Column(Float)
    customer_feedback = Column(Text)
    
    # Ticket Attachments
    attachments = Column(JSON)  # File attachments
    tags = Column(JSON)  # Tags for categorization
    
    # Integration
    related_module = Column(String(50))  # CRM, Finance, HR, etc.
    related_record_id = Column(Integer)  # ID of related record
    external_ticket_id = Column(String(100))  # External system ticket ID
    
    # SLA Management
    sla_id = Column(Integer, ForeignKey('service_level_agreements.id'))
    sla_breach_time = Column(DateTime)
    sla_status = Column(String(50))  # on_time, breached, at_risk
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id])
    assignee = relationship("User", foreign_keys=[assignee_id])
    team = relationship("Team")
    department = relationship("Department")
    sla = relationship("ServiceLevelAgreement")
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
    activities = relationship("TicketActivity", back_populates="ticket", cascade="all, delete-orphan")

class TicketComment(Base):
    __tablename__ = 'ticket_comments'
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey('support_tickets.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    comment = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal notes
    is_solution = Column(Boolean, default=False)  # Solution comment
    
    # Comment Attachments
    attachments = Column(JSON)  # File attachments
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ticket = relationship("SupportTicket", back_populates="comments")
    user = relationship("User")

class TicketActivity(Base):
    __tablename__ = 'ticket_activities'
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey('support_tickets.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    activity_type = Column(String(50), nullable=False)  # created, assigned, status_changed, etc.
    activity_description = Column(Text, nullable=False)
    old_value = Column(String(255))
    new_value = Column(String(255))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ticket = relationship("SupportTicket", back_populates="activities")
    user = relationship("User")

class ServiceLevelAgreement(Base):
    __tablename__ = 'service_level_agreements'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # SLA Rules
    first_response_time = Column(Integer)  # Minutes
    resolution_time = Column(Integer)  # Minutes
    business_hours_only = Column(Boolean, default=True)
    business_hours = Column(JSON)  # Business hours configuration
    
    # SLA Conditions
    conditions = Column(JSON)  # Conditions for SLA application
    priority_multiplier = Column(JSON)  # Priority-based time multipliers
    
    # SLA Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")
    tickets = relationship("SupportTicket")

# Maintenance Models
class Asset(Base):
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True, index=True)
    asset_tag = Column(String(100), unique=True, nullable=False)
    asset_name = Column(String(255), nullable=False)
    asset_description = Column(Text)
    
    # Asset Classification
    asset_type = Column(String(100), nullable=False)  # Equipment, Vehicle, Building, etc.
    asset_category = Column(String(100))  # IT, Manufacturing, Office, etc.
    asset_subcategory = Column(String(100))  # Computer, Printer, Vehicle, etc.
    
    # Asset Details
    manufacturer = Column(String(255))
    model = Column(String(255))
    serial_number = Column(String(255))
    purchase_date = Column(DateTime)
    warranty_expiry = Column(DateTime)
    purchase_cost = Column(Float)
    current_value = Column(Float)
    
    # Asset Location
    location = Column(String(255))
    building = Column(String(255))
    floor = Column(String(50))
    room = Column(String(100))
    coordinates = Column(JSON)  # GPS coordinates
    
    # Asset Assignment
    assigned_to_user_id = Column(Integer, ForeignKey('users.id'))
    assigned_to_department_id = Column(Integer, ForeignKey('departments.id'))
    custodian_id = Column(Integer, ForeignKey('users.id'))
    
    # Asset Status
    status = Column(String(50), default='active')  # active, inactive, maintenance, retired
    condition = Column(String(50), default='good')  # excellent, good, fair, poor, critical
    availability = Column(String(50), default='available')  # available, in_use, maintenance, retired
    
    # Asset Specifications
    specifications = Column(JSON)  # Technical specifications
    maintenance_schedule = Column(JSON)  # Maintenance schedule
    maintenance_history = Column(JSON)  # Maintenance history
    
    # Asset Metrics
    utilization_rate = Column(Float, default=0.0)  # Utilization percentage
    maintenance_cost = Column(Float, default=0.0)  # Total maintenance cost
    downtime_hours = Column(Float, default=0.0)  # Total downtime hours
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    assigned_to_user = relationship("User", foreign_keys=[assigned_to_user_id])
    assigned_to_department = relationship("Department")
    custodian = relationship("User", foreign_keys=[custodian_id])
    creator = relationship("User", foreign_keys=[created_by])
    work_orders = relationship("WorkOrder", back_populates="asset")
    maintenance_schedules = relationship("MaintenanceSchedule", back_populates="asset")

class WorkOrder(Base):
    __tablename__ = 'work_orders'
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_number = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Work Order Classification
    work_order_type = Column(String(50), nullable=False)  # preventive, corrective, emergency, inspection
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    status = Column(String(50), default='open')  # open, in_progress, completed, cancelled
    
    # Work Order Assignment
    requested_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey('users.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    
    # Asset Information
    asset_id = Column(Integer, ForeignKey('assets.id'))
    location = Column(String(255))
    
    # Work Order Details
    scheduled_date = Column(DateTime)
    start_date = Column(DateTime)
    completion_date = Column(DateTime)
    estimated_duration = Column(Integer)  # Minutes
    actual_duration = Column(Integer)  # Minutes
    
    # Work Order Instructions
    instructions = Column(Text)
    safety_requirements = Column(Text)
    required_tools = Column(JSON)  # Required tools
    required_parts = Column(JSON)  # Required parts
    
    # Work Order Results
    work_performed = Column(Text)
    findings = Column(Text)
    recommendations = Column(Text)
    next_maintenance_date = Column(DateTime)
    
    # Work Order Costs
    labor_cost = Column(Float, default=0.0)
    parts_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Work Order Attachments
    attachments = Column(JSON)  # File attachments
    photos = Column(JSON)  # Photo attachments
    
    # Integration
    related_ticket_id = Column(Integer, ForeignKey('support_tickets.id'))
    related_module = Column(String(50))  # CRM, Finance, HR, etc.
    related_record_id = Column(Integer)  # ID of related record
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    team = relationship("Team")
    department = relationship("Department")
    asset = relationship("Asset", back_populates="work_orders")
    related_ticket = relationship("SupportTicket")
    maintenance_logs = relationship("MaintenanceLog", back_populates="work_order", cascade="all, delete-orphan")

class MaintenanceSchedule(Base):
    __tablename__ = 'maintenance_schedules'
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Schedule Details
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False)
    maintenance_type = Column(String(50), nullable=False)  # preventive, predictive, condition_based
    frequency = Column(String(50), nullable=False)  # daily, weekly, monthly, quarterly, annually
    frequency_value = Column(Integer, default=1)  # Frequency multiplier
    
    # Schedule Timing
    next_due_date = Column(DateTime)
    last_performed_date = Column(DateTime)
    estimated_duration = Column(Integer)  # Minutes
    
    # Schedule Instructions
    instructions = Column(Text)
    checklist = Column(JSON)  # Maintenance checklist
    required_tools = Column(JSON)  # Required tools
    required_parts = Column(JSON)  # Required parts
    
    # Schedule Status
    is_active = Column(Boolean, default=True)
    is_overdue = Column(Boolean, default=False)
    overdue_days = Column(Integer, default=0)
    
    # Schedule Metrics
    completion_rate = Column(Float, default=0.0)  # Completion percentage
    average_duration = Column(Float, default=0.0)  # Average duration in minutes
    cost_per_maintenance = Column(Float, default=0.0)  # Average cost per maintenance
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    asset = relationship("Asset", back_populates="maintenance_schedules")
    creator = relationship("User")

class MaintenanceLog(Base):
    __tablename__ = 'maintenance_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey('work_orders.id'), nullable=False)
    performed_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Maintenance Details
    maintenance_date = Column(DateTime, nullable=False)
    maintenance_type = Column(String(50), nullable=False)  # preventive, corrective, emergency, inspection
    work_performed = Column(Text, nullable=False)
    findings = Column(Text)
    recommendations = Column(Text)
    
    # Maintenance Results
    status_before = Column(String(50))  # Asset status before maintenance
    status_after = Column(String(50))  # Asset status after maintenance
    condition_before = Column(String(50))  # Asset condition before maintenance
    condition_after = Column(String(50))  # Asset condition after maintenance
    
    # Maintenance Costs
    labor_hours = Column(Float, default=0.0)
    labor_cost = Column(Float, default=0.0)
    parts_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Maintenance Attachments
    attachments = Column(JSON)  # File attachments
    photos = Column(JSON)  # Photo attachments
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="maintenance_logs")
    performed_by = relationship("User")

class SparePart(Base):
    __tablename__ = 'spare_parts'
    
    id = Column(Integer, primary_key=True, index=True)
    part_number = Column(String(100), unique=True, nullable=False)
    part_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Part Details
    manufacturer = Column(String(255))
    model = Column(String(255))
    category = Column(String(100))
    subcategory = Column(String(100))
    
    # Part Specifications
    specifications = Column(JSON)  # Technical specifications
    dimensions = Column(JSON)  # Physical dimensions
    weight = Column(Float)  # Weight in kg
    color = Column(String(50))
    material = Column(String(100))
    
    # Part Inventory
    current_stock = Column(Integer, default=0)
    minimum_stock = Column(Integer, default=0)
    maximum_stock = Column(Integer, default=0)
    reorder_point = Column(Integer, default=0)
    reorder_quantity = Column(Integer, default=0)
    
    # Part Costs
    unit_cost = Column(Float, default=0.0)
    selling_price = Column(Float, default=0.0)
    total_value = Column(Float, default=0.0)
    
    # Part Status
    is_active = Column(Boolean, default=True)
    is_obsolete = Column(Boolean, default=False)
    is_critical = Column(Boolean, default=False)
    
    # Part Usage
    usage_count = Column(Integer, default=0)
    last_used_date = Column(DateTime)
    average_usage = Column(Float, default=0.0)  # Average usage per month
    
    # Part Location
    location = Column(String(255))
    shelf = Column(String(50))
    bin = Column(String(50))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Knowledge Base Models
class KnowledgeBase(Base):
    __tablename__ = 'knowledge_base'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # Article Classification
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    tags = Column(JSON)  # Tags for categorization
    keywords = Column(JSON)  # Search keywords
    
    # Article Details
    article_type = Column(String(50), default='article')  # article, faq, tutorial, troubleshooting
    difficulty_level = Column(String(20), default='beginner')  # beginner, intermediate, advanced
    estimated_read_time = Column(Integer)  # Minutes
    
    # Article Status
    status = Column(String(50), default='draft')  # draft, published, archived
    is_featured = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    
    # Article Metrics
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    
    # Article Attachments
    attachments = Column(JSON)  # File attachments
    images = Column(JSON)  # Image attachments
    
    # Article SEO
    meta_description = Column(Text)
    meta_keywords = Column(Text)
    slug = Column(String(255), unique=True)
    
    # Article Versioning
    version = Column(Integer, default=1)
    parent_article_id = Column(Integer, ForeignKey('knowledge_base.id'))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")
    parent_article = relationship("KnowledgeBase", remote_side=[id])

# Desk Analytics Models
class DeskAnalytics(Base):
    __tablename__ = 'desk_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    analytics_name = Column(String(255), nullable=False)
    analytics_type = Column(String(50), nullable=False)  # ticket, maintenance, performance, etc.
    analytics_period = Column(String(50), nullable=False)  # daily, weekly, monthly, quarterly
    
    # Analytics Data
    analytics_data = Column(JSON, nullable=False)  # Analytics data
    analytics_metrics = Column(JSON, nullable=False)  # Key metrics
    analytics_insights = Column(JSON)  # Analytics insights
    analytics_recommendations = Column(JSON)  # Recommendations
    
    # Desk Metrics
    total_tickets = Column(Integer, default=0)
    resolved_tickets = Column(Integer, default=0)
    average_resolution_time = Column(Float, default=0.0)  # Hours
    customer_satisfaction = Column(Float, default=0.0)  # 0-100 score
    
    # Maintenance Metrics
    total_work_orders = Column(Integer, default=0)
    completed_work_orders = Column(Integer, default=0)
    average_maintenance_time = Column(Float, default=0.0)  # Hours
    maintenance_cost = Column(Float, default=0.0)  # Total maintenance cost
    
    # Performance Metrics
    first_response_time = Column(Float, default=0.0)  # Hours
    resolution_time = Column(Float, default=0.0)  # Hours
    backlog_count = Column(Integer, default=0)
    overdue_count = Column(Integer, default=0)
    
    # Analytics Trends
    trend_direction = Column(String(20))  # increasing, stable, decreasing
    trend_strength = Column(Float, default=0.0)  # Trend strength
    seasonal_adjustment = Column(Float, default=0.0)  # Seasonal adjustment
    
    # Metadata
    analytics_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    tickets = relationship("SupportTicket")
    work_orders = relationship("WorkOrder")
