# Access Control System
# Comprehensive access control and permission management

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class AccessDecision(enum.Enum):
    ALLOW = "allow"
    DENY = "deny"
    CHALLENGE = "challenge"
    ERROR = "error"

class AccessContext(enum.Enum):
    MODULE = "module"
    FEATURE = "feature"
    DATA = "data"
    API = "api"
    SYSTEM = "system"

class SecurityLevel(enum.Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"

# Access Control Engine
class AccessControlEngine(Base):
    __tablename__ = 'access_control_engines'
    
    id = Column(Integer, primary_key=True, index=True)
    engine_name = Column(String(255), nullable=False)
    engine_type = Column(String(50), nullable=False)  # rbac, abac, dac, mac
    engine_description = Column(Text)
    
    # Engine Configuration
    engine_config = Column(JSON, nullable=False)  # Engine configuration
    engine_rules = Column(JSON, nullable=False)  # Engine rules
    engine_policies = Column(JSON)  # Engine policies
    engine_algorithms = Column(JSON)  # Engine algorithms
    
    # Engine Performance
    engine_performance_score = Column(Float, default=0.0)  # 0-100
    engine_response_time = Column(Float, default=0.0)  # Response time in milliseconds
    engine_throughput = Column(Float, default=0.0)  # Throughput per second
    engine_accuracy = Column(Float, default=100.0)  # Accuracy percentage
    
    # Engine Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    engine_version = Column(String(50), default='1.0.0')
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Access Control Rules
class AccessControlRule(Base):
    __tablename__ = 'access_control_rules'
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(255), nullable=False)
    rule_description = Column(Text)
    rule_type = Column(String(50), nullable=False)  # allow, deny, challenge, conditional
    
    # Rule Configuration
    rule_conditions = Column(JSON, nullable=False)  # Rule conditions
    rule_actions = Column(JSON, nullable=False)  # Rule actions
    rule_priority = Column(Integer, default=0)  # Rule priority
    rule_scope = Column(JSON)  # Rule scope
    
    # Rule Context
    rule_context = Column(Enum(AccessContext), nullable=False)
    rule_resource = Column(String(255))  # Protected resource
    rule_operation = Column(String(100))  # Operation (read, write, delete, etc.)
    rule_subject = Column(JSON)  # Subject (user, role, department)
    
    # Rule Security
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)
    requires_approval = Column(Boolean, default=False)
    requires_audit = Column(Boolean, default=False)
    risk_level = Column(String(20), default='low')  # low, medium, high, critical
    
    # Rule Status
    is_active = Column(Boolean, default=True)
    is_system_rule = Column(Boolean, default=False)
    rule_effective_date = Column(DateTime, default=datetime.utcnow)
    rule_expiry_date = Column(DateTime)
    
    # Rule Performance
    rule_usage_count = Column(Integer, default=0)
    rule_success_count = Column(Integer, default=0)
    rule_failure_count = Column(Integer, default=0)
    rule_accuracy = Column(Float, default=100.0)  # Accuracy percentage
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Access Control Policies
class AccessControlPolicy(Base):
    __tablename__ = 'access_control_policies'
    
    id = Column(Integer, primary_key=True, index=True)
    policy_name = Column(String(255), nullable=False)
    policy_description = Column(Text)
    policy_type = Column(String(50), nullable=False)  # security, compliance, business, technical
    
    # Policy Configuration
    policy_rules = Column(JSON, nullable=False)  # Policy rules
    policy_conditions = Column(JSON)  # Policy conditions
    policy_actions = Column(JSON)  # Policy actions
    policy_priority = Column(Integer, default=0)  # Policy priority
    
    # Policy Scope
    policy_scope = Column(JSON)  # Policy scope
    policy_subjects = Column(JSON)  # Policy subjects
    policy_resources = Column(JSON)  # Policy resources
    policy_operations = Column(JSON)  # Policy operations
    
    # Policy Security
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)
    policy_encryption = Column(Boolean, default=False)
    policy_authentication = Column(String(100))  # Authentication method
    policy_authorization = Column(JSON)  # Authorization configuration
    
    # Policy Status
    is_active = Column(Boolean, default=True)
    is_system_policy = Column(Boolean, default=False)
    policy_effective_date = Column(DateTime, default=datetime.utcnow)
    policy_expiry_date = Column(DateTime)
    
    # Policy Compliance
    compliance_required = Column(Boolean, default=True)
    compliance_monitoring = Column(Boolean, default=True)
    compliance_reporting = Column(Boolean, default=True)
    compliance_audit = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Access Control Decisions
