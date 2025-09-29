# Calendar Models
# Integrated calendar system with all modules, geolocation, and external calendar sync

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, date, timedelta
import enum

class EventType(enum.Enum):
    MEETING = "Meeting"
    CALL = "Call"
    VISIT = "Visit"
    WORKORDER = "Work Order"
    TASK = "Task"
    TRAINING = "Training"
    APPOINTMENT = "Appointment"
    CUSTOM = "Custom"

class EventStatus(enum.Enum):
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    POSTPONED = "Postponed"

class RecurrenceType(enum.Enum):
    NONE = "None"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"

class CalendarType(enum.Enum):
    PERSONAL = "Personal"
    TEAM = "Team"
    COMPANY = "Company"
    PROJECT = "Project"
    EXTERNAL = "External"

class AvailabilityStatus(enum.Enum):
    AVAILABLE = "Available"
    BUSY = "Busy"
    OUT_OF_OFFICE = "Out of Office"
    TENTATIVE = "Tentative"

# Calendar Models
class Calendar(BaseModel):
    """Calendar model"""
    __tablename__ = 'calendars'
    
    # Calendar Information
    calendar_name = db.Column(db.String(200), nullable=False)
    calendar_description = db.Column(db.Text)
    calendar_type = db.Column(db.Enum(CalendarType), nullable=False)
    color = db.Column(db.String(7), default='#3498db')  # Hex color code
    
    # Calendar Settings
    is_public = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Owner Information
    owner_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    owner = relationship("Employee")
    
    # External Calendar Integration
    external_calendar_id = db.Column(db.String(255))  # External calendar ID
    external_provider = db.Column(db.String(50))  # Google, Microsoft, etc.
    sync_enabled = db.Column(db.Boolean, default=False)
    last_sync = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    calendar_events = relationship("CalendarEvent", back_populates="calendar")
    calendar_shares = relationship("CalendarShare", back_populates="calendar")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'calendar_name': self.calendar_name,
            'calendar_description': self.calendar_description,
            'calendar_type': self.calendar_type.value if self.calendar_type else None,
            'color': self.color,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'timezone': self.timezone,
            'owner_id': self.owner_id,
            'external_calendar_id': self.external_calendar_id,
            'external_provider': self.external_provider,
            'sync_enabled': self.sync_enabled,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'company_id': self.company_id
        })
        return data

class CalendarEvent(BaseModel):
    """Calendar event model"""
    __tablename__ = 'calendar_events'
    
    # Event Information
    event_title = db.Column(db.String(200), nullable=False)
    event_description = db.Column(db.Text)
    event_type = db.Column(db.Enum(EventType), nullable=False)
    event_status = db.Column(db.Enum(EventStatus), default=EventStatus.SCHEDULED)
    
    # Event Timing
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    all_day = db.Column(db.Boolean, default=False)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Recurrence
    recurrence_type = db.Column(db.Enum(RecurrenceType), default=RecurrenceType.NONE)
    recurrence_pattern = db.Column(db.JSON)  # Recurrence pattern details
    recurrence_end = db.Column(db.DateTime)
    
    # Location Information
    location = db.Column(db.String(500))
    location_coordinates = db.Column(db.JSON)  # Latitude, longitude
    location_address = db.Column(db.Text)
    location_radius = db.Column(db.Float, default=0.0)  # meters
    
    # Event Details
    attendees = db.Column(db.JSON)  # List of attendee IDs
    organizer_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    organizer = relationship("Employee")
    
    # Calendar Association
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendars.id'), nullable=False)
    calendar = relationship("Calendar", back_populates="calendar_events")
    
    # Related Entity
    related_entity_type = db.Column(db.String(100))  # Customer, Opportunity, etc.
    related_entity_id = db.Column(db.String(100))
    
    # External Integration
    external_event_id = db.Column(db.String(255))
    external_provider = db.Column(db.String(50))
    sync_status = db.Column(db.String(50), default='Synced')
    
    # Reminder Settings
    reminder_minutes = db.Column(db.Integer, default=15)
    reminder_sent = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    event_attendance = relationship("EventAttendance", back_populates="event")
    event_geolocation = relationship("EventGeolocation", back_populates="event")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'event_title': self.event_title,
            'event_description': self.event_description,
            'event_type': self.event_type.value if self.event_type else None,
            'event_status': self.event_status.value if self.event_status else None,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'all_day': self.all_day,
            'timezone': self.timezone,
            'recurrence_type': self.recurrence_type.value if self.recurrence_type else None,
            'recurrence_pattern': self.recurrence_pattern,
            'recurrence_end': self.recurrence_end.isoformat() if self.recurrence_end else None,
            'location': self.location,
            'location_coordinates': self.location_coordinates,
            'location_address': self.location_address,
            'location_radius': self.location_radius,
            'attendees': self.attendees,
            'organizer_id': self.organizer_id,
            'calendar_id': self.calendar_id,
            'related_entity_type': self.related_entity_type,
            'related_entity_id': self.related_entity_id,
            'external_event_id': self.external_event_id,
            'external_provider': self.external_provider,
            'sync_status': self.sync_status,
            'reminder_minutes': self.reminder_minutes,
            'reminder_sent': self.reminder_sent,
            'company_id': self.company_id
        })
        return data

