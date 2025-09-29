# Desk Module - Help Desk, Maintenance, and Support
# Complete help desk, maintenance, and support system with all integrated features

from flask import Blueprint
from .models import HelpDeskTicket, MaintenanceRequest, MaintenanceSchedule, Asset
from .api import desk_api
from .ai_features import AITicketClassification, AIMaintenancePrediction, AISupportBot
from .voice_interface import VoiceDeskCommands, VoiceSupport, VoiceReporting
from .mobile_features import MobileDesk, OfflineSupport, PushAlerts
from .calendar_features import MaintenanceCalendar, ScheduleManagement, EventTracking
from .geolocation_features import FieldServiceTracking, LocationServices, GeoAnalytics
from .integration_features import DeskIntegrations, APIConnectors, WebhookSystem
from .blockchain_features import TicketVerification, SmartContracts, AuditTrails
from .ar_vr_features import ARMaintenanceGuides, VRTraining, ARSupport
from .iot_features import IoTDeviceManagement, SmartSensors, IoTDataProcessing

# Create Desk blueprint
desk_bp = Blueprint('desk', __name__)

# Register API routes
desk_bp.register_blueprint(desk_api, url_prefix='')

# Module information
DESK_MODULE_INFO = {
    'name': 'Desk',
    'version': '2.0.0',
    'description': 'Complete Help Desk, Maintenance, and Support Management with all integrated features',
    'features': [
        'Help Desk Tickets',
        'Maintenance Requests',
        'Asset Management',
        'Maintenance Scheduling',
        'Ticket Routing',
        'Priority Management',
        'SLA Tracking',
        'Knowledge Base',
        'Customer Support',
        'Maintenance Analytics',
        'AI Ticket Classification',
        'AI Maintenance Prediction',
        'AI Support Bot',
        'Voice Commands',
        'Voice Support',
        'Voice Reporting',
        'Mobile Desk',
        'Offline Support',
        'Push Alerts',
        'Maintenance Calendar',
        'Schedule Management',
        'Event Tracking',
        'Field Service Tracking',
        'Location Services',
        'Geo Analytics',
        'Desk Integrations',
        'API Connectors',
        'Webhook System',
        'Ticket Verification',
        'Smart Contracts',
        'Audit Trails',
        'AR Maintenance Guides',
        'VR Training',
        'AR Support',
        'IoT Device Management',
        'Smart Sensors',
        'IoT Data Processing'
    ]
}
