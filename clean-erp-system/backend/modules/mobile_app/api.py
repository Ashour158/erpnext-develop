# Mobile App API Endpoints
# Native mobile applications with offline capability and push notifications

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import require_auth, get_current_user
from .models import (
    MobileDevice, PushNotification, OfflineSync, OfflineAction,
    MobileAppConfig, MobileAnalytics, MobileSecurity
)
from datetime import datetime, date
import json
import uuid

# Create blueprint
mobile_app_bp = Blueprint('mobile_app', __name__, url_prefix='/mobile-app')

# Mobile Device Endpoints
@mobile_app_bp.route('/devices', methods=['GET'])
@require_auth
def get_mobile_devices():
    """Get all mobile devices"""
    try:
        devices = MobileDevice.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [device.to_dict() for device in devices]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@mobile_app_bp.route('/devices', methods=['POST'])
@require_auth
def register_mobile_device():
    """Register a new mobile device"""
    try:
        data = request.get_json()
        device = MobileDevice(
            device_id=data['device_id'],
            device_name=data['device_name'],
            device_type=data['device_type'],
            device_model=data.get('device_model'),
            device_version=data.get('device_version'),
            user_id=get_current_user().id,
            os_version=data.get('os_version'),
            app_version=data.get('app_version'),
            push_token=data.get('push_token'),
            push_enabled=data.get('push_enabled', True),
            notification_settings=data.get('notification_settings', {}),
            company_id=get_current_user().company_id
        )
        
        db.session.add(device)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': device.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@mobile_app_bp.route('/devices/<string:device_id>/heartbeat', methods=['POST'])
