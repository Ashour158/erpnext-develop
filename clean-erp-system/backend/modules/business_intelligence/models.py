# Business Intelligence Models
# Advanced analytics, reporting, and data visualization

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

class DashboardType(enum.Enum):
    EXECUTIVE = "Executive"
    OPERATIONAL = "Operational"
    FINANCIAL = "Financial"
    SALES = "Sales"
    HR = "HR"
    CUSTOM = "Custom"

class ReportType(enum.Enum):
    TABULAR = "Tabular"
    CHART = "Chart"
    PIVOT = "Pivot"
    MATRIX = "Matrix"
    SUMMARY = "Summary"

class ChartType(enum.Enum):
    BAR = "Bar"
    LINE = "Line"
    PIE = "Pie"
    AREA = "Area"
    SCATTER = "Scatter"
    HISTOGRAM = "Histogram"
    HEATMAP = "Heatmap"
    GAUGE = "Gauge"
    TREEMAP = "Treemap"

class DataSource(enum.Enum):
    DATABASE = "Database"
    API = "API"
    FILE = "File"
    MANUAL = "Manual"

class KPIStatus(enum.Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    AVERAGE = "Average"
    POOR = "Poor"
    CRITICAL = "Critical"

# Dashboard Models
class Dashboard(BaseModel):
    """Dashboard model"""
    __tablename__ = 'dashboards'
    
    # Dashboard Information
    dashboard_name = db.Column(db.String(200), nullable=False)
    dashboard_description = db.Column(db.Text)
    dashboard_type = db.Column(db.Enum(DashboardType), nullable=False)
    
    # Dashboard Configuration
    layout_config = db.Column(db.JSON)  # Dashboard layout configuration
    widget_config = db.Column(db.JSON)  # Widget configuration
    filters_config = db.Column(db.JSON)  # Global filters configuration
    
    # Dashboard Settings
    is_public = db.Column(db.Boolean, default=False)
    is_default = db.Column(db.Boolean, default=False)
    refresh_interval = db.Column(db.Integer, default=300)  # seconds
    
    # Access Control
    allowed_users = db.Column(db.JSON)  # List of user IDs with access
    allowed_roles = db.Column(db.JSON)  # List of role IDs with access
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    dashboard_widgets = relationship("DashboardWidget", back_populates="dashboard")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'dashboard_name': self.dashboard_name,
            'dashboard_description': self.dashboard_description,
            'dashboard_type': self.dashboard_type.value if self.dashboard_type else None,
            'layout_config': self.layout_config,
            'widget_config': self.widget_config,
            'filters_config': self.filters_config,
            'is_public': self.is_public,
            'is_default': self.is_default,
            'refresh_interval': self.refresh_interval,
            'allowed_users': self.allowed_users,
            'allowed_roles': self.allowed_roles,
            'company_id': self.company_id
        })
        return data

class DashboardWidget(BaseModel):
    """Dashboard widget model"""
    __tablename__ = 'dashboard_widgets'
    
    # Widget Information
    widget_name = db.Column(db.String(200), nullable=False)
    widget_type = db.Column(db.String(100), nullable=False)  # Chart, KPI, Table, etc.
    widget_title = db.Column(db.String(200))
    widget_description = db.Column(db.Text)
    
    # Dashboard Association
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboards.id'), nullable=False)
    dashboard = relationship("Dashboard", back_populates="dashboard_widgets")
    
    # Widget Configuration
    position_x = db.Column(db.Integer, default=0)
    position_y = db.Column(db.Integer, default=0)
    width = db.Column(db.Integer, default=4)
    height = db.Column(db.Integer, default=3)
    
    # Data Configuration
    data_source = db.Column(db.Enum(DataSource), default=DataSource.DATABASE)
    query_config = db.Column(db.JSON)  # Query configuration
    chart_config = db.Column(db.JSON)  # Chart configuration
    filter_config = db.Column(db.JSON)  # Filter configuration
    
    # Widget Settings
    is_visible = db.Column(db.Boolean, default=True)
    refresh_interval = db.Column(db.Integer, default=300)  # seconds
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'widget_name': self.widget_name,
            'widget_type': self.widget_type,
            'widget_title': self.widget_title,
            'widget_description': self.widget_description,
            'dashboard_id': self.dashboard_id,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'width': self.width,
            'height': self.height,
            'data_source': self.data_source.value if self.data_source else None,
            'query_config': self.query_config,
            'chart_config': self.chart_config,
            'filter_config': self.filter_config,
            'is_visible': self.is_visible,
            'refresh_interval': self.refresh_interval,
            'company_id': self.company_id
        })
        return data

