# Mobile Enhancements Module
# Mobile app enhancements including offline capability, push notifications, voice commands, and AR features

from flask import Blueprint

mobile_enhancements_bp = Blueprint('mobile_enhancements', __name__, url_prefix='/mobile_enhancements')

from . import api, models
