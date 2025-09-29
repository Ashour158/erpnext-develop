# Geolocation Tracking System
# Centralized geolocation tracking for all activities across the system

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class ActivityType(enum.Enum):
    MEETING = "Meeting"
    CALL = "Call"
    VISIT = "Visit"
    WORKORDER = "Work Order"
    TASK = "Task"
    TRAINING = "Training"
    APPOINTMENT = "Appointment"
    ATTENDANCE = "Attendance"
    CUSTOM = "Custom"

class TrackingType(enum.Enum):
    CHECK_IN = "Check-in"
    CHECK_OUT = "Check-out"
    LOCATION_UPDATE = "Location Update"
    ACTIVITY_START = "Activity Start"
    ACTIVITY_END = "Activity End"
    BREAK_START = "Break Start"
    BREAK_END = "Break End"

class GeolocationRecord(BaseModel):
    """Centralized geolocation tracking model"""
    __tablename__ = 'geolocation_records'
    
    # Activity Information
    activity_type = db.Column(db.Enum(ActivityType), nullable=False)
    activity_id = db.Column(db.String(100), nullable=False)  # ID of the related activity
    activity_entity_type = db.Column(db.String(100))  # Customer, Opportunity, etc.
    activity_entity_id = db.Column(db.String(100))
    
    # Geolocation Data
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, default=0.0)  # meters
    altitude = db.Column(db.Float, default=0.0)
    speed = db.Column(db.Float, default=0.0)  # m/s
    heading = db.Column(db.Float, default=0.0)  # degrees
    
    # Location Details
    address = db.Column(db.String(500))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    timezone = db.Column(db.String(50))
    
    # Tracking Information
    tracking_type = db.Column(db.Enum(TrackingType), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Float, default=0.0)  # seconds
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Device Information
    device_info = db.Column(db.JSON)  # Device type, OS, etc.
    app_version = db.Column(db.String(50))
    
    # Validation
    is_validated = db.Column(db.Boolean, default=False)
    validation_notes = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'activity_type': self.activity_type.value if self.activity_type else None,
            'activity_id': self.activity_id,
            'activity_entity_type': self.activity_entity_type,
            'activity_entity_id': self.activity_entity_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'altitude': self.altitude,
            'speed': self.speed,
            'heading': self.heading,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'timezone': self.timezone,
            'tracking_type': self.tracking_type.value if self.tracking_type else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'duration': self.duration,
            'user_id': self.user_id,
            'device_info': self.device_info,
            'app_version': self.app_version,
            'is_validated': self.is_validated,
            'validation_notes': self.validation_notes,
            'company_id': self.company_id
        })
        return data

class GeoRestriction(BaseModel):
    """Geolocation restrictions for activities"""
    __tablename__ = 'geo_restrictions'
    
    # Restriction Information
    restriction_name = db.Column(db.String(200), nullable=False)
    restriction_description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Geographic Boundaries
    center_latitude = db.Column(db.Float, nullable=False)
    center_longitude = db.Column(db.Float, nullable=False)
    radius = db.Column(db.Float, nullable=False)  # meters
    polygon_coordinates = db.Column(db.JSON)  # For complex shapes
    
    # Activity Types
    allowed_activity_types = db.Column(db.JSON)  # List of allowed activity types
    restricted_activity_types = db.Column(db.JSON)  # List of restricted activity types
    
    # Time Restrictions
    start_time = db.Column(db.Time)  # Daily start time
    end_time = db.Column(db.Time)  # Daily end time
    allowed_days = db.Column(db.JSON)  # Days of week (0-6)
    
    # User Restrictions
    allowed_users = db.Column(db.JSON)  # List of user IDs
    restricted_users = db.Column(db.JSON)  # List of restricted user IDs
    allowed_roles = db.Column(db.JSON)  # List of role IDs
    restricted_roles = db.Column(db.JSON)  # List of restricted role IDs
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'restriction_name': self.restriction_name,
            'restriction_description': self.restriction_description,
            'is_active': self.is_active,
            'center_latitude': self.center_latitude,
            'center_longitude': self.center_longitude,
            'radius': self.radius,
            'polygon_coordinates': self.polygon_coordinates,
            'allowed_activity_types': self.allowed_activity_types,
            'restricted_activity_types': self.restricted_activity_types,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'allowed_days': self.allowed_days,
            'allowed_users': self.allowed_users,
            'restricted_users': self.restricted_users,
            'allowed_roles': self.allowed_roles,
            'restricted_roles': self.restricted_roles,
            'company_id': self.company_id
        })
        return data

