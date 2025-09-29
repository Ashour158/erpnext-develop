# Advanced CRM Analytics
# Comprehensive analytics to surpass Zoho CRM and Salesforce

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class AnalyticsType(enum.Enum):
    SALES_PERFORMANCE = "sales_performance"
    CUSTOMER_ANALYTICS = "customer_analytics"
    LEAD_ANALYTICS = "lead_analytics"
    OPPORTUNITY_ANALYTICS = "opportunity_analytics"
    REVENUE_ANALYTICS = "revenue_analytics"
    CONVERSION_ANALYTICS = "conversion_analytics"
    RETENTION_ANALYTICS = "retention_analytics"
    PREDICTIVE_ANALYTICS = "predictive_analytics"

class MetricType(enum.Enum):
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    TREND = "trend"
    FORECAST = "forecast"

class TimePeriod(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

# Advanced Sales Performance Analytics
class SalesPerformanceAnalytics(Base):
    __tablename__ = 'sales_performance_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    time_period = Column(Enum(TimePeriod), nullable=False)
    
    # Sales Metrics
    total_deals = Column(Integer, default=0)
    won_deals = Column(Integer, default=0)
    lost_deals = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)  # Percentage
    
    # Revenue Metrics
    total_revenue = Column(Float, default=0.0)
    average_deal_size = Column(Float, default=0.0)
    revenue_target = Column(Float, default=0.0)
    revenue_achievement = Column(Float, default=0.0)  # Percentage
    
    # Activity Metrics
    calls_made = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    meetings_scheduled = Column(Integer, default=0)
    proposals_sent = Column(Integer, default=0)
    
    # Performance Scores
    activity_score = Column(Float, default=0.0)  # 0-100
    efficiency_score = Column(Float, default=0.0)  # 0-100
    quality_score = Column(Float, default=0.0)  # 0-100
    overall_score = Column(Float, default=0.0)  # 0-100
    
    # Trends
    revenue_trend = Column(String(20))  # increasing, stable, decreasing
    activity_trend = Column(String(20))  # increasing, stable, decreasing
    performance_trend = Column(String(20))  # improving, stable, declining
    
    # Rankings
    team_rank = Column(Integer)  # Rank within team
    company_rank = Column(Integer)  # Rank within company
    percentile = Column(Float)  # Performance percentile
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")

# Customer Analytics
class CustomerAnalytics(Base):
    __tablename__ = 'customer_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Customer Metrics
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    average_order_value = Column(Float, default=0.0)
    order_frequency = Column(Float, default=0.0)  # Orders per month
    
    # Engagement Metrics
    email_opens = Column(Integer, default=0)
    email_clicks = Column(Integer, default=0)
    website_visits = Column(Integer, default=0)
    support_tickets = Column(Integer, default=0)
    
    # Customer Health
    health_score = Column(Float, default=0.0)  # 0-100
    engagement_score = Column(Float, default=0.0)  # 0-100
    satisfaction_score = Column(Float, default=0.0)  # 0-100
    loyalty_score = Column(Float, default=0.0)  # 0-100
    
    # Behavioral Analysis
    preferred_products = Column(JSON)  # Most purchased products
    purchase_patterns = Column(JSON)  # Purchase behavior patterns
    seasonal_behavior = Column(JSON)  # Seasonal purchase patterns
    price_sensitivity = Column(Float)  # Price sensitivity score
    
    # Lifetime Value
    customer_lifetime_value = Column(Float, default=0.0)
    predicted_clv = Column(Float, default=0.0)
    clv_trend = Column(String(20))  # increasing, stable, decreasing
    
    # Churn Risk
    churn_probability = Column(Float, default=0.0)  # 0-100%
    churn_risk_level = Column(String(20))  # Low, Medium, High, Critical
    churn_factors = Column(JSON)  # Factors contributing to churn risk
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    customer = relationship("Customer")

# Lead Analytics
class LeadAnalytics(Base):
    __tablename__ = 'lead_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)
    
    # Lead Metrics
    lead_score = Column(Float, default=0.0)  # 0-100
    conversion_probability = Column(Float, default=0.0)  # 0-100%
    expected_value = Column(Float, default=0.0)
    time_to_convert = Column(Integer)  # Days to convert
    
    # Source Analysis
    source_effectiveness = Column(Float, default=0.0)  # Source conversion rate
    source_quality_score = Column(Float, default=0.0)  # 0-100
    source_cost = Column(Float, default=0.0)
    source_roi = Column(Float, default=0.0)
    
    # Behavioral Analysis
    engagement_level = Column(String(20))  # High, Medium, Low
    response_time = Column(Integer)  # Hours to first response
    touchpoint_count = Column(Integer, default=0)
    last_activity = Column(DateTime)
    
    # Qualification Metrics
    qualification_score = Column(Float, default=0.0)  # 0-100
    qualification_factors = Column(JSON)  # Factors affecting qualification
    qualification_stage = Column(String(50))  # Current qualification stage
    
    # Conversion Analysis
    conversion_stage = Column(String(50))  # Current conversion stage
    stage_probability = Column(Float, default=0.0)  # Probability of stage completion
    next_action = Column(String(255))  # Recommended next action
    action_priority = Column(String(20))  # High, Medium, Low
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    lead = relationship("Lead")

