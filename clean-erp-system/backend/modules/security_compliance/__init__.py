# Security & Compliance Module
# Security and compliance features including data privacy controls, audit trails, encryption, and access controls

from flask import Blueprint

security_compliance_bp = Blueprint('security_compliance', __name__, url_prefix='/security_compliance')

from . import api, models
