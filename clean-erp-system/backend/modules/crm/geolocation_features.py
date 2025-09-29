# Geolocation Features for CRM Module
# Advanced geolocation and location services integrated into CRM

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math
import threading
import queue
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocationType(Enum):
    CUSTOMER_LOCATION = "customer_location"
    OFFICE_LOCATION = "office_location"
    MEETING_LOCATION = "meeting_location"
    WAREHOUSE_LOCATION = "warehouse_location"
    DELIVERY_LOCATION = "delivery_location"
    SALES_TERRITORY = "sales_territory"

class LocationStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"

@dataclass
class Location:
    location_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    location_type: LocationType
    status: LocationStatus = LocationStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LocationTracking:
    tracking_id: str
    user_id: str
    latitude: float
    longitude: float
    timestamp: datetime
    accuracy: float
    activity: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class GeolocationTracking:
    """
    Geolocation Tracking for CRM
    Location tracking and management
    """
    
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.tracking_data: Dict[str, List[LocationTracking]] = {}
        self.geofences: Dict[str, Dict[str, Any]] = {}
        
    def add_location(self, name: str, address: str, latitude: float, longitude: float,
                    location_type: LocationType, metadata: Dict[str, Any] = None) -> Location:
        """Add a location"""
        try:
            location = Location(
                location_id=str(uuid.uuid4()),
                name=name,
                address=address,
                latitude=latitude,
                longitude=longitude,
                location_type=location_type,
                metadata=metadata or {}
            )
            
            self.locations[location.location_id] = location
            
            logger.info(f"Location added: {location.location_id}")
            return location
            
        except Exception as e:
            logger.error(f"Error adding location: {str(e)}")
            raise
    
    def track_location(self, user_id: str, latitude: float, longitude: float,
                      accuracy: float, activity: str, metadata: Dict[str, Any] = None) -> LocationTracking:
        """Track user location"""
        try:
            tracking = LocationTracking(
                tracking_id=str(uuid.uuid4()),
                user_id=user_id,
                latitude=latitude,
                longitude=longitude,
                timestamp=datetime.now(),
                accuracy=accuracy,
                activity=activity,
                metadata=metadata or {}
            )
            
            if user_id not in self.tracking_data:
                self.tracking_data[user_id] = []
            
            self.tracking_data[user_id].append(tracking)
            
            # Keep only last 1000 tracking points per user
            if len(self.tracking_data[user_id]) > 1000:
                self.tracking_data[user_id] = self.tracking_data[user_id][-1000:]
            
            logger.info(f"Location tracked for user: {user_id}")
            return tracking
            
        except Exception as e:
            logger.error(f"Error tracking location: {str(e)}")
            raise
    
    def get_user_locations(self, user_id: str, limit: int = 100) -> List[LocationTracking]:
        """Get user location history"""
        try:
            if user_id not in self.tracking_data:
                return []
            
            return self.tracking_data[user_id][-limit:]
            
        except Exception as e:
            logger.error(f"Error getting user locations: {str(e)}")
            return []
    
    def get_current_location(self, user_id: str) -> Optional[LocationTracking]:
        """Get user's current location"""
        try:
            if user_id not in self.tracking_data or not self.tracking_data[user_id]:
                return None
            
            return self.tracking_data[user_id][-1]
            
        except Exception as e:
            logger.error(f"Error getting current location: {str(e)}")
            return None
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        try:
            # Haversine formula
            R = 6371  # Earth's radius in kilometers
            
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            
            a = (math.sin(dlat/2) * math.sin(dlat/2) +
                 math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                 math.sin(dlon/2) * math.sin(dlon/2))
            
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            return distance
            
        except Exception as e:
            logger.error(f"Error calculating distance: {str(e)}")
            return 0.0
    
    def find_nearby_locations(self, latitude: float, longitude: float, radius_km: float = 10.0) -> List[Location]:
        """Find locations within radius"""
        try:
            nearby_locations = []
            
            for location in self.locations.values():
                distance = self.calculate_distance(
                    latitude, longitude,
                    location.latitude, location.longitude
                )
                
                if distance <= radius_km:
                    nearby_locations.append(location)
            
            return nearby_locations
            
        except Exception as e:
            logger.error(f"Error finding nearby locations: {str(e)}")
            return []
    
    def get_location(self, location_id: str) -> Optional[Location]:
        """Get location by ID"""
        return self.locations.get(location_id)
    
    def update_location(self, location_id: str, updates: Dict[str, Any]) -> bool:
        """Update location"""
        try:
            if location_id not in self.locations:
                return False
            
            location = self.locations[location_id]
            
            # Update fields
            for field, value in updates.items():
                if hasattr(location, field):
                    setattr(location, field, value)
            
            location.updated_at = datetime.now()
            
            logger.info(f"Location updated: {location_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating location: {str(e)}")
            return False

