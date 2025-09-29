# AI & Automation Module
# Advanced AI features, machine learning, and process automation

from flask import Blueprint

ai_automation_bp = Blueprint('ai_automation', __name__, url_prefix='/ai-automation')

from . import api, models
