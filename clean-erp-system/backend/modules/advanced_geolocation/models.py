# Advanced Geolocation Models
# Models for advanced geolocation features including geofencing, route optimization, and location-based automation

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime, time, date, timedelta
import enum

class GeofenceType(enum.Enum):
    CIRCLE = "Circle"
    POLYGON = "Polygon"
    RECTANGLE = "Rectangle"
    CUSTOM = "Custom"

class GeofenceStatus(enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    DISABLED = "Disabled"

class TriggerAction(enum.Enum):
    CHECK_IN = "Check In"
    CHECK_OUT = "Check Out"
    NOTIFICATION = "Notification"
    AUTOMATION = "Automation"
    ALERT = "Alert"
    LOG = "Log"

class RouteOptimizationType(enum.Enum):
    SHORTEST_DISTANCE = "Shortest Distance"
    FASTEST_TIME = "Fastest Time"
    LOWEST_COST = "Lowest Cost"
    FUEL_EFFICIENT = "Fuel Efficient"
    MULTI_STOP = "Multi Stop"

class Geofence(BaseModel):
    """Geofence model for location-based automation"""
    __tablename__ = 'geofences'
    
    # Geofence Information
    geofence_name = db.Column(db.String(200), nullable=False)
    geofence_description = db.Column(db.Text)
    geofence_type = db.Column(db.Enum(GeofenceType), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Geographic Boundaries
    center_latitude = db.Column(db.Float, nullable=False)
    center_longitude = db.Column(db.Float, nullable=False)
    radius = db.Column(db.Float, default=0.0)  # meters
    polygon_coordinates = db.Column(db.JSON)  # For polygon geofences
    boundary_points = db.Column(db.JSON)  # For custom boundaries
    
    # Trigger Settings
    entry_trigger = db.Column(db.Boolean, default=True)
    exit_trigger = db.Column(db.Boolean, default=True)
    dwell_time = db.Column(db.Integer, default=0)  # seconds
    trigger_actions = db.Column(db.JSON)  # List of actions to trigger
    
    # User Restrictions
    allowed_users = db.Column(db.JSON)  # List of user IDs
    restricted_users = db.Column(db.JSON)  # List of restricted user IDs
    allowed_roles = db.Column(db.JSON)  # List of role IDs
    
    # Time Restrictions
    active_start_time = db.Column(db.Time)
    active_end_time = db.Column(db.Time)
    active_days = db.Column(db.JSON)  # Days of week (0-6)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'geofence_name': self.geofence_name,
            'geofence_description': self.geofence_description,
            'geofence_type': self.geofence_type.value if self.geofence_type else None,
            'is_active': self.is_active,
            'center_latitude': self.center_latitude,
            'center_longitude': self.center_longitude,
            'radius': self.radius,
            'polygon_coordinates': self.polygon_coordinates,
            'boundary_points': self.boundary_points,
            'entry_trigger': self.entry_trigger,
            'exit_trigger': self.exit_trigger,
            'dwell_time': self.dwell_time,
            'trigger_actions': self.trigger_actions,
            'allowed_users': self.allowed_users,
            'restricted_users': self.restricted_users,
            'allowed_roles': self.allowed_roles,
            'active_start_time': self.active_start_time.isoformat() if self.active_start_time else None,
            'active_end_time': self.active_end_time.isoformat() if self.active_end_time else None,
            'active_days': self.active_days,
            'company_id': self.company_id
        })
        return data

class GeofenceEvent(BaseModel):
    """Geofence event model"""
    __tablename__ = 'geofence_events'
    
    # Event Information
    event_type = db.Column(db.String(50), nullable=False)  # Entry, Exit, Dwell
    event_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    location_latitude = db.Column(db.Float, nullable=False)
    location_longitude = db.Column(db.Float, nullable=False)
    location_accuracy = db.Column(db.Float, default=0.0)
    
    # Geofence Association
    geofence_id = db.Column(db.Integer, db.ForeignKey('geofences.id'), nullable=False)
    geofence = relationship("Geofence")
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Event Details
    event_data = db.Column(db.JSON)  # Additional event data
    triggered_actions = db.Column(db.JSON)  # Actions that were triggered
    is_processed = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'event_type': self.event_type,
            'event_timestamp': self.event_timestamp.isoformat() if self.event_timestamp else None,
            'location_latitude': self.location_latitude,
            'location_longitude': self.location_longitude,
            'location_accuracy': self.location_accuracy,
            'geofence_id': self.geofence_id,
            'user_id': self.user_id,
            'event_data': self.event_data,
            'triggered_actions': self.triggered_actions,
            'is_processed': self.is_processed,
            'company_id': self.company_id
        })
        return data