# Opportunity Analytics
class OpportunityAnalytics(Base):
    __tablename__ = 'opportunity_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'), nullable=False)
    
    # Opportunity Metrics
    win_probability = Column(Float, default=0.0)  # 0-100%
    expected_value = Column(Float, default=0.0)
    actual_value = Column(Float, default=0.0)
    value_variance = Column(Float, default=0.0)  # Difference between expected and actual
    
    # Stage Analysis
    current_stage = Column(String(50))
    stage_duration = Column(Integer)  # Days in current stage
    stage_probability = Column(Float, default=0.0)  # Probability of stage completion
    next_stage = Column(String(50))
    stage_progression = Column(JSON)  # Stage progression history
    
    # Sales Cycle Analysis
    sales_cycle_length = Column(Integer)  # Days in sales cycle
    cycle_velocity = Column(Float)  # Speed of progression
    cycle_efficiency = Column(Float)  # 0-100 efficiency score
    cycle_bottlenecks = Column(JSON)  # Identified bottlenecks
    
    # Competitive Analysis
    competitor_count = Column(Integer, default=0)
    competitive_position = Column(String(20))  # Leading, Competitive, Losing
    competitive_advantages = Column(JSON)  # Our competitive advantages
    competitive_threats = Column(JSON)  # Competitive threats
    
    # Stakeholder Analysis
    decision_makers = Column(Integer, default=0)
    influencers = Column(Integer, default=0)
    champion_identified = Column(Boolean, default=False)
    stakeholder_engagement = Column(Float, default=0.0)  # 0-100
    
    # Risk Analysis
    risk_score = Column(Float, default=0.0)  # 0-100
    risk_factors = Column(JSON)  # Risk factors
    mitigation_actions = Column(JSON)  # Risk mitigation actions
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    opportunity = relationship("Opportunity")

# Revenue Analytics
class RevenueAnalytics(Base):
    __tablename__ = 'revenue_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    time_period = Column(Enum(TimePeriod), nullable=False)
    
    # Revenue Metrics
    total_revenue = Column(Float, default=0.0)
    recurring_revenue = Column(Float, default=0.0)
    one_time_revenue = Column(Float, default=0.0)
    revenue_growth = Column(Float, default=0.0)  # Percentage growth
    
    # Revenue Sources
    new_customer_revenue = Column(Float, default=0.0)
    existing_customer_revenue = Column(Float, default=0.0)
    upsell_revenue = Column(Float, default=0.0)
    cross_sell_revenue = Column(Float, default=0.0)
    
    # Revenue Trends
    revenue_trend = Column(String(20))  # increasing, stable, decreasing
    growth_rate = Column(Float, default=0.0)  # Monthly growth rate
    seasonal_adjustment = Column(Float, default=0.0)  # Seasonal adjustment factor
    
    # Revenue Forecasting
    forecasted_revenue = Column(Float, default=0.0)
    forecast_confidence = Column(Float, default=0.0)  # 0-100%
    forecast_accuracy = Column(Float, default=0.0)  # Historical accuracy
    
    # Revenue Distribution
    revenue_by_product = Column(JSON)  # Revenue by product
    revenue_by_region = Column(JSON)  # Revenue by region
    revenue_by_customer_segment = Column(JSON)  # Revenue by customer segment
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))

# Conversion Analytics
class ConversionAnalytics(Base):
    __tablename__ = 'conversion_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    time_period = Column(Enum(TimePeriod), nullable=False)
    
    # Conversion Funnel
    total_leads = Column(Integer, default=0)
    qualified_leads = Column(Integer, default=0)
    opportunities = Column(Integer, default=0)
    closed_won = Column(Integer, default=0)
    
    # Conversion Rates
    lead_to_qualified_rate = Column(Float, default=0.0)  # Percentage
    qualified_to_opportunity_rate = Column(Float, default=0.0)  # Percentage
    opportunity_to_close_rate = Column(Float, default=0.0)  # Percentage
    overall_conversion_rate = Column(Float, default=0.0)  # Percentage
    
    # Conversion Time
    average_lead_to_close_time = Column(Integer)  # Days
    average_opportunity_to_close_time = Column(Integer)  # Days
    conversion_velocity = Column(Float)  # Speed of conversion
    
    # Conversion Factors
    top_conversion_sources = Column(JSON)  # Best performing sources
    conversion_barriers = Column(JSON)  # Common barriers to conversion
    conversion_optimization_opportunities = Column(JSON)  # Optimization opportunities
    
    # A/B Testing Results
    ab_test_results = Column(JSON)  # A/B test results
    winning_variants = Column(JSON)  # Winning test variants
    test_impact = Column(Float, default=0.0)  # Impact of tests on conversion
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))