# Report Models
class Report(BaseModel):
    """Report model"""
    __tablename__ = 'reports'
    
    # Report Information
    report_name = db.Column(db.String(200), nullable=False)
    report_description = db.Column(db.Text)
    report_type = db.Column(db.Enum(ReportType), nullable=False)
    
    # Report Configuration
    report_config = db.Column(db.JSON)  # Report configuration
    query_config = db.Column(db.JSON)  # Query configuration
    chart_config = db.Column(db.JSON)  # Chart configuration
    filter_config = db.Column(db.JSON)  # Filter configuration
    
    # Report Settings
    is_scheduled = db.Column(db.Boolean, default=False)
    schedule_config = db.Column(db.JSON)  # Schedule configuration
    is_public = db.Column(db.Boolean, default=False)
    
    # Access Control
    allowed_users = db.Column(db.JSON)  # List of user IDs with access
    allowed_roles = db.Column(db.JSON)  # List of role IDs with access
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    report_executions = relationship("ReportExecution", back_populates="report")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'report_name': self.report_name,
            'report_description': self.report_description,
            'report_type': self.report_type.value if self.report_type else None,
            'report_config': self.report_config,
            'query_config': self.query_config,
            'chart_config': self.chart_config,
            'filter_config': self.filter_config,
            'is_scheduled': self.is_scheduled,
            'schedule_config': self.schedule_config,
            'is_public': self.is_public,
            'allowed_users': self.allowed_users,
            'allowed_roles': self.allowed_roles,
            'company_id': self.company_id
        })
        return data

class ReportExecution(BaseModel):
    """Report execution model"""
    __tablename__ = 'report_executions'
    
    # Execution Information
    execution_date = db.Column(db.DateTime, default=datetime.utcnow)
    execution_status = db.Column(db.String(50), default='Running')  # Running, Completed, Failed
    execution_time = db.Column(db.Float, default=0.0)  # seconds
    
    # Report Association
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    report = relationship("Report", back_populates="report_executions")
    
    # Execution Details
    parameters = db.Column(db.JSON)  # Execution parameters
    filters = db.Column(db.JSON)  # Applied filters
    result_data = db.Column(db.JSON)  # Result data
    error_message = db.Column(db.Text)
    
    # Execution User
    executed_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    executed_by = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'execution_date': self.execution_date.isoformat() if self.execution_date else None,
            'execution_status': self.execution_status,
            'execution_time': self.execution_time,
            'report_id': self.report_id,
            'parameters': self.parameters,
            'filters': self.filters,
            'result_data': self.result_data,
            'error_message': self.error_message,
            'executed_by_id': self.executed_by_id,
            'company_id': self.company_id
        })
        return data

# KPI Models
class KPI(BaseModel):
    """KPI model"""
    __tablename__ = 'kpis'
    
    # KPI Information
    kpi_name = db.Column(db.String(200), nullable=False)
    kpi_description = db.Column(db.Text)
    kpi_category = db.Column(db.String(100))  # Financial, Operational, Customer, etc.
    
    # KPI Configuration
    calculation_method = db.Column(db.Text, nullable=False)
    data_sources = db.Column(db.JSON)  # List of data sources
    calculation_formula = db.Column(db.Text)
    
    # KPI Values
    current_value = db.Column(db.Float, default=0.0)
    target_value = db.Column(db.Float, default=0.0)
    previous_value = db.Column(db.Float, default=0.0)
    unit_of_measure = db.Column(db.String(50))
    
    # KPI Status
    status = db.Column(db.Enum(KPIStatus), default=KPIStatus.AVERAGE)
    trend_direction = db.Column(db.String(20))  # Up, Down, Stable
    trend_percentage = db.Column(db.Float, default=0.0)
    
    # KPI Settings
    is_active = db.Column(db.Boolean, default=True)
    update_frequency = db.Column(db.String(50), default='Daily')  # Daily, Weekly, Monthly
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    kpi_history = relationship("KPIHistory", back_populates="kpi")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'kpi_name': self.kpi_name,
            'kpi_description': self.kpi_description,
            'kpi_category': self.kpi_category,
            'calculation_method': self.calculation_method,
            'data_sources': self.data_sources,
            'calculation_formula': self.calculation_formula,
            'current_value': self.current_value,
            'target_value': self.target_value,
            'previous_value': self.previous_value,
            'unit_of_measure': self.unit_of_measure,
            'status': self.status.value if self.status else None,
            'trend_direction': self.trend_direction,
            'trend_percentage': self.trend_percentage,
            'is_active': self.is_active,
            'update_frequency': self.update_frequency,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'company_id': self.company_id
        })
        return data

