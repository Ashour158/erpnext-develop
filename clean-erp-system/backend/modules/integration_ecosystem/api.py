# Integration Ecosystem API
# API endpoints for integration ecosystem with IoT device integration, wearable technology support, third-party APIs, and webhook system

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from .models import (
    IoTDevice, WearableDevice, DeviceData, ThirdPartyIntegration,
    WebhookSubscription, WebhookEvent, DataSyncLog, SmartOfficeDevice,
    DeviceType, DeviceStatus, IntegrationType, WebhookEvent as WebhookEventEnum
)
from datetime import datetime, timedelta, date
import json

integration_ecosystem_bp = Blueprint('integration_ecosystem', __name__)

# IoT Devices
@integration_ecosystem_bp.route('/iot-devices', methods=['GET'])
@jwt_required()
def get_iot_devices():
    """Get IoT devices"""
    try:
        company_id = request.args.get('company_id', type=int)
        device_type = request.args.get('device_type')
        device_status = request.args.get('device_status')
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = IoTDevice.query.filter(IoTDevice.company_id == company_id)
        
        if device_type:
            query = query.filter(IoTDevice.device_type == DeviceType(device_type))
        
        if device_status:
            query = query.filter(IoTDevice.device_status == DeviceStatus(device_status))
        
        if is_active is not None:
            query = query.filter(IoTDevice.is_active == is_active)
        
        devices = query.order_by(IoTDevice.last_seen.desc()).all()
        
        return jsonify([device.to_dict() for device in devices])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_ecosystem_bp.route('/iot-devices', methods=['POST'])
