# CRM Module - Customer Relationship Management
# Complete CRM system without Frappe dependencies

from flask import Blueprint
from .models import Customer, Contact, Lead, Opportunity, Account
from .api import crm_api

# Create CRM blueprint
crm_bp = Blueprint('crm', __name__)

# Register API routes
crm_bp.register_blueprint(crm_api, url_prefix='')

# Module information
CRM_MODULE_INFO = {
    'name': 'CRM',
    'version': '1.0.0',
    'description': 'Customer Relationship Management',
    'features': [
        'Customer Management',
        'Contact Management', 
        'Lead Management',
        'Opportunity Tracking',
        'Account Management',
        'Sales Pipeline',
        'Customer 360° View',
        'Activity Tracking',
        'Communication History',
        'Sales Analytics'
    ]
}
