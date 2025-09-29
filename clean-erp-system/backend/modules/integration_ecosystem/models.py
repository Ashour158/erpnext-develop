# Integration Ecosystem Models
# Models for integration ecosystem with IoT device integration, wearable technology support, third-party APIs, and webhook system

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime, time, date, timedelta
import enum

class DeviceType(enum.Enum):
    IOT_SENSOR = "IoT Sensor"
    WEARABLE = "Wearable"
    SMART_OFFICE = "Smart Office"
    VEHICLE = "Vehicle"
    ENVIRONMENTAL = "Environmental"
    SECURITY = "Security"
    CUSTOM = "Custom"

class DeviceStatus(enum.Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"
    MAINTENANCE = "Maintenance"
    ERROR = "Error"
    UNKNOWN = "Unknown"

class IntegrationType(enum.Enum):
    API = "API"
    WEBHOOK = "Webhook"
    MQTT = "MQTT"
    REST = "REST"
    GRAPHQL = "GraphQL"
    SOAP = "SOAP"
    CUSTOM = "Custom"

class WebhookEvent(enum.Enum):
    DEVICE_DATA = "Device Data"
    USER_ACTION = "User Action"
    SYSTEM_EVENT = "System Event"
    ALERT = "Alert"
    NOTIFICATION = "Notification"
    CUSTOM = "Custom"

class IoTDevice(BaseModel):
    """IoT device model"""
    __tablename__ = 'iot_devices'
    
    # Device Information
    device_name = db.Column(db.String(200), nullable=False)
    device_description = db.Column(db.Text)
    device_type = db.Column(db.Enum(DeviceType), nullable=False)
    device_model = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    serial_number = db.Column(db.String(100), unique=True)
    
    # Device Status
    device_status = db.Column(db.Enum(DeviceStatus), default=DeviceStatus.UNKNOWN)
    is_active = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    battery_level = db.Column(db.Float, default=0.0)
    signal_strength = db.Column(db.Float, default=0.0)
    
    # Location Information
    location_name = db.Column(db.String(200))
    location_coordinates = db.Column(db.JSON)
    installation_date = db.Column(db.Date)
    
    # Device Capabilities
    capabilities = db.Column(db.JSON)  # List of device capabilities
    sensors = db.Column(db.JSON)  # List of sensors
    actuators = db.Column(db.JSON)  # List of actuators
    
    # Configuration
    device_config = db.Column(db.JSON)  # Device configuration
    calibration_data = db.Column(db.JSON)  # Calibration data
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'device_name': self.device_name,
            'device_description': self.device_description,
            'device_type': self.device_type.value if self.device_type else None,
            'device_model': self.device_model,
            'manufacturer': self.manufacturer,
            'serial_number': self.serial_number,
            'device_status': self.device_status.value if self.device_status else None,
            'is_active': self.is_active,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'battery_level': self.battery_level,
            'signal_strength': self.signal_strength,
            'location_name': self.location_name,
            'location_coordinates': self.location_coordinates,
            'installation_date': self.installation_date.isoformat() if self.installation_date else None,
            'capabilities': self.capabilities,
            'sensors': self.sensors,
            'actuators': self.actuators,
            'device_config': self.device_config,
            'calibration_data': self.calibration_data,
            'company_id': self.company_id
        })
        return data

class WearableDevice(BaseModel):
    """Wearable device model"""
    __tablename__ = 'wearable_devices'
    
    # Device Information
    device_name = db.Column(db.String(200), nullable=False)
    device_type = db.Column(db.String(100), nullable=False)  # Smartwatch, Fitness Tracker, etc.
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100), unique=True)
    
    # User Association
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Device Status
    device_status = db.Column(db.Enum(DeviceStatus), default=DeviceStatus.UNKNOWN)
    is_active = db.Column(db.Boolean, default=True)
    last_synced = db.Column(db.DateTime, default=datetime.utcnow)
    battery_level = db.Column(db.Float, default=0.0)
    
    # Health Metrics
    heart_rate = db.Column(db.Float, default=0.0)
    steps_count = db.Column(db.Integer, default=0)
    calories_burned = db.Column(db.Float, default=0.0)
    sleep_hours = db.Column(db.Float, default=0.0)
    stress_level = db.Column(db.Float, default=0.0)
    
    # Device Capabilities
    capabilities = db.Column(db.JSON)  # List of device capabilities
    sensors = db.Column(db.JSON)  # List of sensors
    supported_metrics = db.Column(db.JSON)  # List of supported health metrics
    
    # Configuration
    device_config = db.Column(db.JSON)  # Device configuration
    sync_settings = db.Column(db.JSON)  # Sync settings
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'device_name': self.device_name,
            'device_type': self.device_type,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'serial_number': self.serial_number,
            'user_id': self.user_id,
            'device_status': self.device_status.value if self.device_status else None,
            'is_active': self.is_active,
            'last_synced': self.last_synced.isoformat() if self.last_synced else None,
            'battery_level': self.battery_level,
            'heart_rate': self.heart_rate,
            'steps_count': self.steps_count,
            'calories_burned': self.calories_burned,
            'sleep_hours': self.sleep_hours,
            'stress_level': self.stress_level,
            'capabilities': self.capabilities,
            'sensors': self.sensors,
            'supported_metrics': self.supported_metrics,
            'device_config': self.device_config,
            'sync_settings': self.sync_settings,
            'company_id': self.company_id
        })
        return data

