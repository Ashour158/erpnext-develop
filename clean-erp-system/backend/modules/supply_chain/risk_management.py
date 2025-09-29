# Risk Management for Supply Chain
# Comprehensive risk assessment and mitigation

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum, Date
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class RiskType(enum.Enum):
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    REGULATORY = "regulatory"
    SUPPLIER = "supplier"
    DEMAND = "demand"
    SUPPLY = "supply"
    LOGISTICS = "logistics"
    QUALITY = "quality"
    CYBER = "cyber"
    ENVIRONMENTAL = "environmental"
    GEOPOLITICAL = "geopolitical"
    MARKET = "market"
    CURRENCY = "currency"
    CREDIT = "credit"
    REPUTATIONAL = "reputational"

class RiskLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskStatus(enum.Enum):
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    MITIGATED = "mitigated"
    MONITORED = "monitored"
    CLOSED = "closed"
    ESCALATED = "escalated"

class MitigationStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Risk Assessment
class RiskAssessment(Base):
    __tablename__ = 'risk_assessments'
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Assessment details
    assessment_name = Column(String(255), nullable=False)
    assessment_type = Column(String(50), nullable=False)  # comprehensive, specific, periodic
    assessment_date = Column(DateTime, default=datetime.utcnow)
    assessment_period_start = Column(DateTime, nullable=False)
    assessment_period_end = Column(DateTime, nullable=False)
    
    # Scope
    scope_items = Column(JSON)  # Items included in assessment
    scope_suppliers = Column(JSON)  # Suppliers included in assessment
    scope_facilities = Column(JSON)  # Facilities included in assessment
    scope_regions = Column(JSON)  # Geographic regions included
    
    # Assessment results
    overall_risk_score = Column(Float, nullable=False)  # 0-100 overall risk score
    risk_level = Column(Enum(RiskLevel), nullable=False)
    risk_factors = Column(JSON)  # Identified risk factors
    risk_impacts = Column(JSON)  # Potential impacts
    risk_probabilities = Column(JSON)  # Risk probabilities
    
    # Assessment methodology
    methodology = Column(String(100))  # Assessment methodology used
    assessment_criteria = Column(JSON)  # Assessment criteria
    weighting_factors = Column(JSON)  # Risk weighting factors
    
    # Status
    status = Column(Enum(RiskStatus), default=RiskStatus.IDENTIFIED)
    is_active = Column(Boolean, default=True)
    next_review_date = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assessed_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    assessor = relationship("User")
    risks = relationship("Risk", back_populates="assessment", cascade="all, delete-orphan")
    mitigations = relationship("RiskMitigation", back_populates="assessment", cascade="all, delete-orphan")

# Individual Risks
class Risk(Base):
    __tablename__ = 'risks'
    
    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(String(100), unique=True, nullable=False, index=True)
    assessment_id = Column(Integer, ForeignKey('risk_assessments.id'), nullable=False)
    
    # Risk details
    risk_name = Column(String(255), nullable=False)
    risk_type = Column(Enum(RiskType), nullable=False)
    risk_description = Column(Text, nullable=False)
    risk_category = Column(String(50))  # primary, secondary, tertiary
    
    # Risk scoring
    probability_score = Column(Float, nullable=False)  # 0-100 probability score
    impact_score = Column(Float, nullable=False)  # 0-100 impact score
    risk_score = Column(Float, nullable=False)  # Calculated risk score
    risk_level = Column(Enum(RiskLevel), nullable=False)
    
    # Risk details
    risk_owner = Column(String(255))  # Risk owner
    risk_source = Column(String(255))  # Source of risk
    risk_drivers = Column(JSON)  # Risk drivers
    risk_indicators = Column(JSON)  # Risk indicators
    
    # Impact assessment
    financial_impact = Column(Float)  # Financial impact
    operational_impact = Column(String(50))  # Operational impact level
    reputational_impact = Column(String(50))  # Reputational impact level
    timeline_impact = Column(String(50))  # Timeline impact
    
    # Risk status
    status = Column(Enum(RiskStatus), default=RiskStatus.IDENTIFIED)
    is_active = Column(Boolean, default=True)
    identified_date = Column(DateTime, default=datetime.utcnow)
    last_reviewed = Column(DateTime)
    next_review = Column(DateTime)
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    identified_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    assessment = relationship("RiskAssessment", back_populates="risks")
    item = relationship("EnhancedItem")
    supplier = relationship("Supplier")
    facility = relationship("Facility")
    identifier = relationship("User")
    mitigations = relationship("RiskMitigation", back_populates="risk", cascade="all, delete-orphan")
    monitoring = relationship("RiskMonitoring", back_populates="risk", cascade="all, delete-orphan")

