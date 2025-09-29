# AI Smart Scheduling Models
# Models for AI-powered intelligent scheduling and meeting optimization

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime, time, date, timedelta
import enum

class MeetingType(enum.Enum):
    ONE_ON_ONE = "One-on-One"
    TEAM_MEETING = "Team Meeting"
    CLIENT_MEETING = "Client Meeting"
    INTERVIEW = "Interview"
    PRESENTATION = "Presentation"
    WORKSHOP = "Workshop"
    CONFERENCE = "Conference"
    STANDUP = "Standup"
    RETROSPECTIVE = "Retrospective"
    PLANNING = "Planning"

class PriorityLevel(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class ConflictResolution(enum.Enum):
    AUTO_RESOLVE = "Auto Resolve"
    MANUAL_REVIEW = "Manual Review"
    ESCALATE = "Escalate"
    POSTPONE = "Postpone"

class SchedulingPreference(enum.Enum):
    MORNING = "Morning"
    AFTERNOON = "Afternoon"
    EVENING = "Evening"
    FLEXIBLE = "Flexible"

class MeetingSuggestion(BaseModel):
    """AI-powered meeting suggestions model"""
    __tablename__ = 'meeting_suggestions'
    
    # Meeting Information
    meeting_title = db.Column(db.String(200), nullable=False)
    meeting_description = db.Column(db.Text)
    meeting_type = db.Column(db.Enum(MeetingType), nullable=False)
    priority_level = db.Column(db.Enum(PriorityLevel), default=PriorityLevel.MEDIUM)
    
    # Suggested Timing
    suggested_start_time = db.Column(db.DateTime, nullable=False)
    suggested_end_time = db.Column(db.DateTime, nullable=False)
    suggested_duration = db.Column(db.Float, default=1.0)  # hours
    
    # AI Analysis
    confidence_score = db.Column(db.Float, default=0.0)  # 0-1
    ai_reasoning = db.Column(db.Text)
    alternative_times = db.Column(db.JSON)  # List of alternative time suggestions
    
    # Participants
    organizer_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    organizer = relationship("Employee")
    suggested_attendees = db.Column(db.JSON)  # List of attendee IDs
    
    # Location
    suggested_location = db.Column(db.String(500))
    location_coordinates = db.Column(db.JSON)
    is_virtual = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'meeting_title': self.meeting_title,
            'meeting_description': self.meeting_description,
            'meeting_type': self.meeting_type.value if self.meeting_type else None,
            'priority_level': self.priority_level.value if self.priority_level else None,
            'suggested_start_time': self.suggested_start_time.isoformat() if self.suggested_start_time else None,
            'suggested_end_time': self.suggested_end_time.isoformat() if self.suggested_end_time else None,
            'suggested_duration': self.suggested_duration,
            'confidence_score': self.confidence_score,
            'ai_reasoning': self.ai_reasoning,
            'alternative_times': self.alternative_times,
            'organizer_id': self.organizer_id,
            'suggested_attendees': self.suggested_attendees,
            'suggested_location': self.suggested_location,
            'location_coordinates': self.location_coordinates,
            'is_virtual': self.is_virtual,
            'company_id': self.company_id
        })
        return data

class SchedulingConflict(BaseModel):
    """Scheduling conflict model"""
    __tablename__ = 'scheduling_conflicts'
    
    # Conflict Information
    conflict_type = db.Column(db.String(100), nullable=False)  # Time, Resource, Location, etc.
    conflict_description = db.Column(db.Text)
    conflict_severity = db.Column(db.Enum(PriorityLevel), default=PriorityLevel.MEDIUM)
    
    # Conflicting Events
    primary_event_id = db.Column(db.String(100), nullable=False)
    conflicting_event_id = db.Column(db.String(100), nullable=False)
    conflict_start_time = db.Column(db.DateTime, nullable=False)
    conflict_end_time = db.Column(db.DateTime, nullable=False)
    
    # Resolution
    resolution_status = db.Column(db.String(50), default='Pending')  # Pending, Resolved, Escalated
    resolution_method = db.Column(db.Enum(ConflictResolution))
    resolution_notes = db.Column(db.Text)
    resolved_by = db.Column(db.Integer, db.ForeignKey('employees.id'))
    resolver = relationship("Employee")
    resolved_at = db.Column(db.DateTime)
    
    # AI Analysis
    ai_suggested_resolution = db.Column(db.JSON)
    resolution_confidence = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'conflict_type': self.conflict_type,
            'conflict_description': self.conflict_description,
            'conflict_severity': self.conflict_severity.value if self.conflict_severity else None,
            'primary_event_id': self.primary_event_id,
            'conflicting_event_id': self.conflicting_event_id,
            'conflict_start_time': self.conflict_start_time.isoformat() if self.conflict_start_time else None,
            'conflict_end_time': self.conflict_end_time.isoformat() if self.conflict_end_time else None,
            'resolution_status': self.resolution_status,
            'resolution_method': self.resolution_method.value if self.resolution_method else None,
            'resolution_notes': self.resolution_notes,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'ai_suggested_resolution': self.ai_suggested_resolution,
            'resolution_confidence': self.resolution_confidence,
            'company_id': self.company_id
        })
        return data