# Retention Analytics
class RetentionAnalytics(Base):
    __tablename__ = 'retention_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    time_period = Column(Enum(TimePeriod), nullable=False)
    
    # Retention Metrics
    customer_retention_rate = Column(Float, default=0.0)  # Percentage
    revenue_retention_rate = Column(Float, default=0.0)  # Percentage
    net_revenue_retention = Column(Float, default=0.0)  # Percentage
    gross_revenue_retention = Column(Float, default=0.0)  # Percentage
    
    # Churn Analysis
    customer_churn_rate = Column(Float, default=0.0)  # Percentage
    revenue_churn_rate = Column(Float, default=0.0)  # Percentage
    churned_customers = Column(Integer, default=0)
    churned_revenue = Column(Float, default=0.0)
    
    # Cohort Analysis
    cohort_data = Column(JSON)  # Cohort analysis data
    cohort_retention_rates = Column(JSON)  # Retention rates by cohort
    cohort_revenue_rates = Column(JSON)  # Revenue rates by cohort
    
    # Retention Factors
    retention_drivers = Column(JSON)  # Factors driving retention
    churn_drivers = Column(JSON)  # Factors driving churn
    retention_strategies = Column(JSON)  # Effective retention strategies
    
    # Customer Lifetime Value
    average_customer_lifetime = Column(Float, default=0.0)  # Months
    average_customer_lifetime_value = Column(Float, default=0.0)
    clv_trend = Column(String(20))  # increasing, stable, decreasing
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))

# Predictive Analytics
class PredictiveAnalytics(Base):
    __tablename__ = 'predictive_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    analytics_type = Column(Enum(AnalyticsType), nullable=False)
    prediction_horizon = Column(Integer, nullable=False)  # Days ahead
    confidence_level = Column(Float, nullable=False)  # 0-100%
    
    # Predictions
    predicted_value = Column(Float, nullable=False)
    prediction_range = Column(JSON)  # Min and max predictions
    prediction_factors = Column(JSON)  # Factors influencing prediction
    
    # Model Information
    model_name = Column(String(255), nullable=False)
    model_version = Column(String(50), nullable=False)
    model_accuracy = Column(Float, default=0.0)  # 0-100%
    
    # Historical Performance
    historical_accuracy = Column(Float, default=0.0)  # 0-100%
    prediction_errors = Column(JSON)  # Historical prediction errors
    model_performance = Column(JSON)  # Model performance metrics
    
    # Business Impact
    business_impact = Column(Float, default=0.0)  # Expected business impact
    risk_level = Column(String(20))  # Low, Medium, High, Critical
    action_required = Column(Boolean, default=False)
    
    # Metadata
    predicted_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))

# Analytics Dashboard
class AnalyticsDashboard(Base):
    __tablename__ = 'analytics_dashboards'
    
    id = Column(Integer, primary_key=True, index=True)
    dashboard_name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Dashboard Configuration
    dashboard_config = Column(JSON, nullable=False)  # Dashboard layout and widgets
    widget_configs = Column(JSON)  # Individual widget configurations
    filters = Column(JSON)  # Dashboard filters
    
    # Dashboard Settings
    refresh_interval = Column(Integer, default=300)  # Seconds
    auto_refresh = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    
    # Dashboard Metrics
    view_count = Column(Integer, default=0)
    last_viewed = Column(DateTime)
    favorite_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")

# Analytics Reports
class AnalyticsReport(Base):
    __tablename__ = 'analytics_reports'
    
    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(255), nullable=False)
    report_type = Column(Enum(AnalyticsType), nullable=False)
    
    # Report Configuration
    report_config = Column(JSON, nullable=False)  # Report configuration
    filters = Column(JSON)  # Report filters
    grouping = Column(JSON)  # Report grouping
    sorting = Column(JSON)  # Report sorting
    
    # Report Data
    report_data = Column(JSON)  # Report data
    summary_metrics = Column(JSON)  # Summary metrics
    insights = Column(JSON)  # Key insights
    recommendations = Column(JSON)  # Recommendations
    
    # Report Settings
    is_scheduled = Column(Boolean, default=False)
    schedule_frequency = Column(String(20))  # daily, weekly, monthly
    next_run = Column(DateTime)
    recipients = Column(JSON)  # Report recipients
    
    # Report Status
    status = Column(String(20), default='active')  # active, paused, archived
    last_generated = Column(DateTime)
    generation_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Analytics Alerts
class AnalyticsAlert(Base):
    __tablename__ = 'analytics_alerts'
    
    id = Column(Integer, primary_key=True, index=True)
    alert_name = Column(String(255), nullable=False)
    alert_type = Column(Enum(AnalyticsType), nullable=False)
    
    # Alert Configuration
    alert_conditions = Column(JSON, nullable=False)  # Alert conditions
    threshold_value = Column(Float, nullable=False)
    comparison_operator = Column(String(10))  # >, <, >=, <=, ==, !=
    
    # Alert Settings
    is_active = Column(Boolean, default=True)
    alert_frequency = Column(String(20), default='immediate')  # immediate, daily, weekly
    recipients = Column(JSON)  # Alert recipients
    
    # Alert Status
    last_triggered = Column(DateTime)
    trigger_count = Column(Integer, default=0)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, ForeignKey('users.id'))
    acknowledged_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    acknowledger = relationship("User", foreign_keys=[acknowledged_by])