# Risk Mitigation
class RiskMitigation(Base):
    __tablename__ = 'risk_mitigations'
    
    id = Column(Integer, primary_key=True, index=True)
    mitigation_id = Column(String(100), unique=True, nullable=False, index=True)
    risk_id = Column(Integer, ForeignKey('risks.id'), nullable=False)
    assessment_id = Column(Integer, ForeignKey('risk_assessments.id'), nullable=False)
    
    # Mitigation details
    mitigation_name = Column(String(255), nullable=False)
    mitigation_type = Column(String(50), nullable=False)  # prevent, reduce, transfer, accept
    mitigation_description = Column(Text, nullable=False)
    mitigation_strategy = Column(Text)  # Mitigation strategy
    
    # Implementation
    implementation_plan = Column(JSON)  # Implementation plan
    required_resources = Column(JSON)  # Required resources
    estimated_cost = Column(Float)  # Estimated cost
    actual_cost = Column(Float)  # Actual cost
    timeline = Column(JSON)  # Implementation timeline
    
    # Status
    status = Column(Enum(MitigationStatus), default=MitigationStatus.PENDING)
    priority = Column(String(20), default='medium')  # low, medium, high, critical
    assigned_to = Column(Integer, ForeignKey('users.id'))
    assigned_date = Column(DateTime, default=datetime.utcnow)
    
    # Progress
    progress_percentage = Column(Float, default=0.0)  # 0-100 progress
    start_date = Column(DateTime)
    target_completion_date = Column(DateTime)
    actual_completion_date = Column(DateTime)
    
    # Effectiveness
    effectiveness_score = Column(Float)  # 0-100 effectiveness score
    risk_reduction = Column(Float)  # Risk reduction percentage
    residual_risk = Column(Float)  # Residual risk score
    
    # Monitoring
    monitoring_required = Column(Boolean, default=True)
    monitoring_frequency = Column(String(20), default='monthly')  # daily, weekly, monthly, quarterly
    next_monitoring_date = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    risk = relationship("Risk", back_populates="mitigations")
    assessment = relationship("RiskAssessment", back_populates="mitigations")
    assignee = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])

# Risk Monitoring
class RiskMonitoring(Base):
    __tablename__ = 'risk_monitoring'
    
    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey('risks.id'), nullable=False)
    
    # Monitoring details
    monitoring_date = Column(DateTime, default=datetime.utcnow)
    monitoring_type = Column(String(50), nullable=False)  # scheduled, ad_hoc, incident_triggered
    monitoring_method = Column(String(50))  # automated, manual, hybrid
    
    # Risk indicators
    current_risk_score = Column(Float, nullable=False)
    risk_trend = Column(String(20))  # increasing, stable, decreasing
    risk_velocity = Column(Float)  # Rate of change
    risk_indicators = Column(JSON)  # Current risk indicators
    
    # Monitoring results
    monitoring_findings = Column(Text)
    risk_changes = Column(JSON)  # Changes in risk factors
    new_risks = Column(JSON)  # New risks identified
    risk_events = Column(JSON)  # Risk events occurred
    
    # Actions
    actions_required = Column(JSON)  # Actions required
    actions_taken = Column(JSON)  # Actions taken
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    
    # Status
    monitoring_status = Column(String(20), default='completed')  # pending, in_progress, completed, failed
    is_escalated = Column(Boolean, default=False)
    escalation_reason = Column(Text)
    
    # Metadata
    monitored_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    risk = relationship("Risk", back_populates="monitoring")
    monitor = relationship("User")

