# Calendar API
# API endpoints for calendar management, event booking, and external integrations

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.auth import has_permission
from core.realtime_sync import emit_realtime_update
from .models import (
    Calendar, CalendarEvent, EventAttendance, EventGeolocation, 
    CalendarShare, UserAvailability, ExternalCalendarIntegration,
    EventType, EventStatus, RecurrenceType, CalendarType, AvailabilityStatus
)
from datetime import datetime, timedelta
import json

calendar_bp = Blueprint('calendar', __name__)

# Calendar Management
@calendar_bp.route('/calendars', methods=['GET'])
@jwt_required()
def get_calendars():
    """Get all calendars for the user"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        # Get user's calendars and shared calendars
        calendars = Calendar.query.filter(
            db.or_(
                Calendar.owner_id == user_id,
                Calendar.id.in_(
                    db.session.query(CalendarShare.calendar_id).filter(
                        CalendarShare.shared_with_id == user_id,
                        CalendarShare.is_active == True
                    )
                )
            ),
            Calendar.company_id == company_id,
            Calendar.is_active == True
        ).all()
        
        return jsonify([calendar.to_dict() for calendar in calendars])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/calendars', methods=['POST'])
@jwt_required()
def create_calendar():
    """Create a new calendar"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['calendar_name', 'calendar_type', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create calendar
        calendar = Calendar(
            calendar_name=data['calendar_name'],
            calendar_description=data.get('calendar_description'),
            calendar_type=CalendarType(data['calendar_type']),
            color=data.get('color', '#3498db'),
            is_public=data.get('is_public', False),
            timezone=data.get('timezone', 'UTC'),
            owner_id=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(calendar)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('calendar_created', calendar.to_dict(), data['company_id'])
        
        return jsonify(calendar.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/calendars/<int:calendar_id>', methods=['GET'])
@jwt_required()
def get_calendar(calendar_id):
    """Get a specific calendar"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        calendar = Calendar.query.filter(
            Calendar.id == calendar_id,
            Calendar.company_id == company_id,
            Calendar.is_active == True
        ).first()
        
        if not calendar:
            return jsonify({'error': 'Calendar not found'}), 404
        
        # Check if user has access
        if calendar.owner_id != user_id and not CalendarShare.query.filter(
            CalendarShare.calendar_id == calendar_id,
            CalendarShare.shared_with_id == user_id,
            CalendarShare.is_active == True
        ).first():
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(calendar.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/calendars/<int:calendar_id>', methods=['PUT'])
@jwt_required()
def update_calendar(calendar_id):
    """Update a calendar"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        calendar = Calendar.query.filter(
            Calendar.id == calendar_id,
            Calendar.owner_id == user_id,
            Calendar.is_active == True
        ).first()
        
        if not calendar:
            return jsonify({'error': 'Calendar not found'}), 404
        
        # Update fields
        for field in ['calendar_name', 'calendar_description', 'color', 'is_public', 'timezone']:
            if field in data:
                setattr(calendar, field, data[field])
        
        if 'calendar_type' in data:
            calendar.calendar_type = CalendarType(data['calendar_type'])
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('calendar_updated', calendar.to_dict(), calendar.company_id)
        
        return jsonify(calendar.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/calendars/<int:calendar_id>', methods=['DELETE'])
@jwt_required()
def delete_calendar(calendar_id):
    """Delete a calendar"""
    try:
        user_id = get_jwt_identity()
        
        calendar = Calendar.query.filter(
            Calendar.id == calendar_id,
            Calendar.owner_id == user_id,
            Calendar.is_active == True
        ).first()
        
        if not calendar:
            return jsonify({'error': 'Calendar not found'}), 404
        
        # Soft delete
        calendar.is_active = False
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('calendar_deleted', {'id': calendar_id}, calendar.company_id)
        
        return jsonify({'message': 'Calendar deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Event Management
@calendar_bp.route('/events', methods=['GET'])
@jwt_required()
def get_events():
    """Get events for a calendar or date range"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        calendar_id = request.args.get('calendar_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        # Build query
        query = CalendarEvent.query.filter(CalendarEvent.company_id == company_id)
        
        if calendar_id:
            query = query.filter(CalendarEvent.calendar_id == calendar_id)
        
        if start_date:
            query = query.filter(CalendarEvent.start_datetime >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(CalendarEvent.end_datetime <= datetime.fromisoformat(end_date))
        
        events = query.all()
        
        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/events', methods=['POST'])
@jwt_required()
def create_event():
    """Create a new event"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['event_title', 'start_datetime', 'end_datetime', 'calendar_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create event
        event = CalendarEvent(
            event_title=data['event_title'],
            event_description=data.get('event_description'),
            event_type=EventType(data.get('event_type', 'CUSTOM')),
            start_datetime=datetime.fromisoformat(data['start_datetime']),
            end_datetime=datetime.fromisoformat(data['end_datetime']),
            all_day=data.get('all_day', False),
            timezone=data.get('timezone', 'UTC'),
            recurrence_type=RecurrenceType(data.get('recurrence_type', 'NONE')),
            recurrence_pattern=data.get('recurrence_pattern'),
            recurrence_end=datetime.fromisoformat(data['recurrence_end']) if data.get('recurrence_end') else None,
            location=data.get('location'),
            location_coordinates=data.get('location_coordinates'),
            location_address=data.get('location_address'),
            location_radius=data.get('location_radius', 0.0),
            attendees=data.get('attendees', []),
            organizer_id=user_id,
            calendar_id=data['calendar_id'],
            related_entity_type=data.get('related_entity_type'),
            related_entity_id=data.get('related_entity_id'),
            reminder_minutes=data.get('reminder_minutes', 15),
            company_id=data['company_id']
        )
        
        db.session.add(event)
        db.session.commit()
        
        # Create attendance records for attendees
        if data.get('attendees'):
            for attendee_id in data['attendees']:
                attendance = EventAttendance(
                    event_id=event.id,
                    attendee_id=attendee_id,
                    company_id=data['company_id']
                )
                db.session.add(attendance)
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('event_created', event.to_dict(), data['company_id'])
        
        return jsonify(event.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/events/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    """Get a specific event"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        event = CalendarEvent.query.filter(
            CalendarEvent.id == event_id,
            CalendarEvent.company_id == company_id
        ).first()
        
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        return jsonify(event.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/events/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """Update an event"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        event = CalendarEvent.query.filter(
            CalendarEvent.id == event_id,
            CalendarEvent.organizer_id == user_id
        ).first()
        
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Update fields
        for field in ['event_title', 'event_description', 'location', 'location_address', 'location_radius']:
            if field in data:
                setattr(event, field, data[field])
        
        if 'event_type' in data:
            event.event_type = EventType(data['event_type'])
        
        if 'event_status' in data:
            event.event_status = EventStatus(data['event_status'])
        
        if 'start_datetime' in data:
            event.start_datetime = datetime.fromisoformat(data['start_datetime'])
        
        if 'end_datetime' in data:
            event.end_datetime = datetime.fromisoformat(data['end_datetime'])
        
        if 'location_coordinates' in data:
            event.location_coordinates = data['location_coordinates']
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('event_updated', event.to_dict(), event.company_id)
        
        return jsonify(event.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/events/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    """Delete an event"""
    try:
        user_id = get_jwt_identity()
        
        event = CalendarEvent.query.filter(
            CalendarEvent.id == event_id,
            CalendarEvent.organizer_id == user_id
        ).first()
        
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        company_id = event.company_id
        db.session.delete(event)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('event_deleted', {'id': event_id}, company_id)
        
        return jsonify({'message': 'Event deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Event Attendance
@calendar_bp.route('/events/<int:event_id>/attendance', methods=['GET'])
@jwt_required()
def get_event_attendance(event_id):
    """Get attendance for an event"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        attendance = EventAttendance.query.filter(
            EventAttendance.event_id == event_id,
            EventAttendance.company_id == company_id
        ).all()
        
        return jsonify([att.to_dict() for att in attendance])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/events/<int:event_id>/attendance', methods=['POST'])
@jwt_required()
def update_event_attendance(event_id):
    """Update attendance for an event"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        attendance = EventAttendance.query.filter(
            EventAttendance.event_id == event_id,
            EventAttendance.attendee_id == user_id
        ).first()
        
        if not attendance:
            return jsonify({'error': 'Attendance record not found'}), 404
        
        # Update attendance
        if 'attendance_status' in data:
            attendance.attendance_status = data['attendance_status']
        
        if 'notes' in data:
            attendance.notes = data['notes']
        
        attendance.response_date = datetime.utcnow()
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('attendance_updated', attendance.to_dict(), attendance.company_id)
        
        return jsonify(attendance.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Geolocation Tracking
@calendar_bp.route('/events/<int:event_id>/check-in', methods=['POST'])
@jwt_required()
def check_in_event(event_id):
    """Check in to an event with geolocation"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['latitude', 'longitude', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Get event
        event = CalendarEvent.query.filter(
            CalendarEvent.id == event_id,
            CalendarEvent.company_id == data['company_id']
        ).first()
        
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Update attendance
        attendance = EventAttendance.query.filter(
            EventAttendance.event_id == event_id,
            EventAttendance.attendee_id == user_id
        ).first()
        
        if attendance:
            attendance.check_in_time = datetime.utcnow()
            attendance.check_in_location = {
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'accuracy': data.get('accuracy', 0.0),
                'address': data.get('address'),
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Create geolocation record
        geolocation = EventGeolocation(
            latitude=data['latitude'],
            longitude=data['longitude'],
            accuracy=data.get('accuracy', 0.0),
            altitude=data.get('altitude', 0.0),
            speed=data.get('speed', 0.0),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            country=data.get('country'),
            postal_code=data.get('postal_code'),
            event_id=event_id,
            user_id=user_id,
            tracking_type='Check-in',
            device_info=data.get('device_info'),
            company_id=data['company_id']
        )
        
        db.session.add(geolocation)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('event_check_in', {
            'event_id': event_id,
            'user_id': user_id,
            'location': geolocation.to_dict()
        }, data['company_id'])
        
        return jsonify(geolocation.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/events/<int:event_id>/check-out', methods=['POST'])
@jwt_required()
def check_out_event(event_id):
    """Check out from an event with geolocation"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['latitude', 'longitude', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Update attendance
        attendance = EventAttendance.query.filter(
            EventAttendance.event_id == event_id,
            EventAttendance.attendee_id == user_id
        ).first()
        
        if attendance:
            attendance.check_out_time = datetime.utcnow()
            attendance.check_out_location = {
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'accuracy': data.get('accuracy', 0.0),
                'address': data.get('address'),
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Create geolocation record
        geolocation = EventGeolocation(
            latitude=data['latitude'],
            longitude=data['longitude'],
            accuracy=data.get('accuracy', 0.0),
            altitude=data.get('altitude', 0.0),
            speed=data.get('speed', 0.0),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            country=data.get('country'),
            postal_code=data.get('postal_code'),
            event_id=event_id,
            user_id=user_id,
            tracking_type='Check-out',
            device_info=data.get('device_info'),
            company_id=data['company_id']
        )
        
        db.session.add(geolocation)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('event_check_out', {
            'event_id': event_id,
            'user_id': user_id,
            'location': geolocation.to_dict()
        }, data['company_id'])
        
        return jsonify(geolocation.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Availability
@calendar_bp.route('/availability', methods=['GET'])
@jwt_required()
def get_user_availability():
    """Get user availability"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        # Build query
        query = UserAvailability.query.filter(
            UserAvailability.user_id == user_id,
            UserAvailability.company_id == company_id
        )
        
        if start_date:
            query = query.filter(UserAvailability.start_datetime >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(UserAvailability.end_datetime <= datetime.fromisoformat(end_date))
        
        availability = query.all()
        
        return jsonify([av.to_dict() for av in availability])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/availability', methods=['POST'])
@jwt_required()
def set_user_availability():
    """Set user availability"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['start_datetime', 'end_datetime', 'availability_status', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create availability
        availability = UserAvailability(
            availability_status=AvailabilityStatus(data['availability_status']),
            status_message=data.get('status_message'),
            start_datetime=datetime.fromisoformat(data['start_datetime']),
            end_datetime=datetime.fromisoformat(data['end_datetime']),
            user_id=user_id,
            location=data.get('location'),
            location_coordinates=data.get('location_coordinates'),
            is_recurring=data.get('is_recurring', False),
            recurrence_pattern=data.get('recurrence_pattern'),
            company_id=data['company_id']
        )
        
        db.session.add(availability)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('availability_updated', availability.to_dict(), data['company_id'])
        
        return jsonify(availability.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# External Calendar Integration
@calendar_bp.route('/integrations', methods=['GET'])
@jwt_required()
def get_calendar_integrations():
    """Get calendar integrations"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        integrations = ExternalCalendarIntegration.query.filter(
            ExternalCalendarIntegration.user_id == user_id,
            ExternalCalendarIntegration.company_id == company_id,
            ExternalCalendarIntegration.is_active == True
        ).all()
        
        return jsonify([integration.to_dict() for integration in integrations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/integrations', methods=['POST'])
@jwt_required()
def create_calendar_integration():
    """Create a calendar integration"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['provider', 'integration_name', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create integration
        integration = ExternalCalendarIntegration(
            provider=data['provider'],
            integration_name=data['integration_name'],
            access_token=data.get('access_token'),
            refresh_token=data.get('refresh_token'),
            token_expires=datetime.fromisoformat(data['token_expires']) if data.get('token_expires') else None,
            sync_enabled=data.get('sync_enabled', True),
            sync_direction=data.get('sync_direction', 'Bidirectional'),
            sync_frequency=data.get('sync_frequency', 15),
            user_id=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(integration)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('integration_created', integration.to_dict(), data['company_id'])
        
        return jsonify(integration.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/integrations/<int:integration_id>/sync', methods=['POST'])
@jwt_required()
def sync_calendar_integration(integration_id):
    """Sync calendar integration"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        integration = ExternalCalendarIntegration.query.filter(
            ExternalCalendarIntegration.id == integration_id,
            ExternalCalendarIntegration.user_id == user_id,
            ExternalCalendarIntegration.company_id == company_id,
            ExternalCalendarIntegration.is_active == True
        ).first()
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # Update last sync
        integration.last_sync = datetime.utcnow()
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('integration_synced', integration.to_dict(), company_id)
        
        return jsonify({'message': 'Sync completed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
