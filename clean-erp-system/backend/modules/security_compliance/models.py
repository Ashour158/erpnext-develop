# Security & Compliance Models
# Models for security and compliance features including data privacy controls, audit trails, encryption, and access controls

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime, time, date, timedelta
import enum

class AuditAction(enum.Enum):
    CREATE = "Create"
    READ = "Read"
    UPDATE = "Update"
    DELETE = "Delete"
    LOGIN = "Login"
    LOGOUT = "Logout"
    EXPORT = "Export"
    IMPORT = "Import"
    BACKUP = "Backup"
    RESTORE = "Restore"
    CUSTOM = "Custom"

class AuditLevel(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class DataClassification(enum.Enum):
    PUBLIC = "Public"
    INTERNAL = "Internal"
    CONFIDENTIAL = "Confidential"
    RESTRICTED = "Restricted"

class EncryptionType(enum.Enum):
    AES256 = "AES256"
    RSA = "RSA"
    ECC = "ECC"
    CUSTOM = "Custom"

class ComplianceStandard(enum.Enum):
    GDPR = "GDPR"
    CCPA = "CCPA"
    HIPAA = "HIPAA"
    SOX = "SOX"
    PCI_DSS = "PCI DSS"
    ISO27001 = "ISO 27001"
    CUSTOM = "Custom"

class AuditLog(BaseModel):
    """Audit log model"""
    __tablename__ = 'audit_logs'
    
    # Audit Information
    action = db.Column(db.Enum(AuditAction), nullable=False)
    action_description = db.Column(db.Text)
    audit_level = db.Column(db.Enum(AuditLevel), default=AuditLevel.MEDIUM)
    
    # Entity Information
    entity_type = db.Column(db.String(100), nullable=False)
    entity_id = db.Column(db.String(100), nullable=False)
    entity_name = db.Column(db.String(200))
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    user_ip = db.Column(db.String(45))  # IPv4 or IPv6
    user_agent = db.Column(db.Text)
    session_id = db.Column(db.String(100))
    
    # Change Information
    old_values = db.Column(db.JSON)  # Previous values
    new_values = db.Column(db.JSON)  # New values
    changed_fields = db.Column(db.JSON)  # List of changed fields
    
    # Additional Data
    metadata = db.Column(db.JSON)  # Additional audit metadata
    tags = db.Column(db.JSON)  # Audit tags for categorization
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'action': self.action.value if self.action else None,
            'action_description': self.action_description,
            'audit_level': self.audit_level.value if self.audit_level else None,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'entity_name': self.entity_name,
            'user_id': self.user_id,
            'user_ip': self.user_ip,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'changed_fields': self.changed_fields,
            'metadata': self.metadata,
            'tags': self.tags,
            'company_id': self.company_id
        })
        return data

class DataPrivacyRule(BaseModel):
    """Data privacy rule model"""
    __tablename__ = 'data_privacy_rules'
    
    # Rule Information
    rule_name = db.Column(db.String(200), nullable=False)
    rule_description = db.Column(db.Text)
    rule_type = db.Column(db.String(100), nullable=False)  # Retention, Anonymization, Encryption, etc.
    is_active = db.Column(db.Boolean, default=True)
    
    # Data Classification
    data_classification = db.Column(db.Enum(DataClassification), nullable=False)
    data_types = db.Column(db.JSON)  # List of data types this rule applies to
    data_fields = db.Column(db.JSON)  # List of specific fields
    
    # Rule Configuration
    rule_config = db.Column(db.JSON)  # Rule-specific configuration
    retention_period = db.Column(db.Integer, default=0)  # days
    anonymization_method = db.Column(db.String(100))
    encryption_required = db.Column(db.Boolean, default=False)
    
    # Compliance
    compliance_standards = db.Column(db.JSON)  # List of compliance standards
    legal_basis = db.Column(db.String(200))
    consent_required = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'rule_name': self.rule_name,
            'rule_description': self.rule_description,
            'rule_type': self.rule_type,
            'is_active': self.is_active,
            'data_classification': self.data_classification.value if self.data_classification else None,
            'data_types': self.data_types,
            'data_fields': self.data_fields,
            'rule_config': self.rule_config,
            'retention_period': self.retention_period,
            'anonymization_method': self.anonymization_method,
            'encryption_required': self.encryption_required,
            'compliance_standards': self.compliance_standards,
            'legal_basis': self.legal_basis,
            'consent_required': self.consent_required,
            'company_id': self.company_id
        })
        return data