class Route(BaseModel):
    """Route model for optimization"""
    __tablename__ = 'routes'
    
    # Route Information
    route_name = db.Column(db.String(200), nullable=False)
    route_description = db.Column(db.Text)
    route_type = db.Column(db.Enum(RouteOptimizationType), default=RouteOptimizationType.SHORTEST_DISTANCE)
    is_active = db.Column(db.Boolean, default=True)
    
    # Route Points
    start_latitude = db.Column(db.Float, nullable=False)
    start_longitude = db.Column(db.Float, nullable=False)
    end_latitude = db.Column(db.Float, nullable=False)
    end_longitude = db.Column(db.Float, nullable=False)
    waypoints = db.Column(db.JSON)  # List of waypoint coordinates
    
    # Route Metrics
    total_distance = db.Column(db.Float, default=0.0)  # meters
    estimated_duration = db.Column(db.Float, default=0.0)  # seconds
    estimated_cost = db.Column(db.Float, default=0.0)
    fuel_consumption = db.Column(db.Float, default=0.0)  # liters
    
    # Optimization Settings
    avoid_tolls = db.Column(db.Boolean, default=False)
    avoid_highways = db.Column(db.Boolean, default=False)
    avoid_ferries = db.Column(db.Boolean, default=False)
    traffic_aware = db.Column(db.Boolean, default=True)
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'route_name': self.route_name,
            'route_description': self.route_description,
            'route_type': self.route_type.value if self.route_type else None,
            'is_active': self.is_active,
            'start_latitude': self.start_latitude,
            'start_longitude': self.start_longitude,
            'end_latitude': self.end_latitude,
            'end_longitude': self.end_longitude,
            'waypoints': self.waypoints,
            'total_distance': self.total_distance,
            'estimated_duration': self.estimated_duration,
            'estimated_cost': self.estimated_cost,
            'fuel_consumption': self.fuel_consumption,
            'avoid_tolls': self.avoid_tolls,
            'avoid_highways': self.avoid_highways,
            'avoid_ferries': self.avoid_ferries,
            'traffic_aware': self.traffic_aware,
            'user_id': self.user_id,
            'company_id': self.company_id
        })
        return data

class RouteOptimization(BaseModel):
    """Route optimization model"""
    __tablename__ = 'route_optimizations'
    
    # Optimization Information
    optimization_type = db.Column(db.Enum(RouteOptimizationType), nullable=False)
    optimization_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_optimized = db.Column(db.Boolean, default=False)
    
    # Route Association
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    route = relationship("Route")
    
    # Optimization Results
    optimized_waypoints = db.Column(db.JSON)
    optimized_distance = db.Column(db.Float, default=0.0)
    optimized_duration = db.Column(db.Float, default=0.0)
    optimization_savings = db.Column(db.Float, default=0.0)  # Percentage savings
    
    # AI Analysis
    optimization_confidence = db.Column(db.Float, default=0.0)
    alternative_routes = db.Column(db.JSON)
    traffic_conditions = db.Column(db.JSON)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'optimization_type': self.optimization_type.value if self.optimization_type else None,
            'optimization_date': self.optimization_date.isoformat() if self.optimization_date else None,
            'is_optimized': self.is_optimized,
            'route_id': self.route_id,
            'optimized_waypoints': self.optimized_waypoints,
            'optimized_distance': self.optimized_distance,
            'optimized_duration': self.optimized_duration,
            'optimization_savings': self.optimization_savings,
            'optimization_confidence': self.optimization_confidence,
            'alternative_routes': self.alternative_routes,
            'traffic_conditions': self.traffic_conditions,
            'company_id': self.company_id
        })
        return data