class KPIHistory(BaseModel):
    """KPI history model"""
    __tablename__ = 'kpi_history'
    
    # KPI Association
    kpi_id = db.Column(db.Integer, db.ForeignKey('kpis.id'), nullable=False)
    kpi = relationship("KPI", back_populates="kpi_history")
    
    # History Data
    recorded_date = db.Column(db.Date, default=date.today)
    recorded_value = db.Column(db.Float, default=0.0)
    target_value = db.Column(db.Float, default=0.0)
    variance = db.Column(db.Float, default=0.0)
    variance_percentage = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'kpi_id': self.kpi_id,
            'recorded_date': self.recorded_date.isoformat() if self.recorded_date else None,
            'recorded_value': self.recorded_value,
            'target_value': self.target_value,
            'variance': self.variance,
            'variance_percentage': self.variance_percentage,
            'company_id': self.company_id
        })
        return data

# Data Source Models
class DataSource(BaseModel):
    """Data source model"""
    __tablename__ = 'data_sources'
    
    # Data Source Information
    source_name = db.Column(db.String(200), nullable=False)
    source_description = db.Column(db.Text)
    source_type = db.Column(db.Enum(DataSource), nullable=False)
    
    # Connection Configuration
    connection_config = db.Column(db.JSON)  # Connection configuration
    authentication_config = db.Column(db.JSON)  # Authentication configuration
    
    # Data Source Settings
    is_active = db.Column(db.Boolean, default=True)
    refresh_interval = db.Column(db.Integer, default=3600)  # seconds
    last_sync = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'source_name': self.source_name,
            'source_description': self.source_description,
            'source_type': self.source_type.value if self.source_type else None,
            'connection_config': self.connection_config,
            'authentication_config': self.authentication_config,
            'is_active': self.is_active,
            'refresh_interval': self.refresh_interval,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'company_id': self.company_id
        })
        return data

# Analytics Models
class AnalyticsQuery(BaseModel):
    """Analytics query model"""
    __tablename__ = 'analytics_queries'
    
    # Query Information
    query_name = db.Column(db.String(200), nullable=False)
    query_description = db.Column(db.Text)
    query_sql = db.Column(db.Text, nullable=False)
    
    # Query Configuration
    parameters = db.Column(db.JSON)  # Query parameters
    filters = db.Column(db.JSON)  # Query filters
    grouping = db.Column(db.JSON)  # Grouping configuration
    sorting = db.Column(db.JSON)  # Sorting configuration
    
    # Query Settings
    is_public = db.Column(db.Boolean, default=False)
    execution_timeout = db.Column(db.Integer, default=300)  # seconds
    
    # Access Control
    allowed_users = db.Column(db.JSON)  # List of user IDs with access
    allowed_roles = db.Column(db.JSON)  # List of role IDs with access
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'query_name': self.query_name,
            'query_description': self.query_description,
            'query_sql': self.query_sql,
            'parameters': self.parameters,
            'filters': self.filters,
            'grouping': self.grouping,
            'sorting': self.sorting,
            'is_public': self.is_public,
            'execution_timeout': self.execution_timeout,
            'allowed_users': self.allowed_users,
            'allowed_roles': self.allowed_roles,
            'company_id': self.company_id
        })
        return data

class DataVisualization(BaseModel):
    """Data visualization model"""
    __tablename__ = 'data_visualizations'
    
    # Visualization Information
    visualization_name = db.Column(db.String(200), nullable=False)
    visualization_description = db.Column(db.Text)
    chart_type = db.Column(db.Enum(ChartType), nullable=False)
    
    # Data Configuration
    data_source_id = db.Column(db.Integer, db.ForeignKey('data_sources.id'))
    data_source = relationship("DataSource")
    query_id = db.Column(db.Integer, db.ForeignKey('analytics_queries.id'))
    query = relationship("AnalyticsQuery")
    
    # Visualization Configuration
    chart_config = db.Column(db.JSON)  # Chart configuration
    color_scheme = db.Column(db.String(100), default='default')
    chart_options = db.Column(db.JSON)  # Chart options
    
    # Visualization Settings
    is_public = db.Column(db.Boolean, default=False)
    is_interactive = db.Column(db.Boolean, default=True)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'visualization_name': self.visualization_name,
            'visualization_description': self.visualization_description,
            'chart_type': self.chart_type.value if self.chart_type else None,
            'data_source_id': self.data_source_id,
            'query_id': self.query_id,
            'chart_config': self.chart_config,
            'color_scheme': self.color_scheme,
            'chart_options': self.chart_options,
            'is_public': self.is_public,
            'is_interactive': self.is_interactive,
            'company_id': self.company_id
        })
        return data
