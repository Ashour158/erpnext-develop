# CRM Module - Customer Relationship Management
# Complete CRM system with all integrated features

from flask import Blueprint
from .models import Customer, Contact, Lead, Opportunity, Account
from .api import crm_api
from .ai_features import AILeadScoring, AICustomerSegmentation, AISalesForecasting, AIChatbot, AISmartScheduling
from .voice_interface import VoiceCRMCommands, VoiceSearch, VoiceReporting
from .mobile_features import MobileCRM, OfflineSync, PushNotifications
from .calendar_features import AdvancedCalendar, CalendarIntegration, EventManagement
from .geolocation_features import GeolocationTracking, LocationServices, GeoAnalytics
from .integration_features import CRMIntegrations, APIConnectors, WebhookSystem
from .blockchain_features import CustomerVerification, SmartContracts, AuditTrails
from .ar_vr_features import ARCustomerVisualization, VRMeetings, ARProductDemo
from .iot_features import IoTDeviceManagement, SmartSensors, IoTDataProcessing

# Create CRM blueprint
crm_bp = Blueprint('crm', __name__)

# Register API routes
crm_bp.register_blueprint(crm_api, url_prefix='')

# Module information
CRM_MODULE_INFO = {
    'name': 'CRM',
    'version': '3.0.0',
    'description': 'Complete Customer Relationship Management with all integrated features',
    'features': [
        'Customer Management',
        'Contact Management', 
        'Lead Management',
        'Opportunity Tracking',
        'Account Management',
        'Sales Pipeline',
        'Customer 360° View',
        'Activity Tracking',
        'Communication History',
        'Sales Analytics',
        'AI Lead Scoring',
        'AI Customer Segmentation',
        'AI Sales Forecasting',
        'AI Chatbot',
        'AI Smart Scheduling',
        'Voice Commands',
        'Voice Search',
        'Voice Reporting',
        'Mobile CRM',
        'Offline Sync',
        'Push Notifications',
        'Advanced Calendar',
        'Calendar Integration',
        'Event Management',
        'Geolocation Tracking',
        'Location Services',
        'Geo Analytics',
        'CRM Integrations',
        'API Connectors',
        'Webhook System',
        'Customer Verification',
        'Smart Contracts',
        'Audit Trails',
        'AR Customer Visualization',
        'VR Meetings',
        'AR Product Demo',
        'IoT Device Management',
        'Smart Sensors',
        'IoT Data Processing'
    ]
}
