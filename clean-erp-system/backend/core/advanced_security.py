# Advanced Security Features
# Comprehensive security implementation with advanced features

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum
import hashlib
import secrets
import jwt
from cryptography.fernet import Fernet
import bcrypt

class SecurityLevel(enum.Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"

class ThreatLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEventType(enum.Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    FAILED_LOGIN = "failed_login"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_CHANGE = "permission_change"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SECURITY_BREACH = "security_breach"

# Advanced Authentication
class AdvancedAuthentication(Base):
    __tablename__ = 'advanced_authentication'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Multi-Factor Authentication
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))  # TOTP secret
    mfa_backup_codes = Column(JSON)  # Backup codes
    mfa_phone = Column(String(20))  # Phone for SMS
    mfa_email = Column(String(255))  # Email for backup
    
    # Biometric Authentication
    biometric_enabled = Column(Boolean, default=False)
    biometric_data = Column(Text)  # Encrypted biometric data
    biometric_type = Column(String(50))  # fingerprint, face, voice, etc.
    
    # Hardware Security Keys
    security_key_enabled = Column(Boolean, default=False)
    security_key_public_key = Column(Text)  # Public key for hardware key
    security_key_attestation = Column(Text)  # Attestation data
    
    # Risk-Based Authentication
    risk_score = Column(Float, default=0.0)  # 0-100 risk score
    risk_factors = Column(JSON)  # Risk factors
    adaptive_auth_enabled = Column(Boolean, default=False)
    
    # Session Management
    session_timeout = Column(Integer, default=480)  # Minutes
    concurrent_sessions = Column(Integer, default=1)
    session_encryption = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")

# Security Policies
class SecurityPolicy(Base):
    __tablename__ = 'security_policies'
    
    id = Column(Integer, primary_key=True, index=True)
    policy_name = Column(String(255), nullable=False)
    policy_type = Column(String(50), nullable=False)  # password, session, access, data, network
    policy_description = Column(Text)
    
    # Policy Configuration
    policy_rules = Column(JSON, nullable=False)  # Policy rules
    policy_conditions = Column(JSON)  # Policy conditions
    policy_actions = Column(JSON)  # Policy actions
    policy_priority = Column(Integer, default=0)  # Policy priority
    
    # Policy Security
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)
    policy_scope = Column(JSON)  # Policy scope
    policy_applies_to = Column(JSON)  # Who the policy applies to
    
    # Policy Status
    is_active = Column(Boolean, default=True)
    is_system_policy = Column(Boolean, default=False)
    policy_effective_date = Column(DateTime, default=datetime.utcnow)
    policy_expiry_date = Column(DateTime)
    
    # Policy Compliance
    compliance_required = Column(Boolean, default=True)
    compliance_monitoring = Column(Boolean, default=True)
    compliance_reporting = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Security Events
class SecurityEvent(Base):
    __tablename__ = 'security_events'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_id = Column(String(255))
    
    # Event Details
    event_type = Column(Enum(SecurityEventType), nullable=False)
    event_description = Column(Text, nullable=False)
    event_severity = Column(String(20), nullable=False)  # low, medium, high, critical
    event_category = Column(String(50))  # authentication, authorization, data, network
    
    # Event Context
    event_ip = Column(String(45))
    event_user_agent = Column(Text)
    event_location = Column(JSON)  # Geographic location
    event_device = Column(JSON)  # Device information
    event_browser = Column(JSON)  # Browser information
    
    # Event Data
    event_data = Column(JSON)  # Event-specific data
    event_metadata = Column(JSON)  # Event metadata
    event_risk_score = Column(Float, default=0.0)  # 0-100 risk score
    
    # Event Security
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)
    threat_level = Column(Enum(ThreatLevel), default=ThreatLevel.LOW)
    security_flags = Column(JSON)  # Security flags
    anomaly_score = Column(Float, default=0.0)  # Anomaly detection score
    
    # Event Response
    event_response = Column(JSON)  # Automated response actions
    event_escalated = Column(Boolean, default=False)
    event_resolved = Column(Boolean, default=False)
    event_resolution_notes = Column(Text)
    
    # Metadata
    event_timestamp = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")

# Threat Detection
class ThreatDetection(Base):
    __tablename__ = 'threat_detection'
    
    id = Column(Integer, primary_key=True, index=True)
    threat_name = Column(String(255), nullable=False)
    threat_type = Column(String(50), nullable=False)  # malware, phishing, brute_force, ddos, etc.
    threat_description = Column(Text)
    
    # Threat Configuration
    threat_rules = Column(JSON, nullable=False)  # Detection rules
    threat_patterns = Column(JSON)  # Threat patterns
    threat_indicators = Column(JSON)  # Threat indicators
    threat_thresholds = Column(JSON)  # Detection thresholds
    
    # Threat Detection
    detection_method = Column(String(50))  # signature, behavioral, machine_learning
    detection_accuracy = Column(Float, default=0.0)  # Detection accuracy
    false_positive_rate = Column(Float, default=0.0)  # False positive rate
    detection_speed = Column(Float, default=0.0)  # Detection speed in milliseconds
    
    # Threat Response
    response_actions = Column(JSON)  # Response actions
    response_automation = Column(Boolean, default=False)
    response_escalation = Column(JSON)  # Escalation rules
    
    # Threat Status
    is_active = Column(Boolean, default=True)
    threat_level = Column(Enum(ThreatLevel), default=ThreatLevel.MEDIUM)
    detection_count = Column(Integer, default=0)
    last_detection = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Security Monitoring
