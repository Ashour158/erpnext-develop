# Advanced Geolocation API
# API endpoints for advanced geolocation features including geofencing, route optimization, and location-based automation

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from .models import (
    Geofence, GeofenceEvent, Route, RouteOptimization, LocationBasedNotification,
    LocationHistory, TravelTimeCalculation,
    GeofenceType, GeofenceStatus, TriggerAction, RouteOptimizationType
)
from datetime import datetime, timedelta
import json
import math

advanced_geolocation_bp = Blueprint('advanced_geolocation', __name__)

# Geofencing
@advanced_geolocation_bp.route('/geofences', methods=['GET'])
@jwt_required()
def get_geofences():
    """Get geofences"""
    try:
        company_id = request.args.get('company_id', type=int)
        geofence_type = request.args.get('geofence_type')
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = Geofence.query.filter(Geofence.company_id == company_id)
        
        if geofence_type:
            query = query.filter(Geofence.geofence_type == GeofenceType(geofence_type))
        
        if is_active is not None:
            query = query.filter(Geofence.is_active == is_active)
        
        geofences = query.all()
        
        return jsonify([geofence.to_dict() for geofence in geofences])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_geolocation_bp.route('/geofences', methods=['POST'])
@jwt_required()
def create_geofence():
    """Create geofence"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['geofence_name', 'geofence_type', 'center_latitude', 'center_longitude', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create geofence
        geofence = Geofence(
            geofence_name=data['geofence_name'],
            geofence_description=data.get('geofence_description'),
            geofence_type=GeofenceType(data['geofence_type']),
            center_latitude=data['center_latitude'],
            center_longitude=data['center_longitude'],
            radius=data.get('radius', 0.0),
            polygon_coordinates=data.get('polygon_coordinates'),
            boundary_points=data.get('boundary_points'),
            entry_trigger=data.get('entry_trigger', True),
            exit_trigger=data.get('exit_trigger', True),
            dwell_time=data.get('dwell_time', 0),
            trigger_actions=data.get('trigger_actions'),
            allowed_users=data.get('allowed_users'),
            restricted_users=data.get('restricted_users'),
            allowed_roles=data.get('allowed_roles'),
            active_start_time=datetime.strptime(data['active_start_time'], '%H:%M').time() if data.get('active_start_time') else None,
            active_end_time=datetime.strptime(data['active_end_time'], '%H:%M').time() if data.get('active_end_time') else None,
            active_days=data.get('active_days'),
            company_id=data['company_id']
        )
        
        db.session.add(geofence)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('geofence_created', geofence.to_dict(), data['company_id'])
        
        return jsonify(geofence.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_geolocation_bp.route('/geofences/<int:geofence_id>', methods=['GET'])
@jwt_required()
def get_geofence(geofence_id):
    """Get specific geofence"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        geofence = Geofence.query.filter(
            Geofence.id == geofence_id,
            Geofence.company_id == company_id
        ).first()
        
        if not geofence:
            return jsonify({'error': 'Geofence not found'}), 404
        
        return jsonify(geofence.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_geolocation_bp.route('/geofences/<int:geofence_id>', methods=['PUT'])
@jwt_required()
def update_geofence(geofence_id):
    """Update geofence"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        geofence = Geofence.query.filter(
            Geofence.id == geofence_id,
            Geofence.company_id == data.get('company_id')
        ).first()
        
        if not geofence:
            return jsonify({'error': 'Geofence not found'}), 404
        
        # Update fields
        for field in ['geofence_name', 'geofence_description', 'is_active', 'center_latitude',
                     'center_longitude', 'radius', 'polygon_coordinates', 'boundary_points',
                     'entry_trigger', 'exit_trigger', 'dwell_time', 'trigger_actions',
                     'allowed_users', 'restricted_users', 'allowed_roles', 'active_days']:
            if field in data:
                setattr(geofence, field, data[field])
        
        if 'geofence_type' in data:
            geofence.geofence_type = GeofenceType(data['geofence_type'])
        
        if 'active_start_time' in data and data['active_start_time']:
            geofence.active_start_time = datetime.strptime(data['active_start_time'], '%H:%M').time()
        
        if 'active_end_time' in data and data['active_end_time']:
            geofence.active_end_time = datetime.strptime(data['active_end_time'], '%H:%M').time()
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('geofence_updated', geofence.to_dict(), geofence.company_id)
        
        return jsonify(geofence.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_geolocation_bp.route('/geofences/<int:geofence_id>', methods=['DELETE'])
@jwt_required()
def delete_geofence(geofence_id):
    """Delete geofence"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        geofence = Geofence.query.filter(
            Geofence.id == geofence_id,
            Geofence.company_id == company_id
        ).first()
        
        if not geofence:
            return jsonify({'error': 'Geofence not found'}), 404
        
        # Soft delete
        geofence.is_active = False
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('geofence_deleted', {'id': geofence_id}, company_id)
        
        return jsonify({'message': 'Geofence deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Geofence Events
@advanced_geolocation_bp.route('/geofence-events', methods=['GET'])
@jwt_required()
def get_geofence_events():
    """Get geofence events"""
    try:
        company_id = request.args.get('company_id', type=int)
        user_id = request.args.get('user_id', type=int)
        geofence_id = request.args.get('geofence_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = GeofenceEvent.query.filter(GeofenceEvent.company_id == company_id)
        
        if user_id:
            query = query.filter(GeofenceEvent.user_id == user_id)
        
        if geofence_id:
            query = query.filter(GeofenceEvent.geofence_id == geofence_id)
        
        if start_date:
            query = query.filter(GeofenceEvent.event_timestamp >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(GeofenceEvent.event_timestamp <= datetime.fromisoformat(end_date))
        
        events = query.order_by(GeofenceEvent.event_timestamp.desc()).limit(100).all()
        
        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_geolocation_bp.route('/geofence-events', methods=['POST'])
@jwt_required()
def create_geofence_event():
    """Create geofence event"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['event_type', 'geofence_id', 'location_latitude', 'location_longitude', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create event
        event = GeofenceEvent(
            event_type=data['event_type'],
            event_timestamp=datetime.fromisoformat(data['event_timestamp']) if data.get('event_timestamp') else datetime.utcnow(),
            location_latitude=data['location_latitude'],
            location_longitude=data['location_longitude'],
            location_accuracy=data.get('location_accuracy', 0.0),
            geofence_id=data['geofence_id'],
            user_id=user_id,
            event_data=data.get('event_data'),
            triggered_actions=data.get('triggered_actions'),
            company_id=data['company_id']
        )
        
        db.session.add(event)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('geofence_event_created', event.to_dict(), data['company_id'])
        
        return jsonify(event.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route Optimization
@advanced_geolocation_bp.route('/routes', methods=['GET'])
@jwt_required()
def get_routes():
    """Get routes"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        route_type = request.args.get('route_type')
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = Route.query.filter(Route.company_id == company_id)
        
        if route_type:
            query = query.filter(Route.route_type == RouteOptimizationType(route_type))
        
        if is_active is not None:
            query = query.filter(Route.is_active == is_active)
        
        routes = query.all()
        
        return jsonify([route.to_dict() for route in routes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_geolocation_bp.route('/routes', methods=['POST'])
@jwt_required()
def create_route():
    """Create route"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['route_name', 'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create route
        route = Route(
            route_name=data['route_name'],
            route_description=data.get('route_description'),
            route_type=RouteOptimizationType(data.get('route_type', 'SHORTEST_DISTANCE')),
            start_latitude=data['start_latitude'],
            start_longitude=data['start_longitude'],
            end_latitude=data['end_latitude'],
            end_longitude=data['end_longitude'],
            waypoints=data.get('waypoints'),
            total_distance=data.get('total_distance', 0.0),
            estimated_duration=data.get('estimated_duration', 0.0),
            estimated_cost=data.get('estimated_cost', 0.0),
            fuel_consumption=data.get('fuel_consumption', 0.0),
            avoid_tolls=data.get('avoid_tolls', False),
            avoid_highways=data.get('avoid_highways', False),
            avoid_ferries=data.get('avoid_ferries', False),
            traffic_aware=data.get('traffic_aware', True),
            user_id=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(route)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('route_created', route.to_dict(), data['company_id'])
        
        return jsonify(route.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_geolocation_bp.route('/routes/<int:route_id>/optimize', methods=['POST'])
@jwt_required()
def optimize_route(route_id):
    """Optimize route"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        route = Route.query.filter(
            Route.id == route_id,
            Route.user_id == user_id,
            Route.company_id == data.get('company_id')
        ).first()
        
        if not route:
            return jsonify({'error': 'Route not found'}), 404
        
        # Create optimization
        optimization = RouteOptimization(
            optimization_type=RouteOptimizationType(data.get('optimization_type', 'SHORTEST_DISTANCE')),
            route_id=route_id,
            optimized_waypoints=data.get('optimized_waypoints'),
            optimized_distance=data.get('optimized_distance', 0.0),
            optimized_duration=data.get('optimized_duration', 0.0),
            optimization_savings=data.get('optimization_savings', 0.0),
            optimization_confidence=data.get('optimization_confidence', 0.0),
            alternative_routes=data.get('alternative_routes'),
            traffic_conditions=data.get('traffic_conditions'),
            company_id=data['company_id']
        )
        
        db.session.add(optimization)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('route_optimized', optimization.to_dict(), data['company_id'])
        
        return jsonify(optimization.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Location-Based Notifications
@advanced_geolocation_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_location_notifications():
    """Get location-based notifications"""
    try:
        company_id = request.args.get('company_id', type=int)
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = LocationBasedNotification.query.filter(LocationBasedNotification.company_id == company_id)
        
        if is_active is not None:
            query = query.filter(LocationBasedNotification.is_active == is_active)
        
        notifications = query.all()
        
        return jsonify([notification.to_dict() for notification in notifications])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_geolocation_bp.route('/notifications', methods=['POST'])
@jwt_required()
def create_location_notification():
    """Create location-based notification"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['notification_title', 'notification_message', 'trigger_latitude', 'trigger_longitude', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create notification
        notification = LocationBasedNotification(
            notification_title=data['notification_title'],
            notification_message=data['notification_message'],
            notification_type=data.get('notification_type', 'Info'),
            trigger_latitude=data['trigger_latitude'],
            trigger_longitude=data['trigger_longitude'],
            trigger_radius=data.get('trigger_radius', 100.0),
            trigger_conditions=data.get('trigger_conditions'),
            is_active=data.get('is_active', True),
            send_immediately=data.get('send_immediately', True),
            delay_seconds=data.get('delay_seconds', 0),
            repeat_notification=data.get('repeat_notification', False),
            repeat_interval=data.get('repeat_interval', 0),
            target_users=data.get('target_users'),
            target_roles=data.get('target_roles'),
            target_geofences=data.get('target_geofences'),
            delivery_methods=data.get('delivery_methods'),
            priority_level=data.get('priority_level', 'Normal'),
            company_id=data['company_id']
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('location_notification_created', notification.to_dict(), data['company_id'])
        
        return jsonify(notification.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Location History
@advanced_geolocation_bp.route('/location-history', methods=['GET'])
@jwt_required()
def get_location_history():
    """Get location history"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        movement_type = request.args.get('movement_type')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = LocationHistory.query.filter(
            LocationHistory.user_id == user_id,
            LocationHistory.company_id == company_id
        )
        
        if start_date:
            query = query.filter(LocationHistory.timestamp >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(LocationHistory.timestamp <= datetime.fromisoformat(end_date))
        
        if movement_type:
            query = query.filter(LocationHistory.movement_type == movement_type)
        
        history = query.order_by(LocationHistory.timestamp.desc()).limit(100).all()
        
        return jsonify([record.to_dict() for record in history])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_geolocation_bp.route('/location-history', methods=['POST'])
@jwt_required()
def add_location_history():
    """Add location to history"""
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
        
        # Create location history record
        history = LocationHistory(
            latitude=data['latitude'],
            longitude=data['longitude'],
            accuracy=data.get('accuracy', 0.0),
            altitude=data.get('altitude', 0.0),
            speed=data.get('speed', 0.0),
            heading=data.get('heading', 0.0),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            country=data.get('country'),
            postal_code=data.get('postal_code'),
            timezone=data.get('timezone'),
            duration=data.get('duration', 0.0),
            movement_type=data.get('movement_type', 'Stationary'),
            user_id=user_id,
            device_info=data.get('device_info'),
            app_version=data.get('app_version'),
            battery_level=data.get('battery_level', 0.0),
            geofence_id=data.get('geofence_id'),
            company_id=data['company_id']
        )
        
        db.session.add(history)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('location_history_added', history.to_dict(), data['company_id'])
        
        return jsonify(history.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Travel Time Calculation
@advanced_geolocation_bp.route('/travel-time', methods=['POST'])
@jwt_required()
def calculate_travel_time():
    """Calculate travel time between locations"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['start_latitude', 'start_longitude', 'end_latitude', 'end_longitude', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create travel time calculation
        calculation = TravelTimeCalculation(
            start_latitude=data['start_latitude'],
            start_longitude=data['start_longitude'],
            end_latitude=data['end_latitude'],
            end_longitude=data['end_longitude'],
            calculated_time=data.get('calculated_time', 0.0),
            distance=data.get('distance', 0.0),
            traffic_conditions=data.get('traffic_conditions', 'Normal'),
            weather_conditions=data.get('weather_conditions', 'Clear'),
            calculation_method=data.get('calculation_method', 'API'),
            confidence_score=data.get('confidence_score', 0.0),
            user_id=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(calculation)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('travel_time_calculated', calculation.to_dict(), data['company_id'])
        
        return jsonify(calculation.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_geolocation_bp.route('/travel-time', methods=['GET'])
@jwt_required()
def get_travel_time_calculations():
    """Get travel time calculations"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = TravelTimeCalculation.query.filter(
            TravelTimeCalculation.user_id == user_id,
            TravelTimeCalculation.company_id == company_id
        )
        
        if start_date:
            query = query.filter(TravelTimeCalculation.last_updated >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(TravelTimeCalculation.last_updated <= datetime.fromisoformat(end_date))
        
        calculations = query.order_by(TravelTimeCalculation.last_updated.desc()).limit(50).all()
        
        return jsonify([calculation.to_dict() for calculation in calculations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
