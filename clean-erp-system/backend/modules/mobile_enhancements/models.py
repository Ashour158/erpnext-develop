# Mobile Enhancements Models
# Models for mobile app enhancements including offline capability, push notifications, voice commands, and AR features

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime, time, date, timedelta
import enum

class NotificationType(enum.Enum):
    MEETING_REMINDER = "Meeting Reminder"
    LOCATION_ALERT = "Location Alert"
    DEADLINE_WARNING = "Deadline Warning"
    SYSTEM_UPDATE = "System Update"
    SECURITY_ALERT = "Security Alert"
    CUSTOM = "Custom"

class NotificationPriority(enum.Enum):
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    URGENT = "Urgent"

class DeliveryStatus(enum.Enum):
    PENDING = "Pending"
    SENT = "Sent"
    DELIVERED = "Delivered"
    FAILED = "Failed"
    READ = "Read"

class OfflineSyncStatus(enum.Enum):
    PENDING = "Pending"
    SYNCING = "Syncing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CONFLICT = "Conflict"

class VoiceCommandType(enum.Enum):
    CHECK_IN = "Check In"
    CHECK_OUT = "Check Out"
    CREATE_MEETING = "Create Meeting"
    NAVIGATE = "Navigate"
    CALL = "Call"
    MESSAGE = "Message"
    CUSTOM = "Custom"

class ARFeatureType(enum.Enum):
    LOCATION_VERIFICATION = "Location Verification"
    NAVIGATION = "Navigation"
    OBJECT_RECOGNITION = "Object Recognition"
    MEASUREMENT = "Measurement"
    ANNOTATION = "Annotation"

class PushNotification(BaseModel):
    """Push notification model"""
    __tablename__ = 'push_notifications'
    
    # Notification Information
    notification_title = db.Column(db.String(200), nullable=False)
    notification_message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.Enum(NotificationType), nullable=False)
    priority = db.Column(db.Enum(NotificationPriority), default=NotificationPriority.NORMAL)
    
    # Delivery Information
    delivery_status = db.Column(db.Enum(DeliveryStatus), default=DeliveryStatus.PENDING)
    scheduled_time = db.Column(db.DateTime)
    sent_time = db.Column(db.DateTime)
    delivered_time = db.Column(db.DateTime)
    read_time = db.Column(db.DateTime)
    
    # Recipients
    target_user_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    target_user = relationship("Employee")
    target_device_id = db.Column(db.String(100))
    target_platform = db.Column(db.String(50))  # iOS, Android, Web
    
    # Notification Data
    notification_data = db.Column(db.JSON)  # Additional notification data
    action_buttons = db.Column(db.JSON)  # Action buttons for the notification
    deep_link = db.Column(db.String(500))  # Deep link URL
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'notification_title': self.notification_title,
            'notification_message': self.notification_message,
            'notification_type': self.notification_type.value if self.notification_type else None,
            'priority': self.priority.value if self.priority else None,
            'delivery_status': self.delivery_status.value if self.delivery_status else None,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'sent_time': self.sent_time.isoformat() if self.sent_time else None,
            'delivered_time': self.delivered_time.isoformat() if self.delivered_time else None,
            'read_time': self.read_time.isoformat() if self.read_time else None,
            'target_user_id': self.target_user_id,
            'target_device_id': self.target_device_id,
            'target_platform': self.target_platform,
            'notification_data': self.notification_data,
            'action_buttons': self.action_buttons,
            'deep_link': self.deep_link,
            'company_id': self.company_id
        })
        return data

class OfflineData(BaseModel):
    """Offline data model"""
    __tablename__ = 'offline_data'
    
    # Data Information
    data_type = db.Column(db.String(100), nullable=False)  # Meeting, Contact, Task, etc.
    data_id = db.Column(db.String(100), nullable=False)
    data_content = db.Column(db.JSON, nullable=False)
    
    # Sync Information
    sync_status = db.Column(db.Enum(OfflineSyncStatus), default=OfflineSyncStatus.PENDING)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow)
    sync_attempts = db.Column(db.Integer, default=0)
    sync_errors = db.Column(db.JSON)
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Device Information
    device_id = db.Column(db.String(100), nullable=False)
    app_version = db.Column(db.String(50))
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'data_type': self.data_type,
            'data_id': self.data_id,
            'data_content': self.data_content,
            'sync_status': self.sync_status.value if self.sync_status else None,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None,
            'sync_attempts': self.sync_attempts,
            'sync_errors': self.sync_errors,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'app_version': self.app_version,
            'company_id': self.company_id
        })
        return data

class VoiceCommand(BaseModel):
    """Voice command model"""
    __tablename__ = 'voice_commands'
    
    # Command Information
    command_text = db.Column(db.Text, nullable=False)
    command_type = db.Column(db.Enum(VoiceCommandType), nullable=False)
    confidence_score = db.Column(db.Float, default=0.0)  # 0-1
    
    # Processing Information
    is_processed = db.Column(db.Boolean, default=False)
    processing_time = db.Column(db.Float, default=0.0)  # seconds
    processing_errors = db.Column(db.JSON)
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Device Information
    device_id = db.Column(db.String(100), nullable=False)
    audio_file_path = db.Column(db.String(500))
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'command_text': self.command_text,
            'command_type': self.command_type.value if self.command_type else None,
            'confidence_score': self.confidence_score,
            'is_processed': self.is_processed,
            'processing_time': self.processing_time,
            'processing_errors': self.processing_errors,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'audio_file_path': self.audio_file_path,
            'company_id': self.company_id
        })
        return data