# Risk Events
class RiskEvent(Base):
    __tablename__ = 'risk_events'
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, nullable=False, index=True)
    risk_id = Column(Integer, ForeignKey('risks.id'), nullable=False)
    
    # Event details
    event_name = Column(String(255), nullable=False)
    event_type = Column(String(50), nullable=False)  # incident, near_miss, opportunity
    event_description = Column(Text, nullable=False)
    event_date = Column(DateTime, default=datetime.utcnow)
    event_location = Column(String(255))
    
    # Event impact
    impact_assessment = Column(Text)
    financial_impact = Column(Float)  # Financial impact
    operational_impact = Column(String(50))  # Operational impact
    reputational_impact = Column(String(50))  # Reputational impact
    timeline_impact = Column(String(50))  # Timeline impact
    
    # Event response
    response_actions = Column(JSON)  # Response actions taken
    response_time = Column(Integer)  # Response time in minutes
    response_effectiveness = Column(Float)  # Response effectiveness score
    
    # Root cause analysis
    root_causes = Column(JSON)  # Root causes identified
    contributing_factors = Column(JSON)  # Contributing factors
    lessons_learned = Column(Text)  # Lessons learned
    
    # Status
    status = Column(String(20), default='open')  # open, investigating, resolved, closed
    severity = Column(String(20), default='medium')  # low, medium, high, critical
    priority = Column(String(20), default='medium')  # low, medium, high, critical
    
    # Resolution
    resolution_actions = Column(JSON)  # Resolution actions
    resolution_date = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reported_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    risk = relationship("Risk")
    reporter = relationship("User")

# Risk Controls
class RiskControl(Base):
    __tablename__ = 'risk_controls'
    
    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(String(100), unique=True, nullable=False, index=True)
    risk_id = Column(Integer, ForeignKey('risks.id'), nullable=False)
    
    # Control details
    control_name = Column(String(255), nullable=False)
    control_type = Column(String(50), nullable=False)  # preventive, detective, corrective
    control_category = Column(String(50))  # administrative, technical, physical
    control_description = Column(Text, nullable=False)
    
    # Control implementation
    control_owner = Column(String(255))  # Control owner
    control_implementation = Column(Text)  # Implementation details
    control_frequency = Column(String(20), default='continuous')  # continuous, daily, weekly, monthly
    control_effectiveness = Column(Float)  # 0-100 effectiveness score
    
    # Control testing
    testing_frequency = Column(String(20), default='annual')  # monthly, quarterly, semi_annual, annual
    last_tested = Column(DateTime)
    next_test_date = Column(DateTime)
    testing_results = Column(JSON)  # Testing results
    testing_notes = Column(Text)
    
    # Control status
    status = Column(String(20), default='active')  # active, inactive, under_review
    is_automated = Column(Boolean, default=False)
    automation_level = Column(String(20))  # manual, semi_automated, fully_automated
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    risk = relationship("Risk")
    creator = relationship("User")

# Risk Reporting
class RiskReport(Base):
    __tablename__ = 'risk_reports'
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Report details
    report_name = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # executive, operational, regulatory, ad_hoc
    report_period_start = Column(DateTime, nullable=False)
    report_period_end = Column(DateTime, nullable=False)
    
    # Report content
    executive_summary = Column(Text)
    risk_overview = Column(JSON)  # Risk overview
    key_risks = Column(JSON)  # Key risks identified
    risk_trends = Column(JSON)  # Risk trends
    mitigation_status = Column(JSON)  # Mitigation status
    recommendations = Column(JSON)  # Recommendations
    
    # Report data
    report_data = Column(JSON)  # Detailed report data
    charts_data = Column(JSON)  # Charts and visualizations
    appendices = Column(JSON)  # Report appendices
    
    # Report status
    status = Column(String(20), default='draft')  # draft, review, approved, published
    is_public = Column(Boolean, default=False)
    published_date = Column(DateTime)
    
    # Compliance
    regulatory_requirements = Column(JSON)  # Regulatory requirements
    audit_trail = Column(JSON)  # Audit trail
    approval_chain = Column(JSON)  # Approval chain
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Risk Dashboard
class RiskDashboard(Base):
    __tablename__ = 'risk_dashboards'
    
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

# Risk Analytics
class RiskAnalytics(Base):
    __tablename__ = 'risk_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    analytics_type = Column(String(50), nullable=False)  # risk_trends, mitigation_effectiveness, cost_analysis
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Analytics data
    analytics_data = Column(JSON, nullable=False)
    key_metrics = Column(JSON)  # Key metrics
    trends = Column(JSON)  # Trend analysis
    insights = Column(JSON)  # Key insights
    recommendations = Column(JSON)  # Recommendations
    
    # Performance metrics
    total_risks = Column(Integer, default=0)
    high_risk_count = Column(Integer, default=0)
    mitigated_risks = Column(Integer, default=0)
    mitigation_effectiveness = Column(Float, default=0.0)
    
    # Cost analysis
    total_mitigation_cost = Column(Float, default=0.0)
    cost_per_risk = Column(Float, default=0.0)
    roi_mitigation = Column(Float, default=0.0)
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    calculated_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    calculator = relationship("User")
