# Mobile App Module
# Native mobile applications with offline capability and push notifications

from flask import Blueprint

mobile_app_bp = Blueprint('mobile_app', __name__, url_prefix='/mobile-app')

from . import api, models
