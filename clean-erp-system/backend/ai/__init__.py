# AI Module Initialization
# Advanced AI-powered features for ERP system

from flask import Blueprint

# Create AI Blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

# Import AI components
from . import ai_api
from .ai_analytics_engine import ai_analytics_engine
from .intelligent_automation import intelligent_automation_engine
from .natural_language_interface import natural_language_interface

# Export AI components
__all__ = [
    'ai_bp',
    'ai_api',
    'ai_analytics_engine',
    'intelligent_automation_engine',
    'natural_language_interface'
]
