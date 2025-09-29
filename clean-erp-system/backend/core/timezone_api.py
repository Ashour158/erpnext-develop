# Timezone Management API
# API endpoints for timezone-aware scheduling and event management

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from core.timezone_management import (
    TimezoneRule, UserTimezone, TimezoneConversion,
    get_timezone_info, convert_timezone, get_available_timezones,
    get_timezone_by_offset, get_business_hours, find_common_business_hours,
    schedule_event_across_timezones, get_timezone_aware_datetime,
    get_timezone_difference, is_business_hours, get_next_business_hour,
    create_timezone_conversion, get_user_timezone, set_user_timezone
)
from datetime import datetime, timedelta
import json

timezone_bp = Blueprint('timezone', __name__)

# Timezone Information
@timezone_bp.route('/timezones', methods=['GET'])
@jwt_required()
def get_timezones():
    """Get available timezones"""
    try:
        timezones = get_available_timezones()
        return jsonify(timezones)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timezone_bp.route('/timezones/info', methods=['GET'])
@jwt_required()
def get_timezone_info_endpoint():
    """Get timezone information"""
    try:
        timezone_name = request.args.get('timezone')
        
        if not timezone_name:
            return jsonify({'error': 'Timezone name is required'}), 400
        
        info = get_timezone_info(timezone_name)
        
        if 'error' in info:
            return jsonify({'error': info['error']}), 400
        
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timezone_bp.route('/timezones/by-offset', methods=['GET'])
@jwt_required()
def get_timezones_by_offset():
    """Get timezones by UTC offset"""
    try:
        offset_hours = request.args.get('offset', type=float)
        
        if offset_hours is None:
            return jsonify({'error': 'Offset is required'}), 400
        
        timezones = get_timezone_by_offset(offset_hours)
        return jsonify(timezones)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Timezone Conversion
