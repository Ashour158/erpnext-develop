# WhatsApp API Endpoints
# REST API endpoints for WhatsApp Business integration

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import json
import uuid
from functools import wraps

# Import WhatsApp integration
from .whatsapp_integration import (
    WhatsAppBusinessAPI, 
    WhatsAppIntegrationManager, 
    whatsapp_integration_manager,
    MessageType,
    MessageStatus,
    IntentType,
    Priority
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
whatsapp_bp = Blueprint('whatsapp', __name__, url_prefix='/api/whatsapp')

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in headers
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != current_app.config.get('WHATSAPP_API_KEY'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """WhatsApp webhook endpoint"""
    try:
        if request.method == 'GET':
            # Webhook verification
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            
            # Get the first integration (in production, you'd determine which integration)
            integrations = list(whatsapp_integration_manager.integrations.values())
            if not integrations:
                return jsonify({'error': 'No WhatsApp integrations configured'}), 400
            
            integration = integrations[0]
            result = integration.verify_webhook(mode, token, challenge)
            
            if result:
                return result, 200
            else:
                return jsonify({'error': 'Webhook verification failed'}), 403
        
        elif request.method == 'POST':
            # Handle incoming webhook
            webhook_data = request.get_json()
            
            if not webhook_data:
                return jsonify({'error': 'No webhook data received'}), 400
            
            # Get the first integration (in production, you'd determine which integration)
            integrations = list(whatsapp_integration_manager.integrations.values())
            if not integrations:
                return jsonify({'error': 'No WhatsApp integrations configured'}), 400
            
            integration = integrations[0]
            result = integration.handle_webhook(webhook_data)
            
            return jsonify(result), 200 if result.get('status') == 'success' else 400
    
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/integrations', methods=['POST'])
@require_auth
def create_integration():
    """Create new WhatsApp integration"""
    try:
        data = request.get_json()
        
        required_fields = ['access_token', 'phone_number_id', 'webhook_verify_token']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        integration_id = str(uuid.uuid4())
        success = whatsapp_integration_manager.add_integration(
            integration_id=integration_id,
            access_token=data['access_token'],
            phone_number_id=data['phone_number_id'],
            webhook_verify_token=data['webhook_verify_token']
        )
        
        if success:
            return jsonify({
                'success': True,
                'integration_id': integration_id,
                'message': 'WhatsApp integration created successfully'
            }), 201
        else:
            return jsonify({'error': 'Failed to create integration'}), 500
    
    except Exception as e:
        logger.error(f"Error creating integration: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/integrations/<integration_id>', methods=['GET'])
@require_auth
def get_integration(integration_id: str):
    """Get WhatsApp integration details"""
    try:
        integration = whatsapp_integration_manager.get_integration(integration_id)
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        return jsonify({
            'integration_id': integration_id,
            'phone_number_id': integration.phone_number_id,
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting integration: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/integrations/<integration_id>', methods=['DELETE'])
@require_auth
def delete_integration(integration_id: str):
    """Delete WhatsApp integration"""
    try:
        success = whatsapp_integration_manager.remove_integration(integration_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Integration deleted successfully'
            }), 200
        else:
            return jsonify({'error': 'Integration not found'}), 404
    
    except Exception as e:
        logger.error(f"Error deleting integration: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/integrations', methods=['GET'])
@require_auth
def list_integrations():
    """List all WhatsApp integrations"""
    try:
        integrations = []
        for integration_id, integration in whatsapp_integration_manager.integrations.items():
            integrations.append({
                'integration_id': integration_id,
                'phone_number_id': integration.phone_number_id,
                'status': 'active',
                'created_at': datetime.now().isoformat()
            })
        
        return jsonify({
            'integrations': integrations,
            'total': len(integrations)
        }), 200
    
    except Exception as e:
        logger.error(f"Error listing integrations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/send-message', methods=['POST'])
@require_auth
def send_message():
    """Send WhatsApp message"""
    try:
        data = request.get_json()
        
        required_fields = ['to', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get integration
        integration_id = data.get('integration_id')
        if integration_id:
            integration = whatsapp_integration_manager.get_integration(integration_id)
        else:
            # Use first available integration
            integrations = list(whatsapp_integration_manager.integrations.values())
            if not integrations:
                return jsonify({'error': 'No WhatsApp integrations configured'}), 400
            integration = integrations[0]
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # Send message
        result = integration._send_text_message(data['to'], data['message'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'message_id': result['message_id'],
                'message': 'Message sent successfully'
            }), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/conversations/<phone_number>', methods=['GET'])
@require_auth
def get_conversation_history(phone_number: str):
    """Get conversation history for a phone number"""
    try:
        # Get integration
        integration_id = request.args.get('integration_id')
        if integration_id:
            integration = whatsapp_integration_manager.get_integration(integration_id)
        else:
            # Use first available integration
            integrations = list(whatsapp_integration_manager.integrations.values())
            if not integrations:
                return jsonify({'error': 'No WhatsApp integrations configured'}), 400
            integration = integrations[0]
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        limit = request.args.get('limit', 50, type=int)
        conversations = integration.get_conversation_history(phone_number, limit)
        
        return jsonify({
            'phone_number': phone_number,
            'conversations': conversations,
            'total': len(conversations)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/analytics', methods=['GET'])
@require_auth
def get_analytics():
    """Get WhatsApp analytics"""
    try:
        analytics = whatsapp_integration_manager.get_all_analytics()
        
        return jsonify({
            'analytics': analytics,
            'generated_at': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/templates', methods=['GET'])
@require_auth
def get_templates():
    """Get WhatsApp message templates"""
    try:
        # Get integration
        integration_id = request.args.get('integration_id')
        if integration_id:
            integration = whatsapp_integration_manager.get_integration(integration_id)
        else:
            # Use first available integration
            integrations = list(whatsapp_integration_manager.integrations.values())
            if not integrations:
                return jsonify({'error': 'No WhatsApp integrations configured'}), 400
            integration = integrations[0]
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # Get templates from WhatsApp API
        url = f"{integration.base_url}/{integration.phone_number_id}/message_templates"
        response = integration.session.get(url)
        response.raise_for_status()
        
        templates_data = response.json()
        
        return jsonify({
            'templates': templates_data.get('data', []),
            'total': len(templates_data.get('data', []))
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/templates', methods=['POST'])
@require_auth
def create_template():
    """Create WhatsApp message template"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'category', 'language', 'components']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get integration
        integration_id = data.get('integration_id')
        if integration_id:
            integration = whatsapp_integration_manager.get_integration(integration_id)
        else:
            # Use first available integration
            integrations = list(whatsapp_integration_manager.integrations.values())
            if not integrations:
                return jsonify({'error': 'No WhatsApp integrations configured'}), 400
            integration = integrations[0]
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # Create template via WhatsApp API
        url = f"{integration.base_url}/{integration.phone_number_id}/message_templates"
        payload = {
            'name': data['name'],
            'category': data['category'],
            'language': data['language'],
            'components': data['components']
        }
        
        response = integration.session.post(url, json=payload)
        response.raise_for_status()
        
        template_data = response.json()
        
        return jsonify({
            'success': True,
            'template_id': template_data.get('id'),
            'message': 'Template created successfully'
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/media', methods=['POST'])
@require_auth
def upload_media():
    """Upload media to WhatsApp"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get integration
        integration_id = request.form.get('integration_id')
        if integration_id:
            integration = whatsapp_integration_manager.get_integration(integration_id)
        else:
            # Use first available integration
            integrations = list(whatsapp_integration_manager.integrations.values())
            if not integrations:
                return jsonify({'error': 'No WhatsApp integrations configured'}), 400
            integration = integrations[0]
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # Upload media to WhatsApp
        url = f"{integration.base_url}/{integration.phone_number_id}/media"
        files = {'file': (file.filename, file.stream, file.content_type)}
        
        response = integration.session.post(url, files=files)
        response.raise_for_status()
        
        media_data = response.json()
        
        return jsonify({
            'success': True,
            'media_id': media_data.get('id'),
            'message': 'Media uploaded successfully'
        }), 201
    
    except Exception as e:
        logger.error(f"Error uploading media: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/contacts', methods=['GET'])
@require_auth
def get_contacts():
    """Get WhatsApp contacts"""
    try:
        # Get integration
        integration_id = request.args.get('integration_id')
        if integration_id:
            integration = whatsapp_integration_manager.get_integration(integration_id)
        else:
            # Use first available integration
            integrations = list(whatsapp_integration_manager.integrations.values())
            if not integrations:
                return jsonify({'error': 'No WhatsApp integrations configured'}), 400
            integration = integrations[0]
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # This would query the CRM database for contacts
        # For now, return empty list
        contacts = []
        
        return jsonify({
            'contacts': contacts,
            'total': len(contacts)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting contacts: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/contacts/<contact_id>', methods=['GET'])
@require_auth
def get_contact(contact_id: str):
    """Get specific WhatsApp contact"""
    try:
        # This would query the CRM database for the specific contact
        # For now, return placeholder
        contact = {
            'contact_id': contact_id,
            'phone_number': '+1234567890',
            'name': 'WhatsApp User',
            'conversation_count': 0,
            'last_seen': datetime.now().isoformat()
        }
        
        return jsonify({'contact': contact}), 200
    
    except Exception as e:
        logger.error(f"Error getting contact: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/webhook/status', methods=['GET'])
@require_auth
def get_webhook_status():
    """Get webhook status"""
    try:
        # Check if webhook is properly configured
        webhook_status = {
            'configured': len(whatsapp_integration_manager.integrations) > 0,
            'integrations_count': len(whatsapp_integration_manager.integrations),
            'last_webhook_received': datetime.now().isoformat(),
            'status': 'active' if len(whatsapp_integration_manager.integrations) > 0 else 'inactive'
        }
        
        return jsonify({'webhook_status': webhook_status}), 200
    
    except Exception as e:
        logger.error(f"Error getting webhook status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/test', methods=['POST'])
@require_auth
def test_integration():
    """Test WhatsApp integration"""
    try:
        data = request.get_json()
        
        integration_id = data.get('integration_id')
        if integration_id:
            integration = whatsapp_integration_manager.get_integration(integration_id)
        else:
            # Use first available integration
            integrations = list(whatsapp_integration_manager.integrations.values())
            if not integrations:
                return jsonify({'error': 'No WhatsApp integrations configured'}), 400
            integration = integrations[0]
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # Send test message
        test_number = data.get('test_number', '+1234567890')
        test_message = "This is a test message from ERP WhatsApp integration."
        
        result = integration._send_text_message(test_number, test_message)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Test message sent successfully',
                'message_id': result['message_id']
            }), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        logger.error(f"Error testing integration: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@whatsapp_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@whatsapp_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Health check endpoint
@whatsapp_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        integrations_count = len(whatsapp_integration_manager.integrations)
        
        return jsonify({
            'status': 'healthy',
            'integrations': integrations_count,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
