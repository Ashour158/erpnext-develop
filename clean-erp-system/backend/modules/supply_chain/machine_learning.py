# Machine Learning for Supply Chain
# Advanced AI for demand forecasting and optimization

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum
import json

class MLModelType(enum.Enum):
    DEMAND_FORECASTING = "demand_forecasting"
    INVENTORY_OPTIMIZATION = "inventory_optimization"
    SUPPLIER_PERFORMANCE = "supplier_performance"
    QUALITY_PREDICTION = "quality_prediction"
    PRICE_PREDICTION = "price_prediction"
    ROUTE_OPTIMIZATION = "route_optimization"
    ANOMALY_DETECTION = "anomaly_detection"
    RISK_ASSESSMENT = "risk_assessment"
    CUSTOMER_BEHAVIOR = "customer_behavior"
    MAINTENANCE_PREDICTION = "maintenance_prediction"

class MLAlgorithm(enum.Enum):
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    LSTM = "lstm"
    ARIMA = "arima"
    SARIMA = "sarima"
    PROPHET = "prophet"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    SVM = "svm"
    K_MEANS = "k_means"
    DBSCAN = "dbscan"
    ISOLATION_FOREST = "isolation_forest"

class ModelStatus(enum.Enum):
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    RETIRED = "retired"
    FAILED = "failed"

class PredictionStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# ML Models
class MLModel(Base):
    __tablename__ = 'ml_models'
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(255), nullable=False)
    model_type = Column(Enum(MLModelType), nullable=False)
    algorithm = Column(Enum(MLAlgorithm), nullable=False)
    version = Column(String(50), default='1.0')
    
    # Model configuration
    model_config = Column(JSON)  # Model-specific configuration
    hyperparameters = Column(JSON)  # Model hyperparameters
    feature_columns = Column(JSON)  # Input feature columns
    target_column = Column(String(100))  # Target variable column
    
    # Model files
    model_file_path = Column(String(500))  # Path to saved model file
    model_size = Column(Integer)  # Model file size in bytes
    model_format = Column(String(20))  # pickle, joblib, h5, pkl
    
    # Training data
    training_data_path = Column(String(500))
    training_data_size = Column(Integer)  # Number of training samples
    training_period_start = Column(DateTime)
    training_period_end = Column(DateTime)
    
    # Model performance
    accuracy_score = Column(Float)  # Overall accuracy
    precision_score = Column(Float)
    recall_score = Column(Float)
    f1_score = Column(Float)
    rmse = Column(Float)  # Root Mean Square Error
    mae = Column(Float)  # Mean Absolute Error
    r2_score = Column(Float)  # R-squared score
    
    # Model status
    status = Column(Enum(ModelStatus), default=ModelStatus.TRAINING)
    is_active = Column(Boolean, default=True)
    deployed_at = Column(DateTime)
    retired_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")
    predictions = relationship("MLPrediction", back_populates="model")
    training_runs = relationship("MLTrainingRun", back_populates="model")

# ML Training Runs
class MLTrainingRun(Base):
    __tablename__ = 'ml_training_runs'
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey('ml_models.id'), nullable=False)
    run_name = Column(String(255), nullable=False)
    
    # Training configuration
    training_config = Column(JSON)  # Training-specific configuration
    data_split = Column(JSON)  # Train/validation/test split
    cross_validation_folds = Column(Integer, default=5)
    
    # Training process
    training_started = Column(DateTime, default=datetime.utcnow)
    training_completed = Column(DateTime)
    training_duration = Column(Integer)  # Duration in seconds
    epochs = Column(Integer)  # Number of training epochs
    batch_size = Column(Integer)
    learning_rate = Column(Float)
    
    # Training results
    training_accuracy = Column(Float)
    validation_accuracy = Column(Float)
    training_loss = Column(Float)
    validation_loss = Column(Float)
    best_epoch = Column(Integer)
    
    # Status
    status = Column(String(20), default='running')  # running, completed, failed, cancelled
    error_message = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    model = relationship("MLModel", back_populates="training_runs")
    creator = relationship("User")

