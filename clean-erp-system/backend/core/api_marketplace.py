# API Marketplace and Integration System
# Generate APIs for marketplace installation

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum

class APIType(enum.Enum):
    REST = "REST"
    GRAPHQL = "GraphQL"
    SOAP = "SOAP"
    WEBHOOK = "Webhook"
    WEBSOCKET = "WebSocket"

class APIVersion(enum.Enum):
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"
    BETA = "beta"
    ALPHA = "alpha"

class APIMarketplace(BaseModel):
    """API marketplace model"""
    __tablename__ = 'api_marketplace'
    
    # API Information
    api_name = db.Column(db.String(200), nullable=False)
    api_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # API Configuration
    api_type = db.Column(db.Enum(APIType), nullable=False)
    api_version = db.Column(db.Enum(APIVersion), default=APIVersion.V1)
    base_url = db.Column(db.String(500), nullable=False)
    endpoint = db.Column(db.String(500), nullable=False)
    
    # API Settings
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    requires_authentication = db.Column(db.Boolean, default=True)
    
    # API Documentation
    api_documentation = db.Column(db.Text)
    api_examples = db.Column(db.JSON)  # API examples configuration
    api_schema = db.Column(db.JSON)  # API schema configuration
    
    # API Statistics
    total_requests = db.Column(db.Integer, default=0)
    successful_requests = db.Column(db.Integer, default=0)
    failed_requests = db.Column(db.Integer, default=0)
    average_response_time = db.Column(db.Float, default=0.0)  # milliseconds
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'api_name': self.api_name,
            'api_code': self.api_code,
            'description': self.description,
            'api_type': self.api_type.value if self.api_type else None,
            'api_version': self.api_version.value if self.api_version else None,
            'base_url': self.base_url,
            'endpoint': self.endpoint,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'is_featured': self.is_featured,
            'requires_authentication': self.requires_authentication,
            'api_documentation': self.api_documentation,
            'api_examples': self.api_examples,
            'api_schema': self.api_schema,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'average_response_time': self.average_response_time,
            'company_id': self.company_id
        })
        return data

class APIAuthentication(BaseModel):
    """API authentication model"""
    __tablename__ = 'api_authentication'
    
    # Authentication Information
    auth_name = db.Column(db.String(200), nullable=False)
    auth_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Authentication Configuration
    auth_type = db.Column(db.String(50), nullable=False)  # API Key, OAuth, JWT, Basic
    auth_config = db.Column(db.JSON)  # Authentication configuration
    auth_credentials = db.Column(db.JSON)  # Authentication credentials
    
    # Authentication Settings
    is_active = db.Column(db.Boolean, default=True)
    is_secure = db.Column(db.Boolean, default=True)
    expires_in = db.Column(db.Integer, default=3600)  # seconds
    
    # Authentication Statistics
    total_authentications = db.Column(db.Integer, default=0)
    successful_authentications = db.Column(db.Integer, default=0)
    failed_authentications = db.Column(db.Integer, default=0)
    last_authentication_date = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'auth_name': self.auth_name,
            'auth_code': self.auth_code,
            'description': self.description,
            'auth_type': self.auth_type,
            'auth_config': self.auth_config,
            'auth_credentials': self.auth_credentials,
            'is_active': self.is_active,
            'is_secure': self.is_secure,
            'expires_in': self.expires_in,
            'total_authentications': self.total_authentications,
            'successful_authentications': self.successful_authentications,
            'failed_authentications': self.failed_authentications,
            'last_authentication_date': self.last_authentication_date.isoformat() if self.last_authentication_date else None,
            'company_id': self.company_id
        })
        return data

