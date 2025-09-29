# Booking Models - Complete Resource Booking and Scheduling
# Advanced booking models without Frappe dependencies

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date, timedelta
import enum

# Enums
class ResourceType(enum.Enum):
    ROOM = "Room"
    EQUIPMENT = "Equipment"
    VEHICLE = "Vehicle"
    FACILITY = "Facility"
    PERSON = "Person"

class BookingStatus(enum.Enum):
    DRAFT = "Draft"
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    NO_SHOW = "No Show"

class BookingPriority(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class RecurrenceType(enum.Enum):
    NONE = "None"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"

# Resource Category Model
class ResourceCategory(BaseModel):
    """Resource Category model"""
    __tablename__ = 'resource_categories'
    
    category_name = db.Column(db.String(200), nullable=False)
    category_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Category Settings
    booking_advance_days = db.Column(db.Integer, default=30)
    cancellation_hours = db.Column(db.Integer, default=24)
    requires_approval = db.Column(db.Boolean, default=False)
    max_booking_duration_hours = db.Column(db.Float, default=24.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    resources = relationship("Resource", back_populates="category")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'category_name': self.category_name,
            'category_code': self.category_code,
            'description': self.description,
            'booking_advance_days': self.booking_advance_days,
            'cancellation_hours': self.cancellation_hours,
            'requires_approval': self.requires_approval,
            'max_booking_duration_hours': self.max_booking_duration_hours,
            'company_id': self.company_id
        })
        return data

# Resource Model
class Resource(BaseModel):
    """Resource model"""
    __tablename__ = 'resources'
    
    resource_name = db.Column(db.String(200), nullable=False)
    resource_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Resource Details
    resource_type = db.Column(db.Enum(ResourceType), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('resource_categories.id'), nullable=False)
    category = relationship("ResourceCategory", back_populates="resources")
    
    # Location Information
    location = db.Column(db.String(200))
    address = db.Column(db.Text)
    capacity = db.Column(db.Integer, default=1)
    
    # Resource Settings
    is_active = db.Column(db.Boolean, default=True)
    is_bookable = db.Column(db.Boolean, default=True)
    requires_approval = db.Column(db.Boolean, default=False)
    
    # Pricing
    hourly_rate = db.Column(db.Float, default=0.0)
    daily_rate = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Availability
    available_from_time = db.Column(db.String(10), default='09:00')
    available_to_time = db.Column(db.String(10), default='17:00')
    available_days = db.Column(db.JSON)  # Days of week [1,2,3,4,5] for Mon-Fri
    
    # Features and Amenities
    features = db.Column(db.JSON)  # WiFi, Projector, etc.
    images = db.Column(db.JSON)  # List of image URLs
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    bookings = relationship("Booking", back_populates="resource")
    booking_slots = relationship("BookingSlot", back_populates="resource")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'resource_name': self.resource_name,
            'resource_code': self.resource_code,
            'description': self.description,
            'resource_type': self.resource_type.value if self.resource_type else None,
            'category_id': self.category_id,
            'location': self.location,
            'address': self.address,
            'capacity': self.capacity,
            'is_active': self.is_active,
            'is_bookable': self.is_bookable,
            'requires_approval': self.requires_approval,
            'hourly_rate': self.hourly_rate,
            'daily_rate': self.daily_rate,
            'currency': self.currency,
            'available_from_time': self.available_from_time,
            'available_to_time': self.available_to_time,
            'available_days': self.available_days,
            'features': self.features,
            'images': self.images,
            'company_id': self.company_id
        })
        return data

# Booking Model
class Booking(BaseModel):
    """Booking model"""
    __tablename__ = 'bookings'
    
    booking_number = db.Column(db.String(50), unique=True, nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)
    
    # Resource
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    resource = relationship("Resource", back_populates="bookings")
    
    # Booking Details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Timing
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    duration_hours = db.Column(db.Float, default=0.0)
    
    # Booking Information
    booked_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    booked_by = relationship("Employee")
    
    # Attendees
    attendees = db.Column(db.JSON)  # List of attendee information
    expected_attendees = db.Column(db.Integer, default=1)
    
    # Status and Priority
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING)
    priority = db.Column(db.Enum(BookingPriority), default=BookingPriority.MEDIUM)
    
    # Recurrence
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_type = db.Column(db.Enum(RecurrenceType), default=RecurrenceType.NONE)
    recurrence_end_date = db.Column(db.Date)
    
    # Pricing
    total_cost = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Additional Information
    special_requirements = db.Column(db.Text)
    setup_notes = db.Column(db.Text)
    cancellation_reason = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    booking_slots = relationship("BookingSlot", back_populates="booking")
    recurring_bookings = relationship("RecurringBooking", back_populates="booking")
    conflicts = relationship("BookingConflict", back_populates="booking")
    approvals = relationship("BookingApproval", back_populates="booking")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'booking_number': self.booking_number,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'resource_id': self.resource_id,
            'title': self.title,
            'description': self.description,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'duration_hours': self.duration_hours,
            'booked_by_id': self.booked_by_id,
            'attendees': self.attendees,
            'expected_attendees': self.expected_attendees,
            'status': self.status.value if self.status else None,
            'priority': self.priority.value if self.priority else None,
            'is_recurring': self.is_recurring,
            'recurrence_type': self.recurrence_type.value if self.recurrence_type else None,
            'recurrence_end_date': self.recurrence_end_date.isoformat() if self.recurrence_end_date else None,
            'total_cost': self.total_cost,
            'currency': self.currency,
            'special_requirements': self.special_requirements,
            'setup_notes': self.setup_notes,
            'cancellation_reason': self.cancellation_reason,
            'company_id': self.company_id
        })
        return data

