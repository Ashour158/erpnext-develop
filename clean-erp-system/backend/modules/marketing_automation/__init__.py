# Marketing Automation Module
# Comprehensive marketing automation for online and offline activities

from flask import Blueprint

marketing_automation_bp = Blueprint('marketing_automation', __name__, url_prefix='/marketing_automation')

from . import api, models
