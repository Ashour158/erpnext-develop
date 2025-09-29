# Advanced Calendar API
# API endpoints for advanced calendar features including recurring event intelligence, meeting room integration, and smart scheduling

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from .models import (
    RecurringEvent, EventOccurrence, MeetingRoom, RoomBooking,
    CalendarIntegration, CalendarEvent, CalendarReminder, CalendarConflict,
    RecurrencePattern, MeetingRoomStatus, EventPriority, EventStatus
)
from datetime import datetime, timedelta, date, time
import json

advanced_calendar_bp = Blueprint('advanced_calendar', __name__)

# Recurring Events
@advanced_calendar_bp.route('/recurring-events', methods=['GET'])
@jwt_required()
def get_recurring_events():
    """Get recurring events"""
    try:
        company_id = request.args.get('company_id', type=int)
        recurrence_pattern = request.args.get('recurrence_pattern')
        event_type = request.args.get('event_type')
        status = request.args.get('status')
        organizer_id = request.args.get('organizer_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = RecurringEvent.query.filter(RecurringEvent.company_id == company_id)
        
        if recurrence_pattern:
            query = query.filter(RecurringEvent.recurrence_pattern == RecurrencePattern(recurrence_pattern))
        
        if event_type:
            query = query.filter(RecurringEvent.event_type == event_type)
        
        if status:
            query = query.filter(RecurringEvent.status == EventStatus(status))
        
        if organizer_id:
            query = query.filter(RecurringEvent.organizer_id == organizer_id)
        
        events = query.order_by(RecurringEvent.start_date.desc()).all()
        
        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_calendar_bp.route('/recurring-events', methods=['POST'])
@jwt_required()
def create_recurring_event():
    """Create recurring event"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['event_title', 'event_type', 'recurrence_pattern', 'start_date', 'start_time', 'end_time', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create recurring event
        event = RecurringEvent(
            event_title=data['event_title'],
            event_description=data.get('event_description'),
            event_type=data['event_type'],
            priority=EventPriority(data.get('priority', 'NORMAL')),
            status=EventStatus(data.get('status', 'SCHEDULED')),
            recurrence_pattern=RecurrencePattern(data['recurrence_pattern']),
            recurrence_config=data.get('recurrence_config'),
            start_date=date.fromisoformat(data['start_date']),
            end_date=date.fromisoformat(data['end_date']) if data.get('end_date') else None,
            start_time=time.fromisoformat(data['start_time']),
            end_time=time.fromisoformat(data['end_time']),
            duration=data.get('duration', 1.0),
            location=data.get('location'),
            meeting_room_id=data.get('meeting_room_id'),
            is_virtual=data.get('is_virtual', False),
            virtual_meeting_link=data.get('virtual_meeting_link'),
            organizer_id=data.get('organizer_id', user_id),
            participants=data.get('participants'),
            required_participants=data.get('required_participants'),
            max_occurrences=data.get('max_occurrences', 0),
            occurrence_count=data.get('occurrence_count', 0),
            last_occurrence=datetime.fromisoformat(data['last_occurrence']) if data.get('last_occurrence') else None,
            next_occurrence=datetime.fromisoformat(data['next_occurrence']) if data.get('next_occurrence') else None,
            company_id=data['company_id']
        )
        
        db.session.add(event)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('recurring_event_created', event.to_dict(), data['company_id'])
        
        return jsonify(event.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Meeting Rooms
@advanced_calendar_bp.route('/meeting-rooms', methods=['GET'])
@jwt_required()
def get_meeting_rooms():
    """Get meeting rooms"""
    try:
        company_id = request.args.get('company_id', type=int)
        status = request.args.get('status')
        is_active = request.args.get('is_active', type=bool)
        is_bookable = request.args.get('is_bookable', type=bool)
        capacity_min = request.args.get('capacity_min', type=int)
        capacity_max = request.args.get('capacity_max', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = MeetingRoom.query.filter(MeetingRoom.company_id == company_id)
        
        if status:
            query = query.filter(MeetingRoom.status == MeetingRoomStatus(status))
        
        if is_active is not None:
            query = query.filter(MeetingRoom.is_active == is_active)
        
        if is_bookable is not None:
            query = query.filter(MeetingRoom.is_bookable == is_bookable)
        
        if capacity_min:
            query = query.filter(MeetingRoom.capacity >= capacity_min)
        
        if capacity_max:
            query = query.filter(MeetingRoom.capacity <= capacity_max)
        
        rooms = query.order_by(MeetingRoom.room_name).all()
        
        return jsonify([room.to_dict() for room in rooms])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_calendar_bp.route('/meeting-rooms', methods=['POST'])
@jwt_required()
def create_meeting_room():
    """Create meeting room"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['room_name', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create meeting room
        room = MeetingRoom(
            room_name=data['room_name'],
            room_description=data.get('room_description'),
            room_number=data.get('room_number'),
            floor=data.get('floor'),
            building=data.get('building'),
            capacity=data.get('capacity', 0),
            max_capacity=data.get('max_capacity', 0),
            features=data.get('features'),
            equipment=data.get('equipment'),
            amenities=data.get('amenities'),
            status=MeetingRoomStatus(data.get('status', 'AVAILABLE')),
            is_active=data.get('is_active', True),
            is_bookable=data.get('is_bookable', True),
            booking_advance_days=data.get('booking_advance_days', 30),
            booking_duration_min=data.get('booking_duration_min', 15),
            booking_duration_max=data.get('booking_duration_max', 480),
            location_coordinates=data.get('location_coordinates'),
            address=data.get('address'),
            company_id=data['company_id']
        )
        
        db.session.add(room)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('meeting_room_created', room.to_dict(), data['company_id'])
        
        return jsonify(room.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_calendar_bp.route('/meeting-rooms/<int:room_id>', methods=['GET'])
@jwt_required()
def get_meeting_room(room_id):
    """Get specific meeting room"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        room = MeetingRoom.query.filter(
            MeetingRoom.id == room_id,
            MeetingRoom.company_id == company_id
        ).first()
        
        if not room:
            return jsonify({'error': 'Meeting room not found'}), 404
        
        return jsonify(room.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_calendar_bp.route('/meeting-rooms/<int:room_id>', methods=['PUT'])
@jwt_required()
def update_meeting_room(room_id):
    """Update meeting room"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        room = MeetingRoom.query.filter(
            MeetingRoom.id == room_id,
            MeetingRoom.company_id == data.get('company_id')
        ).first()
        
        if not room:
            return jsonify({'error': 'Meeting room not found'}), 404
        
        # Update fields
        for field in ['room_name', 'room_description', 'room_number', 'floor', 'building',
                     'capacity', 'max_capacity', 'features', 'equipment', 'amenities',
                     'is_active', 'is_bookable', 'booking_advance_days', 'booking_duration_min',
                     'booking_duration_max', 'location_coordinates', 'address']:
            if field in data:
                setattr(room, field, data[field])
        
        if 'status' in data:
            room.status = MeetingRoomStatus(data['status'])
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('meeting_room_updated', room.to_dict(), room.company_id)
        
        return jsonify(room.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Room Bookings
@advanced_calendar_bp.route('/room-bookings', methods=['GET'])
@jwt_required()
def get_room_bookings():
    """Get room bookings"""
    try:
        company_id = request.args.get('company_id', type=int)
        meeting_room_id = request.args.get('meeting_room_id', type=int)
        booking_date = request.args.get('booking_date')
        booking_status = request.args.get('booking_status')
        booked_by = request.args.get('booked_by', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = RoomBooking.query.filter(RoomBooking.company_id == company_id)
        
        if meeting_room_id:
            query = query.filter(RoomBooking.meeting_room_id == meeting_room_id)
        
        if booking_date:
            query = query.filter(RoomBooking.booking_date == date.fromisoformat(booking_date))
        
        if booking_status:
            query = query.filter(RoomBooking.booking_status == booking_status)
        
        if booked_by:
            query = query.filter(RoomBooking.booked_by == booked_by)
        
        if start_date:
            query = query.filter(RoomBooking.booking_date >= date.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(RoomBooking.booking_date <= date.fromisoformat(end_date))
        
        bookings = query.order_by(RoomBooking.booking_date.desc()).all()
        
        return jsonify([booking.to_dict() for booking in bookings])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_calendar_bp.route('/room-bookings', methods=['POST'])
@jwt_required()
def create_room_booking():
    """Create room booking"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['booking_title', 'meeting_room_id', 'booking_date', 'start_time', 'end_time', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create room booking
        booking = RoomBooking(
            booking_title=data['booking_title'],
            booking_description=data.get('booking_description'),
            booking_date=date.fromisoformat(data['booking_date']),
            start_time=time.fromisoformat(data['start_time']),
            end_time=time.fromisoformat(data['end_time']),
            duration=data.get('duration', 1.0),
            meeting_room_id=data['meeting_room_id'],
            recurring_event_id=data.get('recurring_event_id'),
            event_occurrence_id=data.get('event_occurrence_id'),
            booking_status=data.get('booking_status', 'Confirmed'),
            is_recurring=data.get('is_recurring', False),
            booked_by=data.get('booked_by', user_id),
            attendees=data.get('attendees'),
            booking_data=data.get('booking_data'),
            special_requirements=data.get('special_requirements'),
            company_id=data['company_id']
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('room_booking_created', booking.to_dict(), data['company_id'])
        
        return jsonify(booking.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Calendar Events
@advanced_calendar_bp.route('/events', methods=['GET'])
@jwt_required()
def get_calendar_events():
    """Get calendar events"""
    try:
        company_id = request.args.get('company_id', type=int)
        event_type = request.args.get('event_type')
        status = request.args.get('status')
        priority = request.args.get('priority')
        organizer_id = request.args.get('organizer_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = CalendarEvent.query.filter(CalendarEvent.company_id == company_id)
        
        if event_type:
            query = query.filter(CalendarEvent.event_type == event_type)
        
        if status:
            query = query.filter(CalendarEvent.status == EventStatus(status))
        
        if priority:
            query = query.filter(CalendarEvent.priority == EventPriority(priority))
        
        if organizer_id:
            query = query.filter(CalendarEvent.organizer_id == organizer_id)
        
        if start_date:
            query = query.filter(CalendarEvent.start_datetime >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(CalendarEvent.start_datetime <= datetime.fromisoformat(end_date))
        
        events = query.order_by(CalendarEvent.start_datetime.desc()).all()
        
        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_calendar_bp.route('/events', methods=['POST'])
@jwt_required()
def create_calendar_event():
    """Create calendar event"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['event_title', 'event_type', 'start_datetime', 'end_datetime', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create calendar event
        event = CalendarEvent(
            event_title=data['event_title'],
            event_description=data.get('event_description'),
            event_type=data['event_type'],
            priority=EventPriority(data.get('priority', 'NORMAL')),
            status=EventStatus(data.get('status', 'SCHEDULED')),
            start_datetime=datetime.fromisoformat(data['start_datetime']),
            end_datetime=datetime.fromisoformat(data['end_datetime']),
            duration=data.get('duration', 1.0),
            is_all_day=data.get('is_all_day', False),
            location=data.get('location'),
            meeting_room_id=data.get('meeting_room_id'),
            is_virtual=data.get('is_virtual', False),
            virtual_meeting_link=data.get('virtual_meeting_link'),
            recurring_event_id=data.get('recurring_event_id'),
            parent_event_id=data.get('parent_event_id'),
            organizer_id=data.get('organizer_id', user_id),
            participants=data.get('participants'),
            required_participants=data.get('required_participants'),
            event_data=data.get('event_data'),
            reminders=data.get('reminders'),
            attachments=data.get('attachments'),
            company_id=data['company_id']
        )
        
        db.session.add(event)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('calendar_event_created', event.to_dict(), data['company_id'])
        
        return jsonify(event.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Calendar Integrations
@advanced_calendar_bp.route('/integrations', methods=['GET'])
@jwt_required()
def get_calendar_integrations():
    """Get calendar integrations"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        integration_type = request.args.get('integration_type')
        provider = request.args.get('provider')
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = CalendarIntegration.query.filter(CalendarIntegration.company_id == company_id)
        
        if integration_type:
            query = query.filter(CalendarIntegration.integration_type == integration_type)
        
        if provider:
            query = query.filter(CalendarIntegration.provider == provider)
        
        if is_active is not None:
            query = query.filter(CalendarIntegration.is_active == is_active)
        
        integrations = query.order_by(CalendarIntegration.created_at.desc()).all()
        
        return jsonify([integration.to_dict() for integration in integrations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_calendar_bp.route('/integrations', methods=['POST'])
@jwt_required()
def create_calendar_integration():
    """Create calendar integration"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['integration_name', 'integration_type', 'provider', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create integration
        integration = CalendarIntegration(
            integration_name=data['integration_name'],
            integration_type=data['integration_type'],
            provider=data['provider'],
            access_token=data.get('access_token'),
            refresh_token=data.get('refresh_token'),
            token_expires=datetime.fromisoformat(data['token_expires']) if data.get('token_expires') else None,
            is_active=data.get('is_active', True),
            sync_enabled=data.get('sync_enabled', True),
            sync_frequency=data.get('sync_frequency', 15),
            last_sync=datetime.fromisoformat(data['last_sync']) if data.get('last_sync') else None,
            user_id=data.get('user_id', user_id),
            integration_data=data.get('integration_data'),
            sync_settings=data.get('sync_settings'),
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

# Calendar Reminders
@advanced_calendar_bp.route('/reminders', methods=['GET'])
@jwt_required()
def get_calendar_reminders():
    """Get calendar reminders"""
    try:
        company_id = request.args.get('company_id', type=int)
        event_id = request.args.get('event_id', type=int)
        reminder_type = request.args.get('reminder_type')
        is_sent = request.args.get('is_sent', type=bool)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = CalendarReminder.query.filter(CalendarReminder.company_id == company_id)
        
        if event_id:
            query = query.filter(CalendarReminder.event_id == event_id)
        
        if reminder_type:
            query = query.filter(CalendarReminder.reminder_type == reminder_type)
        
        if is_sent is not None:
            query = query.filter(CalendarReminder.is_sent == is_sent)
        
        if start_date:
            query = query.filter(CalendarReminder.reminder_datetime >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(CalendarReminder.reminder_datetime <= datetime.fromisoformat(end_date))
        
        reminders = query.order_by(CalendarReminder.reminder_datetime.desc()).all()
        
        return jsonify([reminder.to_dict() for reminder in reminders])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_calendar_bp.route('/reminders', methods=['POST'])
@jwt_required()
def create_calendar_reminder():
    """Create calendar reminder"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['reminder_title', 'event_id', 'reminder_datetime', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create reminder
        reminder = CalendarReminder(
            reminder_title=data['reminder_title'],
            reminder_message=data.get('reminder_message'),
            reminder_type=data.get('reminder_type', 'Email'),
            event_id=data['event_id'],
            reminder_datetime=datetime.fromisoformat(data['reminder_datetime']),
            reminder_offset=data.get('reminder_offset', 15),
            is_sent=data.get('is_sent', False),
            sent_at=datetime.fromisoformat(data['sent_at']) if data.get('sent_at') else None,
            recipient_users=data.get('recipient_users'),
            recipient_emails=data.get('recipient_emails'),
            company_id=data['company_id']
        )
        
        db.session.add(reminder)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('calendar_reminder_created', reminder.to_dict(), data['company_id'])
        
        return jsonify(reminder.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Calendar Conflicts
@advanced_calendar_bp.route('/conflicts', methods=['GET'])
@jwt_required()
def get_calendar_conflicts():
    """Get calendar conflicts"""
    try:
        company_id = request.args.get('company_id', type=int)
        conflict_type = request.args.get('conflict_type')
        conflict_severity = request.args.get('conflict_severity')
        resolution_status = request.args.get('resolution_status')
        resolved_by = request.args.get('resolved_by', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = CalendarConflict.query.filter(CalendarConflict.company_id == company_id)
        
        if conflict_type:
            query = query.filter(CalendarConflict.conflict_type == conflict_type)
        
        if conflict_severity:
            query = query.filter(CalendarConflict.conflict_severity == conflict_severity)
        
        if resolution_status:
            query = query.filter(CalendarConflict.resolution_status == resolution_status)
        
        if resolved_by:
            query = query.filter(CalendarConflict.resolved_by == resolved_by)
        
        if start_date:
            query = query.filter(CalendarConflict.created_at >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(CalendarConflict.created_at <= datetime.fromisoformat(end_date))
        
        conflicts = query.order_by(CalendarConflict.created_at.desc()).all()
        
        return jsonify([conflict.to_dict() for conflict in conflicts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_calendar_bp.route('/conflicts', methods=['POST'])
@jwt_required()
def create_calendar_conflict():
    """Create calendar conflict"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['conflict_type', 'primary_event_id', 'conflicting_event_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create conflict
        conflict = CalendarConflict(
            conflict_type=data['conflict_type'],
            conflict_description=data.get('conflict_description'),
            conflict_severity=data.get('conflict_severity', 'Medium'),
            primary_event_id=data['primary_event_id'],
            conflicting_event_id=data['conflicting_event_id'],
            resolution_status=data.get('resolution_status', 'Pending'),
            resolution_notes=data.get('resolution_notes'),
            resolved_by=data.get('resolved_by'),
            resolved_at=datetime.fromisoformat(data['resolved_at']) if data.get('resolved_at') else None,
            company_id=data['company_id']
        )
        
        db.session.add(conflict)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('calendar_conflict_created', conflict.to_dict(), data['company_id'])
        
        return jsonify(conflict.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_calendar_bp.route('/conflicts/<int:conflict_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_calendar_conflict(conflict_id):
    """Resolve calendar conflict"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        conflict = CalendarConflict.query.filter(
            CalendarConflict.id == conflict_id,
            CalendarConflict.company_id == data.get('company_id')
        ).first()
        
        if not conflict:
            return jsonify({'error': 'Calendar conflict not found'}), 404
        
        # Update conflict resolution
        conflict.resolution_status = 'Resolved'
        conflict.resolution_notes = data.get('resolution_notes')
        conflict.resolved_by = user_id
        conflict.resolved_at = datetime.utcnow()
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('calendar_conflict_resolved', conflict.to_dict(), conflict.company_id)
        
        return jsonify(conflict.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