# ML Predictions
class MLPrediction(Base):
    __tablename__ = 'ml_predictions'
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey('ml_models.id'), nullable=False)
    prediction_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Prediction details
    prediction_type = Column(Enum(MLModelType), nullable=False)
    input_data = Column(JSON, nullable=False)  # Input features
    prediction_result = Column(JSON, nullable=False)  # Prediction output
    confidence_score = Column(Float)  # Prediction confidence (0-1)
    prediction_interval = Column(JSON)  # Confidence interval
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    lot_id = Column(Integer, ForeignKey('item_lots.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    
    # Prediction metadata
    prediction_date = Column(DateTime, default=datetime.utcnow)
    prediction_horizon = Column(Integer)  # Days ahead for forecasting
    status = Column(Enum(PredictionStatus), default=PredictionStatus.PENDING)
    
    # Validation
    actual_value = Column(Float)  # Actual value for validation
    actual_date = Column(DateTime)  # Date when actual value was recorded
    prediction_error = Column(Float)  # Difference between prediction and actual
    is_validated = Column(Boolean, default=False)
    validated_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    model = relationship("MLModel", back_populates="predictions")
    item = relationship("EnhancedItem")
    batch = relationship("ItemBatch")
    lot = relationship("ItemLot")
    supplier = relationship("Supplier")
    customer = relationship("Customer")

# ML Data Sources
class MLDataSource(Base):
    __tablename__ = 'ml_data_sources'
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # database, api, file, stream
    source_config = Column(JSON, nullable=False)  # Source-specific configuration
    
    # Data details
    data_schema = Column(JSON)  # Data schema definition
    update_frequency = Column(String(20), default='daily')  # real_time, hourly, daily, weekly
    last_updated = Column(DateTime)
    next_update = Column(DateTime)
    
    # Data quality
    data_quality_score = Column(Float)  # 0-1 data quality score
    completeness_score = Column(Float)  # 0-1 data completeness
    accuracy_score = Column(Float)  # 0-1 data accuracy
    consistency_score = Column(Float)  # 0-1 data consistency
    
    # Status
    is_active = Column(Boolean, default=True)
    is_connected = Column(Boolean, default=False)
    last_connection = Column(DateTime)
    connection_errors = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")
    datasets = relationship("MLDataset", back_populates="data_source")

# ML Datasets
class MLDataset(Base):
    __tablename__ = 'ml_datasets'
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_name = Column(String(255), nullable=False)
    data_source_id = Column(Integer, ForeignKey('ml_data_sources.id'), nullable=False)
    
    # Dataset details
    dataset_type = Column(String(50), nullable=False)  # training, validation, test, production
    dataset_config = Column(JSON)  # Dataset-specific configuration
    data_filters = Column(JSON)  # Data filtering criteria
    feature_engineering = Column(JSON)  # Feature engineering steps
    
    # Dataset statistics
    row_count = Column(Integer)
    column_count = Column(Integer)
    missing_values = Column(Integer)
    duplicate_rows = Column(Integer)
    data_quality_score = Column(Float)
    
    # Dataset files
    dataset_file_path = Column(String(500))
    dataset_size = Column(Integer)  # File size in bytes
    dataset_format = Column(String(20))  # csv, parquet, json, hdf5
    
    # Status
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    processing_errors = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    data_source = relationship("MLDataSource", back_populates="datasets")
    creator = relationship("User")

# ML Feature Engineering
class MLFeature(Base):
    __tablename__ = 'ml_features'
    
    id = Column(Integer, primary_key=True, index=True)
    feature_name = Column(String(255), nullable=False)
    feature_type = Column(String(50), nullable=False)  # numerical, categorical, datetime, text
    feature_category = Column(String(50))  # demand, inventory, supplier, quality, price
    
    # Feature definition
    feature_definition = Column(Text)
    feature_formula = Column(Text)  # Mathematical formula for derived features
    feature_source = Column(String(100))  # Source table/column
    feature_transformation = Column(JSON)  # Transformation steps
    
    # Feature statistics
    mean_value = Column(Float)
    median_value = Column(Float)
    std_deviation = Column(Float)
    min_value = Column(Float)
    max_value = Column(Float)
    null_count = Column(Integer)
    unique_count = Column(Integer)
    
    # Feature importance
    importance_score = Column(Float)  # Feature importance score
    correlation_score = Column(Float)  # Correlation with target
    mutual_information = Column(Float)  # Mutual information score
    
    # Status
    is_active = Column(Boolean, default=True)
    is_engineered = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# ML Model Performance
class MLModelPerformance(Base):
    __tablename__ = 'ml_model_performance'
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey('ml_models.id'), nullable=False)
    performance_date = Column(DateTime, default=datetime.utcnow)
    
    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    rmse = Column(Float)
    mae = Column(Float)
    r2_score = Column(Float)
    mape = Column(Float)  # Mean Absolute Percentage Error
    
    # Model drift detection
    prediction_drift = Column(Float)  # Prediction drift score
    feature_drift = Column(Float)  # Feature drift score
    data_drift = Column(Float)  # Data drift score
    
    # Performance context
    test_data_size = Column(Integer)
    validation_period_start = Column(DateTime)
    validation_period_end = Column(DateTime)
    
    # Status
    performance_status = Column(String(20), default='good')  # good, warning, poor, critical
    needs_retraining = Column(Boolean, default=False)
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    calculated_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    model = relationship("MLModel")
    calculator = relationship("User")

# ML Model Deployment
class MLModelDeployment(Base):
    __tablename__ = 'ml_model_deployments'
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey('ml_models.id'), nullable=False)
    deployment_name = Column(String(255), nullable=False)
    
    # Deployment configuration
    deployment_config = Column(JSON)  # Deployment-specific configuration
    endpoint_url = Column(String(500))  # Model serving endpoint
    api_key = Column(String(100))  # API authentication key
    
    # Deployment environment
    environment = Column(String(50), default='production')  # development, staging, production
    deployment_type = Column(String(50), default='api')  # api, batch, stream, edge
    
    # Performance monitoring
    request_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    average_response_time = Column(Float, default=0.0)
    throughput = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    deployed_at = Column(DateTime, default=datetime.utcnow)
    last_health_check = Column(DateTime)
    health_status = Column(String(20), default='healthy')  # healthy, warning, error, offline
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    model = relationship("MLModel")
    creator = relationship("User")

