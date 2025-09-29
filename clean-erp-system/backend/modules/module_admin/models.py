# Module Admin Models
# Module-specific administration and control panels

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class ModuleAdminLevel(enum.Enum):
    MODULE_SUPER_ADMIN = "module_super_admin"
    MODULE_ADMIN = "module_admin"
    MODULE_MANAGER = "module_manager"
    MODULE_LEAD = "module_lead"
    MODULE_USER = "module_user"

class ModuleFeatureStatus(enum.Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"

class ModuleConfigType(enum.Enum):
    GENERAL = "general"
    SECURITY = "security"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"
    CUSTOMIZATION = "customization"

# Module Administration
class ModuleAdmin(Base):
    __tablename__ = 'module_admins'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('system_modules.id'), nullable=False)
    
    # Admin Details
    admin_level = Column(Enum(ModuleAdminLevel), nullable=False)
    admin_permissions = Column(JSON, nullable=False)  # Module admin permissions
    admin_scope = Column(JSON)  # Admin scope within module
    
    # Admin Status
    is_active = Column(Boolean, default=True)
    can_manage_users = Column(Boolean, default=False)
    can_manage_settings = Column(Boolean, default=False)
    can_manage_data = Column(Boolean, default=False)
    can_manage_integrations = Column(Boolean, default=False)
    
    # Admin Audit
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    admin_actions = Column(JSON)  # Admin actions log
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    module = relationship("SystemModule")
    creator = relationship("User", foreign_keys=[created_by])

# Module Configuration
class ModuleConfiguration(Base):
    __tablename__ = 'module_configurations'
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey('system_modules.id'), nullable=False)
    
    # Configuration Details
    config_type = Column(Enum(ModuleConfigType), nullable=False)
    config_key = Column(String(255), nullable=False)
    config_value = Column(Text, nullable=False)
    config_description = Column(Text)
    
    # Configuration Settings
    config_category = Column(String(100))  # Configuration category
    config_scope = Column(String(50))  # global, department, user
    config_validation = Column(JSON)  # Validation rules
    config_options = Column(JSON)  # Available options
    
    # Configuration Status
    is_active = Column(Boolean, default=True)
    is_readonly = Column(Boolean, default=False)
    requires_restart = Column(Boolean, default=False)
    
    # Configuration Access
    access_level = Column(String(50), default='admin')  # admin, manager, user
    requires_approval = Column(Boolean, default=False)
    approval_status = Column(String(50), default='pending')  # pending, approved, rejected
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    module = relationship("SystemModule")
    creator = relationship("User")

# Module Features
class ModuleFeature(Base):
    __tablename__ = 'module_features'
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey('system_modules.id'), nullable=False)
    
    # Feature Details
    feature_name = Column(String(255), nullable=False)
    feature_display_name = Column(String(255), nullable=False)
    feature_description = Column(Text)
    feature_version = Column(String(50), default='1.0.0')
    
    # Feature Configuration
    feature_status = Column(Enum(ModuleFeatureStatus), default=ModuleFeatureStatus.ENABLED)
    feature_permissions = Column(JSON)  # Feature permissions
    feature_settings = Column(JSON)  # Feature settings
    feature_dependencies = Column(JSON)  # Feature dependencies
    
    # Feature Access Control
    access_level = Column(String(50), default='user')  # admin, manager, user, guest
    requires_permission = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    
    # Feature Performance
    feature_usage_count = Column(Integer, default=0)
    feature_performance_score = Column(Float, default=0.0)  # 0-100
    feature_error_count = Column(Integer, default=0)
    feature_last_used = Column(DateTime)
    
    # Feature Status
    is_active = Column(Boolean, default=True)
    is_system_feature = Column(Boolean, default=False)
    is_experimental = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    module = relationship("SystemModule")
    creator = relationship("User")

# Module User Access
class ModuleUserAccess(Base):
    __tablename__ = 'module_user_access'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('system_modules.id'), nullable=False)
    
    # Access Configuration
    access_level = Column(String(50), nullable=False)  # admin, manager, user, guest
    access_permissions = Column(JSON)  # User permissions within module
    access_scope = Column(JSON)  # Access scope
    access_restrictions = Column(JSON)  # Access restrictions
    
    # Access Control
    can_read = Column(Boolean, default=True)
    can_write = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_export = Column(Boolean, default=False)
    can_import = Column(Boolean, default=False)
    can_admin = Column(Boolean, default=False)
    
    # Access Status
    is_active = Column(Boolean, default=True)
    access_granted_at = Column(DateTime, default=datetime.utcnow)
    access_granted_by = Column(Integer, ForeignKey('users.id'))
    access_expires_at = Column(DateTime)
    
    # Access Usage
    last_accessed = Column(DateTime)
    access_count = Column(Integer, default=0)
    usage_hours = Column(Float, default=0.0)
    usage_analytics = Column(JSON)  # Usage analytics
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    module = relationship("SystemModule")
    granter = relationship("User", foreign_keys=[access_granted_by])