@timezone_bp.route('/convert', methods=['POST'])
@jwt_required()
def convert_timezone_endpoint():
    """Convert datetime between timezones"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['source_timezone', 'target_timezone', 'datetime', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse datetime
        source_datetime = datetime.fromisoformat(data['datetime'])
        
        # Convert timezone
        target_datetime = convert_timezone(
            source_datetime,
            data['source_timezone'],
            data['target_timezone']
        )
        
        # Create conversion record
        conversion = create_timezone_conversion(
            user_id=user_id,
            source_timezone=data['source_timezone'],
            target_timezone=data['target_timezone'],
            source_datetime=source_datetime,
            company_id=data['company_id'],
            conversion_context=data.get('conversion_context'),
            conversion_notes=data.get('conversion_notes')
        )
        
        # Emit real-time update
        emit_realtime_update('timezone_converted', conversion.to_dict(), data['company_id'])
        
        return jsonify({
            'source_datetime': source_datetime.isoformat(),
            'target_datetime': target_datetime.isoformat(),
            'conversion': conversion.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timezone_bp.route('/conversions', methods=['GET'])
@jwt_required()
def get_timezone_conversions():
    """Get timezone conversions"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = TimezoneConversion.query.filter(
            TimezoneConversion.user_id == user_id,
            TimezoneConversion.company_id == company_id
        )
        
        if start_date:
            query = query.filter(TimezoneConversion.source_datetime >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(TimezoneConversion.source_datetime <= datetime.fromisoformat(end_date))
        
        conversions = query.order_by(TimezoneConversion.source_datetime.desc()).limit(100).all()
        
        return jsonify([conversion.to_dict() for conversion in conversions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Business Hours
@timezone_bp.route('/business-hours', methods=['GET'])
@jwt_required()
def get_business_hours_endpoint():
    """Get business hours for a timezone"""
    try:
        timezone_name = request.args.get('timezone')
        start_hour = request.args.get('start_hour', 9, type=int)
        end_hour = request.args.get('end_hour', 17, type=int)
        
        if not timezone_name:
            return jsonify({'error': 'Timezone name is required'}), 400
        
        business_hours = get_business_hours(timezone_name, start_hour, end_hour)
        
        if 'error' in business_hours:
            return jsonify({'error': business_hours['error']}), 400
        
        return jsonify(business_hours)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timezone_bp.route('/business-hours/common', methods=['POST'])
@jwt_required()
def get_common_business_hours():
    """Get common business hours across timezones"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['timezones']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        start_hour = data.get('start_hour', 9)
        end_hour = data.get('end_hour', 17)
        
        common_hours = find_common_business_hours(data['timezones'], start_hour, end_hour)
        
        if 'error' in common_hours:
            return jsonify({'error': common_hours['error']}), 400
        
        return jsonify(common_hours)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Event Scheduling
@timezone_bp.route('/schedule-event', methods=['POST'])
@jwt_required()
def schedule_event():
    """Schedule event across timezones"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['event_datetime', 'timezones']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse datetime
        event_datetime = datetime.fromisoformat(data['event_datetime'])
        duration_hours = data.get('duration_hours', 1.0)
        
        # Schedule event
        scheduled_event = schedule_event_across_timezones(
            event_datetime,
            data['timezones'],
            duration_hours
        )
        
        if 'error' in scheduled_event:
            return jsonify({'error': scheduled_event['error']}), 400
        
        return jsonify(scheduled_event)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timezone_bp.route('/next-business-hour', methods=['POST'])
@jwt_required()
def get_next_business_hour_endpoint():
    """Get next business hour"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['datetime', 'timezone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse datetime
        dt = datetime.fromisoformat(data['datetime'])
        start_hour = data.get('start_hour', 9)
        end_hour = data.get('end_hour', 17)
        
        # Get next business hour
        next_hour = get_next_business_hour(dt, data['timezone'], start_hour, end_hour)
        
        return jsonify({
            'current_datetime': dt.isoformat(),
            'next_business_hour': next_hour.isoformat(),
            'timezone': data['timezone']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Timezone Management
@timezone_bp.route('/user-timezone', methods=['GET'])
@jwt_required()
def get_user_timezone_endpoint():
    """Get user's timezone"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        timezone = get_user_timezone(user_id, company_id)
        
        if not timezone:
            return jsonify({'error': 'User timezone not set'}), 404
        
        return jsonify({'timezone': timezone})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timezone_bp.route('/user-timezone', methods=['POST'])
@jwt_required()
def set_user_timezone_endpoint():
    """Set user's timezone"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['timezone', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Set user timezone
        user_tz = set_user_timezone(
            user_id=user_id,
            timezone=data['timezone'],
            company_id=data['company_id'],
            is_primary=data.get('is_primary', True)
        )
        
        # Emit real-time update
        emit_realtime_update('user_timezone_set', user_tz.to_dict(), data['company_id'])
        
        return jsonify(user_tz.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timezone_bp.route('/user-timezone', methods=['PUT'])
@jwt_required()
def update_user_timezone():
    """Update user's timezone"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['timezone', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Update user timezone
        user_tz = set_user_timezone(
            user_id=user_id,
            timezone=data['timezone'],
            company_id=data['company_id'],
            is_primary=data.get('is_primary', True)
        )
        
        # Emit real-time update
        emit_realtime_update('user_timezone_updated', user_tz.to_dict(), data['company_id'])
        
        return jsonify(user_tz.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Timezone Rules
@timezone_bp.route('/rules', methods=['GET'])
@jwt_required()
def get_timezone_rules():
    """Get timezone rules"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        rules = TimezoneRule.query.filter(
            TimezoneRule.company_id == company_id,
            TimezoneRule.is_active == True
        ).all()
        
        return jsonify([rule.to_dict() for rule in rules])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timezone_bp.route('/rules', methods=['POST'])
@jwt_required()
def create_timezone_rule():
    """Create timezone rule"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['rule_name', 'timezone', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create rule
        rule = TimezoneRule(
            rule_name=data['rule_name'],
            rule_description=data.get('rule_description'),
            timezone=data['timezone'],
            timezone_display=data.get('timezone_display'),
            utc_offset=data.get('utc_offset', 0.0),
            dst_offset=data.get('dst_offset', 0.0),
            dst_start_rule=data.get('dst_start_rule'),
            dst_end_rule=data.get('dst_end_rule'),
            dst_enabled=data.get('dst_enabled', True),
            company_id=data['company_id']
        )
        
        db.session.add(rule)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('timezone_rule_created', rule.to_dict(), data['company_id'])
        
        return jsonify(rule.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@timezone_bp.route('/rules/<int:rule_id>', methods=['GET'])
@jwt_required()
def get_timezone_rule(rule_id):
    """Get specific timezone rule"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        rule = TimezoneRule.query.filter(
            TimezoneRule.id == rule_id,
            TimezoneRule.company_id == company_id
        ).first()
        
        if not rule:
            return jsonify({'error': 'Rule not found'}), 404
        
        return jsonify(rule.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timezone_bp.route('/rules/<int:rule_id>', methods=['PUT'])
@jwt_required()
def update_timezone_rule(rule_id):
    """Update timezone rule"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        rule = TimezoneRule.query.filter(
            TimezoneRule.id == rule_id,
            TimezoneRule.company_id == data.get('company_id')
        ).first()
        
        if not rule:
            return jsonify({'error': 'Rule not found'}), 404
        
        # Update fields
        for field in ['rule_name', 'rule_description', 'is_active', 'timezone',
                     'timezone_display', 'utc_offset', 'dst_offset', 'dst_start_rule',
                     'dst_end_rule', 'dst_enabled']:
            if field in data:
                setattr(rule, field, data[field])
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('timezone_rule_updated', rule.to_dict(), rule.company_id)
        
        return jsonify(rule.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@timezone_bp.route('/rules/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_timezone_rule(rule_id):
    """Delete timezone rule"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        rule = TimezoneRule.query.filter(
            TimezoneRule.id == rule_id,
            TimezoneRule.company_id == company_id
        ).first()
        
        if not rule:
            return jsonify({'error': 'Rule not found'}), 404
        
        # Soft delete
        rule.is_active = False
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('timezone_rule_deleted', {'id': rule_id}, company_id)
        
        return jsonify({'message': 'Rule deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Timezone Difference
@timezone_bp.route('/difference', methods=['GET'])
@jwt_required()
def get_timezone_difference_endpoint():
    """Get time difference between timezones"""
    try:
        tz1 = request.args.get('timezone1')
        tz2 = request.args.get('timezone2')
        
        if not tz1 or not tz2:
            return jsonify({'error': 'Both timezone1 and timezone2 are required'}), 400
        
        difference = get_timezone_difference(tz1, tz2)
        
        return jsonify({
            'timezone1': tz1,
            'timezone2': tz2,
            'difference_hours': difference
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Business Hours Check
@timezone_bp.route('/is-business-hours', methods=['GET'])
@jwt_required()
def is_business_hours_endpoint():
    """Check if datetime is within business hours"""
    try:
        datetime_str = request.args.get('datetime')
        timezone_name = request.args.get('timezone')
        start_hour = request.args.get('start_hour', 9, type=int)
        end_hour = request.args.get('end_hour', 17, type=int)
        
        if not datetime_str or not timezone_name:
            return jsonify({'error': 'Datetime and timezone are required'}), 400
        
        # Parse datetime
        dt = datetime.fromisoformat(datetime_str)
        
        # Check business hours
        is_business = is_business_hours(dt, timezone_name, start_hour, end_hour)
        
        return jsonify({
            'datetime': datetime_str,
            'timezone': timezone_name,
            'is_business_hours': is_business,
            'start_hour': start_hour,
            'end_hour': end_hour
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
