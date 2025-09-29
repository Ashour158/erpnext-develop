# Integrations Module
# Third-party integrations, API marketplace, and external system connections

from flask import Blueprint

integrations_bp = Blueprint('integrations', __name__, url_prefix='/integrations')

from . import api, models
