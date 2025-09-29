# AI API Endpoints
# REST API for AI Analytics Engine, Intelligent Automation, and Natural Language Interface

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

from .ai_analytics_engine import ai_analytics_engine, PredictionResult, AnalyticsInsight
from .intelligent_automation import intelligent_automation_engine, AutomationRule, AutomationExecution
from .natural_language_interface import natural_language_interface, Intent, VoiceCommand

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create AI Blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a real implementation, this would verify JWT tokens
        # For now, we'll just check for a user_id in headers
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# AI ANALYTICS ENGINE ENDPOINTS
# =============================================================================

@ai_bp.route('/analytics/train-sales-model', methods=['POST'])
@require_auth
def train_sales_forecasting_model():
    """Train sales forecasting ML model"""
    try:
        data = request.get_json()
        sales_data = data.get('sales_data', [])
        
        if not sales_data:
            return jsonify({'error': 'Sales data is required'}), 400
        
        result = ai_analytics_engine.train_sales_forecasting_model(sales_data)
        
        return jsonify({
            'success': True,
            'message': 'Sales forecasting model trained successfully',
            'result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error training sales model: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/analytics/predict-sales', methods=['POST'])
@require_auth
def predict_sales():
    """Predict sales using trained model"""
    try:
        data = request.get_json()
        features = data.get('features', {})
        
        if not features:
            return jsonify({'error': 'Features are required'}), 400
        
        prediction = ai_analytics_engine.predict_sales(features)
        
        return jsonify({
            'success': True,
            'prediction': {
                'value': prediction.prediction,
                'confidence': prediction.confidence,
                'model_accuracy': prediction.model_accuracy,
                'features_importance': prediction.features_importance,
                'timestamp': prediction.timestamp.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error predicting sales: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/analytics/train-churn-model', methods=['POST'])
@require_auth
def train_customer_churn_model():
    """Train customer churn prediction model"""
    try:
        data = request.get_json()
        customer_data = data.get('customer_data', [])
        
        if not customer_data:
            return jsonify({'error': 'Customer data is required'}), 400
        
        result = ai_analytics_engine.train_customer_churn_model(customer_data)
        
        return jsonify({
            'success': True,
            'message': 'Customer churn model trained successfully',
            'result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error training churn model: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/analytics/predict-churn', methods=['POST'])
@require_auth
def predict_customer_churn():
    """Predict customer churn probability"""
    try:
        data = request.get_json()
        customer_features = data.get('customer_features', {})
        
        if not customer_features:
            return jsonify({'error': 'Customer features are required'}), 400
        
        prediction = ai_analytics_engine.predict_customer_churn(customer_features)
        
        return jsonify({
            'success': True,
            'prediction': {
                'churn_probability': prediction.prediction,
                'confidence': prediction.confidence,
                'model_accuracy': prediction.model_accuracy,
                'timestamp': prediction.timestamp.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error predicting churn: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/analytics/insights', methods=['POST'])
@require_auth
def generate_analytics_insights():
    """Generate AI-powered analytics insights"""
    try:
        data = request.get_json()
        
        insights = ai_analytics_engine.generate_analytics_insights(data)
        
        # Convert insights to serializable format
        insights_data = []
        for insight in insights:
            insights_data.append({
                'insight_type': insight.insight_type,
                'title': insight.title,
                'description': insight.description,
                'confidence': insight.confidence,
                'impact': insight.impact,
                'recommendations': insight.recommendations,
                'data_points': insight.data_points,
                'timestamp': insight.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'insights': insights_data,
            'count': len(insights_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/analytics/detect-anomalies', methods=['POST'])
@require_auth
def detect_anomalies():
    """Detect anomalies in data"""
    try:
        data = request.get_json()
        data_points = data.get('data', [])
        threshold = data.get('threshold', 2.0)
        
        if not data_points:
            return jsonify({'error': 'Data points are required'}), 400
        
        anomalies = ai_analytics_engine.detect_anomalies(data_points, threshold)
        
        return jsonify({
            'success': True,
            'anomalies': anomalies,
            'count': len(anomalies)
        }), 200
        
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# INTELLIGENT AUTOMATION ENDPOINTS
# =============================================================================

@ai_bp.route('/automation/rules', methods=['POST'])
@require_auth
def create_automation_rule():
    """Create a new automation rule"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'description', 'trigger', 'conditions', 'actions']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        rule = intelligent_automation_engine.create_automation_rule(
            name=data['name'],
            description=data['description'],
            trigger=data['trigger'],
            conditions=data['conditions'],
            actions=data['actions'],
            created_by=request.headers.get('X-User-ID', 'system'),
            priority=data.get('priority', 1),
            metadata=data.get('metadata', {})
        )
        
        return jsonify({
            'success': True,
            'message': 'Automation rule created successfully',
            'rule': {
                'id': rule.id,
                'name': rule.name,
                'description': rule.description,
                'trigger': rule.trigger.value,
                'status': rule.status.value,
                'created_at': rule.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating automation rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/automation/rules/<rule_id>', methods=['PUT'])
@require_auth
def update_automation_rule(rule_id):
    """Update an automation rule"""
    try:
        data = request.get_json()
        
        success = intelligent_automation_engine.update_automation_rule(rule_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Automation rule updated successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to update automation rule'}), 400
            
    except Exception as e:
        logger.error(f"Error updating automation rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/automation/rules/<rule_id>', methods=['DELETE'])
@require_auth
def delete_automation_rule(rule_id):
    """Delete an automation rule"""
    try:
        success = intelligent_automation_engine.delete_automation_rule(rule_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Automation rule deleted successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to delete automation rule'}), 400
            
    except Exception as e:
        logger.error(f"Error deleting automation rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/automation/rules/<rule_id>/execute', methods=['POST'])
@require_auth
def execute_automation_rule(rule_id):
    """Execute an automation rule"""
    try:
        data = request.get_json()
        context_data = data.get('context_data', {})
        
        execution = intelligent_automation_engine.execute_automation_rule(rule_id, context_data)
        
        return jsonify({
            'success': True,
            'execution': {
                'id': execution.id,
                'rule_id': execution.rule_id,
                'status': execution.status.value,
                'started_at': execution.started_at.isoformat(),
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'error_message': execution.error_message,
                'results': execution.results
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error executing automation rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/automation/analyze-process', methods=['POST'])
@require_auth
def analyze_process_efficiency():
    """Analyze process efficiency"""
    try:
        data = request.get_json()
        
        insight = intelligent_automation_engine.analyze_process_efficiency(data)
        
        return jsonify({
            'success': True,
            'insight': {
                'process_id': insight.process_id,
                'process_name': insight.process_name,
                'efficiency_score': insight.efficiency_score,
                'bottleneck_steps': insight.bottleneck_steps,
                'optimization_suggestions': insight.optimization_suggestions,
                'time_savings_potential': insight.time_savings_potential,
                'cost_savings_potential': insight.cost_savings_potential,
                'confidence': insight.confidence,
                'timestamp': insight.timestamp.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing process: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/automation/recommendations', methods=['POST'])
@require_auth
def get_automation_recommendations():
    """Get AI-powered automation recommendations"""
    try:
        data = request.get_json()
        
        recommendations = intelligent_automation_engine.get_automation_recommendations(data)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/automation/statistics', methods=['GET'])
@require_auth
def get_automation_statistics():
    """Get automation statistics"""
    try:
        stats = intelligent_automation_engine.get_automation_rule_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# NATURAL LANGUAGE INTERFACE ENDPOINTS
# =============================================================================

@ai_bp.route('/nlp/process', methods=['POST'])
@require_auth
def process_natural_language():
    """Process natural language input"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        user_id = request.headers.get('X-User-ID')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        intent = natural_language_interface.process_natural_language(text, user_id)
        
        return jsonify({
            'success': True,
            'intent': {
                'type': intent.intent_type.value,
                'confidence': intent.confidence,
                'entities': intent.entities,
                'parameters': intent.parameters,
                'original_text': intent.original_text,
                'processed_text': intent.processed_text
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing natural language: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/nlp/voice-command', methods=['POST'])
@require_auth
def execute_voice_command():
    """Execute a voice command"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        user_id = request.headers.get('X-User-ID')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        command = natural_language_interface.execute_voice_command(text, user_id)
        
        return jsonify({
            'success': True,
            'command': {
                'id': command.command_id,
                'text': command.text,
                'intent': {
                    'type': command.intent.intent_type.value,
                    'confidence': command.intent.confidence,
                    'entities': command.intent.entities,
                    'parameters': command.intent.parameters
                },
                'executed': command.executed,
                'result': command.result,
                'error_message': command.error_message
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error executing voice command: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/nlp/chat', methods=['POST'])
@require_auth
def chat_with_data():
    """Chat interface for data interaction"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = request.headers.get('X-User-ID')
        context = data.get('context', {})
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        response = natural_language_interface.chat_with_data(message, user_id, context)
        
        return jsonify({
            'success': True,
            'response': response
        }), 200
        
    except Exception as e:
        logger.error(f"Error in chat interface: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/nlp/help', methods=['GET'])
@require_auth
def get_voice_commands_help():
    """Get help for voice commands"""
    try:
        help_data = natural_language_interface.get_voice_commands_help()
        
        return jsonify({
            'success': True,
            'help': help_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting help: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# AI SYSTEM STATUS ENDPOINTS
# =============================================================================

@ai_bp.route('/status', methods=['GET'])
@require_auth
def get_ai_system_status():
    """Get AI system status"""
    try:
        status = {
            'analytics_engine': {
                'status': 'active',
                'models_trained': len(ai_analytics_engine.models),
                'available_models': list(ai_analytics_engine.models.keys())
            },
            'automation_engine': {
                'status': 'active',
                'total_rules': len(intelligent_automation_engine.automation_rules),
                'active_rules': len([r for r in intelligent_automation_engine.automation_rules.values() if r.status.value == 'active']),
                'total_executions': len(intelligent_automation_engine.execution_history)
            },
            'nlp_interface': {
                'status': 'active',
                'supported_intents': ['query', 'command', 'report', 'analysis', 'help'],
                'supported_entities': ['date', 'number', 'currency', 'email', 'phone']
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'status': status
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting AI status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/health', methods=['GET'])
def health_check():
    """AI system health check"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'analytics_engine': 'operational',
                'automation_engine': 'operational',
                'nlp_interface': 'operational'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({'error': str(e)}), 500