class DeviceData(BaseModel):
    """Device data model"""
    __tablename__ = 'device_data'
    
    # Data Information
    data_type = db.Column(db.String(100), nullable=False)
    data_value = db.Column(db.Float, nullable=False)
    data_unit = db.Column(db.String(50), default='')
    data_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Device Association
    device_id = db.Column(db.Integer, db.ForeignKey('iot_devices.id'))
    iot_device = relationship("IoTDevice")
    wearable_device_id = db.Column(db.Integer, db.ForeignKey('wearable_devices.id'))
    wearable_device = relationship("WearableDevice")
    
    # Data Quality
    data_quality = db.Column(db.Float, default=1.0)  # 0-1
    is_validated = db.Column(db.Boolean, default=False)
    validation_notes = db.Column(db.Text)
    
    # Additional Data
    metadata = db.Column(db.JSON)  # Additional metadata
    raw_data = db.Column(db.JSON)  # Raw device data
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'data_type': self.data_type,
            'data_value': self.data_value,
            'data_unit': self.data_unit,
            'data_timestamp': self.data_timestamp.isoformat() if self.data_timestamp else None,
            'device_id': self.device_id,
            'wearable_device_id': self.wearable_device_id,
            'data_quality': self.data_quality,
            'is_validated': self.is_validated,
            'validation_notes': self.validation_notes,
            'metadata': self.metadata,
            'raw_data': self.raw_data,
            'company_id': self.company_id
        })
        return data

class ThirdPartyIntegration(BaseModel):
    """Third-party integration model"""
    __tablename__ = 'third_party_integrations'
    
    # Integration Information
    integration_name = db.Column(db.String(200), nullable=False)
    integration_description = db.Column(db.Text)
    integration_type = db.Column(db.Enum(IntegrationType), nullable=False)
    provider_name = db.Column(db.String(100), nullable=False)
    provider_url = db.Column(db.String(500))
    
    # Authentication
    api_key = db.Column(db.String(500))
    api_secret = db.Column(db.String(500))
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expires = db.Column(db.DateTime)
    
    # Integration Settings
    is_active = db.Column(db.Boolean, default=True)
    sync_enabled = db.Column(db.Boolean, default=True)
    sync_frequency = db.Column(db.Integer, default=15)  # minutes
    rate_limit = db.Column(db.Integer, default=1000)  # requests per hour
    
    # Configuration
    integration_config = db.Column(db.JSON)  # Integration configuration
    webhook_url = db.Column(db.String(500))
    webhook_secret = db.Column(db.String(500))
    
    # Status
    last_sync = db.Column(db.DateTime)
    sync_status = db.Column(db.String(50), default='Pending')
    error_count = db.Column(db.Integer, default=0)
    last_error = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'integration_name': self.integration_name,
            'integration_description': self.integration_description,
            'integration_type': self.integration_type.value if self.integration_type else None,
            'provider_name': self.provider_name,
            'provider_url': self.provider_url,
            'api_key': self.api_key,
            'api_secret': self.api_secret,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_expires': self.token_expires.isoformat() if self.token_expires else None,
            'is_active': self.is_active,
            'sync_enabled': self.sync_enabled,
            'sync_frequency': self.sync_frequency,
            'rate_limit': self.rate_limit,
            'integration_config': self.integration_config,
            'webhook_url': self.webhook_url,
            'webhook_secret': self.webhook_secret,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'sync_status': self.sync_status,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'company_id': self.company_id
        })
        return data

class WebhookSubscription(BaseModel):
    """Webhook subscription model"""
    __tablename__ = 'webhook_subscriptions'
    
    # Subscription Information
    subscription_name = db.Column(db.String(200), nullable=False)
    webhook_url = db.Column(db.String(500), nullable=False)
    webhook_secret = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    
    # Event Configuration
    subscribed_events = db.Column(db.JSON)  # List of subscribed events
    event_filters = db.Column(db.JSON)  # Event filters
    retry_count = db.Column(db.Integer, default=3)
    timeout_seconds = db.Column(db.Integer, default=30)
    
    # Delivery Settings
    delivery_method = db.Column(db.String(50), default='POST')  # POST, PUT, PATCH
    content_type = db.Column(db.String(50), default='application/json')
    headers = db.Column(db.JSON)  # Additional headers
    
    # Status
    last_delivery = db.Column(db.DateTime)
    delivery_status = db.Column(db.String(50), default='Pending')
    failure_count = db.Column(db.Integer, default=0)
    last_failure = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'subscription_name': self.subscription_name,
            'webhook_url': self.webhook_url,
            'webhook_secret': self.webhook_secret,
            'is_active': self.is_active,
            'subscribed_events': self.subscribed_events,
            'event_filters': self.event_filters,
            'retry_count': self.retry_count,
            'timeout_seconds': self.timeout_seconds,
            'delivery_method': self.delivery_method,
            'content_type': self.content_type,
            'headers': self.headers,
            'last_delivery': self.last_delivery.isoformat() if self.last_delivery else None,
            'delivery_status': self.delivery_status,
            'failure_count': self.failure_count,
            'last_failure': self.last_failure,
            'company_id': self.company_id
        })
        return data

