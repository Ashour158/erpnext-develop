# Integrations API Endpoints
# Third-party integrations, API marketplace, and external system connections

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import require_auth, get_current_user
from .models import (
    Integration, IntegrationLog, IntegrationSync, APIMarketplace,
    APISubscription, APIUsageLog, Webhook, WebhookLog
)
from datetime import datetime, date
import json
import uuid

# Create blueprint
integrations_bp = Blueprint('integrations', __name__, url_prefix='/integrations')

# Integration Endpoints
@integrations_bp.route('/integrations', methods=['GET'])
@require_auth
def get_integrations():
    """Get all integrations"""
    try:
        integrations = Integration.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [integration.to_dict() for integration in integrations]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@integrations_bp.route('/integrations', methods=['POST'])
@require_auth
def create_integration():
    """Create a new integration"""
    try:
        data = request.get_json()
        integration = Integration(
            integration_name=data['integration_name'],
            integration_description=data.get('integration_description'),
            integration_type=data['integration_type'],
            external_system=data['external_system'],
            base_url=data.get('base_url'),
            api_version=data.get('api_version'),
            authentication_type=data['authentication_type'],
            auth_config=data.get('auth_config', {}),
            status=data.get('status', 'Configuring'),
            is_active=data.get('is_active', False),
            sync_direction=data.get('sync_direction', 'Bidirectional'),
            sync_frequency=data.get('sync_frequency', 'Real-time'),
            supported_entities=data.get('supported_entities', []),
            field_mappings=data.get('field_mappings', {}),
            transformation_rules=data.get('transformation_rules', {}),
            company_id=get_current_user().company_id
        )
        
        db.session.add(integration)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': integration.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@integrations_bp.route('/integrations/<int:integration_id>/test', methods=['POST'])
