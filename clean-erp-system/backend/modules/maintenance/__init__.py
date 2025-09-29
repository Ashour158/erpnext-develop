# Maintenance Module - Complete Asset and Maintenance Management
# Advanced maintenance and asset tracking without Frappe dependencies

from flask import Blueprint
from .models import (
    Asset, AssetCategory, MaintenanceSchedule, MaintenanceTask,
    WorkOrder, SparePart, MaintenanceTeam, AssetLocation
)
from .api import maintenance_api

# Create Maintenance blueprint
maintenance_bp = Blueprint('maintenance', __name__)

# Register API routes
maintenance_bp.register_blueprint(maintenance_api, url_prefix='')

# Module information
MAINTENANCE_MODULE_INFO = {
    'name': 'Maintenance',
    'version': '1.0.0',
    'description': 'Complete Asset and Maintenance Management System',
    'features': [
        'Asset Management',
        'Asset Tracking & Location',
        'Preventive Maintenance',
        'Work Order Management',
        'Maintenance Scheduling',
        'Spare Parts Management',
        'Maintenance Team Management',
        'Asset Performance Analytics',
        'Predictive Maintenance',
        'Maintenance Cost Tracking',
        'Asset Lifecycle Management',
        'Compliance Management'
    ]
}
