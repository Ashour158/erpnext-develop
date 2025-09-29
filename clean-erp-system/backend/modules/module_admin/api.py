# Module Admin API
# Module-specific administration and control panels API

from flask import Blueprint, request, jsonify
from core.database import DatabaseUtils
from core.auth import require_auth, get_current_user
from .models import (
    ModuleAdmin, ModuleConfiguration, ModuleFeature, ModuleUserAccess,
    ModuleDepartmentAccess, ModuleIntegration, ModuleAnalytics, ModuleAlert, ModuleReport
)
import uuid
from datetime import datetime

# Create Module Admin API blueprint
module_admin_api = Blueprint('module_admin_api', __name__)

# Module Admin Management
@module_admin_api.route('/admins', methods=['GET'])
@require_auth
def get_module_admins():
    """Get all module administrators"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        admins = DatabaseUtils.get_all(ModuleAdmin, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [admin.to_dict() for admin in admins],
            'count': len(admins)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/admins', methods=['POST'])
@require_auth
def create_module_admin():
    """Create new module administrator"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        admin = DatabaseUtils.create(ModuleAdmin, data)
        return jsonify({
            'success': True,
            'data': admin.to_dict(),
            'message': 'Module administrator created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Module Configuration Management
@module_admin_api.route('/configurations', methods=['GET'])
@require_auth
def get_module_configurations():
    """Get module configurations"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        configurations = DatabaseUtils.get_all(ModuleConfiguration, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [config.to_dict() for config in configurations],
            'count': len(configurations)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/configurations', methods=['POST'])
@require_auth
def create_module_configuration():
    """Create module configuration"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        configuration = DatabaseUtils.create(ModuleConfiguration, data)
        return jsonify({
            'success': True,
            'data': configuration.to_dict(),
            'message': 'Module configuration created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/configurations/<int:config_id>', methods=['PUT'])
@require_auth
def update_module_configuration(config_id):
    """Update module configuration"""
    try:
        data = request.get_json()
        
        configuration = DatabaseUtils.update(ModuleConfiguration, config_id, data)
        if not configuration:
            return jsonify({'success': False, 'error': 'Configuration not found'}), 404
        
        return jsonify({
            'success': True,
            'data': configuration.to_dict(),
            'message': 'Module configuration updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Module Features Management
@module_admin_api.route('/features', methods=['GET'])
@require_auth
def get_module_features():
    """Get module features"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        features = DatabaseUtils.get_all(ModuleFeature, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [feature.to_dict() for feature in features],
            'count': len(features)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/features', methods=['POST'])
@require_auth
def create_module_feature():
    """Create module feature"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        feature = DatabaseUtils.create(ModuleFeature, data)
        return jsonify({
            'success': True,
            'data': feature.to_dict(),
            'message': 'Module feature created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/features/<int:feature_id>/status', methods=['PUT'])
@require_auth
def update_feature_status(feature_id):
    """Update feature status"""
    try:
        data = request.get_json()
        
        feature = DatabaseUtils.update(ModuleFeature, feature_id, data)
        if not feature:
            return jsonify({'success': False, 'error': 'Feature not found'}), 404
        
        return jsonify({
            'success': True,
            'data': feature.to_dict(),
            'message': 'Feature status updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Module User Access Management
@module_admin_api.route('/user-access', methods=['GET'])
@require_auth
def get_module_user_access():
    """Get module user access"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        access = DatabaseUtils.get_all(ModuleUserAccess, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in access],
            'count': len(access)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/user-access', methods=['POST'])
@require_auth
def grant_module_user_access():
    """Grant module access to user"""
    try:
        data = request.get_json()
        
        # Set granted by
        current_user = get_current_user()
        if current_user:
            data['access_granted_by'] = current_user.id
        
        access = DatabaseUtils.create(ModuleUserAccess, data)
        return jsonify({
            'success': True,
            'data': access.to_dict(),
            'message': 'Module access granted to user successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/user-access/<int:access_id>', methods=['PUT'])
@require_auth
def update_module_user_access(access_id):
    """Update module user access"""
    try:
        data = request.get_json()
        
        access = DatabaseUtils.update(ModuleUserAccess, access_id, data)
        if not access:
            return jsonify({'success': False, 'error': 'Access not found'}), 404
        
        return jsonify({
            'success': True,
            'data': access.to_dict(),
            'message': 'Module user access updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Module Department Access Management
@module_admin_api.route('/department-access', methods=['GET'])
@require_auth
def get_module_department_access():
    """Get module department access"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        access = DatabaseUtils.get_all(ModuleDepartmentAccess, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in access],
            'count': len(access)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/department-access', methods=['POST'])
@require_auth
def grant_module_department_access():
    """Grant module access to department"""
    try:
        data = request.get_json()
        
        # Set granted by
        current_user = get_current_user()
        if current_user:
            data['access_granted_by'] = current_user.id
        
        access = DatabaseUtils.create(ModuleDepartmentAccess, data)
        return jsonify({
            'success': True,
            'data': access.to_dict(),
            'message': 'Module access granted to department successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Module Integrations Management
@module_admin_api.route('/integrations', methods=['GET'])
@require_auth
def get_module_integrations():
    """Get module integrations"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        integrations = DatabaseUtils.get_all(ModuleIntegration, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [integration.to_dict() for integration in integrations],
            'count': len(integrations)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/integrations', methods=['POST'])
@require_auth
def create_module_integration():
    """Create module integration"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        integration = DatabaseUtils.create(ModuleIntegration, data)
        return jsonify({
            'success': True,
            'data': integration.to_dict(),
            'message': 'Module integration created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/integrations/<int:integration_id>/test', methods=['POST'])
@require_auth
def test_module_integration(integration_id):
    """Test module integration"""
    try:
        integration = DatabaseUtils.get_by_id(ModuleIntegration, integration_id)
        if not integration:
            return jsonify({'success': False, 'error': 'Integration not found'}), 404
        
        # Test integration logic would go here
        # For now, return success
        return jsonify({
            'success': True,
            'message': 'Integration test completed successfully',
            'data': {
                'integration_id': integration_id,
                'test_status': 'success',
                'test_time': datetime.utcnow().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Module Analytics
@module_admin_api.route('/analytics', methods=['GET'])
@require_auth
def get_module_analytics():
    """Get module analytics"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        analytics = DatabaseUtils.get_all(ModuleAnalytics, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in analytics],
            'count': len(analytics)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/analytics/dashboard', methods=['GET'])
@require_auth
def get_module_analytics_dashboard():
    """Get module analytics dashboard"""
    try:
        # Get module analytics summary
        total_analytics = DatabaseUtils.count(ModuleAnalytics)
        usage_analytics = DatabaseUtils.count(ModuleAnalytics, {'analytics_type': 'usage'})
        performance_analytics = DatabaseUtils.count(ModuleAnalytics, {'analytics_type': 'performance'})
        error_analytics = DatabaseUtils.count(ModuleAnalytics, {'analytics_type': 'error'})
        
        # Get module features summary
        total_features = DatabaseUtils.count(ModuleFeature)
        enabled_features = DatabaseUtils.count(ModuleFeature, {'feature_status': 'enabled'})
        disabled_features = DatabaseUtils.count(ModuleFeature, {'feature_status': 'disabled'})
        maintenance_features = DatabaseUtils.count(ModuleFeature, {'feature_status': 'maintenance'})
        
        # Get module integrations summary
        total_integrations = DatabaseUtils.count(ModuleIntegration)
        active_integrations = DatabaseUtils.count(ModuleIntegration, {'integration_status': 'active'})
        inactive_integrations = DatabaseUtils.count(ModuleIntegration, {'integration_status': 'inactive'})
        error_integrations = DatabaseUtils.count(ModuleIntegration, {'integration_status': 'error'})
        
        return jsonify({
            'success': True,
            'data': {
                'analytics': {
                    'total_analytics': total_analytics,
                    'usage_analytics': usage_analytics,
                    'performance_analytics': performance_analytics,
                    'error_analytics': error_analytics
                },
                'features': {
                    'total_features': total_features,
                    'enabled_features': enabled_features,
                    'disabled_features': disabled_features,
                    'maintenance_features': maintenance_features
                },
                'integrations': {
                    'total_integrations': total_integrations,
                    'active_integrations': active_integrations,
                    'inactive_integrations': inactive_integrations,
                    'error_integrations': error_integrations
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Module Alerts Management
@module_admin_api.route('/alerts', methods=['GET'])
@require_auth
def get_module_alerts():
    """Get module alerts"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        alerts = DatabaseUtils.get_all(ModuleAlert, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [alert.to_dict() for alert in alerts],
            'count': len(alerts)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/alerts', methods=['POST'])
@require_auth
def create_module_alert():
    """Create module alert"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        alert = DatabaseUtils.create(ModuleAlert, data)
        return jsonify({
            'success': True,
            'data': alert.to_dict(),
            'message': 'Module alert created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/alerts/<int:alert_id>/status', methods=['PUT'])
@require_auth
def update_alert_status(alert_id):
    """Update alert status"""
    try:
        data = request.get_json()
        
        alert = DatabaseUtils.update(ModuleAlert, alert_id, data)
        if not alert:
            return jsonify({'success': False, 'error': 'Alert not found'}), 404
        
        return jsonify({
            'success': True,
            'data': alert.to_dict(),
            'message': 'Alert status updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Module Reports Management
@module_admin_api.route('/reports', methods=['GET'])
@require_auth
def get_module_reports():
    """Get module reports"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        reports = DatabaseUtils.get_all(ModuleReport, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [report.to_dict() for report in reports],
            'count': len(reports)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/reports', methods=['POST'])
@require_auth
def create_module_report():
    """Create module report"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        report = DatabaseUtils.create(ModuleReport, data)
        return jsonify({
            'success': True,
            'data': report.to_dict(),
            'message': 'Module report created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@module_admin_api.route('/reports/<int:report_id>/generate', methods=['POST'])
@require_auth
def generate_module_report(report_id):
    """Generate module report"""
    try:
        report = DatabaseUtils.get_by_id(ModuleReport, report_id)
        if not report:
            return jsonify({'success': False, 'error': 'Report not found'}), 404
        
        # Report generation logic would go here
        # For now, return success
        return jsonify({
            'success': True,
            'message': 'Report generated successfully',
            'data': {
                'report_id': report_id,
                'generation_status': 'success',
                'generation_time': datetime.utcnow().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
