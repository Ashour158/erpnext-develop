# Desk Module
# Integrated Help Desk and Maintenance Management

from flask import Blueprint

desk_bp = Blueprint('desk', __name__, url_prefix='/desk')

from . import api, models
