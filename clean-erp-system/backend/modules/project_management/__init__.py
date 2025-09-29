# Project Management Module
# Complete project management with Gantt charts, resource allocation, and project analytics

from flask import Blueprint

project_management_bp = Blueprint('project_management', __name__, url_prefix='/project-management')

from . import api, models
