# Geolocation Tracking API
# API endpoints for geolocation tracking across all activities

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from core.geolocation_tracking import (
    GeolocationRecord, GeoRestriction, LocationHistory,
    ActivityType, TrackingType, create_geolocation_record,
    validate_geolocation, get_user_location_history,
    get_activity_geolocation
)
from datetime import datetime, timedelta
import json

geolocation_bp = Blueprint('geolocation', __name__)

# Geolocation Tracking
@geolocation_bp.route('/track', methods=['POST'])
@jwt_required()
def track_location():
    """Track user location for an activity"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['activity_type', 'activity_id', 'latitude', 'longitude', 'tracking_type', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create geolocation record
        record, message = create_geolocation_record(
            user_id=user_id,
            activity_type=ActivityType(data['activity_type']),
            activity_id=data['activity_id'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            tracking_type=TrackingType(data['tracking_type']),
            company_id=data['company_id'],
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
            activity_entity_type=data.get('activity_entity_type'),
            activity_entity_id=data.get('activity_entity_id'),
            device_info=data.get('device_info'),
            app_version=data.get('app_version')
        )
        
        if not record:
            return jsonify({'error': message}), 400
        
        # Emit real-time update
        emit_realtime_update('location_tracked', record.to_dict(), data['company_id'])
        
        return jsonify(record.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@geolocation_bp.route('/validate', methods=['POST'])
@jwt_required()
def validate_location():
    """Validate location against restrictions"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['activity_type', 'latitude', 'longitude', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate geolocation
        is_valid, message = validate_geolocation(
            user_id=user_id,
            activity_type=ActivityType(data['activity_type']),
            latitude=data['latitude'],
            longitude=data['longitude'],
            company_id=data['company_id']
        )
        
        return jsonify({
            'is_valid': is_valid,
            'message': message
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@geolocation_bp.route('/history', methods=['GET'])
@jwt_required()
def get_location_history():
    """Get user location history"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        # Parse dates
        start_date = datetime.fromisoformat(start_date) if start_date else None
        end_date = datetime.fromisoformat(end_date) if end_date else None
        
        # Get location history
        history = get_user_location_history(
            user_id=user_id,
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return jsonify([record.to_dict() for record in history])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@geolocation_bp.route('/activity/<activity_type>/<activity_id>', methods=['GET'])
@jwt_required()
def get_activity_geolocation_records(activity_type, activity_id):
    """Get geolocation records for a specific activity"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        # Get activity geolocation records
        records = get_activity_geolocation(
            activity_type=ActivityType(activity_type),
            activity_id=activity_id,
            company_id=company_id
        )
        
        return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Geo Restrictions
@geolocation_bp.route('/restrictions', methods=['GET'])
@jwt_required()
def get_geo_restrictions():
    """Get geo restrictions"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        restrictions = GeoRestriction.query.filter(
            GeoRestriction.company_id == company_id,
            GeoRestriction.is_active == True
        ).all()
        
        return jsonify([restriction.to_dict() for restriction in restrictions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@geolocation_bp.route('/restrictions', methods=['POST'])
@jwt_required()
def create_geo_restriction():
    """Create a geo restriction"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['restriction_name', 'center_latitude', 'center_longitude', 'radius', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create restriction
        restriction = GeoRestriction(
            restriction_name=data['restriction_name'],
            restriction_description=data.get('restriction_description'),
            center_latitude=data['center_latitude'],
            center_longitude=data['center_longitude'],
            radius=data['radius'],
            polygon_coordinates=data.get('polygon_coordinates'),
            allowed_activity_types=data.get('allowed_activity_types'),
            restricted_activity_types=data.get('restricted_activity_types'),
            start_time=datetime.strptime(data['start_time'], '%H:%M').time() if data.get('start_time') else None,
            end_time=datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else None,
            allowed_days=data.get('allowed_days'),
            allowed_users=data.get('allowed_users'),
            restricted_users=data.get('restricted_users'),
            allowed_roles=data.get('allowed_roles'),
            restricted_roles=data.get('restricted_roles'),
            company_id=data['company_id']
        )
        
        db.session.add(restriction)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('geo_restriction_created', restriction.to_dict(), data['company_id'])
        
        return jsonify(restriction.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@geolocation_bp.route('/restrictions/<int:restriction_id>', methods=['GET'])
@jwt_required()
def get_geo_restriction(restriction_id):
    """Get a specific geo restriction"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        restriction = GeoRestriction.query.filter(
            GeoRestriction.id == restriction_id,
            GeoRestriction.company_id == company_id
        ).first()
        
        if not restriction:
            return jsonify({'error': 'Restriction not found'}), 404
        
        return jsonify(restriction.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@geolocation_bp.route('/restrictions/<int:restriction_id>', methods=['PUT'])
@jwt_required()
def update_geo_restriction(restriction_id):
    """Update a geo restriction"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        restriction = GeoRestriction.query.filter(
            GeoRestriction.id == restriction_id,
            GeoRestriction.company_id == data.get('company_id')
        ).first()
        
        if not restriction:
            return jsonify({'error': 'Restriction not found'}), 404
        
        # Update fields
        for field in ['restriction_name', 'restriction_description', 'is_active', 'center_latitude', 
                     'center_longitude', 'radius', 'polygon_coordinates', 'allowed_activity_types',
                     'restricted_activity_types', 'allowed_days', 'allowed_users', 'restricted_users',
                     'allowed_roles', 'restricted_roles']:
            if field in data:
                setattr(restriction, field, data[field])
        
        if 'start_time' in data and data['start_time']:
            restriction.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        
        if 'end_time' in data and data['end_time']:
            restriction.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('geo_restriction_updated', restriction.to_dict(), restriction.company_id)
        
        return jsonify(restriction.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@geolocation_bp.route('/restrictions/<int:restriction_id>', methods=['DELETE'])
@jwt_required()
def delete_geo_restriction(restriction_id):
    """Delete a geo restriction"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        restriction = GeoRestriction.query.filter(
            GeoRestriction.id == restriction_id,
            GeoRestriction.company_id == company_id
        ).first()
        
        if not restriction:
            return jsonify({'error': 'Restriction not found'}), 404
        
        # Soft delete
        restriction.is_active = False
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('geo_restriction_deleted', {'id': restriction_id}, company_id)
        
        return jsonify({'message': 'Restriction deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Location History
@geolocation_bp.route('/history', methods=['POST'])
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
            user_id=user_id,
            device_info=data.get('device_info'),
            app_version=data.get('app_version'),
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

# Analytics
@geolocation_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_geolocation_analytics():
    """Get geolocation analytics"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        # Parse dates
        start_date = datetime.fromisoformat(start_date) if start_date else None
        end_date = datetime.fromisoformat(end_date) if end_date else None
        
        # Get analytics data
        query = GeolocationRecord.query.filter(
            GeolocationRecord.company_id == company_id
        )
        
        if start_date:
            query = query.filter(GeolocationRecord.timestamp >= start_date)
        
        if end_date:
            query = query.filter(GeolocationRecord.timestamp <= end_date)
        
        records = query.all()
        
        # Calculate analytics
        total_records = len(records)
        unique_locations = len(set((r.latitude, r.longitude) for r in records))
        activity_types = {}
        tracking_types = {}
        
        for record in records:
            # Count by activity type
            activity_type = record.activity_type.value
            activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
            
            # Count by tracking type
            tracking_type = record.tracking_type.value
            tracking_types[tracking_type] = tracking_types.get(tracking_type, 0) + 1
        
        analytics = {
            'total_records': total_records,
            'unique_locations': unique_locations,
            'activity_types': activity_types,
            'tracking_types': tracking_types,
            'date_range': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }
        }
        
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