class ResourceOptimization(BaseModel):
    """Resource optimization model"""
    __tablename__ = 'resource_optimizations'
    
    # Resource Information
    resource_type = db.Column(db.String(100), nullable=False)  # Room, Equipment, Vehicle, etc.
    resource_id = db.Column(db.String(100), nullable=False)
    resource_name = db.Column(db.String(200), nullable=False)
    
    # Optimization Data
    utilization_rate = db.Column(db.Float, default=0.0)  # 0-1
    efficiency_score = db.Column(db.Float, default=0.0)  # 0-1
    cost_per_hour = db.Column(db.Float, default=0.0)
    
    # Scheduling
    optimal_start_time = db.Column(db.DateTime)
    optimal_end_time = db.Column(db.DateTime)
    availability_windows = db.Column(db.JSON)  # List of available time windows
    
    # AI Analysis
    optimization_recommendations = db.Column(db.JSON)
    predicted_demand = db.Column(db.Float, default=0.0)
    maintenance_schedule = db.Column(db.JSON)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'utilization_rate': self.utilization_rate,
            'efficiency_score': self.efficiency_score,
            'cost_per_hour': self.cost_per_hour,
            'optimal_start_time': self.optimal_start_time.isoformat() if self.optimal_start_time else None,
            'optimal_end_time': self.optimal_end_time.isoformat() if self.optimal_end_time else None,
            'availability_windows': self.availability_windows,
            'optimization_recommendations': self.optimization_recommendations,
            'predicted_demand': self.predicted_demand,
            'maintenance_schedule': self.maintenance_schedule,
            'company_id': self.company_id
        })
        return data

class PredictiveAnalytics(BaseModel):
    """Predictive analytics model"""
    __tablename__ = 'predictive_analytics'
    
    # Analytics Information
    analytics_type = db.Column(db.String(100), nullable=False)  # Meeting Success, Attendance, Productivity
    prediction_date = db.Column(db.Date, nullable=False)
    prediction_horizon = db.Column(db.Integer, default=30)  # days
    
    # Predictions
    predicted_value = db.Column(db.Float, nullable=False)
    confidence_interval_lower = db.Column(db.Float, default=0.0)
    confidence_interval_upper = db.Column(db.Float, default=0.0)
    accuracy_score = db.Column(db.Float, default=0.0)
    
    # Model Information
    model_version = db.Column(db.String(50), default='1.0')
    training_data_size = db.Column(db.Integer, default=0)
    last_training_date = db.Column(db.DateTime)
    
    # Context
    context_data = db.Column(db.JSON)  # Additional context for the prediction
    influencing_factors = db.Column(db.JSON)  # Factors that influenced the prediction
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'analytics_type': self.analytics_type,
            'prediction_date': self.prediction_date.isoformat() if self.prediction_date else None,
            'prediction_horizon': self.prediction_horizon,
            'predicted_value': self.predicted_value,
            'confidence_interval_lower': self.confidence_interval_lower,
            'confidence_interval_upper': self.confidence_interval_upper,
            'accuracy_score': self.accuracy_score,
            'model_version': self.model_version,
            'training_data_size': self.training_data_size,
            'last_training_date': self.last_training_date.isoformat() if self.last_training_date else None,
            'context_data': self.context_data,
            'influencing_factors': self.influencing_factors,
            'company_id': self.company_id
        })
        return data

class UserSchedulingProfile(BaseModel):
    """User scheduling preferences and patterns"""
    __tablename__ = 'user_scheduling_profiles'
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Preferences
    preferred_meeting_times = db.Column(db.JSON)  # List of preferred time slots
    preferred_meeting_duration = db.Column(db.Float, default=1.0)  # hours
    preferred_meeting_type = db.Column(db.Enum(MeetingType), default=MeetingType.TEAM_MEETING)
    scheduling_preference = db.Column(db.Enum(SchedulingPreference), default=SchedulingPreference.FLEXIBLE)
    
    # Patterns
    most_productive_hours = db.Column(db.JSON)  # Hours when user is most productive
    least_productive_hours = db.Column(db.JSON)  # Hours when user is least productive
    typical_meeting_duration = db.Column(db.Float, default=1.0)
    meeting_frequency = db.Column(db.Float, default=0.0)  # meetings per day
    
    # AI Learning
    ai_learning_enabled = db.Column(db.Boolean, default=True)
    learning_data_points = db.Column(db.Integer, default=0)
    last_learning_update = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'preferred_meeting_times': self.preferred_meeting_times,
            'preferred_meeting_duration': self.preferred_meeting_duration,
            'preferred_meeting_type': self.preferred_meeting_type.value if self.preferred_meeting_type else None,
            'scheduling_preference': self.scheduling_preference.value if self.scheduling_preference else None,
            'most_productive_hours': self.most_productive_hours,
            'least_productive_hours': self.least_productive_hours,
            'typical_meeting_duration': self.typical_meeting_duration,
            'meeting_frequency': self.meeting_frequency,
            'ai_learning_enabled': self.ai_learning_enabled,
            'learning_data_points': self.learning_data_points,
            'last_learning_update': self.last_learning_update.isoformat() if self.last_learning_update else None,
            'company_id': self.company_id
        })
        return data
