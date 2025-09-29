# AI Smart Scheduling Module
# AI-powered intelligent scheduling and meeting optimization

from flask import Blueprint

ai_smart_scheduling_bp = Blueprint('ai_smart_scheduling', __name__, url_prefix='/ai_smart_scheduling')

from . import api, models