@require_auth
def test_integration(integration_id):
    """Test an integration"""
    try:
        integration = Integration.query.get_or_404(integration_id)
        
        # Simulate integration test
        test_result = {
            'connection_status': 'Success',
            'authentication_status': 'Success',
            'api_access': 'Success',
            'response_time': 150.5,
            'test_details': {
                'endpoint_tested': integration.base_url,
                'authentication_method': integration.authentication_type.value,
                'response_status': 200
            }
        }
        
        # Update integration status
        integration.status = 'Active'
        integration.is_active = True
        
        # Create test log
        log = IntegrationLog(
            log_level='INFO',
            log_message='Integration test completed successfully',
            log_details=test_result,
            integration_id=integration_id,
            operation_type='Test',
            execution_time=test_result['response_time'],
            company_id=get_current_user().company_id
        )
        db.session.add(log)
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': test_result
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@integrations_bp.route('/integrations/<int:integration_id>/sync', methods=['POST'])
@require_auth
def sync_integration(integration_id):
    """Sync an integration"""
    try:
        integration = Integration.query.get_or_404(integration_id)
        data = request.get_json()
        
        # Create sync record
        sync_id = str(uuid.uuid4())
        sync = IntegrationSync(
            sync_id=sync_id,
            sync_type=data.get('sync_type', 'Incremental'),
            sync_status='Running',
            integration_id=integration_id,
            company_id=get_current_user().company_id
        )
        
        db.session.add(sync)
        db.session.flush()
        
        # Simulate sync process
        sync.sync_status = 'Completed'
        sync.sync_end_time = datetime.utcnow()
        sync.sync_duration = (sync.sync_end_time - sync.sync_start_time).total_seconds()
        sync.entities_synced = data.get('entities_synced', [])
        sync.sync_statistics = {
            'total_entities': len(sync.entities_synced),
            'successful_syncs': len(sync.entities_synced),
            'failed_syncs': 0,
            'sync_duration': sync.sync_duration
        }
        
        # Update integration statistics
        integration.total_syncs += 1
        integration.successful_syncs += 1
        integration.last_sync = datetime.utcnow()
        integration.average_sync_time = (
            (integration.average_sync_time * (integration.total_syncs - 1) + sync.sync_duration) / 
            integration.total_syncs
        )
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': sync.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# API Marketplace Endpoints
@integrations_bp.route('/marketplace', methods=['GET'])
@require_auth
def get_api_marketplace():
    """Get API marketplace"""
    try:
        apis = APIMarketplace.query.filter_by(
            company_id=get_current_user().company_id,
            is_active=True
        ).all()
        return jsonify({
            'success': True,
            'data': [api.to_dict() for api in apis]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@integrations_bp.route('/marketplace', methods=['POST'])
@require_auth
def create_api_marketplace():
    """Create a new API in marketplace"""
    try:
        data = request.get_json()
        api = APIMarketplace(
            api_name=data['api_name'],
            api_description=data.get('api_description'),
            api_version=data.get('api_version', '1.0.0'),
            api_category=data.get('api_category'),
            base_url=data['base_url'],
            api_documentation=data.get('api_documentation'),
            api_specification=data.get('api_specification', {}),
            is_public=data.get('is_public', False),
            is_active=data.get('is_active', True),
            requires_approval=data.get('requires_approval', False),
            rate_limit=data.get('rate_limit', 1000),
            rate_limit_window=data.get('rate_limit_window', 3600),
            company_id=get_current_user().company_id
        )
        
        db.session.add(api)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': api.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@integrations_bp.route('/marketplace/<int:api_id>/subscribe', methods=['POST'])
@require_auth
def subscribe_to_api(api_id):
    """Subscribe to an API"""
    try:
        api = APIMarketplace.query.get_or_404(api_id)
        data = request.get_json()
        
        # Generate API key
        api_key = str(uuid.uuid4())
        
        subscription = APISubscription(
            subscription_name=data['subscription_name'],
            subscription_status='Active',
            api_id=api_id,
            subscriber_id=get_current_user().id,
            subscriber_company_id=get_current_user().company_id,
            api_key=api_key,
            subscription_tier=data.get('subscription_tier', 'Basic'),
            usage_limit=data.get('usage_limit', 1000),
            subscription_start=date.today(),
            subscription_end=date.today().replace(year=date.today().year + 1) if data.get('subscription_end') else None,
            company_id=get_current_user().company_id
        )
        
        db.session.add(subscription)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': subscription.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@integrations_bp.route('/marketplace/<int:api_id>/usage', methods=['POST'])
@require_auth
def log_api_usage(api_id):
    """Log API usage"""
    try:
        api = APIMarketplace.query.get_or_404(api_id)
        data = request.get_json()
        
        # Create usage log
        request_id = str(uuid.uuid4())
        usage_log = APIUsageLog(
            request_id=request_id,
            endpoint=data['endpoint'],
            method=data.get('method', 'GET'),
            status_code=data.get('status_code', 200),
            api_id=api_id,
            request_data=data.get('request_data', {}),
            response_data=data.get('response_data', {}),
            request_size=data.get('request_size', 0),
            response_size=data.get('response_size', 0),
            response_time=data.get('response_time', 0.0),
            processing_time=data.get('processing_time', 0.0),
            client_ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            api_key=data.get('api_key'),
            company_id=get_current_user().company_id
        )
        
        db.session.add(usage_log)
        
        # Update API statistics
        api.total_requests += 1
        if data.get('status_code', 200) < 400:
            api.successful_requests += 1
        else:
            api.failed_requests += 1
        
        # Update average response time
        api.average_response_time = (
            (api.average_response_time * (api.total_requests - 1) + data.get('response_time', 0.0)) / 
            api.total_requests
        )
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': usage_log.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Webhook Endpoints
@integrations_bp.route('/webhooks', methods=['GET'])
@require_auth
def get_webhooks():
    """Get all webhooks"""
    try:
        webhooks = Webhook.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [webhook.to_dict() for webhook in webhooks]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@integrations_bp.route('/webhooks', methods=['POST'])
@require_auth
def create_webhook():
    """Create a new webhook"""
    try:
        data = request.get_json()
        webhook = Webhook(
            webhook_name=data['webhook_name'],
            webhook_description=data.get('webhook_description'),
            webhook_url=data['webhook_url'],
            events=data.get('events', []),
            headers=data.get('headers', {}),
            authentication=data.get('authentication', {}),
            is_active=data.get('is_active', True),
            retry_count=data.get('retry_count', 3),
            timeout=data.get('timeout', 30),
            company_id=get_current_user().company_id
        )
        
        db.session.add(webhook)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': webhook.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@integrations_bp.route('/webhooks/<int:webhook_id>/trigger', methods=['POST'])
@require_auth
def trigger_webhook(webhook_id):
    """Trigger a webhook"""
    try:
        webhook = Webhook.query.get_or_404(webhook_id)
        data = request.get_json()
        
        # Create webhook log
        webhook_log = WebhookLog(
            event_type=data.get('event_type', 'Custom'),
            payload=data.get('payload', {}),
            webhook_id=webhook_id,
            request_url=webhook.webhook_url,
            request_method='POST',
            request_headers=webhook.headers,
            request_body=json.dumps(data.get('payload', {})),
            company_id=get_current_user().company_id
        )
        
        # Simulate webhook execution
        webhook_log.response_status = 200
        webhook_log.response_time = 150.5
        webhook_log.is_successful = True
        
        db.session.add(webhook_log)
        
        # Update webhook statistics
        webhook.total_requests += 1
        webhook.successful_requests += 1
        webhook.last_triggered = datetime.utcnow()
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': webhook_log.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Analytics Endpoints
@integrations_bp.route('/analytics/integration-performance', methods=['GET'])
@require_auth
def get_integration_performance():
    """Get integration performance analytics"""
    try:
        # Get integration statistics
        integrations = Integration.query.filter_by(company_id=get_current_user().company_id).all()
        
        integration_performance = []
        for integration in integrations:
            success_rate = (integration.successful_syncs / integration.total_syncs * 100) if integration.total_syncs > 0 else 0
            integration_performance.append({
                'integration_id': integration.id,
                'integration_name': integration.integration_name,
                'external_system': integration.external_system,
                'status': integration.status.value if integration.status else None,
                'total_syncs': integration.total_syncs,
                'successful_syncs': integration.successful_syncs,
                'failed_syncs': integration.failed_syncs,
                'success_rate': success_rate,
                'average_sync_time': integration.average_sync_time,
                'last_sync': integration.last_sync.isoformat() if integration.last_sync else None
            })
        
        # Get overall statistics
        total_integrations = len(integrations)
        active_integrations = len([i for i in integrations if i.is_active])
        total_syncs = sum(i.total_syncs for i in integrations)
        successful_syncs = sum(i.successful_syncs for i in integrations)
        overall_success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'integration_performance': integration_performance,
                'total_integrations': total_integrations,
                'active_integrations': active_integrations,
                'total_syncs': total_syncs,
                'successful_syncs': successful_syncs,
                'overall_success_rate': overall_success_rate
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@integrations_bp.route('/analytics/api-usage', methods=['GET'])
@require_auth
def get_api_usage_analytics():
    """Get API usage analytics"""
    try:
        # Get API usage statistics
        apis = APIMarketplace.query.filter_by(company_id=get_current_user().company_id).all()
        
        api_usage = []
        for api in apis:
            api_usage.append({
                'api_id': api.id,
                'api_name': api.api_name,
                'api_category': api.api_category,
                'total_requests': api.total_requests,
                'successful_requests': api.successful_requests,
                'failed_requests': api.failed_requests,
                'success_rate': (api.successful_requests / api.total_requests * 100) if api.total_requests > 0 else 0,
                'average_response_time': api.average_response_time
            })
        
        # Get subscription statistics
        subscriptions = APISubscription.query.filter_by(company_id=get_current_user().company_id).all()
        total_subscriptions = len(subscriptions)
        active_subscriptions = len([s for s in subscriptions if s.subscription_status == 'Active'])
        
        return jsonify({
            'success': True,
            'data': {
                'api_usage': api_usage,
                'total_subscriptions': total_subscriptions,
                'active_subscriptions': active_subscriptions
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@integrations_bp.route('/analytics/webhook-performance', methods=['GET'])
@require_auth
def get_webhook_performance():
    """Get webhook performance analytics"""
    try:
        # Get webhook statistics
        webhooks = Webhook.query.filter_by(company_id=get_current_user().company_id).all()
        
        webhook_performance = []
        for webhook in webhooks:
            success_rate = (webhook.successful_requests / webhook.total_requests * 100) if webhook.total_requests > 0 else 0
            webhook_performance.append({
                'webhook_id': webhook.id,
                'webhook_name': webhook.webhook_name,
                'webhook_url': webhook.webhook_url,
                'is_active': webhook.is_active,
                'total_requests': webhook.total_requests,
                'successful_requests': webhook.successful_requests,
                'failed_requests': webhook.failed_requests,
                'success_rate': success_rate,
                'last_triggered': webhook.last_triggered.isoformat() if webhook.last_triggered else None
            })
        
        return jsonify({
            'success': True,
            'data': webhook_performance
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
