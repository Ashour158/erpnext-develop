# Performance Optimization Models
# Models for performance optimization features including caching strategy, load balancing, and performance monitoring

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime, time, date, timedelta
import enum

class CacheType(enum.Enum):
    REDIS = "Redis"
    MEMCACHED = "Memcached"
    IN_MEMORY = "In Memory"
    DATABASE = "Database"
    FILE = "File"

class CacheStrategy(enum.Enum):
    LRU = "LRU"  # Least Recently Used
    LFU = "LFU"  # Least Frequently Used
    FIFO = "FIFO"  # First In First Out
    TTL = "TTL"  # Time To Live
    CUSTOM = "Custom"

class LoadBalancerType(enum.Enum):
    ROUND_ROBIN = "Round Robin"
    LEAST_CONNECTIONS = "Least Connections"
    WEIGHTED_ROUND_ROBIN = "Weighted Round Robin"
    IP_HASH = "IP Hash"
    LEAST_RESPONSE_TIME = "Least Response Time"

class PerformanceMetricType(enum.Enum):
    RESPONSE_TIME = "Response Time"
    THROUGHPUT = "Throughput"
    CPU_USAGE = "CPU Usage"
    MEMORY_USAGE = "Memory Usage"
    DISK_USAGE = "Disk Usage"
    NETWORK_USAGE = "Network Usage"
    ERROR_RATE = "Error Rate"
    AVAILABILITY = "Availability"

class CacheEntry(BaseModel):
    """Cache entry model"""
    __tablename__ = 'cache_entries'
    
    # Cache Information
    cache_key = db.Column(db.String(500), nullable=False, unique=True)
    cache_value = db.Column(db.Text, nullable=False)
    cache_type = db.Column(db.Enum(CacheType), nullable=False)
    cache_strategy = db.Column(db.Enum(CacheStrategy), default=CacheStrategy.TTL)
    
    # Cache Metadata
    cache_size = db.Column(db.Integer, default=0)  # bytes
    hit_count = db.Column(db.Integer, default=0)
    miss_count = db.Column(db.Integer, default=0)
    access_count = db.Column(db.Integer, default=0)
    
    # Cache Timing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    ttl = db.Column(db.Integer, default=3600)  # seconds
    
    # Cache Configuration
    cache_config = db.Column(db.JSON)  # Cache-specific configuration
    tags = db.Column(db.JSON)  # Cache tags for invalidation
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'cache_key': self.cache_key,
            'cache_value': self.cache_value,
            'cache_type': self.cache_type.value if self.cache_type else None,
            'cache_strategy': self.cache_strategy.value if self.cache_strategy else None,
            'cache_size': self.cache_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'access_count': self.access_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'ttl': self.ttl,
            'cache_config': self.cache_config,
            'tags': self.tags,
            'company_id': self.company_id
        })
        return data

class LoadBalancer(BaseModel):
    """Load balancer model"""
    __tablename__ = 'load_balancers'
    
    # Load Balancer Information
    balancer_name = db.Column(db.String(200), nullable=False)
    balancer_description = db.Column(db.Text)
    balancer_type = db.Column(db.Enum(LoadBalancerType), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Load Balancer Configuration
    balancer_config = db.Column(db.JSON)  # Load balancer configuration
    health_check_config = db.Column(db.JSON)  # Health check configuration
    ssl_config = db.Column(db.JSON)  # SSL configuration
    
    # Backend Servers
    backend_servers = db.Column(db.JSON)  # List of backend servers
    server_weights = db.Column(db.JSON)  # Server weights for weighted algorithms
    
    # Load Balancer Status
    status = db.Column(db.String(50), default='Active')  # Active, Inactive, Maintenance
    last_health_check = db.Column(db.DateTime)
    health_check_interval = db.Column(db.Integer, default=30)  # seconds
    
    # Performance Metrics
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
            'balancer_name': self.balancer_name,
            'balancer_description': self.balancer_description,
            'balancer_type': self.balancer_type.value if self.balancer_type else None,
            'is_active': self.is_active,
            'balancer_config': self.balancer_config,
            'health_check_config': self.health_check_config,
            'ssl_config': self.ssl_config,
            'backend_servers': self.backend_servers,
            'server_weights': self.server_weights,
            'status': self.status,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'health_check_interval': self.health_check_interval,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'average_response_time': self.average_response_time,
            'company_id': self.company_id
        })
        return data

