# Vigilance System for Supply Chain Management
# Advanced tracking and corrective action system

from datetime import datetime, date, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Date, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class VigilanceType(enum.Enum):
    QUALITY_ISSUE = "quality_issue"
    COMPLIANCE_VIOLATION = "compliance_violation"
    EXPIRY_ALERT = "expiry_alert"
    STOCK_SHORTAGE = "stock_shortage"
    SUPPLIER_DELAY = "supplier_delay"
    TEMPERATURE_DEVIATION = "temperature_deviation"
    BATCH_RECALL = "batch_recall"
    LOT_CONTAMINATION = "lot_contamination"
    DOCUMENTATION_ERROR = "documentation_error"
    SHIPPING_DAMAGE = "shipping_damage"

class VigilanceStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"

class CorrectiveActionStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    FAILED = "failed"

class PreventiveActionStatus(enum.Enum):
    PENDING = "pending"
    IMPLEMENTED = "implemented"
    MONITORING = "monitoring"
    EFFECTIVE = "effective"
    INEFFECTIVE = "ineffective"

# Enhanced Vigilance Record
class EnhancedVigilanceRecord(Base):
    __tablename__ = 'enhanced_vigilance_records'
    
    id = Column(Integer, primary_key=True, index=True)
    record_number = Column(String(100), unique=True, nullable=False, index=True)
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    lot_id = Column(Integer, ForeignKey('item_lots.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    
    # Vigilance details
    vigilance_type = Column(Enum(VigilanceType), nullable=False)
    vigilance_level = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    impact_assessment = Column(Text)
    risk_level = Column(String(20))  # low, medium, high, critical
    
    # Detection details
    detected_date = Column(DateTime, default=datetime.utcnow)
    detected_by = Column(Integer, ForeignKey('users.id'))
    detection_method = Column(String(100))  # inspection, test, complaint, system_alert
    detection_location = Column(String(255))
    
    # Status and assignment
    status = Column(Enum(VigilanceStatus), default=VigilanceStatus.OPEN)
    assigned_to = Column(Integer, ForeignKey('users.id'))
    assigned_date = Column(DateTime)
    priority = Column(String(20), default='medium')  # low, medium, high, urgent
    
    # Resolution
    resolution_date = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey('users.id'))
    resolution_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem")
    batch = relationship("ItemBatch")
    lot = relationship("ItemLot")
    supplier = relationship("Supplier")
    customer = relationship("Customer")
    detected_by_user = relationship("User", foreign_keys=[detected_by])
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])
    corrective_actions = relationship("CorrectiveAction", back_populates="vigilance_record", cascade="all, delete-orphan")
    preventive_actions = relationship("PreventiveAction", back_populates="vigilance_record", cascade="all, delete-orphan")
    attachments = relationship("VigilanceAttachment", back_populates="vigilance_record", cascade="all, delete-orphan")

# Corrective Actions
class CorrectiveAction(Base):
    __tablename__ = 'corrective_actions'
    
    id = Column(Integer, primary_key=True, index=True)
    vigilance_record_id = Column(Integer, ForeignKey('enhanced_vigilance_records.id'), nullable=False)
    action_number = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    action_type = Column(String(50))  # immediate, short_term, long_term
    status = Column(Enum(CorrectiveActionStatus), default=CorrectiveActionStatus.PENDING)
    
    # Assignment and timeline
    assigned_to = Column(Integer, ForeignKey('users.id'))
    assigned_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    completed_date = Column(DateTime)
    
    # Implementation details
    implementation_notes = Column(Text)
    resources_required = Column(JSON)
    cost_estimate = Column(Float)
    actual_cost = Column(Float)
    
    # Verification
    verification_required = Column(Boolean, default=True)
    verification_date = Column(DateTime)
    verified_by = Column(Integer, ForeignKey('users.id'))
    verification_notes = Column(Text)
    effectiveness_rating = Column(Integer)  # 1-5 scale
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    vigilance_record = relationship("EnhancedVigilanceRecord", back_populates="corrective_actions")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    verified_by_user = relationship("User", foreign_keys=[verified_by])