class LocationBasedNotification(BaseModel):
    """Location-based notification model"""
    __tablename__ = 'location_based_notifications'
    
    # Notification Information
    notification_title = db.Column(db.String(200), nullable=False)
    notification_message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='Info')  # Info, Warning, Alert, Success
    
    # Location Triggers
    trigger_latitude = db.Column(db.Float, nullable=False)
    trigger_longitude = db.Column(db.Float, nullable=False)
    trigger_radius = db.Column(db.Float, default=100.0)  # meters
    trigger_conditions = db.Column(db.JSON)  # Additional trigger conditions
    
    # Notification Settings
    is_active = db.Column(db.Boolean, default=True)
    send_immediately = db.Column(db.Boolean, default=True)
    delay_seconds = db.Column(db.Integer, default=0)
    repeat_notification = db.Column(db.Boolean, default=False)
    repeat_interval = db.Column(db.Integer, default=0)  # seconds
    
    # Recipients
    target_users = db.Column(db.JSON)  # List of user IDs
    target_roles = db.Column(db.JSON)  # List of role IDs
    target_geofences = db.Column(db.JSON)  # List of geofence IDs
    
    # Delivery Settings
    delivery_methods = db.Column(db.JSON)  # Email, SMS, Push, In-app
    priority_level = db.Column(db.String(20), default='Normal')
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'notification_title': self.notification_title,
            'notification_message': self.notification_message,
            'notification_type': self.notification_type,
            'trigger_latitude': self.trigger_latitude,
            'trigger_longitude': self.trigger_longitude,
            'trigger_radius': self.trigger_radius,
            'trigger_conditions': self.trigger_conditions,
            'is_active': self.is_active,
            'send_immediately': self.send_immediately,
            'delay_seconds': self.delay_seconds,
            'repeat_notification': self.repeat_notification,
            'repeat_interval': self.repeat_interval,
            'target_users': self.target_users,
            'target_roles': self.target_roles,
            'target_geofences': self.target_geofences,
            'delivery_methods': self.delivery_methods,
            'priority_level': self.priority_level,
            'company_id': self.company_id
        })
        return data

class LocationHistory(BaseModel):
    """Enhanced location history model"""
    __tablename__ = 'location_history_enhanced'
    
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
    movement_type = db.Column(db.String(50), default='Stationary')  # Stationary, Walking, Driving, etc.
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Device Information
    device_info = db.Column(db.JSON)
    app_version = db.Column(db.String(50))
    battery_level = db.Column(db.Float, default=0.0)
    
    # Geofence Association
    geofence_id = db.Column(db.Integer, db.ForeignKey('geofences.id'))
    geofence = relationship("Geofence")
    
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
            'movement_type': self.movement_type,
            'user_id': self.user_id,
            'device_info': self.device_info,
            'app_version': self.app_version,
            'battery_level': self.battery_level,
            'geofence_id': self.geofence_id,
            'company_id': self.company_id
        })
        return data

class TravelTimeCalculation(BaseModel):
    """Travel time calculation model"""
    __tablename__ = 'travel_time_calculations'
    
    # Route Information
    start_latitude = db.Column(db.Float, nullable=False)
    start_longitude = db.Column(db.Float, nullable=False)
    end_latitude = db.Column(db.Float, nullable=False)
    end_longitude = db.Column(db.Float, nullable=False)
    
    # Travel Time Data
    calculated_time = db.Column(db.Float, nullable=False)  # seconds
    distance = db.Column(db.Float, default=0.0)  # meters
    traffic_conditions = db.Column(db.String(50), default='Normal')
    weather_conditions = db.Column(db.String(50), default='Clear')
    
    # Calculation Details
    calculation_method = db.Column(db.String(50), default='API')  # API, Algorithm, Historical
    confidence_score = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'start_latitude': self.start_latitude,
            'start_longitude': self.start_longitude,
            'end_latitude': self.end_latitude,
            'end_longitude': self.end_longitude,
            'calculated_time': self.calculated_time,
            'distance': self.distance,
            'traffic_conditions': self.traffic_conditions,
            'weather_conditions': self.weather_conditions,
            'calculation_method': self.calculation_method,
            'confidence_score': self.confidence_score,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'user_id': self.user_id,
            'company_id': self.company_id
        })
        return data
