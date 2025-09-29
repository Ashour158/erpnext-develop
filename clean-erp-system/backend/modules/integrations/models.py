# Integrations Models
# Third-party integrations, API marketplace, and external system connections

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

class IntegrationType(enum.Enum):
    API = "API"
    WEBHOOK = "Webhook"
    FILE_TRANSFER = "File Transfer"
    DATABASE = "Database"
    MESSAGE_QUEUE = "Message Queue"
    CLOUD_SERVICE = "Cloud Service"

class IntegrationStatus(enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ERROR = "Error"
    CONFIGURING = "Configuring"
    TESTING = "Testing"

class AuthenticationType(enum.Enum):
    API_KEY = "API Key"
    OAUTH2 = "OAuth2"
    BASIC_AUTH = "Basic Auth"
    BEARER_TOKEN = "Bearer Token"
    CUSTOM = "Custom"

class SyncDirection(enum.Enum):
    INBOUND = "Inbound"
    OUTBOUND = "Outbound"
    BIDIRECTIONAL = "Bidirectional"

class WebhookEvent(enum.Enum):
    CREATED = "Created"
    UPDATED = "Updated"
    DELETED = "Deleted"
    STATUS_CHANGED = "Status Changed"
    CUSTOM = "Custom"

# Integration Models
class Integration(BaseModel):
    """Integration model"""
    __tablename__ = 'integrations'
    
    # Integration Information
    integration_name = db.Column(db.String(200), nullable=False)
    integration_description = db.Column(db.Text)
    integration_type = db.Column(db.Enum(IntegrationType), nullable=False)
    external_system = db.Column(db.String(200), nullable=False)  # Salesforce, SAP, etc.
    
    # Integration Configuration
    base_url = db.Column(db.String(500))
    api_version = db.Column(db.String(50))
    authentication_type = db.Column(db.Enum(AuthenticationType), nullable=False)
    auth_config = db.Column(db.JSON)  # Authentication configuration
    
    # Integration Settings
    status = db.Column(db.Enum(IntegrationStatus), default=IntegrationStatus.CONFIGURING)
    is_active = db.Column(db.Boolean, default=False)
    sync_direction = db.Column(db.Enum(SyncDirection), default=SyncDirection.BIDIRECTIONAL)
    sync_frequency = db.Column(db.String(50), default='Real-time')  # Real-time, Hourly, Daily, etc.
    
    # Integration Details
    supported_entities = db.Column(db.JSON)  # List of supported entities
    field_mappings = db.Column(db.JSON)  # Field mappings between systems
    transformation_rules = db.Column(db.JSON)  # Data transformation rules
    
    # Performance Metrics
    total_syncs = db.Column(db.Integer, default=0)
    successful_syncs = db.Column(db.Integer, default=0)
    failed_syncs = db.Column(db.Integer, default=0)
    last_sync = db.Column(db.DateTime)
    average_sync_time = db.Column(db.Float, default=0.0)  # seconds
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    integration_logs = relationship("IntegrationLog", back_populates="integration")
    integration_syncs = relationship("IntegrationSync", back_populates="integration")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'integration_name': self.integration_name,
            'integration_description': self.integration_description,
            'integration_type': self.integration_type.value if self.integration_type else None,
            'external_system': self.external_system,
            'base_url': self.base_url,
            'api_version': self.api_version,
            'authentication_type': self.authentication_type.value if self.authentication_type else None,
            'auth_config': self.auth_config,
            'status': self.status.value if self.status else None,
            'is_active': self.is_active,
            'sync_direction': self.sync_direction.value if self.sync_direction else None,
            'sync_frequency': self.sync_frequency,
            'supported_entities': self.supported_entities,
            'field_mappings': self.field_mappings,
            'transformation_rules': self.transformation_rules,
            'total_syncs': self.total_syncs,
            'successful_syncs': self.successful_syncs,
            'failed_syncs': self.failed_syncs,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'average_sync_time': self.average_sync_time,
            'company_id': self.company_id
        })
        return data

class IntegrationLog(BaseModel):
    """Integration log model"""
    __tablename__ = 'integration_logs'
    
    # Log Information
    log_level = db.Column(db.String(50), default='INFO')  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_message = db.Column(db.Text, nullable=False)
    log_details = db.Column(db.JSON)  # Additional log details
    
    # Integration Association
    integration_id = db.Column(db.Integer, db.ForeignKey('integrations.id'), nullable=False)
    integration = relationship("Integration", back_populates="integration_logs")
    
    # Operation Details
    operation_type = db.Column(db.String(100))  # Sync, Auth, Test, etc.
    entity_type = db.Column(db.String(100))  # Customer, Invoice, etc.
    entity_id = db.Column(db.String(100))
    
    # Performance Data
    execution_time = db.Column(db.Float, default=0.0)  # seconds
    memory_usage = db.Column(db.Float, default=0.0)  # MB
    network_latency = db.Column(db.Float, default=0.0)  # milliseconds
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'log_level': self.log_level,
            'log_message': self.log_message,
            'log_details': self.log_details,
            'integration_id': self.integration_id,
            'operation_type': self.operation_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'execution_time': self.execution_time,
            'memory_usage': self.memory_usage,
            'network_latency': self.network_latency,
            'company_id': self.company_id
        })
        return data