class DataRetentionPolicy(BaseModel):
    """Data retention policy model"""
    __tablename__ = 'data_retention_policies'
    
    # Policy Information
    policy_name = db.Column(db.String(200), nullable=False)
    policy_description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Data Scope
    data_types = db.Column(db.JSON)  # List of data types
    data_classification = db.Column(db.Enum(DataClassification), nullable=False)
    entity_types = db.Column(db.JSON)  # List of entity types
    
    # Retention Rules
    retention_period = db.Column(db.Integer, nullable=False)  # days
    retention_unit = db.Column(db.String(20), default='days')  # days, months, years
    auto_delete = db.Column(db.Boolean, default=False)
    archive_before_delete = db.Column(db.Boolean, default=True)
    
    # Compliance
    compliance_standards = db.Column(db.JSON)  # List of compliance standards
    legal_requirements = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'policy_name': self.policy_name,
            'policy_description': self.policy_description,
            'is_active': self.is_active,
            'data_types': self.data_types,
            'data_classification': self.data_classification.value if self.data_classification else None,
            'entity_types': self.entity_types,
            'retention_period': self.retention_period,
            'retention_unit': self.retention_unit,
            'auto_delete': self.auto_delete,
            'archive_before_delete': self.archive_before_delete,
            'compliance_standards': self.compliance_standards,
            'legal_requirements': self.legal_requirements,
            'company_id': self.company_id
        })
        return data

class EncryptionKey(BaseModel):
    """Encryption key model"""
    __tablename__ = 'encryption_keys'
    
    # Key Information
    key_name = db.Column(db.String(200), nullable=False)
    key_description = db.Column(db.Text)
    key_type = db.Column(db.Enum(EncryptionType), nullable=False)
    key_size = db.Column(db.Integer, default=256)  # bits
    
    # Key Data
    key_data = db.Column(db.Text, nullable=False)  # Encrypted key data
    key_hash = db.Column(db.String(64))  # SHA-256 hash of the key
    
    # Key Management
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    creator = relationship("Employee")
    expires_at = db.Column(db.DateTime)
    last_used = db.Column(db.DateTime)
    
    # Usage Information
    usage_count = db.Column(db.Integer, default=0)
    max_usage = db.Column(db.Integer, default=0)  # 0 = unlimited
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'key_name': self.key_name,
            'key_description': self.key_description,
            'key_type': self.key_type.value if self.key_type else None,
            'key_size': self.key_size,
            'key_data': self.key_data,
            'key_hash': self.key_hash,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count,
            'max_usage': self.max_usage,
            'company_id': self.company_id
        })
        return data

class AccessControl(BaseModel):
    """Access control model"""
    __tablename__ = 'access_controls'
    
    # Access Information
    resource_type = db.Column(db.String(100), nullable=False)
    resource_id = db.Column(db.String(100), nullable=False)
    resource_name = db.Column(db.String(200))
    
    # User/Role Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    user = relationship("Employee")
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = relationship("Role")
    
    # Permissions
    permissions = db.Column(db.JSON)  # List of permissions
    access_level = db.Column(db.String(50), default='Read')  # Read, Write, Admin
    is_granted = db.Column(db.Boolean, default=True)
    
    # Access Control
    ip_restrictions = db.Column(db.JSON)  # List of allowed IP addresses
    time_restrictions = db.Column(db.JSON)  # Time-based restrictions
    location_restrictions = db.Column(db.JSON)  # Location-based restrictions
    
    # Expiration
    expires_at = db.Column(db.DateTime)
    is_temporary = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'user_id': self.user_id,
            'role_id': self.role_id,
            'permissions': self.permissions,
            'access_level': self.access_level,
            'is_granted': self.is_granted,
            'ip_restrictions': self.ip_restrictions,
            'time_restrictions': self.time_restrictions,
            'location_restrictions': self.location_restrictions,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_temporary': self.is_temporary,
            'company_id': self.company_id
        })
        return data