class APIRateLimit(BaseModel):
    """API rate limit model"""
    __tablename__ = 'api_rate_limits'
    
    # Rate Limit Information
    rate_limit_name = db.Column(db.String(200), nullable=False)
    rate_limit_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Rate Limit Configuration
    requests_per_minute = db.Column(db.Integer, default=60)
    requests_per_hour = db.Column(db.Integer, default=1000)
    requests_per_day = db.Column(db.Integer, default=10000)
    burst_limit = db.Column(db.Integer, default=100)
    
    # Rate Limit Settings
    is_active = db.Column(db.Boolean, default=True)
    is_global = db.Column(db.Boolean, default=False)
    is_per_user = db.Column(db.Boolean, default=True)
    
    # Rate Limit Statistics
    total_requests = db.Column(db.Integer, default=0)
    blocked_requests = db.Column(db.Integer, default=0)
    rate_limit_hits = db.Column(db.Integer, default=0)
    last_rate_limit_hit = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'rate_limit_name': self.rate_limit_name,
            'rate_limit_code': self.rate_limit_code,
            'description': self.description,
            'requests_per_minute': self.requests_per_minute,
            'requests_per_hour': self.requests_per_hour,
            'requests_per_day': self.requests_per_day,
            'burst_limit': self.burst_limit,
            'is_active': self.is_active,
            'is_global': self.is_global,
            'is_per_user': self.is_per_user,
            'total_requests': self.total_requests,
            'blocked_requests': self.blocked_requests,
            'rate_limit_hits': self.rate_limit_hits,
            'last_rate_limit_hit': self.last_rate_limit_hit.isoformat() if self.last_rate_limit_hit else None,
            'company_id': self.company_id
        })
        return data

class APIMonitoring(BaseModel):
    """API monitoring model"""
    __tablename__ = 'api_monitoring'
    
    # Monitoring Information
    monitoring_name = db.Column(db.String(200), nullable=False)
    monitoring_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Monitoring Configuration
    monitoring_type = db.Column(db.String(50), nullable=False)  # Health, Performance, Security
    monitoring_config = db.Column(db.JSON)  # Monitoring configuration
    alert_rules = db.Column(db.JSON)  # Alert rules configuration
    
    # Monitoring Settings
    is_active = db.Column(db.Boolean, default=True)
    is_automatic = db.Column(db.Boolean, default=False)
    monitoring_interval = db.Column(db.Integer, default=60)  # seconds
    
    # Monitoring Statistics
    total_checks = db.Column(db.Integer, default=0)
    successful_checks = db.Column(db.Integer, default=0)
    failed_checks = db.Column(db.Integer, default=0)
    last_check_date = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'monitoring_name': self.monitoring_name,
            'monitoring_code': self.monitoring_code,
            'description': self.description,
            'monitoring_type': self.monitoring_type,
            'monitoring_config': self.monitoring_config,
            'alert_rules': self.alert_rules,
            'is_active': self.is_active,
            'is_automatic': self.is_automatic,
            'monitoring_interval': self.monitoring_interval,
            'total_checks': self.total_checks,
            'successful_checks': self.successful_checks,
            'failed_checks': self.failed_checks,
            'last_check_date': self.last_check_date.isoformat() if self.last_check_date else None,
            'company_id': self.company_id
        })
        return data

class APIIntegration(BaseModel):
    """API integration model"""
    __tablename__ = 'api_integrations'
    
    # Integration Information
    integration_name = db.Column(db.String(200), nullable=False)
    integration_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Integration Configuration
    integration_type = db.Column(db.String(50), nullable=False)  # Internal, External, Third-party
    integration_config = db.Column(db.JSON)  # Integration configuration
    integration_mapping = db.Column(db.JSON)  # Integration mapping configuration
    
    # Integration Settings
    is_active = db.Column(db.Boolean, default=True)
    is_automatic = db.Column(db.Boolean, default=False)
    is_bidirectional = db.Column(db.Boolean, default=False)
    
    # Integration Statistics
    total_syncs = db.Column(db.Integer, default=0)
    successful_syncs = db.Column(db.Integer, default=0)
    failed_syncs = db.Column(db.Integer, default=0)
    last_sync_date = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'integration_name': self.integration_name,
            'integration_code': self.integration_code,
            'description': self.description,
            'integration_type': self.integration_type,
            'integration_config': self.integration_config,
            'integration_mapping': self.integration_mapping,
            'is_active': self.is_active,
            'is_automatic': self.is_automatic,
            'is_bidirectional': self.is_bidirectional,
            'total_syncs': self.total_syncs,
            'successful_syncs': self.successful_syncs,
            'failed_syncs': self.failed_syncs,
            'last_sync_date': self.last_sync_date.isoformat() if self.last_sync_date else None,
            'company_id': self.company_id
        })
        return data
