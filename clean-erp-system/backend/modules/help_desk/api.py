# Help Desk API
# Comprehensive customer service and support API

from flask import Blueprint, request, jsonify
from core.database import DatabaseUtils
from core.auth import require_auth, get_current_user
from .models import (
    SupportTicket, TicketComment, TicketActivity, KnowledgeBase, FAQ,
    CustomerFeedback, ServiceLevelAgreement, SupportTeam, SupportAnalytics
)
import uuid
from datetime import datetime

# Create Help Desk API blueprint
help_desk_api = Blueprint('help_desk_api', __name__)

# Support Ticket API Endpoints
@help_desk_api.route('/tickets', methods=['GET'])
@require_auth
def get_tickets():
    """Get all support tickets"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        tickets = DatabaseUtils.get_all(SupportTicket, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [ticket.to_dict() for ticket in tickets],
            'count': len(tickets)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_desk_api.route('/tickets', methods=['POST'])
@require_auth
def create_ticket():
    """Create new support ticket"""
    try:
        data = request.get_json()
        
        # Generate ticket number if not provided
        if 'ticket_number' not in data:
            data['ticket_number'] = f"TKT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        ticket = DatabaseUtils.create(SupportTicket, data)
        return jsonify({
            'success': True,
            'data': ticket.to_dict(),
            'message': 'Support ticket created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_desk_api.route('/tickets/<int:ticket_id>', methods=['GET'])
@require_auth
def get_ticket(ticket_id):
    """Get ticket by ID"""
    try:
        ticket = DatabaseUtils.get_by_id(SupportTicket, ticket_id)
        if not ticket:
            return jsonify({'success': False, 'error': 'Ticket not found'}), 404
        
        return jsonify({
            'success': True,
            'data': ticket.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_desk_api.route('/tickets/<int:ticket_id>', methods=['PUT'])
@require_auth
def update_ticket(ticket_id):
    """Update ticket"""
    try:
        data = request.get_json()
        
        ticket = DatabaseUtils.update(SupportTicket, ticket_id, data)
        if not ticket:
            return jsonify({'success': False, 'error': 'Ticket not found'}), 404
        
        return jsonify({
            'success': True,
            'data': ticket.to_dict(),
            'message': 'Ticket updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_desk_api.route('/tickets/<int:ticket_id>', methods=['DELETE'])
@require_auth
def delete_ticket(ticket_id):
    """Delete ticket"""
    try:
        ticket = DatabaseUtils.delete(SupportTicket, ticket_id)
        if not ticket:
            return jsonify({'success': False, 'error': 'Ticket not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Ticket deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Ticket Comments API Endpoints
@help_desk_api.route('/tickets/<int:ticket_id>/comments', methods=['GET'])
@require_auth
def get_ticket_comments(ticket_id):
    """Get ticket comments"""
    try:
        filters = request.args.to_dict()
        filters['ticket_id'] = ticket_id
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        comments = DatabaseUtils.get_all(TicketComment, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [comment.to_dict() for comment in comments],
            'count': len(comments)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_desk_api.route('/tickets/<int:ticket_id>/comments', methods=['POST'])
@require_auth
def create_ticket_comment(ticket_id):
    """Create ticket comment"""
    try:
        data = request.get_json()
        data['ticket_id'] = ticket_id
        
        # Set user
        current_user = get_current_user()
        if current_user:
            data['user_id'] = current_user.id
        
        comment = DatabaseUtils.create(TicketComment, data)
        return jsonify({
            'success': True,
            'data': comment.to_dict(),
            'message': 'Comment added successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Knowledge Base API Endpoints
@help_desk_api.route('/knowledge-base', methods=['GET'])
@require_auth
def get_knowledge_base():
    """Get knowledge base articles"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        articles = DatabaseUtils.get_all(KnowledgeBase, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [article.to_dict() for article in articles],
            'count': len(articles)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_desk_api.route('/knowledge-base', methods=['POST'])
