# System Admin Panel
# Comprehensive system administration with full control

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class SystemRole(enum.Enum):
    SUPER_ADMIN = "super_admin"
    SYSTEM_ADMIN = "system_admin"
    MODULE_ADMIN = "module_admin"
    DEPARTMENT_ADMIN = "department_admin"
    TEAM_LEADER = "team_leader"
    USER = "user"
    GUEST = "guest"

class ModuleStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"

class AccessLevel(enum.Enum):
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    FULL_ACCESS = "full_access"
    ADMIN = "admin"

class PermissionType(enum.Enum):
    MODULE_ACCESS = "module_access"
    FEATURE_ACCESS = "feature_access"
    DATA_ACCESS = "data_access"
    SYSTEM_ACCESS = "system_access"
    API_ACCESS = "api_access"

# System Administration
class SystemAdmin(Base):
    __tablename__ = 'system_admins'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Admin Details
    admin_level = Column(Enum(SystemRole), nullable=False)
    admin_permissions = Column(JSON, nullable=False)  # Admin permissions
    admin_scope = Column(JSON)  # Admin scope (global, module-specific, department-specific)
    
    # Admin Status
    is_active = Column(Boolean, default=True)
    is_super_admin = Column(Boolean, default=False)
    can_manage_users = Column(Boolean, default=False)
    can_manage_modules = Column(Boolean, default=False)
    can_manage_system = Column(Boolean, default=False)
    
    # Admin Audit
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    failed_login_attempts = Column(Integer, default=0)
    account_locked = Column(Boolean, default=False)
    account_locked_until = Column(DateTime)
    
    # Admin Security
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))
    password_reset_required = Column(Boolean, default=False)
    password_last_changed = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])

# System Modules
class SystemModule(Base):
    __tablename__ = 'system_modules'
    
    id = Column(Integer, primary_key=True, index=True)
    module_name = Column(String(100), unique=True, nullable=False)
    module_display_name = Column(String(255), nullable=False)
    module_description = Column(Text)
    module_version = Column(String(50), nullable=False)
    
    # Module Configuration
    module_status = Column(Enum(ModuleStatus), default=ModuleStatus.ACTIVE)
    module_category = Column(String(100))  # crm, finance, hr, marketing, etc.
    module_dependencies = Column(JSON)  # Module dependencies
    module_config = Column(JSON)  # Module configuration
    
    # Module Access Control
    module_permissions = Column(JSON)  # Module permissions
    module_features = Column(JSON)  # Module features
    module_api_endpoints = Column(JSON)  # API endpoints
    module_database_tables = Column(JSON)  # Database tables
    
    # Module Performance
    module_performance_score = Column(Float, default=0.0)  # 0-100
    module_usage_count = Column(Integer, default=0)
    module_last_used = Column(DateTime)
    module_error_count = Column(Integer, default=0)
    
    # Module Maintenance
    module_maintenance_mode = Column(Boolean, default=False)
    module_maintenance_message = Column(Text)
    module_maintenance_scheduled = Column(DateTime)
    module_maintenance_duration = Column(Integer)  # Minutes
    
    # Metadata
    module_created_at = Column(DateTime, default=datetime.utcnow)
    module_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    module_created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")
    departments = relationship("DepartmentModule", back_populates="module")
    users = relationship("UserModule", back_populates="module")

# Departments
class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String(255), nullable=False)
    department_code = Column(String(50), unique=True, nullable=False)
    department_description = Column(Text)
    
    # Department Hierarchy
    parent_department_id = Column(Integer, ForeignKey('departments.id'))
    department_level = Column(Integer, default=1)
    department_path = Column(String(500))  # Hierarchical path
    
    # Department Configuration
    department_head = Column(Integer, ForeignKey('users.id'))
    department_budget = Column(Float, default=0.0)
    department_goals = Column(JSON)  # Department goals
    department_kpis = Column(JSON)  # Department KPIs
    
    # Department Status
    department_status = Column(String(50), default='active')  # active, inactive, archived
    department_created_at = Column(DateTime, default=datetime.utcnow)
    department_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    parent_department = relationship("Department", remote_side=[id])
    head = relationship("User")
    modules = relationship("DepartmentModule", back_populates="department")
    users = relationship("UserDepartment", back_populates="department")

