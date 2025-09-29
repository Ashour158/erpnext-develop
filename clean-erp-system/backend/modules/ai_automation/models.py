# AI & Automation Models
# Advanced AI features, machine learning, and process automation

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

class AIModelType(enum.Enum):
    PREDICTIVE = "Predictive"
    CLASSIFICATION = "Classification"
    REGRESSION = "Regression"
    CLUSTERING = "Clustering"
    NLP = "NLP"
    COMPUTER_VISION = "Computer Vision"
    RECOMMENDATION = "Recommendation"

class ModelStatus(enum.Enum):
    TRAINING = "Training"
    TRAINED = "Trained"
    DEPLOYED = "Deployed"
    RETIRED = "Retired"
    FAILED = "Failed"

class AutomationType(enum.Enum):
    WORKFLOW = "Workflow"
    DATA_PROCESSING = "Data Processing"
    NOTIFICATION = "Notification"
    INTEGRATION = "Integration"
    REPORTING = "Reporting"

class AutomationStatus(enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PAUSED = "Paused"
    ERROR = "Error"

class PredictionType(enum.Enum):
    SALES_FORECAST = "Sales Forecast"
    DEMAND_FORECAST = "Demand Forecast"
    CUSTOMER_CHURN = "Customer Churn"
    PRICE_OPTIMIZATION = "Price Optimization"
    INVENTORY_OPTIMIZATION = "Inventory Optimization"
    RISK_ASSESSMENT = "Risk Assessment"

# AI Model Models
class AIModel(BaseModel):
    """AI model model"""
    __tablename__ = 'ai_models'
    
    # Model Information
    model_name = db.Column(db.String(200), nullable=False)
    model_description = db.Column(db.Text)
    model_type = db.Column(db.Enum(AIModelType), nullable=False)
    model_version = db.Column(db.String(50), default='1.0.0')
    
    # Model Configuration
    model_config = db.Column(db.JSON)  # Model configuration
    training_config = db.Column(db.JSON)  # Training configuration
    hyperparameters = db.Column(db.JSON)  # Model hyperparameters
    
    # Model Status
    status = db.Column(db.Enum(ModelStatus), default=ModelStatus.TRAINING)
    training_progress = db.Column(db.Float, default=0.0)  # Percentage
    accuracy_score = db.Column(db.Float, default=0.0)
    precision_score = db.Column(db.Float, default=0.0)
    recall_score = db.Column(db.Float, default=0.0)
    f1_score = db.Column(db.Float, default=0.0)
    
    # Training Information
    training_start_time = db.Column(db.DateTime)
    training_end_time = db.Column(db.DateTime)
    training_duration = db.Column(db.Float, default=0.0)  # seconds
    training_data_size = db.Column(db.Integer, default=0)
    
    # Model Files
    model_file_path = db.Column(db.String(500))
    model_size = db.Column(db.Float, default=0.0)  # MB
    model_hash = db.Column(db.String(255))
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    model_predictions = relationship("AIPrediction", back_populates="ai_model")
    model_training_logs = relationship("AITrainingLog", back_populates="ai_model")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'model_name': self.model_name,
            'model_description': self.model_description,
            'model_type': self.model_type.value if self.model_type else None,
            'model_version': self.model_version,
            'model_config': self.model_config,
            'training_config': self.training_config,
            'hyperparameters': self.hyperparameters,
            'status': self.status.value if self.status else None,
            'training_progress': self.training_progress,
            'accuracy_score': self.accuracy_score,
            'precision_score': self.precision_score,
            'recall_score': self.recall_score,
            'f1_score': self.f1_score,
            'training_start_time': self.training_start_time.isoformat() if self.training_start_time else None,
            'training_end_time': self.training_end_time.isoformat() if self.training_end_time else None,
            'training_duration': self.training_duration,
            'training_data_size': self.training_data_size,
            'model_file_path': self.model_file_path,
            'model_size': self.model_size,
            'model_hash': self.model_hash,
            'company_id': self.company_id
        })
        return data

