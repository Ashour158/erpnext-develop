# AI Models - Complete AI Analytics and Smart Features
# Advanced AI models without Frappe dependencies

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

# Enums
class AIModelType(enum.Enum):
    PREDICTIVE = "Predictive"
    CLASSIFICATION = "Classification"
    REGRESSION = "Regression"
    CLUSTERING = "Clustering"
    NLP = "Natural Language Processing"
    COMPUTER_VISION = "Computer Vision"
    RECOMMENDATION = "Recommendation"

class ModelStatus(enum.Enum):
    TRAINING = "Training"
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    DEPRECATED = "Deprecated"

class AnalysisType(enum.Enum):
    FINANCIAL = "Financial"
    OPERATIONAL = "Operational"
    CUSTOMER = "Customer"
    EMPLOYEE = "Employee"
    MARKETING = "Marketing"
    SALES = "Sales"

class InsightType(enum.Enum):
    TREND = "Trend"
    ANOMALY = "Anomaly"
    PATTERN = "Pattern"
    PREDICTION = "Prediction"
    RECOMMENDATION = "Recommendation"

# AI Model Model
class AIModel(BaseModel):
    """AI Model model"""
    __tablename__ = 'ai_models'
    
    model_name = db.Column(db.String(200), nullable=False)
    model_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Model Details
    model_type = db.Column(db.Enum(AIModelType), nullable=False)
    model_version = db.Column(db.String(20), default='1.0.0')
    model_status = db.Column(db.Enum(ModelStatus), default=ModelStatus.TRAINING)
    
    # Model Configuration
    model_config = db.Column(db.JSON)  # Model parameters and configuration
    training_data_source = db.Column(db.String(200))
    model_file_path = db.Column(db.String(255))
    
    # Performance Metrics
    accuracy = db.Column(db.Float, default=0.0)
    precision = db.Column(db.Float, default=0.0)
    recall = db.Column(db.Float, default=0.0)
    f1_score = db.Column(db.Float, default=0.0)
    
    # Training Information
    training_start_date = db.Column(db.DateTime)
    training_end_date = db.Column(db.DateTime)
    last_retrain_date = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    analyses = relationship("AIAnalysis", back_populates="model")
    predictions = relationship("AIPrediction", back_populates="model")
    recommendations = relationship("AIRecommendation", back_populates="model")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'model_name': self.model_name,
            'model_code': self.model_code,
            'description': self.description,
            'model_type': self.model_type.value if self.model_type else None,
            'model_version': self.model_version,
            'model_status': self.model_status.value if self.model_status else None,
            'model_config': self.model_config,
            'training_data_source': self.training_data_source,
            'model_file_path': self.model_file_path,
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'training_start_date': self.training_start_date.isoformat() if self.training_start_date else None,
            'training_end_date': self.training_end_date.isoformat() if self.training_end_date else None,
            'last_retrain_date': self.last_retrain_date.isoformat() if self.last_retrain_date else None,
            'company_id': self.company_id
        })
        return data

# AI Analysis Model
class AIAnalysis(BaseModel):
    """AI Analysis model"""
    __tablename__ = 'ai_analyses'
    
    # Model
    model_id = db.Column(db.Integer, db.ForeignKey('ai_models.id'), nullable=False)
    model = relationship("AIModel", back_populates="analyses")
    
    # Analysis Details
    analysis_name = db.Column(db.String(200), nullable=False)
    analysis_type = db.Column(db.Enum(AnalysisType), nullable=False)
    description = db.Column(db.Text)
    
    # Data Source
    data_source = db.Column(db.String(200))
    data_period_start = db.Column(db.DateTime)
    data_period_end = db.Column(db.DateTime)
    
    # Analysis Results
    analysis_results = db.Column(db.JSON)  # Analysis results and insights
    confidence_score = db.Column(db.Float, default=0.0)
    key_findings = db.Column(db.JSON)  # Key findings from analysis
    
    # Status
    status = db.Column(db.String(20), default='Completed')  # Pending, Running, Completed, Failed
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    insights = relationship("AIInsight", back_populates="analysis")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'model_id': self.model_id,
            'analysis_name': self.analysis_name,
            'analysis_type': self.analysis_type.value if self.analysis_type else None,
            'description': self.description,
            'data_source': self.data_source,
            'data_period_start': self.data_period_start.isoformat() if self.data_period_start else None,
            'data_period_end': self.data_period_end.isoformat() if self.data_period_end else None,
            'analysis_results': self.analysis_results,
            'confidence_score': self.confidence_score,
            'key_findings': self.key_findings,
            'status': self.status,
            'company_id': self.company_id
        })
        return data

