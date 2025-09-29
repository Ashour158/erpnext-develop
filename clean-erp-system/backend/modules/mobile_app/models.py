# Mobile App Models
# Native mobile applications with offline capability and push notifications

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

class DeviceType(enum.Enum):
    IOS = "iOS"
    ANDROID = "Android"
    WEB = "Web"

class NotificationType(enum.Enum):
    PUSH = "Push"
    EMAIL = "Email"
    SMS = "SMS"
    IN_APP = "In-App"

class NotificationPriority(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class SyncStatus(enum.Enum):
    PENDING = "Pending"
    SYNCING = "Syncing"
    COMPLETED = "Completed"
    FAILED = "Failed"

class OfflineAction(enum.Enum):
    CREATE = "Create"
    UPDATE = "Update"
    DELETE = "Delete"
    VIEW = "View"

# Mobile Device Models
class MobileDevice(BaseModel):
    """Mobile device model"""
    __tablename__ = 'mobile_devices'
    
    # Device Information
    device_id = db.Column(db.String(255), unique=True, nullable=False)  # Unique device identifier
    device_name = db.Column(db.String(200), nullable=False)
    device_type = db.Column(db.Enum(DeviceType), nullable=False)
    device_model = db.Column(db.String(100))
    device_version = db.Column(db.String(50))
    
    # User Association
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Device Details
    os_version = db.Column(db.String(50))
    app_version = db.Column(db.String(50))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Push Notification Settings
    push_token = db.Column(db.String(500))
    push_enabled = db.Column(db.Boolean, default=True)
    notification_settings = db.Column(db.JSON)  # Notification preferences
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type.value if self.device_type else None,
            'device_model': self.device_model,
            'device_version': self.device_version,
            'user_id': self.user_id,
            'os_version': self.os_version,
            'app_version': self.app_version,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'is_active': self.is_active,
            'push_token': self.push_token,
            'push_enabled': self.push_enabled,
            'notification_settings': self.notification_settings,
            'company_id': self.company_id
        })
        return data

# Push Notification Models
class PushNotification(BaseModel):
    """Push notification model"""
    __tablename__ = 'push_notifications'
    
    # Notification Information
    notification_title = db.Column(db.String(200), nullable=False)
    notification_body = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.Enum(NotificationType), default=NotificationType.PUSH)
    priority = db.Column(db.Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    
    # Target Information
    target_user_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    target_user = relationship("Employee")
    target_device_id = db.Column(db.String(255))
    target_audience = db.Column(db.JSON)  # List of user IDs or roles
    
    # Notification Content
    notification_data = db.Column(db.JSON)  # Additional notification data
    action_url = db.Column(db.String(500))  # Deep link or action URL
    image_url = db.Column(db.String(500))  # Notification image
    
    # Notification Status
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    is_delivered = db.Column(db.Boolean, default=False)
    delivered_at = db.Column(db.DateTime)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    
    # Scheduling
    scheduled_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'notification_title': self.notification_title,
            'notification_body': self.notification_body,
            'notification_type': self.notification_type.value if self.notification_type else None,
            'priority': self.priority.value if self.priority else None,
            'target_user_id': self.target_user_id,
            'target_device_id': self.target_device_id,
            'target_audience': self.target_audience,
            'notification_data': self.notification_data,
            'action_url': self.action_url,
            'image_url': self.image_url,
            'is_sent': self.is_sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'is_delivered': self.is_delivered,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'company_id': self.company_id
        })
        return data

# Offline Sync Models
class OfflineSync(BaseModel):
    """Offline sync model"""
    __tablename__ = 'offline_syncs'
    
    # Sync Information
    sync_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    device_id = db.Column(db.String(255), nullable=False)
    
    # Sync Details
    sync_type = db.Column(db.String(100), nullable=False)  # Full, Incremental, Manual
    sync_status = db.Column(db.Enum(SyncStatus), default=SyncStatus.PENDING)
    sync_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    sync_end_time = db.Column(db.DateTime)
    sync_duration = db.Column(db.Float, default=0.0)  # seconds
    
    # Sync Data
    data_synced = db.Column(db.JSON)  # List of synced data
    conflicts_resolved = db.Column(db.JSON)  # List of resolved conflicts
    sync_errors = db.Column(db.JSON)  # List of sync errors
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'sync_id': self.sync_id,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'sync_type': self.sync_type,
            'sync_status': self.sync_status.value if self.sync_status else None,
            'sync_start_time': self.sync_start_time.isoformat() if self.sync_start_time else None,
            'sync_end_time': self.sync_end_time.isoformat() if self.sync_end_time else None,
            'sync_duration': self.sync_duration,
            'data_synced': self.data_synced,
            'conflicts_resolved': self.conflicts_resolved,
            'sync_errors': self.sync_errors,
            'company_id': self.company_id
        })
        return data