class SecurityIncident(BaseModel):
    """Security incident model"""
    __tablename__ = 'security_incidents'
    
    # Incident Information
    incident_title = db.Column(db.String(200), nullable=False)
    incident_description = db.Column(db.Text)
    incident_type = db.Column(db.String(100), nullable=False)  # Data Breach, Unauthorized Access, etc.
    severity = db.Column(db.Enum(AuditLevel), nullable=False)
    
    # Incident Details
    incident_date = db.Column(db.DateTime, default=datetime.utcnow)
    discovered_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    discoverer = relationship("Employee")
    affected_users = db.Column(db.JSON)  # List of affected user IDs
    affected_data = db.Column(db.JSON)  # List of affected data types
    
    # Status
    status = db.Column(db.String(50), default='Open')  # Open, Investigating, Resolved, Closed
    assigned_to = db.Column(db.Integer, db.ForeignKey('employees.id'))
    assignee = relationship("Employee", foreign_keys=[assigned_to])
    resolution_notes = db.Column(db.Text)
    resolved_at = db.Column(db.DateTime)
    
    # Impact Assessment
    impact_level = db.Column(db.String(50), default='Low')  # Low, Medium, High, Critical
    data_compromised = db.Column(db.Boolean, default=False)
    systems_affected = db.Column(db.JSON)  # List of affected systems
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'incident_title': self.incident_title,
            'incident_description': self.incident_description,
            'incident_type': self.incident_type,
            'severity': self.severity.value if self.severity else None,
            'incident_date': self.incident_date.isoformat() if self.incident_date else None,
            'discovered_by': self.discovered_by,
            'affected_users': self.affected_users,
            'affected_data': self.affected_data,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'resolution_notes': self.resolution_notes,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'impact_level': self.impact_level,
            'data_compromised': self.data_compromised,
            'systems_affected': self.systems_affected,
            'company_id': self.company_id
        })
        return data

class ComplianceReport(BaseModel):
    """Compliance report model"""
    __tablename__ = 'compliance_reports'
    
    # Report Information
    report_name = db.Column(db.String(200), nullable=False)
    report_description = db.Column(db.Text)
    compliance_standard = db.Column(db.Enum(ComplianceStandard), nullable=False)
    report_period_start = db.Column(db.Date, nullable=False)
    report_period_end = db.Column(db.Date, nullable=False)
    
    # Report Status
    status = db.Column(db.String(50), default='Draft')  # Draft, Review, Approved, Published
    generated_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    generator = relationship("Employee")
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Report Data
    report_data = db.Column(db.JSON)  # Report data
    findings = db.Column(db.JSON)  # Compliance findings
    recommendations = db.Column(db.JSON)  # Recommendations
    violations = db.Column(db.JSON)  # Compliance violations
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'report_name': self.report_name,
            'report_description': self.report_description,
            'compliance_standard': self.compliance_standard.value if self.compliance_standard else None,
            'report_period_start': self.report_period_start.isoformat() if self.report_period_start else None,
            'report_period_end': self.report_period_end.isoformat() if self.report_period_end else None,
            'status': self.status,
            'generated_by': self.generated_by,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'report_data': self.report_data,
            'findings': self.findings,
            'recommendations': self.recommendations,
            'violations': self.violations,
            'company_id': self.company_id
        })
        return data

class DataAnonymization(BaseModel):
    """Data anonymization model"""
    __tablename__ = 'data_anonymizations'
    
    # Anonymization Information
    anonymization_name = db.Column(db.String(200), nullable=False)
    anonymization_description = db.Column(db.Text)
    anonymization_method = db.Column(db.String(100), nullable=False)  # Masking, Hashing, etc.
    
    # Data Information
    data_type = db.Column(db.String(100), nullable=False)
    data_classification = db.Column(db.Enum(DataClassification), nullable=False)
    original_data = db.Column(db.Text)  # Original data (encrypted)
    anonymized_data = db.Column(db.Text)  # Anonymized data
    
    # Anonymization Details
    anonymization_config = db.Column(db.JSON)  # Anonymization configuration
    anonymization_date = db.Column(db.DateTime, default=datetime.utcnow)
    anonymized_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    anonymizer = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'anonymization_name': self.anonymization_name,
            'anonymization_description': self.anonymization_description,
            'anonymization_method': self.anonymization_method,
            'data_type': self.data_type,
            'data_classification': self.data_classification.value if self.data_classification else None,
            'original_data': self.original_data,
            'anonymized_data': self.anonymized_data,
            'anonymization_config': self.anonymization_config,
            'anonymization_date': self.anonymization_date.isoformat() if self.anonymization_date else None,
            'anonymized_by': self.anonymized_by,
            'company_id': self.company_id
        })
        return data
