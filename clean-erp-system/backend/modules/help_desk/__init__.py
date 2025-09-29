# Help Desk Module
# Comprehensive customer service and support system

from flask import Blueprint

help_desk_bp = Blueprint('help_desk', __name__, url_prefix='/help_desk')

from . import api, models
