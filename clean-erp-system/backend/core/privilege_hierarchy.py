# Enhanced Privilege Hierarchy System
# Comprehensive access control and privilege management

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class PrivilegeLevel(enum.Enum):
    SUPER_ADMIN = "super_admin"
    SYSTEM_ADMIN = "system_admin"
    MODULE_ADMIN = "module_admin"
    DEPARTMENT_ADMIN = "department_admin"
    TEAM_LEADER = "team_leader"
    SENIOR_USER = "senior_user"
    USER = "user"
    LIMITED_USER = "limited_user"
    GUEST = "guest"

class AccessScope(enum.Enum):
    GLOBAL = "global"
    MODULE = "module"
    DEPARTMENT = "department"
    TEAM = "team"
    PROJECT = "project"
    PERSONAL = "personal"

class PermissionAction(enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    IMPORT = "import"
    ADMIN = "admin"
    APPROVE = "approve"
    AUDIT = "audit"

class SecurityLevel(enum.Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"

# Enhanced User Roles
class UserRole(Base):
    __tablename__ = 'user_roles'
    
    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(100), unique=True, nullable=False)
    role_display_name = Column(String(255), nullable=False)
    role_description = Column(Text)
    
    # Role Hierarchy
    privilege_level = Column(Enum(PrivilegeLevel), nullable=False)
    parent_role_id = Column(Integer, ForeignKey('user_roles.id'))
    role_level = Column(Integer, default=1)
    role_path = Column(String(500))  # Hierarchical path
    
    # Role Configuration
    role_scope = Column(Enum(AccessScope), default=AccessScope.PERSONAL)
    role_permissions = Column(JSON, nullable=False)  # Role permissions
    role_restrictions = Column(JSON)  # Role restrictions
    role_conditions = Column(JSON)  # Role conditions
    
    # Role Security
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)
    requires_approval = Column(Boolean, default=False)
    requires_2fa = Column(Boolean, default=False)
    session_timeout = Column(Integer, default=480)  # Minutes
    
    # Role Status
    is_active = Column(Boolean, default=True)
    is_system_role = Column(Boolean, default=False)
    is_default_role = Column(Boolean, default=False)
    
    # Role Usage
    user_count = Column(Integer, default=0)
    usage_frequency = Column(Float, default=0.0)
    last_used = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    parent_role = relationship("UserRole", remote_side=[id])
    creator = relationship("User")
    permissions = relationship("RolePermission", back_populates="role")
    users = relationship("UserRoleAssignment", back_populates="role")

# Enhanced Permissions
class Permission(Base):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, index=True)
    permission_name = Column(String(100), unique=True, nullable=False)
    permission_display_name = Column(String(255), nullable=False)
    permission_description = Column(Text)
    
    # Permission Configuration
    permission_type = Column(String(50), nullable=False)  # module, feature, data, system, api
    permission_module = Column(String(100))  # Associated module
    permission_feature = Column(String(100))  # Associated feature
    permission_action = Column(Enum(PermissionAction), nullable=False)
    permission_resource = Column(String(100))  # Resource being accessed
    
    # Permission Hierarchy
    parent_permission_id = Column(Integer, ForeignKey('permissions.id'))
    permission_level = Column(Integer, default=1)
    permission_path = Column(String(500))  # Hierarchical path
    
    # Permission Security
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)
    requires_approval = Column(Boolean, default=False)
    requires_audit = Column(Boolean, default=False)
    risk_level = Column(String(20), default='low')  # low, medium, high, critical
    
    # Permission Scope
    access_scope = Column(Enum(AccessScope), default=AccessScope.PERSONAL)
    scope_conditions = Column(JSON)  # Scope conditions
    scope_restrictions = Column(JSON)  # Scope restrictions
    
    # Permission Status
    is_active = Column(Boolean, default=True)
    is_system_permission = Column(Boolean, default=False)
    is_deprecated = Column(Boolean, default=False)
    
    # Permission Usage
    usage_count = Column(Integer, default=0)
    usage_frequency = Column(Float, default=0.0)
    last_used = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    parent_permission = relationship("Permission", remote_side=[id])
    creator = relationship("User")
    role_permissions = relationship("RolePermission", back_populates="permission")
    user_permissions = relationship("UserPermission", back_populates="permission")

