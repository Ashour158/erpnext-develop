# Workflow Automation Module
# Smart workflows and conditional logic for automated business processes

from flask import Blueprint

workflow_automation_bp = Blueprint('workflow_automation', __name__, url_prefix='/workflow_automation')

from . import api, models
