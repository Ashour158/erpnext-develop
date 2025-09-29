# Moments Module - Complete Social and Collaboration Platform
# Advanced social features without Frappe dependencies

from flask import Blueprint
from .models import (
    Moment, MomentReaction, MomentComment, MomentShare, MomentTag,
    UserFeed, Notification, Follow, UserProfile, MomentCategory
)
from .api import moments_api

# Create Moments blueprint
moments_bp = Blueprint('moments', __name__)

# Register API routes
moments_bp.register_blueprint(moments_api, url_prefix='')

# Module information
MOMENTS_MODULE_INFO = {
    'name': 'Moments',
    'version': '1.0.0',
    'description': 'Complete Social and Collaboration Platform',
    'features': [
        'Social Moments & Posts',
        'Reactions & Comments',
        'User Following System',
        'Personalized Feeds',
        'Notifications & Alerts',
        'Content Sharing',
        'Tagging & Categories',
        'User Profiles',
        'Social Analytics',
        'Content Moderation',
        'Privacy Controls',
        'Real-time Updates'
    ]
}
