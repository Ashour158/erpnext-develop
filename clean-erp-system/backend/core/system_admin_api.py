# System Admin API
# Comprehensive system administration API with full control

from flask import Blueprint, request, jsonify
from core.database import DatabaseUtils
from core.auth import require_auth, get_current_user
from .system_admin import (
    SystemAdmin, SystemModule, Department, DepartmentModule, UserDepartment,
    UserModule, SystemPermission, UserPermission, SystemSetting, SystemAuditLog, SystemHealth
)
from .privilege_hierarchy import (
    UserRole, Permission, RolePermission, UserRoleAssignment, UserPermission,
    AccessControlList, SecurityPolicy, AccessLog, PermissionAudit
)
import uuid
from datetime import datetime

# Create System Admin API blueprint
system_admin_api = Blueprint('system_admin_api', __name__)

# System Admin Management
@system_admin_api.route('/admins', methods=['GET'])
@require_auth
def get_system_admins():
    """Get all system administrators"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        admins = DatabaseUtils.get_all(SystemAdmin, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [admin.to_dict() for admin in admins],
            'count': len(admins)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@system_admin_api.route('/admins', methods=['POST'])
@require_auth
def create_system_admin():
    """Create new system administrator"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        admin = DatabaseUtils.create(SystemAdmin, data)
        return jsonify({
            'success': True,
            'data': admin.to_dict(),
            'message': 'System administrator created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# System Modules Management
@system_admin_api.route('/modules', methods=['GET'])
@require_auth
def get_system_modules():
    """Get all system modules"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        modules = DatabaseUtils.get_all(SystemModule, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [module.to_dict() for module in modules],
            'count': len(modules)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@system_admin_api.route('/modules', methods=['POST'])
@require_auth
def create_system_module():
    """Create new system module"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['module_created_by'] = current_user.id
        
        module = DatabaseUtils.create(SystemModule, data)
        return jsonify({
            'success': True,
            'data': module.to_dict(),
            'message': 'System module created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@system_admin_api.route('/modules/<int:module_id>/status', methods=['PUT'])
@require_auth
def update_module_status(module_id):
    """Update module status"""
    try:
        data = request.get_json()
        
        module = DatabaseUtils.update(SystemModule, module_id, data)
        if not module:
            return jsonify({'success': False, 'error': 'Module not found'}), 404
        
        return jsonify({
            'success': True,
            'data': module.to_dict(),
            'message': 'Module status updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Department Management
@system_admin_api.route('/departments', methods=['GET'])
@require_auth
def get_departments():
    """Get all departments"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        departments = DatabaseUtils.get_all(Department, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [dept.to_dict() for dept in departments],
            'count': len(departments)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@system_admin_api.route('/departments', methods=['POST'])
@require_auth
def create_department():
    """Create new department"""
    try:
        data = request.get_json()
        
        # Generate department code if not provided
        if 'department_code' not in data:
            data['department_code'] = f"DEPT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        department = DatabaseUtils.create(Department, data)
        return jsonify({
            'success': True,
            'data': department.to_dict(),
            'message': 'Department created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@system_admin_api.route('/departments/<int:department_id>/modules', methods=['POST'])
@require_auth
def assign_module_to_department(department_id):
    """Assign module to department"""
    try:
        data = request.get_json()
        data['department_id'] = department_id
        
        # Set granted by
        current_user = get_current_user()
        if current_user:
            data['access_granted_by'] = current_user.id
        
        assignment = DatabaseUtils.create(DepartmentModule, data)
        return jsonify({
            'success': True,
            'data': assignment.to_dict(),
            'message': 'Module assigned to department successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# User Department Assignment
@system_admin_api.route('/users/<int:user_id>/departments', methods=['POST'])
@require_auth
def assign_user_to_department(user_id):
    """Assign user to department"""
    try:
        data = request.get_json()
        data['user_id'] = user_id
        
        # Set assigned by
        current_user = get_current_user()
        if current_user:
            data['assigned_by'] = current_user.id
        
        assignment = DatabaseUtils.create(UserDepartment, data)
        return jsonify({
            'success': True,
            'data': assignment.to_dict(),
            'message': 'User assigned to department successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# User Module Access
@system_admin_api.route('/users/<int:user_id>/modules', methods=['POST'])
@require_auth
def grant_module_access_to_user(user_id):
    """Grant module access to user"""
    try:
        data = request.get_json()
        data['user_id'] = user_id
        
        # Set granted by
        current_user = get_current_user()
        if current_user:
            data['access_granted_by'] = current_user.id
        
        access = DatabaseUtils.create(UserModule, data)
        return jsonify({
            'success': True,
            'data': access.to_dict(),
            'message': 'Module access granted to user successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Role Management
@system_admin_api.route('/roles', methods=['GET'])
@require_auth
def get_user_roles():
    """Get all user roles"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        roles = DatabaseUtils.get_all(UserRole, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [role.to_dict() for role in roles],
            'count': len(roles)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@system_admin_api.route('/roles', methods=['POST'])
@require_auth
def create_user_role():
    """Create new user role"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        role = DatabaseUtils.create(UserRole, data)
        return jsonify({
            'success': True,
            'data': role.to_dict(),
            'message': 'User role created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Permission Management
@system_admin_api.route('/permissions', methods=['GET'])
@require_auth
def get_permissions():
    """Get all permissions"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        permissions = DatabaseUtils.get_all(Permission, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [permission.to_dict() for permission in permissions],
            'count': len(permissions)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@system_admin_api.route('/permissions', methods=['POST'])
@require_auth
def create_permission():
    """Create new permission"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        permission = DatabaseUtils.create(Permission, data)
        return jsonify({
            'success': True,
            'data': permission.to_dict(),
            'message': 'Permission created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Role-Permission Assignment
@system_admin_api.route('/roles/<int:role_id>/permissions', methods=['POST'])
@require_auth
def assign_permission_to_role(role_id):
    """Assign permission to role"""
    try:
        data = request.get_json()
        data['role_id'] = role_id
        
        # Set assigned by
        current_user = get_current_user()
        if current_user:
            data['assigned_by'] = current_user.id
        
        assignment = DatabaseUtils.create(RolePermission, data)
        return jsonify({
            'success': True,
            'data': assignment.to_dict(),
            'message': 'Permission assigned to role successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# User Role Assignment
@system_admin_api.route('/users/<int:user_id>/roles', methods=['POST'])
@require_auth
def assign_role_to_user(user_id):
    """Assign role to user"""
    try:
        data = request.get_json()
        data['user_id'] = user_id
        
        # Set assigned by
        current_user = get_current_user()
        if current_user:
            data['assigned_by'] = current_user.id
        
        assignment = DatabaseUtils.create(UserRoleAssignment, data)
        return jsonify({
            'success': True,
            'data': assignment.to_dict(),
            'message': 'Role assigned to user successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# System Settings
@system_admin_api.route('/settings', methods=['GET'])
@require_auth
def get_system_settings():
    """Get system settings"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        settings = DatabaseUtils.get_all(SystemSetting, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [setting.to_dict() for setting in settings],
            'count': len(settings)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@system_admin_api.route('/settings', methods=['POST'])
@require_auth
def create_system_setting():
    """Create system setting"""
    try:
        data = request.get_json()
        
        # Set updated by
        current_user = get_current_user()
        if current_user:
            data['setting_updated_by'] = current_user.id
        
        setting = DatabaseUtils.create(SystemSetting, data)
        return jsonify({
            'success': True,
            'data': setting.to_dict(),
            'message': 'System setting created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@system_admin_api.route('/settings/<int:setting_id>', methods=['PUT'])
@require_auth
def update_system_setting(setting_id):
    """Update system setting"""
    try:
        data = request.get_json()
        
        # Set updated by
        current_user = get_current_user()
        if current_user:
            data['setting_updated_by'] = current_user.id
        
        setting = DatabaseUtils.update(SystemSetting, setting_id, data)
        if not setting:
            return jsonify({'success': False, 'error': 'Setting not found'}), 404
        
        return jsonify({
            'success': True,
            'data': setting.to_dict(),
            'message': 'System setting updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# System Dashboard
@system_admin_api.route('/dashboard', methods=['GET'])
@require_auth
def get_system_dashboard():
    """Get system dashboard"""
    try:
        # Get system overview
        total_users = DatabaseUtils.count('users')
        total_departments = DatabaseUtils.count(Department)
        total_modules = DatabaseUtils.count(SystemModule)
        total_roles = DatabaseUtils.count(UserRole)
        total_permissions = DatabaseUtils.count(Permission)
        
        # Get active modules
        active_modules = DatabaseUtils.count(SystemModule, {'module_status': 'active'})
        inactive_modules = DatabaseUtils.count(SystemModule, {'module_status': 'inactive'})
        maintenance_modules = DatabaseUtils.count(SystemModule, {'module_status': 'maintenance'})
        
        # Get user distribution
        admin_users = DatabaseUtils.count(SystemAdmin)
        regular_users = total_users - admin_users
        
        # Get department distribution
        active_departments = DatabaseUtils.count(Department, {'department_status': 'active'})
        inactive_departments = DatabaseUtils.count(Department, {'department_status': 'inactive'})
        
        # Get permission distribution
        active_permissions = DatabaseUtils.count(Permission, {'is_active': True})
        inactive_permissions = DatabaseUtils.count(Permission, {'is_active': False})
        
        return jsonify({
            'success': True,
            'data': {
                'overview': {
                    'total_users': total_users,
                    'total_departments': total_departments,
                    'total_modules': total_modules,
                    'total_roles': total_roles,
                    'total_permissions': total_permissions
                },
                'modules': {
                    'active_modules': active_modules,
                    'inactive_modules': inactive_modules,
                    'maintenance_modules': maintenance_modules
                },
                'users': {
                    'admin_users': admin_users,
                    'regular_users': regular_users
                },
                'departments': {
                    'active_departments': active_departments,
                    'inactive_departments': inactive_departments
                },
                'permissions': {
                    'active_permissions': active_permissions,
                    'inactive_permissions': inactive_permissions
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# System Health Check
@system_admin_api.route('/health', methods=['GET'])
@require_auth
def get_system_health():
    """Get system health status"""
    try:
        # Get system health metrics
        health_checks = DatabaseUtils.get_all(SystemHealth)
        
        # Calculate overall health
        total_checks = len(health_checks)
        healthy_checks = len([h for h in health_checks if h.health_status == 'healthy'])
        warning_checks = len([h for h in health_checks if h.health_status == 'warning'])
        critical_checks = len([h for h in health_checks if h.health_status == 'critical'])
        
        overall_health = (healthy_checks / total_checks * 100) if total_checks > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'overall_health': overall_health,
                'total_checks': total_checks,
                'healthy_checks': healthy_checks,
                'warning_checks': warning_checks,
                'critical_checks': critical_checks,
                'health_details': [check.to_dict() for check in health_checks]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Audit Logs
@system_admin_api.route('/audit-logs', methods=['GET'])
@require_auth
def get_audit_logs():
    """Get system audit logs"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        logs = DatabaseUtils.get_all(SystemAuditLog, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [log.to_dict() for log in logs],
            'count': len(logs)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Access Logs
@system_admin_api.route('/access-logs', methods=['GET'])
@require_auth
def get_access_logs():
    """Get access logs"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        logs = DatabaseUtils.get_all(AccessLog, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [log.to_dict() for log in logs],
            'count': len(logs)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Permission Audit
@system_admin_api.route('/permission-audit', methods=['GET'])
@require_auth
def get_permission_audit():
    """Get permission audit logs"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        audits = DatabaseUtils.get_all(PermissionAudit, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [audit.to_dict() for audit in audits],
            'count': len(audits)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
