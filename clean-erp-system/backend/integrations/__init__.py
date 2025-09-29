# Integration Module Initialization
# Advanced integration ecosystem for ERP system

from flask import Blueprint

# Create Integration Blueprint
integration_bp = Blueprint('integration', __name__, url_prefix='/integration')

# Import Integration components
from . import integration_api
from .enterprise_connectors import enterprise_connector_manager
from .crm_connectors import crm_connector_manager
from .ecommerce_connectors import ecommerce_connector_manager
from .api_marketplace import api_marketplace
from .webhook_system import webhook_system

# Export Integration components
__all__ = [
    'integration_bp',
    'integration_api',
    'enterprise_connector_manager',
    'crm_connector_manager',
    'ecommerce_connector_manager',
    'api_marketplace',
    'webhook_system'
]
