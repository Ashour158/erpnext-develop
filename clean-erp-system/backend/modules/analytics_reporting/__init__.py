# Analytics & Reporting Module
# Advanced analytics and reporting system with productivity insights, attendance analytics, and performance metrics

from flask import Blueprint

analytics_reporting_bp = Blueprint('analytics_reporting', __name__, url_prefix='/analytics_reporting')

from . import api, models