@require_auth
def create_knowledge_base_article():
    """Create knowledge base article"""
    try:
        data = request.get_json()
        
        # Set author
        current_user = get_current_user()
        if current_user:
            data['article_author'] = current_user.id
        
        article = DatabaseUtils.create(KnowledgeBase, data)
        return jsonify({
            'success': True,
            'data': article.to_dict(),
            'message': 'Article created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_desk_api.route('/knowledge-base/<int:article_id>', methods=['GET'])
@require_auth
def get_knowledge_base_article(article_id):
    """Get knowledge base article by ID"""
    try:
        article = DatabaseUtils.get_by_id(KnowledgeBase, article_id)
        if not article:
            return jsonify({'success': False, 'error': 'Article not found'}), 404
        
        return jsonify({
            'success': True,
            'data': article.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_desk_api.route('/knowledge-base/<int:article_id>', methods=['PUT'])
@require_auth
def update_knowledge_base_article(article_id):
    """Update knowledge base article"""
    try:
        data = request.get_json()
        
        # Set editor
        current_user = get_current_user()
        if current_user:
            data['article_editor'] = current_user.id
        
        article = DatabaseUtils.update(KnowledgeBase, article_id, data)
        if not article:
            return jsonify({'success': False, 'error': 'Article not found'}), 404
        
        return jsonify({
            'success': True,
            'data': article.to_dict(),
            'message': 'Article updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# FAQ API Endpoints
@help_desk_api.route('/faqs', methods=['GET'])
@require_auth
def get_faqs():
    """Get FAQs"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        faqs = DatabaseUtils.get_all(FAQ, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [faq.to_dict() for faq in faqs],
            'count': len(faqs)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_desk_api.route('/faqs', methods=['POST'])
@require_auth
def create_faq():
    """Create FAQ"""
    try:
        data = request.get_json()
        
        # Set author
        current_user = get_current_user()
        if current_user:
            data['faq_author'] = current_user.id
        
        faq = DatabaseUtils.create(FAQ, data)
        return jsonify({
            'success': True,
            'data': faq.to_dict(),
            'message': 'FAQ created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Customer Feedback API Endpoints
@help_desk_api.route('/feedback', methods=['GET'])
@require_auth
def get_customer_feedback():
    """Get customer feedback"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        feedback = DatabaseUtils.get_all(CustomerFeedback, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in feedback],
            'count': len(feedback)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_desk_api.route('/feedback', methods=['POST'])
@require_auth
def create_customer_feedback():
    """Create customer feedback"""
    try:
        data = request.get_json()
        
        feedback = DatabaseUtils.create(CustomerFeedback, data)
        return jsonify({
            'success': True,
            'data': feedback.to_dict(),
            'message': 'Feedback submitted successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Service Level Agreement API Endpoints
@help_desk_api.route('/slas', methods=['GET'])
@require_auth
def get_slas():
    """Get service level agreements"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        slas = DatabaseUtils.get_all(ServiceLevelAgreement, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [sla.to_dict() for sla in slas],
            'count': len(slas)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_desk_api.route('/slas', methods=['POST'])
@require_auth
def create_sla():
    """Create service level agreement"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.id
        
        sla = DatabaseUtils.create(ServiceLevelAgreement, data)
        return jsonify({
            'success': True,
            'data': sla.to_dict(),
            'message': 'SLA created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Support Team API Endpoints
@help_desk_api.route('/teams', methods=['GET'])
@require_auth
def get_support_teams():
    """Get support teams"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        teams = DatabaseUtils.get_all(SupportTeam, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [team.to_dict() for team in teams],
            'count': len(teams)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_desk_api.route('/teams', methods=['POST'])
@require_auth
def create_support_team():
    """Create support team"""
    try:
        data = request.get_json()
        
        team = DatabaseUtils.create(SupportTeam, data)
        return jsonify({
            'success': True,
            'data': team.to_dict(),
            'message': 'Support team created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Support Analytics API Endpoints
@help_desk_api.route('/analytics', methods=['GET'])
@require_auth
def get_support_analytics():
    """Get support analytics"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        analytics = DatabaseUtils.get_all(SupportAnalytics, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in analytics],
            'count': len(analytics)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_desk_api.route('/analytics/dashboard', methods=['GET'])
@require_auth
def get_support_dashboard():
    """Get support dashboard analytics"""
    try:
        # Get ticket counts
        total_tickets = DatabaseUtils.count(SupportTicket)
        open_tickets = DatabaseUtils.count(SupportTicket, {'ticket_status': 'open'})
        in_progress_tickets = DatabaseUtils.count(SupportTicket, {'ticket_status': 'in_progress'})
        resolved_tickets = DatabaseUtils.count(SupportTicket, {'ticket_status': 'resolved'})
        closed_tickets = DatabaseUtils.count(SupportTicket, {'ticket_status': 'closed'})
        
        # Get priority distribution
        low_priority = DatabaseUtils.count(SupportTicket, {'ticket_priority': 'low'})
        medium_priority = DatabaseUtils.count(SupportTicket, {'ticket_priority': 'medium'})
        high_priority = DatabaseUtils.count(SupportTicket, {'ticket_priority': 'high'})
        urgent_priority = DatabaseUtils.count(SupportTicket, {'ticket_priority': 'urgent'})
        critical_priority = DatabaseUtils.count(SupportTicket, {'ticket_priority': 'critical'})
        
        # Get team performance
        total_teams = DatabaseUtils.count(SupportTeam)
        active_teams = DatabaseUtils.count(SupportTeam, {'team_status': 'active'})
        
        # Get knowledge base metrics
        total_articles = DatabaseUtils.count(KnowledgeBase)
        published_articles = DatabaseUtils.count(KnowledgeBase, {'article_status': 'published'})
        total_faqs = DatabaseUtils.count(FAQ)
        active_faqs = DatabaseUtils.count(FAQ, {'faq_status': 'active'})
        
        # Get feedback metrics
        total_feedback = DatabaseUtils.count(CustomerFeedback)
        positive_feedback = DatabaseUtils.count(CustomerFeedback, {'feedback_rating': 'satisfied'})
        negative_feedback = DatabaseUtils.count(CustomerFeedback, {'feedback_rating': 'dissatisfied'})
        
        return jsonify({
            'success': True,
            'data': {
                'ticket_overview': {
                    'total_tickets': total_tickets,
                    'open_tickets': open_tickets,
                    'in_progress_tickets': in_progress_tickets,
                    'resolved_tickets': resolved_tickets,
                    'closed_tickets': closed_tickets
                },
                'priority_distribution': {
                    'low_priority': low_priority,
                    'medium_priority': medium_priority,
                    'high_priority': high_priority,
                    'urgent_priority': urgent_priority,
                    'critical_priority': critical_priority
                },
                'team_performance': {
                    'total_teams': total_teams,
                    'active_teams': active_teams
                },
                'knowledge_base': {
                    'total_articles': total_articles,
                    'published_articles': published_articles,
                    'total_faqs': total_faqs,
                    'active_faqs': active_faqs
                },
                'customer_feedback': {
                    'total_feedback': total_feedback,
                    'positive_feedback': positive_feedback,
                    'negative_feedback': negative_feedback,
                    'satisfaction_rate': (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Ticket Assignment API
@help_desk_api.route('/tickets/<int:ticket_id>/assign', methods=['POST'])
@require_auth
def assign_ticket(ticket_id):
    """Assign ticket to user or team"""
    try:
        data = request.get_json()
        
        # Update ticket assignment
        ticket = DatabaseUtils.update(SupportTicket, ticket_id, data)
        if not ticket:
            return jsonify({'success': False, 'error': 'Ticket not found'}), 404
        
        return jsonify({
            'success': True,
            'data': ticket.to_dict(),
            'message': 'Ticket assigned successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Ticket Status Update API
@help_desk_api.route('/tickets/<int:ticket_id>/status', methods=['POST'])
@require_auth
def update_ticket_status(ticket_id):
    """Update ticket status"""
    try:
        data = request.get_json()
        
        # Update ticket status
        ticket = DatabaseUtils.update(SupportTicket, ticket_id, data)
        if not ticket:
            return jsonify({'success': False, 'error': 'Ticket not found'}), 404
        
        return jsonify({
            'success': True,
            'data': ticket.to_dict(),
            'message': 'Ticket status updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Ticket Resolution API
@help_desk_api.route('/tickets/<int:ticket_id>/resolve', methods=['POST'])
@require_auth
def resolve_ticket(ticket_id):
    """Resolve ticket"""
    try:
        data = request.get_json()
        data['ticket_status'] = 'resolved'
        data['resolved_at'] = datetime.utcnow()
        
        # Set resolved by
        current_user = get_current_user()
        if current_user:
            data['resolved_by'] = current_user.id
        
        # Update ticket
        ticket = DatabaseUtils.update(SupportTicket, ticket_id, data)
        if not ticket:
            return jsonify({'success': False, 'error': 'Ticket not found'}), 404
        
        return jsonify({
            'success': True,
            'data': ticket.to_dict(),
            'message': 'Ticket resolved successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