# Module Department Access
class ModuleDepartmentAccess(Base):
    __tablename__ = 'module_department_access'
    
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('system_modules.id'), nullable=False)
    
    # Access Configuration
    access_level = Column(String(50), nullable=False)  # admin, manager, user, guest
    access_permissions = Column(JSON)  # Department permissions within module
    access_scope = Column(JSON)  # Access scope
    access_restrictions = Column(JSON)  # Access restrictions
    
    # Access Control
    can_read = Column(Boolean, default=True)
    can_write = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_export = Column(Boolean, default=False)
    can_import = Column(Boolean, default=False)
    can_admin = Column(Boolean, default=False)
    
    # Access Status
    is_active = Column(Boolean, default=True)
    access_granted_at = Column(DateTime, default=datetime.utcnow)
    access_granted_by = Column(Integer, ForeignKey('users.id'))
    access_expires_at = Column(DateTime)
    
    # Access Usage
    department_usage_count = Column(Integer, default=0)
    department_usage_hours = Column(Float, default=0.0)
    department_usage_analytics = Column(JSON)  # Usage analytics
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    department = relationship("Department")
    module = relationship("SystemModule")
    granter = relationship("User")

# Module Integrations
class ModuleIntegration(Base):
    __tablename__ = 'module_integrations'
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey('system_modules.id'), nullable=False)
    
    # Integration Details
    integration_name = Column(String(255), nullable=False)
    integration_type = Column(String(100), nullable=False)  # api, webhook, database, file
    integration_provider = Column(String(100))  # Integration provider
    integration_endpoint = Column(String(500))  # Integration endpoint
    
    # Integration Configuration
    integration_config = Column(JSON, nullable=False)  # Integration configuration
    integration_credentials = Column(JSON)  # Integration credentials (encrypted)
    integration_settings = Column(JSON)  # Integration settings
    integration_mapping = Column(JSON)  # Data mapping configuration
    
    # Integration Status
    integration_status = Column(String(50), default='active')  # active, inactive, error
    integration_health = Column(String(50), default='healthy')  # healthy, warning, critical
    integration_last_sync = Column(DateTime)
    integration_sync_count = Column(Integer, default=0)
    integration_error_count = Column(Integer, default=0)
    
    # Integration Performance
    integration_response_time = Column(Float, default=0.0)  # Response time in milliseconds
    integration_success_rate = Column(Float, default=100.0)  # Success rate percentage
    integration_throughput = Column(Float, default=0.0)  # Throughput per minute
    
    # Integration Security
    integration_security_level = Column(String(50), default='standard')  # low, standard, high, critical
    integration_encryption = Column(Boolean, default=True)
    integration_authentication = Column(String(100))  # Authentication method
    integration_authorization = Column(JSON)  # Authorization configuration
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    module = relationship("SystemModule")
    creator = relationship("User")

# Module Analytics
class ModuleAnalytics(Base):
    __tablename__ = 'module_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey('system_modules.id'), nullable=False)
    
    # Analytics Details
    analytics_type = Column(String(50), nullable=False)  # usage, performance, error, user
    analytics_period = Column(String(50), nullable=False)  # daily, weekly, monthly, quarterly
    analytics_date = Column(DateTime, nullable=False)
    
    # Analytics Data
    analytics_data = Column(JSON, nullable=False)  # Analytics data
    analytics_metrics = Column(JSON, nullable=False)  # Key metrics
    analytics_insights = Column(JSON)  # Analytics insights
    analytics_recommendations = Column(JSON)  # Recommendations
    
    # Performance Metrics
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    average_session_duration = Column(Float, default=0.0)  # Minutes
    
    # Usage Metrics
    feature_usage = Column(JSON)  # Feature usage statistics
    user_engagement = Column(Float, default=0.0)  # User engagement score
    module_adoption = Column(Float, default=0.0)  # Module adoption rate
    
    # Performance Metrics
    response_time = Column(Float, default=0.0)  # Average response time
    error_rate = Column(Float, default=0.0)  # Error rate percentage
    availability = Column(Float, default=100.0)  # Availability percentage
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    module = relationship("SystemModule")

# Module Alerts
class ModuleAlert(Base):
    __tablename__ = 'module_alerts'
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey('system_modules.id'), nullable=False)
    
    # Alert Details
    alert_name = Column(String(255), nullable=False)
    alert_type = Column(String(50), nullable=False)  # performance, error, security, usage
    alert_severity = Column(String(20), nullable=False)  # low, medium, high, critical
    alert_message = Column(Text, nullable=False)
    
    # Alert Configuration
    alert_conditions = Column(JSON, nullable=False)  # Alert conditions
    alert_thresholds = Column(JSON)  # Alert thresholds
    alert_actions = Column(JSON)  # Alert actions
    alert_recipients = Column(JSON)  # Alert recipients
    
    # Alert Status
    alert_status = Column(String(50), default='active')  # active, inactive, triggered, resolved
    is_enabled = Column(Boolean, default=True)
    last_triggered = Column(DateTime)
    trigger_count = Column(Integer, default=0)
    
    # Alert Performance
    alert_response_time = Column(Float, default=0.0)  # Response time in milliseconds
    alert_success_rate = Column(Float, default=100.0)  # Success rate percentage
    alert_false_positive_rate = Column(Float, default=0.0)  # False positive rate
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    module = relationship("SystemModule")
    creator = relationship("User")

# Module Reports
class ModuleReport(Base):
    __tablename__ = 'module_reports'
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey('system_modules.id'), nullable=False)
    
    # Report Details
    report_name = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # usage, performance, error, user, custom
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
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    module = relationship("SystemModule")
    creator = relationship("User")