# Role-Permission Assignment
class RolePermission(Base):
    __tablename__ = 'role_permissions'
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey('user_roles.id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False)
    
    # Permission Assignment
    permission_granted = Column(Boolean, default=True)
    permission_scope = Column(JSON)  # Permission scope
    permission_conditions = Column(JSON)  # Permission conditions
    permission_restrictions = Column(JSON)  # Permission restrictions
    
    # Assignment Details
    assignment_type = Column(String(50), default='direct')  # direct, inherited, conditional
    assignment_priority = Column(Integer, default=0)  # Assignment priority
    assignment_expires_at = Column(DateTime)
    
    # Assignment Status
    is_active = Column(Boolean, default=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    assigned_by = Column(Integer, ForeignKey('users.id'))
    revoked_at = Column(DateTime)
    revoked_by = Column(Integer, ForeignKey('users.id'))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    role = relationship("UserRole", back_populates="permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    assigner = relationship("User", foreign_keys=[assigned_by])
    revoker = relationship("User", foreign_keys=[revoked_by])

# User Role Assignment
class UserRoleAssignment(Base):
    __tablename__ = 'user_role_assignments'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('user_roles.id'), nullable=False)
    
    # Assignment Details
    assignment_type = Column(String(50), default='direct')  # direct, inherited, temporary
    assignment_scope = Column(JSON)  # Assignment scope
    assignment_conditions = Column(JSON)  # Assignment conditions
    assignment_restrictions = Column(JSON)  # Assignment restrictions
    
    # Assignment Status
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)  # Primary role
    assignment_start = Column(DateTime, default=datetime.utcnow)
    assignment_end = Column(DateTime)
    assignment_reason = Column(Text)
    
    # Assignment Approval
    requires_approval = Column(Boolean, default=False)
    approval_status = Column(String(50), default='pending')  # pending, approved, rejected
    approved_by = Column(Integer, ForeignKey('users.id'))
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    
    # Assignment Audit
    assignment_audit = Column(JSON)  # Assignment audit trail
    last_accessed = Column(DateTime)
    access_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("UserRole", back_populates="users")
    assigner = relationship("User", foreign_keys=[assigned_by])
    approver = relationship("User", foreign_keys=[approved_by])

# User Permission Assignment
class UserPermission(Base):
    __tablename__ = 'user_permissions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False)
    
    # Permission Assignment
    permission_granted = Column(Boolean, default=True)
    permission_scope = Column(JSON)  # Permission scope
    permission_conditions = Column(JSON)  # Permission conditions
    permission_restrictions = Column(JSON)  # Permission restrictions
    
    # Assignment Details
    assignment_type = Column(String(50), default='direct')  # direct, inherited, role-based
    assignment_source = Column(String(100))  # Source of permission (role, direct, inherited)
    assignment_priority = Column(Integer, default=0)  # Assignment priority
    assignment_expires_at = Column(DateTime)
    
    # Assignment Status
    is_active = Column(Boolean, default=True)
    granted_at = Column(DateTime, default=datetime.utcnow)
    granted_by = Column(Integer, ForeignKey('users.id'))
    revoked_at = Column(DateTime)
    revoked_by = Column(Integer, ForeignKey('users.id'))
    
    # Permission Usage
    usage_count = Column(Integer, default=0)
    usage_frequency = Column(Float, default=0.0)
    last_used = Column(DateTime)
    usage_analytics = Column(JSON)  # Usage analytics
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    permission = relationship("Permission", back_populates="user_permissions")
    granter = relationship("User", foreign_keys=[granted_by])
    revoker = relationship("User", foreign_keys=[revoked_by])

# Access Control Lists
class AccessControlList(Base):
    __tablename__ = 'access_control_lists'
    
    id = Column(Integer, primary_key=True, index=True)
    acl_name = Column(String(255), nullable=False)
    acl_description = Column(Text)
    acl_type = Column(String(50), nullable=False)  # user, role, department, module
    
    # ACL Configuration
    acl_scope = Column(Enum(AccessScope), nullable=False)
    acl_conditions = Column(JSON)  # ACL conditions
    acl_restrictions = Column(JSON)  # ACL restrictions
    acl_priority = Column(Integer, default=0)  # ACL priority
    
    # ACL Rules
    acl_rules = Column(JSON, nullable=False)  # ACL rules
    acl_actions = Column(JSON, nullable=False)  # Allowed/denied actions
    acl_resources = Column(JSON)  # Protected resources
    
    # ACL Security
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)
    requires_approval = Column(Boolean, default=False)
    requires_audit = Column(Boolean, default=False)
    
    # ACL Status
    is_active = Column(Boolean, default=True)
    is_system_acl = Column(Boolean, default=False)
    acl_created_at = Column(DateTime, default=datetime.utcnow)
    acl_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    acl_created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Security Policies
