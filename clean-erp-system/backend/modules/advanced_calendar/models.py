# Advanced Calendar Models
# Models for advanced calendar features including recurring event intelligence, meeting room integration, and smart scheduling

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime, time, date, timedelta
import enum

class RecurrencePattern(enum.Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"
    CUSTOM = "Custom"

class MeetingRoomStatus(enum.Enum):
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    MAINTENANCE = "Maintenance"
    RESERVED = "Reserved"

class EventPriority(enum.Enum):
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    URGENT = "Urgent"

class EventStatus(enum.Enum):
    SCHEDULED = "Scheduled"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    POSTPONED = "Postponed"

class RecurringEvent(BaseModel):
    """Recurring event model"""
    __tablename__ = 'recurring_events'
    
    # Event Information
    event_title = db.Column(db.String(200), nullable=False)
    event_description = db.Column(db.Text)
    event_type = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.Enum(EventPriority), default=EventPriority.NORMAL)
    status = db.Column(db.Enum(EventStatus), default=EventStatus.SCHEDULED)
    
    # Recurrence Information
    recurrence_pattern = db.Column(db.Enum(RecurrencePattern), nullable=False)
    recurrence_config = db.Column(db.JSON)  # Recurrence configuration
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Float, default=1.0)  # hours
    
    # Location Information
    location = db.Column(db.String(500))
    meeting_room_id = db.Column(db.Integer, db.ForeignKey('meeting_rooms.id'))
    meeting_room = relationship("MeetingRoom")
    is_virtual = db.Column(db.Boolean, default=False)
    virtual_meeting_link = db.Column(db.String(500))
    
    # Participants
    organizer_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    organizer = relationship("Employee")
    participants = db.Column(db.JSON)  # List of participant IDs
    required_participants = db.Column(db.JSON)  # List of required participant IDs
    
    # Recurrence Settings
    max_occurrences = db.Column(db.Integer, default=0)  # 0 = unlimited
    occurrence_count = db.Column(db.Integer, default=0)
    last_occurrence = db.Column(db.DateTime)
    next_occurrence = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'event_title': self.event_title,
            'event_description': self.event_description,
            'event_type': self.event_type,
            'priority': self.priority.value if self.priority else None,
            'status': self.status.value if self.status else None,
            'recurrence_pattern': self.recurrence_pattern.value if self.recurrence_pattern else None,
            'recurrence_config': self.recurrence_config,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'location': self.location,
            'meeting_room_id': self.meeting_room_id,
            'is_virtual': self.is_virtual,
            'virtual_meeting_link': self.virtual_meeting_link,
            'organizer_id': self.organizer_id,
            'participants': self.participants,
            'required_participants': self.required_participants,
            'max_occurrences': self.max_occurrences,
            'occurrence_count': self.occurrence_count,
            'last_occurrence': self.last_occurrence.isoformat() if self.last_occurrence else None,
            'next_occurrence': self.next_occurrence.isoformat() if self.next_occurrence else None,
            'company_id': self.company_id
        })
        return data

class EventOccurrence(BaseModel):
    """Event occurrence model"""
    __tablename__ = 'event_occurrences'
    
    # Occurrence Information
    occurrence_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum(EventStatus), default=EventStatus.SCHEDULED)
    
    # Recurring Event Association
    recurring_event_id = db.Column(db.Integer, db.ForeignKey('recurring_events.id'), nullable=False)
    recurring_event = relationship("RecurringEvent")
    
    # Meeting Room Association
    meeting_room_id = db.Column(db.Integer, db.ForeignKey('meeting_rooms.id'))
    meeting_room = relationship("MeetingRoom")
    
    # Occurrence Data
    occurrence_data = db.Column(db.JSON)  # Occurrence-specific data
    attendance_data = db.Column(db.JSON)  # Attendance tracking
    notes = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'occurrence_date': self.occurrence_date.isoformat() if self.occurrence_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status.value if self.status else None,
            'recurring_event_id': self.recurring_event_id,
            'meeting_room_id': self.meeting_room_id,
            'occurrence_data': self.occurrence_data,
            'attendance_data': self.attendance_data,
            'notes': self.notes,
            'company_id': self.company_id
        })
        return data

