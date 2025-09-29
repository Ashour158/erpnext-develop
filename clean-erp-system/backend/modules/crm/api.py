# CRM API - Customer Relationship Management
# Complete CRM API without Frappe dependencies

from flask import Blueprint, request, jsonify
from core.database import DatabaseUtils
from core.auth import require_auth, get_current_user
from .models import Customer, Contact, Lead, Opportunity, Account
import uuid
from datetime import datetime

# Create CRM API blueprint
crm_api = Blueprint('crm_api', __name__)

# Customer API Endpoints
@crm_api.route('/customers', methods=['GET'])
@require_auth
def get_customers():
    """Get all customers"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        customers = DatabaseUtils.get_all(Customer, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [customer.to_dict() for customer in customers],
            'count': len(customers)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@crm_api.route('/customers', methods=['POST'])
@require_auth
def create_customer():
    """Create new customer"""
    try:
        data = request.get_json()
        
        # Generate customer code if not provided
        if 'customer_code' not in data:
            data['customer_code'] = f"CUST-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        customer = DatabaseUtils.create(Customer, data)
        return jsonify({
            'success': True,
            'data': customer.to_dict(),
            'message': 'Customer created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@crm_api.route('/customers/<int:customer_id>', methods=['GET'])
@require_auth
def get_customer(customer_id):
    """Get customer by ID"""
    try:
        customer = DatabaseUtils.get_by_id(Customer, customer_id)
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
        
        return jsonify({
            'success': True,
            'data': customer.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@crm_api.route('/customers/<int:customer_id>', methods=['PUT'])
@require_auth
def update_customer(customer_id):
    """Update customer"""
    try:
        data = request.get_json()
        
        # Set updated by
        current_user = get_current_user()
        if current_user:
            data['updated_by'] = current_user.username
        
        customer = DatabaseUtils.update(Customer, customer_id, data)
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
        
        return jsonify({
            'success': True,
            'data': customer.to_dict(),
            'message': 'Customer updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@crm_api.route('/customers/<int:customer_id>', methods=['DELETE'])
@require_auth
def delete_customer(customer_id):
    """Delete customer"""
    try:
        customer = DatabaseUtils.delete(Customer, customer_id)
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Customer deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Contact API Endpoints
@crm_api.route('/contacts', methods=['GET'])
@require_auth
def get_contacts():
    """Get all contacts"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        contacts = DatabaseUtils.get_all(Contact, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [contact.to_dict() for contact in contacts],
            'count': len(contacts)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@crm_api.route('/contacts', methods=['POST'])
@require_auth
def create_contact():
    """Create new contact"""
    try:
        data = request.get_json()
        
        # Generate contact code if not provided
        if 'contact_code' not in data:
            data['contact_code'] = f"CON-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        contact = DatabaseUtils.create(Contact, data)
        return jsonify({
            'success': True,
            'data': contact.to_dict(),
            'message': 'Contact created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Lead API Endpoints
@crm_api.route('/leads', methods=['GET'])
@require_auth
def get_leads():
    """Get all leads"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        leads = DatabaseUtils.get_all(Lead, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [lead.to_dict() for lead in leads],
            'count': len(leads)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@crm_api.route('/leads', methods=['POST'])
@require_auth
def create_lead():
    """Create new lead"""
    try:
        data = request.get_json()
        
        # Generate lead code if not provided
        if 'lead_code' not in data:
            data['lead_code'] = f"LEAD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        lead = DatabaseUtils.create(Lead, data)
        return jsonify({
            'success': True,
            'data': lead.to_dict(),
            'message': 'Lead created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Opportunity API Endpoints
@crm_api.route('/opportunities', methods=['GET'])
@require_auth
def get_opportunities():
    """Get all opportunities"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        opportunities = DatabaseUtils.get_all(Opportunity, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [opportunity.to_dict() for opportunity in opportunities],
            'count': len(opportunities)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@crm_api.route('/opportunities', methods=['POST'])
@require_auth
def create_opportunity():
    """Create new opportunity"""
    try:
        data = request.get_json()
        
        # Generate opportunity code if not provided
        if 'opportunity_code' not in data:
            data['opportunity_code'] = f"OPP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        opportunity = DatabaseUtils.create(Opportunity, data)
        return jsonify({
            'success': True,
            'data': opportunity.to_dict(),
            'message': 'Opportunity created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Account API Endpoints
@crm_api.route('/accounts', methods=['GET'])
@require_auth
def get_accounts():
    """Get all accounts"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        accounts = DatabaseUtils.get_all(Account, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [account.to_dict() for account in accounts],
            'count': len(accounts)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@crm_api.route('/accounts', methods=['POST'])
@require_auth
def create_account():
    """Create new account"""
    try:
        data = request.get_json()
        
        # Generate account code if not provided
        if 'account_code' not in data:
            data['account_code'] = f"ACC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        account = DatabaseUtils.create(Account, data)
        return jsonify({
            'success': True,
            'data': account.to_dict(),
            'message': 'Account created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# CRM Analytics Endpoints
@crm_api.route('/analytics/dashboard', methods=['GET'])
@require_auth
def get_crm_dashboard():
    """Get CRM dashboard analytics"""
    try:
        # Get counts
        total_customers = DatabaseUtils.count(Customer)
        total_contacts = DatabaseUtils.count(Contact)
        total_leads = DatabaseUtils.count(Lead)
        total_opportunities = DatabaseUtils.count(Opportunity)
        
        # Get active customers
        active_customers = DatabaseUtils.count(Customer, {'status': 'Active'})
        
        # Get leads by status
        new_leads = DatabaseUtils.count(Lead, {'lead_status': 'New'})
        qualified_leads = DatabaseUtils.count(Lead, {'lead_status': 'Qualified'})
        
        # Get opportunities by stage
        prospecting_opps = DatabaseUtils.count(Opportunity, {'stage': 'Prospecting'})
        proposal_opps = DatabaseUtils.count(Opportunity, {'stage': 'Proposal'})
        closed_won_opps = DatabaseUtils.count(Opportunity, {'stage': 'Closed Won'})
        
        return jsonify({
            'success': True,
            'data': {
                'overview': {
                    'total_customers': total_customers,
                    'active_customers': active_customers,
                    'total_contacts': total_contacts,
                    'total_leads': total_leads,
                    'total_opportunities': total_opportunities
                },
                'leads': {
                    'new_leads': new_leads,
                    'qualified_leads': qualified_leads
                },
                'opportunities': {
                    'prospecting': prospecting_opps,
                    'proposal': proposal_opps,
                    'closed_won': closed_won_opps
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