class SecurityPolicy(Base):
    __tablename__ = 'security_policies'
    
    id = Column(Integer, primary_key=True, index=True)
    policy_name = Column(String(255), nullable=False)
    policy_description = Column(Text)
    policy_type = Column(String(50), nullable=False)  # password, session, access, data
    
    # Policy Configuration
    policy_rules = Column(JSON, nullable=False)  # Policy rules
    policy_conditions = Column(JSON)  # Policy conditions
    policy_actions = Column(JSON)  # Policy actions
    policy_priority = Column(Integer, default=0)  # Policy priority
    
    # Policy Security
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)
    policy_scope = Column(Enum(AccessScope), default=AccessScope.GLOBAL)
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

# Access Logs
class AccessLog(Base):
    __tablename__ = 'access_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_id = Column(String(255))
    
    # Access Details
    access_type = Column(String(50), nullable=False)  # login, logout, access, denied
    access_module = Column(String(100))  # Accessed module
    access_feature = Column(String(100))  # Accessed feature
    access_resource = Column(String(255))  # Accessed resource
    
    # Access Context
    access_ip = Column(String(45))
    access_user_agent = Column(Text)
    access_location = Column(JSON)  # Geographic location
    access_device = Column(JSON)  # Device information
    
    # Access Result
    access_result = Column(String(50), nullable=False)  # success, failure, denied, error
    access_reason = Column(Text)  # Access reason or denial reason
    access_duration = Column(Float)  # Access duration in seconds
    
    # Security Details
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)
    risk_score = Column(Float, default=0.0)  # 0-100 risk score
    security_flags = Column(JSON)  # Security flags
    threat_level = Column(String(20), default='low')  # low, medium, high, critical
    
    # Access Data
    access_data = Column(JSON)  # Additional access data
    access_metadata = Column(JSON)  # Access metadata
    
    # Metadata
    access_timestamp = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")

# Permission Audit
class PermissionAudit(Base):
    __tablename__ = 'permission_audits'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    permission_id = Column(Integer, ForeignKey('permissions.id'))
    
    # Audit Details
    audit_action = Column(String(50), nullable=False)  # granted, revoked, modified, accessed
    audit_reason = Column(Text)
    audit_data = Column(JSON)  # Audit data
    
    # Audit Context
    audit_ip = Column(String(45))
    audit_user_agent = Column(Text)
    audit_location = Column(JSON)  # Geographic location
    
    # Audit Result
    audit_result = Column(String(50), nullable=False)  # success, failure, error
    audit_message = Column(Text)
    audit_impact = Column(String(50))  # low, medium, high, critical
    
    # Security Details
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)
    risk_score = Column(Float, default=0.0)  # 0-100 risk score
    security_flags = Column(JSON)  # Security flags
    
    # Metadata
    audit_timestamp = Column(DateTime, default=datetime.utcnow)
    audited_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    permission = relationship("Permission")
    auditor = relationship("User", foreign_keys=[audited_by])
