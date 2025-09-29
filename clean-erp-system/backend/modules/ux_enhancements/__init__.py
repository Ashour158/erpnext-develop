# UX Enhancements Module
# Module for personalization and accessibility features

from flask import Blueprint

ux_enhancements_bp = Blueprint('ux_enhancements', __name__, url_prefix='/ux_enhancements')

from . import api, models
