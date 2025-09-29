# IoT Integration for Supply Chain
# Real-time monitoring and data collection from IoT devices

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum
import json

class IoTDeviceType(enum.Enum):
    TEMPERATURE_SENSOR = "temperature_sensor"
    HUMIDITY_SENSOR = "humidity_sensor"
    PRESSURE_SENSOR = "pressure_sensor"
    MOTION_SENSOR = "motion_sensor"
    WEIGHT_SENSOR = "weight_sensor"
    GPS_TRACKER = "gps_tracker"
    RFID_READER = "rfid_reader"
    BARCODE_SCANNER = "barcode_scanner"
    CAMERA = "camera"
    AIR_QUALITY_SENSOR = "air_quality_sensor"
    VIBRATION_SENSOR = "vibration_sensor"
    LIGHT_SENSOR = "light_sensor"

class IoTDeviceStatus(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    DISCONNECTED = "disconnected"

class DataQuality(enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"

# IoT Device Management
class IoTDevice(Base):
    __tablename__ = 'iot_devices'
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), unique=True, nullable=False, index=True)
    device_name = Column(String(255), nullable=False)
    device_type = Column(Enum(IoTDeviceType), nullable=False)
    manufacturer = Column(String(255))
    model = Column(String(255))
    serial_number = Column(String(100))
    firmware_version = Column(String(50))
    hardware_version = Column(String(50))
    
    # Location and installation
    location_id = Column(Integer, ForeignKey('warehouse_locations.id'))
    installation_date = Column(DateTime, default=datetime.utcnow)
    last_maintenance_date = Column(DateTime)
    next_maintenance_date = Column(DateTime)
    
    # Device configuration
    device_config = Column(JSON)  # Device-specific configuration
    calibration_data = Column(JSON)  # Calibration parameters
    alert_thresholds = Column(JSON)  # Alert configuration
    
    # Status and connectivity
    status = Column(Enum(IoTDeviceStatus), default=IoTDeviceStatus.OFFLINE)
    last_seen = Column(DateTime)
    battery_level = Column(Float)  # For battery-powered devices
    signal_strength = Column(Float)  # For wireless devices
    
    # Data collection settings
    sampling_rate = Column(Integer, default=60)  # Seconds between readings
    data_retention_days = Column(Integer, default=365)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    location = relationship("WarehouseLocation")
    readings = relationship("IoTReading", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("IoTAlert", back_populates="device", cascade="all, delete-orphan")

# IoT Data Readings
class IoTReading(Base):
    __tablename__ = 'iot_readings'
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey('iot_devices.id'), nullable=False)
    reading_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Sensor data
    sensor_value = Column(Float, nullable=False)
    sensor_unit = Column(String(20))
    data_quality = Column(Enum(DataQuality), default=DataQuality.GOOD)
    
    # Environmental context
    temperature = Column(Float)  # Ambient temperature
    humidity = Column(Float)    # Ambient humidity
    pressure = Column(Float)    # Atmospheric pressure
    
    # Location data (if GPS enabled)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    accuracy = Column(Float)
    
    # Additional sensor data
    additional_data = Column(JSON)  # Device-specific additional readings
    
    # Data processing
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    processing_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    device = relationship("IoTDevice", back_populates="readings")

# IoT Alerts and Notifications
class IoTAlert(Base):
    __tablename__ = 'iot_alerts'
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey('iot_devices.id'), nullable=False)
    alert_type = Column(String(50), nullable=False)  # threshold, anomaly, device_error, maintenance
    alert_level = Column(String(20), nullable=False)  # info, warning, error, critical
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Alert data
    threshold_value = Column(Float)
    actual_value = Column(Float)
    deviation_percentage = Column(Float)
    alert_data = Column(JSON)  # Additional alert-specific data
    
    # Status and handling
    is_active = Column(Boolean, default=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, ForeignKey('users.id'))
    acknowledged_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Notification
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    recipients = Column(JSON)  # List of notification recipients
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    device = relationship("IoTDevice", back_populates="alerts")
    acknowledged_user = relationship("User", foreign_keys=[acknowledged_by])