class ARSession(BaseModel):
    """AR session model"""
    __tablename__ = 'ar_sessions'
    
    # Session Information
    session_name = db.Column(db.String(200), nullable=False)
    session_description = db.Column(db.Text)
    feature_type = db.Column(db.Enum(ARFeatureType), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # AR Data
    ar_data = db.Column(db.JSON)  # AR-specific data
    coordinates = db.Column(db.JSON)  # 3D coordinates
    measurements = db.Column(db.JSON)  # AR measurements
    annotations = db.Column(db.JSON)  # AR annotations
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Device Information
    device_id = db.Column(db.String(100), nullable=False)
    device_capabilities = db.Column(db.JSON)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'session_name': self.session_name,
            'session_description': self.session_description,
            'feature_type': self.feature_type.value if self.feature_type else None,
            'is_active': self.is_active,
            'ar_data': self.ar_data,
            'coordinates': self.coordinates,
            'measurements': self.measurements,
            'annotations': self.annotations,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'device_capabilities': self.device_capabilities,
            'company_id': self.company_id
        })
        return data

class MobileDevice(BaseModel):
    """Mobile device model"""
    __tablename__ = 'mobile_devices'
    
    # Device Information
    device_id = db.Column(db.String(100), nullable=False, unique=True)
    device_name = db.Column(db.String(200))
    device_type = db.Column(db.String(50))  # iPhone, Android, Tablet
    operating_system = db.Column(db.String(50))
    os_version = db.Column(db.String(50))
    app_version = db.Column(db.String(50))
    
    # Device Capabilities
    has_camera = db.Column(db.Boolean, default=False)
    has_gps = db.Column(db.Boolean, default=False)
    has_accelerometer = db.Column(db.Boolean, default=False)
    has_gyroscope = db.Column(db.Boolean, default=False)
    has_magnetometer = db.Column(db.Boolean, default=False)
    has_ar_support = db.Column(db.Boolean, default=False)
    
    # Device Status
    is_active = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    battery_level = db.Column(db.Float, default=0.0)
    network_status = db.Column(db.String(50), default='Unknown')
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'operating_system': self.operating_system,
            'os_version': self.os_version,
            'app_version': self.app_version,
            'has_camera': self.has_camera,
            'has_gps': self.has_gps,
            'has_accelerometer': self.has_accelerometer,
            'has_gyroscope': self.has_gyroscope,
            'has_magnetometer': self.has_magnetometer,
            'has_ar_support': self.has_ar_support,
            'is_active': self.is_active,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'battery_level': self.battery_level,
            'network_status': self.network_status,
            'user_id': self.user_id,
            'company_id': self.company_id
        })
        return data

class OfflineSyncLog(BaseModel):
    """Offline sync log model"""
    __tablename__ = 'offline_sync_logs'
    
    # Sync Information
    sync_type = db.Column(db.String(50), nullable=False)  # Upload, Download, Conflict Resolution
    sync_status = db.Column(db.Enum(OfflineSyncStatus), nullable=False)
    sync_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    sync_end_time = db.Column(db.DateTime)
    sync_duration = db.Column(db.Float, default=0.0)  # seconds
    
    # Sync Results
    records_synced = db.Column(db.Integer, default=0)
    records_created = db.Column(db.Integer, default=0)
    records_updated = db.Column(db.Integer, default=0)
    records_deleted = db.Column(db.Integer, default=0)
    conflicts_resolved = db.Column(db.Integer, default=0)
    
    # Error Information
    error_message = db.Column(db.Text)
    error_details = db.Column(db.JSON)
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Device Information
    device_id = db.Column(db.String(100), nullable=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'sync_type': self.sync_type,
            'sync_status': self.sync_status.value if self.sync_status else None,
            'sync_start_time': self.sync_start_time.isoformat() if self.sync_start_time else None,
            'sync_end_time': self.sync_end_time.isoformat() if self.sync_end_time else None,
            'sync_duration': self.sync_duration,
            'records_synced': self.records_synced,
            'records_created': self.records_created,
            'records_updated': self.records_updated,
            'records_deleted': self.records_deleted,
            'conflicts_resolved': self.conflicts_resolved,
            'error_message': self.error_message,
            'error_details': self.error_details,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'company_id': self.company_id
        })
        return data

class MobileAppSetting(BaseModel):
    """Mobile app settings model"""
    __tablename__ = 'mobile_app_settings'
    
    # Setting Information
    setting_name = db.Column(db.String(100), nullable=False)
    setting_value = db.Column(db.Text, nullable=False)
    setting_type = db.Column(db.String(50), default='String')  # String, Number, Boolean, JSON
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Device Information
    device_id = db.Column(db.String(100), nullable=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'setting_name': self.setting_name,
            'setting_value': self.setting_value,
            'setting_type': self.setting_type,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'company_id': self.company_id
        })
        return data
