# AI-Powered CRM Features
# Advanced AI capabilities to surpass Zoho CRM and Salesforce

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class AIActionType(enum.Enum):
    LEAD_SCORING = "lead_scoring"
    DEAL_PREDICTION = "deal_prediction"
    CUSTOMER_CHURN = "customer_churn"
    NEXT_BEST_ACTION = "next_best_action"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    AUTOMATED_FOLLOW_UP = "automated_follow_up"
    PRICE_OPTIMIZATION = "price_optimization"
    CROSS_SELL = "cross_sell"
    UPSELL = "upsell"
    CUSTOMER_LIFETIME_VALUE = "customer_lifetime_value"

class AIStatus(enum.Enum):
    ACTIVE = "active"
    TRAINING = "training"
    DEPLOYED = "deployed"
    RETIRED = "retired"
    ERROR = "error"

class PredictionConfidence(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

# AI-Powered Lead Scoring
class AILeadScoring(Base):
    __tablename__ = 'ai_lead_scoring'
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)
    
    # AI Scoring
    ai_score = Column(Float, nullable=False)  # 0-100 AI-generated score
    confidence_level = Column(Enum(PredictionConfidence), nullable=False)
    scoring_factors = Column(JSON)  # Factors that influenced the score
    model_version = Column(String(50))  # AI model version used
    
    # Behavioral Analysis
    engagement_score = Column(Float)  # Email opens, clicks, website visits
    demographic_score = Column(Float)  # Company size, industry, location
    behavioral_score = Column(Float)  # Purchase history, interaction patterns
    intent_score = Column(Float)  # Buying signals and intent indicators
    
    # Predictive Insights
    conversion_probability = Column(Float)  # Probability of conversion
    expected_deal_size = Column(Float)  # Predicted deal value
    time_to_close = Column(Integer)  # Days to close prediction
    best_contact_time = Column(DateTime)  # Optimal contact time
    
    # AI Recommendations
    recommended_actions = Column(JSON)  # AI-suggested next actions
    priority_level = Column(String(20))  # High, Medium, Low
    follow_up_suggestions = Column(JSON)  # Personalized follow-up suggestions
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    lead = relationship("Lead")

# AI-Powered Deal Prediction
class AIDealPrediction(Base):
    __tablename__ = 'ai_deal_prediction'
    
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'), nullable=False)
    
    # AI Predictions
    win_probability = Column(Float, nullable=False)  # 0-100% win probability
    confidence_level = Column(Enum(PredictionConfidence), nullable=False)
    predicted_close_date = Column(DateTime)
    predicted_deal_value = Column(Float)
    
    # Risk Analysis
    risk_factors = Column(JSON)  # Factors that could affect the deal
    risk_score = Column(Float)  # 0-100 risk score
    mitigation_suggestions = Column(JSON)  # AI-suggested risk mitigation
    
    # Competitive Analysis
    competitor_analysis = Column(JSON)  # AI analysis of competitive landscape
    competitive_advantage = Column(JSON)  # Our competitive advantages
    competitive_threats = Column(JSON)  # Potential competitive threats
    
    # Deal Optimization
    optimal_price = Column(Float)  # AI-suggested optimal price
    price_sensitivity = Column(Float)  # How price affects win probability
    negotiation_tips = Column(JSON)  # AI-generated negotiation strategies
    
    # Stakeholder Analysis
    decision_makers = Column(JSON)  # Identified decision makers
    influencers = Column(JSON)  # Key influencers
    champion = Column(String(255))  # Internal champion
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    opportunity = relationship("Opportunity")

# AI-Powered Customer Churn Prediction
class AICustomerChurn(Base):
    __tablename__ = 'ai_customer_churn'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    
    # Churn Prediction
    churn_probability = Column(Float, nullable=False)  # 0-100% churn probability
    confidence_level = Column(Enum(PredictionConfidence), nullable=False)
    churn_risk_level = Column(String(20))  # Low, Medium, High, Critical
    predicted_churn_date = Column(DateTime)
    
    # Churn Indicators
    engagement_decline = Column(Float)  # Decline in engagement metrics
    support_ticket_increase = Column(Float)  # Increase in support tickets
    payment_delays = Column(Integer)  # Number of payment delays
    feature_usage_decline = Column(Float)  # Decline in feature usage
    
    # Retention Strategies
    retention_actions = Column(JSON)  # AI-suggested retention actions
    personalized_offers = Column(JSON)  # Personalized retention offers
    intervention_urgency = Column(String(20))  # Immediate, Soon, Later
    
    # Customer Health Score
    health_score = Column(Float)  # Overall customer health score
    health_trend = Column(String(20))  # Improving, Stable, Declining
    health_factors = Column(JSON)  # Factors affecting health score
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    customer = relationship("Customer")

