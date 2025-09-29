# People Module - Complete Human Resources Management
# Advanced HR features without Frappe dependencies

from flask import Blueprint
from .models import (
    Employee, Department, Designation, LeaveRequest, LeaveType,
    Attendance, Payroll, Performance, Training, Recruitment
)
from .api import people_api

# Create People blueprint
people_bp = Blueprint('people', __name__)

# Register API routes
people_bp.register_blueprint(people_api, url_prefix='')

# Module information
PEOPLE_MODULE_INFO = {
    'name': 'People',
    'version': '1.0.0',
    'description': 'Complete Human Resources Management System',
    'features': [
        'Employee Management',
        'Department & Designation Management',
        'Leave Management System',
        'Attendance Tracking',
        'Payroll Processing',
        'Performance Management',
        'Training & Development',
        'Recruitment Management',
        'HR Analytics',
        'Employee Self-Service',
        'Document Management',
        'Compliance Tracking'
    ]
}
