# AI Smart Scheduling API
# API endpoints for AI-powered intelligent scheduling and meeting optimization

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from .models import (
    MeetingSuggestion, SchedulingConflict, ResourceOptimization,
    PredictiveAnalytics, UserSchedulingProfile,
    MeetingType, PriorityLevel, ConflictResolution, SchedulingPreference
)
from datetime import datetime, timedelta
import json

ai_smart_scheduling_bp = Blueprint('ai_smart_scheduling', __name__)

# Meeting Suggestions
@ai_smart_scheduling_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def get_meeting_suggestions():
    """Get AI-powered meeting suggestions"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        meeting_type = request.args.get('meeting_type')
        priority = request.args.get('priority')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = MeetingSuggestion.query.filter(
            MeetingSuggestion.organizer_id == user_id,
            MeetingSuggestion.company_id == company_id
        )
        
        if meeting_type:
            query = query.filter(MeetingSuggestion.meeting_type == MeetingType(meeting_type))
        
        if priority:
            query = query.filter(MeetingSuggestion.priority_level == PriorityLevel(priority))
        
        suggestions = query.order_by(MeetingSuggestion.confidence_score.desc()).all()
        
        return jsonify([suggestion.to_dict() for suggestion in suggestions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_smart_scheduling_bp.route('/suggestions', methods=['POST'])
@jwt_required()
def create_meeting_suggestion():
    """Create AI-powered meeting suggestion"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['meeting_title', 'meeting_type', 'suggested_start_time', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create suggestion
        suggestion = MeetingSuggestion(
            meeting_title=data['meeting_title'],
            meeting_description=data.get('meeting_description'),
            meeting_type=MeetingType(data['meeting_type']),
            priority_level=PriorityLevel(data.get('priority_level', 'MEDIUM')),
            suggested_start_time=datetime.fromisoformat(data['suggested_start_time']),
            suggested_end_time=datetime.fromisoformat(data['suggested_end_time']) if data.get('suggested_end_time') else None,
            suggested_duration=data.get('suggested_duration', 1.0),
            confidence_score=data.get('confidence_score', 0.0),
            ai_reasoning=data.get('ai_reasoning'),
            alternative_times=data.get('alternative_times'),
            organizer_id=user_id,
            suggested_attendees=data.get('suggested_attendees', []),
            suggested_location=data.get('suggested_location'),
            location_coordinates=data.get('location_coordinates'),
            is_virtual=data.get('is_virtual', False),
            company_id=data['company_id']
        )
        
        # Calculate end time if not provided
        if not suggestion.suggested_end_time and suggestion.suggested_start_time:
            suggestion.suggested_end_time = suggestion.suggested_start_time + timedelta(hours=suggestion.suggested_duration)
        
        db.session.add(suggestion)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('meeting_suggestion_created', suggestion.to_dict(), data['company_id'])
        
        return jsonify(suggestion.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_smart_scheduling_bp.route('/suggestions/<int:suggestion_id>', methods=['GET'])
@jwt_required()
def get_meeting_suggestion(suggestion_id):
    """Get specific meeting suggestion"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        suggestion = MeetingSuggestion.query.filter(
            MeetingSuggestion.id == suggestion_id,
            MeetingSuggestion.organizer_id == user_id,
            MeetingSuggestion.company_id == company_id
        ).first()
        
        if not suggestion:
            return jsonify({'error': 'Suggestion not found'}), 404
        
        return jsonify(suggestion.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_smart_scheduling_bp.route('/suggestions/<int:suggestion_id>/accept', methods=['POST'])
@jwt_required()
def accept_meeting_suggestion(suggestion_id):
    """Accept meeting suggestion"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        suggestion = MeetingSuggestion.query.filter(
            MeetingSuggestion.id == suggestion_id,
            MeetingSuggestion.organizer_id == user_id,
            MeetingSuggestion.company_id == data.get('company_id')
        ).first()
        
        if not suggestion:
            return jsonify({'error': 'Suggestion not found'}), 404
        
        # Create actual meeting from suggestion
        # This would integrate with the calendar system
        meeting_data = {
            'event_title': suggestion.meeting_title,
            'event_description': suggestion.meeting_description,
            'start_datetime': suggestion.suggested_start_time.isoformat(),
            'end_datetime': suggestion.suggested_end_time.isoformat(),
            'attendees': suggestion.suggested_attendees,
            'location': suggestion.suggested_location,
            'location_coordinates': suggestion.location_coordinates,
            'is_virtual': suggestion.is_virtual,
            'company_id': suggestion.company_id
        }
        
        # Emit real-time update
        emit_realtime_update('meeting_suggestion_accepted', {
            'suggestion_id': suggestion_id,
            'meeting_data': meeting_data
        }, suggestion.company_id)
        
        return jsonify({'message': 'Suggestion accepted', 'meeting_data': meeting_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Scheduling Conflicts
@ai_smart_scheduling_bp.route('/conflicts', methods=['GET'])
@jwt_required()
def get_scheduling_conflicts():
    """Get scheduling conflicts"""
    try:
        company_id = request.args.get('company_id', type=int)
        conflict_type = request.args.get('conflict_type')
        resolution_status = request.args.get('resolution_status')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = SchedulingConflict.query.filter(SchedulingConflict.company_id == company_id)
        
        if conflict_type:
            query = query.filter(SchedulingConflict.conflict_type == conflict_type)
        
        if resolution_status:
            query = query.filter(SchedulingConflict.resolution_status == resolution_status)
        
        conflicts = query.order_by(SchedulingConflict.conflict_start_time.desc()).all()
        
        return jsonify([conflict.to_dict() for conflict in conflicts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_smart_scheduling_bp.route('/conflicts', methods=['POST'])
@jwt_required()
def create_scheduling_conflict():
    """Create scheduling conflict"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['conflict_type', 'primary_event_id', 'conflicting_event_id', 'conflict_start_time', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create conflict
        conflict = SchedulingConflict(
            conflict_type=data['conflict_type'],
            conflict_description=data.get('conflict_description'),
            conflict_severity=PriorityLevel(data.get('conflict_severity', 'MEDIUM')),
            primary_event_id=data['primary_event_id'],
            conflicting_event_id=data['conflicting_event_id'],
            conflict_start_time=datetime.fromisoformat(data['conflict_start_time']),
            conflict_end_time=datetime.fromisoformat(data['conflict_end_time']) if data.get('conflict_end_time') else None,
            ai_suggested_resolution=data.get('ai_suggested_resolution'),
            resolution_confidence=data.get('resolution_confidence', 0.0),
            company_id=data['company_id']
        )
        
        # Calculate end time if not provided
        if not conflict.conflict_end_time and conflict.conflict_start_time:
            conflict.conflict_end_time = conflict.conflict_start_time + timedelta(hours=1)
        
        db.session.add(conflict)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('scheduling_conflict_created', conflict.to_dict(), data['company_id'])
        
        return jsonify(conflict.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_smart_scheduling_bp.route('/conflicts/<int:conflict_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_scheduling_conflict(conflict_id):
    """Resolve scheduling conflict"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        conflict = SchedulingConflict.query.filter(
            SchedulingConflict.id == conflict_id,
            SchedulingConflict.company_id == data.get('company_id')
        ).first()
        
        if not conflict:
            return jsonify({'error': 'Conflict not found'}), 404
        
        # Update conflict resolution
        conflict.resolution_status = 'Resolved'
        conflict.resolution_method = ConflictResolution(data.get('resolution_method', 'MANUAL_REVIEW'))
        conflict.resolution_notes = data.get('resolution_notes')
        conflict.resolved_by = user_id
        conflict.resolved_at = datetime.utcnow()
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('scheduling_conflict_resolved', conflict.to_dict(), conflict.company_id)
        
        return jsonify(conflict.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Resource Optimization
@ai_smart_scheduling_bp.route('/resources', methods=['GET'])
@jwt_required()
def get_resource_optimizations():
    """Get resource optimizations"""
    try:
        company_id = request.args.get('company_id', type=int)
        resource_type = request.args.get('resource_type')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = ResourceOptimization.query.filter(ResourceOptimization.company_id == company_id)
        
        if resource_type:
            query = query.filter(ResourceOptimization.resource_type == resource_type)
        
        resources = query.order_by(ResourceOptimization.efficiency_score.desc()).all()
        
        return jsonify([resource.to_dict() for resource in resources])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_smart_scheduling_bp.route('/resources', methods=['POST'])
@jwt_required()
def create_resource_optimization():
    """Create resource optimization"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['resource_type', 'resource_id', 'resource_name', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create resource optimization
        resource = ResourceOptimization(
            resource_type=data['resource_type'],
            resource_id=data['resource_id'],
            resource_name=data['resource_name'],
            utilization_rate=data.get('utilization_rate', 0.0),
            efficiency_score=data.get('efficiency_score', 0.0),
            cost_per_hour=data.get('cost_per_hour', 0.0),
            optimal_start_time=datetime.fromisoformat(data['optimal_start_time']) if data.get('optimal_start_time') else None,
            optimal_end_time=datetime.fromisoformat(data['optimal_end_time']) if data.get('optimal_end_time') else None,
            availability_windows=data.get('availability_windows'),
            optimization_recommendations=data.get('optimization_recommendations'),
            predicted_demand=data.get('predicted_demand', 0.0),
            maintenance_schedule=data.get('maintenance_schedule'),
            company_id=data['company_id']
        )
        
        db.session.add(resource)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('resource_optimization_created', resource.to_dict(), data['company_id'])
        
        return jsonify(resource.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Predictive Analytics
@ai_smart_scheduling_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_predictive_analytics():
    """Get predictive analytics"""
    try:
        company_id = request.args.get('company_id', type=int)
        analytics_type = request.args.get('analytics_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = PredictiveAnalytics.query.filter(PredictiveAnalytics.company_id == company_id)
        
        if analytics_type:
            query = query.filter(PredictiveAnalytics.analytics_type == analytics_type)
        
        if start_date:
            query = query.filter(PredictiveAnalytics.prediction_date >= date.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(PredictiveAnalytics.prediction_date <= date.fromisoformat(end_date))
        
        analytics = query.order_by(PredictiveAnalytics.prediction_date.desc()).all()
        
        return jsonify([analytic.to_dict() for analytic in analytics])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_smart_scheduling_bp.route('/analytics', methods=['POST'])
@jwt_required()
def create_predictive_analytics():
    """Create predictive analytics"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['analytics_type', 'prediction_date', 'predicted_value', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create analytics
        analytics = PredictiveAnalytics(
            analytics_type=data['analytics_type'],
            prediction_date=date.fromisoformat(data['prediction_date']),
            prediction_horizon=data.get('prediction_horizon', 30),
            predicted_value=data['predicted_value'],
            confidence_interval_lower=data.get('confidence_interval_lower', 0.0),
            confidence_interval_upper=data.get('confidence_interval_upper', 0.0),
            accuracy_score=data.get('accuracy_score', 0.0),
            model_version=data.get('model_version', '1.0'),
            training_data_size=data.get('training_data_size', 0),
            last_training_date=datetime.fromisoformat(data['last_training_date']) if data.get('last_training_date') else None,
            context_data=data.get('context_data'),
            influencing_factors=data.get('influencing_factors'),
            company_id=data['company_id']
        )
        
        db.session.add(analytics)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('predictive_analytics_created', analytics.to_dict(), data['company_id'])
        
        return jsonify(analytics.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Scheduling Profiles
@ai_smart_scheduling_bp.route('/profiles', methods=['GET'])
@jwt_required()
def get_user_scheduling_profiles():
    """Get user scheduling profiles"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        profiles = UserSchedulingProfile.query.filter(
            UserSchedulingProfile.user_id == user_id,
            UserSchedulingProfile.company_id == company_id
        ).all()
        
        return jsonify([profile.to_dict() for profile in profiles])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_smart_scheduling_bp.route('/profiles', methods=['POST'])
@jwt_required()
def create_user_scheduling_profile():
    """Create user scheduling profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create profile
        profile = UserSchedulingProfile(
            user_id=user_id,
            preferred_meeting_times=data.get('preferred_meeting_times'),
            preferred_meeting_duration=data.get('preferred_meeting_duration', 1.0),
            preferred_meeting_type=MeetingType(data.get('preferred_meeting_type', 'TEAM_MEETING')),
            scheduling_preference=SchedulingPreference(data.get('scheduling_preference', 'FLEXIBLE')),
            most_productive_hours=data.get('most_productive_hours'),
            least_productive_hours=data.get('least_productive_hours'),
            typical_meeting_duration=data.get('typical_meeting_duration', 1.0),
            meeting_frequency=data.get('meeting_frequency', 0.0),
            ai_learning_enabled=data.get('ai_learning_enabled', True),
            company_id=data['company_id']
        )
        
        db.session.add(profile)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('user_scheduling_profile_created', profile.to_dict(), data['company_id'])
        
        return jsonify(profile.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_smart_scheduling_bp.route('/profiles/<int:profile_id>', methods=['PUT'])
@jwt_required()
def update_user_scheduling_profile(profile_id):
    """Update user scheduling profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        profile = UserSchedulingProfile.query.filter(
            UserSchedulingProfile.id == profile_id,
            UserSchedulingProfile.user_id == user_id,
            UserSchedulingProfile.company_id == data.get('company_id')
        ).first()
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Update fields
        for field in ['preferred_meeting_times', 'preferred_meeting_duration', 'most_productive_hours',
                     'least_productive_hours', 'typical_meeting_duration', 'meeting_frequency',
                     'ai_learning_enabled']:
            if field in data:
                setattr(profile, field, data[field])
        
        if 'preferred_meeting_type' in data:
            profile.preferred_meeting_type = MeetingType(data['preferred_meeting_type'])
        
        if 'scheduling_preference' in data:
            profile.scheduling_preference = SchedulingPreference(data['scheduling_preference'])
        
        profile.last_learning_update = datetime.utcnow()
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('user_scheduling_profile_updated', profile.to_dict(), profile.company_id)
        
        return jsonify(profile.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
