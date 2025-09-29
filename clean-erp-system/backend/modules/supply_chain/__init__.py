# Supply Chain Module - Complete Supply Chain Management
# Advanced inventory, procurement, and logistics with IoT, Blockchain, AI, Voice, and Mobile capabilities

from flask import Blueprint
from .models import (
    Supplier, Item, ItemGroup, Warehouse, StockEntry, PurchaseOrder,
    PurchaseReceipt, SalesOrder, DeliveryNote, StockMovement,
    ItemPrice, ItemVariant, BOM, ProductionOrder
)
from .api import supply_chain_api
from .iot_features import IoTDeviceManagement, SmartManufacturing, SupplyChainIoT
from .blockchain_features import SupplyChainTransparency, SmartContracts, AuditTrails
from .ai_features import AIDemandForecasting, AIInventoryOptimization, AISupplierAnalytics
from .voice_interface import VoiceSupplyChainCommands, VoiceInventorySearch, VoiceReporting
from .mobile_features import MobileSupplyChain, OfflineInventorySync, PushAlerts

# Create Supply Chain blueprint
supply_chain_bp = Blueprint('supply_chain', __name__)

# Register API routes
supply_chain_bp.register_blueprint(supply_chain_api, url_prefix='')

# Module information
SUPPLY_CHAIN_MODULE_INFO = {
    'name': 'Supply Chain',
    'version': '2.0.0',
    'description': 'Complete Supply Chain Management System with IoT, Blockchain, AI, Voice, and Mobile capabilities',
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
        'Supplier Performance Analytics',
        'IoT Device Management',
        'Smart Manufacturing',
        'Supply Chain IoT',
        'Blockchain Transparency',
        'Smart Contracts',
        'Audit Trails',
        'AI Demand Forecasting',
        'AI Inventory Optimization',
        'AI Supplier Analytics',
        'Voice Commands',
        'Voice Inventory Search',
        'Voice Reporting',
        'Mobile Supply Chain',
        'Offline Inventory Sync',
        'Push Alerts'
    ]
}
