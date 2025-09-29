# Business Intelligence Module
# Advanced analytics, reporting, and data visualization

from flask import Blueprint

business_intelligence_bp = Blueprint('business_intelligence', __name__, url_prefix='/business-intelligence')

from . import api, models