class EventAttendance(BaseModel):
    """Event attendance model"""
    __tablename__ = 'event_attendance'
    
    # Attendance Information
    attendance_status = db.Column(db.String(50), default='Invited')  # Invited, Accepted, Declined, Tentative
    response_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    # Event Association
    event_id = db.Column(db.Integer, db.ForeignKey('calendar_events.id'), nullable=False)
    event = relationship("CalendarEvent", back_populates="event_attendance")
    
    # Attendee Information
    attendee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    attendee = relationship("Employee")
    
    # Check-in/Check-out
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    check_in_location = db.Column(db.JSON)  # Geolocation data
    check_out_location = db.Column(db.JSON)  # Geolocation data
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'attendance_status': self.attendance_status,
            'response_date': self.response_date.isoformat() if self.response_date else None,
            'notes': self.notes,
            'event_id': self.event_id,
            'attendee_id': self.attendee_id,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'check_in_location': self.check_in_location,
            'check_out_location': self.check_out_location,
            'company_id': self.company_id
        })
        return data

class EventGeolocation(BaseModel):
    """Event geolocation tracking model"""
    __tablename__ = 'event_geolocation'
    
    # Geolocation Information
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, default=0.0)  # meters
    altitude = db.Column(db.Float, default=0.0)
    speed = db.Column(db.Float, default=0.0)  # m/s
    
    # Location Details
    address = db.Column(db.String(500))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    
    # Event Association
    event_id = db.Column(db.Integer, db.ForeignKey('calendar_events.id'), nullable=False)
    event = relationship("CalendarEvent", back_populates="event_geolocation")
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Tracking Details
    tracking_type = db.Column(db.String(50), default='Check-in')  # Check-in, Check-out, Location Update
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    device_info = db.Column(db.JSON)  # Device information
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'altitude': self.altitude,
            'speed': self.speed,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'event_id': self.event_id,
            'user_id': self.user_id,
            'tracking_type': self.tracking_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'device_info': self.device_info,
            'company_id': self.company_id
        })
        return data

class CalendarShare(BaseModel):
    """Calendar sharing model"""
    __tablename__ = 'calendar_shares'
    
    # Share Information
    share_type = db.Column(db.String(50), default='View')  # View, Edit, Admin
    permissions = db.Column(db.JSON)  # Detailed permissions
    
    # Calendar Association
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendars.id'), nullable=False)
    calendar = relationship("Calendar", back_populates="calendar_shares")
    
    # Shared With
    shared_with_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    shared_with = relationship("Employee")
    shared_with_role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    shared_with_role = relationship("Role")
    
    # Share Settings
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'share_type': self.share_type,
            'permissions': self.permissions,
            'calendar_id': self.calendar_id,
            'shared_with_id': self.shared_with_id,
            'shared_with_role_id': self.shared_with_role_id,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'company_id': self.company_id
        })
        return data

class UserAvailability(BaseModel):
    """User availability model"""
    __tablename__ = 'user_availability'
    
    # Availability Information
    availability_status = db.Column(db.Enum(AvailabilityStatus), default=AvailabilityStatus.AVAILABLE)
    status_message = db.Column(db.String(200))
    
    # Time Period
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Location Information
    location = db.Column(db.String(500))
    location_coordinates = db.Column(db.JSON)
    
    # Availability Settings
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.JSON)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'availability_status': self.availability_status.value if self.availability_status else None,
            'status_message': self.status_message,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'user_id': self.user_id,
            'location': self.location,
            'location_coordinates': self.location_coordinates,
            'is_recurring': self.is_recurring,
            'recurrence_pattern': self.recurrence_pattern,
            'company_id': self.company_id
        })
        return data

class ExternalCalendarIntegration(BaseModel):
    """External calendar integration model"""
    __tablename__ = 'external_calendar_integrations'
    
    # Integration Information
    provider = db.Column(db.String(50), nullable=False)  # Google, Microsoft, etc.
    integration_name = db.Column(db.String(200), nullable=False)
    
    # Authentication
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expires = db.Column(db.DateTime)
    
    # Integration Settings
    sync_enabled = db.Column(db.Boolean, default=True)
    sync_direction = db.Column(db.String(50), default='Bidirectional')  # Inbound, Outbound, Bidirectional
    sync_frequency = db.Column(db.Integer, default=15)  # minutes
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Integration Status
    is_active = db.Column(db.Boolean, default=True)
    last_sync = db.Column(db.DateTime)
    sync_errors = db.Column(db.JSON)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'provider': self.provider,
            'integration_name': self.integration_name,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_expires': self.token_expires.isoformat() if self.token_expires else None,
            'sync_enabled': self.sync_enabled,
            'sync_direction': self.sync_direction,
            'sync_frequency': self.sync_frequency,
            'user_id': self.user_id,
            'is_active': self.is_active,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'sync_errors': self.sync_errors,
            'company_id': self.company_id
        })
        return data