class OfflineAction(BaseModel):
    """Offline action model"""
    __tablename__ = 'offline_actions'
    
    # Action Information
    action_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    device_id = db.Column(db.String(255), nullable=False)
    
    # Action Details
    action_type = db.Column(db.Enum(OfflineAction), nullable=False)
    entity_type = db.Column(db.String(100), nullable=False)  # Customer, Invoice, etc.
    entity_id = db.Column(db.String(100))
    action_data = db.Column(db.JSON)  # Action data payload
    
    # Action Status
    is_pending = db.Column(db.Boolean, default=True)
    is_synced = db.Column(db.Boolean, default=False)
    sync_attempts = db.Column(db.Integer, default=0)
    last_sync_attempt = db.Column(db.DateTime)
    sync_error = db.Column(db.Text)
    
    # Timestamps
    created_offline_at = db.Column(db.DateTime, default=datetime.utcnow)
    synced_at = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'action_id': self.action_id,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'action_type': self.action_type.value if self.action_type else None,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'action_data': self.action_data,
            'is_pending': self.is_pending,
            'is_synced': self.is_synced,
            'sync_attempts': self.sync_attempts,
            'last_sync_attempt': self.last_sync_attempt.isoformat() if self.last_sync_attempt else None,
            'sync_error': self.sync_error,
            'created_offline_at': self.created_offline_at.isoformat() if self.created_offline_at else None,
            'synced_at': self.synced_at.isoformat() if self.synced_at else None,
            'company_id': self.company_id
        })
        return data

# Mobile App Configuration Models
class MobileAppConfig(BaseModel):
    """Mobile app configuration model"""
    __tablename__ = 'mobile_app_configs'
    
    # Configuration Information
    config_name = db.Column(db.String(200), nullable=False)
    config_description = db.Column(db.Text)
    config_type = db.Column(db.String(100), nullable=False)  # App, Feature, Security, etc.
    
    # Configuration Data
    config_data = db.Column(db.JSON, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_global = db.Column(db.Boolean, default=True)  # Global or user-specific
    
    # Target Information
    target_users = db.Column(db.JSON)  # List of user IDs
    target_roles = db.Column(db.JSON)  # List of role IDs
    target_devices = db.Column(db.JSON)  # List of device types
    
    # Version Control
    version = db.Column(db.String(50), default='1.0.0')
    min_app_version = db.Column(db.String(50))
    max_app_version = db.Column(db.String(50))
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'config_name': self.config_name,
            'config_description': self.config_description,
            'config_type': self.config_type,
            'config_data': self.config_data,
            'is_active': self.is_active,
            'is_global': self.is_global,
            'target_users': self.target_users,
            'target_roles': self.target_roles,
            'target_devices': self.target_devices,
            'version': self.version,
            'min_app_version': self.min_app_version,
            'max_app_version': self.max_app_version,
            'company_id': self.company_id
        })
        return data

# Mobile Analytics Models
class MobileAnalytics(BaseModel):
    """Mobile analytics model"""
    __tablename__ = 'mobile_analytics'
    
    # Analytics Information
    event_name = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)  # User, System, Error, etc.
    event_category = db.Column(db.String(100))  # Navigation, Action, Performance, etc.
    
    # User and Device Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    user = relationship("Employee")
    device_id = db.Column(db.String(255))
    device_type = db.Column(db.Enum(DeviceType))
    
    # Event Data
    event_data = db.Column(db.JSON)  # Event-specific data
    event_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100))
    
    # Performance Data
    response_time = db.Column(db.Float, default=0.0)  # milliseconds
    memory_usage = db.Column(db.Float, default=0.0)  # MB
    battery_level = db.Column(db.Float, default=0.0)  # percentage
    network_type = db.Column(db.String(50))  # WiFi, 4G, 5G, etc.
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'event_name': self.event_name,
            'event_type': self.event_type,
            'event_category': self.event_category,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'device_type': self.device_type.value if self.device_type else None,
            'event_data': self.event_data,
            'event_timestamp': self.event_timestamp.isoformat() if self.event_timestamp else None,
            'session_id': self.session_id,
            'response_time': self.response_time,
            'memory_usage': self.memory_usage,
            'battery_level': self.battery_level,
            'network_type': self.network_type,
            'company_id': self.company_id
        })
        return data

# Mobile Security Models
class MobileSecurity(BaseModel):
    """Mobile security model"""
    __tablename__ = 'mobile_security'
    
    # Security Information
    security_event = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)  # Login, Logout, Data Access, etc.
    severity = db.Column(db.Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    
    # User and Device Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    user = relationship("Employee")
    device_id = db.Column(db.String(255))
    device_type = db.Column(db.Enum(DeviceType))
    
    # Security Details
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    user_agent = db.Column(db.String(500))
    location = db.Column(db.String(200))
    security_data = db.Column(db.JSON)  # Additional security data
    
    # Event Status
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    resolved_by = relationship("Employee", foreign_keys=[resolved_by_id])
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'security_event': self.security_event,
            'event_type': self.event_type,
            'severity': self.severity.value if self.severity else None,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'device_type': self.device_type.value if self.device_type else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'location': self.location,
            'security_data': self.security_data,
            'is_resolved': self.is_resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by_id': self.resolved_by_id,
            'company_id': self.company_id
        })
        return data
