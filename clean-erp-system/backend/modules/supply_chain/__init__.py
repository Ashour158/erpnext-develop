# Supply Chain Module - Complete Supply Chain Management
# Advanced inventory, procurement, and logistics without Frappe dependencies

from flask import Blueprint
from .models import (
    Supplier, Item, ItemGroup, Warehouse, StockEntry, PurchaseOrder,
    PurchaseReceipt, SalesOrder, DeliveryNote, StockMovement,
    ItemPrice, ItemVariant, BOM, ProductionOrder
)
from .api import supply_chain_api

# Create Supply Chain blueprint
supply_chain_bp = Blueprint('supply_chain', __name__)

# Register API routes
supply_chain_bp.register_blueprint(supply_chain_api, url_prefix='')

# Module information
SUPPLY_CHAIN_MODULE_INFO = {
    'name': 'Supply Chain',
    'version': '1.0.0',
    'description': 'Complete Supply Chain Management System',
    'features': [
        'Inventory Management',
        'Supplier Management',
        'Purchase Order Processing',
        'Sales Order Management',
        'Warehouse Management',
        'Stock Movement Tracking',
        'Item Variants & Pricing',
        'Bill of Materials (BOM)',
        'Production Planning',
        'Logistics Management',
        'Demand Forecasting',
        'Supplier Performance Analytics'
    ]
}
