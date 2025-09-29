# Enhanced CRM Features
# Additional advanced features to make CRM superior to all competitors

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class RelationshipType(enum.Enum):
    CUSTOMER = "customer"
    VENDOR = "vendor"
    PARTNER = "partner"
    COMPETITOR = "competitor"
    SUPPLIER = "supplier"
    INVESTOR = "investor"
    ADVISOR = "advisor"

class InteractionType(enum.Enum):
    EMAIL = "email"
    PHONE = "phone"
    MEETING = "meeting"
    DEMO = "demo"
    PROPOSAL = "proposal"
    CONTRACT = "contract"
    SUPPORT = "support"
    SOCIAL = "social"
    WEBSITE = "website"
    REFERRAL = "referral"

class DealComplexity(enum.Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"

class SalesMethodology(enum.Enum):
    CHALLENGER = "challenger"
    SPIN = "spin"
    SANDLER = "sandler"
    MEDDIC = "meddic"
    BANT = "bant"
    CUSTOM = "custom"

# Advanced Customer Relationship Management
class CustomerRelationship(Base):
    __tablename__ = 'customer_relationships'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    related_entity_id = Column(Integer, nullable=False)  # Related customer, vendor, etc.
    relationship_type = Column(Enum(RelationshipType), nullable=False)
    
    # Relationship Details
    relationship_strength = Column(Float, default=0.0)  # 0-100 relationship strength
    relationship_status = Column(String(50), default='active')  # active, inactive, terminated
    relationship_start = Column(DateTime, nullable=False)
    relationship_end = Column(DateTime)
    
    # Relationship Metrics
    interaction_frequency = Column(Float, default=0.0)  # Interactions per month
    last_interaction = Column(DateTime)
    total_interactions = Column(Integer, default=0)
    satisfaction_score = Column(Float)  # 0-100 satisfaction score
    
    # Relationship Context
    relationship_context = Column(JSON)  # Context and history
    relationship_notes = Column(Text)
    relationship_tags = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    customer = relationship("Customer")

# Advanced Interaction Tracking
class CustomerInteraction(Base):
    __tablename__ = 'customer_interactions'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    
    # Interaction Details
    interaction_type = Column(Enum(InteractionType), nullable=False)
    interaction_subject = Column(String(255))
    interaction_description = Column(Text, nullable=False)
    interaction_outcome = Column(String(100))  # positive, negative, neutral
    
    # Interaction Metrics
    interaction_duration = Column(Integer)  # Minutes
    interaction_quality = Column(Float)  # 0-100 quality score
    satisfaction_rating = Column(Float)  # 0-100 satisfaction
    follow_up_required = Column(Boolean, default=False)
    
    # Interaction Context
    interaction_location = Column(String(255))
    interaction_participants = Column(JSON)  # List of participants
    interaction_materials = Column(JSON)  # Materials used/shared
    interaction_notes = Column(Text)
    
    # Sentiment Analysis
    sentiment_score = Column(Float)  # -1 to 1
    emotion_tags = Column(JSON)  # Detected emotions
    key_phrases = Column(JSON)  # Important phrases
    topics_discussed = Column(JSON)  # Topics discussed
    
    # Follow-up Actions
    follow_up_actions = Column(JSON)  # Required follow-up actions
    follow_up_deadline = Column(DateTime)
    follow_up_assigned_to = Column(Integer, ForeignKey('users.id'))
    follow_up_status = Column(String(50), default='pending')
    
    # Metadata
    interaction_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    customer = relationship("Customer")
    contact = relationship("Contact")
    assigned_user = relationship("User")

# Advanced Deal Management
class AdvancedDeal(Base):
    __tablename__ = 'advanced_deals'
    
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'), nullable=False)
    
    # Deal Complexity
    deal_complexity = Column(Enum(DealComplexity), nullable=False)
    deal_size_category = Column(String(50))  # small, medium, large, enterprise
    deal_urgency = Column(String(20))  # low, medium, high, critical
    
    # Sales Methodology
    sales_methodology = Column(Enum(SalesMethodology), nullable=False)
    methodology_stage = Column(String(50))  # Current methodology stage
    methodology_score = Column(Float, default=0.0)  # 0-100 methodology score
    
    # Deal Structure
    deal_structure = Column(JSON)  # Deal structure and components
    pricing_model = Column(String(50))  # one-time, subscription, usage-based
    payment_terms = Column(JSON)  # Payment terms and conditions
    contract_terms = Column(JSON)  # Contract terms and conditions
    
    # Stakeholder Analysis
    decision_makers = Column(JSON)  # Decision makers and their roles
    influencers = Column(JSON)  # Influencers and their impact
    champions = Column(JSON)  # Internal champions
    blockers = Column(JSON)  # Potential blockers
    
    # Competitive Analysis
    competitors = Column(JSON)  # Competing vendors
    competitive_position = Column(String(50))  # leading, competitive, losing
    competitive_advantages = Column(JSON)  # Our competitive advantages
    competitive_threats = Column(JSON)  # Competitive threats
    
    # Risk Assessment
    risk_factors = Column(JSON)  # Risk factors and mitigation
    risk_score = Column(Float, default=0.0)  # 0-100 risk score
    risk_mitigation = Column(JSON)  # Risk mitigation strategies
    
    # Deal Optimization
    optimization_opportunities = Column(JSON)  # Optimization opportunities
    upsell_potential = Column(Float, default=0.0)  # 0-100 upsell potential
    cross_sell_potential = Column(Float, default=0.0)  # 0-100 cross-sell potential
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    opportunity = relationship("Opportunity")

# Advanced Sales Forecasting
class SalesForecast(Base):
    __tablename__ = 'sales_forecasts'
    
    id = Column(Integer, primary_key=True, index=True)
    forecast_name = Column(String(255), nullable=False)
    forecast_period = Column(String(50), nullable=False)  # monthly, quarterly, yearly
    forecast_start = Column(DateTime, nullable=False)
    forecast_end = Column(DateTime, nullable=False)
    
    # Forecast Data
    forecasted_revenue = Column(Float, nullable=False)
    forecasted_deals = Column(Integer, nullable=False)
    forecasted_conversion_rate = Column(Float, nullable=False)
    forecasted_average_deal_size = Column(Float, nullable=False)
    
    # Forecast Accuracy
    forecast_accuracy = Column(Float, default=0.0)  # 0-100% accuracy
    forecast_confidence = Column(Float, default=0.0)  # 0-100% confidence
    forecast_methodology = Column(String(100))  # Forecasting methodology used
    
    # Forecast Breakdown
    forecast_by_product = Column(JSON)  # Revenue by product
    forecast_by_region = Column(JSON)  # Revenue by region
    forecast_by_rep = Column(JSON)  # Revenue by sales rep
    forecast_by_stage = Column(JSON)  # Revenue by deal stage
    
    # Forecast Trends
    forecast_trend = Column(String(20))  # increasing, stable, decreasing
    forecast_growth_rate = Column(Float, default=0.0)  # Growth rate percentage
    forecast_seasonality = Column(JSON)  # Seasonal adjustments
    
    # Forecast Validation
    actual_revenue = Column(Float, default=0.0)  # Actual revenue achieved
    actual_deals = Column(Integer, default=0)  # Actual deals closed
    variance_percentage = Column(Float, default=0.0)  # Forecast variance
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Advanced Territory Management
class SalesTerritory(Base):
    __tablename__ = 'sales_territories'
    
    id = Column(Integer, primary_key=True, index=True)
    territory_name = Column(String(255), nullable=False)
    territory_code = Column(String(50), unique=True, nullable=False)
    
    # Territory Definition
    territory_type = Column(String(50), nullable=False)  # geographic, industry, product
    territory_description = Column(Text)
    territory_boundaries = Column(JSON)  # Geographic or logical boundaries
    
    # Territory Assignment
    assigned_user_id = Column(Integer, ForeignKey('users.id'))
    assigned_team_id = Column(Integer, ForeignKey('teams.id'))
    assignment_start = Column(DateTime, nullable=False)
    assignment_end = Column(DateTime)
    
    # Territory Metrics
    territory_revenue_target = Column(Float, default=0.0)
    territory_revenue_actual = Column(Float, default=0.0)
    territory_deal_target = Column(Integer, default=0)
    territory_deal_actual = Column(Integer, default=0)
    
    # Territory Performance
    territory_performance_score = Column(Float, default=0.0)  # 0-100
    territory_growth_rate = Column(Float, default=0.0)  # Growth rate percentage
    territory_market_share = Column(Float, default=0.0)  # Market share percentage
    
    # Territory Rules
    territory_rules = Column(JSON)  # Territory-specific rules
    assignment_rules = Column(JSON)  # Lead assignment rules
    conflict_resolution = Column(JSON)  # Conflict resolution rules
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    assigned_user = relationship("User")
    assigned_team = relationship("Team")

# Advanced Sales Team Management
class SalesTeam(Base):
    __tablename__ = 'sales_teams'
    
    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String(255), nullable=False)
    team_code = Column(String(50), unique=True, nullable=False)
    
    # Team Structure
    team_leader_id = Column(Integer, ForeignKey('users.id'))
    team_type = Column(String(50), nullable=False)  # inside, outside, hybrid
    team_size = Column(Integer, default=0)
    
    # Team Performance
    team_revenue_target = Column(Float, default=0.0)
    team_revenue_actual = Column(Float, default=0.0)
    team_performance_score = Column(Float, default=0.0)  # 0-100
    
    # Team Metrics
    team_conversion_rate = Column(Float, default=0.0)
    team_average_deal_size = Column(Float, default=0.0)
    team_sales_velocity = Column(Float, default=0.0)
    team_customer_satisfaction = Column(Float, default=0.0)
    
    # Team Collaboration
    team_collaboration_score = Column(Float, default=0.0)  # 0-100
    team_communication_frequency = Column(Float, default=0.0)
    team_knowledge_sharing = Column(Float, default=0.0)
    
    # Team Development
    team_training_hours = Column(Float, default=0.0)
    team_certification_rate = Column(Float, default=0.0)
    team_skill_development = Column(JSON)  # Skill development tracking
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    team_leader = relationship("User")

