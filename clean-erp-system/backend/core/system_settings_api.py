# System Settings API Endpoints
# API endpoints for system settings management

from flask import Blueprint, request, jsonify
from core.database import db
from core.system_settings import SystemSetting, Department, UserProfile, WorkflowTemplate, ApprovalSystem
from core.user_roles import Role, Permission, RolePermission, UserRole, UserPermission, AccessControlList
from core.data_organization import DataArchive, DataRetentionRule, DataBackup, DataIndex, DataPartition
from core.api_marketplace import APIMarketplace, APIAuthentication, APIRateLimit, APIMonitoring, APIIntegration
from core.auth import require_auth, get_current_user
from datetime import datetime
import json

# Create blueprint
system_settings_bp = Blueprint('system_settings', __name__, url_prefix='/system-settings')

# System Settings Endpoints
@system_settings_bp.route('/settings', methods=['GET'])
@require_auth
def get_system_settings():
    """Get all system settings"""
    try:
        settings = SystemSetting.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [setting.to_dict() for setting in settings]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@system_settings_bp.route('/settings', methods=['POST'])
@require_auth
def create_system_setting():
    """Create a new system setting"""
    try:
        data = request.get_json()
        setting = SystemSetting(
            setting_key=data['setting_key'],
            setting_name=data['setting_name'],
            setting_description=data.get('setting_description'),
            category=data['category'],
            setting_value=data.get('setting_value'),
            setting_type=data.get('setting_type', 'string'),
            default_value=data.get('default_value'),
            is_required=data.get('is_required', False),
            is_encrypted=data.get('is_encrypted', False),
            validation_rules=data.get('validation_rules'),
            allowed_values=data.get('allowed_values'),
            display_order=data.get('display_order', 0),
            is_visible=data.get('is_visible', True),
            is_editable=data.get('is_editable', True),
            help_text=data.get('help_text'),
            company_id=get_current_user().company_id
        )
        db.session.add(setting)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': setting.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@system_settings_bp.route('/settings/<int:setting_id>', methods=['PUT'])
@require_auth
def update_system_setting(setting_id):
    """Update a system setting"""
    try:
        setting = SystemSetting.query.get_or_404(setting_id)
        data = request.get_json()
        
        for key, value in data.items():
            if hasattr(setting, key):
                setattr(setting, key, value)
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': setting.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Department Management Endpoints
@system_settings_bp.route('/departments', methods=['GET'])
@require_auth
def get_departments():
    """Get all departments"""
    try:
        departments = Department.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [dept.to_dict() for dept in departments]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@system_settings_bp.route('/departments', methods=['POST'])
@require_auth
def create_department():
    """Create a new department"""
    try:
        data = request.get_json()
        department = Department(
            name=data['name'],
            code=data['code'],
            description=data.get('description'),
            parent_department_id=data.get('parent_department_id'),
            department_head_id=data.get('department_head_id'),
            is_active=data.get('is_active', True),
            budget_limit=data.get('budget_limit', 0.0),
            currency=data.get('currency', 'USD'),
            company_id=get_current_user().company_id
        )
        db.session.add(department)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': department.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# User Profile Management Endpoints
@system_settings_bp.route('/user-profiles', methods=['GET'])
@require_auth
def get_user_profiles():
    """Get all user profiles"""
    try:
        profiles = UserProfile.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [profile.to_dict() for profile in profiles]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@system_settings_bp.route('/user-profiles', methods=['POST'])
@require_auth
def create_user_profile():
    """Create a new user profile"""
    try:
        data = request.get_json()
        profile = UserProfile(
            user_id=data['user_id'],
            display_name=data.get('display_name'),
            bio=data.get('bio'),
            profile_picture=data.get('profile_picture'),
            cover_photo=data.get('cover_photo'),
            personal_email=data.get('personal_email'),
            personal_phone=data.get('personal_phone'),
            website=data.get('website'),
            location=data.get('location'),
            timezone=data.get('timezone', 'UTC'),
            language=data.get('language', 'en'),
            date_format=data.get('date_format', 'YYYY-MM-DD'),
            time_format=data.get('time_format', '24h'),
            email_notifications=data.get('email_notifications', True),
            push_notifications=data.get('push_notifications', True),
            sms_notifications=data.get('sms_notifications', False),
            is_public=data.get('is_public', True),
            allow_following=data.get('allow_following', True),
            allow_messages=data.get('allow_messages', True),
            company_id=get_current_user().company_id
        )
        db.session.add(profile)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': profile.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Workflow Template Management Endpoints
@system_settings_bp.route('/workflow-templates', methods=['GET'])
@require_auth
def get_workflow_templates():
    """Get all workflow templates"""
    try:
        templates = WorkflowTemplate.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [template.to_dict() for template in templates]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@system_settings_bp.route('/workflow-templates', methods=['POST'])
