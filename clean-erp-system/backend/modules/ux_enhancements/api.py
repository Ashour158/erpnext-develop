# UX Enhancements API
# API endpoints for personalization and accessibility features

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from .models import (
    UserPreference, UserTheme, UserLayout, UserDashboard, AccessibilitySetting,
    UserNotification, UserShortcut, UserWorkspace, UserActivity, UserRecommendation,
    UserFeedback, UserTutorial, UserHelp, UserSession
)
from datetime import datetime, timedelta
import json

ux_enhancements_bp = Blueprint('ux_enhancements', __name__)

# User Preferences
@ux_enhancements_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_user_preferences():
    """Get user preferences"""
    try:
        user_id = get_jwt_identity()
        preference_key = request.args.get('preference_key')
        preference_type = request.args.get('preference_type')
        
        query = UserPreference.query.filter(UserPreference.user_id == user_id)
        
        if preference_key:
            query = query.filter(UserPreference.preference_key == preference_key)
        
        if preference_type:
            query = query.filter(UserPreference.preference_type == preference_type)
        
        preferences = query.order_by(UserPreference.preference_key).all()
        
        return jsonify([pref.to_dict() for pref in preferences])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/preferences', methods=['POST'])
@jwt_required()
def create_user_preference():
    """Create or update user preference"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['preference_key', 'preference_value']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if preference already exists
        existing_pref = UserPreference.query.filter(
            UserPreference.user_id == user_id,
            UserPreference.preference_key == data['preference_key']
        ).first()
        
        if existing_pref:
            # Update existing preference
            existing_pref.preference_value = data['preference_value']
            existing_pref.preference_type = data.get('preference_type', existing_pref.preference_type)
            existing_pref.updated_at = datetime.utcnow()
            db.session.commit()
            
            emit_realtime_update('user_preference_updated', existing_pref.to_dict(), user_id)
            return jsonify(existing_pref.to_dict())
        else:
            # Create new preference
            preference = UserPreference(
                user_id=user_id,
                preference_key=data['preference_key'],
                preference_value=data['preference_value'],
                preference_type=data.get('preference_type', 'string')
            )
            
            db.session.add(preference)
            db.session.commit()
            
            emit_realtime_update('user_preference_created', preference.to_dict(), user_id)
            return jsonify(preference.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Themes
@ux_enhancements_bp.route('/themes', methods=['GET'])
@jwt_required()
def get_user_themes():
    """Get user themes"""
    try:
        user_id = get_jwt_identity()
        theme_name = request.args.get('theme_name')
        theme_type = request.args.get('theme_type')
        is_active = request.args.get('is_active', type=bool)
        
        query = UserTheme.query.filter(UserTheme.user_id == user_id)
        
        if theme_name:
            query = query.filter(UserTheme.theme_name == theme_name)
        
        if theme_type:
            query = query.filter(UserTheme.theme_type == theme_type)
        
        if is_active is not None:
            query = query.filter(UserTheme.is_active == is_active)
        
        themes = query.order_by(UserTheme.created_at.desc()).all()
        
        return jsonify([theme.to_dict() for theme in themes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/themes', methods=['POST'])
@jwt_required()
def create_user_theme():
    """Create user theme"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['theme_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create theme
        theme = UserTheme(
            user_id=user_id,
            theme_name=data['theme_name'],
            theme_type=data.get('theme_type', 'light'),
            primary_color=data.get('primary_color'),
            secondary_color=data.get('secondary_color'),
            accent_color=data.get('accent_color'),
            background_color=data.get('background_color'),
            text_color=data.get('text_color'),
            font_family=data.get('font_family'),
            font_size=data.get('font_size', 'medium')
        )
        
        db.session.add(theme)
        db.session.commit()
        
        emit_realtime_update('user_theme_created', theme.to_dict(), user_id)
        return jsonify(theme.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/themes/<int:theme_id>/activate', methods=['POST'])
@jwt_required()
def activate_user_theme(theme_id):
    """Activate user theme"""
    try:
        user_id = get_jwt_identity()
        
        # Deactivate all other themes for this user
        UserTheme.query.filter(
            UserTheme.user_id == user_id,
            UserTheme.id != theme_id
        ).update({'is_active': False})
        
        # Activate the selected theme
        theme = UserTheme.query.filter(
            UserTheme.id == theme_id,
            UserTheme.user_id == user_id
        ).first()
        
        if not theme:
            return jsonify({'error': 'Theme not found'}), 404
        
        theme.is_active = True
        theme.updated_at = datetime.utcnow()
        db.session.commit()
        
        emit_realtime_update('user_theme_activated', theme.to_dict(), user_id)
        return jsonify(theme.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Layouts
@ux_enhancements_bp.route('/layouts', methods=['GET'])
@jwt_required()
def get_user_layouts():
    """Get user layouts"""
    try:
        user_id = get_jwt_identity()
        layout_name = request.args.get('layout_name')
        layout_type = request.args.get('layout_type')
        is_active = request.args.get('is_active', type=bool)
        
        query = UserLayout.query.filter(UserLayout.user_id == user_id)
        
        if layout_name:
            query = query.filter(UserLayout.layout_name == layout_name)
        
        if layout_type:
            query = query.filter(UserLayout.layout_type == layout_type)
        
        if is_active is not None:
            query = query.filter(UserLayout.is_active == is_active)
        
        layouts = query.order_by(UserLayout.created_at.desc()).all()
        
        return jsonify([layout.to_dict() for layout in layouts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/layouts', methods=['POST'])
@jwt_required()
def create_user_layout():
    """Create user layout"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['layout_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create layout
        layout = UserLayout(
            user_id=user_id,
            layout_name=data['layout_name'],
            layout_type=data.get('layout_type', 'default'),
            sidebar_position=data.get('sidebar_position', 'left'),
            sidebar_width=data.get('sidebar_width', 250),
            header_height=data.get('header_height', 60),
            footer_visible=data.get('footer_visible', True),
            grid_columns=data.get('grid_columns', 12),
            card_size=data.get('card_size', 'medium')
        )
        
        db.session.add(layout)
        db.session.commit()
        
        emit_realtime_update('user_layout_created', layout.to_dict(), user_id)
        return jsonify(layout.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Dashboards
@ux_enhancements_bp.route('/dashboards', methods=['GET'])
@jwt_required()
def get_user_dashboards():
    """Get user dashboards"""
    try:
        user_id = get_jwt_identity()
        dashboard_name = request.args.get('dashboard_name')
        dashboard_type = request.args.get('dashboard_type')
        is_default = request.args.get('is_default', type=bool)
        is_public = request.args.get('is_public', type=bool)
        
        query = UserDashboard.query.filter(UserDashboard.user_id == user_id)
        
        if dashboard_name:
            query = query.filter(UserDashboard.dashboard_name == dashboard_name)
        
        if dashboard_type:
            query = query.filter(UserDashboard.dashboard_type == dashboard_type)
        
        if is_default is not None:
            query = query.filter(UserDashboard.is_default == is_default)
        
        if is_public is not None:
            query = query.filter(UserDashboard.is_public == is_public)
        
        dashboards = query.order_by(UserDashboard.created_at.desc()).all()
        
        return jsonify([dashboard.to_dict() for dashboard in dashboards])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/dashboards', methods=['POST'])
@jwt_required()
def create_user_dashboard():
    """Create user dashboard"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['dashboard_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create dashboard
        dashboard = UserDashboard(
            user_id=user_id,
            dashboard_name=data['dashboard_name'],
            dashboard_type=data.get('dashboard_type', 'personal'),
            widgets=data.get('widgets', []),
            layout_config=data.get('layout_config', {}),
            is_default=data.get('is_default', False),
            is_public=data.get('is_public', False)
        )
        
        db.session.add(dashboard)
        db.session.commit()
        
        emit_realtime_update('user_dashboard_created', dashboard.to_dict(), user_id)
        return jsonify(dashboard.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Accessibility Settings
@ux_enhancements_bp.route('/accessibility', methods=['GET'])
@jwt_required()
def get_accessibility_settings():
    """Get accessibility settings"""
    try:
        user_id = get_jwt_identity()
        setting_name = request.args.get('setting_name')
        category = request.args.get('category')
        is_active = request.args.get('is_active', type=bool)
        
        query = AccessibilitySetting.query.filter(AccessibilitySetting.user_id == user_id)
        
        if setting_name:
            query = query.filter(AccessibilitySetting.setting_name == setting_name)
        
        if category:
            query = query.filter(AccessibilitySetting.category == category)
        
        if is_active is not None:
            query = query.filter(AccessibilitySetting.is_active == is_active)
        
        settings = query.order_by(AccessibilitySetting.setting_name).all()
        
        return jsonify([setting.to_dict() for setting in settings])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/accessibility', methods=['POST'])
@jwt_required()
def create_accessibility_setting():
    """Create accessibility setting"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['setting_name', 'setting_value']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if setting already exists
        existing_setting = AccessibilitySetting.query.filter(
            AccessibilitySetting.user_id == user_id,
            AccessibilitySetting.setting_name == data['setting_name']
        ).first()
        
        if existing_setting:
            # Update existing setting
            existing_setting.setting_value = data['setting_value']
            existing_setting.setting_type = data.get('setting_type', existing_setting.setting_type)
            existing_setting.category = data.get('category', existing_setting.category)
            existing_setting.updated_at = datetime.utcnow()
            db.session.commit()
            
            emit_realtime_update('accessibility_setting_updated', existing_setting.to_dict(), user_id)
            return jsonify(existing_setting.to_dict())
        else:
            # Create new setting
            setting = AccessibilitySetting(
                user_id=user_id,
                setting_name=data['setting_name'],
                setting_value=data['setting_value'],
                setting_type=data.get('setting_type', 'boolean'),
                category=data.get('category', 'general')
            )
            
            db.session.add(setting)
            db.session.commit()
            
            emit_realtime_update('accessibility_setting_created', setting.to_dict(), user_id)
            return jsonify(setting.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Notifications
@ux_enhancements_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_user_notifications():
    """Get user notification preferences"""
    try:
        user_id = get_jwt_identity()
        notification_type = request.args.get('notification_type')
        notification_channel = request.args.get('notification_channel')
        is_enabled = request.args.get('is_enabled', type=bool)
        
        query = UserNotification.query.filter(UserNotification.user_id == user_id)
        
        if notification_type:
            query = query.filter(UserNotification.notification_type == notification_type)
        
        if notification_channel:
            query = query.filter(UserNotification.notification_channel == notification_channel)
        
        if is_enabled is not None:
            query = query.filter(UserNotification.is_enabled == is_enabled)
        
        notifications = query.order_by(UserNotification.notification_type).all()
        
        return jsonify([notification.to_dict() for notification in notifications])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/notifications', methods=['POST'])
@jwt_required()
def create_user_notification():
    """Create user notification preference"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['notification_type', 'notification_channel']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if notification preference already exists
        existing_notification = UserNotification.query.filter(
            UserNotification.user_id == user_id,
            UserNotification.notification_type == data['notification_type'],
            UserNotification.notification_channel == data['notification_channel']
        ).first()
        
        if existing_notification:
            # Update existing notification
            existing_notification.is_enabled = data.get('is_enabled', True)
            existing_notification.frequency = data.get('frequency', existing_notification.frequency)
            existing_notification.quiet_hours_start = data.get('quiet_hours_start', existing_notification.quiet_hours_start)
            existing_notification.quiet_hours_end = data.get('quiet_hours_end', existing_notification.quiet_hours_end)
            existing_notification.timezone = data.get('timezone', existing_notification.timezone)
            existing_notification.updated_at = datetime.utcnow()
            db.session.commit()
            
            emit_realtime_update('user_notification_updated', existing_notification.to_dict(), user_id)
            return jsonify(existing_notification.to_dict())
        else:
            # Create new notification preference
            notification = UserNotification(
                user_id=user_id,
                notification_type=data['notification_type'],
                notification_channel=data['notification_channel'],
                is_enabled=data.get('is_enabled', True),
                frequency=data.get('frequency', 'immediate'),
                quiet_hours_start=data.get('quiet_hours_start'),
                quiet_hours_end=data.get('quiet_hours_end'),
                timezone=data.get('timezone', 'UTC')
            )
            
            db.session.add(notification)
            db.session.commit()
            
            emit_realtime_update('user_notification_created', notification.to_dict(), user_id)
            return jsonify(notification.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Shortcuts
@ux_enhancements_bp.route('/shortcuts', methods=['GET'])
@jwt_required()
def get_user_shortcuts():
    """Get user keyboard shortcuts"""
    try:
        user_id = get_jwt_identity()
        shortcut_name = request.args.get('shortcut_name')
        shortcut_category = request.args.get('shortcut_category')
        is_active = request.args.get('is_active', type=bool)
        
        query = UserShortcut.query.filter(UserShortcut.user_id == user_id)
        
        if shortcut_name:
            query = query.filter(UserShortcut.shortcut_name == shortcut_name)
        
        if shortcut_category:
            query = query.filter(UserShortcut.shortcut_category == shortcut_category)
        
        if is_active is not None:
            query = query.filter(UserShortcut.is_active == is_active)
        
        shortcuts = query.order_by(UserShortcut.shortcut_category, UserShortcut.shortcut_name).all()
        
        return jsonify([shortcut.to_dict() for shortcut in shortcuts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/shortcuts', methods=['POST'])
@jwt_required()
def create_user_shortcut():
    """Create user keyboard shortcut"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['shortcut_name', 'shortcut_key', 'shortcut_action']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create shortcut
        shortcut = UserShortcut(
            user_id=user_id,
            shortcut_name=data['shortcut_name'],
            shortcut_key=data['shortcut_key'],
            shortcut_action=data['shortcut_action'],
            shortcut_category=data.get('shortcut_category', 'general')
        )
        
        db.session.add(shortcut)
        db.session.commit()
        
        emit_realtime_update('user_shortcut_created', shortcut.to_dict(), user_id)
        return jsonify(shortcut.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Workspaces
@ux_enhancements_bp.route('/workspaces', methods=['GET'])
@jwt_required()
def get_user_workspaces():
    """Get user workspaces"""
    try:
        user_id = get_jwt_identity()
        workspace_name = request.args.get('workspace_name')
        workspace_type = request.args.get('workspace_type')
        is_default = request.args.get('is_default', type=bool)
        is_active = request.args.get('is_active', type=bool)
        
        query = UserWorkspace.query.filter(UserWorkspace.user_id == user_id)
        
        if workspace_name:
            query = query.filter(UserWorkspace.workspace_name == workspace_name)
        
        if workspace_type:
            query = query.filter(UserWorkspace.workspace_type == workspace_type)
        
        if is_default is not None:
            query = query.filter(UserWorkspace.is_default == is_default)
        
        if is_active is not None:
            query = query.filter(UserWorkspace.is_active == is_active)
        
        workspaces = query.order_by(UserWorkspace.created_at.desc()).all()
        
        return jsonify([workspace.to_dict() for workspace in workspaces])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/workspaces', methods=['POST'])
@jwt_required()
def create_user_workspace():
    """Create user workspace"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['workspace_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create workspace
        workspace = UserWorkspace(
            user_id=user_id,
            workspace_name=data['workspace_name'],
            workspace_type=data.get('workspace_type', 'personal'),
            modules=data.get('modules', []),
            module_order=data.get('module_order', []),
            module_config=data.get('module_config', {}),
            is_default=data.get('is_default', False)
        )
        
        db.session.add(workspace)
        db.session.commit()
        
        emit_realtime_update('user_workspace_created', workspace.to_dict(), user_id)
        return jsonify(workspace.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Activity Tracking
@ux_enhancements_bp.route('/activities', methods=['GET'])
@jwt_required()
def get_user_activities():
    """Get user activities"""
    try:
        user_id = get_jwt_identity()
        activity_type = request.args.get('activity_type')
        module_name = request.args.get('module_name')
        feature_name = request.args.get('feature_name')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = UserActivity.query.filter(UserActivity.user_id == user_id)
        
        if activity_type:
            query = query.filter(UserActivity.activity_type == activity_type)
        
        if module_name:
            query = query.filter(UserActivity.module_name == module_name)
        
        if feature_name:
            query = query.filter(UserActivity.feature_name == feature_name)
        
        if start_date:
            query = query.filter(UserActivity.activity_timestamp >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(UserActivity.activity_timestamp <= datetime.fromisoformat(end_date))
        
        activities = query.order_by(UserActivity.activity_timestamp.desc()).limit(1000).all()
        
        return jsonify([activity.to_dict() for activity in activities])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/activities', methods=['POST'])
@jwt_required()
def create_user_activity():
    """Create user activity"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['activity_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create activity
        activity = UserActivity(
            user_id=user_id,
            activity_type=data['activity_type'],
            activity_data=data.get('activity_data'),
            module_name=data.get('module_name'),
            feature_name=data.get('feature_name'),
            duration_seconds=data.get('duration_seconds', 0),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        db.session.add(activity)
        db.session.commit()
        
        emit_realtime_update('user_activity_created', activity.to_dict(), user_id)
        return jsonify(activity.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Recommendations
@ux_enhancements_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_user_recommendations():
    """Get user recommendations"""
    try:
        user_id = get_jwt_identity()
        recommendation_type = request.args.get('recommendation_type')
        is_read = request.args.get('is_read', type=bool)
        is_accepted = request.args.get('is_accepted', type=bool)
        is_dismissed = request.args.get('is_dismissed', type=bool)
        
        query = UserRecommendation.query.filter(UserRecommendation.user_id == user_id)
        
        if recommendation_type:
            query = query.filter(UserRecommendation.recommendation_type == recommendation_type)
        
        if is_read is not None:
            query = query.filter(UserRecommendation.is_read == is_read)
        
        if is_accepted is not None:
            query = query.filter(UserRecommendation.is_accepted == is_accepted)
        
        if is_dismissed is not None:
            query = query.filter(UserRecommendation.is_dismissed == is_dismissed)
        
        recommendations = query.order_by(UserRecommendation.priority.desc(), UserRecommendation.created_at.desc()).all()
        
        return jsonify([recommendation.to_dict() for recommendation in recommendations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/recommendations/<int:recommendation_id>/read', methods=['POST'])
@jwt_required()
def mark_recommendation_read(recommendation_id):
    """Mark recommendation as read"""
    try:
        user_id = get_jwt_identity()
        
        recommendation = UserRecommendation.query.filter(
            UserRecommendation.id == recommendation_id,
            UserRecommendation.user_id == user_id
        ).first()
        
        if not recommendation:
            return jsonify({'error': 'Recommendation not found'}), 404
        
        recommendation.is_read = True
        db.session.commit()
        
        emit_realtime_update('user_recommendation_read', recommendation.to_dict(), user_id)
        return jsonify(recommendation.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/recommendations/<int:recommendation_id>/accept', methods=['POST'])
@jwt_required()
def accept_recommendation(recommendation_id):
    """Accept recommendation"""
    try:
        user_id = get_jwt_identity()
        
        recommendation = UserRecommendation.query.filter(
            UserRecommendation.id == recommendation_id,
            UserRecommendation.user_id == user_id
        ).first()
        
        if not recommendation:
            return jsonify({'error': 'Recommendation not found'}), 404
        
        recommendation.is_accepted = True
        recommendation.is_read = True
        db.session.commit()
        
        emit_realtime_update('user_recommendation_accepted', recommendation.to_dict(), user_id)
        return jsonify(recommendation.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/recommendations/<int:recommendation_id>/dismiss', methods=['POST'])
@jwt_required()
def dismiss_recommendation(recommendation_id):
    """Dismiss recommendation"""
    try:
        user_id = get_jwt_identity()
        
        recommendation = UserRecommendation.query.filter(
            UserRecommendation.id == recommendation_id,
            UserRecommendation.user_id == user_id
        ).first()
        
        if not recommendation:
            return jsonify({'error': 'Recommendation not found'}), 404
        
        recommendation.is_dismissed = True
        recommendation.is_read = True
        db.session.commit()
        
        emit_realtime_update('user_recommendation_dismissed', recommendation.to_dict(), user_id)
        return jsonify(recommendation.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Feedback
@ux_enhancements_bp.route('/feedback', methods=['GET'])
@jwt_required()
def get_user_feedback():
    """Get user feedback"""
    try:
        user_id = get_jwt_identity()
        feedback_type = request.args.get('feedback_type')
        module_name = request.args.get('module_name')
        feature_name = request.args.get('feature_name')
        status = request.args.get('status')
        
        query = UserFeedback.query.filter(UserFeedback.user_id == user_id)
        
        if feedback_type:
            query = query.filter(UserFeedback.feedback_type == feedback_type)
        
        if module_name:
            query = query.filter(UserFeedback.module_name == module_name)
        
        if feature_name:
            query = query.filter(UserFeedback.feature_name == feature_name)
        
        if status:
            query = query.filter(UserFeedback.status == status)
        
        feedback = query.order_by(UserFeedback.created_at.desc()).all()
        
        return jsonify([fb.to_dict() for fb in feedback])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/feedback', methods=['POST'])
@jwt_required()
def create_user_feedback():
    """Create user feedback"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['feedback_title', 'feedback_description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create feedback
        feedback = UserFeedback(
            user_id=user_id,
            feedback_type=data.get('feedback_type', 'general'),
            feedback_title=data['feedback_title'],
            feedback_description=data['feedback_description'],
            feedback_rating=data.get('feedback_rating'),
            module_name=data.get('module_name'),
            feature_name=data.get('feature_name'),
            feedback_data=data.get('feedback_data'),
            is_anonymous=data.get('is_anonymous', False)
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        emit_realtime_update('user_feedback_created', feedback.to_dict(), user_id)
        return jsonify(feedback.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Tutorials
@ux_enhancements_bp.route('/tutorials', methods=['GET'])
@jwt_required()
def get_user_tutorials():
    """Get user tutorials"""
    try:
        user_id = get_jwt_identity()
        tutorial_name = request.args.get('tutorial_name')
        tutorial_type = request.args.get('tutorial_type')
        tutorial_module = request.args.get('tutorial_module')
        is_completed = request.args.get('is_completed', type=bool)
        
        query = UserTutorial.query.filter(UserTutorial.user_id == user_id)
        
        if tutorial_name:
            query = query.filter(UserTutorial.tutorial_name == tutorial_name)
        
        if tutorial_type:
            query = query.filter(UserTutorial.tutorial_type == tutorial_type)
        
        if tutorial_module:
            query = query.filter(UserTutorial.tutorial_module == tutorial_module)
        
        if is_completed is not None:
            query = query.filter(UserTutorial.is_completed == is_completed)
        
        tutorials = query.order_by(UserTutorial.started_at.desc()).all()
        
        return jsonify([tutorial.to_dict() for tutorial in tutorials])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/tutorials', methods=['POST'])
@jwt_required()
def create_user_tutorial():
    """Create user tutorial"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['tutorial_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create tutorial
        tutorial = UserTutorial(
            user_id=user_id,
            tutorial_name=data['tutorial_name'],
            tutorial_type=data.get('tutorial_type', 'interactive'),
            tutorial_module=data.get('tutorial_module'),
            tutorial_step=data.get('tutorial_step', 0),
            total_steps=data.get('total_steps', 1)
        )
        
        db.session.add(tutorial)
        db.session.commit()
        
        emit_realtime_update('user_tutorial_created', tutorial.to_dict(), user_id)
        return jsonify(tutorial.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/tutorials/<int:tutorial_id>/progress', methods=['POST'])
@jwt_required()
def update_tutorial_progress(tutorial_id):
    """Update tutorial progress"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        tutorial = UserTutorial.query.filter(
            UserTutorial.id == tutorial_id,
            UserTutorial.user_id == user_id
        ).first()
        
        if not tutorial:
            return jsonify({'error': 'Tutorial not found'}), 404
        
        # Update progress
        tutorial.tutorial_step = data.get('tutorial_step', tutorial.tutorial_step)
        tutorial.completion_percentage = (tutorial.tutorial_step / tutorial.total_steps) * 100
        tutorial.last_accessed = datetime.utcnow()
        
        if tutorial.tutorial_step >= tutorial.total_steps:
            tutorial.is_completed = True
            tutorial.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        emit_realtime_update('user_tutorial_progress_updated', tutorial.to_dict(), user_id)
        return jsonify(tutorial.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Help
@ux_enhancements_bp.route('/help', methods=['GET'])
@jwt_required()
def get_user_help():
    """Get user help requests"""
    try:
        user_id = get_jwt_identity()
        help_type = request.args.get('help_type')
        help_category = request.args.get('help_category')
        help_priority = request.args.get('help_priority')
        status = request.args.get('status')
        
        query = UserHelp.query.filter(UserHelp.user_id == user_id)
        
        if help_type:
            query = query.filter(UserHelp.help_type == help_type)
        
        if help_category:
            query = query.filter(UserHelp.help_category == help_category)
        
        if help_priority:
            query = query.filter(UserHelp.help_priority == help_priority)
        
        if status:
            query = query.filter(UserHelp.status == status)
        
        help_requests = query.order_by(UserHelp.created_at.desc()).all()
        
        return jsonify([help_req.to_dict() for help_req in help_requests])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/help', methods=['POST'])
@jwt_required()
def create_user_help():
    """Create user help request"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['help_title', 'help_description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create help request
        help_request = UserHelp(
            user_id=user_id,
            help_type=data.get('help_type', 'question'),
            help_title=data['help_title'],
            help_description=data['help_description'],
            help_category=data.get('help_category'),
            help_priority=data.get('help_priority', 'medium'),
            help_data=data.get('help_data')
        )
        
        db.session.add(help_request)
        db.session.commit()
        
        emit_realtime_update('user_help_created', help_request.to_dict(), user_id)
        return jsonify(help_request.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Sessions
@ux_enhancements_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_user_sessions():
    """Get user sessions"""
    try:
        user_id = get_jwt_identity()
        is_active = request.args.get('is_active', type=bool)
        
        query = UserSession.query.filter(UserSession.user_id == user_id)
        
        if is_active is not None:
            query = query.filter(UserSession.is_active == is_active)
        
        sessions = query.order_by(UserSession.last_activity.desc()).all()
        
        return jsonify([session.to_dict() for session in sessions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_user_session():
    """Create user session"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['session_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create session
        session = UserSession(
            user_id=user_id,
            session_id=data['session_id'],
            session_data=data.get('session_data'),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        )
        
        db.session.add(session)
        db.session.commit()
        
        emit_realtime_update('user_session_created', session.to_dict(), user_id)
        return jsonify(session.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ux_enhancements_bp.route('/sessions/<string:session_id>/update', methods=['POST'])
@jwt_required()
def update_user_session(session_id):
    """Update user session"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        session = UserSession.query.filter(
            UserSession.session_id == session_id,
            UserSession.user_id == user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Update session
        session.session_data = data.get('session_data', session.session_data)
        session.last_activity = datetime.utcnow()
        
        if data.get('expires_at'):
            session.expires_at = datetime.fromisoformat(data['expires_at'])
        
        db.session.commit()
        
        emit_realtime_update('user_session_updated', session.to_dict(), user_id)
        return jsonify(session.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