# AI-Powered Next Best Action
class AINextBestAction(Base):
    __tablename__ = 'ai_next_best_action'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'))
    
    # AI Recommendations
    recommended_action = Column(String(255), nullable=False)
    action_type = Column(Enum(AIActionType), nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0-100 confidence
    expected_outcome = Column(String(255))  # Expected result of action
    
    # Action Details
    action_description = Column(Text)
    action_priority = Column(String(20))  # High, Medium, Low
    estimated_effort = Column(String(20))  # Low, Medium, High
    time_to_complete = Column(Integer)  # Estimated minutes to complete
    
    # Context and Timing
    optimal_timing = Column(DateTime)  # Best time to execute action
    context_factors = Column(JSON)  # Factors influencing the recommendation
    success_probability = Column(Float)  # Probability of success
    
    # Personalization
    personalized_message = Column(Text)  # AI-generated personalized message
    communication_channel = Column(String(50))  # Email, Phone, SMS, etc.
    tone_suggestion = Column(String(50))  # Professional, Friendly, Urgent, etc.
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    customer = relationship("Customer")
    opportunity = relationship("Opportunity")

# AI-Powered Sentiment Analysis
class AISentimentAnalysis(Base):
    __tablename__ = 'ai_sentiment_analysis'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    
    # Sentiment Analysis
    overall_sentiment = Column(String(20), nullable=False)  # Positive, Negative, Neutral
    sentiment_score = Column(Float, nullable=False)  # -1 to 1 sentiment score
    confidence_level = Column(Enum(PredictionConfidence), nullable=False)
    
    # Emotion Analysis
    emotions = Column(JSON)  # Detected emotions (joy, anger, fear, etc.)
    emotion_scores = Column(JSON)  # Scores for each emotion
    dominant_emotion = Column(String(50))  # Most dominant emotion
    
    # Content Analysis
    analyzed_content = Column(Text)  # Content that was analyzed
    content_type = Column(String(50))  # Email, Call, Chat, Review, etc.
    key_phrases = Column(JSON)  # Important phrases identified
    topics = Column(JSON)  # Topics discussed
    
    # Trend Analysis
    sentiment_trend = Column(String(20))  # Improving, Stable, Declining
    trend_duration = Column(Integer)  # Days of trend
    trend_factors = Column(JSON)  # Factors influencing trend
    
    # Actionable Insights
    recommended_actions = Column(JSON)  # Actions based on sentiment
    urgency_level = Column(String(20))  # Low, Medium, High, Critical
    follow_up_required = Column(Boolean, default=False)
    
    # Metadata
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    customer = relationship("Customer")

# AI-Powered Customer Lifetime Value
class AICustomerLifetimeValue(Base):
    __tablename__ = 'ai_customer_lifetime_value'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    
    # CLV Predictions
    predicted_clv = Column(Float, nullable=False)  # Predicted lifetime value
    confidence_level = Column(Enum(PredictionConfidence), nullable=False)
    clv_confidence_interval = Column(JSON)  # Min and max CLV predictions
    
    # CLV Components
    acquisition_cost = Column(Float)  # Customer acquisition cost
    retention_rate = Column(Float)  # Predicted retention rate
    average_order_value = Column(Float)  # Predicted average order value
    purchase_frequency = Column(Float)  # Predicted purchase frequency
    
    # Segmentation
    customer_segment = Column(String(50))  # High-value, Medium-value, Low-value
    segment_characteristics = Column(JSON)  # Characteristics of the segment
    segment_rank = Column(Integer)  # Rank within segment
    
    # Growth Potential
    growth_potential = Column(Float)  # Potential for CLV growth
    growth_factors = Column(JSON)  # Factors that could increase CLV
    growth_strategies = Column(JSON)  # Strategies to increase CLV
    
    # Risk Factors
    churn_risk = Column(Float)  # Risk of customer churn
    value_at_risk = Column(Float)  # Potential value loss
    risk_mitigation = Column(JSON)  # Strategies to reduce risk
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    customer = relationship("Customer")

# AI-Powered Cross-sell and Upsell
class AICrossSellUpsell(Base):
    __tablename__ = 'ai_cross_sell_upsell'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    
    # Recommendations
    recommendation_type = Column(String(20), nullable=False)  # Cross-sell, Upsell
    recommended_products = Column(JSON)  # Recommended products/services
    recommendation_score = Column(Float, nullable=False)  # 0-100 recommendation score
    confidence_level = Column(Enum(PredictionConfidence), nullable=False)
    
    # Product Analysis
    product_affinity = Column(JSON)  # Product affinity scores
    complementary_products = Column(JSON)  # Complementary products
    upgrade_paths = Column(JSON)  # Potential upgrade paths
    
    # Customer Analysis
    purchase_history = Column(JSON)  # Relevant purchase history
    behavior_patterns = Column(JSON)  # Behavior patterns indicating interest
    demographic_factors = Column(JSON)  # Demographic factors
    
    # Timing and Context
    optimal_timing = Column(DateTime)  # Best time to make offer
    seasonal_factors = Column(JSON)  # Seasonal considerations
    market_conditions = Column(JSON)  # Current market conditions
    
    # Personalization
    personalized_message = Column(Text)  # Personalized offer message
    offer_value = Column(Float)  # Value of the offer
    discount_suggestion = Column(Float)  # Suggested discount percentage
    
    # Success Prediction
    acceptance_probability = Column(Float)  # Probability of acceptance
    expected_revenue = Column(Float)  # Expected revenue from recommendation
    roi_prediction = Column(Float)  # Predicted ROI
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    customer = relationship("Customer")

# AI-Powered Price Optimization
class AIPriceOptimization(Base):
    __tablename__ = 'ai_price_optimization'
    
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'), nullable=False)
    
    # Price Recommendations
    optimal_price = Column(Float, nullable=False)  # AI-recommended optimal price
    price_range = Column(JSON)  # Min and max recommended prices
    confidence_level = Column(Enum(PredictionConfidence), nullable=False)
    
    # Price Analysis
    current_price = Column(Float)  # Current quoted price
    price_sensitivity = Column(Float)  # How price affects win probability
    competitive_positioning = Column(JSON)  # Competitive price analysis
    
    # Market Factors
    market_conditions = Column(JSON)  # Current market conditions
    demand_forecast = Column(Float)  # Demand forecast
    supply_conditions = Column(JSON)  # Supply conditions
    
    # Customer Factors
    customer_price_sensitivity = Column(Float)  # Customer's price sensitivity
    budget_constraints = Column(JSON)  # Customer budget constraints
    value_perception = Column(Float)  # Customer's value perception
    
    # Revenue Impact
    revenue_impact = Column(Float)  # Expected revenue impact
    win_probability_impact = Column(Float)  # Impact on win probability
    margin_impact = Column(Float)  # Impact on profit margin
    
    # Negotiation Support
    negotiation_tips = Column(JSON)  # AI-generated negotiation tips
    fallback_prices = Column(JSON)  # Fallback price options
    value_proposition = Column(Text)  # Value proposition for the price
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    opportunity = relationship("Opportunity")

# AI Model Management
class AIModel(Base):
    __tablename__ = 'ai_models'
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(255), nullable=False)
    model_type = Column(Enum(AIActionType), nullable=False)
    model_version = Column(String(50), nullable=False)
    
    # Model Configuration
    model_config = Column(JSON)  # Model configuration
    training_data = Column(JSON)  # Training data information
    model_metrics = Column(JSON)  # Model performance metrics
    
    # Model Status
    status = Column(Enum(AIStatus), default=AIStatus.TRAINING)
    accuracy_score = Column(Float)  # Model accuracy score
    last_trained = Column(DateTime)  # Last training date
    next_training = Column(DateTime)  # Next scheduled training
    
    # Deployment
    is_deployed = Column(Boolean, default=False)
    deployment_date = Column(DateTime)
    deployment_environment = Column(String(50))  # Production, Staging, Development
    
    # Performance Monitoring
    prediction_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)
    last_performance_check = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# AI Insights and Analytics