class IntegrationSync(BaseModel):
    """Integration sync model"""
    __tablename__ = 'integration_syncs'
    
    # Sync Information
    sync_id = db.Column(db.String(100), unique=True, nullable=False)
    sync_type = db.Column(db.String(100), nullable=False)  # Full, Incremental, Manual
    sync_status = db.Column(db.String(50), default='Running')  # Running, Completed, Failed, Cancelled
    
    # Integration Association
    integration_id = db.Column(db.Integer, db.ForeignKey('integrations.id'), nullable=False)
    integration = relationship("Integration", back_populates="integration_syncs")
    
    # Sync Details
    sync_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    sync_end_time = db.Column(db.DateTime)
    sync_duration = db.Column(db.Float, default=0.0)  # seconds
    
    # Sync Data
    entities_synced = db.Column(db.JSON)  # List of synced entities
    sync_statistics = db.Column(db.JSON)  # Sync statistics
    error_details = db.Column(db.JSON)  # Error details if failed
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'sync_id': self.sync_id,
            'sync_type': self.sync_type,
            'sync_status': self.sync_status,
            'integration_id': self.integration_id,
            'sync_start_time': self.sync_start_time.isoformat() if self.sync_start_time else None,
            'sync_end_time': self.sync_end_time.isoformat() if self.sync_end_time else None,
            'sync_duration': self.sync_duration,
            'entities_synced': self.entities_synced,
            'sync_statistics': self.sync_statistics,
            'error_details': self.error_details,
            'company_id': self.company_id
        })
        return data

# API Marketplace Models
class APIMarketplace(BaseModel):
    """API marketplace model"""
    __tablename__ = 'api_marketplace'
    
    # API Information
    api_name = db.Column(db.String(200), nullable=False)
    api_description = db.Column(db.Text)
    api_version = db.Column(db.String(50), default='1.0.0')
    api_category = db.Column(db.String(100))  # CRM, Finance, HR, etc.
    
    # API Configuration
    base_url = db.Column(db.String(500), nullable=False)
    api_documentation = db.Column(db.String(500))
    api_specification = db.Column(db.JSON)  # OpenAPI/Swagger specification
    
    # API Settings
    is_public = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    requires_approval = db.Column(db.Boolean, default=False)
    
    # API Usage
    total_requests = db.Column(db.Integer, default=0)
    successful_requests = db.Column(db.Integer, default=0)
    failed_requests = db.Column(db.Integer, default=0)
    average_response_time = db.Column(db.Float, default=0.0)  # milliseconds
    
    # Rate Limiting
    rate_limit = db.Column(db.Integer, default=1000)  # requests per hour
    rate_limit_window = db.Column(db.Integer, default=3600)  # seconds
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    api_subscriptions = relationship("APISubscription", back_populates="api_marketplace")
    api_usage_logs = relationship("APIUsageLog", back_populates="api_marketplace")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'api_name': self.api_name,
            'api_description': self.api_description,
            'api_version': self.api_version,
            'api_category': self.api_category,
            'base_url': self.base_url,
            'api_documentation': self.api_documentation,
            'api_specification': self.api_specification,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'requires_approval': self.requires_approval,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'average_response_time': self.average_response_time,
            'rate_limit': self.rate_limit,
            'rate_limit_window': self.rate_limit_window,
            'company_id': self.company_id
        })
        return data

class APISubscription(BaseModel):
    """API subscription model"""
    __tablename__ = 'api_subscriptions'
    
    # Subscription Information
    subscription_name = db.Column(db.String(200), nullable=False)
    subscription_status = db.Column(db.String(50), default='Active')  # Active, Inactive, Suspended, Cancelled
    
    # API Association
    api_id = db.Column(db.Integer, db.ForeignKey('api_marketplace.id'), nullable=False)
    api_marketplace = relationship("APIMarketplace", back_populates="api_subscriptions")
    
    # Subscriber Information
    subscriber_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    subscriber = relationship("Employee")
    subscriber_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    subscriber_company = relationship("Company", foreign_keys=[subscriber_company_id])
    
    # Subscription Details
    api_key = db.Column(db.String(255), unique=True, nullable=False)
    subscription_tier = db.Column(db.String(100), default='Basic')  # Basic, Premium, Enterprise
    usage_limit = db.Column(db.Integer, default=1000)  # requests per month
    current_usage = db.Column(db.Integer, default=0)
    
    # Subscription Dates
    subscription_start = db.Column(db.Date, default=date.today)
    subscription_end = db.Column(db.Date)
    last_used = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'subscription_name': self.subscription_name,
            'subscription_status': self.subscription_status,
            'api_id': self.api_id,
            'subscriber_id': self.subscriber_id,
            'subscriber_company_id': self.subscriber_company_id,
            'api_key': self.api_key,
            'subscription_tier': self.subscription_tier,
            'usage_limit': self.usage_limit,
            'current_usage': self.current_usage,
            'subscription_start': self.subscription_start.isoformat() if self.subscription_start else None,
            'subscription_end': self.subscription_end.isoformat() if self.subscription_end else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'company_id': self.company_id
        })
        return data

