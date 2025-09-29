# Marketing Automation API
# Comprehensive marketing automation API for online and offline activities

from flask import Blueprint, request, jsonify
from core.database import DatabaseUtils
from core.auth import require_auth, get_current_user
from .models import (
    MarketingCampaign, EmailCampaign, SocialMediaCampaign, WebCampaign,
    LeadNurturing, ContentMarketing, EventMarketing, MarketingAutomation,
    MarketingAnalytics, MarketingAttribution
)
import uuid
from datetime import datetime

# Create Marketing Automation API blueprint
marketing_automation_api = Blueprint('marketing_automation_api', __name__)

# Marketing Campaign API Endpoints
@marketing_automation_api.route('/campaigns', methods=['GET'])
@require_auth
def get_campaigns():
    """Get all marketing campaigns"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        campaigns = DatabaseUtils.get_all(MarketingCampaign, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [campaign.to_dict() for campaign in campaigns],
            'count': len(campaigns)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@marketing_automation_api.route('/campaigns', methods=['POST'])
@require_auth
def create_campaign():
    """Create new marketing campaign"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        campaign = DatabaseUtils.create(MarketingCampaign, data)
        return jsonify({
            'success': True,
            'data': campaign.to_dict(),
            'message': 'Campaign created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@marketing_automation_api.route('/campaigns/<int:campaign_id>', methods=['GET'])
@require_auth
def get_campaign(campaign_id):
    """Get campaign by ID"""
    try:
        campaign = DatabaseUtils.get_by_id(MarketingCampaign, campaign_id)
        if not campaign:
            return jsonify({'success': False, 'error': 'Campaign not found'}), 404
        
        return jsonify({
            'success': True,
            'data': campaign.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@marketing_automation_api.route('/campaigns/<int:campaign_id>', methods=['PUT'])
@require_auth
def update_campaign(campaign_id):
    """Update campaign"""
    try:
        data = request.get_json()
        
        # Set updated by
        current_user = get_current_user()
        if current_user:
            data['updated_by'] = current_user.id
        
        campaign = DatabaseUtils.update(MarketingCampaign, campaign_id, data)
        if not campaign:
            return jsonify({'success': False, 'error': 'Campaign not found'}), 404
        
        return jsonify({
            'success': True,
            'data': campaign.to_dict(),
            'message': 'Campaign updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@marketing_automation_api.route('/campaigns/<int:campaign_id>', methods=['DELETE'])
@require_auth
def delete_campaign(campaign_id):
    """Delete campaign"""
    try:
        campaign = DatabaseUtils.delete(MarketingCampaign, campaign_id)
        if not campaign:
            return jsonify({'success': False, 'error': 'Campaign not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Campaign deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Email Campaign API Endpoints
@marketing_automation_api.route('/email-campaigns', methods=['GET'])
@require_auth
def get_email_campaigns():
    """Get all email campaigns"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        email_campaigns = DatabaseUtils.get_all(EmailCampaign, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [campaign.to_dict() for campaign in email_campaigns],
            'count': len(email_campaigns)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@marketing_automation_api.route('/email-campaigns', methods=['POST'])
@require_auth
def create_email_campaign():
    """Create new email campaign"""
    try:
        data = request.get_json()
        
        email_campaign = DatabaseUtils.create(EmailCampaign, data)
        return jsonify({
            'success': True,
            'data': email_campaign.to_dict(),
            'message': 'Email campaign created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Social Media Campaign API Endpoints
@marketing_automation_api.route('/social-campaigns', methods=['GET'])
@require_auth
def get_social_campaigns():
    """Get all social media campaigns"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        social_campaigns = DatabaseUtils.get_all(SocialMediaCampaign, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [campaign.to_dict() for campaign in social_campaigns],
            'count': len(social_campaigns)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@marketing_automation_api.route('/social-campaigns', methods=['POST'])
@require_auth
def create_social_campaign():
    """Create new social media campaign"""
    try:
        data = request.get_json()
        
        social_campaign = DatabaseUtils.create(SocialMediaCampaign, data)
        return jsonify({
            'success': True,
            'data': social_campaign.to_dict(),
            'message': 'Social media campaign created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Web Campaign API Endpoints
@marketing_automation_api.route('/web-campaigns', methods=['GET'])
@require_auth
def get_web_campaigns():
    """Get all web campaigns"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        web_campaigns = DatabaseUtils.get_all(WebCampaign, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [campaign.to_dict() for campaign in web_campaigns],
            'count': len(web_campaigns)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@marketing_automation_api.route('/web-campaigns', methods=['POST'])
@require_auth
def create_web_campaign():
    """Create new web campaign"""
    try:
        data = request.get_json()
        
        web_campaign = DatabaseUtils.create(WebCampaign, data)
        return jsonify({
            'success': True,
            'data': web_campaign.to_dict(),
            'message': 'Web campaign created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Lead Nurturing API Endpoints
@marketing_automation_api.route('/lead-nurturing', methods=['GET'])
@require_auth
def get_lead_nurturing():
    """Get all lead nurturing sequences"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        nurturing = DatabaseUtils.get_all(LeadNurturing, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [nurture.to_dict() for nurture in nurturing],
            'count': len(nurturing)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@marketing_automation_api.route('/lead-nurturing', methods=['POST'])
@require_auth
def create_lead_nurturing():
    """Create new lead nurturing sequence"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        nurturing = DatabaseUtils.create(LeadNurturing, data)
        return jsonify({
            'success': True,
            'data': nurturing.to_dict(),
            'message': 'Lead nurturing sequence created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Content Marketing API Endpoints
@marketing_automation_api.route('/content', methods=['GET'])
@require_auth
def get_content():
    """Get all content marketing"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        content = DatabaseUtils.get_all(ContentMarketing, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in content],
            'count': len(content)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@marketing_automation_api.route('/content', methods=['POST'])
@require_auth
def create_content():
    """Create new content marketing"""
    try:
        data = request.get_json()
        
        content = DatabaseUtils.create(ContentMarketing, data)
        return jsonify({
            'success': True,
            'data': content.to_dict(),
            'message': 'Content created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Event Marketing API Endpoints
@marketing_automation_api.route('/events', methods=['GET'])
@require_auth
def get_events():
    """Get all marketing events"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        events = DatabaseUtils.get_all(EventMarketing, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [event.to_dict() for event in events],
            'count': len(events)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@marketing_automation_api.route('/events', methods=['POST'])
@require_auth
def create_event():
    """Create new marketing event"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        event = DatabaseUtils.create(EventMarketing, data)
        return jsonify({
            'success': True,
            'data': event.to_dict(),
            'message': 'Event created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Marketing Automation API Endpoints
@marketing_automation_api.route('/automation', methods=['GET'])
@require_auth
def get_automation():
    """Get all marketing automation"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        automation = DatabaseUtils.get_all(MarketingAutomation, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in automation],
            'count': len(automation)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@marketing_automation_api.route('/automation', methods=['POST'])
@require_auth
def create_automation():
    """Create new marketing automation"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        automation = DatabaseUtils.create(MarketingAutomation, data)
        return jsonify({
            'success': True,
            'data': automation.to_dict(),
            'message': 'Marketing automation created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Marketing Analytics API Endpoints
@marketing_automation_api.route('/analytics', methods=['GET'])
@require_auth
def get_analytics():
    """Get marketing analytics"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        analytics = DatabaseUtils.get_all(MarketingAnalytics, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in analytics],
            'count': len(analytics)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@marketing_automation_api.route('/analytics/dashboard', methods=['GET'])
@require_auth
def get_analytics_dashboard():
    """Get marketing analytics dashboard"""
    try:
        # Get campaign counts
        total_campaigns = DatabaseUtils.count(MarketingCampaign)
        active_campaigns = DatabaseUtils.count(MarketingCampaign, {'campaign_status': 'active'})
        
        # Get email campaign metrics
        total_emails = DatabaseUtils.count(EmailCampaign)
        emails_sent = DatabaseUtils.sum(EmailCampaign, 'emails_sent')
        emails_opened = DatabaseUtils.sum(EmailCampaign, 'emails_opened')
        emails_clicked = DatabaseUtils.sum(EmailCampaign, 'emails_clicked')
        
        # Get social media metrics
        total_social = DatabaseUtils.count(SocialMediaCampaign)
        social_impressions = DatabaseUtils.sum(SocialMediaCampaign, 'impressions')
        social_engagements = DatabaseUtils.sum(SocialMediaCampaign, 'engagements')
        
        # Get content metrics
        total_content = DatabaseUtils.count(ContentMarketing)
        content_views = DatabaseUtils.sum(ContentMarketing, 'content_views')
        content_shares = DatabaseUtils.sum(ContentMarketing, 'content_shares')
        
        # Get event metrics
        total_events = DatabaseUtils.count(EventMarketing)
        event_registrations = DatabaseUtils.sum(EventMarketing, 'event_registrations')
        event_attendees = DatabaseUtils.sum(EventMarketing, 'event_attendees')
        
        return jsonify({
            'success': True,
            'data': {
                'overview': {
                    'total_campaigns': total_campaigns,
                    'active_campaigns': active_campaigns,
                    'total_emails': total_emails,
                    'total_social': total_social,
                    'total_content': total_content,
                    'total_events': total_events
                },
                'email_metrics': {
                    'emails_sent': emails_sent,
                    'emails_opened': emails_opened,
                    'emails_clicked': emails_clicked,
                    'open_rate': (emails_opened / emails_sent * 100) if emails_sent > 0 else 0,
                    'click_rate': (emails_clicked / emails_sent * 100) if emails_sent > 0 else 0
                },
                'social_metrics': {
                    'impressions': social_impressions,
                    'engagements': social_engagements,
                    'engagement_rate': (social_engagements / social_impressions * 100) if social_impressions > 0 else 0
                },
                'content_metrics': {
                    'content_views': content_views,
                    'content_shares': content_shares,
                    'share_rate': (content_shares / content_views * 100) if content_views > 0 else 0
                },
                'event_metrics': {
                    'registrations': event_registrations,
                    'attendees': event_attendees,
                    'attendance_rate': (event_attendees / event_registrations * 100) if event_registrations > 0 else 0
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Marketing Attribution API Endpoints
@marketing_automation_api.route('/attribution', methods=['GET'])
@require_auth
def get_attribution():
    """Get marketing attribution"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        attribution = DatabaseUtils.get_all(MarketingAttribution, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in attribution],
            'count': len(attribution)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@marketing_automation_api.route('/attribution', methods=['POST'])
@require_auth
def create_attribution():
    """Create new marketing attribution"""
    try:
        data = request.get_json()
        
        attribution = DatabaseUtils.create(MarketingAttribution, data)
        return jsonify({
            'success': True,
            'data': attribution.to_dict(),
            'message': 'Marketing attribution created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
