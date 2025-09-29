# Calendar Integrations API
# API endpoints for external calendar integrations

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from core.calendar_integrations import (
    CalendarIntegration, SyncLog, IntegrationProvider, SyncDirection, IntegrationStatus,
    IntegrationFactory, CalendarSyncService
)
from datetime import datetime, timedelta
import json

calendar_integrations_bp = Blueprint('calendar_integrations', __name__)

# Calendar Integrations
@calendar_integrations_bp.route('/integrations', methods=['GET'])
@jwt_required()
def get_calendar_integrations():
    """Get calendar integrations"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        integrations = CalendarIntegration.query.filter(
            CalendarIntegration.user_id == user_id,
            CalendarIntegration.company_id == company_id
        ).all()
        
        return jsonify([integration.to_dict() for integration in integrations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_integrations_bp.route('/integrations', methods=['POST'])
@jwt_required()
def create_calendar_integration():
    """Create calendar integration"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['integration_name', 'provider', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create integration
        integration = CalendarIntegration(
            integration_name=data['integration_name'],
            provider=IntegrationProvider(data['provider']),
            access_token=data.get('access_token'),
            refresh_token=data.get('refresh_token'),
            token_expires=datetime.fromisoformat(data['token_expires']) if data.get('token_expires') else None,
            client_id=data.get('client_id'),
            client_secret=data.get('client_secret'),
            sync_direction=SyncDirection(data.get('sync_direction', 'Bidirectional')),
            sync_frequency=data.get('sync_frequency', 15),
            auto_sync=data.get('auto_sync', True),
            external_calendar_id=data.get('external_calendar_id'),
            internal_calendar_id=data.get('internal_calendar_id'),
            user_id=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(integration)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('calendar_integration_created', integration.to_dict(), data['company_id'])
        
        return jsonify(integration.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@calendar_integrations_bp.route('/integrations/<int:integration_id>', methods=['GET'])
@jwt_required()
def get_calendar_integration(integration_id):
    """Get specific calendar integration"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        integration = CalendarIntegration.query.filter(
            CalendarIntegration.id == integration_id,
            CalendarIntegration.user_id == user_id,
            CalendarIntegration.company_id == company_id
        ).first()
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        return jsonify(integration.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_integrations_bp.route('/integrations/<int:integration_id>', methods=['PUT'])
@jwt_required()
def update_calendar_integration(integration_id):
    """Update calendar integration"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        integration = CalendarIntegration.query.filter(
            CalendarIntegration.id == integration_id,
            CalendarIntegration.user_id == user_id,
            CalendarIntegration.company_id == data.get('company_id')
        ).first()
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # Update fields
        for field in ['integration_name', 'is_active', 'access_token', 'refresh_token',
                     'client_id', 'client_secret', 'sync_direction', 'sync_frequency',
                     'auto_sync', 'external_calendar_id', 'internal_calendar_id']:
            if field in data:
                setattr(integration, field, data[field])
        
        if 'provider' in data:
            integration.provider = IntegrationProvider(data['provider'])
        
        if 'token_expires' in data and data['token_expires']:
            integration.token_expires = datetime.fromisoformat(data['token_expires'])
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('calendar_integration_updated', integration.to_dict(), integration.company_id)
        
        return jsonify(integration.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@calendar_integrations_bp.route('/integrations/<int:integration_id>', methods=['DELETE'])
@jwt_required()
def delete_calendar_integration(integration_id):
    """Delete calendar integration"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        integration = CalendarIntegration.query.filter(
            CalendarIntegration.id == integration_id,
            CalendarIntegration.user_id == user_id,
            CalendarIntegration.company_id == company_id
        ).first()
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # Soft delete
        integration.is_active = False
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('calendar_integration_deleted', {'id': integration_id}, company_id)
        
        return jsonify({'message': 'Integration deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Sync Operations
@calendar_integrations_bp.route('/integrations/<int:integration_id>/sync', methods=['POST'])
@jwt_required()
def sync_calendar_integration(integration_id):
    """Sync calendar integration"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        integration = CalendarIntegration.query.filter(
            CalendarIntegration.id == integration_id,
            CalendarIntegration.user_id == user_id,
            CalendarIntegration.company_id == data.get('company_id')
        ).first()
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # Create sync service
        sync_service = CalendarSyncService(integration)
        
        # Perform sync
        sync_log = sync_service.sync_events(
            start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
            end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None
        )
        
        # Update integration status
        integration.last_sync = datetime.utcnow()
        integration.sync_status = IntegrationStatus.ACTIVE if sync_log.sync_status == 'Success' else IntegrationStatus.ERROR
        integration.sync_count += 1
        
        if sync_log.sync_status == 'Error':
            integration.sync_errors = {
                'message': sync_log.error_message,
                'timestamp': sync_log.sync_start.isoformat()
            }
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('calendar_sync_completed', {
            'integration_id': integration_id,
            'sync_log': sync_log.to_dict()
        }, integration.company_id)
        
        return jsonify(sync_log.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@calendar_integrations_bp.route('/integrations/<int:integration_id>/calendars', methods=['GET'])
@jwt_required()
def get_external_calendars(integration_id):
    """Get external calendars"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        integration = CalendarIntegration.query.filter(
            CalendarIntegration.id == integration_id,
            CalendarIntegration.user_id == user_id,
            CalendarIntegration.company_id == company_id
        ).first()
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # Create integration instance
        external_integration = IntegrationFactory.create_integration(integration)
        
        # Get calendars
        calendars = external_integration.get_calendars()
        
        return jsonify(calendars)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_integrations_bp.route('/integrations/<int:integration_id>/events', methods=['GET'])
@jwt_required()
def get_external_events(integration_id):
    """Get external events"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        integration = CalendarIntegration.query.filter(
            CalendarIntegration.id == integration_id,
            CalendarIntegration.user_id == user_id,
            CalendarIntegration.company_id == company_id
        ).first()
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # Create integration instance
        external_integration = IntegrationFactory.create_integration(integration)
        
        # Parse dates
        start_date = datetime.fromisoformat(start_date) if start_date else None
        end_date = datetime.fromisoformat(end_date) if end_date else None
        
        # Get events
        events = external_integration.get_events(
            integration.external_calendar_id,
            start_date,
            end_date
        )
        
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Sync Logs
@calendar_integrations_bp.route('/sync-logs', methods=['GET'])
@jwt_required()
def get_sync_logs():
    """Get sync logs"""
    try:
        company_id = request.args.get('company_id', type=int)
        integration_id = request.args.get('integration_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = SyncLog.query.filter(SyncLog.company_id == company_id)
        
        if integration_id:
            query = query.filter(SyncLog.integration_id == integration_id)
        
        if start_date:
            query = query.filter(SyncLog.sync_start >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(SyncLog.sync_start <= datetime.fromisoformat(end_date))
        
        logs = query.order_by(SyncLog.sync_start.desc()).limit(100).all()
        
        return jsonify([log.to_dict() for log in logs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_integrations_bp.route('/sync-logs/<int:log_id>', methods=['GET'])
@jwt_required()
def get_sync_log(log_id):
    """Get specific sync log"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        log = SyncLog.query.filter(
            SyncLog.id == log_id,
            SyncLog.company_id == company_id
        ).first()
        
        if not log:
            return jsonify({'error': 'Sync log not found'}), 404
        
        return jsonify(log.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# OAuth Callbacks
@calendar_integrations_bp.route('/oauth/google/callback', methods=['POST'])
@jwt_required()
def google_oauth_callback():
    """Handle Google OAuth callback"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['code', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Exchange code for tokens
        # This would typically involve making a request to Google's OAuth endpoint
        # For now, we'll simulate the response
        
        # Create integration
        integration = CalendarIntegration(
            integration_name=data.get('integration_name', 'Google Calendar'),
            provider=IntegrationProvider.GOOGLE,
            access_token=data.get('access_token'),
            refresh_token=data.get('refresh_token'),
            token_expires=datetime.utcnow() + timedelta(hours=1),
            client_id=data.get('client_id'),
            client_secret=data.get('client_secret'),
            user_id=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(integration)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('google_oauth_completed', integration.to_dict(), data['company_id'])
        
        return jsonify(integration.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@calendar_integrations_bp.route('/oauth/microsoft/callback', methods=['POST'])
@jwt_required()
def microsoft_oauth_callback():
    """Handle Microsoft OAuth callback"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['code', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Exchange code for tokens
        # This would typically involve making a request to Microsoft's OAuth endpoint
        # For now, we'll simulate the response
        
        # Create integration
        integration = CalendarIntegration(
            integration_name=data.get('integration_name', 'Microsoft Outlook'),
            provider=IntegrationProvider.MICROSOFT,
            access_token=data.get('access_token'),
            refresh_token=data.get('refresh_token'),
            token_expires=datetime.utcnow() + timedelta(hours=1),
            client_id=data.get('client_id'),
            client_secret=data.get('client_secret'),
            user_id=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(integration)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('microsoft_oauth_completed', integration.to_dict(), data['company_id'])
        
        return jsonify(integration.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Integration Status
@calendar_integrations_bp.route('/integrations/<int:integration_id>/status', methods=['GET'])
@jwt_required()
def get_integration_status(integration_id):
    """Get integration status"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        integration = CalendarIntegration.query.filter(
            CalendarIntegration.id == integration_id,
            CalendarIntegration.user_id == user_id,
            CalendarIntegration.company_id == company_id
        ).first()
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404        
        # Get recent sync logs
        recent_logs = SyncLog.query.filter(
            SyncLog.integration_id == integration_id,
            SyncLog.company_id == company_id
        ).order_by(SyncLog.sync_start.desc()).limit(5).all()
        
        status = {
            'integration_id': integration_id,
            'is_active': integration.is_active,
            'sync_status': integration.sync_status.value if integration.sync_status else None,
            'last_sync': integration.last_sync.isoformat() if integration.last_sync else None,
            'sync_count': integration.sync_count,
            'sync_errors': integration.sync_errors,
            'recent_logs': [log.to_dict() for log in recent_logs]
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
