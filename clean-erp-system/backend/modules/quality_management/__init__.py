# Quality Management Module
# Complete quality control, inspection management, and compliance tracking

from flask import Blueprint

quality_management_bp = Blueprint('quality_management', __name__, url_prefix='/quality-management')

from . import api, models