class WebhookEvent(BaseModel):
    """Webhook event model"""
    __tablename__ = 'webhook_events'
    
    # Event Information
    event_type = db.Column(db.Enum(WebhookEvent), nullable=False)
    event_name = db.Column(db.String(200), nullable=False)
    event_data = db.Column(db.JSON, nullable=False)
    event_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Source Information
    source_system = db.Column(db.String(100))
    source_id = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    user = relationship("Employee")
    
    # Delivery Information
    delivery_status = db.Column(db.String(50), default='Pending')
    delivery_attempts = db.Column(db.Integer, default=0)
    last_delivery_attempt = db.Column(db.DateTime)
    delivery_response = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'event_type': self.event_type.value if self.event_type else None,
            'event_name': self.event_name,
            'event_data': self.event_data,
            'event_timestamp': self.event_timestamp.isoformat() if self.event_timestamp else None,
            'source_system': self.source_system,
            'source_id': self.source_id,
            'user_id': self.user_id,
            'delivery_status': self.delivery_status,
            'delivery_attempts': self.delivery_attempts,
            'last_delivery_attempt': self.last_delivery_attempt.isoformat() if self.last_delivery_attempt else None,
            'delivery_response': self.delivery_response,
            'company_id': self.company_id
        })
        return data

class DataSyncLog(BaseModel):
    """Data sync log model"""
    __tablename__ = 'data_sync_logs'
    
    # Sync Information
    sync_type = db.Column(db.String(50), nullable=False)  # Inbound, Outbound, Bidirectional
    source_system = db.Column(db.String(100), nullable=False)
    target_system = db.Column(db.String(100), nullable=False)
    sync_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    sync_end_time = db.Column(db.DateTime)
    sync_duration = db.Column(db.Float, default=0.0)  # seconds
    
    # Sync Results
    records_processed = db.Column(db.Integer, default=0)
    records_synced = db.Column(db.Integer, default=0)
    records_created = db.Column(db.Integer, default=0)
    records_updated = db.Column(db.Integer, default=0)
    records_deleted = db.Column(db.Integer, default=0)
    records_failed = db.Column(db.Integer, default=0)
    
    # Error Information
    error_message = db.Column(db.Text)
    error_details = db.Column(db.JSON)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'sync_type': self.sync_type,
            'source_system': self.source_system,
            'target_system': self.target_system,
            'sync_start_time': self.sync_start_time.isoformat() if self.sync_start_time else None,
            'sync_end_time': self.sync_end_time.isoformat() if self.sync_end_time else None,
            'sync_duration': self.sync_duration,
            'records_processed': self.records_processed,
            'records_synced': self.records_synced,
            'records_created': self.records_created,
            'records_updated': self.records_updated,
            'records_deleted': self.records_deleted,
            'records_failed': self.records_failed,
            'error_message': self.error_message,
            'error_details': self.error_details,
            'company_id': self.company_id
        })
        return data

class SmartOfficeDevice(BaseModel):
    """Smart office device model"""
    __tablename__ = 'smart_office_devices'
    
    # Device Information
    device_name = db.Column(db.String(200), nullable=False)
    device_type = db.Column(db.String(100), nullable=False)  # Smart Light, Thermostat, etc.
    location = db.Column(db.String(200))
    room_number = db.Column(db.String(50))
    
    # Device Status
    device_status = db.Column(db.Enum(DeviceStatus), default=DeviceStatus.UNKNOWN)
    is_active = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Device Data
    current_value = db.Column(db.Float, default=0.0)
    target_value = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(50))
    
    # Automation
    automation_enabled = db.Column(db.Boolean, default=False)
    automation_rules = db.Column(db.JSON)  # Automation rules
    schedule = db.Column(db.JSON)  # Device schedule
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'device_name': self.device_name,
            'device_type': self.device_type,
            'location': self.location,
            'room_number': self.room_number,
            'device_status': self.device_status.value if self.device_status else None,
            'is_active': self.is_active,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'current_value': self.current_value,
            'target_value': self.target_value,
            'unit': self.unit,
            'automation_enabled': self.automation_enabled,
            'automation_rules': self.automation_rules,
            'schedule': self.schedule,
            'company_id': self.company_id
        })
        return data