class AccessControlDecision(Base):
    __tablename__ = 'access_control_decisions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_id = Column(String(255))
    
    # Decision Details
    decision_type = Column(Enum(AccessDecision), nullable=False)
    decision_context = Column(Enum(AccessContext), nullable=False)
    decision_resource = Column(String(255))  # Accessed resource
    decision_operation = Column(String(100))  # Operation performed
    decision_reason = Column(Text)  # Decision reason
    
    # Decision Context
    decision_ip = Column(String(45))
    decision_user_agent = Column(Text)
    decision_location = Column(JSON)  # Geographic location
    decision_device = Column(JSON)  # Device information
    
    # Decision Data
    decision_data = Column(JSON)  # Decision data
    decision_metadata = Column(JSON)  # Decision metadata
    decision_risk_score = Column(Float, default=0.0)  # 0-100 risk score
    
    # Decision Security
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)
    security_flags = Column(JSON)  # Security flags
    threat_level = Column(String(20), default='low')  # low, medium, high, critical
    
    # Decision Performance
    decision_time = Column(Float, default=0.0)  # Decision time in milliseconds
    decision_accuracy = Column(Float, default=100.0)  # Decision accuracy
    decision_confidence = Column(Float, default=100.0)  # Decision confidence
    
    # Metadata
    decision_timestamp = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")

# Access Control Audit
class AccessControlAudit(Base):
    __tablename__ = 'access_control_audits'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    audit_type = Column(String(50), nullable=False)  # access, permission, policy, rule
    audit_action = Column(String(50), nullable=False)  # granted, denied, modified, revoked
    
    # Audit Details
    audit_resource = Column(String(255))  # Audited resource
    audit_operation = Column(String(100))  # Audited operation
    audit_reason = Column(Text)  # Audit reason
    audit_data = Column(JSON)  # Audit data
    
    # Audit Context
    audit_ip = Column(String(45))
    audit_user_agent = Column(Text)
    audit_location = Column(JSON)  # Geographic location
    audit_device = Column(JSON)  # Device information
    
    # Audit Result
    audit_result = Column(String(50), nullable=False)  # success, failure, error
    audit_message = Column(Text)
    audit_impact = Column(String(50))  # low, medium, high, critical
    
    # Audit Security
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)
    risk_score = Column(Float, default=0.0)  # 0-100 risk score
    security_flags = Column(JSON)  # Security flags
    
    # Audit Compliance
    compliance_required = Column(Boolean, default=False)
    compliance_status = Column(String(50))  # compliant, non-compliant, pending
    compliance_notes = Column(Text)
    
    # Metadata
    audit_timestamp = Column(DateTime, default=datetime.utcnow)
    audited_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    auditor = relationship("User", foreign_keys=[audited_by])