@jwt_required()
def create_iot_device():
    """Create IoT device"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['device_name', 'device_type', 'serial_number', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create device
        device = IoTDevice(
            device_name=data['device_name'],
            device_description=data.get('device_description'),
            device_type=DeviceType(data['device_type']),
            device_model=data.get('device_model'),
            manufacturer=data.get('manufacturer'),
            serial_number=data['serial_number'],
            device_status=DeviceStatus(data.get('device_status', 'UNKNOWN')),
            is_active=data.get('is_active', True),
            battery_level=data.get('battery_level', 0.0),
            signal_strength=data.get('signal_strength', 0.0),
            location_name=data.get('location_name'),
            location_coordinates=data.get('location_coordinates'),
            installation_date=date.fromisoformat(data['installation_date']) if data.get('installation_date') else None,
            capabilities=data.get('capabilities'),
            sensors=data.get('sensors'),
            actuators=data.get('actuators'),
            device_config=data.get('device_config'),
            calibration_data=data.get('calibration_data'),
            company_id=data['company_id']
        )
        
        db.session.add(device)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('iot_device_created', device.to_dict(), data['company_id'])
        
        return jsonify(device.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@integration_ecosystem_bp.route('/iot-devices/<int:device_id>', methods=['GET'])
@jwt_required()
def get_iot_device(device_id):
    """Get specific IoT device"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        device = IoTDevice.query.filter(
            IoTDevice.id == device_id,
            IoTDevice.company_id == company_id
        ).first()
        
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        return jsonify(device.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_ecosystem_bp.route('/iot-devices/<int:device_id>', methods=['PUT'])
@jwt_required()
def update_iot_device(device_id):
    """Update IoT device"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        device = IoTDevice.query.filter(
            IoTDevice.id == device_id,
            IoTDevice.company_id == data.get('company_id')
        ).first()
        
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        # Update fields
        for field in ['device_name', 'device_description', 'device_model', 'manufacturer',
                     'is_active', 'battery_level', 'signal_strength', 'location_name',
                     'location_coordinates', 'capabilities', 'sensors', 'actuators',
                     'device_config', 'calibration_data']:
            if field in data:
                setattr(device, field, data[field])
        
        if 'device_type' in data:
            device.device_type = DeviceType(data['device_type'])
        
        if 'device_status' in data:
            device.device_status = DeviceStatus(data['device_status'])
        
        if 'installation_date' in data and data['installation_date']:
            device.installation_date = date.fromisoformat(data['installation_date'])
        
        device.last_seen = datetime.utcnow()
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('iot_device_updated', device.to_dict(), device.company_id)
        
        return jsonify(device.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Wearable Devices
@integration_ecosystem_bp.route('/wearable-devices', methods=['GET'])
@jwt_required()
def get_wearable_devices():
    """Get wearable devices"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        device_type = request.args.get('device_type')
        device_status = request.args.get('device_status')
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = WearableDevice.query.filter(WearableDevice.company_id == company_id)
        
        if device_type:
            query = query.filter(WearableDevice.device_type == device_type)
        
        if device_status:
            query = query.filter(WearableDevice.device_status == DeviceStatus(device_status))
        
        if is_active is not None:
            query = query.filter(WearableDevice.is_active == is_active)
        
        devices = query.order_by(WearableDevice.last_synced.desc()).all()
        
        return jsonify([device.to_dict() for device in devices])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_ecosystem_bp.route('/wearable-devices', methods=['POST'])
@jwt_required()
def create_wearable_device():
    """Create wearable device"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['device_name', 'device_type', 'serial_number', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create device
        device = WearableDevice(
            device_name=data['device_name'],
            device_type=data['device_type'],
            manufacturer=data.get('manufacturer'),
            model=data.get('model'),
            serial_number=data['serial_number'],
            user_id=data.get('user_id', user_id),
            device_status=DeviceStatus(data.get('device_status', 'UNKNOWN')),
            is_active=data.get('is_active', True),
            battery_level=data.get('battery_level', 0.0),
            heart_rate=data.get('heart_rate', 0.0),
            steps_count=data.get('steps_count', 0),
            calories_burned=data.get('calories_burned', 0.0),
            sleep_hours=data.get('sleep_hours', 0.0),
            stress_level=data.get('stress_level', 0.0),
            capabilities=data.get('capabilities'),
            sensors=data.get('sensors'),
            supported_metrics=data.get('supported_metrics'),
            device_config=data.get('device_config'),
            sync_settings=data.get('sync_settings'),
            company_id=data['company_id']
        )
        
        db.session.add(device)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('wearable_device_created', device.to_dict(), data['company_id'])
        
        return jsonify(device.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Device Data
@integration_ecosystem_bp.route('/device-data', methods=['GET'])
@jwt_required()
def get_device_data():
    """Get device data"""
    try:
        company_id = request.args.get('company_id', type=int)
        device_id = request.args.get('device_id', type=int)
        wearable_device_id = request.args.get('wearable_device_id', type=int)
        data_type = request.args.get('data_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = DeviceData.query.filter(DeviceData.company_id == company_id)
        
        if device_id:
            query = query.filter(DeviceData.device_id == device_id)
        
        if wearable_device_id:
            query = query.filter(DeviceData.wearable_device_id == wearable_device_id)
        
        if data_type:
            query = query.filter(DeviceData.data_type == data_type)
        
        if start_date:
            query = query.filter(DeviceData.data_timestamp >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(DeviceData.data_timestamp <= datetime.fromisoformat(end_date))
        
        data = query.order_by(DeviceData.data_timestamp.desc()).limit(1000).all()
        
        return jsonify([record.to_dict() for record in data])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_ecosystem_bp.route('/device-data', methods=['POST'])
@jwt_required()
def create_device_data():
    """Create device data"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['data_type', 'data_value', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create device data
        device_data = DeviceData(
            data_type=data['data_type'],
            data_value=data['data_value'],
            data_unit=data.get('data_unit', ''),
            data_timestamp=datetime.fromisoformat(data['data_timestamp']) if data.get('data_timestamp') else datetime.utcnow(),
            device_id=data.get('device_id'),
            wearable_device_id=data.get('wearable_device_id'),
            data_quality=data.get('data_quality', 1.0),
            is_validated=data.get('is_validated', False),
            validation_notes=data.get('validation_notes'),
            metadata=data.get('metadata'),
            raw_data=data.get('raw_data'),
            company_id=data['company_id']
        )
        
        db.session.add(device_data)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('device_data_created', device_data.to_dict(), data['company_id'])
        
        return jsonify(device_data.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Third-Party Integrations
@integration_ecosystem_bp.route('/integrations', methods=['GET'])
@jwt_required()
def get_third_party_integrations():
    """Get third-party integrations"""
    try:
        company_id = request.args.get('company_id', type=int)
        integration_type = request.args.get('integration_type')
        provider_name = request.args.get('provider_name')
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = ThirdPartyIntegration.query.filter(ThirdPartyIntegration.company_id == company_id)
        
        if integration_type:
            query = query.filter(ThirdPartyIntegration.integration_type == IntegrationType(integration_type))
        
        if provider_name:
            query = query.filter(ThirdPartyIntegration.provider_name == provider_name)
        
        if is_active is not None:
            query = query.filter(ThirdPartyIntegration.is_active == is_active)
        
        integrations = query.order_by(ThirdPartyIntegration.created_at.desc()).all()
        
        return jsonify([integration.to_dict() for integration in integrations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_ecosystem_bp.route('/integrations', methods=['POST'])
@jwt_required()
def create_third_party_integration():
    """Create third-party integration"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['integration_name', 'integration_type', 'provider_name', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create integration
        integration = ThirdPartyIntegration(
            integration_name=data['integration_name'],
            integration_description=data.get('integration_description'),
            integration_type=IntegrationType(data['integration_type']),
            provider_name=data['provider_name'],
            provider_url=data.get('provider_url'),
            api_key=data.get('api_key'),
            api_secret=data.get('api_secret'),
            access_token=data.get('access_token'),
            refresh_token=data.get('refresh_token'),
            token_expires=datetime.fromisoformat(data['token_expires']) if data.get('token_expires') else None,
            is_active=data.get('is_active', True),
            sync_enabled=data.get('sync_enabled', True),
            sync_frequency=data.get('sync_frequency', 15),
            rate_limit=data.get('rate_limit', 1000),
            integration_config=data.get('integration_config'),
            webhook_url=data.get('webhook_url'),
            webhook_secret=data.get('webhook_secret'),
            company_id=data['company_id']
        )
        
        db.session.add(integration)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('third_party_integration_created', integration.to_dict(), data['company_id'])
        
        return jsonify(integration.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Webhook Subscriptions
@integration_ecosystem_bp.route('/webhooks', methods=['GET'])
@jwt_required()
def get_webhook_subscriptions():
    """Get webhook subscriptions"""
    try:
        company_id = request.args.get('company_id', type=int)
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = WebhookSubscription.query.filter(WebhookSubscription.company_id == company_id)
        
        if is_active is not None:
            query = query.filter(WebhookSubscription.is_active == is_active)
        
        subscriptions = query.order_by(WebhookSubscription.created_at.desc()).all()
        
        return jsonify([subscription.to_dict() for subscription in subscriptions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_ecosystem_bp.route('/webhooks', methods=['POST'])
@jwt_required()
def create_webhook_subscription():
    """Create webhook subscription"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['subscription_name', 'webhook_url', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create subscription
        subscription = WebhookSubscription(
            subscription_name=data['subscription_name'],
            webhook_url=data['webhook_url'],
            webhook_secret=data.get('webhook_secret'),
            is_active=data.get('is_active', True),
            subscribed_events=data.get('subscribed_events'),
            event_filters=data.get('event_filters'),
            retry_count=data.get('retry_count', 3),
            timeout_seconds=data.get('timeout_seconds', 30),
            delivery_method=data.get('delivery_method', 'POST'),
            content_type=data.get('content_type', 'application/json'),
            headers=data.get('headers'),
            company_id=data['company_id']
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('webhook_subscription_created', subscription.to_dict(), data['company_id'])
        
        return jsonify(subscription.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Webhook Events
@integration_ecosystem_bp.route('/webhook-events', methods=['GET'])
@jwt_required()
def get_webhook_events():
    """Get webhook events"""
    try:
        company_id = request.args.get('company_id', type=int)
        event_type = request.args.get('event_type')
        delivery_status = request.args.get('delivery_status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = WebhookEvent.query.filter(WebhookEvent.company_id == company_id)
        
        if event_type:
            query = query.filter(WebhookEvent.event_type == WebhookEventEnum(event_type))
        
        if delivery_status:
            query = query.filter(WebhookEvent.delivery_status == delivery_status)
        
        if start_date:
            query = query.filter(WebhookEvent.event_timestamp >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(WebhookEvent.event_timestamp <= datetime.fromisoformat(end_date))
        
        events = query.order_by(WebhookEvent.event_timestamp.desc()).limit(100).all()
        
        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Data Sync Logs
@integration_ecosystem_bp.route('/sync-logs', methods=['GET'])
@jwt_required()
def get_data_sync_logs():
    """Get data sync logs"""
    try:
        company_id = request.args.get('company_id', type=int)
        sync_type = request.args.get('sync_type')
        source_system = request.args.get('source_system')
        target_system = request.args.get('target_system')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = DataSyncLog.query.filter(DataSyncLog.company_id == company_id)
        
        if sync_type:
            query = query.filter(DataSyncLog.sync_type == sync_type)
        
        if source_system:
            query = query.filter(DataSyncLog.source_system == source_system)
        
        if target_system:
            query = query.filter(DataSyncLog.target_system == target_system)
        
        if start_date:
            query = query.filter(DataSyncLog.sync_start_time >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(DataSyncLog.sync_start_time <= datetime.fromisoformat(end_date))
        
        logs = query.order_by(DataSyncLog.sync_start_time.desc()).limit(100).all()
        
        return jsonify([log.to_dict() for log in logs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Smart Office Devices
@integration_ecosystem_bp.route('/smart-office-devices', methods=['GET'])
@jwt_required()
def get_smart_office_devices():
    """Get smart office devices"""
    try:
        company_id = request.args.get('company_id', type=int)
        device_type = request.args.get('device_type')
        device_status = request.args.get('device_status')
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = SmartOfficeDevice.query.filter(SmartOfficeDevice.company_id == company_id)
        
        if device_type:
            query = query.filter(SmartOfficeDevice.device_type == device_type)
        
        if device_status:
            query = query.filter(SmartOfficeDevice.device_status == DeviceStatus(device_status))
        
        if is_active is not None:
            query = query.filter(SmartOfficeDevice.is_active == is_active)
        
        devices = query.order_by(SmartOfficeDevice.last_updated.desc()).all()
        
        return jsonify([device.to_dict() for device in devices])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_ecosystem_bp.route('/smart-office-devices', methods=['POST'])
@jwt_required()
def create_smart_office_device():
    """Create smart office device"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['device_name', 'device_type', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create device
        device = SmartOfficeDevice(
            device_name=data['device_name'],
            device_type=data['device_type'],
            location=data.get('location'),
            room_number=data.get('room_number'),
            device_status=DeviceStatus(data.get('device_status', 'UNKNOWN')),
            is_active=data.get('is_active', True),
            current_value=data.get('current_value', 0.0),
            target_value=data.get('target_value', 0.0),
            unit=data.get('unit'),
            automation_enabled=data.get('automation_enabled', False),
            automation_rules=data.get('automation_rules'),
            schedule=data.get('schedule'),
            company_id=data['company_id']
        )
        
        db.session.add(device)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('smart_office_device_created', device.to_dict(), data['company_id'])
        
        return jsonify(device.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@integration_ecosystem_bp.route('/smart-office-devices/<int:device_id>', methods=['PUT'])
@jwt_required()
def update_smart_office_device(device_id):
    """Update smart office device"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        device = SmartOfficeDevice.query.filter(
            SmartOfficeDevice.id == device_id,
            SmartOfficeDevice.company_id == data.get('company_id')
        ).first()
        
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        # Update fields
        for field in ['device_name', 'device_type', 'location', 'room_number',
                     'is_active', 'current_value', 'target_value', 'unit',
                     'automation_enabled', 'automation_rules', 'schedule']:
            if field in data:
                setattr(device, field, data[field])
        
        if 'device_status' in data:
            device.device_status = DeviceStatus(data['device_status'])
        
        device.last_updated = datetime.utcnow()
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('smart_office_device_updated', device.to_dict(), device.company_id)
        
        return jsonify(device.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