@require_auth
def device_heartbeat(device_id):
    """Update device heartbeat"""
    try:
        device = MobileDevice.query.filter_by(
            device_id=device_id,
            company_id=get_current_user().company_id
        ).first()
        
        if not device:
            return jsonify({
                'success': False,
                'message': 'Device not found'
            }), 404
        
        device.last_seen = datetime.utcnow()
        device.is_active = True
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': device.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Push Notification Endpoints
@mobile_app_bp.route('/notifications', methods=['GET'])
@require_auth
def get_push_notifications():
    """Get push notifications for user"""
    try:
        notifications = PushNotification.query.filter_by(
            target_user_id=get_current_user().id,
            company_id=get_current_user().company_id
        ).order_by(PushNotification.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [notification.to_dict() for notification in notifications]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@mobile_app_bp.route('/notifications', methods=['POST'])
@require_auth
def create_push_notification():
    """Create a new push notification"""
    try:
        data = request.get_json()
        notification = PushNotification(
            notification_title=data['notification_title'],
            notification_body=data['notification_body'],
            notification_type=data.get('notification_type', 'Push'),
            priority=data.get('priority', 'Medium'),
            target_user_id=data.get('target_user_id'),
            target_device_id=data.get('target_device_id'),
            target_audience=data.get('target_audience', []),
            notification_data=data.get('notification_data', {}),
            action_url=data.get('action_url'),
            image_url=data.get('image_url'),
            scheduled_at=datetime.strptime(data['scheduled_at'], '%Y-%m-%dT%H:%M:%S') if data.get('scheduled_at') else None,
            expires_at=datetime.strptime(data['expires_at'], '%Y-%m-%dT%H:%M:%S') if data.get('expires_at') else None,
            company_id=get_current_user().company_id
        )
        
        db.session.add(notification)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': notification.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@mobile_app_bp.route('/notifications/<int:notification_id>/mark-read', methods=['PUT'])
@require_auth
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        notification = PushNotification.query.get_or_404(notification_id)
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': notification.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Offline Sync Endpoints
@mobile_app_bp.route('/sync', methods=['POST'])
@require_auth
def start_offline_sync():
    """Start offline sync process"""
    try:
        data = request.get_json()
        sync_id = str(uuid.uuid4())
        
        sync = OfflineSync(
            sync_id=sync_id,
            user_id=get_current_user().id,
            device_id=data['device_id'],
            sync_type=data.get('sync_type', 'Incremental'),
            sync_status='Pending',
            company_id=get_current_user().company_id
        )
        
        db.session.add(sync)
        db.session.commit()
        
        # Simulate sync process
        sync.sync_status = 'Syncing'
        sync.sync_start_time = datetime.utcnow()
        
        # Simulate data sync
        sync.data_synced = {
            'customers': 150,
            'invoices': 75,
            'products': 200,
            'employees': 25
        }
        
        sync.sync_status = 'Completed'
        sync.sync_end_time = datetime.utcnow()
        sync.sync_duration = (sync.sync_end_time - sync.sync_start_time).total_seconds()
        
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

@mobile_app_bp.route('/sync/<string:sync_id>/status', methods=['GET'])
@require_auth
def get_sync_status(sync_id):
    """Get sync status"""
    try:
        sync = OfflineSync.query.filter_by(
            sync_id=sync_id,
            company_id=get_current_user().company_id
        ).first()
        
        if not sync:
            return jsonify({
                'success': False,
                'message': 'Sync not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': sync.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Offline Action Endpoints
@mobile_app_bp.route('/offline-actions', methods=['GET'])
@require_auth
def get_offline_actions():
    """Get offline actions for user"""
    try:
        actions = OfflineAction.query.filter_by(
            user_id=get_current_user().id,
            company_id=get_current_user().company_id
        ).order_by(OfflineAction.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [action.to_dict() for action in actions]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@mobile_app_bp.route('/offline-actions', methods=['POST'])
@require_auth
def create_offline_action():
    """Create a new offline action"""
    try:
        data = request.get_json()
        action_id = str(uuid.uuid4())
        
        action = OfflineAction(
            action_id=action_id,
            user_id=get_current_user().id,
            device_id=data['device_id'],
            action_type=data['action_type'],
            entity_type=data['entity_type'],
            entity_id=data.get('entity_id'),
            action_data=data.get('action_data', {}),
            company_id=get_current_user().company_id
        )
        
        db.session.add(action)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': action.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@mobile_app_bp.route('/offline-actions/<string:action_id>/sync', methods=['POST'])
@require_auth
def sync_offline_action(action_id):
    """Sync offline action to server"""
    try:
        action = OfflineAction.query.filter_by(
            action_id=action_id,
            company_id=get_current_user().company_id
        ).first()
        
        if not action:
            return jsonify({
                'success': False,
                'message': 'Action not found'
            }), 404
        
        # Simulate sync process
        action.is_synced = True
        action.synced_at = datetime.utcnow()
        action.sync_attempts += 1
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': action.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Mobile App Configuration Endpoints
@mobile_app_bp.route('/config', methods=['GET'])
@require_auth
def get_mobile_app_config():
    """Get mobile app configuration"""
    try:
        configs = MobileAppConfig.query.filter_by(
            company_id=get_current_user().company_id,
            is_active=True
        ).all()
        
        return jsonify({
            'success': True,
            'data': [config.to_dict() for config in configs]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@mobile_app_bp.route('/config', methods=['POST'])
@require_auth
def create_mobile_app_config():
    """Create mobile app configuration"""
    try:
        data = request.get_json()
        config = MobileAppConfig(
            config_name=data['config_name'],
            config_description=data.get('config_description'),
            config_type=data['config_type'],
            config_data=data['config_data'],
            is_active=data.get('is_active', True),
            is_global=data.get('is_global', True),
            target_users=data.get('target_users', []),
            target_roles=data.get('target_roles', []),
            target_devices=data.get('target_devices', []),
            version=data.get('version', '1.0.0'),
            min_app_version=data.get('min_app_version'),
            max_app_version=data.get('max_app_version'),
            company_id=get_current_user().company_id
        )
        
        db.session.add(config)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': config.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Mobile Analytics Endpoints
@mobile_app_bp.route('/analytics', methods=['POST'])
@require_auth
def track_mobile_analytics():
    """Track mobile analytics event"""
    try:
        data = request.get_json()
        analytics = MobileAnalytics(
            event_name=data['event_name'],
            event_type=data.get('event_type', 'User'),
            event_category=data.get('event_category'),
            user_id=get_current_user().id,
            device_id=data.get('device_id'),
            device_type=data.get('device_type'),
            event_data=data.get('event_data', {}),
            session_id=data.get('session_id'),
            response_time=data.get('response_time', 0.0),
            memory_usage=data.get('memory_usage', 0.0),
            battery_level=data.get('battery_level', 0.0),
            network_type=data.get('network_type'),
            company_id=get_current_user().company_id
        )
        
        db.session.add(analytics)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': analytics.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@mobile_app_bp.route('/analytics/summary', methods=['GET'])
@require_auth
def get_mobile_analytics_summary():
    """Get mobile analytics summary"""
    try:
        # Get analytics summary for the last 30 days
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Get event counts by type
        event_counts = db.session.query(
            MobileAnalytics.event_type,
            db.func.count(MobileAnalytics.id)
        ).filter(
            MobileAnalytics.company_id == get_current_user().company_id,
            MobileAnalytics.event_timestamp >= start_date
        ).group_by(MobileAnalytics.event_type).all()
        
        # Get device distribution
        device_distribution = db.session.query(
            MobileAnalytics.device_type,
            db.func.count(MobileAnalytics.id)
        ).filter(
            MobileAnalytics.company_id == get_current_user().company_id,
            MobileAnalytics.event_timestamp >= start_date
        ).group_by(MobileAnalytics.device_type).all()
        
        # Get performance metrics
        avg_response_time = db.session.query(
            db.func.avg(MobileAnalytics.response_time)
        ).filter(
            MobileAnalytics.company_id == get_current_user().company_id,
            MobileAnalytics.event_timestamp >= start_date
        ).scalar() or 0
        
        avg_memory_usage = db.session.query(
            db.func.avg(MobileAnalytics.memory_usage)
        ).filter(
            MobileAnalytics.company_id == get_current_user().company_id,
            MobileAnalytics.event_timestamp >= start_date
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'event_counts': dict(event_counts),
                'device_distribution': dict(device_distribution),
                'avg_response_time': float(avg_response_time),
                'avg_memory_usage': float(avg_memory_usage)
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Mobile Security Endpoints
@mobile_app_bp.route('/security', methods=['POST'])
@require_auth
def track_mobile_security():
    """Track mobile security event"""
    try:
        data = request.get_json()
        security = MobileSecurity(
            security_event=data['security_event'],
            event_type=data['event_type'],
            severity=data.get('severity', 'Medium'),
            user_id=get_current_user().id,
            device_id=data.get('device_id'),
            device_type=data.get('device_type'),
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent'),
            location=data.get('location'),
            security_data=data.get('security_data', {}),
            company_id=get_current_user().company_id
        )
        
        db.session.add(security)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': security.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@mobile_app_bp.route('/security/events', methods=['GET'])
@require_auth
def get_mobile_security_events():
    """Get mobile security events"""
    try:
        events = MobileSecurity.query.filter_by(
            company_id=get_current_user().company_id
        ).order_by(MobileSecurity.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [event.to_dict() for event in events]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@mobile_app_bp.route('/security/events/<int:event_id>/resolve', methods=['PUT'])
@require_auth
def resolve_security_event(event_id):
    """Resolve security event"""
    try:
        event = MobileSecurity.query.get_or_404(event_id)
        event.is_resolved = True
        event.resolved_at = datetime.utcnow()
        event.resolved_by_id = get_current_user().id
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': event.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