class AIPrediction(BaseModel):
    """AI prediction model"""
    __tablename__ = 'ai_predictions'
    
    # Prediction Information
    prediction_type = db.Column(db.Enum(PredictionType), nullable=False)
    prediction_value = db.Column(db.Float, default=0.0)
    confidence_score = db.Column(db.Float, default=0.0)
    prediction_data = db.Column(db.JSON)  # Input data for prediction
    
    # Model Association
    model_id = db.Column(db.Integer, db.ForeignKey('ai_models.id'), nullable=False)
    ai_model = relationship("AIModel", back_populates="model_predictions")
    
    # Prediction Details
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    actual_value = db.Column(db.Float)  # Actual value for comparison
    prediction_accuracy = db.Column(db.Float)  # Accuracy of prediction
    
    # Context Information
    entity_id = db.Column(db.String(100))  # ID of the entity being predicted
    entity_type = db.Column(db.String(100))  # Type of entity
    prediction_context = db.Column(db.JSON)  # Additional context
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'prediction_type': self.prediction_type.value if self.prediction_type else None,
            'prediction_value': self.prediction_value,
            'confidence_score': self.confidence_score,
            'prediction_data': self.prediction_data,
            'model_id': self.model_id,
            'prediction_date': self.prediction_date.isoformat() if self.prediction_date else None,
            'actual_value': self.actual_value,
            'prediction_accuracy': self.prediction_accuracy,
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'prediction_context': self.prediction_context,
            'company_id': self.company_id
        })
        return data

class AITrainingLog(BaseModel):
    """AI training log model"""
    __tablename__ = 'ai_training_logs'
    
    # Training Information
    epoch = db.Column(db.Integer, default=0)
    loss = db.Column(db.Float, default=0.0)
    accuracy = db.Column(db.Float, default=0.0)
    validation_loss = db.Column(db.Float, default=0.0)
    validation_accuracy = db.Column(db.Float, default=0.0)
    
    # Model Association
    model_id = db.Column(db.Integer, db.ForeignKey('ai_models.id'), nullable=False)
    ai_model = relationship("AIModel", back_populates="model_training_logs")
    
    # Training Details
    training_time = db.Column(db.DateTime, default=datetime.utcnow)
    training_duration = db.Column(db.Float, default=0.0)  # seconds
    memory_usage = db.Column(db.Float, default=0.0)  # MB
    gpu_usage = db.Column(db.Float, default=0.0)  # Percentage
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'epoch': self.epoch,
            'loss': self.loss,
            'accuracy': self.accuracy,
            'validation_loss': self.validation_loss,
            'validation_accuracy': self.validation_accuracy,
            'model_id': self.model_id,
            'training_time': self.training_time.isoformat() if self.training_time else None,
            'training_duration': self.training_duration,
            'memory_usage': self.memory_usage,
            'gpu_usage': self.gpu_usage,
            'company_id': self.company_id
        })
        return data

# Automation Models
class AutomationRule(BaseModel):
    """Automation rule model"""
    __tablename__ = 'automation_rules'
    
    # Rule Information
    rule_name = db.Column(db.String(200), nullable=False)
    rule_description = db.Column(db.Text)
    rule_type = db.Column(db.Enum(AutomationType), nullable=False)
    
    # Rule Configuration
    trigger_conditions = db.Column(db.JSON)  # Trigger conditions
    action_config = db.Column(db.JSON)  # Action configuration
    condition_config = db.Column(db.JSON)  # Additional conditions
    
    # Rule Status
    status = db.Column(db.Enum(AutomationStatus), default=AutomationStatus.ACTIVE)
    is_enabled = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=1)
    
    # Execution Information
    execution_count = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    failure_count = db.Column(db.Integer, default=0)
    last_execution = db.Column(db.DateTime)
    
    # Rule Settings
    max_executions = db.Column(db.Integer, default=0)  # 0 for unlimited
    execution_timeout = db.Column(db.Integer, default=300)  # seconds
    retry_count = db.Column(db.Integer, default=3)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    rule_executions = relationship("AutomationExecution", back_populates="automation_rule")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'rule_name': self.rule_name,
            'rule_description': self.rule_description,
            'rule_type': self.rule_type.value if self.rule_type else None,
            'trigger_conditions': self.trigger_conditions,
            'action_config': self.action_config,
            'condition_config': self.condition_config,
            'status': self.status.value if self.status else None,
            'is_enabled': self.is_enabled,
            'priority': self.priority,
            'execution_count': self.execution_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'max_executions': self.max_executions,
            'execution_timeout': self.execution_timeout,
            'retry_count': self.retry_count,
            'company_id': self.company_id
        })
        return data

