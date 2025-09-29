# Advanced CRM API Endpoints
# Enhanced CRM functionality with sales pipeline, marketing automation, and customer service

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import require_auth, get_current_user
from .advanced_models import (
    SalesPipeline, Opportunity, SalesActivity, MarketingCampaign, CampaignRecipient,
    SupportTicket, TicketComment, TicketAttachment, Quote, QuoteItem
)
from datetime import datetime, date
import json

# Create blueprint
advanced_crm_bp = Blueprint('advanced_crm', __name__, url_prefix='/advanced-crm')

# Sales Pipeline Endpoints
@advanced_crm_bp.route('/pipelines', methods=['GET'])
@require_auth
def get_sales_pipelines():
    """Get all sales pipelines"""
    try:
        pipelines = SalesPipeline.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [pipeline.to_dict() for pipeline in pipelines]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_crm_bp.route('/pipelines', methods=['POST'])
@require_auth
def create_sales_pipeline():
    """Create a new sales pipeline"""
    try:
        data = request.get_json()
        pipeline = SalesPipeline(
            pipeline_name=data['pipeline_name'],
            description=data.get('description'),
            stages=data.get('stages', []),
            stage_probabilities=data.get('stage_probabilities', {}),
            stage_durations=data.get('stage_durations', {}),
            is_active=data.get('is_active', True),
            is_default=data.get('is_default', False),
            company_id=get_current_user().company_id
        )
        db.session.add(pipeline)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': pipeline.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Enhanced Opportunities Endpoints