class AIInsights(Base):
    __tablename__ = 'ai_insights'
    
    id = Column(Integer, primary_key=True, index=True)
    insight_type = Column(String(50), nullable=False)  # trend, anomaly, opportunity, risk
    insight_title = Column(String(255), nullable=False)
    insight_description = Column(Text, nullable=False)
    
    # Insight Data
    insight_data = Column(JSON, nullable=False)  # Insight data
    confidence_score = Column(Float, nullable=False)  # 0-100 confidence
    impact_score = Column(Float, nullable=False)  # 0-100 impact score
    urgency_level = Column(String(20))  # Low, Medium, High, Critical
    
    # Recommendations
    recommended_actions = Column(JSON)  # Recommended actions
    expected_outcomes = Column(JSON)  # Expected outcomes
    success_metrics = Column(JSON)  # Metrics to track success
    
    # Context
    affected_entities = Column(JSON)  # Affected customers, opportunities, etc.
    time_horizon = Column(String(20))  # Short-term, Medium-term, Long-term
    business_impact = Column(String(50))  # Revenue, Cost, Risk, Opportunity
    
    # Status
    status = Column(String(20), default='new')  # new, reviewed, acted_upon, dismissed
    reviewed_by = Column(Integer, ForeignKey('users.id'))
    reviewed_at = Column(DateTime)
    action_taken = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    reviewer = relationship("User")
