# Performance Optimization Module
# Performance optimization features including caching strategy, load balancing, and performance monitoring

from flask import Blueprint

performance_optimization_bp = Blueprint('performance_optimization', __name__, url_prefix='/performance_optimization')

from . import api, models