# Booking Slot Model
class BookingSlot(BaseModel):
    """Booking Slot model"""
    __tablename__ = 'booking_slots'
    
    # Resource
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    resource = relationship("Resource", back_populates="booking_slots")
    
    # Booking
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    booking = relationship("Booking", back_populates="booking_slots")
    
    # Slot Details
    slot_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    
    # Status
    is_available = db.Column(db.Boolean, default=True)
    is_blocked = db.Column(db.Boolean, default=False)
    block_reason = db.Column(db.String(200))
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'resource_id': self.resource_id,
            'booking_id': self.booking_id,
            'slot_date': self.slot_date.isoformat() if self.slot_date else None,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'is_available': self.is_available,
            'is_blocked': self.is_blocked,
            'block_reason': self.block_reason,
            'company_id': self.company_id
        })
        return data

# Booking Rule Model
class BookingRule(BaseModel):
    """Booking Rule model"""
    __tablename__ = 'booking_rules'
    
    rule_name = db.Column(db.String(200), nullable=False)
    rule_type = db.Column(db.String(50), nullable=False)  # Time, Duration, Capacity, etc.
    description = db.Column(db.Text)
    
    # Rule Conditions
    conditions = db.Column(db.JSON)  # Rule conditions
    is_active = db.Column(db.Boolean, default=True)
    
    # Rule Actions
    actions = db.Column(db.JSON)  # Actions to take when rule is triggered
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'rule_name': self.rule_name,
            'rule_type': self.rule_type,
            'description': self.description,
            'conditions': self.conditions,
            'is_active': self.is_active,
            'actions': self.actions,
            'company_id': self.company_id
        })
        return data

# Recurring Booking Model
class RecurringBooking(BaseModel):
    """Recurring Booking model"""
    __tablename__ = 'recurring_bookings'
    
    # Parent Booking
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    booking = relationship("Booking", back_populates="recurring_bookings")
    
    # Recurrence Details
    recurrence_type = db.Column(db.Enum(RecurrenceType), nullable=False)
    recurrence_interval = db.Column(db.Integer, default=1)  # Every 2 weeks, etc.
    recurrence_end_date = db.Column(db.Date)
    max_occurrences = db.Column(db.Integer, default=0)
    
    # Generated Bookings
    generated_booking_ids = db.Column(db.JSON)  # List of generated booking IDs
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'booking_id': self.booking_id,
            'recurrence_type': self.recurrence_type.value if self.recurrence_type else None,
            'recurrence_interval': self.recurrence_interval,
            'recurrence_end_date': self.recurrence_end_date.isoformat() if self.recurrence_end_date else None,
            'max_occurrences': self.max_occurrences,
            'generated_booking_ids': self.generated_booking_ids,
            'company_id': self.company_id
        })
        return data

# Booking Conflict Model
class BookingConflict(BaseModel):
    """Booking Conflict model"""
    __tablename__ = 'booking_conflicts'
    
    # Booking
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    booking = relationship("Booking", back_populates="conflicts")
    
    # Conflicting Booking
    conflicting_booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    conflicting_booking = relationship("Booking", foreign_keys=[conflicting_booking_id])
    
    # Conflict Details
    conflict_type = db.Column(db.String(50))  # Time, Resource, Capacity
    conflict_description = db.Column(db.Text)
    severity = db.Column(db.String(20), default='Medium')  # Low, Medium, High
    
    # Resolution
    is_resolved = db.Column(db.Boolean, default=False)
    resolution_notes = db.Column(db.Text)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    resolved_by = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'booking_id': self.booking_id,
            'conflicting_booking_id': self.conflicting_booking_id,
            'conflict_type': self.conflict_type,
            'conflict_description': self.conflict_description,
            'severity': self.severity,
            'is_resolved': self.is_resolved,
            'resolution_notes': self.resolution_notes,
            'resolved_by_id': self.resolved_by_id,
            'company_id': self.company_id
        })
        return data

# Booking Approval Model
class BookingApproval(BaseModel):
    """Booking Approval model"""
    __tablename__ = 'booking_approvals'
    
    # Booking
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    booking = relationship("Booking", back_populates="approvals")
    
    # Approver
    approver_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    approver = relationship("Employee")
    
    # Approval Details
    approval_status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    approval_date = db.Column(db.DateTime)
    approval_notes = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'booking_id': self.booking_id,
            'approver_id': self.approver_id,
            'approval_status': self.approval_status,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'approval_notes': self.approval_notes,
            'company_id': self.company_id
        })
        return data
