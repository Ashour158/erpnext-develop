# Booking Module - Complete Resource Booking and Scheduling
# Advanced booking and scheduling without Frappe dependencies

from flask import Blueprint
from .models import (
    Resource, ResourceCategory, Booking, BookingSlot, BookingRule,
    RecurringBooking, BookingConflict, BookingApproval
)
from .api import booking_api

# Create Booking blueprint
booking_bp = Blueprint('booking', __name__)

# Register API routes
booking_bp.register_blueprint(booking_api, url_prefix='')

# Module information
BOOKING_MODULE_INFO = {
    'name': 'Booking',
    'version': '1.0.0',
    'description': 'Complete Resource Booking and Scheduling System',
    'features': [
        'Resource Management',
        'Booking Scheduling',
        'Recurring Bookings',
        'Booking Rules & Policies',
        'Conflict Resolution',
        'Approval Workflows',
        'Calendar Integration',
        'Resource Availability',
        'Booking Analytics',
        'Multi-Resource Booking',
        'Time Zone Support',
        'Booking Notifications'
    ]
}