# AI Training Model
class AITraining(BaseModel):
    """AI Training model"""
    __tablename__ = 'ai_trainings'
    
    # Model
    model_id = db.Column(db.Integer, db.ForeignKey('ai_models.id'), nullable=False)
    model = relationship("AIModel")
    
    # Training Details
    training_name = db.Column(db.String(200), nullable=False)
    training_data_size = db.Column(db.Integer, default=0)
    training_algorithm = db.Column(db.String(100))
    
    # Training Parameters
    training_parameters = db.Column(db.JSON)  # Training hyperparameters
    validation_split = db.Column(db.Float, default=0.2)
    epochs = db.Column(db.Integer, default=100)
    batch_size = db.Column(db.Integer, default=32)
    
    # Training Results
    training_accuracy = db.Column(db.Float, default=0.0)
    validation_accuracy = db.Column(db.Float, default=0.0)
    training_loss = db.Column(db.Float, default=0.0)
    validation_loss = db.Column(db.Float, default=0.0)
    
    # Training Status
    status = db.Column(db.String(20), default='Pending')  # Pending, Running, Completed, Failed
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'model_id': self.model_id,
            'training_name': self.training_name,
            'training_data_size': self.training_data_size,
            'training_algorithm': self.training_algorithm,
            'training_parameters': self.training_parameters,
            'validation_split': self.validation_split,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'training_accuracy': self.training_accuracy,
            'validation_accuracy': self.validation_accuracy,
            'training_loss': self.training_loss,
            'validation_loss': self.validation_loss,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'company_id': self.company_id
        })
        return data

# AI Prediction Model
class AIPrediction(BaseModel):
    """AI Prediction model"""
    __tablename__ = 'ai_predictions'
    
    # Model
    model_id = db.Column(db.Integer, db.ForeignKey('ai_models.id'), nullable=False)
    model = relationship("AIModel", back_populates="predictions")
    
    # Prediction Details
    prediction_name = db.Column(db.String(200), nullable=False)
    prediction_type = db.Column(db.String(100))  # Sales, Revenue, Customer Churn, etc.
    
    # Input Data
    input_data = db.Column(db.JSON)  # Input data for prediction
    prediction_date = db.Column(db.DateTime, default=datetime.now)
    
    # Prediction Results
    predicted_value = db.Column(db.Float, default=0.0)
    confidence_score = db.Column(db.Float, default=0.0)
    prediction_interval = db.Column(db.JSON)  # Lower and upper bounds
    
    # Actual Results (for validation)
    actual_value = db.Column(db.Float)
    prediction_accuracy = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'model_id': self.model_id,
            'prediction_name': self.prediction_name,
            'prediction_type': self.prediction_type,
            'input_data': self.input_data,
            'prediction_date': self.prediction_date.isoformat() if self.prediction_date else None,
            'predicted_value': self.predicted_value,
            'confidence_score': self.confidence_score,
            'prediction_interval': self.prediction_interval,
            'actual_value': self.actual_value,
            'prediction_accuracy': self.prediction_accuracy,
            'company_id': self.company_id
        })
        return data

# AI Recommendation Model
class AIRecommendation(BaseModel):
    """AI Recommendation model"""
    __tablename__ = 'ai_recommendations'
    
    # Model
    model_id = db.Column(db.Integer, db.ForeignKey('ai_models.id'), nullable=False)
    model = relationship("AIModel", back_populates="recommendations")
    
    # Recommendation Details
    recommendation_type = db.Column(db.String(100))  # Product, Content, Action, etc.
    target_user_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    target_user = relationship("Employee")
    
    # Recommendation Content
    recommendation_title = db.Column(db.String(200), nullable=False)
    recommendation_description = db.Column(db.Text)
    recommendation_data = db.Column(db.JSON)  # Recommendation details
    
    # Scoring
    recommendation_score = db.Column(db.Float, default=0.0)
    confidence_level = db.Column(db.Float, default=0.0)
    
    # Status
    status = db.Column(db.String(20), default='Active')  # Active, Accepted, Rejected, Expired
    is_implemented = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'model_id': self.model_id,
            'recommendation_type': self.recommendation_type,
            'target_user_id': self.target_user_id,
            'recommendation_title': self.recommendation_title,
            'recommendation_description': self.recommendation_description,
            'recommendation_data': self.recommendation_data,
            'recommendation_score': self.recommendation_score,
            'confidence_level': self.confidence_level,
            'status': self.status,
            'is_implemented': self.is_implemented,
            'company_id': self.company_id
        })
        return data

