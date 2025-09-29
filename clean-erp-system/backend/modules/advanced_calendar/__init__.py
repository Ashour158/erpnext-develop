# Advanced Calendar Module
# Advanced calendar features including recurring event intelligence, meeting room integration, and smart scheduling

from flask import Blueprint

advanced_calendar_bp = Blueprint('advanced_calendar', __name__, url_prefix='/advanced_calendar')

from . import api, models
