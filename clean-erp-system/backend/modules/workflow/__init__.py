# Workflow Module - Complete Workflow Engine and Automation
# Advanced workflow and automation without Frappe dependencies

from flask import Blueprint
from .models import (
    Workflow, WorkflowStep, WorkflowExecution, WorkflowRule,
    WorkflowTrigger, WorkflowAction, WorkflowCondition, WorkflowTemplate
)
from .api import workflow_api

# Create Workflow blueprint
workflow_bp = Blueprint('workflow', __name__)

# Register API routes
workflow_bp.register_blueprint(workflow_api, url_prefix='')

# Module information
WORKFLOW_MODULE_INFO = {
    'name': 'Workflow Engine',
    'version': '1.0.0',
    'description': 'Complete Workflow Engine and Automation System',
    'features': [
        'Visual Workflow Designer',
        'Automated Workflows',
        'Conditional Logic',
        'Multi-step Processes',
        'Approval Workflows',
        'Notification Automation',
        'Data Integration',
        'Workflow Templates',
        'Process Analytics',
        'Error Handling',
        'Workflow Scheduling',
        'Custom Actions'
    ]
}
