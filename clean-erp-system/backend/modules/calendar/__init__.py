# Calendar Module
# Integrated calendar system with all modules, geolocation, and external calendar sync

from flask import Blueprint

calendar_bp = Blueprint('calendar', __name__, url_prefix='/calendar')

from . import api, models
