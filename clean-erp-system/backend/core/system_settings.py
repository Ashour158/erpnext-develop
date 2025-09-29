# System Settings Management
# Comprehensive system configuration and settings

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class SettingCategory(enum.Enum):
    GENERAL = "General"
    SECURITY = "Security"
    NOTIFICATIONS = "Notifications"
    INTEGRATIONS = "Integrations"
    WORKFLOWS = "Workflows"
    APPEARANCE = "Appearance"
    BACKUP = "Backup"
    MONITORING = "Monitoring"

class SystemSetting(BaseModel):
    """System settings model"""
    __tablename__ = 'system_settings'
    
    # Basic Settings
    setting_key = db.Column(db.String(200), unique=True, nullable=False)
    setting_name = db.Column(db.String(200), nullable=False)
    setting_description = db.Column(db.Text)
    category = db.Column(db.Enum(SettingCategory), nullable=False)
    
    # Setting Configuration
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(50), default='string')  # string, number, boolean, json, array
    default_value = db.Column(db.Text)
    is_required = db.Column(db.Boolean, default=False)
    is_encrypted = db.Column(db.Boolean, default=False)
    
    # Validation
    validation_rules = db.Column(db.JSON)  # Validation rules for the setting
    allowed_values = db.Column(db.JSON)  # Allowed values for the setting
    
    # UI Configuration
    display_order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)
    is_editable = db.Column(db.Boolean, default=True)
    help_text = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'setting_key': self.setting_key,
            'setting_name': self.setting_name,
            'setting_description': self.setting_description,
            'category': self.category.value if self.category else None,
            'setting_value': self.setting_value,
            'setting_type': self.setting_type,
            'default_value': self.default_value,
            'is_required': self.is_required,
            'is_encrypted': self.is_encrypted,
            'validation_rules': self.validation_rules,
            'allowed_values': self.allowed_values,
            'display_order': self.display_order,
            'is_visible': self.is_visible,
            'is_editable': self.is_editable,
            'help_text': self.help_text,
            'company_id': self.company_id
        })
        return data

class Department(BaseModel):
    """Department model"""
    __tablename__ = 'departments'
    
    # Department Information
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Hierarchy
    parent_department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    parent_department = relationship("Department", remote_side=[id])
    child_departments = relationship("Department", back_populates="parent_department")
    
    # Department Head
    department_head_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    department_head = relationship("Employee")
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    budget_limit = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'parent_department_id': self.parent_department_id,
            'department_head_id': self.department_head_id,
            'is_active': self.is_active,
            'budget_limit': self.budget_limit,
            'currency': self.currency,
            'company_id': self.company_id
        })
        return data

class UserProfile(BaseModel):
    """User profile model"""
    __tablename__ = 'user_profiles'
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Profile Settings
    display_name = db.Column(db.String(200))
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(255))
    cover_photo = db.Column(db.String(255))
    
    # Contact Information
    personal_email = db.Column(db.String(120))
    personal_phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    location = db.Column(db.String(200))
    
    # Preferences
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(10), default='en')
    date_format = db.Column(db.String(20), default='YYYY-MM-DD')
    time_format = db.Column(db.String(20), default='24h')
    
    # Notification Preferences
    email_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    
    # Privacy Settings
    is_public = db.Column(db.Boolean, default=True)
    allow_following = db.Column(db.Boolean, default=True)
    allow_messages = db.Column(db.Boolean, default=True)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'display_name': self.display_name,
            'bio': self.bio,
            'profile_picture': self.profile_picture,
            'cover_photo': self.cover_photo,
            'personal_email': self.personal_email,
            'personal_phone': self.personal_phone,
            'website': self.website,
            'location': self.location,
            'timezone': self.timezone,
            'language': self.language,
            'date_format': self.date_format,
            'time_format': self.time_format,
            'email_notifications': self.email_notifications,
            'push_notifications': self.push_notifications,
            'sms_notifications': self.sms_notifications,
            'is_public': self.is_public,
            'allow_following': self.allow_following,
            'allow_messages': self.allow_messages,
            'company_id': self.company_id
        })
        return data

class WorkflowTemplate(BaseModel):
    """Workflow template model"""
    __tablename__ = 'workflow_templates'
    
    # Template Information
    template_name = db.Column(db.String(200), nullable=False)
    template_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Template Configuration
    template_config = db.Column(db.JSON)  # Template configuration
    workflow_steps = db.Column(db.JSON)  # Workflow steps configuration
    approval_rules = db.Column(db.JSON)  # Approval rules configuration
    
    # Template Settings
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Usage Statistics
    usage_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'template_name': self.template_name,
            'template_code': self.template_code,
            'description': self.description,
            'template_config': self.template_config,
            'workflow_steps': self.workflow_steps,
            'approval_rules': self.approval_rules,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'is_featured': self.is_featured,
            'usage_count': self.usage_count,
            'rating': self.rating,
            'company_id': self.company_id
        })
        return data

class ApprovalSystem(BaseModel):
    """Approval system model"""
    __tablename__ = 'approval_systems'
    
    # Approval System Information
    system_name = db.Column(db.String(200), nullable=False)
    system_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Approval Configuration
    approval_rules = db.Column(db.JSON)  # Approval rules configuration
    approval_levels = db.Column(db.JSON)  # Approval levels configuration
    escalation_rules = db.Column(db.JSON)  # Escalation rules configuration
    
    # System Settings
    is_active = db.Column(db.Boolean, default=True)
    requires_approval = db.Column(db.Boolean, default=True)
    auto_approve = db.Column(db.Boolean, default=False)
    approval_timeout = db.Column(db.Integer, default=24)  # hours
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'system_name': self.system_name,
            'system_code': self.system_code,
            'description': self.description,
            'approval_rules': self.approval_rules,
            'approval_levels': self.approval_levels,
            'escalation_rules': self.escalation_rules,
            'is_active': self.is_active,
            'requires_approval': self.requires_approval,
            'auto_approve': self.auto_approve,
            'approval_timeout': self.approval_timeout,
            'company_id': self.company_id
        })
        return data
