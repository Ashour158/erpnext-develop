# Analytics & Reporting Models
# Models for advanced analytics and reporting system with productivity insights, attendance analytics, and performance metrics

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime, time, date, timedelta
import enum

class ReportType(enum.Enum):
    PRODUCTIVITY = "Productivity"
    ATTENDANCE = "Attendance"
    LOCATION = "Location"
    MEETING = "Meeting"
    PERFORMANCE = "Performance"
    FINANCIAL = "Financial"
    CUSTOM = "Custom"

class ReportFrequency(enum.Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"
    ON_DEMAND = "On Demand"

class MetricType(enum.Enum):
    COUNT = "Count"
    PERCENTAGE = "Percentage"
    AVERAGE = "Average"
    SUM = "Sum"
    RATIO = "Ratio"
    TREND = "Trend"

class DashboardType(enum.Enum):
    EXECUTIVE = "Executive"
    MANAGER = "Manager"
    EMPLOYEE = "Employee"
    DEPARTMENT = "Department"
    PROJECT = "Project"
    CUSTOM = "Custom"

class ProductivityAnalytics(BaseModel):
    """Productivity analytics model"""
    __tablename__ = 'productivity_analytics'
    
    # Analytics Information
    analytics_date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Productivity Metrics
    total_work_hours = db.Column(db.Float, default=0.0)
    productive_hours = db.Column(db.Float, default=0.0)
    productivity_score = db.Column(db.Float, default=0.0)  # 0-100
    efficiency_rating = db.Column(db.Float, default=0.0)  # 0-5
    
    # Task Metrics
    tasks_completed = db.Column(db.Integer, default=0)
    tasks_pending = db.Column(db.Integer, default=0)
    tasks_overdue = db.Column(db.Integer, default=0)
    task_completion_rate = db.Column(db.Float, default=0.0)
    
    # Meeting Metrics
    meetings_attended = db.Column(db.Integer, default=0)
    meeting_hours = db.Column(db.Float, default=0.0)
    meeting_effectiveness = db.Column(db.Float, default=0.0)
    
    # Location Metrics
    time_at_office = db.Column(db.Float, default=0.0)
    time_remote = db.Column(db.Float, default=0.0)
    travel_time = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'analytics_date': self.analytics_date.isoformat() if self.analytics_date else None,
            'user_id': self.user_id,
            'total_work_hours': self.total_work_hours,
            'productive_hours': self.productive_hours,
            'productivity_score': self.productivity_score,
            'efficiency_rating': self.efficiency_rating,
            'tasks_completed': self.tasks_completed,
            'tasks_pending': self.tasks_pending,
            'tasks_overdue': self.tasks_overdue,
            'task_completion_rate': self.task_completion_rate,
            'meetings_attended': self.meetings_attended,
            'meeting_hours': self.meeting_hours,
            'meeting_effectiveness': self.meeting_effectiveness,
            'time_at_office': self.time_at_office,
            'time_remote': self.time_remote,
            'travel_time': self.travel_time,
            'company_id': self.company_id
        })
        return data

class AttendanceAnalytics(BaseModel):
    """Attendance analytics model"""
    __tablename__ = 'attendance_analytics'
    
    # Analytics Information
    analytics_date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Attendance Metrics
    total_days = db.Column(db.Integer, default=0)
    present_days = db.Column(db.Integer, default=0)
    absent_days = db.Column(db.Integer, default=0)
    late_days = db.Column(db.Integer, default=0)
    early_leave_days = db.Column(db.Integer, default=0)
    attendance_rate = db.Column(db.Float, default=0.0)
    
    # Time Metrics
    total_work_hours = db.Column(db.Float, default=0.0)
    overtime_hours = db.Column(db.Float, default=0.0)
    break_hours = db.Column(db.Float, default=0.0)
    average_daily_hours = db.Column(db.Float, default=0.0)
    
    # Punctuality Metrics
    average_check_in_time = db.Column(db.Time)
    average_check_out_time = db.Column(db.Time)
    punctuality_score = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'analytics_date': self.analytics_date.isoformat() if self.analytics_date else None,
            'user_id': self.user_id,
            'total_days': self.total_days,
            'present_days': self.present_days,
            'absent_days': self.absent_days,
            'late_days': self.late_days,
            'early_leave_days': self.early_leave_days,
            'attendance_rate': self.attendance_rate,
            'total_work_hours': self.total_work_hours,
            'overtime_hours': self.overtime_hours,
            'break_hours': self.break_hours,
            'average_daily_hours': self.average_daily_hours,
            'average_check_in_time': self.average_check_in_time.isoformat() if self.average_check_in_time else None,
            'average_check_out_time': self.average_check_out_time.isoformat() if self.average_check_out_time else None,
            'punctuality_score': self.punctuality_score,
            'company_id': self.company_id
        })
        return data