# Preventive Actions
class PreventiveAction(Base):
    __tablename__ = 'preventive_actions'
    
    id = Column(Integer, primary_key=True, index=True)
    vigilance_record_id = Column(Integer, ForeignKey('enhanced_vigilance_records.id'), nullable=False)
    action_number = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    action_type = Column(String(50))  # process_improvement, training, system_upgrade, policy_change
    status = Column(Enum(PreventiveActionStatus), default=PreventiveActionStatus.PENDING)
    
    # Assignment and timeline
    assigned_to = Column(Integer, ForeignKey('users.id'))
    assigned_date = Column(DateTime, default=datetime.utcnow)
    implementation_date = Column(DateTime)
    completion_date = Column(DateTime)
    
    # Implementation details
    implementation_notes = Column(Text)
    resources_required = Column(JSON)
    cost_estimate = Column(Float)
    actual_cost = Column(Float)
    
    # Monitoring
    monitoring_required = Column(Boolean, default=True)
    monitoring_period_days = Column(Integer, default=90)
    monitoring_frequency = Column(String(20), default='weekly')  # daily, weekly, monthly
    effectiveness_rating = Column(Integer)  # 1-5 scale
    last_monitoring_date = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    vigilance_record = relationship("EnhancedVigilanceRecord", back_populates="preventive_actions")
    assigned_user = relationship("User", foreign_keys=[assigned_to])

# Vigilance Attachments
class VigilanceAttachment(Base):
    __tablename__ = 'vigilance_attachments'
    
    id = Column(Integer, primary_key=True, index=True)
    vigilance_record_id = Column(Integer, ForeignKey('enhanced_vigilance_records.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    description = Column(Text)
    
    # Metadata
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    vigilance_record = relationship("EnhancedVigilanceRecord", back_populates="attachments")
    uploader = relationship("User")

# Vigilance Alerts
class VigilanceAlert(Base):
    __tablename__ = 'vigilance_alerts'
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)  # expiry, stock, quality, compliance
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    alert_level = Column(String(20), nullable=False)  # info, warning, error, critical
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    lot_id = Column(Integer, ForeignKey('item_lots.id'))
    vigilance_record_id = Column(Integer, ForeignKey('enhanced_vigilance_records.id'))
    
    # Alert configuration
    is_active = Column(Boolean, default=True)
    is_sent = Column(Boolean, default=False)
    sent_date = Column(DateTime)
    recipients = Column(JSON)  # List of user IDs or email addresses
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem")
    batch = relationship("ItemBatch")
    lot = relationship("ItemLot")
    vigilance_record = relationship("EnhancedVigilanceRecord")

# Vigilance Metrics
class VigilanceMetric(Base):
    __tablename__ = 'vigilance_metrics'
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_type = Column(String(50), nullable=False)  # count, percentage, rate, trend
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))
    
    # Time period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    period_type = Column(String(20))  # daily, weekly, monthly, quarterly, annual
    
    # Context
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    vigilance_type = Column(Enum(VigilanceType))
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem")
    supplier = relationship("Supplier")

# Vigilance Dashboard
class VigilanceDashboard(Base):
    __tablename__ = 'vigilance_dashboards'
    
    id = Column(Integer, primary_key=True, index=True)
    dashboard_name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    dashboard_config = Column(JSON)  # Dashboard layout and widgets configuration
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")

# Vigilance Reports
class VigilanceReport(Base):
    __tablename__ = 'vigilance_reports'
    
    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # summary, detailed, trend, compliance
    report_period = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly, annual
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Report data
    report_data = Column(JSON)
    report_summary = Column(JSON)
    recommendations = Column(JSON)
    
    # Filters
    item_filters = Column(JSON)
    supplier_filters = Column(JSON)
    vigilance_type_filters = Column(JSON)
    status_filters = Column(JSON)
    
    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    generator = relationship("User")

# Vigilance Workflow
class VigilanceWorkflow(Base):
    __tablename__ = 'vigilance_workflows'
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String(255), nullable=False)
    workflow_type = Column(String(50), nullable=False)  # escalation, approval, notification
    is_active = Column(Boolean, default=True)
    
    # Workflow configuration
    workflow_config = Column(JSON)  # Workflow steps and conditions
    trigger_conditions = Column(JSON)  # Conditions that trigger the workflow
    action_conditions = Column(JSON)  # Conditions for each action
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Vigilance Workflow Instance
class VigilanceWorkflowInstance(Base):
    __tablename__ = 'vigilance_workflow_instances'
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey('vigilance_workflows.id'), nullable=False)
    vigilance_record_id = Column(Integer, ForeignKey('enhanced_vigilance_records.id'), nullable=False)
    current_step = Column(Integer, default=0)
    status = Column(String(50), default='active')  # active, completed, failed, cancelled
    
    # Workflow execution
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    execution_log = Column(JSON)  # Log of workflow execution steps
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    workflow = relationship("VigilanceWorkflow")
    vigilance_record = relationship("EnhancedVigilanceRecord")
