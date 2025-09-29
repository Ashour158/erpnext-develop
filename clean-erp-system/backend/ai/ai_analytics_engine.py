# AI Analytics Engine
# Advanced AI-powered analytics and machine learning capabilities

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import joblib
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsType(Enum):
    PREDICTIVE = "predictive"
    DESCRIPTIVE = "descriptive"
    PRESCRIPTIVE = "prescriptive"
    DIAGNOSTIC = "diagnostic"

class ModelType(Enum):
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"

@dataclass
class PredictionResult:
    prediction: float
    confidence: float
    model_accuracy: float
    features_importance: Dict[str, float]
    timestamp: datetime

@dataclass
class AnalyticsInsight:
    insight_type: str
    title: str
    description: str
    confidence: float
    impact: str
    recommendations: List[str]
    data_points: Dict[str, Any]
    timestamp: datetime

class AIAnalyticsEngine:
    """
    Advanced AI Analytics Engine for ERP System
    Provides predictive analytics, machine learning models, and intelligent insights
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_importance = {}
        self.model_accuracy = {}
        
    def train_sales_forecasting_model(self, sales_data: List[Dict]) -> Dict[str, Any]:
        """
        Train ML model for sales forecasting
        """
        try:
            # Prepare data
            df = pd.DataFrame(sales_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Feature engineering
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.month
            df['quarter'] = df['date'].dt.quarter
            df['day_of_week'] = df['date'].dt.dayofweek
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            
            # Create lag features
            df['sales_lag_1'] = df['sales_amount'].shift(1)
            df['sales_lag_7'] = df['sales_amount'].shift(7)
            df['sales_lag_30'] = df['sales_amount'].shift(30)
            
            # Rolling averages
            df['sales_ma_7'] = df['sales_amount'].rolling(window=7).mean()
            df['sales_ma_30'] = df['sales_amount'].rolling(window=30).mean()
            
            # Remove NaN values
            df = df.dropna()
            
            # Prepare features and target
            feature_columns = ['year', 'month', 'quarter', 'day_of_week', 'is_weekend',
                             'sales_lag_1', 'sales_lag_7', 'sales_lag_30', 'sales_ma_7', 'sales_ma_30']
            
            X = df[feature_columns]
            y = df['sales_amount']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train multiple models
            models = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'linear_regression': LinearRegression()
            }
            
            best_model = None
            best_score = float('inf')
            best_model_name = None
            
            for name, model in models.items():
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                mse = mean_squared_error(y_test, y_pred)
                
                if mse < best_score:
                    best_score = mse
                    best_model = model
                    best_model_name = name
            
            # Store best model
            self.models['sales_forecasting'] = best_model
            self.scalers['sales_forecasting'] = scaler
            self.model_accuracy['sales_forecasting'] = 1 - (best_score / y_test.var())
            
            # Feature importance
            if hasattr(best_model, 'feature_importances_'):
                self.feature_importance['sales_forecasting'] = dict(zip(feature_columns, best_model.feature_importances_))
            else:
                self.feature_importance['sales_forecasting'] = dict(zip(feature_columns, [0.1] * len(feature_columns)))
            
            logger.info(f"Sales forecasting model trained successfully. Best model: {best_model_name}, Accuracy: {self.model_accuracy['sales_forecasting']:.3f}")
            
            return {
                'model_name': best_model_name,
                'accuracy': self.model_accuracy['sales_forecasting'],
                'feature_importance': self.feature_importance['sales_forecasting'],
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Error training sales forecasting model: {str(e)}")
            raise
    
    def predict_sales(self, features: Dict[str, Any]) -> PredictionResult:
        """
        Predict sales using trained model
        """
        try:
            if 'sales_forecasting' not in self.models:
                raise ValueError("Sales forecasting model not trained")
            
            # Prepare features
            feature_vector = np.array([
                features.get('year', datetime.now().year),
                features.get('month', datetime.now().month),
                features.get('quarter', (datetime.now().month - 1) // 3 + 1),
                features.get('day_of_week', datetime.now().weekday()),
                features.get('is_weekend', 1 if datetime.now().weekday() >= 5 else 0),
                features.get('sales_lag_1', 0),
                features.get('sales_lag_7', 0),
                features.get('sales_lag_30', 0),
                features.get('sales_ma_7', 0),
                features.get('sales_ma_30', 0)
            ]).reshape(1, -1)
            
            # Scale features
            scaler = self.scalers['sales_forecasting']
            feature_vector_scaled = scaler.transform(feature_vector)
            
            # Make prediction
            model = self.models['sales_forecasting']
            prediction = model.predict(feature_vector_scaled)[0]
            
            # Calculate confidence (simplified)
            confidence = min(0.95, max(0.5, self.model_accuracy['sales_forecasting']))
            
            return PredictionResult(
                prediction=float(prediction),
                confidence=confidence,
                model_accuracy=self.model_accuracy['sales_forecasting'],
                features_importance=self.feature_importance['sales_forecasting'],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error predicting sales: {str(e)}")
            raise
    
    def train_customer_churn_model(self, customer_data: List[Dict]) -> Dict[str, Any]:
        """
        Train ML model for customer churn prediction
        """
        try:
            # Prepare data
            df = pd.DataFrame(customer_data)
            
            # Feature engineering
            df['days_since_last_purchase'] = (datetime.now() - pd.to_datetime(df['last_purchase_date'])).dt.days
            df['total_orders'] = df['total_orders'].fillna(0)
            df['avg_order_value'] = df['total_spent'] / df['total_orders'].replace(0, 1)
            df['is_vip'] = (df['total_spent'] > df['total_spent'].quantile(0.8)).astype(int)
            
            # Prepare features
            feature_columns = ['total_orders', 'total_spent', 'avg_order_value', 
                             'days_since_last_purchase', 'is_vip']
            
            X = df[feature_columns]
            y = df['churned'].astype(int)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = LogisticRegression(random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Store model
            self.models['customer_churn'] = model
            self.scalers['customer_churn'] = scaler
            self.model_accuracy['customer_churn'] = accuracy
            
            logger.info(f"Customer churn model trained successfully. Accuracy: {accuracy:.3f}")
            
            return {
                'accuracy': accuracy,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'classification_report': classification_report(y_test, y_pred, output_dict=True)
            }
            
        except Exception as e:
            logger.error(f"Error training customer churn model: {str(e)}")
            raise
    
    def predict_customer_churn(self, customer_features: Dict[str, Any]) -> PredictionResult:
        """
        Predict customer churn probability
        """
        try:
            if 'customer_churn' not in self.models:
                raise ValueError("Customer churn model not trained")
            
            # Prepare features
            feature_vector = np.array([
                customer_features.get('total_orders', 0),
                customer_features.get('total_spent', 0),
                customer_features.get('avg_order_value', 0),
                customer_features.get('days_since_last_purchase', 0),
                customer_features.get('is_vip', 0)
            ]).reshape(1, -1)
            
            # Scale features
            scaler = self.scalers['customer_churn']
            feature_vector_scaled = scaler.transform(feature_vector)
            
            # Make prediction
            model = self.models['customer_churn']
            churn_probability = model.predict_proba(feature_vector_scaled)[0][1]
            
            return PredictionResult(
                prediction=float(churn_probability),
                confidence=float(churn_probability),
                model_accuracy=self.model_accuracy['customer_churn'],
                features_importance={},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error predicting customer churn: {str(e)}")
            raise
    
    def generate_analytics_insights(self, data: Dict[str, Any]) -> List[AnalyticsInsight]:
        """
        Generate intelligent analytics insights
        """
        insights = []
        
        try:
            # Sales trend analysis
            if 'sales_data' in data:
                sales_df = pd.DataFrame(data['sales_data'])
                sales_df['date'] = pd.to_datetime(sales_df['date'])
                
                # Calculate growth rate
                current_period = sales_df['sales_amount'].sum()
                previous_period = sales_df['sales_amount'].shift(1).sum()
                growth_rate = ((current_period - previous_period) / previous_period * 100) if previous_period > 0 else 0
                
                if growth_rate > 10:
                    insights.append(AnalyticsInsight(
                        insight_type="positive_trend",
                        title="Strong Sales Growth",
                        description=f"Sales have grown by {growth_rate:.1f}% compared to previous period",
                        confidence=0.85,
                        impact="high",
                        recommendations=[
                            "Consider expanding marketing efforts",
                            "Increase inventory for high-demand products",
                            "Invest in customer acquisition"
                        ],
                        data_points={"growth_rate": growth_rate, "current_sales": current_period},
                        timestamp=datetime.now()
                    ))
                elif growth_rate < -10:
                    insights.append(AnalyticsInsight(
                        insight_type="negative_trend",
                        title="Sales Decline Alert",
                        description=f"Sales have declined by {abs(growth_rate):.1f}% compared to previous period",
                        confidence=0.90,
                        impact="high",
                        recommendations=[
                            "Investigate market conditions",
                            "Review pricing strategy",
                            "Analyze competitor activities",
                            "Consider promotional campaigns"
                        ],
                        data_points={"growth_rate": growth_rate, "current_sales": current_period},
                        timestamp=datetime.now()
                    ))
            
            # Customer segmentation insights
            if 'customer_data' in data:
                customer_df = pd.DataFrame(data['customer_data'])
                
                # High-value customer analysis
                high_value_customers = customer_df[customer_df['total_spent'] > customer_df['total_spent'].quantile(0.8)]
                
                if len(high_value_customers) > 0:
                    insights.append(AnalyticsInsight(
                        insight_type="customer_segmentation",
                        title="High-Value Customer Segment",
                        description=f"Identified {len(high_value_customers)} high-value customers representing {high_value_customers['total_spent'].sum():.0f} in revenue",
                        confidence=0.80,
                        impact="medium",
                        recommendations=[
                            "Implement VIP customer program",
                            "Provide personalized service",
                            "Offer exclusive products/services",
                            "Increase retention efforts"
                        ],
                        data_points={"high_value_count": len(high_value_customers), "revenue": high_value_customers['total_spent'].sum()},
                        timestamp=datetime.now()
                    ))
            
            # Inventory optimization insights
            if 'inventory_data' in data:
                inventory_df = pd.DataFrame(data['inventory_data'])
                
                # Low stock analysis
                low_stock_items = inventory_df[inventory_df['current_stock'] < inventory_df['min_stock_level']]
                
                if len(low_stock_items) > 0:
                    insights.append(AnalyticsInsight(
                        insight_type="inventory_alert",
                        title="Low Stock Alert",
                        description=f"{len(low_stock_items)} items are below minimum stock levels",
                        confidence=0.95,
                        impact="high",
                        recommendations=[
                            "Place urgent reorder for low stock items",
                            "Review minimum stock levels",
                            "Implement automated reorder system",
                            "Consider supplier lead time optimization"
                        ],
                        data_points={"low_stock_count": len(low_stock_items), "items": low_stock_items['item_name'].tolist()},
                        timestamp=datetime.now()
                    ))
            
            logger.info(f"Generated {len(insights)} analytics insights")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating analytics insights: {str(e)}")
            return []
    
    def detect_anomalies(self, data: List[Dict], threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detect anomalies in data using statistical methods
        """
        try:
            df = pd.DataFrame(data)
            anomalies = []
            
            # Numerical columns for anomaly detection
            numerical_columns = df.select_dtypes(include=[np.number]).columns
            
            for column in numerical_columns:
                if column in df.columns:
                    values = df[column].dropna()
                    if len(values) > 0:
                        mean = values.mean()
                        std = values.std()
                        
                        # Z-score based anomaly detection
                        z_scores = np.abs((values - mean) / std)
                        anomaly_indices = z_scores > threshold
                        
                        if anomaly_indices.any():
                            anomaly_data = df[anomaly_indices]
                            for idx, row in anomaly_data.iterrows():
                                anomalies.append({
                                    'column': column,
                                    'value': row[column],
                                    'z_score': z_scores[idx],
                                    'row_index': idx,
                                    'anomaly_type': 'statistical_outlier',
                                    'severity': 'high' if z_scores[idx] > 3 else 'medium',
                                    'timestamp': datetime.now()
                                })
            
            logger.info(f"Detected {len(anomalies)} anomalies")
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return []
    
    def save_models(self, filepath: str) -> bool:
        """
        Save trained models to disk
        """
        try:
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'encoders': self.encoders,
                'feature_importance': self.feature_importance,
                'model_accuracy': self.model_accuracy
            }
            joblib.dump(model_data, filepath)
            logger.info(f"Models saved successfully to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            return False
    
    def load_models(self, filepath: str) -> bool:
        """
        Load trained models from disk
        """
        try:
            model_data = joblib.load(filepath)
            self.models = model_data['models']
            self.scalers = model_data['scalers']
            self.encoders = model_data['encoders']
            self.feature_importance = model_data['feature_importance']
            self.model_accuracy = model_data['model_accuracy']
            logger.info(f"Models loaded successfully from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return False

# Global AI Analytics Engine instance
ai_analytics_engine = AIAnalyticsEngine()
