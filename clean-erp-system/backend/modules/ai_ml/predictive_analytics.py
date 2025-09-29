# Predictive Analytics System
# Advanced predictive analytics for sales forecasting, demand prediction, and business insights

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import pickle
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionType(Enum):
    SALES_FORECAST = "sales_forecast"
    DEMAND_PREDICTION = "demand_prediction"
    REVENUE_FORECAST = "revenue_forecast"
    CUSTOMER_CHURN = "customer_churn"
    INVENTORY_OPTIMIZATION = "inventory_optimization"
    PRICE_OPTIMIZATION = "price_optimization"
    MARKET_TREND = "market_trend"
    FINANCIAL_PERFORMANCE = "financial_performance"

class ModelType(Enum):
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    TIME_SERIES = "time_series"
    ENSEMBLE = "ensemble"

@dataclass
class PredictionResult:
    prediction_id: str
    model_id: str
    prediction_type: PredictionType
    input_data: Dict[str, Any]
    predictions: List[float]
    confidence_scores: List[float]
    accuracy_metrics: Dict[str, float]
    created_at: datetime
    valid_until: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MLModel:
    model_id: str
    name: str
    model_type: ModelType
    prediction_type: PredictionType
    features: List[str]
    target_variable: str
    model_object: Any = None
    scaler: Any = None
    encoder: Any = None
    accuracy_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_trained: bool = False
    training_data_size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

