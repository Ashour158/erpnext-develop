# Module Admin Panel
# Module-specific administration and control panels

from flask import Blueprint

module_admin_bp = Blueprint('module_admin', __name__, url_prefix='/module_admin')

from . import api, models
