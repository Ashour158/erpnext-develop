# Integration Ecosystem Module
# Integration ecosystem with IoT device integration, wearable technology support, third-party APIs, and webhook system

from flask import Blueprint

integration_ecosystem_bp = Blueprint('integration_ecosystem', __name__, url_prefix='/integration_ecosystem')

from . import api, models