# Access Control Monitoring
class AccessControlMonitoring(Base):
    __tablename__ = 'access_control_monitoring'
    
    id = Column(Integer, primary_key=True, index=True)
    monitoring_name = Column(String(255), nullable=False)
    monitoring_type = Column(String(50), nullable=False)  # real-time, scheduled, event-driven
    monitoring_description = Column(Text)
    
    # Monitoring Configuration
    monitoring_config = Column(JSON, nullable=False)  # Monitoring configuration
    monitoring_rules = Column(JSON, nullable=False)  # Monitoring rules
    monitoring_thresholds = Column(JSON)  # Monitoring thresholds
    monitoring_alerts = Column(JSON)  # Monitoring alerts
    
    # Monitoring Scope
    monitoring_scope = Column(JSON)  # Monitoring scope
    monitoring_subjects = Column(JSON)  # Monitoring subjects
    monitoring_resources = Column(JSON)  # Monitoring resources
    monitoring_operations = Column(JSON)  # Monitoring operations
    
    # Monitoring Status
    is_active = Column(Boolean, default=True)
    monitoring_frequency = Column(String(50))  # real-time, hourly, daily, weekly
    monitoring_duration = Column(Integer)  # Monitoring duration in minutes
    
    # Monitoring Performance
    monitoring_accuracy = Column(Float, default=100.0)  # Monitoring accuracy
    monitoring_response_time = Column(Float, default=0.0)  # Response time in milliseconds
    monitoring_throughput = Column(Float, default=0.0)  # Throughput per second
    
    # Monitoring Results
    monitoring_results = Column(JSON)  # Monitoring results
    monitoring_insights = Column(JSON)  # Monitoring insights
    monitoring_recommendations = Column(JSON)  # Monitoring recommendations
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Access Control Reports
class AccessControlReport(Base):
    __tablename__ = 'access_control_reports'
    
    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # access, permission, policy, compliance
    report_description = Column(Text)
    
    # Report Configuration
    report_config = Column(JSON, nullable=False)  # Report configuration
    report_filters = Column(JSON)  # Report filters
    report_grouping = Column(JSON)  # Report grouping
    report_sorting = Column(JSON)  # Report sorting
    
    # Report Data
    report_data = Column(JSON)  # Report data
    report_summary = Column(JSON)  # Report summary
    report_insights = Column(JSON)  # Report insights
    report_recommendations = Column(JSON)  # Report recommendations
    
    # Report Settings
    is_scheduled = Column(Boolean, default=False)
    schedule_frequency = Column(String(20))  # daily, weekly, monthly
    next_run = Column(DateTime)
    recipients = Column(JSON)  # Report recipients
    
    # Report Status
    report_status = Column(String(20), default='active')  # active, paused, archived
    last_generated = Column(DateTime)
    generation_count = Column(Integer, default=0)
    
    # Report Security
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)
    requires_approval = Column(Boolean, default=False)
    approval_status = Column(String(50))  # pending, approved, rejected
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Access Control Compliance
class AccessControlCompliance(Base):
    __tablename__ = 'access_control_compliance'
    
    id = Column(Integer, primary_key=True, index=True)
    compliance_name = Column(String(255), nullable=False)
    compliance_type = Column(String(50), nullable=False)  # gdpr, hipaa, sox, pci, iso27001
    compliance_description = Column(Text)
    
    # Compliance Configuration
    compliance_rules = Column(JSON, nullable=False)  # Compliance rules
    compliance_requirements = Column(JSON)  # Compliance requirements
    compliance_controls = Column(JSON)  # Compliance controls
    compliance_metrics = Column(JSON)  # Compliance metrics
    
    # Compliance Status
    compliance_status = Column(String(50), default='pending')  # pending, compliant, non-compliant, exempt
    compliance_score = Column(Float, default=0.0)  # 0-100 compliance score
    compliance_rating = Column(String(20))  # excellent, good, fair, poor, critical
    
    # Compliance Monitoring
    monitoring_frequency = Column(String(50))  # real-time, daily, weekly, monthly
    monitoring_thresholds = Column(JSON)  # Monitoring thresholds
    monitoring_alerts = Column(JSON)  # Monitoring alerts
    monitoring_reports = Column(JSON)  # Monitoring reports
    
    # Compliance Audit
    audit_required = Column(Boolean, default=True)
    audit_frequency = Column(String(50))  # monthly, quarterly, annually
    last_audit = Column(DateTime)
    next_audit = Column(DateTime)
    audit_results = Column(JSON)  # Audit results
    
    # Compliance Actions
    action_required = Column(Boolean, default=False)
    action_plan = Column(JSON)  # Action plan
    action_owner = Column(Integer, ForeignKey('users.id'))
    action_deadline = Column(DateTime)
    action_status = Column(String(50))  # pending, in-progress, completed, overdue
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")
    owner = relationship("User", foreign_keys=[action_owner])