class AutomationExecution(BaseModel):
    """Automation execution model"""
    __tablename__ = 'automation_executions'
    
    # Execution Information
    execution_id = db.Column(db.String(100), unique=True, nullable=False)
    execution_status = db.Column(db.String(50), default='Running')  # Running, Completed, Failed, Cancelled
    execution_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    execution_end_time = db.Column(db.DateTime)
    execution_duration = db.Column(db.Float, default=0.0)  # seconds
    
    # Rule Association
    rule_id = db.Column(db.Integer, db.ForeignKey('automation_rules.id'), nullable=False)
    automation_rule = relationship("AutomationRule", back_populates="rule_executions")
    
    # Execution Details
    trigger_data = db.Column(db.JSON)  # Data that triggered the rule
    execution_data = db.Column(db.JSON)  # Data used during execution
    result_data = db.Column(db.JSON)  # Result data
    error_message = db.Column(db.Text)
    
    # Execution Context
    executed_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    executed_by = relationship("Employee")
    execution_context = db.Column(db.JSON)  # Additional context
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'execution_id': self.execution_id,
            'execution_status': self.execution_status,
            'execution_start_time': self.execution_start_time.isoformat() if self.execution_start_time else None,
            'execution_end_time': self.execution_end_time.isoformat() if self.execution_end_time else None,
            'execution_duration': self.execution_duration,
            'rule_id': self.rule_id,
            'trigger_data': self.trigger_data,
            'execution_data': self.execution_data,
            'result_data': self.result_data,
            'error_message': self.error_message,
            'executed_by_id': self.executed_by_id,
            'execution_context': self.execution_context,
            'company_id': self.company_id
        })
        return data

# Machine Learning Pipeline Models
class MLPipeline(BaseModel):
    """Machine learning pipeline model"""
    __tablename__ = 'ml_pipelines'
    
    # Pipeline Information
    pipeline_name = db.Column(db.String(200), nullable=False)
    pipeline_description = db.Column(db.Text)
    pipeline_version = db.Column(db.String(50), default='1.0.0')
    
    # Pipeline Configuration
    pipeline_config = db.Column(db.JSON)  # Pipeline configuration
    data_sources = db.Column(db.JSON)  # Data sources
    preprocessing_steps = db.Column(db.JSON)  # Preprocessing steps
    model_steps = db.Column(db.JSON)  # Model steps
    postprocessing_steps = db.Column(db.JSON)  # Postprocessing steps
    
    # Pipeline Status
    status = db.Column(db.String(50), default='Draft')  # Draft, Active, Inactive, Failed
    is_active = db.Column(db.Boolean, default=False)
    
    # Execution Information
    execution_count = db.Column(db.Integer, default=0)
    last_execution = db.Column(db.DateTime)
    average_execution_time = db.Column(db.Float, default=0.0)  # seconds
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    pipeline_executions = relationship("MLPipelineExecution", back_populates="ml_pipeline")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'pipeline_name': self.pipeline_name,
            'pipeline_description': self.pipeline_description,
            'pipeline_version': self.pipeline_version,
            'pipeline_config': self.pipeline_config,
            'data_sources': self.data_sources,
            'preprocessing_steps': self.preprocessing_steps,
            'model_steps': self.model_steps,
            'postprocessing_steps': self.postprocessing_steps,
            'status': self.status,
            'is_active': self.is_active,
            'execution_count': self.execution_count,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'average_execution_time': self.average_execution_time,
            'company_id': self.company_id
        })
        return data