class BackendServer(BaseModel):
    """Backend server model"""
    __tablename__ = 'backend_servers'
    
    # Server Information
    server_name = db.Column(db.String(200), nullable=False)
    server_description = db.Column(db.Text)
    server_url = db.Column(db.String(500), nullable=False)
    server_port = db.Column(db.Integer, default=80)
    server_protocol = db.Column(db.String(20), default='http')  # http, https
    
    # Load Balancer Association
    load_balancer_id = db.Column(db.Integer, db.ForeignKey('load_balancers.id'), nullable=False)
    load_balancer = relationship("LoadBalancer")
    
    # Server Configuration
    server_weight = db.Column(db.Integer, default=1)
    max_connections = db.Column(db.Integer, default=100)
    timeout = db.Column(db.Integer, default=30)  # seconds
    
    # Server Status
    is_active = db.Column(db.Boolean, default=True)
    is_healthy = db.Column(db.Boolean, default=True)
    last_health_check = db.Column(db.DateTime)
    health_check_url = db.Column(db.String(500))
    
    # Performance Metrics
    current_connections = db.Column(db.Integer, default=0)
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
            'server_name': self.server_name,
            'server_description': self.server_description,
            'server_url': self.server_url,
            'server_port': self.server_port,
            'server_protocol': self.server_protocol,
            'load_balancer_id': self.load_balancer_id,
            'server_weight': self.server_weight,
            'max_connections': self.max_connections,
            'timeout': self.timeout,
            'is_active': self.is_active,
            'is_healthy': self.is_healthy,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'health_check_url': self.health_check_url,
            'current_connections': self.current_connections,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'average_response_time': self.average_response_time,
            'company_id': self.company_id
        })
        return data

class PerformanceMetric(BaseModel):
    """Performance metric model"""
    __tablename__ = 'performance_metrics'
    
    # Metric Information
    metric_name = db.Column(db.String(200), nullable=False)
    metric_type = db.Column(db.Enum(PerformanceMetricType), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    metric_unit = db.Column(db.String(50), default='')
    
    # Metric Context
    resource_name = db.Column(db.String(200))  # Server, Database, API, etc.
    resource_id = db.Column(db.String(100))
    component = db.Column(db.String(100))  # Frontend, Backend, Database, etc.
    
    # Metric Timing
    metric_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    collection_interval = db.Column(db.Integer, default=60)  # seconds
    
    # Metric Metadata
    metric_metadata = db.Column(db.JSON)  # Additional metric data
    tags = db.Column(db.JSON)  # Metric tags
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'metric_name': self.metric_name,
            'metric_type': self.metric_type.value if self.metric_type else None,
            'metric_value': self.metric_value,
            'metric_unit': self.metric_unit,
            'resource_name': self.resource_name,
            'resource_id': self.resource_id,
            'component': self.component,
            'metric_timestamp': self.metric_timestamp.isoformat() if self.metric_timestamp else None,
            'collection_interval': self.collection_interval,
            'metric_metadata': self.metric_metadata,
            'tags': self.tags,
            'company_id': self.company_id
        })
        return data

class PerformanceAlert(BaseModel):
    """Performance alert model"""
    __tablename__ = 'performance_alerts'
    
    # Alert Information
    alert_name = db.Column(db.String(200), nullable=False)
    alert_description = db.Column(db.Text)
    alert_type = db.Column(db.String(100), nullable=False)  # Threshold, Anomaly, Trend
    severity = db.Column(db.String(50), default='Medium')  # Low, Medium, High, Critical
    
    # Alert Configuration
    metric_name = db.Column(db.String(200), nullable=False)
    threshold_value = db.Column(db.Float, nullable=False)
    comparison_operator = db.Column(db.String(20), default='>')  # >, <, >=, <=, ==, !=
    alert_condition = db.Column(db.Text)  # Custom alert condition
    
    # Alert Status
    is_active = db.Column(db.Boolean, default=True)
    is_triggered = db.Column(db.Boolean, default=False)
    last_triggered = db.Column(db.DateTime)
    trigger_count = db.Column(db.Integer, default=0)
    
    # Alert Actions
    alert_actions = db.Column(db.JSON)  # List of actions to take when alert is triggered
    notification_recipients = db.Column(db.JSON)  # List of notification recipients
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'alert_name': self.alert_name,
            'alert_description': self.alert_description,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'metric_name': self.metric_name,
            'threshold_value': self.threshold_value,
            'comparison_operator': self.comparison_operator,
            'alert_condition': self.alert_condition,
            'is_active': self.is_active,
            'is_triggered': self.is_triggered,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'trigger_count': self.trigger_count,
            'alert_actions': self.alert_actions,
            'notification_recipients': self.notification_recipients,
            'company_id': self.company_id
        })
        return data