class MeetingRoom(BaseModel):
    """Meeting room model"""
    __tablename__ = 'meeting_rooms'
    
    # Room Information
    room_name = db.Column(db.String(200), nullable=False)
    room_description = db.Column(db.Text)
    room_number = db.Column(db.String(50))
    floor = db.Column(db.String(50))
    building = db.Column(db.String(100))
    
    # Room Capacity
    capacity = db.Column(db.Integer, default=0)
    max_capacity = db.Column(db.Integer, default=0)
    
    # Room Features
    features = db.Column(db.JSON)  # List of room features
    equipment = db.Column(db.JSON)  # List of equipment
    amenities = db.Column(db.JSON)  # List of amenities
    
    # Room Status
    status = db.Column(db.Enum(MeetingRoomStatus), default=MeetingRoomStatus.AVAILABLE)
    is_active = db.Column(db.Boolean, default=True)
    is_bookable = db.Column(db.Boolean, default=True)
    
    # Booking Settings
    booking_advance_days = db.Column(db.Integer, default=30)  # Days in advance
    booking_duration_min = db.Column(db.Integer, default=15)  # Minimum booking duration (minutes)
    booking_duration_max = db.Column(db.Integer, default=480)  # Maximum booking duration (minutes)
    
    # Location
    location_coordinates = db.Column(db.JSON)
    address = db.Column(db.String(500))
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'room_name': self.room_name,
            'room_description': self.room_description,
            'room_number': self.room_number,
            'floor': self.floor,
            'building': self.building,
            'capacity': self.capacity,
            'max_capacity': self.max_capacity,
            'features': self.features,
            'equipment': self.equipment,
            'amenities': self.amenities,
            'status': self.status.value if self.status else None,
            'is_active': self.is_active,
            'is_bookable': self.is_bookable,
            'booking_advance_days': self.booking_advance_days,
            'booking_duration_min': self.booking_duration_min,
            'booking_duration_max': self.booking_duration_max,
            'location_coordinates': self.location_coordinates,
            'address': self.address,
            'company_id': self.company_id
        })
        return data

class RoomBooking(BaseModel):
    """Room booking model"""
    __tablename__ = 'room_bookings'
    
    # Booking Information
    booking_title = db.Column(db.String(200), nullable=False)
    booking_description = db.Column(db.Text)
    booking_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Float, default=1.0)  # hours
    
    # Room Association
    meeting_room_id = db.Column(db.Integer, db.ForeignKey('meeting_rooms.id'), nullable=False)
    meeting_room = relationship("MeetingRoom")
    
    # Event Association
    recurring_event_id = db.Column(db.Integer, db.ForeignKey('recurring_events.id'))
    recurring_event = relationship("RecurringEvent")
    event_occurrence_id = db.Column(db.Integer, db.ForeignKey('event_occurrences.id'))
    event_occurrence = relationship("EventOccurrence")
    
    # Booking Status
    booking_status = db.Column(db.String(50), default='Confirmed')  # Confirmed, Cancelled, Completed
    is_recurring = db.Column(db.Boolean, default=False)
    
    # User Information
    booked_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    booker = relationship("Employee")
    attendees = db.Column(db.JSON)  # List of attendee IDs
    
    # Booking Data
    booking_data = db.Column(db.JSON)  # Additional booking data
    special_requirements = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'booking_title': self.booking_title,
            'booking_description': self.booking_description,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'meeting_room_id': self.meeting_room_id,
            'recurring_event_id': self.recurring_event_id,
            'event_occurrence_id': self.event_occurrence_id,
            'booking_status': self.booking_status,
            'is_recurring': self.is_recurring,
            'booked_by': self.booked_by,
            'attendees': self.attendees,
            'booking_data': self.booking_data,
            'special_requirements': self.special_requirements,
            'company_id': self.company_id
        })
        return data

class CalendarIntegration(BaseModel):
    """Calendar integration model"""
    __tablename__ = 'calendar_integrations'
    
    # Integration Information
    integration_name = db.Column(db.String(200), nullable=False)
    integration_type = db.Column(db.String(100), nullable=False)  # Google, Outlook, Apple, etc.
    provider = db.Column(db.String(100), nullable=False)
    
    # Authentication
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expires = db.Column(db.DateTime)
    
    # Integration Settings
    is_active = db.Column(db.Boolean, default=True)
    sync_enabled = db.Column(db.Boolean, default=True)
    sync_frequency = db.Column(db.Integer, default=15)  # minutes
    last_sync = db.Column(db.DateTime)
    
    # User Association
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Integration Data
    integration_data = db.Column(db.JSON)  # Integration-specific data
    sync_settings = db.Column(db.JSON)  # Sync settings
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'integration_name': self.integration_name,
            'integration_type': self.integration_type,
            'provider': self.provider,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_expires': self.token_expires.isoformat() if self.token_expires else None,
            'is_active': self.is_active,
            'sync_enabled': self.sync_enabled,
            'sync_frequency': self.sync_frequency,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'user_id': self.user_id,
            'integration_data': self.integration_data,
            'sync_settings': self.sync_settings,
            'company_id': self.company_id
        })
        return data