@require_auth
def create_workflow_template():
    """Create a new workflow template"""
    try:
        data = request.get_json()
        template = WorkflowTemplate(
            template_name=data['template_name'],
            template_code=data['template_code'],
            description=data.get('description'),
            template_config=data.get('template_config'),
            workflow_steps=data.get('workflow_steps'),
            approval_rules=data.get('approval_rules'),
            is_active=data.get('is_active', True),
            is_public=data.get('is_public', False),
            is_featured=data.get('is_featured', False),
            company_id=get_current_user().company_id
        )
        db.session.add(template)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': template.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Approval System Management Endpoints
@system_settings_bp.route('/approval-systems', methods=['GET'])
@require_auth
def get_approval_systems():
    """Get all approval systems"""
    try:
        systems = ApprovalSystem.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [system.to_dict() for system in systems]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@system_settings_bp.route('/approval-systems', methods=['POST'])
@require_auth
def create_approval_system():
    """Create a new approval system"""
    try:
        data = request.get_json()
        system = ApprovalSystem(
            system_name=data['system_name'],
            system_code=data['system_code'],
            description=data.get('description'),
            approval_rules=data.get('approval_rules'),
            approval_levels=data.get('approval_levels'),
            escalation_rules=data.get('escalation_rules'),
            is_active=data.get('is_active', True),
            requires_approval=data.get('requires_approval', True),
            auto_approve=data.get('auto_approve', False),
            approval_timeout=data.get('approval_timeout', 24),
            company_id=get_current_user().company_id
        )
        db.session.add(system)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': system.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Role Management Endpoints
@system_settings_bp.route('/roles', methods=['GET'])
@require_auth
def get_roles():
    """Get all roles"""
    try:
        roles = Role.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [role.to_dict() for role in roles]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@system_settings_bp.route('/roles', methods=['POST'])
@require_auth
def create_role():
    """Create a new role"""
    try:
        data = request.get_json()
        role = Role(
            role_name=data['role_name'],
            role_code=data['role_code'],
            description=data.get('description'),
            is_active=data.get('is_active', True),
            is_system_role=data.get('is_system_role', False),
            is_default=data.get('is_default', False),
            parent_role_id=data.get('parent_role_id'),
            company_id=get_current_user().company_id
        )
        db.session.add(role)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': role.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Permission Management Endpoints
@system_settings_bp.route('/permissions', methods=['GET'])
@require_auth
def get_permissions():
    """Get all permissions"""
    try:
        permissions = Permission.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [permission.to_dict() for permission in permissions]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@system_settings_bp.route('/permissions', methods=['POST'])
@require_auth
def create_permission():
    """Create a new permission"""
    try:
        data = request.get_json()
        permission = Permission(
            permission_name=data['permission_name'],
            permission_code=data['permission_code'],
            description=data.get('description'),
            module=data['module'],
            action=data['action'],
            resource=data['resource'],
            permission_level=data.get('permission_level', 'Read'),
            is_active=data.get('is_active', True),
            is_system_permission=data.get('is_system_permission', False),
            company_id=get_current_user().company_id
        )
        db.session.add(permission)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': permission.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Data Organization Endpoints
@system_settings_bp.route('/data-archives', methods=['GET'])
@require_auth
def get_data_archives():
    """Get all data archives"""
    try:
        archives = DataArchive.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [archive.to_dict() for archive in archives]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@system_settings_bp.route('/data-retention-rules', methods=['GET'])
@require_auth
def get_data_retention_rules():
    """Get all data retention rules"""
    try:
        rules = DataRetentionRule.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [rule.to_dict() for rule in rules]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# API Marketplace Endpoints
@system_settings_bp.route('/api-marketplace', methods=['GET'])
@require_auth
def get_api_marketplace():
    """Get all API marketplace entries"""
    try:
        apis = APIMarketplace.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [api.to_dict() for api in apis]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@system_settings_bp.route('/api-marketplace', methods=['POST'])
@require_auth
def create_api_marketplace():
    """Create a new API marketplace entry"""
    try:
        data = request.get_json()
        api = APIMarketplace(
            api_name=data['api_name'],
            api_code=data['api_code'],
            description=data.get('description'),
            api_type=data['api_type'],
            api_version=data.get('api_version', 'v1'),
            base_url=data['base_url'],
            endpoint=data['endpoint'],
            is_active=data.get('is_active', True),
            is_public=data.get('is_public', False),
            is_featured=data.get('is_featured', False),
            requires_authentication=data.get('requires_authentication', True),
            api_documentation=data.get('api_documentation'),
            api_examples=data.get('api_examples'),
            api_schema=data.get('api_schema'),
            company_id=get_current_user().company_id
        )
        db.session.add(api)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': api.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