class PredictiveAnalytics:
    """
    Predictive Analytics System
    Advanced predictive analytics for business insights
    """
    
    def __init__(self):
        self.models: Dict[str, MLModel] = {}
        self.predictions: Dict[str, PredictionResult] = {}
        self.training_data: Dict[str, pd.DataFrame] = {}
        self.feature_importance: Dict[str, Dict[str, float]] = {}
        
        # Initialize default models
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize default ML models"""
        try:
            # Sales Forecasting Model
            sales_model = MLModel(
                model_id=str(uuid.uuid4()),
                name="Sales Forecasting Model",
                model_type=ModelType.RANDOM_FOREST,
                prediction_type=PredictionType.SALES_FORECAST,
                features=['historical_sales', 'seasonality', 'marketing_spend', 'economic_indicators'],
                target_variable='future_sales'
            )
            self.models[sales_model.model_id] = sales_model
            
            # Demand Prediction Model
            demand_model = MLModel(
                model_id=str(uuid.uuid4()),
                name="Demand Prediction Model",
                model_type=ModelType.GRADIENT_BOOSTING,
                prediction_type=PredictionType.DEMAND_PREDICTION,
                features=['product_category', 'price', 'promotions', 'competitor_activity'],
                target_variable='demand_quantity'
            )
            self.models[demand_model.model_id] = demand_model
            
            # Customer Churn Model
            churn_model = MLModel(
                model_id=str(uuid.uuid4()),
                name="Customer Churn Model",
                model_type=ModelType.NEURAL_NETWORK,
                prediction_type=PredictionType.CUSTOMER_CHURN,
                features=['customer_tenure', 'purchase_frequency', 'avg_order_value', 'support_tickets'],
                target_variable='churn_probability'
            )
            self.models[churn_model.model_id] = churn_model
            
            logger.info("Default ML models initialized")
            
        except Exception as e:
            logger.error(f"Error initializing default models: {str(e)}")
    
    def train_model(self, model_id: str, training_data: pd.DataFrame, 
                   target_column: str, test_size: float = 0.2) -> bool:
        """Train a machine learning model"""
        try:
            if model_id not in self.models:
                return False
            
            model = self.models[model_id]
            
            # Prepare data
            X = training_data[model.features]
            y = training_data[target_column]
            
            # Handle missing values
            X = X.fillna(X.mean())
            y = y.fillna(y.mean())
            
            # Encode categorical variables
            categorical_features = X.select_dtypes(include=['object']).columns
            for feature in categorical_features:
                le = LabelEncoder()
                X[feature] = le.fit_transform(X[feature].astype(str))
                model.encoder = le
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            model.scaler = scaler
            
            # Train model based on type
            if model.model_type == ModelType.LINEAR_REGRESSION:
                model.model_object = LinearRegression()
            elif model.model_type == ModelType.RANDOM_FOREST:
                model.model_object = RandomForestRegressor(n_estimators=100, random_state=42)
            elif model.model_type == ModelType.GRADIENT_BOOSTING:
                model.model_object = GradientBoostingRegressor(n_estimators=100, random_state=42)
            elif model.model_type == ModelType.NEURAL_NETWORK:
                model.model_object = MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42)
            
            # Train the model
            model.model_object.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.model_object.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            model.accuracy_score = r2
            model.is_trained = True
            model.training_data_size = len(training_data)
            model.updated_at = datetime.now()
            
            # Calculate feature importance
            if hasattr(model.model_object, 'feature_importances_'):
                feature_importance = dict(zip(model.features, model.model_object.feature_importances_))
                self.feature_importance[model_id] = feature_importance
            
            logger.info(f"Model {model_id} trained successfully. R² Score: {r2:.4f}")
            return True
            
        except Exception as e:
            logger.error(f"Error training model {model_id}: {str(e)}")
            return False
    
    def make_prediction(self, model_id: str, input_data: Dict[str, Any]) -> Optional[PredictionResult]:
        """Make a prediction using a trained model"""
        try:
            if model_id not in self.models:
                return None
            
            model = self.models[model_id]
            
            if not model.is_trained:
                return None
            
            # Prepare input data
            input_df = pd.DataFrame([input_data])
            
            # Handle categorical variables
            if model.encoder:
                categorical_features = input_df.select_dtypes(include=['object']).columns
                for feature in categorical_features:
                    if feature in model.features:
                        input_df[feature] = model.encoder.transform(input_df[feature].astype(str))
            
            # Select features
            X = input_df[model.features]
            
            # Handle missing values
            X = X.fillna(X.mean())
            
            # Scale features
            if model.scaler:
                X_scaled = model.scaler.transform(X)
            else:
                X_scaled = X.values
            
            # Make prediction
            prediction = model.model_object.predict(X_scaled)[0]
            
            # Calculate confidence score (simplified)
            confidence = min(max(model.accuracy_score, 0.0), 1.0)
            
            # Create prediction result
            result = PredictionResult(
                prediction_id=str(uuid.uuid4()),
                model_id=model_id,
                prediction_type=model.prediction_type,
                input_data=input_data,
                predictions=[float(prediction)],
                confidence_scores=[confidence],
                accuracy_metrics={
                    'r2_score': model.accuracy_score,
                    'mse': 0.0,  # Would calculate from validation data
                    'mae': 0.0   # Would calculate from validation data
                },
                created_at=datetime.now(),
                valid_until=datetime.now() + timedelta(days=30)
            )
            
            self.predictions[result.prediction_id] = result
            
            logger.info(f"Prediction made using model {model_id}: {prediction}")
            return result
            
        except Exception as e:
            logger.error(f"Error making prediction with model {model_id}: {str(e)}")
            return None
    
    def create_model(self, name: str, model_type: ModelType, prediction_type: PredictionType,
                    features: List[str], target_variable: str) -> MLModel:
        """Create a new ML model"""
        try:
            model = MLModel(
                model_id=str(uuid.uuid4()),
                name=name,
                model_type=model_type,
                prediction_type=prediction_type,
                features=features,
                target_variable=target_variable
            )
            
            self.models[model.model_id] = model
            
            logger.info(f"Model created: {model.model_id}")
            return model
            
        except Exception as e:
            logger.error(f"Error creating model: {str(e)}")
            raise
    
    def get_model(self, model_id: str) -> Optional[MLModel]:
        """Get a model by ID"""
        return self.models.get(model_id)
    
    def get_models_by_type(self, prediction_type: PredictionType) -> List[MLModel]:
        """Get models by prediction type"""
        return [
            model for model in self.models.values()
            if model.prediction_type == prediction_type
        ]
    
    def get_prediction(self, prediction_id: str) -> Optional[PredictionResult]:
        """Get a prediction by ID"""
        return self.predictions.get(prediction_id)
    
    def get_predictions_by_model(self, model_id: str) -> List[PredictionResult]:
        """Get all predictions for a model"""
        return [
            prediction for prediction in self.predictions.values()
            if prediction.model_id == model_id
        ]
    
    def get_feature_importance(self, model_id: str) -> Dict[str, float]:
        """Get feature importance for a model"""
        return self.feature_importance.get(model_id, {})
    
    def save_model(self, model_id: str, file_path: str) -> bool:
        """Save a trained model to file"""
        try:
            if model_id not in self.models:
                return False
            
            model = self.models[model_id]
            
            if not model.is_trained:
                return False
            
            # Save model
            model_data = {
                'model_object': model.model_object,
                'scaler': model.scaler,
                'encoder': model.encoder,
                'features': model.features,
                'target_variable': model.target_variable,
                'accuracy_score': model.accuracy_score,
                'model_type': model.model_type.value,
                'prediction_type': model.prediction_type.value
            }
            
            with open(file_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model {model_id} saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model {model_id}: {str(e)}")
            return False
    
    def load_model(self, model_id: str, file_path: str) -> bool:
        """Load a trained model from file"""
        try:
            with open(file_path, 'rb') as f:
                model_data = pickle.load(f)
            
            if model_id not in self.models:
                model = MLModel(
                    model_id=model_id,
                    name=f"Loaded Model {model_id}",
                    model_type=ModelType(model_data['model_type']),
                    prediction_type=PredictionType(model_data['prediction_type']),
                    features=model_data['features'],
                    target_variable=model_data['target_variable']
                )
                self.models[model_id] = model
            
            model = self.models[model_id]
            model.model_object = model_data['model_object']
            model.scaler = model_data['scaler']
            model.encoder = model_data['encoder']
            model.accuracy_score = model_data['accuracy_score']
            model.is_trained = True
            model.updated_at = datetime.now()
            
            logger.info(f"Model {model_id} loaded from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model {model_id}: {str(e)}")
            return False
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get predictive analytics insights"""
        try:
            total_models = len(self.models)
            trained_models = len([m for m in self.models.values() if m.is_trained])
            total_predictions = len(self.predictions)
            
            # Model performance summary
            model_performance = {}
            for model in self.models.values():
                if model.is_trained:
                    model_performance[model.name] = {
                        'accuracy': model.accuracy_score,
                        'training_size': model.training_data_size,
                        'last_updated': model.updated_at.isoformat()
                    }
            
            # Prediction trends
            recent_predictions = [
                p for p in self.predictions.values()
                if p.created_at > datetime.now() - timedelta(days=7)
            ]
            
            return {
                'total_models': total_models,
                'trained_models': trained_models,
                'total_predictions': total_predictions,
                'recent_predictions': len(recent_predictions),
                'model_performance': model_performance,
                'feature_importance': self.feature_importance
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}

# Global predictive analytics instance
predictive_analytics = PredictiveAnalytics()