# Department Module Access
class DepartmentModule(Base):
    __tablename__ = 'department_modules'
    
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('system_modules.id'), nullable=False)
    
    # Access Configuration
    access_level = Column(Enum(AccessLevel), nullable=False)
    module_permissions = Column(JSON)  # Module-specific permissions
    feature_permissions = Column(JSON)  # Feature-specific permissions
    data_permissions = Column(JSON)  # Data access permissions
    
    # Access Control
    can_read = Column(Boolean, default=True)
    can_write = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_export = Column(Boolean, default=False)
    can_import = Column(Boolean, default=False)
    
    # Access Restrictions
    access_restrictions = Column(JSON)  # Access restrictions
    time_restrictions = Column(JSON)  # Time-based restrictions
    ip_restrictions = Column(JSON)  # IP-based restrictions
    
    # Access Status
    is_active = Column(Boolean, default=True)
    access_granted_at = Column(DateTime, default=datetime.utcnow)
    access_granted_by = Column(Integer, ForeignKey('users.id'))
    access_expires_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    department = relationship("Department", back_populates="modules")
    module = relationship("SystemModule", back_populates="departments")
    granted_by = relationship("User")

# User Department Assignment
class UserDepartment(Base):
    __tablename__ = 'user_departments'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    
    # Assignment Details
    user_role = Column(String(100), nullable=False)  # manager, member, intern, etc.
    user_level = Column(Integer, default=1)  # Hierarchical level
    is_primary = Column(Boolean, default=True)  # Primary department
    
    # Assignment Status
    is_active = Column(Boolean, default=True)
    assignment_start = Column(DateTime, default=datetime.utcnow)
    assignment_end = Column(DateTime)
    assignment_reason = Column(Text)
    
    # Assignment Permissions
    department_permissions = Column(JSON)  # Department-specific permissions
    team_permissions = Column(JSON)  # Team-specific permissions
    project_permissions = Column(JSON)  # Project-specific permissions
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")
    department = relationship("Department", back_populates="users")
    assigner = relationship("User", foreign_keys=[assigned_by])

# User Module Access
class UserModule(Base):
    __tablename__ = 'user_modules'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('system_modules.id'), nullable=False)
    
    # Access Configuration
    access_level = Column(Enum(AccessLevel), nullable=False)
    module_permissions = Column(JSON)  # Module-specific permissions
    feature_permissions = Column(JSON)  # Feature-specific permissions
    data_permissions = Column(JSON)  # Data access permissions
    
    # Access Control
    can_read = Column(Boolean, default=True)
    can_write = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_export = Column(Boolean, default=False)
    can_import = Column(Boolean, default=False)
    can_admin = Column(Boolean, default=False)
    
    # Access Restrictions
    access_restrictions = Column(JSON)  # Access restrictions
    time_restrictions = Column(JSON)  # Time-based restrictions
    ip_restrictions = Column(JSON)  # IP-based restrictions
    
    # Access Status
    is_active = Column(Boolean, default=True)
    access_granted_at = Column(DateTime, default=datetime.utcnow)
    access_granted_by = Column(Integer, ForeignKey('users.id'))
    access_expires_at = Column(DateTime)
    
    # Usage Tracking
    last_accessed = Column(DateTime)
    access_count = Column(Integer, default=0)
    usage_hours = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")
    module = relationship("SystemModule", back_populates="users")
    granted_by = relationship("User")

# System Permissions
class SystemPermission(Base):
    __tablename__ = 'system_permissions'
    
    id = Column(Integer, primary_key=True, index=True)
    permission_name = Column(String(100), unique=True, nullable=False)
    permission_display_name = Column(String(255), nullable=False)
    permission_description = Column(Text)
    permission_type = Column(Enum(PermissionType), nullable=False)
    
    # Permission Configuration
    permission_category = Column(String(100))  # module, feature, data, system
    permission_module = Column(String(100))  # Associated module
    permission_feature = Column(String(100))  # Associated feature
    permission_action = Column(String(100))  # read, write, delete, admin
    
    # Permission Hierarchy
    parent_permission_id = Column(Integer, ForeignKey('system_permissions.id'))
    permission_level = Column(Integer, default=1)
    permission_path = Column(String(500))  # Hierarchical path
    
    # Permission Status
    is_active = Column(Boolean, default=True)
    is_system_permission = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    parent_permission = relationship("SystemPermission", remote_side=[id])
    creator = relationship("User")