class APIUsageLog(BaseModel):
    """API usage log model"""
    __tablename__ = 'api_usage_logs'
    
    # Usage Information
    request_id = db.Column(db.String(100), unique=True, nullable=False)
    endpoint = db.Column(db.String(500), nullable=False)
    method = db.Column(db.String(10), nullable=False)  # GET, POST, PUT, DELETE
    status_code = db.Column(db.Integer, default=200)
    
    # API Association
    api_id = db.Column(db.Integer, db.ForeignKey('api_marketplace.id'), nullable=False)
    api_marketplace = relationship("APIMarketplace", back_populates="api_usage_logs")
    
    # Request Details
    request_data = db.Column(db.JSON)  # Request payload
    response_data = db.Column(db.JSON)  # Response payload
    request_size = db.Column(db.Integer, default=0)  # bytes
    response_size = db.Column(db.Integer, default=0)  # bytes
    
    # Performance Data
    response_time = db.Column(db.Float, default=0.0)  # milliseconds
    processing_time = db.Column(db.Float, default=0.0)  # milliseconds
    
    # Client Information
    client_ip = db.Column(db.String(45))  # IPv4 or IPv6
    user_agent = db.Column(db.String(500))
    api_key = db.Column(db.String(255))
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'request_id': self.request_id,
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'api_id': self.api_id,
            'request_data': self.request_data,
            'response_data': self.response_data,
            'request_size': self.request_size,
            'response_size': self.response_size,
            'response_time': self.response_time,
            'processing_time': self.processing_time,
            'client_ip': self.client_ip,
            'user_agent': self.user_agent,
            'api_key': self.api_key,
            'company_id': self.company_id
        })
        return data

# Webhook Models
class Webhook(BaseModel):
    """Webhook model"""
    __tablename__ = 'webhooks'
    
    # Webhook Information
    webhook_name = db.Column(db.String(200), nullable=False)
    webhook_description = db.Column(db.Text)
    webhook_url = db.Column(db.String(500), nullable=False)
    
    # Webhook Configuration
    events = db.Column(db.JSON)  # List of events to listen for
    headers = db.Column(db.JSON)  # Custom headers
    authentication = db.Column(db.JSON)  # Authentication configuration
    
    # Webhook Settings
    is_active = db.Column(db.Boolean, default=True)
    retry_count = db.Column(db.Integer, default=3)
    timeout = db.Column(db.Integer, default=30)  # seconds
    
    # Webhook Statistics
    total_requests = db.Column(db.Integer, default=0)
    successful_requests = db.Column(db.Integer, default=0)
    failed_requests = db.Column(db.Integer, default=0)
    last_triggered = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    webhook_logs = relationship("WebhookLog", back_populates="webhook")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'webhook_name': self.webhook_name,
            'webhook_description': self.webhook_description,
            'webhook_url': self.webhook_url,
            'events': self.events,
            'headers': self.headers,
            'authentication': self.authentication,
            'is_active': self.is_active,
            'retry_count': self.retry_count,
            'timeout': self.timeout,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'company_id': self.company_id
        })
        return data

class WebhookLog(BaseModel):
    """Webhook log model"""
    __tablename__ = 'webhook_logs'
    
    # Log Information
    event_type = db.Column(db.Enum(WebhookEvent), nullable=False)
    payload = db.Column(db.JSON)  # Webhook payload
    
    # Webhook Association
    webhook_id = db.Column(db.Integer, db.ForeignKey('webhooks.id'), nullable=False)
    webhook = relationship("Webhook", back_populates="webhook_logs")
    
    # Request Details
    request_url = db.Column(db.String(500))
    request_method = db.Column(db.String(10), default='POST')
    request_headers = db.Column(db.JSON)
    request_body = db.Column(db.Text)
    
    # Response Details
    response_status = db.Column(db.Integer)
    response_headers = db.Column(db.JSON)
    response_body = db.Column(db.Text)
    response_time = db.Column(db.Float, default=0.0)  # milliseconds
    
    # Retry Information
    retry_count = db.Column(db.Integer, default=0)
    is_successful = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'event_type': self.event_type.value if self.event_type else None,
            'payload': self.payload,
            'webhook_id': self.webhook_id,
            'request_url': self.request_url,
            'request_method': self.request_method,
            'request_headers': self.request_headers,
            'request_body': self.request_body,
            'response_status': self.response_status,
            'response_headers': self.response_headers,
            'response_body': self.response_body,
            'response_time': self.response_time,
            'retry_count': self.retry_count,
            'is_successful': self.is_successful,
            'error_message': self.error_message,
            'company_id': self.company_id
        })
        return data
