# Mobile Enhancements API
# API endpoints for mobile app enhancements including offline capability, push notifications, voice commands, and AR features

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from .models import (
    PushNotification, OfflineData, VoiceCommand, ARSession, MobileDevice,
    OfflineSyncLog, MobileAppSetting,
    NotificationType, NotificationPriority, DeliveryStatus, OfflineSyncStatus,
    VoiceCommandType, ARFeatureType
)
from datetime import datetime, timedelta
import json

mobile_enhancements_bp = Blueprint('mobile_enhancements', __name__)

# Push Notifications
@mobile_enhancements_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_push_notifications():
    """Get push notifications"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        notification_type = request.args.get('notification_type')
        delivery_status = request.args.get('delivery_status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = PushNotification.query.filter(
            PushNotification.target_user_id == user_id,
            PushNotification.company_id == company_id
        )
        
        if notification_type:
            query = query.filter(PushNotification.notification_type == NotificationType(notification_type))
        
        if delivery_status:
            query = query.filter(PushNotification.delivery_status == DeliveryStatus(delivery_status))
        
        if start_date:
            query = query.filter(PushNotification.scheduled_time >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(PushNotification.scheduled_time <= datetime.fromisoformat(end_date))
        
        notifications = query.order_by(PushNotification.scheduled_time.desc()).limit(100).all()
        
        return jsonify([notification.to_dict() for notification in notifications])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mobile_enhancements_bp.route('/notifications', methods=['POST'])
@jwt_required()
def create_push_notification():
    """Create push notification"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['notification_title', 'notification_message', 'notification_type', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create notification
        notification = PushNotification(
            notification_title=data['notification_title'],
            notification_message=data['notification_message'],
            notification_type=NotificationType(data['notification_type']),
            priority=NotificationPriority(data.get('priority', 'NORMAL')),
            scheduled_time=datetime.fromisoformat(data['scheduled_time']) if data.get('scheduled_time') else datetime.utcnow(),
            target_user_id=data.get('target_user_id', user_id),
            target_device_id=data.get('target_device_id'),
            target_platform=data.get('target_platform'),
            notification_data=data.get('notification_data'),
            action_buttons=data.get('action_buttons'),
            deep_link=data.get('deep_link'),
            company_id=data['company_id']
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('push_notification_created', notification.to_dict(), data['company_id'])
        
        return jsonify(notification.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mobile_enhancements_bp.route('/notifications/<int:notification_id>/mark-read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        notification = PushNotification.query.filter(
            PushNotification.id == notification_id,
            PushNotification.target_user_id == user_id,
            PushNotification.company_id == company_id
        ).first()
        
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        # Update notification
        notification.delivery_status = DeliveryStatus.READ
        notification.read_time = datetime.utcnow()
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('notification_marked_read', notification.to_dict(), company_id)
        
        return jsonify(notification.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Offline Data
@mobile_enhancements_bp.route('/offline-data', methods=['GET'])
@jwt_required()
def get_offline_data():
    """Get offline data"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        data_type = request.args.get('data_type')
        sync_status = request.args.get('sync_status')
        device_id = request.args.get('device_id')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = OfflineData.query.filter(
            OfflineData.user_id == user_id,
            OfflineData.company_id == company_id
        )
        
        if data_type:
            query = query.filter(OfflineData.data_type == data_type)
        
        if sync_status:
            query = query.filter(OfflineData.sync_status == OfflineSyncStatus(sync_status))
        
        if device_id:
            query = query.filter(OfflineData.device_id == device_id)
        
        offline_data = query.order_by(OfflineData.last_modified.desc()).limit(100).all()
        
        return jsonify([data.to_dict() for data in offline_data])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mobile_enhancements_bp.route('/offline-data', methods=['POST'])
@jwt_required()
def create_offline_data():
    """Create offline data"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['data_type', 'data_id', 'data_content', 'device_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create offline data
        offline_data = OfflineData(
            data_type=data['data_type'],
            data_id=data['data_id'],
            data_content=data['data_content'],
            sync_status=OfflineSyncStatus(data.get('sync_status', 'PENDING')),
            user_id=user_id,
            device_id=data['device_id'],
            app_version=data.get('app_version'),
            company_id=data['company_id']
        )
        
        db.session.add(offline_data)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('offline_data_created', offline_data.to_dict(), data['company_id'])
        
        return jsonify(offline_data.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mobile_enhancements_bp.route('/offline-data/<int:data_id>/sync', methods=['POST'])
@jwt_required()
def sync_offline_data(data_id):
    """Sync offline data"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        offline_data = OfflineData.query.filter(
            OfflineData.id == data_id,
            OfflineData.user_id == user_id,
            OfflineData.company_id == data.get('company_id')
        ).first()
        
        if not offline_data:
            return jsonify({'error': 'Offline data not found'}), 404
        
        # Update sync status
        offline_data.sync_status = OfflineSyncStatus.SYNCING
        offline_data.sync_attempts += 1
        
        # Simulate sync process
        # In a real implementation, this would sync with the server
        offline_data.sync_status = OfflineSyncStatus.COMPLETED
        offline_data.last_modified = datetime.utcnow()
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('offline_data_synced', offline_data.to_dict(), offline_data.company_id)
        
        return jsonify(offline_data.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Voice Commands
@mobile_enhancements_bp.route('/voice-commands', methods=['GET'])
@jwt_required()
def get_voice_commands():
    """Get voice commands"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        command_type = request.args.get('command_type')
        is_processed = request.args.get('is_processed', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = VoiceCommand.query.filter(
            VoiceCommand.user_id == user_id,
            VoiceCommand.company_id == company_id
        )
        
        if command_type:
            query = query.filter(VoiceCommand.command_type == VoiceCommandType(command_type))
        
        if is_processed is not None:
            query = query.filter(VoiceCommand.is_processed == is_processed)
        
        commands = query.order_by(VoiceCommand.created_at.desc()).limit(50).all()
        
        return jsonify([command.to_dict() for command in commands])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mobile_enhancements_bp.route('/voice-commands', methods=['POST'])
@jwt_required()
def create_voice_command():
    """Create voice command"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['command_text', 'command_type', 'device_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create voice command
        command = VoiceCommand(
            command_text=data['command_text'],
            command_type=VoiceCommandType(data['command_type']),
            confidence_score=data.get('confidence_score', 0.0),
            user_id=user_id,
            device_id=data['device_id'],
            audio_file_path=data.get('audio_file_path'),
            company_id=data['company_id']
        )
        
        db.session.add(command)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('voice_command_created', command.to_dict(), data['company_id'])
        
        return jsonify(command.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mobile_enhancements_bp.route('/voice-commands/<int:command_id>/process', methods=['POST'])
@jwt_required()
def process_voice_command(command_id):
    """Process voice command"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        command = VoiceCommand.query.filter(
            VoiceCommand.id == command_id,
            VoiceCommand.user_id == user_id,
            VoiceCommand.company_id == data.get('company_id')
        ).first()
        
        if not command:
            return jsonify({'error': 'Voice command not found'}), 404
        
        # Process command
        command.is_processed = True
        command.processing_time = data.get('processing_time', 0.0)
        command.processing_errors = data.get('processing_errors')
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('voice_command_processed', command.to_dict(), command.company_id)
        
        return jsonify(command.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# AR Sessions
@mobile_enhancements_bp.route('/ar-sessions', methods=['GET'])
@jwt_required()
def get_ar_sessions():
    """Get AR sessions"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        feature_type = request.args.get('feature_type')
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = ARSession.query.filter(
            ARSession.user_id == user_id,
            ARSession.company_id == company_id
        )
        
        if feature_type:
            query = query.filter(ARSession.feature_type == ARFeatureType(feature_type))
        
        if is_active is not None:
            query = query.filter(ARSession.is_active == is_active)
        
        sessions = query.order_by(ARSession.created_at.desc()).limit(50).all()
        
        return jsonify([session.to_dict() for session in sessions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mobile_enhancements_bp.route('/ar-sessions', methods=['POST'])
@jwt_required()
def create_ar_session():
    """Create AR session"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['session_name', 'feature_type', 'device_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create AR session
        session = ARSession(
            session_name=data['session_name'],
            session_description=data.get('session_description'),
            feature_type=ARFeatureType(data['feature_type']),
            ar_data=data.get('ar_data'),
            coordinates=data.get('coordinates'),
            measurements=data.get('measurements'),
            annotations=data.get('annotations'),
            user_id=user_id,
            device_id=data['device_id'],
            device_capabilities=data.get('device_capabilities'),
            company_id=data['company_id']
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('ar_session_created', session.to_dict(), data['company_id'])
        
        return jsonify(session.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Mobile Devices
@mobile_enhancements_bp.route('/devices', methods=['GET'])
@jwt_required()
def get_mobile_devices():
    """Get mobile devices"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = MobileDevice.query.filter(
            MobileDevice.user_id == user_id,
            MobileDevice.company_id == company_id
        )
        
        if is_active is not None:
            query = query.filter(MobileDevice.is_active == is_active)
        
        devices = query.all()
        
        return jsonify([device.to_dict() for device in devices])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mobile_enhancements_bp.route('/devices', methods=['POST'])
@jwt_required()
def register_mobile_device():
    """Register mobile device"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['device_id', 'device_name', 'device_type', 'operating_system', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if device already exists
        existing_device = MobileDevice.query.filter(
            MobileDevice.device_id == data['device_id'],
            MobileDevice.company_id == data['company_id']
        ).first()
        
        if existing_device:
            # Update existing device
            existing_device.device_name = data['device_name']
            existing_device.device_type = data['device_type']
            existing_device.operating_system = data['operating_system']
            existing_device.os_version = data.get('os_version')
            existing_device.app_version = data.get('app_version')
            existing_device.has_camera = data.get('has_camera', False)
            existing_device.has_gps = data.get('has_gps', False)
            existing_device.has_accelerometer = data.get('has_accelerometer', False)
            existing_device.has_gyroscope = data.get('has_gyroscope', False)
            existing_device.has_magnetometer = data.get('has_magnetometer', False)
            existing_device.has_ar_support = data.get('has_ar_support', False)
            existing_device.is_active = True
            existing_device.last_seen = datetime.utcnow()
            existing_device.battery_level = data.get('battery_level', 0.0)
            existing_device.network_status = data.get('network_status', 'Unknown')
            
            db.session.commit()
            
            # Emit real-time update
            emit_realtime_update('mobile_device_updated', existing_device.to_dict(), data['company_id'])
            
            return jsonify(existing_device.to_dict())
        else:
            # Create new device
            device = MobileDevice(
                device_id=data['device_id'],
                device_name=data['device_name'],
                device_type=data['device_type'],
                operating_system=data['operating_system'],
                os_version=data.get('os_version'),
                app_version=data.get('app_version'),
                has_camera=data.get('has_camera', False),
                has_gps=data.get('has_gps', False),
                has_accelerometer=data.get('has_accelerometer', False),
                has_gyroscope=data.get('has_gyroscope', False),
                has_magnetometer=data.get('has_magnetometer', False),
                has_ar_support=data.get('has_ar_support', False),
                is_active=True,
                last_seen=datetime.utcnow(),
                battery_level=data.get('battery_level', 0.0),
                network_status=data.get('network_status', 'Unknown'),
                user_id=user_id,
                company_id=data['company_id']
            )
            
            db.session.add(device)
            db.session.commit()
            
            # Emit real-time update
            emit_realtime_update('mobile_device_registered', device.to_dict(), data['company_id'])
            
            return jsonify(device.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Offline Sync Logs
@mobile_enhancements_bp.route('/sync-logs', methods=['GET'])
@jwt_required()
def get_sync_logs():
    """Get offline sync logs"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        sync_type = request.args.get('sync_type')
        sync_status = request.args.get('sync_status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = OfflineSyncLog.query.filter(
            OfflineSyncLog.user_id == user_id,
            OfflineSyncLog.company_id == company_id
        )
        
        if sync_type:
            query = query.filter(OfflineSyncLog.sync_type == sync_type)
        
        if sync_status:
            query = query.filter(OfflineSyncLog.sync_status == OfflineSyncStatus(sync_status))
        
        if start_date:
            query = query.filter(OfflineSyncLog.sync_start_time >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(OfflineSyncLog.sync_start_time <= datetime.fromisoformat(end_date))
        
        logs = query.order_by(OfflineSyncLog.sync_start_time.desc()).limit(50).all()
        
        return jsonify([log.to_dict() for log in logs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Mobile App Settings
@mobile_enhancements_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_mobile_app_settings():
    """Get mobile app settings"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        device_id = request.args.get('device_id')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = MobileAppSetting.query.filter(
            MobileAppSetting.user_id == user_id,
            MobileAppSetting.company_id == company_id
        )
        
        if device_id:
            query = query.filter(MobileAppSetting.device_id == device_id)
        
        settings = query.all()
        
        return jsonify([setting.to_dict() for setting in settings])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mobile_enhancements_bp.route('/settings', methods=['POST'])
@jwt_required()
def create_mobile_app_setting():
    """Create mobile app setting"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['setting_name', 'setting_value', 'device_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create setting
        setting = MobileAppSetting(
            setting_name=data['setting_name'],
            setting_value=data['setting_value'],
            setting_type=data.get('setting_type', 'String'),
            user_id=user_id,
            device_id=data['device_id'],
            company_id=data['company_id']
        )
        
        db.session.add(setting)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('mobile_app_setting_created', setting.to_dict(), data['company_id'])
        
        return jsonify(setting.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mobile_enhancements_bp.route('/settings/<int:setting_id>', methods=['PUT'])
@jwt_required()
def update_mobile_app_setting(setting_id):
    """Update mobile app setting"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        setting = MobileAppSetting.query.filter(
            MobileAppSetting.id == setting_id,
            MobileAppSetting.user_id == user_id,
            MobileAppSetting.company_id == data.get('company_id')
        ).first()
        
        if not setting:
            return jsonify({'error': 'Setting not found'}), 404
        
        # Update fields
        for field in ['setting_name', 'setting_value', 'setting_type']:
            if field in data:
                setattr(setting, field, data[field])
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('mobile_app_setting_updated', setting.to_dict(), setting.company_id)
        
        return jsonify(setting.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