class LocationAnalytics(BaseModel):
    """Location analytics model"""
    __tablename__ = 'location_analytics'
    
    # Analytics Information
    analytics_date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Location Metrics
    total_locations = db.Column(db.Integer, default=0)
    unique_locations = db.Column(db.Integer, default=0)
    most_visited_location = db.Column(db.String(200))
    time_at_most_visited = db.Column(db.Float, default=0.0)
    
    # Travel Metrics
    total_distance_traveled = db.Column(db.Float, default=0.0)  # meters
    total_travel_time = db.Column(db.Float, default=0.0)  # hours
    average_speed = db.Column(db.Float, default=0.0)  # km/h
    fuel_consumption = db.Column(db.Float, default=0.0)  # liters
    
    # Location Patterns
    location_heatmap = db.Column(db.JSON)  # Heat map data
    location_timeline = db.Column(db.JSON)  # Timeline data
    movement_patterns = db.Column(db.JSON)  # Movement pattern analysis
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'analytics_date': self.analytics_date.isoformat() if self.analytics_date else None,
            'user_id': self.user_id,
            'total_locations': self.total_locations,
            'unique_locations': self.unique_locations,
            'most_visited_location': self.most_visited_location,
            'time_at_most_visited': self.time_at_most_visited,
            'total_distance_traveled': self.total_distance_traveled,
            'total_travel_time': self.total_travel_time,
            'average_speed': self.average_speed,
            'fuel_consumption': self.fuel_consumption,
            'location_heatmap': self.location_heatmap,
            'location_timeline': self.location_timeline,
            'movement_patterns': self.movement_patterns,
            'company_id': self.company_id
        })
        return data

class PerformanceMetric(BaseModel):
    """Performance metric model"""
    __tablename__ = 'performance_metrics'
    
    # Metric Information
    metric_name = db.Column(db.String(200), nullable=False)
    metric_description = db.Column(db.Text)
    metric_type = db.Column(db.Enum(MetricType), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    target_value = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(50), default='')
    
    # Time Period
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Department Information
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    department = relationship("Department")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'metric_name': self.metric_name,
            'metric_description': self.metric_description,
            'metric_type': self.metric_type.value if self.metric_type else None,
            'metric_value': self.metric_value,
            'target_value': self.target_value,
            'unit': self.unit,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'user_id': self.user_id,
            'department_id': self.department_id,
            'company_id': self.company_id
        })
        return data

class Report(BaseModel):
    """Report model"""
    __tablename__ = 'reports'
    
    # Report Information
    report_name = db.Column(db.String(200), nullable=False)
    report_description = db.Column(db.Text)
    report_type = db.Column(db.Enum(ReportType), nullable=False)
    report_frequency = db.Column(db.Enum(ReportFrequency), default=ReportFrequency.ON_DEMAND)
    
    # Report Configuration
    report_config = db.Column(db.JSON)  # Report configuration
    filters = db.Column(db.JSON)  # Report filters
    columns = db.Column(db.JSON)  # Report columns
    sorting = db.Column(db.JSON)  # Report sorting
    
    # Report Data
    report_data = db.Column(db.JSON)  # Report data
    last_generated = db.Column(db.DateTime)
    generation_status = db.Column(db.String(50), default='Pending')
    
    # Access Control
    is_public = db.Column(db.Boolean, default=False)
    allowed_users = db.Column(db.JSON)  # List of user IDs
    allowed_roles = db.Column(db.JSON)  # List of role IDs
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'report_name': self.report_name,
            'report_description': self.report_description,
            'report_type': self.report_type.value if self.report_type else None,
            'report_frequency': self.report_frequency.value if self.report_frequency else None,
            'report_config': self.report_config,
            'filters': self.filters,
            'columns': self.columns,
            'sorting': self.sorting,
            'report_data': self.report_data,
            'last_generated': self.last_generated.isoformat() if self.last_generated else None,
            'generation_status': self.generation_status,
            'is_public': self.is_public,
            'allowed_users': self.allowed_users,
            'allowed_roles': self.allowed_roles,
            'company_id': self.company_id
        })
        return data