# AI Conversation Model
class AIConversation(BaseModel):
    """AI Conversation model"""
    __tablename__ = 'ai_conversations'
    
    # User
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Conversation Details
    conversation_id = db.Column(db.String(100), unique=True, nullable=False)
    conversation_type = db.Column(db.String(50))  # Chat, Support, Assistant, etc.
    
    # Messages
    messages = db.Column(db.JSON)  # List of conversation messages
    total_messages = db.Column(db.Integer, default=0)
    
    # Status
    status = db.Column(db.String(20), default='Active')  # Active, Closed, Archived
    is_resolved = db.Column(db.Boolean, default=False)
    
    # Sentiment Analysis
    overall_sentiment = db.Column(db.String(20))  # Positive, Negative, Neutral
    sentiment_score = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'conversation_id': self.conversation_id,
            'conversation_type': self.conversation_type,
            'messages': self.messages,
            'total_messages': self.total_messages,
            'status': self.status,
            'is_resolved': self.is_resolved,
            'overall_sentiment': self.overall_sentiment,
            'sentiment_score': self.sentiment_score,
            'company_id': self.company_id
        })
        return data

# AI Insight Model
class AIInsight(BaseModel):
    """AI Insight model"""
    __tablename__ = 'ai_insights'
    
    # Analysis
    analysis_id = db.Column(db.Integer, db.ForeignKey('ai_analyses.id'), nullable=False)
    analysis = relationship("AIAnalysis", back_populates="insights")
    
    # Insight Details
    insight_type = db.Column(db.Enum(InsightType), nullable=False)
    insight_title = db.Column(db.String(200), nullable=False)
    insight_description = db.Column(db.Text)
    
    # Insight Data
    insight_data = db.Column(db.JSON)  # Insight details and metrics
    confidence_score = db.Column(db.Float, default=0.0)
    impact_score = db.Column(db.Float, default=0.0)
    
    # Status
    status = db.Column(db.String(20), default='New')  # New, Reviewed, Actioned, Dismissed
    is_important = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'analysis_id': self.analysis_id,
            'insight_type': self.insight_type.value if self.insight_type else None,
            'insight_title': self.insight_title,
            'insight_description': self.insight_description,
            'insight_data': self.insight_data,
            'confidence_score': self.confidence_score,
            'impact_score': self.impact_score,
            'status': self.status,
            'is_important': self.is_important,
            'company_id': self.company_id
        })
        return data

# AI Pattern Model
class AIPattern(BaseModel):
    """AI Pattern model"""
    __tablename__ = 'ai_patterns'
    
    # Pattern Details
    pattern_name = db.Column(db.String(200), nullable=False)
    pattern_type = db.Column(db.String(100))  # Behavioral, Temporal, Seasonal, etc.
    pattern_description = db.Column(db.Text)
    
    # Pattern Data
    pattern_data = db.Column(db.JSON)  # Pattern details and metrics
    pattern_frequency = db.Column(db.Float, default=0.0)
    pattern_confidence = db.Column(db.Float, default=0.0)
    
    # Detection
    detection_date = db.Column(db.DateTime, default=datetime.now)
    last_occurrence = db.Column(db.DateTime)
    occurrence_count = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'pattern_name': self.pattern_name,
            'pattern_type': self.pattern_type,
            'pattern_description': self.pattern_description,
            'pattern_data': self.pattern_data,
            'pattern_frequency': self.pattern_frequency,
            'pattern_confidence': self.pattern_confidence,
            'detection_date': self.detection_date.isoformat() if self.detection_date else None,
            'last_occurrence': self.last_occurrence.isoformat() if self.last_occurrence else None,
            'occurrence_count': self.occurrence_count,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'company_id': self.company_id
        })
        return data

# AI Alert Model
class AIAlert(BaseModel):
    """AI Alert model"""
    __tablename__ = 'ai_alerts'
    
    # Alert Details
    alert_name = db.Column(db.String(200), nullable=False)
    alert_type = db.Column(db.String(100))  # Anomaly, Threshold, Trend, etc.
    alert_description = db.Column(db.Text)
    
    # Alert Conditions
    alert_conditions = db.Column(db.JSON)  # Alert trigger conditions
    alert_threshold = db.Column(db.Float, default=0.0)
    alert_severity = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Critical
    
    # Alert Data
    alert_data = db.Column(db.JSON)  # Alert details and context
    alert_value = db.Column(db.Float, default=0.0)
    expected_value = db.Column(db.Float, default=0.0)
    
    # Status
    status = db.Column(db.String(20), default='Active')  # Active, Acknowledged, Resolved, Dismissed
    is_acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    acknowledged_by = relationship("Employee")
    acknowledged_date = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'alert_name': self.alert_name,
            'alert_type': self.alert_type,
            'alert_description': self.alert_description,
            'alert_conditions': self.alert_conditions,
            'alert_threshold': self.alert_threshold,
            'alert_severity': self.alert_severity,
            'alert_data': self.alert_data,
            'alert_value': self.alert_value,
            'expected_value': self.expected_value,
            'status': self.status,
            'is_acknowledged': self.is_acknowledged,
            'acknowledged_by_id': self.acknowledged_by_id,
            'acknowledged_date': self.acknowledged_date.isoformat() if self.acknowledged_date else None,
            'company_id': self.company_id
        })
        return data
