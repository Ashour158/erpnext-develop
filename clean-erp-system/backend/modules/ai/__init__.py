# AI Module - Complete AI Analytics and Smart Features
# Advanced AI capabilities without Frappe dependencies

from flask import Blueprint
from .models import (
    AIAnalysis, AIModel, AITraining, AIPrediction, AIRecommendation,
    AIConversation, AIInsight, AIPattern, AIAlert
)
from .api import ai_api

# Create AI blueprint
ai_bp = Blueprint('ai', __name__)

# Register API routes
ai_bp.register_blueprint(ai_api, url_prefix='')

# Module information
AI_MODULE_INFO = {
    'name': 'AI Analytics',
    'version': '1.0.0',
    'description': 'Complete AI Analytics and Smart Features System',
    'features': [
        'Predictive Analytics',
        'Machine Learning Models',
        'Natural Language Processing',
        'Computer Vision',
        'Recommendation Engine',
        'Anomaly Detection',
        'Sentiment Analysis',
        'Chatbot & Virtual Assistant',
        'Automated Insights',
        'Pattern Recognition',
        'Smart Alerts',
        'Data Mining'
    ]
}
