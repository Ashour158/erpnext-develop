# Calendar System
# Backend core calendar system for all modules

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class EventType(enum.Enum):
    MEETING = "meeting"
    CALL = "call"
    TASK = "task"
    DEADLINE = "deadline"
    APPOINTMENT = "appointment"
    MAINTENANCE = "maintenance"
    TRAINING = "training"
    VACATION = "vacation"
    HOLIDAY = "holiday"
    OTHER = "other"

class EventStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"

class RecurrenceType(enum.Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class AvailabilityStatus(enum.Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    TENTATIVE = "tentative"
    OUT_OF_OFFICE = "out_of_office"
    FREE = "free"

# Calendar Events
class CalendarEvent(Base):
    __tablename__ = 'calendar_events'
    
    id = Column(Integer, primary_key=True, index=True)
    event_title = Column(String(255), nullable=False)
    event_description = Column(Text)
    
    # Event Classification
    event_type = Column(Enum(EventType), nullable=False)
    event_category = Column(String(100))  # Business, Personal, Project, etc.
    event_status = Column(Enum(EventStatus), default=EventStatus.SCHEDULED)
    
    # Event Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    timezone = Column(String(100), default='UTC')
    all_day = Column(Boolean, default=False)
    
    # Event Location
    location = Column(String(255))
    location_type = Column(String(50))  # physical, virtual, hybrid
    location_details = Column(JSON)  # Location-specific details
    coordinates = Column(JSON)  # GPS coordinates
    
    # Event Recurrence
    is_recurring = Column(Boolean, default=False)
    recurrence_type = Column(Enum(RecurrenceType), default=RecurrenceType.NONE)
    recurrence_pattern = Column(JSON)  # Recurrence pattern
    recurrence_end_date = Column(DateTime)
    parent_event_id = Column(Integer, ForeignKey('calendar_events.id'))
    
    # Event Context
    context_module = Column(String(50))  # CRM, Finance, HR, etc.
    context_entity = Column(String(50))  # Customer, Invoice, Employee, etc.
    context_record_id = Column(Integer)  # ID of the related record
    context_data = Column(JSON)  # Context-specific data
    
    # Event Assignment
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    assigned_to = Column(Integer, ForeignKey('users.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    
    # Event Details
    priority = Column(String(20), default='medium')  # low, medium, high, urgent
    is_private = Column(Boolean, default=False)
    is_confidential = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)
    approval_status = Column(String(50))  # pending, approved, rejected
    
    # Event Resources
    required_resources = Column(JSON)  # Required resources
    booked_resources = Column(JSON)  # Booked resources
    resource_conflicts = Column(JSON)  # Resource conflicts
    
    # Event Integration
    external_event_id = Column(String(100))  # External system event ID
    external_calendar_id = Column(String(100))  # External calendar ID
    integration_data = Column(JSON)  # Integration data
    
    # Event Notifications
    reminder_minutes = Column(JSON)  # Reminder times in minutes
    notification_sent = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    
    # Event Attachments
    attachments = Column(JSON)  # File attachments
    meeting_notes = Column(Text)  # Meeting notes
    action_items = Column(JSON)  # Action items from the event
    
    # Event Metrics
    attendance_count = Column(Integer, default=0)
    expected_attendance = Column(Integer, default=0)
    actual_duration = Column(Integer)  # Actual duration in minutes
    estimated_duration = Column(Integer)  # Estimated duration in minutes
    
    # Event Status
    is_active = Column(Boolean, default=True)
    is_cancelled = Column(Boolean, default=False)
    cancellation_reason = Column(Text)
    reschedule_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    owner = relationship("User", foreign_keys=[owner_id])
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    team = relationship("Team")
    department = relationship("Department")
    parent_event = relationship("CalendarEvent", remote_side=[id])
    participants = relationship("EventParticipant", back_populates="event", cascade="all, delete-orphan")
    reminders = relationship("EventReminder", back_populates="event", cascade="all, delete-orphan")

# Event Participants
class EventParticipant(Base):
    __tablename__ = 'event_participants'
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('calendar_events.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Participant Details
    participant_name = Column(String(255))
    participant_email = Column(String(255))
    participant_phone = Column(String(50))
    participant_role = Column(String(100))  # organizer, attendee, optional, etc.
    
    # Participant Status
    response_status = Column(String(50), default='pending')  # pending, accepted, declined, tentative
    response_time = Column(DateTime)
    response_notes = Column(Text)
    
    # Participant Requirements
    is_required = Column(Boolean, default=True)
    is_optional = Column(Boolean, default=False)
    can_invite_others = Column(Boolean, default=False)
    can_modify_event = Column(Boolean, default=False)
    
    # Participant Notifications
    notification_sent = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    reminder_count = Column(Integer, default=0)
    
    # Participant Attendance
    attendance_status = Column(String(50))  # present, absent, late, left_early
    attendance_time = Column(DateTime)
    attendance_notes = Column(Text)
    
    # Participant Integration
    external_participant_id = Column(String(100))  # External system participant ID
    integration_data = Column(JSON)  # Integration data
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("CalendarEvent", back_populates="participants")
    user = relationship("User")

# Event Reminders
class EventReminder(Base):
    __tablename__ = 'event_reminders'
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('calendar_events.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Reminder Details
    reminder_time = Column(DateTime, nullable=False)
    reminder_type = Column(String(50), nullable=False)  # email, sms, push, popup
    reminder_message = Column(Text)
    reminder_status = Column(String(50), default='pending')  # pending, sent, failed, cancelled
    
    # Reminder Configuration
    reminder_minutes = Column(Integer, nullable=False)  # Minutes before event
    reminder_method = Column(String(50), nullable=False)  # email, sms, push, popup
    reminder_recipients = Column(JSON)  # Recipient list
    
    # Reminder Status
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    delivery_status = Column(String(50))  # delivered, failed, bounced
    error_message = Column(Text)
    
    # Reminder Integration
    external_reminder_id = Column(String(100))  # External system reminder ID
    integration_data = Column(JSON)  # Integration data
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("CalendarEvent", back_populates="reminders")
    user = relationship("User")

# User Availability
class UserAvailability(Base):
    __tablename__ = 'user_availability'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Availability Details
    availability_date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    timezone = Column(String(100), default='UTC')
    
    # Availability Status
    status = Column(Enum(AvailabilityStatus), default=AvailabilityStatus.AVAILABLE)
    status_reason = Column(String(255))  # Reason for availability status
    status_notes = Column(Text)
    
    # Availability Type
    availability_type = Column(String(50), default='general')  # general, meeting, break, travel, etc.
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(JSON)  # Recurrence pattern
    
    # Availability Location
    location = Column(String(255))
    location_type = Column(String(50))  # office, home, travel, etc.
    coordinates = Column(JSON)  # GPS coordinates
    
    # Availability Preferences
    preferred_meeting_duration = Column(Integer, default=60)  # Minutes
    preferred_meeting_times = Column(JSON)  # Preferred meeting times
    buffer_time = Column(Integer, default=15)  # Buffer time in minutes
    
    # Availability Integration
    external_calendar_id = Column(String(100))  # External calendar ID
    integration_data = Column(JSON)  # Integration data
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")

# Calendar Resources
class CalendarResource(Base):
    __tablename__ = 'calendar_resources'
    
    id = Column(Integer, primary_key=True, index=True)
    resource_name = Column(String(255), nullable=False)
    resource_description = Column(Text)
    
    # Resource Classification
    resource_type = Column(String(50), nullable=False)  # room, equipment, vehicle, etc.
    resource_category = Column(String(100))  # meeting_room, conference_room, equipment, etc.
    resource_subcategory = Column(String(100))  # boardroom, training_room, projector, etc.
    
    # Resource Details
    capacity = Column(Integer)  # Maximum capacity
    location = Column(String(255))
    building = Column(String(255))
    floor = Column(String(50))
    room_number = Column(String(50))
    coordinates = Column(JSON)  # GPS coordinates
    
    # Resource Features
    features = Column(JSON)  # Resource features (projector, whiteboard, etc.)
    amenities = Column(JSON)  # Resource amenities
    specifications = Column(JSON)  # Technical specifications
    
    # Resource Availability
    is_available = Column(Boolean, default=True)
    availability_schedule = Column(JSON)  # Availability schedule
    booking_restrictions = Column(JSON)  # Booking restrictions
    advance_booking_limit = Column(Integer)  # Days in advance
    
    # Resource Assignment
    assigned_to_department = Column(Integer, ForeignKey('departments.id'))
    assigned_to_team = Column(Integer, ForeignKey('teams.id'))
    assigned_to_user = Column(Integer, ForeignKey('users.id'))
    
    # Resource Status
    status = Column(String(50), default='active')  # active, inactive, maintenance, retired
    condition = Column(String(50), default='good')  # excellent, good, fair, poor, critical
    
    # Resource Metrics
    utilization_rate = Column(Float, default=0.0)  # Utilization percentage
    booking_count = Column(Integer, default=0)
    total_booking_hours = Column(Float, default=0.0)
    
    # Resource Integration
    external_resource_id = Column(String(100))  # External system resource ID
    integration_data = Column(JSON)  # Integration data
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    assigned_department = relationship("Department")
    assigned_team = relationship("Team")
    assigned_user = relationship("User")
    creator = relationship("User")
    bookings = relationship("ResourceBooking", back_populates="resource", cascade="all, delete-orphan")

# Resource Bookings
class ResourceBooking(Base):
    __tablename__ = 'resource_bookings'
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey('calendar_resources.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('calendar_events.id'))
    
    # Booking Details
    booking_title = Column(String(255), nullable=False)
    booking_description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # Booking Assignment
    booked_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    booked_for = Column(Integer, ForeignKey('users.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    
    # Booking Status
    status = Column(String(50), default='confirmed')  # pending, confirmed, cancelled, completed
    booking_type = Column(String(50), default='standard')  # standard, recurring, emergency, etc.
    
    # Booking Requirements
    setup_time = Column(Integer, default=0)  # Setup time in minutes
    cleanup_time = Column(Integer, default=0)  # Cleanup time in minutes
    special_requirements = Column(Text)
    additional_services = Column(JSON)  # Additional services required
    
    # Booking Costs
    booking_cost = Column(Float, default=0.0)
    additional_costs = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Booking Integration
    external_booking_id = Column(String(100))  # External system booking ID
    integration_data = Column(JSON)  # Integration data
    
    # Booking Notes
    booking_notes = Column(Text)
    cancellation_reason = Column(Text)
    feedback = Column(Text)
    rating = Column(Float)  # Booking rating
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    resource = relationship("CalendarResource", back_populates="bookings")
    event = relationship("CalendarEvent")
    booker = relationship("User", foreign_keys=[booked_by])
    bookee = relationship("User", foreign_keys=[booked_for])
    team = relationship("Team")
    department = relationship("Department")

# External Calendar Integration
class ExternalCalendarIntegration(Base):
    __tablename__ = 'external_calendar_integrations'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Integration Details
    provider = Column(String(50), nullable=False)  # google, microsoft, outlook, etc.
    integration_name = Column(String(255), nullable=False)
    integration_description = Column(Text)
    
    # Integration Configuration
    api_endpoint = Column(String(500))
    api_key = Column(String(500))  # Encrypted API key
    access_token = Column(Text)  # Encrypted access token
    refresh_token = Column(Text)  # Encrypted refresh token
    client_id = Column(String(255))
    client_secret = Column(String(500))  # Encrypted client secret
    
    # Integration Settings
    sync_enabled = Column(Boolean, default=True)
    sync_direction = Column(String(20), default='bidirectional')  # import, export, bidirectional
    sync_frequency = Column(String(20), default='realtime')  # realtime, hourly, daily
    sync_calendars = Column(JSON)  # Calendars to sync
    
    # Integration Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    sync_status = Column(String(50), default='pending')  # pending, syncing, completed, failed
    error_message = Column(Text)
    error_count = Column(Integer, default=0)
    
    # Integration Metrics
    sync_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_successful_sync = Column(DateTime)
    
    # Integration Data
    integration_data = Column(JSON)  # Integration-specific data
    sync_settings = Column(JSON)  # Sync settings
    mapping_rules = Column(JSON)  # Data mapping rules
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    user = relationship("User")

# Calendar Analytics
class CalendarAnalytics(Base):
    __tablename__ = 'calendar_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    analytics_name = Column(String(255), nullable=False)
    analytics_type = Column(String(50), nullable=False)  # usage, efficiency, productivity, etc.
    analytics_period = Column(String(50), nullable=False)  # daily, weekly, monthly, quarterly
    
    # Analytics Data
    analytics_data = Column(JSON, nullable=False)  # Analytics data
    analytics_metrics = Column(JSON, nullable=False)  # Key metrics
    analytics_insights = Column(JSON)  # Analytics insights
    analytics_recommendations = Column(JSON)  # Recommendations
    
    # Calendar Metrics
    total_events = Column(Integer, default=0)
    total_meetings = Column(Integer, default=0)
    total_calls = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    
    # Usage Metrics
    meeting_frequency = Column(Float, default=0.0)  # Meetings per day
    average_meeting_duration = Column(Float, default=0.0)  # Minutes
    meeting_utilization = Column(Float, default=0.0)  # Meeting time percentage
    free_time_percentage = Column(Float, default=0.0)  # Free time percentage
    
    # Productivity Metrics
    productivity_score = Column(Float, default=0.0)  # Productivity score
    meeting_effectiveness = Column(Float, default=0.0)  # Meeting effectiveness
    time_management_score = Column(Float, default=0.0)  # Time management score
    schedule_efficiency = Column(Float, default=0.0)  # Schedule efficiency
    
    # Resource Metrics
    resource_utilization = Column(Float, default=0.0)  # Resource utilization
    resource_conflicts = Column(Integer, default=0)  # Resource conflicts
    booking_success_rate = Column(Float, default=0.0)  # Booking success rate
    cancellation_rate = Column(Float, default=0.0)  # Cancellation rate
    
    # Analytics Trends
    trend_direction = Column(String(20))  # increasing, stable, decreasing
    trend_strength = Column(Float, default=0.0)  # Trend strength
    seasonal_adjustment = Column(Float, default=0.0)  # Seasonal adjustment
    
    # Metadata
    analytics_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    events = relationship("CalendarEvent")
    resources = relationship("CalendarResource")
    bookings = relationship("ResourceBooking")
