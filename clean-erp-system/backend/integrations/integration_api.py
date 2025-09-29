# Integration API Endpoints
# REST API for Enterprise Connectors, CRM Connectors, E-commerce Connectors, API Marketplace, and Webhook System

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

from .enterprise_connectors import enterprise_connector_manager, ConnectorConfig, ConnectorType
from .crm_connectors import crm_connector_manager, CRMConnectorConfig, CRMConnectorType, SyncDirection
from .ecommerce_connectors import ecommerce_connector_manager, EcommerceConnectorConfig, EcommerceConnectorType
from .api_marketplace import api_marketplace, APITier, APIStatus, WebhookEvent
from .webhook_system import webhook_system, WebhookPriority

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Integration Blueprint
integration_bp = Blueprint('integration', __name__, url_prefix='/api/integration')

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
# ENTERPRISE CONNECTOR ENDPOINTS
# =============================================================================

@integration_bp.route('/enterprise/connectors', methods=['POST'])
@require_auth
def create_enterprise_connector():
    """Create a new enterprise connector"""
    try:
        data = request.get_json()
        
        required_fields = ['connector_type', 'name', 'base_url', 'api_key']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        config = ConnectorConfig(
            connector_id=str(uuid.uuid4()),
            connector_type=ConnectorType(data['connector_type']),
            name=data['name'],
            base_url=data['base_url'],
            api_key=data['api_key'],
            secret_key=data.get('secret_key'),
            username=data.get('username'),
            password=data.get('password'),
            oauth_token=data.get('oauth_token'),
            refresh_token=data.get('refresh_token'),
            is_active=data.get('is_active', True),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata=data.get('metadata', {})
        )
        
        success = enterprise_connector_manager.create_connector(config)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Enterprise connector created successfully',
                'connector_id': config.connector_id
            }), 201
        else:
            return jsonify({'error': 'Failed to create enterprise connector'}), 400
            
    except Exception as e:
        logger.error(f"Error creating enterprise connector: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/enterprise/connectors/<connector_id>/sync', methods=['POST'])
@require_auth
def sync_enterprise_data(connector_id):
    """Sync data with enterprise system"""
    try:
        data = request.get_json()
        sync_type = data.get('sync_type', 'customers')
        sync_data = data.get('sync_data', {})
        
        sync_job = enterprise_connector_manager.sync_data(connector_id, sync_type, sync_data)
        
        return jsonify({
            'success': True,
            'sync_job': {
                'job_id': sync_job.job_id,
                'connector_id': sync_job.connector_id,
                'sync_type': sync_job.sync_type,
                'status': sync_job.status.value,
                'started_at': sync_job.started_at.isoformat(),
                'completed_at': sync_job.completed_at.isoformat() if sync_job.completed_at else None,
                'records_synced': sync_job.records_synced,
                'records_failed': sync_job.records_failed,
                'error_message': sync_job.error_message
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error syncing enterprise data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/enterprise/connectors/<connector_id>/sync/<job_id>', methods=['GET'])
@require_auth
def get_enterprise_sync_status(connector_id, job_id):
    """Get enterprise sync job status"""
    try:
        sync_job = enterprise_connector_manager.get_sync_status(job_id)
        
        if not sync_job:
            return jsonify({'error': 'Sync job not found'}), 404
        
        return jsonify({
            'success': True,
            'sync_job': {
                'job_id': sync_job.job_id,
                'connector_id': sync_job.connector_id,
                'sync_type': sync_job.sync_type,
                'status': sync_job.status.value,
                'started_at': sync_job.started_at.isoformat(),
                'completed_at': sync_job.completed_at.isoformat() if sync_job.completed_at else None,
                'records_synced': sync_job.records_synced,
                'records_failed': sync_job.records_failed,
                'error_message': sync_job.error_message
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting enterprise sync status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/enterprise/statistics', methods=['GET'])
@require_auth
def get_enterprise_statistics():
    """Get enterprise connector statistics"""
    try:
        stats = enterprise_connector_manager.get_connector_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting enterprise statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# CRM CONNECTOR ENDPOINTS
# =============================================================================

@integration_bp.route('/crm/connectors', methods=['POST'])
@require_auth
def create_crm_connector():
    """Create a new CRM connector"""
    try:
        data = request.get_json()
        
        required_fields = ['connector_type', 'name', 'base_url', 'api_key']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        config = CRMConnectorConfig(
            connector_id=str(uuid.uuid4()),
            connector_type=CRMConnectorType(data['connector_type']),
            name=data['name'],
            base_url=data['base_url'],
            api_key=data['api_key'],
            secret_key=data.get('secret_key'),
            access_token=data.get('access_token'),
            refresh_token=data.get('refresh_token'),
            client_id=data.get('client_id'),
            client_secret=data.get('client_secret'),
            is_active=data.get('is_active', True),
            sync_direction=SyncDirection(data.get('sync_direction', 'bidirectional')),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata=data.get('metadata', {})
        )
        
        success = crm_connector_manager.create_connector(config)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'CRM connector created successfully',
                'connector_id': config.connector_id
            }), 201
        else:
            return jsonify({'error': 'Failed to create CRM connector'}), 400
            
    except Exception as e:
        logger.error(f"Error creating CRM connector: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/crm/connectors/<connector_id>/sync', methods=['POST'])
@require_auth
def sync_crm_data(connector_id):
    """Sync data with CRM system"""
    try:
        data = request.get_json()
        sync_type = data.get('sync_type', 'leads')
        direction = SyncDirection(data.get('direction', 'import'))
        sync_data = data.get('sync_data', {})
        
        sync_job = crm_connector_manager.sync_crm_data(connector_id, sync_type, direction, sync_data)
        
        return jsonify({
            'success': True,
            'sync_job': {
                'job_id': sync_job.job_id,
                'connector_id': sync_job.connector_id,
                'sync_type': sync_job.sync_type,
                'direction': sync_job.direction.value,
                'status': sync_job.status,
                'started_at': sync_job.started_at.isoformat(),
                'completed_at': sync_job.completed_at.isoformat() if sync_job.completed_at else None,
                'records_synced': sync_job.records_synced,
                'records_failed': sync_job.records_failed,
                'error_message': sync_job.error_message
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error syncing CRM data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/crm/statistics', methods=['GET'])
@require_auth
def get_crm_statistics():
    """Get CRM connector statistics"""
    try:
        stats = crm_connector_manager.get_crm_connector_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting CRM statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# E-COMMERCE CONNECTOR ENDPOINTS
# =============================================================================

@integration_bp.route('/ecommerce/connectors', methods=['POST'])
@require_auth
def create_ecommerce_connector():
    """Create a new e-commerce connector"""
    try:
        data = request.get_json()
        
        required_fields = ['connector_type', 'name', 'base_url', 'api_key']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        config = EcommerceConnectorConfig(
            connector_id=str(uuid.uuid4()),
            connector_type=EcommerceConnectorType(data['connector_type']),
            name=data['name'],
            base_url=data['base_url'],
            api_key=data['api_key'],
            secret_key=data.get('secret_key'),
            access_token=data.get('access_token'),
            refresh_token=data.get('refresh_token'),
            client_id=data.get('client_id'),
            client_secret=data.get('client_secret'),
            is_active=data.get('is_active', True),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata=data.get('metadata', {})
        )
        
        success = ecommerce_connector_manager.create_connector(config)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'E-commerce connector created successfully',
                'connector_id': config.connector_id
            }), 201
        else:
            return jsonify({'error': 'Failed to create e-commerce connector'}), 400
            
    except Exception as e:
        logger.error(f"Error creating e-commerce connector: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/ecommerce/connectors/<connector_id>/sync', methods=['POST'])
@require_auth
def sync_ecommerce_data(connector_id):
    """Sync data with e-commerce platform"""
    try:
        data = request.get_json()
        sync_type = data.get('sync_type', 'products')
        sync_data = data.get('sync_data', {})
        
        sync_job = ecommerce_connector_manager.sync_ecommerce_data(connector_id, sync_type, sync_data)
        
        return jsonify({
            'success': True,
            'sync_job': {
                'job_id': sync_job.job_id,
                'connector_id': sync_job.connector_id,
                'sync_type': sync_job.sync_type,
                'status': sync_job.status.value,
                'started_at': sync_job.started_at.isoformat(),
                'completed_at': sync_job.completed_at.isoformat() if sync_job.completed_at else None,
                'records_synced': sync_job.records_synced,
                'records_failed': sync_job.records_failed,
                'error_message': sync_job.error_message
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error syncing e-commerce data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/ecommerce/statistics', methods=['GET'])
@require_auth
def get_ecommerce_statistics():
    """Get e-commerce connector statistics"""
    try:
        stats = ecommerce_connector_manager.get_ecommerce_connector_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting e-commerce statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# API MARKETPLACE ENDPOINTS
# =============================================================================

@integration_bp.route('/api-marketplace/clients', methods=['POST'])
@require_auth
def create_api_client():
    """Create a new API client"""
    try:
        data = request.get_json()
        
        required_fields = ['client_name', 'tier']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        client = api_marketplace.create_api_client(
            client_name=data['client_name'],
            tier=APITier(data['tier']),
            created_by=request.headers.get('X-User-ID', 'system'),
            webhook_url=data.get('webhook_url'),
            allowed_ips=data.get('allowed_ips'),
            metadata=data.get('metadata')
        )
        
        return jsonify({
            'success': True,
            'message': 'API client created successfully',
            'client': {
                'client_id': client.client_id,
                'client_name': client.client_name,
                'api_key': client.api_key,
                'tier': client.tier.value,
                'status': client.status.value,
                'rate_limit': client.rate_limit,
                'created_at': client.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating API client: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api-marketplace/clients/<client_id>', methods=['PUT'])
@require_auth
def update_api_client(client_id):
    """Update API client"""
    try:
        data = request.get_json()
        
        success = api_marketplace.update_api_client(client_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'API client updated successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to update API client'}), 400
            
    except Exception as e:
        logger.error(f"Error updating API client: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api-marketplace/clients/<client_id>', methods=['DELETE'])
@require_auth
def delete_api_client(client_id):
    """Delete API client"""
    try:
        success = api_marketplace.delete_api_client(client_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'API client deleted successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to delete API client'}), 400
            
    except Exception as e:
        logger.error(f"Error deleting API client: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api-marketplace/endpoints', methods=['GET'])
@require_auth
def get_api_endpoints():
    """Get API endpoints"""
    try:
        is_public = request.args.get('public', type=bool)
        endpoints = api_marketplace.get_api_endpoints(is_public)
        
        endpoints_data = []
        for endpoint in endpoints:
            endpoints_data.append({
                'endpoint_id': endpoint.endpoint_id,
                'name': endpoint.name,
                'path': endpoint.path,
                'method': endpoint.method,
                'description': endpoint.description,
                'parameters': endpoint.parameters,
                'response_schema': endpoint.response_schema,
                'rate_limit': endpoint.rate_limit,
                'authentication_required': endpoint.authentication_required,
                'is_public': endpoint.is_public,
                'created_at': endpoint.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'endpoints': endpoints_data,
            'count': len(endpoints_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting API endpoints: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api-marketplace/sdk/<language>', methods=['POST'])
@require_auth
def generate_sdk(language):
    """Generate SDK for a specific language"""
    try:
        data = request.get_json()
        client_id = data.get('client_id')
        
        if not client_id:
            return jsonify({'error': 'client_id is required'}), 400
        
        sdk = api_marketplace.generate_sdk(language, client_id)
        
        return jsonify({
            'success': True,
            'sdk': sdk
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating SDK: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# WEBHOOK SYSTEM ENDPOINTS
# =============================================================================

@integration_bp.route('/webhooks/subscriptions', methods=['POST'])
@require_auth
def create_webhook_subscription():
    """Create a webhook subscription"""
    try:
        data = request.get_json()
        
        required_fields = ['client_id', 'event_types', 'webhook_url', 'secret_key']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        subscription = webhook_system.create_subscription(
            client_id=data['client_id'],
            event_types=data['event_types'],
            webhook_url=data['webhook_url'],
            secret_key=data['secret_key'],
            retry_policy=data.get('retry_policy'),
            headers=data.get('headers'),
            timeout=data.get('timeout', 30)
        )
        
        return jsonify({
            'success': True,
            'message': 'Webhook subscription created successfully',
            'subscription': {
                'subscription_id': subscription.subscription_id,
                'client_id': subscription.client_id,
                'event_types': subscription.event_types,
                'webhook_url': subscription.webhook_url,
                'is_active': subscription.is_active,
                'created_at': subscription.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating webhook subscription: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/webhooks/trigger', methods=['POST'])
@require_auth
def trigger_webhook():
    """Trigger webhook event"""
    try:
        data = request.get_json()
        
        required_fields = ['event_type', 'payload']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        event_id = webhook_system.trigger_webhook(
            event_type=data['event_type'],
            payload=data['payload'],
            source=data.get('source', 'api'),
            priority=WebhookPriority(data.get('priority', 'normal'))
        )
        
        return jsonify({
            'success': True,
            'message': 'Webhook triggered successfully',
            'event_id': event_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error triggering webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/webhooks/statistics', methods=['GET'])
@require_auth
def get_webhook_statistics():
    """Get webhook system statistics"""
    try:
        stats = webhook_system.get_webhook_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting webhook statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/webhooks/deliveries/<delivery_id>', methods=['GET'])
@require_auth
def get_webhook_delivery_status(delivery_id):
    """Get webhook delivery status"""
    try:
        delivery = webhook_system.get_delivery_status(delivery_id)
        
        if not delivery:
            return jsonify({'error': 'Webhook delivery not found'}), 404
        
        return jsonify({
            'success': True,
            'delivery': {
                'delivery_id': delivery.delivery_id,
                'webhook_url': delivery.webhook_url,
                'event_id': delivery.event.event_id,
                'event_type': delivery.event.event_type,
                'status': delivery.status.value,
                'created_at': delivery.created_at.isoformat(),
                'delivered_at': delivery.delivered_at.isoformat() if delivery.delivered_at else None,
                'response_code': delivery.response_code,
                'error_message': delivery.error_message,
                'retry_count': delivery.retry_count
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting webhook delivery status: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# INTEGRATION SYSTEM STATUS ENDPOINTS
# =============================================================================

@integration_bp.route('/status', methods=['GET'])
@require_auth
def get_integration_system_status():
    """Get integration system status"""
    try:
        status = {
            'enterprise_connectors': {
                'status': 'operational',
                'total_connectors': len(enterprise_connector_manager.connectors),
                'active_connectors': len([c for c in enterprise_connector_manager.connectors.values() if c.config.is_active])
            },
            'crm_connectors': {
                'status': 'operational',
                'total_connectors': len(crm_connector_manager.connectors),
                'active_connectors': len([c for c in crm_connector_manager.connectors.values() if c.config.is_active])
            },
            'ecommerce_connectors': {
                'status': 'operational',
                'total_connectors': len(ecommerce_connector_manager.connectors),
                'active_connectors': len([c for c in ecommerce_connector_manager.connectors.values() if c.config.is_active])
            },
            'api_marketplace': {
                'status': 'operational',
                'total_clients': len(api_marketplace.api_clients),
                'total_endpoints': len(api_marketplace.api_endpoints)
            },
            'webhook_system': {
                'status': 'operational',
                'total_subscriptions': len(webhook_system.subscriptions),
                'active_subscriptions': len([s for s in webhook_system.subscriptions.values() if s.is_active])
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'status': status
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting integration system status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/health', methods=['GET'])
def health_check():
    """Integration system health check"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'enterprise_connectors': 'operational',
                'crm_connectors': 'operational',
                'ecommerce_connectors': 'operational',
                'api_marketplace': 'operational',
                'webhook_system': 'operational'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in integration health check: {str(e)}")
        return jsonify({'error': str(e)}), 500