# IoT Data Analytics
class IoTAnalytics(Base):
    __tablename__ = 'iot_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey('iot_devices.id'), nullable=False)
    analytics_type = Column(String(50), nullable=False)  # trend, anomaly, prediction, correlation
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Analytics results
    analytics_data = Column(JSON)  # Computed analytics results
    insights = Column(JSON)  # Key insights and findings
    recommendations = Column(JSON)  # Actionable recommendations
    
    # Performance metrics
    data_points_analyzed = Column(Integer)
    confidence_score = Column(Float)  # 0-1 confidence in results
    accuracy_score = Column(Float)  # 0-1 accuracy of predictions
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    calculated_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    device = relationship("IoTDevice")

# IoT Device Groups
class IoTDeviceGroup(Base):
    __tablename__ = 'iot_device_groups'
    
    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String(255), nullable=False)
    group_description = Column(Text)
    group_type = Column(String(50))  # warehouse, transport, production, storage
    
    # Group configuration
    group_config = Column(JSON)  # Group-specific settings
    alert_config = Column(JSON)  # Group-level alert settings
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    devices = relationship("IoTDevice", secondary="iot_device_group_memberships")

# IoT Device Group Membership
class IoTDeviceGroupMembership(Base):
    __tablename__ = 'iot_device_group_memberships'
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey('iot_devices.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('iot_device_groups.id'), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    device = relationship("IoTDevice")
    group = relationship("IoTDeviceGroup")

# IoT Data Processing Rules
class IoTProcessingRule(Base):
    __tablename__ = 'iot_processing_rules'
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(255), nullable=False)
    rule_description = Column(Text)
    rule_type = Column(String(50), nullable=False)  # filter, transform, aggregate, alert
    
    # Rule configuration
    rule_config = Column(JSON)  # Rule-specific configuration
    conditions = Column(JSON)  # Rule conditions
    actions = Column(JSON)  # Actions to take when rule matches
    
    # Rule execution
    is_active = Column(Boolean, default=True)
    execution_order = Column(Integer, default=0)
    last_executed = Column(DateTime)
    execution_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# IoT Data Export
class IoTDataExport(Base):
    __tablename__ = 'iot_data_exports'
    
    id = Column(Integer, primary_key=True, index=True)
    export_name = Column(String(255), nullable=False)
    export_type = Column(String(50), nullable=False)  # csv, json, xml, excel
    device_ids = Column(JSON)  # List of device IDs to export
    date_range_start = Column(DateTime, nullable=False)
    date_range_end = Column(DateTime, nullable=False)
    
    # Export configuration
    export_config = Column(JSON)  # Export-specific settings
    filters = Column(JSON)  # Data filters
    columns = Column(JSON)  # Columns to include
    
    # Export status
    status = Column(String(20), default='pending')  # pending, processing, completed, failed
    file_path = Column(String(500))
    file_size = Column(Integer)
    record_count = Column(Integer)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# IoT Dashboard
class IoTDashboard(Base):
    __tablename__ = 'iot_dashboards'
    
    id = Column(Integer, primary_key=True, index=True)
    dashboard_name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    dashboard_config = Column(JSON)  # Dashboard layout and widgets
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    
    # Dashboard settings
    refresh_interval = Column(Integer, default=30)  # Seconds
    auto_refresh = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")

# IoT Integration Status
class IoTIntegrationStatus(Base):
    __tablename__ = 'iot_integration_status'
    
    id = Column(Integer, primary_key=True, index=True)
    integration_name = Column(String(255), nullable=False)
    integration_type = Column(String(50), nullable=False)  # api, mqtt, websocket, file
    status = Column(String(20), nullable=False)  # active, inactive, error, maintenance
    
    # Integration details
    endpoint_url = Column(String(500))
    connection_config = Column(JSON)
    authentication_config = Column(JSON)
    
    # Status monitoring
    last_connection = Column(DateTime)
    last_data_received = Column(DateTime)
    connection_attempts = Column(Integer, default=0)
    failed_attempts = Column(Integer, default=0)
    
    # Error handling
    last_error = Column(Text)
    error_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    devices = relationship("IoTDevice", secondary="iot_integration_device_mappings")

# IoT Integration Device Mapping
class IoTIntegrationDeviceMapping(Base):
    __tablename__ = 'iot_integration_device_mappings'
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey('iot_integration_status.id'), nullable=False)
    device_id = Column(Integer, ForeignKey('iot_devices.id'), nullable=False)
    external_device_id = Column(String(100))  # Device ID in external system
    mapping_config = Column(JSON)  # Mapping configuration
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    integration = relationship("IoTIntegrationStatus")
    device = relationship("IoTDevice")