# User Permissions
class UserPermission(Base):
    __tablename__ = 'user_permissions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('system_permissions.id'), nullable=False)
    
    # Permission Details
    permission_granted = Column(Boolean, default=True)
    permission_scope = Column(JSON)  # Permission scope
    permission_conditions = Column(JSON)  # Permission conditions
    permission_expires_at = Column(DateTime)
    
    # Permission Status
    is_active = Column(Boolean, default=True)
    granted_at = Column(DateTime, default=datetime.utcnow)
    granted_by = Column(Integer, ForeignKey('users.id'))
    revoked_at = Column(DateTime)
    revoked_by = Column(Integer, ForeignKey('users.id'))
    
    # Permission Audit
    permission_usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    usage_frequency = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    permission = relationship("SystemPermission")
    granter = relationship("User", foreign_keys=[granted_by])
    revoker = relationship("User", foreign_keys=[revoked_by])

# System Settings
class SystemSetting(Base):
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(255), unique=True, nullable=False)
    setting_value = Column(Text, nullable=False)
    setting_type = Column(String(50), nullable=False)  # string, integer, boolean, json
    setting_category = Column(String(100))  # system, security, performance, etc.
    
    # Setting Configuration
    setting_description = Column(Text)
    setting_default_value = Column(Text)
    setting_validation_rules = Column(JSON)  # Validation rules
    setting_options = Column(JSON)  # Available options
    
    # Setting Access
    is_public = Column(Boolean, default=False)
    is_readonly = Column(Boolean, default=False)
    requires_restart = Column(Boolean, default=False)
    
    # Setting Status
    is_active = Column(Boolean, default=True)
    setting_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    setting_updated_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    updater = relationship("User")

# System Audit Log
class SystemAuditLog(Base):
    __tablename__ = 'system_audit_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action_type = Column(String(100), nullable=False)  # login, logout, create, update, delete
    action_description = Column(Text, nullable=False)
    
    # Action Details
    action_module = Column(String(100))  # Associated module
    action_feature = Column(String(100))  # Associated feature
    action_data = Column(JSON)  # Action data
    action_result = Column(String(50))  # success, failure, error
    
    # Request Details
    request_ip = Column(String(45))
    request_user_agent = Column(Text)
    request_method = Column(String(10))
    request_url = Column(String(500))
    
    # Response Details
    response_status = Column(Integer)
    response_time = Column(Float)  # Response time in milliseconds
    response_size = Column(Integer)  # Response size in bytes
    
    # Security Details
    security_level = Column(String(20))  # low, medium, high, critical
    risk_score = Column(Float, default=0.0)  # 0-100 risk score
    security_flags = Column(JSON)  # Security flags
    
    # Metadata
    action_timestamp = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")

# System Health Monitoring
class SystemHealth(Base):
    __tablename__ = 'system_health'
    
    id = Column(Integer, primary_key=True, index=True)
    health_check_name = Column(String(255), nullable=False)
    health_check_type = Column(String(100), nullable=False)  # system, module, service, database
    
    # Health Metrics
    health_status = Column(String(20), nullable=False)  # healthy, warning, critical, down
    health_score = Column(Float, default=0.0)  # 0-100 health score
    health_metrics = Column(JSON)  # Health metrics
    health_thresholds = Column(JSON)  # Health thresholds
    
    # Performance Metrics
    response_time = Column(Float, default=0.0)  # Response time in milliseconds
    throughput = Column(Float, default=0.0)  # Throughput per second
    error_rate = Column(Float, default=0.0)  # Error rate percentage
    availability = Column(Float, default=100.0)  # Availability percentage
    
    # Health Details
    health_message = Column(Text)
    health_recommendations = Column(JSON)  # Health recommendations
    health_alerts = Column(JSON)  # Health alerts
    
    # Metadata
    health_check_time = Column(DateTime, default=datetime.utcnow)
    next_check_time = Column(DateTime)
    company_id = Column(Integer, ForeignKey('companies.id'))