class LocationHistory(BaseModel):
    """Location history for users"""
    __tablename__ = 'location_history'
    
    # Location Information
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, default=0.0)
    altitude = db.Column(db.Float, default=0.0)
    speed = db.Column(db.Float, default=0.0)
    heading = db.Column(db.Float, default=0.0)
    
    # Location Details
    address = db.Column(db.String(500))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    timezone = db.Column(db.String(50))
    
    # Tracking Information
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Float, default=0.0)  # seconds
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Device Information
    device_info = db.Column(db.JSON)
    app_version = db.Column(db.String(50))
    
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
            'heading': self.heading,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'timezone': self.timezone,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'duration': self.duration,
            'user_id': self.user_id,
            'device_info': self.device_info,
            'app_version': self.app_version,
            'company_id': self.company_id
        })
        return data

# Utility Functions
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters"""
    from math import radians, cos, sin, asin, sqrt
    
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    return c * r

def is_within_radius(lat1, lon1, lat2, lon2, radius):
    """Check if two points are within specified radius"""
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    return distance <= radius

def validate_geolocation(user_id, activity_type, latitude, longitude, company_id):
    """Validate geolocation against restrictions"""
    from datetime import datetime, time
    
    # Get active restrictions for the user and activity type
    restrictions = GeoRestriction.query.filter(
        GeoRestriction.company_id == company_id,
        GeoRestriction.is_active == True
    ).all()
    
    for restriction in restrictions:
        # Check if activity type is restricted
        if restriction.restricted_activity_types and activity_type.value in restriction.restricted_activity_types:
            return False, f"Activity type {activity_type.value} is restricted in this area"
        
        # Check if activity type is allowed
        if restriction.allowed_activity_types and activity_type.value not in restriction.allowed_activity_types:
            return False, f"Activity type {activity_type.value} is not allowed in this area"
        
        # Check if user is restricted
        if restriction.restricted_users and user_id in restriction.restricted_users:
            return False, "User is restricted from this area"
        
        # Check if user is allowed
        if restriction.allowed_users and user_id not in restriction.allowed_users:
            return False, "User is not allowed in this area"
        
        # Check geographic boundaries
        if restriction.polygon_coordinates:
            # Check if point is within polygon (simplified check)
            if not is_within_radius(
                restriction.center_latitude, 
                restriction.center_longitude, 
                latitude, 
                longitude, 
                restriction.radius
            ):
                return False, "Location is outside allowed area"
        
        # Check time restrictions
        if restriction.start_time and restriction.end_time:
            current_time = datetime.now().time()
            if not (restriction.start_time <= current_time <= restriction.end_time):
                return False, "Activity not allowed at this time"
        
        # Check day restrictions
        if restriction.allowed_days:
            current_day = datetime.now().weekday()
            if current_day not in restriction.allowed_days:
                return False, "Activity not allowed on this day"
    
    return True, "Location validated successfully"

def create_geolocation_record(user_id, activity_type, activity_id, latitude, longitude, 
                            tracking_type, company_id, **kwargs):
    """Create a geolocation record"""
    # Validate geolocation
    is_valid, message = validate_geolocation(user_id, activity_type, latitude, longitude, company_id)
    
    if not is_valid:
        return None, message
    
    # Create geolocation record
    record = GeolocationRecord(
        activity_type=activity_type,
        activity_id=activity_id,
        activity_entity_type=kwargs.get('activity_entity_type'),
        activity_entity_id=kwargs.get('activity_entity_id'),
        latitude=latitude,
        longitude=longitude,
        accuracy=kwargs.get('accuracy', 0.0),
        altitude=kwargs.get('altitude', 0.0),
        speed=kwargs.get('speed', 0.0),
        heading=kwargs.get('heading', 0.0),
        address=kwargs.get('address'),
        city=kwargs.get('city'),
        state=kwargs.get('state'),
        country=kwargs.get('country'),
        postal_code=kwargs.get('postal_code'),
        timezone=kwargs.get('timezone'),
        tracking_type=tracking_type,
        user_id=user_id,
        device_info=kwargs.get('device_info'),
        app_version=kwargs.get('app_version'),
        is_validated=is_valid,
        validation_notes=message,
        company_id=company_id
    )
    
    db.session.add(record)
    db.session.commit()
    
    return record, message

def get_user_location_history(user_id, company_id, start_date=None, end_date=None, limit=100):
    """Get user location history"""
    query = LocationHistory.query.filter(
        LocationHistory.user_id == user_id,
        LocationHistory.company_id == company_id
    )
    
    if start_date:
        query = query.filter(LocationHistory.timestamp >= start_date)
    
    if end_date:
        query = query.filter(LocationHistory.timestamp <= end_date)
    
    query = query.order_by(LocationHistory.timestamp.desc()).limit(limit)
    
    return query.all()

def get_activity_geolocation(activity_type, activity_id, company_id):
    """Get geolocation records for a specific activity"""
    return GeolocationRecord.query.filter(
        GeolocationRecord.activity_type == activity_type,
        GeolocationRecord.activity_id == activity_id,
        GeolocationRecord.company_id == company_id
    ).all()
