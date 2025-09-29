# User Roles and Privileges System
# Advanced role-based access control

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class PermissionLevel(enum.Enum):
    NONE = "None"
    READ = "Read"
    WRITE = "Write"
    DELETE = "Delete"
    ADMIN = "Admin"

class Role(BaseModel):
    """Role model"""
    __tablename__ = 'roles'
    
    # Role Information
    role_name = db.Column(db.String(200), nullable=False)
    role_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Role Settings
    is_active = db.Column(db.Boolean, default=True)
    is_system_role = db.Column(db.Boolean, default=False)
    is_default = db.Column(db.Boolean, default=False)
    
    # Role Hierarchy
    parent_role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    parent_role = relationship("Role", remote_side=[id])
    child_roles = relationship("Role", back_populates="parent_role")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    permissions = relationship("RolePermission", back_populates="role")
    users = relationship("UserRole", back_populates="role")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'role_name': self.role_name,
            'role_code': self.role_code,
            'description': self.description,
            'is_active': self.is_active,
            'is_system_role': self.is_system_role,
            'is_default': self.is_default,
            'parent_role_id': self.parent_role_id,
            'company_id': self.company_id
        })
        return data

class Permission(BaseModel):
    """Permission model"""
    __tablename__ = 'permissions'
    
    # Permission Information
    permission_name = db.Column(db.String(200), nullable=False)
    permission_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Permission Settings
    module = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    resource = db.Column(db.String(100), nullable=False)
    
    # Permission Level
    permission_level = db.Column(db.Enum(PermissionLevel), default=PermissionLevel.READ)
    
    # Permission Settings
    is_active = db.Column(db.Boolean, default=True)
    is_system_permission = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'permission_name': self.permission_name,
            'permission_code': self.permission_code,
            'description': self.description,
            'module': self.module,
            'action': self.action,
            'resource': self.resource,
            'permission_level': self.permission_level.value if self.permission_level else None,
            'is_active': self.is_active,
            'is_system_permission': self.is_system_permission,
            'company_id': self.company_id
        })
        return data

class RolePermission(BaseModel):
    """Role-Permission association model"""
    __tablename__ = 'role_permissions'
    
    # Association
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    
    # Permission Level Override
    permission_level = db.Column(db.Enum(PermissionLevel), default=PermissionLevel.READ)
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    is_granted = db.Column(db.Boolean, default=True)
    
    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'role_id': self.role_id,
            'permission_id': self.permission_id,
            'permission_level': self.permission_level.value if self.permission_level else None,
            'is_active': self.is_active,
            'is_granted': self.is_granted
        })
        return data

class UserRole(BaseModel):
    """User-Role association model"""
    __tablename__ = 'user_roles'
    
    # Association
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    # Role Settings
    is_active = db.Column(db.Boolean, default=True)
    is_primary = db.Column(db.Boolean, default=False)
    
    # Assignment Information
    assigned_by = db.Column(db.Integer, db.ForeignKey('employees.id'))
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    
    # Relationships
    user = relationship("Employee", foreign_keys=[user_id])
    role = relationship("Role", back_populates="users")
    assigned_by_user = relationship("Employee", foreign_keys=[assigned_by])
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'role_id': self.role_id,
            'is_active': self.is_active,
            'is_primary': self.is_primary,
            'assigned_by': self.assigned_by,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None
        })
        return data

class UserPermission(BaseModel):
    """User-Permission association model"""
    __tablename__ = 'user_permissions'
    
    # Association
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    
    # Permission Level Override
    permission_level = db.Column(db.Enum(PermissionLevel), default=PermissionLevel.READ)
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    is_granted = db.Column(db.Boolean, default=True)
    
    # Assignment Information
    assigned_by = db.Column(db.Integer, db.ForeignKey('employees.id'))
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    
    # Relationships
    user = relationship("Employee", foreign_keys=[user_id])
    permission = relationship("Permission")
    assigned_by_user = relationship("Employee", foreign_keys=[assigned_by])
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'permission_id': self.permission_id,
            'permission_level': self.permission_level.value if self.permission_level else None,
            'is_active': self.is_active,
            'is_granted': self.is_granted,
            'assigned_by': self.assigned_by,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None
        })
        return data

class AccessControlList(BaseModel):
    """Access Control List model"""
    __tablename__ = 'access_control_lists'
    
    # ACL Information
    acl_name = db.Column(db.String(200), nullable=False)
    acl_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # ACL Configuration
    acl_rules = db.Column(db.JSON)  # ACL rules configuration
    resource_filters = db.Column(db.JSON)  # Resource filters configuration
    time_restrictions = db.Column(db.JSON)  # Time restrictions configuration
    
    # ACL Settings
    is_active = db.Column(db.Boolean, default=True)
    is_global = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'acl_name': self.acl_name,
            'acl_code': self.acl_code,
            'description': self.description,
            'acl_rules': self.acl_rules,
            'resource_filters': self.resource_filters,
            'time_restrictions': self.time_restrictions,
            'is_active': self.is_active,
            'is_global': self.is_global,
            'priority': self.priority,
            'company_id': self.company_id
        })
        return data