class Dashboard(BaseModel):
    """Dashboard model"""
    __tablename__ = 'dashboards'
    
    # Dashboard Information
    dashboard_name = db.Column(db.String(200), nullable=False)
    dashboard_description = db.Column(db.Text)
    dashboard_type = db.Column(db.Enum(DashboardType), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    
    # Dashboard Configuration
    dashboard_config = db.Column(db.JSON)  # Dashboard configuration
    widgets = db.Column(db.JSON)  # Dashboard widgets
    layout = db.Column(db.JSON)  # Dashboard layout
    
    # Access Control
    is_public = db.Column(db.Boolean, default=False)
    allowed_users = db.Column(db.JSON)  # List of user IDs
    allowed_roles = db.Column(db.JSON)  # List of role IDs
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'dashboard_name': self.dashboard_name,
            'dashboard_description': self.dashboard_description,
            'dashboard_type': self.dashboard_type.value if self.dashboard_type else None,
            'is_default': self.is_default,
            'dashboard_config': self.dashboard_config,
            'widgets': self.widgets,
            'layout': self.layout,
            'is_public': self.is_public,
            'allowed_users': self.allowed_users,
            'allowed_roles': self.allowed_roles,
            'company_id': self.company_id
        })
        return data

class KPI(BaseModel):
    """KPI model"""
    __tablename__ = 'kpis'
    
    # KPI Information
    kpi_name = db.Column(db.String(200), nullable=False)
    kpi_description = db.Column(db.Text)
    kpi_category = db.Column(db.String(100), nullable=False)
    kpi_type = db.Column(db.Enum(MetricType), nullable=False)
    
    # KPI Configuration
    calculation_formula = db.Column(db.Text)
    data_sources = db.Column(db.JSON)  # List of data sources
    update_frequency = db.Column(db.Enum(ReportFrequency), default=ReportFrequency.DAILY)
    
    # KPI Values
    current_value = db.Column(db.Float, default=0.0)
    target_value = db.Column(db.Float, default=0.0)
    previous_value = db.Column(db.Float, default=0.0)
    trend = db.Column(db.String(20), default='Stable')  # Up, Down, Stable
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'kpi_name': self.kpi_name,
            'kpi_description': self.kpi_description,
            'kpi_category': self.kpi_category,
            'kpi_type': self.kpi_type.value if self.kpi_type else None,
            'calculation_formula': self.calculation_formula,
            'data_sources': self.data_sources,
            'update_frequency': self.update_frequency.value if self.update_frequency else None,
            'current_value': self.current_value,
            'target_value': self.target_value,
            'previous_value': self.previous_value,
            'trend': self.trend,
            'company_id': self.company_id
        })
        return data

class DataVisualization(BaseModel):
    """Data visualization model"""
    __tablename__ = 'data_visualizations'
    
    # Visualization Information
    visualization_name = db.Column(db.String(200), nullable=False)
    visualization_description = db.Column(db.Text)
    visualization_type = db.Column(db.String(100), nullable=False)  # Chart, Graph, Table, etc.
    
    # Visualization Configuration
    chart_config = db.Column(db.JSON)  # Chart configuration
    data_query = db.Column(db.Text)  # Data query
    filters = db.Column(db.JSON)  # Visualization filters
    
    # Visualization Data
    visualization_data = db.Column(db.JSON)  # Visualization data
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Access Control
    is_public = db.Column(db.Boolean, default=False)
    allowed_users = db.Column(db.JSON)  # List of user IDs
    allowed_roles = db.Column(db.JSON)  # List of role IDs
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'visualization_name': self.visualization_name,
            'visualization_description': self.visualization_description,
            'visualization_type': self.visualization_type,
            'chart_config': self.chart_config,
            'data_query': self.data_query,
            'filters': self.filters,
            'visualization_data': self.visualization_data,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'is_public': self.is_public,
            'allowed_users': self.allowed_users,
            'allowed_roles': self.allowed_roles,
            'company_id': self.company_id
        })
        return data