class MLPipelineExecution(BaseModel):
    """ML pipeline execution model"""
    __tablename__ = 'ml_pipeline_executions'
    
    # Execution Information
    execution_id = db.Column(db.String(100), unique=True, nullable=False)
    execution_status = db.Column(db.String(50), default='Running')  # Running, Completed, Failed, Cancelled
    execution_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    execution_end_time = db.Column(db.DateTime)
    execution_duration = db.Column(db.Float, default=0.0)  # seconds
    
    # Pipeline Association
    pipeline_id = db.Column(db.Integer, db.ForeignKey('ml_pipelines.id'), nullable=False)
    ml_pipeline = relationship("MLPipeline", back_populates="pipeline_executions")
    
    # Execution Details
    input_data = db.Column(db.JSON)  # Input data
    output_data = db.Column(db.JSON)  # Output data
    execution_logs = db.Column(db.JSON)  # Execution logs
    error_message = db.Column(db.Text)
    
    # Performance Metrics
    memory_usage = db.Column(db.Float, default=0.0)  # MB
    cpu_usage = db.Column(db.Float, default=0.0)  # Percentage
    gpu_usage = db.Column(db.Float, default=0.0)  # Percentage
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'execution_id': self.execution_id,
            'execution_status': self.execution_status,
            'execution_start_time': self.execution_start_time.isoformat() if self.execution_start_time else None,
            'execution_end_time': self.execution_end_time.isoformat() if self.execution_end_time else None,
            'execution_duration': self.execution_duration,
            'pipeline_id': self.pipeline_id,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'execution_logs': self.execution_logs,
            'error_message': self.error_message,
            'memory_usage': self.memory_usage,
            'cpu_usage': self.cpu_usage,
            'gpu_usage': self.gpu_usage,
            'company_id': self.company_id
        })
        return data

# AI Chatbot Models
class Chatbot(BaseModel):
    """Chatbot model"""
    __tablename__ = 'chatbots'
    
    # Chatbot Information
    chatbot_name = db.Column(db.String(200), nullable=False)
    chatbot_description = db.Column(db.Text)
    chatbot_type = db.Column(db.String(100), default='General')  # General, Customer Service, Sales, etc.
    
    # Chatbot Configuration
    chatbot_config = db.Column(db.JSON)  # Chatbot configuration
    knowledge_base = db.Column(db.JSON)  # Knowledge base
    response_templates = db.Column(db.JSON)  # Response templates
    conversation_flow = db.Column(db.JSON)  # Conversation flow
    
    # Chatbot Settings
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(10), default='en')
    
    # Performance Metrics
    total_conversations = db.Column(db.Integer, default=0)
    successful_conversations = db.Column(db.Integer, default=0)
    average_response_time = db.Column(db.Float, default=0.0)  # seconds
    user_satisfaction_score = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    chatbot_conversations = relationship("ChatbotConversation", back_populates="chatbot")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'chatbot_name': self.chatbot_name,
            'chatbot_description': self.chatbot_description,
            'chatbot_type': self.chatbot_type,
            'chatbot_config': self.chatbot_config,
            'knowledge_base': self.knowledge_base,
            'response_templates': self.response_templates,
            'conversation_flow': self.conversation_flow,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'language': self.language,
            'total_conversations': self.total_conversations,
            'successful_conversations': self.successful_conversations,
            'average_response_time': self.average_response_time,
            'user_satisfaction_score': self.user_satisfaction_score,
            'company_id': self.company_id
        })
        return data

class ChatbotConversation(BaseModel):
    """Chatbot conversation model"""
    __tablename__ = 'chatbot_conversations'
    
    # Conversation Information
    conversation_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    user = relationship("Employee")
    session_id = db.Column(db.String(100))
    
    # Chatbot Association
    chatbot_id = db.Column(db.Integer, db.ForeignKey('chatbots.id'), nullable=False)
    chatbot = relationship("Chatbot", back_populates="chatbot_conversations")
    
    # Conversation Details
    conversation_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    conversation_end_time = db.Column(db.DateTime)
    conversation_duration = db.Column(db.Float, default=0.0)  # seconds
    message_count = db.Column(db.Integer, default=0)
    
    # Conversation Status
    status = db.Column(db.String(50), default='Active')  # Active, Completed, Abandoned
    satisfaction_score = db.Column(db.Float)  # User satisfaction score
    resolution_status = db.Column(db.String(50))  # Resolved, Unresolved, Escalated
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'chatbot_id': self.chatbot_id,
            'conversation_start_time': self.conversation_start_time.isoformat() if self.conversation_start_time else None,
            'conversation_end_time': self.conversation_end_time.isoformat() if self.conversation_end_time else None,
            'conversation_duration': self.conversation_duration,
            'message_count': self.message_count,
            'status': self.status,
            'satisfaction_score': self.satisfaction_score,
            'resolution_status': self.resolution_status,
            'company_id': self.company_id
        })
        return data