# ML Model A/B Testing
class MLModelABTest(Base):
    __tablename__ = 'ml_model_ab_tests'
    
    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String(255), nullable=False)
    test_description = Column(Text)
    
    # Test configuration
    control_model_id = Column(Integer, ForeignKey('ml_models.id'), nullable=False)
    treatment_model_id = Column(Integer, ForeignKey('ml_models.id'), nullable=False)
    traffic_split = Column(Float, default=0.5)  # Traffic split ratio
    
    # Test metrics
    primary_metric = Column(String(100), nullable=False)  # Primary metric to compare
    secondary_metrics = Column(JSON)  # Additional metrics to track
    minimum_sample_size = Column(Integer, default=1000)
    confidence_level = Column(Float, default=0.95)
    
    # Test status
    status = Column(String(20), default='draft')  # draft, running, completed, cancelled
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    test_duration = Column(Integer)  # Duration in days
    
    # Test results
    control_metric_value = Column(Float)
    treatment_metric_value = Column(Float)
    statistical_significance = Column(Float)
    p_value = Column(Float)
    confidence_interval = Column(JSON)
    winner = Column(String(20))  # control, treatment, inconclusive
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    control_model = relationship("MLModel", foreign_keys=[control_model_id])
    treatment_model = relationship("MLModel", foreign_keys=[treatment_model_id])
    creator = relationship("User")

# ML Model Monitoring
class MLModelMonitoring(Base):
    __tablename__ = 'ml_model_monitoring'
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey('ml_models.id'), nullable=False)
    monitoring_date = Column(DateTime, default=datetime.utcnow)
    
    # Monitoring metrics
    prediction_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    error_rate = Column(Float, default=0.0)
    average_confidence = Column(Float, default=0.0)
    data_quality_score = Column(Float, default=0.0)
    
    # Drift detection
    input_drift = Column(Float, default=0.0)
    output_drift = Column(Float, default=0.0)
    concept_drift = Column(Float, default=0.0)
    
    # Performance metrics
    average_prediction_time = Column(Float, default=0.0)
    throughput = Column(Float, default=0.0)
    latency_p95 = Column(Float, default=0.0)
    latency_p99 = Column(Float, default=0.0)
    
    # Alerts
    alert_count = Column(Integer, default=0)
    critical_alerts = Column(Integer, default=0)
    warning_alerts = Column(Integer, default=0)
    
    # Status
    monitoring_status = Column(String(20), default='normal')  # normal, warning, critical
    requires_attention = Column(Boolean, default=False)
    
    # Metadata
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    model = relationship("MLModel")