@advanced_crm_bp.route('/opportunities', methods=['GET'])
@require_auth
def get_opportunities():
    """Get all opportunities with advanced filtering"""
    try:
        query = Opportunity.query.filter_by(company_id=get_current_user().company_id)
        
        # Apply filters
        if request.args.get('stage'):
            query = query.filter_by(current_stage=request.args.get('stage'))
        if request.args.get('sales_rep_id'):
            query = query.filter_by(sales_rep_id=request.args.get('sales_rep_id'))
        if request.args.get('pipeline_id'):
            query = query.filter_by(pipeline_id=request.args.get('pipeline_id'))
        
        opportunities = query.all()
        return jsonify({
            'success': True,
            'data': [opp.to_dict() for opp in opportunities]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_crm_bp.route('/opportunities', methods=['POST'])
@require_auth
def create_opportunity():
    """Create a new opportunity"""
    try:
        data = request.get_json()
        opportunity = Opportunity(
            opportunity_name=data['opportunity_name'],
            description=data.get('description'),
            customer_id=data['customer_id'],
            expected_revenue=data.get('expected_revenue', 0.0),
            probability=data.get('probability', 0.0),
            expected_close_date=datetime.strptime(data['expected_close_date'], '%Y-%m-%d').date() if data.get('expected_close_date') else None,
            pipeline_id=data.get('pipeline_id'),
            current_stage=data.get('current_stage', 'Lead'),
            sales_rep_id=data.get('sales_rep_id'),
            sales_team=data.get('sales_team', []),
            lead_source=data.get('lead_source'),
            lead_score=data.get('lead_score', 0),
            lead_qualification=data.get('lead_qualification', {}),
            competitors=data.get('competitors', []),
            competitive_advantages=data.get('competitive_advantages'),
            company_id=get_current_user().company_id
        )
        
        # Calculate weighted revenue
        opportunity.weighted_revenue = opportunity.expected_revenue * (opportunity.probability / 100)
        
        db.session.add(opportunity)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': opportunity.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_crm_bp.route('/opportunities/<int:opportunity_id>/move-stage', methods=['PUT'])
@require_auth
def move_opportunity_stage(opportunity_id):
    """Move opportunity to next stage"""
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        data = request.get_json()
        new_stage = data.get('new_stage')
        
        if new_stage:
            opportunity.current_stage = new_stage
            if new_stage in ['Closed Won', 'Closed Lost']:
                opportunity.actual_close_date = date.today()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': opportunity.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'New stage is required'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Sales Activities Endpoints
@advanced_crm_bp.route('/activities', methods=['GET'])
@require_auth
def get_sales_activities():
    """Get all sales activities"""
    try:
        activities = SalesActivity.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [activity.to_dict() for activity in activities]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_crm_bp.route('/activities', methods=['POST'])
@require_auth
def create_sales_activity():
    """Create a new sales activity"""
    try:
        data = request.get_json()
        activity = SalesActivity(
            activity_type=data['activity_type'],
            subject=data['subject'],
            description=data.get('description'),
            activity_date=datetime.strptime(data['activity_date'], '%Y-%m-%dT%H:%M:%S') if data.get('activity_date') else datetime.utcnow(),
            duration=data.get('duration', 0),
            outcome=data.get('outcome'),
            next_action=data.get('next_action'),
            next_action_date=datetime.strptime(data['next_action_date'], '%Y-%m-%dT%H:%M:%S') if data.get('next_action_date') else None,
            opportunity_id=data.get('opportunity_id'),
            contact_id=data.get('contact_id'),
            company_id=get_current_user().company_id
        )
        db.session.add(activity)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': activity.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Marketing Campaign Endpoints
@advanced_crm_bp.route('/campaigns', methods=['GET'])
@require_auth
def get_marketing_campaigns():
    """Get all marketing campaigns"""
    try:
        campaigns = MarketingCampaign.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [campaign.to_dict() for campaign in campaigns]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_crm_bp.route('/campaigns', methods=['POST'])
@require_auth
def create_marketing_campaign():
    """Create a new marketing campaign"""
    try:
        data = request.get_json()
        campaign = MarketingCampaign(
            campaign_name=data['campaign_name'],
            description=data.get('description'),
            campaign_type=data['campaign_type'],
            target_audience=data.get('target_audience', {}),
            campaign_content=data.get('campaign_content', {}),
            schedule_config=data.get('schedule_config', {}),
            status=data.get('status', 'Draft'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%dT%H:%M:%S') if data.get('start_date') else None,
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%dT%H:%M:%S') if data.get('end_date') else None,
            company_id=get_current_user().company_id
        )
        db.session.add(campaign)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': campaign.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_crm_bp.route('/campaigns/<int:campaign_id>/launch', methods=['POST'])
@require_auth
def launch_campaign(campaign_id):
    """Launch a marketing campaign"""
    try:
        campaign = MarketingCampaign.query.get_or_404(campaign_id)
        campaign.status = 'Active'
        campaign.start_date = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Campaign launched successfully',
            'data': campaign.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Support Ticket Endpoints
@advanced_crm_bp.route('/tickets', methods=['GET'])
@require_auth
def get_support_tickets():
    """Get all support tickets"""
    try:
        query = SupportTicket.query.filter_by(company_id=get_current_user().company_id)
        
        # Apply filters
        if request.args.get('status'):
            query = query.filter_by(status=request.args.get('status'))
        if request.args.get('priority'):
            query = query.filter_by(priority=request.args.get('priority'))
        if request.args.get('assigned_to_id'):
            query = query.filter_by(assigned_to_id=request.args.get('assigned_to_id'))
        
        tickets = query.all()
        return jsonify({
            'success': True,
            'data': [ticket.to_dict() for ticket in tickets]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_crm_bp.route('/tickets', methods=['POST'])
@require_auth
def create_support_ticket():
    """Create a new support ticket"""
    try:
        data = request.get_json()
        
        # Generate ticket number
        ticket_number = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        ticket = SupportTicket(
            ticket_number=ticket_number,
            subject=data['subject'],
            description=data['description'],
            customer_id=data.get('customer_id'),
            contact_id=data.get('contact_id'),
            priority=data.get('priority', 'Medium'),
            status=data.get('status', 'Open'),
            category=data.get('category'),
            subcategory=data.get('subcategory'),
            assigned_to_id=data.get('assigned_to_id'),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%dT%H:%M:%S') if data.get('due_date') else None,
            company_id=get_current_user().company_id
        )
        db.session.add(ticket)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': ticket.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_crm_bp.route('/tickets/<int:ticket_id>/comments', methods=['POST'])
@require_auth
def add_ticket_comment(ticket_id):
    """Add a comment to a support ticket"""
    try:
        data = request.get_json()
        comment = TicketComment(
            comment_text=data['comment_text'],
            is_internal=data.get('is_internal', False),
            ticket_id=ticket_id,
            author_id=get_current_user().id,
            company_id=get_current_user().company_id
        )
        db.session.add(comment)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': comment.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Quote Endpoints
@advanced_crm_bp.route('/quotes', methods=['GET'])
@require_auth
def get_quotes():
    """Get all quotes"""
    try:
        quotes = Quote.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [quote.to_dict() for quote in quotes]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_crm_bp.route('/quotes', methods=['POST'])
@require_auth
def create_quote():
    """Create a new quote"""
    try:
        data = request.get_json()
        
        # Generate quote number
        quote_number = f"QUO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        quote = Quote(
            quote_number=quote_number,
            quote_name=data['quote_name'],
            description=data.get('description'),
            customer_id=data['customer_id'],
            opportunity_id=data.get('opportunity_id'),
            quote_date=datetime.strptime(data['quote_date'], '%Y-%m-%d').date() if data.get('quote_date') else date.today(),
            valid_until=datetime.strptime(data['valid_until'], '%Y-%m-%d').date() if data.get('valid_until') else None,
            status=data.get('status', 'Draft'),
            subtotal=data.get('subtotal', 0.0),
            tax_amount=data.get('tax_amount', 0.0),
            discount_amount=data.get('discount_amount', 0.0),
            total_amount=data.get('total_amount', 0.0),
            payment_terms=data.get('payment_terms'),
            delivery_terms=data.get('delivery_terms'),
            notes=data.get('notes'),
            company_id=get_current_user().company_id
        )
        db.session.add(quote)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': quote.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Analytics Endpoints
@advanced_crm_bp.route('/analytics/sales-funnel', methods=['GET'])
@require_auth
def get_sales_funnel_analytics():
    """Get sales funnel analytics"""
    try:
        # Get opportunities by stage
        opportunities = Opportunity.query.filter_by(company_id=get_current_user().company_id).all()
        
        funnel_data = {}
        for opp in opportunities:
            stage = opp.current_stage.value if opp.current_stage else 'Unknown'
            if stage not in funnel_data:
                funnel_data[stage] = {
                    'count': 0,
                    'total_value': 0.0,
                    'weighted_value': 0.0
                }
            funnel_data[stage]['count'] += 1
            funnel_data[stage]['total_value'] += opp.expected_revenue
            funnel_data[stage]['weighted_value'] += opp.weighted_revenue
        
        return jsonify({
            'success': True,
            'data': funnel_data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_crm_bp.route('/analytics/campaign-performance', methods=['GET'])
@require_auth
def get_campaign_performance():
    """Get marketing campaign performance analytics"""
    try:
        campaigns = MarketingCampaign.query.filter_by(company_id=get_current_user().company_id).all()
        
        performance_data = []
        for campaign in campaigns:
            performance_data.append({
                'campaign_id': campaign.id,
                'campaign_name': campaign.campaign_name,
                'campaign_type': campaign.campaign_type,
                'status': campaign.status.value if campaign.status else None,
                'total_sent': campaign.total_sent,
                'total_delivered': campaign.total_delivered,
                'total_opened': campaign.total_opened,
                'total_clicked': campaign.total_clicked,
                'total_converted': campaign.total_converted,
                'delivery_rate': (campaign.total_delivered / campaign.total_sent * 100) if campaign.total_sent > 0 else 0,
                'open_rate': (campaign.total_opened / campaign.total_delivered * 100) if campaign.total_delivered > 0 else 0,
                'click_rate': (campaign.total_clicked / campaign.total_opened * 100) if campaign.total_opened > 0 else 0,
                'conversion_rate': (campaign.total_converted / campaign.total_clicked * 100) if campaign.total_clicked > 0 else 0
            })
        
        return jsonify({
            'success': True,
            'data': performance_data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