class SecurityMonitoring(Base):
    __tablename__ = 'security_monitoring'
    
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
    monitoring_targets = Column(JSON)  # Monitoring targets
    monitoring_metrics = Column(JSON)  # Monitoring metrics
    monitoring_frequency = Column(String(50))  # real-time, hourly, daily
    
    # Monitoring Status
    is_active = Column(Boolean, default=True)
    monitoring_duration = Column(Integer)  # Monitoring duration in minutes
    monitoring_interval = Column(Integer)  # Monitoring interval in seconds
    
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

# Data Encryption
class DataEncryption(Base):
    __tablename__ = 'data_encryption'
    
    id = Column(Integer, primary_key=True, index=True)
    encryption_name = Column(String(255), nullable=False)
    encryption_type = Column(String(50), nullable=False)  # aes, rsa, ecc, quantum
    encryption_description = Column(Text)
    
    # Encryption Configuration
    encryption_algorithm = Column(String(50), nullable=False)  # AES-256, RSA-4096, ECC-384
    encryption_key_size = Column(Integer, nullable=False)  # Key size in bits
    encryption_mode = Column(String(50))  # CBC, GCM, CTR, etc.
    encryption_padding = Column(String(50))  # PKCS7, OAEP, etc.
    
    # Key Management
    key_management = Column(JSON)  # Key management configuration
    key_rotation = Column(Boolean, default=True)
    key_rotation_interval = Column(Integer, default=90)  # Days
    key_backup = Column(Boolean, default=True)
    key_recovery = Column(JSON)  # Key recovery procedures
    
    # Encryption Status
    is_active = Column(Boolean, default=True)
    encryption_status = Column(String(50), default='active')  # active, inactive, deprecated
    encryption_performance = Column(Float, default=0.0)  # Encryption performance score
    
    # Encryption Usage
    encryption_count = Column(Integer, default=0)
    encryption_success_rate = Column(Float, default=100.0)  # Success rate percentage
    encryption_error_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Security Compliance
class SecurityCompliance(Base):
    __tablename__ = 'security_compliance'
    
    id = Column(Integer, primary_key=True, index=True)
    compliance_name = Column(String(255), nullable=False)
    compliance_type = Column(String(50), nullable=False)  # gdpr, hipaa, sox, pci, iso27001, nist
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

# Security Analytics
class SecurityAnalytics(Base):
    __tablename__ = 'security_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    analytics_name = Column(String(255), nullable=False)
    analytics_type = Column(String(50), nullable=False)  # threat, risk, compliance, performance
    analytics_period = Column(String(50), nullable=False)  # daily, weekly, monthly, quarterly
    
    # Analytics Data
    analytics_data = Column(JSON, nullable=False)  # Analytics data
    analytics_metrics = Column(JSON, nullable=False)  # Key metrics
    analytics_insights = Column(JSON)  # Analytics insights
    analytics_recommendations = Column(JSON)  # Recommendations
    
    # Security Metrics
    threat_count = Column(Integer, default=0)
    threat_severity = Column(Float, default=0.0)  # Average threat severity
    risk_score = Column(Float, default=0.0)  # Overall risk score
    compliance_score = Column(Float, default=0.0)  # Compliance score
    
    # Performance Metrics
    detection_accuracy = Column(Float, default=0.0)  # Detection accuracy
    response_time = Column(Float, default=0.0)  # Response time in milliseconds
    false_positive_rate = Column(Float, default=0.0)  # False positive rate
    security_effectiveness = Column(Float, default=0.0)  # Security effectiveness score
    
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
    events = relationship("SecurityEvent")

# Security Incident Response
class SecurityIncident(Base):
    __tablename__ = 'security_incidents'
    
    id = Column(Integer, primary_key=True, index=True)
    incident_name = Column(String(255), nullable=False)
    incident_type = Column(String(50), nullable=False)  # breach, malware, phishing, ddos, etc.
    incident_description = Column(Text)
    
    # Incident Details
    incident_severity = Column(Enum(ThreatLevel), nullable=False)
    incident_status = Column(String(50), default='open')  # open, investigating, contained, resolved
    incident_priority = Column(String(20), default='medium')  # low, medium, high, critical
    
    # Incident Context
    incident_source = Column(String(100))  # Source of the incident
    incident_target = Column(String(100))  # Target of the incident
    incident_scope = Column(JSON)  # Scope of the incident
    incident_impact = Column(JSON)  # Impact assessment
    
    # Incident Response
    response_team = Column(JSON)  # Response team members
    response_actions = Column(JSON)  # Response actions taken
    response_timeline = Column(JSON)  # Response timeline
    response_effectiveness = Column(Float, default=0.0)  # Response effectiveness
    
    # Incident Resolution
    resolution_notes = Column(Text)
    resolution_actions = Column(JSON)  # Resolution actions
    resolution_lessons = Column(JSON)  # Lessons learned
    resolution_prevention = Column(JSON)  # Prevention measures
    
    # Incident Timeline
    incident_discovered = Column(DateTime)
    incident_reported = Column(DateTime)
    incident_contained = Column(DateTime)
    incident_resolved = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")