class CalendarEvent(BaseModel):
    """Calendar event model"""
    __tablename__ = 'calendar_events'
    
    # Event Information
    event_title = db.Column(db.String(200), nullable=False)
    event_description = db.Column(db.Text)
    event_type = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.Enum(EventPriority), default=EventPriority.NORMAL)
    status = db.Column(db.Enum(EventStatus), default=EventStatus.SCHEDULED)
    
    # Event Timing
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Float, default=1.0)  # hours
    is_all_day = db.Column(db.Boolean, default=False)
    
    # Location Information
    location = db.Column(db.String(500))
    meeting_room_id = db.Column(db.Integer, db.ForeignKey('meeting_rooms.id'))
    meeting_room = relationship("MeetingRoom")
    is_virtual = db.Column(db.Boolean, default=False)
    virtual_meeting_link = db.Column(db.String(500))
    
    # Event Association
    recurring_event_id = db.Column(db.Integer, db.ForeignKey('recurring_events.id'))
    recurring_event = relationship("RecurringEvent")
    parent_event_id = db.Column(db.Integer, db.ForeignKey('calendar_events.id'))
    parent_event = relationship("CalendarEvent", remote_side=[id])
    
    # Participants
    organizer_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    organizer = relationship("Employee")
    participants = db.Column(db.JSON)  # List of participant IDs
    required_participants = db.Column(db.JSON)  # List of required participant IDs
    
    # Event Data
    event_data = db.Column(db.JSON)  # Additional event data
    reminders = db.Column(db.JSON)  # Reminder settings
    attachments = db.Column(db.JSON)  # List of attachments
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'event_title': self.event_title,
            'event_description': self.event_description,
            'event_type': self.event_type,
            'priority': self.priority.value if self.priority else None,
            'status': self.status.value if self.status else None,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'duration': self.duration,
            'is_all_day': self.is_all_day,
            'location': self.location,
            'meeting_room_id': self.meeting_room_id,
            'is_virtual': self.is_virtual,
            'virtual_meeting_link': self.virtual_meeting_link,
            'recurring_event_id': self.recurring_event_id,
            'parent_event_id': self.parent_event_id,
            'organizer_id': self.organizer_id,
            'participants': self.participants,
            'required_participants': self.required_participants,
            'event_data': self.event_data,
            'reminders': self.reminders,
            'attachments': self.attachments,
            'company_id': self.company_id
        })
        return data

class CalendarReminder(BaseModel):
    """Calendar reminder model"""
    __tablename__ = 'calendar_reminders'
    
    # Reminder Information
    reminder_title = db.Column(db.String(200), nullable=False)
    reminder_message = db.Column(db.Text)
    reminder_type = db.Column(db.String(50), default='Email')  # Email, SMS, Push, In-app
    
    # Event Association
    event_id = db.Column(db.Integer, db.ForeignKey('calendar_events.id'), nullable=False)
    event = relationship("CalendarEvent")
    
    # Reminder Timing
    reminder_datetime = db.Column(db.DateTime, nullable=False)
    reminder_offset = db.Column(db.Integer, default=15)  # minutes before event
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    
    # Recipients
    recipient_users = db.Column(db.JSON)  # List of user IDs
    recipient_emails = db.Column(db.JSON)  # List of email addresses
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'reminder_title': self.reminder_title,
            'reminder_message': self.reminder_message,
            'reminder_type': self.reminder_type,
            'event_id': self.event_id,
            'reminder_datetime': self.reminder_datetime.isoformat() if self.reminder_datetime else None,
            'reminder_offset': self.reminder_offset,
            'is_sent': self.is_sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'recipient_users': self.recipient_users,
            'recipient_emails': self.recipient_emails,
            'company_id': self.company_id
        })
        return data

class CalendarConflict(BaseModel):
    """Calendar conflict model"""
    __tablename__ = 'calendar_conflicts'
    
    # Conflict Information
    conflict_type = db.Column(db.String(100), nullable=False)  # Time, Room, Participant
    conflict_description = db.Column(db.Text)
    conflict_severity = db.Column(db.String(50), default='Medium')  # Low, Medium, High, Critical
    
    # Conflicting Events
    primary_event_id = db.Column(db.Integer, db.ForeignKey('calendar_events.id'), nullable=False)
    primary_event = relationship("CalendarEvent", foreign_keys=[primary_event_id])
    conflicting_event_id = db.Column(db.Integer, db.ForeignKey('calendar_events.id'), nullable=False)
    conflicting_event = relationship("CalendarEvent", foreign_keys=[conflicting_event_id])
    
    # Conflict Resolution
    resolution_status = db.Column(db.String(50), default='Pending')  # Pending, Resolved, Escalated
    resolution_notes = db.Column(db.Text)
    resolved_by = db.Column(db.Integer, db.ForeignKey('employees.id'))
    resolver = relationship("Employee")
    resolved_at = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'conflict_type': self.conflict_type,
            'conflict_description': self.conflict_description,
            'conflict_severity': self.conflict_severity,
            'primary_event_id': self.primary_event_id,
            'conflicting_event_id': self.conflicting_event_id,
            'resolution_status': self.resolution_status,
            'resolution_notes': self.resolution_notes,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'company_id': self.company_id
        })
        return data