class LocationServices:
    """
    Location Services for CRM
    Location-based services and features
    """
    
    def __init__(self):
        self.geofences: Dict[str, Dict[str, Any]] = {}
        self.location_alerts: Dict[str, List[Dict[str, Any]]] = {}
        self.routes: Dict[str, Dict[str, Any]] = {}
    
    def create_geofence(self, name: str, center_lat: float, center_lon: float,
                       radius_meters: float, location_type: LocationType) -> str:
        """Create a geofence"""
        try:
            geofence_id = str(uuid.uuid4())
            
            geofence = {
                'geofence_id': geofence_id,
                'name': name,
                'center_lat': center_lat,
                'center_lon': center_lon,
                'radius_meters': radius_meters,
                'location_type': location_type.value,
                'status': 'active',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            self.geofences[geofence_id] = geofence
            
            logger.info(f"Geofence created: {geofence_id}")
            return geofence_id
            
        except Exception as e:
            logger.error(f"Error creating geofence: {str(e)}")
            return ""
    
    def check_geofence_entry(self, user_id: str, latitude: float, longitude: float) -> List[str]:
        """Check if user entered any geofences"""
        try:
            entered_geofences = []
            
            for geofence_id, geofence in self.geofences.items():
                if geofence['status'] != 'active':
                    continue
                
                # Calculate distance to geofence center
                distance = self._calculate_distance(
                    latitude, longitude,
                    geofence['center_lat'], geofence['center_lon']
                )
                
                # Convert to meters
                distance_meters = distance * 1000
                
                if distance_meters <= geofence['radius_meters']:
                    entered_geofences.append(geofence_id)
                    
                    # Create alert
                    self._create_location_alert(
                        user_id, geofence_id, 'entry',
                        f"Entered {geofence['name']}"
                    )
            
            return entered_geofences
            
        except Exception as e:
            logger.error(f"Error checking geofence entry: {str(e)}")
            return []
    
    def check_geofence_exit(self, user_id: str, latitude: float, longitude: float) -> List[str]:
        """Check if user exited any geofences"""
        try:
            exited_geofences = []
            
            for geofence_id, geofence in self.geofences.items():
                if geofence['status'] != 'active':
                    continue
                
                # Calculate distance to geofence center
                distance = self._calculate_distance(
                    latitude, longitude,
                    geofence['center_lat'], geofence['center_lon']
                )
                
                # Convert to meters
                distance_meters = distance * 1000
                
                if distance_meters > geofence['radius_meters']:
                    exited_geofences.append(geofence_id)
                    
                    # Create alert
                    self._create_location_alert(
                        user_id, geofence_id, 'exit',
                        f"Exited {geofence['name']}"
                    )
            
            return exited_geofences
            
        except Exception as e:
            logger.error(f"Error checking geofence exit: {str(e)}")
            return []
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        try:
            R = 6371  # Earth's radius in kilometers
            
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            
            a = (math.sin(dlat/2) * math.sin(dlat/2) +
                 math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                 math.sin(dlon/2) * math.sin(dlon/2))
            
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            return distance
            
        except Exception as e:
            logger.error(f"Error calculating distance: {str(e)}")
            return 0.0
    
    def _create_location_alert(self, user_id: str, geofence_id: str, alert_type: str, message: str):
        """Create location alert"""
        try:
            if user_id not in self.location_alerts:
                self.location_alerts[user_id] = []
            
            alert = {
                'alert_id': str(uuid.uuid4()),
                'user_id': user_id,
                'geofence_id': geofence_id,
                'alert_type': alert_type,
                'message': message,
                'timestamp': datetime.now(),
                'status': 'active'
            }
            
            self.location_alerts[user_id].append(alert)
            
            logger.info(f"Location alert created: {alert['alert_id']}")
            
        except Exception as e:
            logger.error(f"Error creating location alert: {str(e)}")
    
    def get_location_alerts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get location alerts for user"""
        return self.location_alerts.get(user_id, [])
    
    def create_route(self, name: str, waypoints: List[Tuple[float, float]], 
                    route_type: str = 'driving') -> str:
        """Create a route"""
        try:
            route_id = str(uuid.uuid4())
            
            route = {
                'route_id': route_id,
                'name': name,
                'waypoints': waypoints,
                'route_type': route_type,
                'status': 'active',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            self.routes[route_id] = route
            
            logger.info(f"Route created: {route_id}")
            return route_id
            
        except Exception as e:
            logger.error(f"Error creating route: {str(e)}")
            return ""
    
    def get_route(self, route_id: str) -> Optional[Dict[str, Any]]:
        """Get route by ID"""
        return self.routes.get(route_id)

class GeoAnalytics:
    """
    Geo Analytics for CRM
    Location-based analytics and insights
    """
    
    def __init__(self):
        self.analytics_data: Dict[str, Dict[str, Any]] = {}
    
    def analyze_user_movement(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze user movement patterns"""
        try:
            # This would analyze user movement data
            # For now, return mock analytics
            analytics = {
                'user_id': user_id,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_distance': 150.5,  # kilometers
                'average_speed': 25.3,   # km/h
                'most_visited_location': 'Office',
                'time_spent_at_locations': {
                    'Office': 8.5,  # hours
                    'Customer Site A': 2.0,
                    'Customer Site B': 1.5
                },
                'geofence_entries': 15,
                'geofence_exits': 12,
                'route_efficiency': 0.85
            }
            
            self.analytics_data[user_id] = analytics
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error analyzing user movement: {str(e)}")
            return {}
    
    def get_territory_analytics(self, territory_id: str) -> Dict[str, Any]:
        """Get territory analytics"""
        try:
            # This would analyze territory data
            # For now, return mock analytics
            analytics = {
                'territory_id': territory_id,
                'total_customers': 150,
                'active_customers': 120,
                'average_distance_to_customers': 25.3,  # km
                'coverage_area': 500.0,  # km²
                'customer_density': 0.24,  # customers per km²
                'top_performing_areas': [
                    {'area': 'Downtown', 'customers': 45, 'revenue': 125000},
                    {'area': 'Business District', 'customers': 38, 'revenue': 98000},
                    {'area': 'Industrial Zone', 'customers': 32, 'revenue': 87000}
                ]
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting territory analytics: {str(e)}")
            return {}
    
    def get_location_insights(self, location_id: str) -> Dict[str, Any]:
        """Get location insights"""
        try:
            # This would analyze location data
            # For now, return mock insights
            insights = {
                'location_id': location_id,
                'visit_frequency': 15,  # visits per month
                'average_visit_duration': 45,  # minutes
                'peak_hours': ['09:00-11:00', '14:00-16:00'],
                'customer_satisfaction': 4.2,  # out of 5
                'revenue_generated': 25000,  # per month
                'recommendations': [
                    'Increase visit frequency during peak hours',
                    'Consider extending visit duration',
                    'Focus on high-value customers in this area'
                ]
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting location insights: {str(e)}")
            return {}

# Global geolocation features instances
geolocation_tracking = GeolocationTracking()
location_services = LocationServices()
geo_analytics = GeoAnalytics()