class DatabaseOptimization(BaseModel):
    """Database optimization model"""
    __tablename__ = 'database_optimizations'
    
    # Optimization Information
    optimization_name = db.Column(db.String(200), nullable=False)
    optimization_description = db.Column(db.Text)
    optimization_type = db.Column(db.String(100), nullable=False)  # Index, Query, Schema, etc.
    
    # Database Information
    database_name = db.Column(db.String(200), nullable=False)
    table_name = db.Column(db.String(200))
    query_text = db.Column(db.Text)
    
    # Optimization Configuration
    optimization_config = db.Column(db.JSON)  # Optimization-specific configuration
    optimization_sql = db.Column(db.Text)  # SQL for optimization
    
    # Optimization Status
    is_applied = db.Column(db.Boolean, default=False)
    applied_at = db.Column(db.DateTime)
    applied_by = db.Column(db.Integer, db.ForeignKey('employees.id'))
    applier = relationship("Employee")
    
    # Performance Impact
    before_performance = db.Column(db.JSON)  # Performance metrics before optimization
    after_performance = db.Column(db.JSON)  # Performance metrics after optimization
    improvement_percentage = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'optimization_name': self.optimization_name,
            'optimization_description': self.optimization_description,
            'optimization_type': self.optimization_type,
            'database_name': self.database_name,
            'table_name': self.table_name,
            'query_text': self.query_text,
            'optimization_config': self.optimization_config,
            'optimization_sql': self.optimization_sql,
            'is_applied': self.is_applied,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'applied_by': self.applied_by,
            'before_performance': self.before_performance,
            'after_performance': self.after_performance,
            'improvement_percentage': self.improvement_percentage,
            'company_id': self.company_id
        })
        return data

class APIOptimization(BaseModel):
    """API optimization model"""
    __tablename__ = 'api_optimizations'
    
    # Optimization Information
    optimization_name = db.Column(db.String(200), nullable=False)
    optimization_description = db.Column(db.Text)
    optimization_type = db.Column(db.String(100), nullable=False)  # Caching, Rate Limiting, Compression, etc.
    
    # API Information
    api_endpoint = db.Column(db.String(500), nullable=False)
    api_method = db.Column(db.String(20), default='GET')  # GET, POST, PUT, DELETE, etc.
    api_version = db.Column(db.String(50), default='v1')
    
    # Optimization Configuration
    optimization_config = db.Column(db.JSON)  # Optimization-specific configuration
    cache_strategy = db.Column(db.String(100))
    rate_limit_config = db.Column(db.JSON)
    compression_config = db.Column(db.JSON)
    
    # Optimization Status
    is_active = db.Column(db.Boolean, default=True)
    is_applied = db.Column(db.Boolean, default=False)
    applied_at = db.Column(db.DateTime)
    applied_by = db.Column(db.Integer, db.ForeignKey('employees.id'))
    applier = relationship("Employee")
    
    # Performance Impact
    before_performance = db.Column(db.JSON)  # Performance metrics before optimization
    after_performance = db.Column(db.JSON)  # Performance metrics after optimization
    improvement_percentage = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'optimization_name': self.optimization_name,
            'optimization_description': self.optimization_description,
            'optimization_type': self.optimization_type,
            'api_endpoint': self.api_endpoint,
            'api_method': self.api_method,
            'api_version': self.api_version,
            'optimization_config': self.optimization_config,
            'cache_strategy': self.cache_strategy,
            'rate_limit_config': self.rate_limit_config,
            'compression_config': self.compression_config,
            'is_active': self.is_active,
            'is_applied': self.is_applied,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'applied_by': self.applied_by,
            'before_performance': self.before_performance,
            'after_performance': self.after_performance,
            'improvement_percentage': self.improvement_percentage,
            'company_id': self.company_id
        })
        return data

class PerformanceReport(BaseModel):
    """Performance report model"""
    __tablename__ = 'performance_reports'
    
    # Report Information
    report_name = db.Column(db.String(200), nullable=False)
    report_description = db.Column(db.Text)
    report_type = db.Column(db.String(100), nullable=False)  # Daily, Weekly, Monthly, Custom
    
    # Report Period
    report_period_start = db.Column(db.DateTime, nullable=False)
    report_period_end = db.Column(db.DateTime, nullable=False)
    
    # Report Status
    status = db.Column(db.String(50), default='Draft')  # Draft, Generated, Published
    generated_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    generator = relationship("Employee")
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Report Data
    report_data = db.Column(db.JSON)  # Report data
    performance_summary = db.Column(db.JSON)  # Performance summary
    recommendations = db.Column(db.JSON)  # Performance recommendations
    charts_data = db.Column(db.JSON)  # Charts and graphs data
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'report_name': self.report_name,
            'report_description': self.report_description,
            'report_type': self.report_type,
            'report_period_start': self.report_period_start.isoformat() if self.report_period_start else None,
            'report_period_end': self.report_period_end.isoformat() if self.report_period_end else None,
            'status': self.status,
            'generated_by': self.generated_by,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'report_data': self.report_data,
            'performance_summary': self.performance_summary,
            'recommendations': self.recommendations,
            'charts_data': self.charts_data,
            'company_id': self.company_id
        })
        return data