# Advanced Sales Coaching
class SalesCoaching(Base):
    __tablename__ = 'sales_coaching'
    
    id = Column(Integer, primary_key=True, index=True)
    coach_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    coachee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Coaching Session
    session_date = Column(DateTime, nullable=False)
    session_duration = Column(Integer, nullable=False)  # Minutes
    session_type = Column(String(50), nullable=False)  # one-on-one, group, role-play
    session_topic = Column(String(255), nullable=False)
    
    # Coaching Content
    coaching_objectives = Column(JSON)  # Session objectives
    coaching_activities = Column(JSON)  # Activities performed
    coaching_materials = Column(JSON)  # Materials used
    coaching_feedback = Column(Text)  # Feedback provided
    
    # Performance Assessment
    skill_assessment = Column(JSON)  # Skill assessment scores
    improvement_areas = Column(JSON)  # Areas for improvement
    strengths_identified = Column(JSON)  # Strengths identified
    action_plan = Column(JSON)  # Action plan for improvement
    
    # Coaching Outcomes
    session_rating = Column(Float)  # 0-100 session rating
    learning_objectives_met = Column(Boolean, default=False)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    coach = relationship("User", foreign_keys=[coach_id])
    coachee = relationship("User", foreign_keys=[coachee_id])

# Advanced Sales Training
class SalesTraining(Base):
    __tablename__ = 'sales_training'
    
    id = Column(Integer, primary_key=True, index=True)
    training_name = Column(String(255), nullable=False)
    training_type = Column(String(50), nullable=False)  # online, offline, hybrid
    training_category = Column(String(50), nullable=False)  # product, process, skill
    
    # Training Content
    training_description = Column(Text)
    training_objectives = Column(JSON)  # Learning objectives
    training_materials = Column(JSON)  # Training materials
    training_curriculum = Column(JSON)  # Training curriculum
    
    # Training Schedule
    training_start = Column(DateTime, nullable=False)
    training_end = Column(DateTime, nullable=False)
    training_duration = Column(Integer, nullable=False)  # Hours
    training_location = Column(String(255))
    
    # Training Requirements
    prerequisites = Column(JSON)  # Prerequisites for training
    target_audience = Column(JSON)  # Target audience
    max_participants = Column(Integer, default=0)
    min_participants = Column(Integer, default=0)
    
    # Training Assessment
    assessment_method = Column(String(50))  # exam, project, practical
    passing_score = Column(Float, default=70.0)  # Passing score percentage
    certification_required = Column(Boolean, default=False)
    certification_validity = Column(Integer)  # Months
    
    # Training Performance
    completion_rate = Column(Float, default=0.0)  # Completion rate percentage
    average_score = Column(Float, default=0.0)  # Average score
    satisfaction_rating = Column(Float, default=0.0)  # Satisfaction rating
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Advanced Sales Performance Management
class SalesPerformance(Base):
    __tablename__ = 'sales_performance'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    performance_period = Column(String(50), nullable=False)  # monthly, quarterly, yearly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Performance Metrics
    revenue_target = Column(Float, default=0.0)
    revenue_actual = Column(Float, default=0.0)
    revenue_achievement = Column(Float, default=0.0)  # Percentage
    
    deal_target = Column(Integer, default=0)
    deal_actual = Column(Integer, default=0)
    deal_achievement = Column(Float, default=0.0)  # Percentage
    
    # Activity Metrics
    calls_made = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    meetings_scheduled = Column(Integer, default=0)
    proposals_sent = Column(Integer, default=0)
    demos_given = Column(Integer, default=0)
    
    # Quality Metrics
    lead_quality_score = Column(Float, default=0.0)  # 0-100
    deal_quality_score = Column(Float, default=0.0)  # 0-100
    customer_satisfaction = Column(Float, default=0.0)  # 0-100
    follow_up_rate = Column(Float, default=0.0)  # Percentage
    
    # Efficiency Metrics
    sales_velocity = Column(Float, default=0.0)  # Days to close
    conversion_rate = Column(Float, default=0.0)  # Percentage
    average_deal_size = Column(Float, default=0.0)
    pipeline_health = Column(Float, default=0.0)  # 0-100
    
    # Performance Ranking
    team_rank = Column(Integer)
    company_rank = Column(Integer)
    percentile = Column(Float)  # Performance percentile
    
    # Performance Trends
    revenue_trend = Column(String(20))  # increasing, stable, decreasing
    activity_trend = Column(String(20))  # increasing, stable, decreasing
    performance_trend = Column(String(20))  # improving, stable, declining
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")

# Advanced Sales Gamification
class SalesGamification(Base):
    __tablename__ = 'sales_gamification'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Gamification Elements
    points_total = Column(Integer, default=0)
    points_current = Column(Integer, default=0)
    level_current = Column(Integer, default=1)
    level_name = Column(String(50), default='Rookie')
    
    # Achievements
    achievements_earned = Column(JSON)  # Achievements earned
    badges_earned = Column(JSON)  # Badges earned
    streaks_current = Column(Integer, default=0)
    streaks_longest = Column(Integer, default=0)
    
    # Leaderboards
    team_rank = Column(Integer)
    company_rank = Column(Integer)
    monthly_rank = Column(Integer)
    quarterly_rank = Column(Integer)
    
    # Challenges
    active_challenges = Column(JSON)  # Active challenges
    completed_challenges = Column(JSON)  # Completed challenges
    challenge_progress = Column(JSON)  # Challenge progress
    
    # Rewards
    rewards_earned = Column(JSON)  # Rewards earned
    rewards_pending = Column(JSON)  # Pending rewards
    rewards_redeemed = Column(JSON)  # Redeemed rewards
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")

# Advanced Sales Intelligence
class SalesIntelligence(Base):
    __tablename__ = 'sales_intelligence'
    
    id = Column(Integer, primary_key=True, index=True)
    intelligence_type = Column(String(50), nullable=False)  # market, competitor, customer
    intelligence_title = Column(String(255), nullable=False)
    intelligence_description = Column(Text)
    
    # Intelligence Data
    intelligence_data = Column(JSON, nullable=False)  # Intelligence data
    intelligence_source = Column(String(100))  # Source of intelligence
    intelligence_confidence = Column(Float, default=0.0)  # 0-100 confidence
    intelligence_relevance = Column(Float, default=0.0)  # 0-100 relevance
    
    # Intelligence Impact
    impact_score = Column(Float, default=0.0)  # 0-100 impact score
    urgency_level = Column(String(20))  # low, medium, high, critical
    action_required = Column(Boolean, default=False)
    action_taken = Column(Boolean, default=False)
    
    # Intelligence Context
    affected_entities = Column(JSON)  # Affected customers, deals, etc.
    intelligence_tags = Column(JSON)  # Intelligence tags
    intelligence_notes = Column(Text)  # Additional notes
    
    # Metadata
    intelligence_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")
