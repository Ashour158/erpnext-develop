# Enhanced CRM Core API - Core Submodules
# Complete CRM API matching enterprise CRM requirements

from flask import Blueprint, request, jsonify
from core.database import DatabaseUtils
from core.auth import require_auth, get_current_user
from .enhanced_core_models import (
    Lead, Account, Contact, Deal, SalesForecast, TerritoryForecast,
    Macro, Feed, SalesSignal, Document, Activity, Reminder,
    RecurringActivity, CalendarBooking, Currency, SocialIntegration,
    ScoringRule, MultipleScoringRule
)
import uuid
from datetime import datetime

# Create Enhanced CRM API blueprint
enhanced_crm_api = Blueprint('enhanced_crm_api', __name__)

# =============================================================================
# 1. LEADS API - Lead capture, management, and qualification
# =============================================================================

@enhanced_crm_api.route('/leads', methods=['GET'])
@require_auth
def get_leads():
    """Get all leads with filtering and pagination"""
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

@enhanced_crm_api.route('/leads', methods=['POST'])
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

@enhanced_crm_api.route('/leads/<int:lead_id>', methods=['GET'])
@require_auth
def get_lead(lead_id):
    """Get lead by ID"""
    try:
        lead = DatabaseUtils.get_by_id(Lead, lead_id)
        if not lead:
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        return jsonify({
            'success': True,
            'data': lead.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/leads/<int:lead_id>', methods=['PUT'])
@require_auth
def update_lead(lead_id):
    """Update lead"""
    try:
        data = request.get_json()
        
        # Set updated by
        current_user = get_current_user()
        if current_user:
            data['updated_by'] = current_user.username
        
        lead = DatabaseUtils.update(Lead, lead_id, data)
        if not lead:
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        return jsonify({
            'success': True,
            'data': lead.to_dict(),
            'message': 'Lead updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/leads/<int:lead_id>', methods=['DELETE'])
@require_auth
def delete_lead(lead_id):
    """Delete lead"""
    try:
        success = DatabaseUtils.delete(Lead, lead_id)
        if not success:
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Lead deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/leads/<int:lead_id>/qualify', methods=['POST'])
@require_auth
def qualify_lead(lead_id):
    """Qualify lead and convert to opportunity"""
    try:
        data = request.get_json()
        lead = DatabaseUtils.get_by_id(Lead, lead_id)
        if not lead:
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        # Update lead status to qualified
        lead.lead_status = 'Qualified'
        lead.lead_score = data.get('lead_score', lead.lead_score)
        lead.probability = data.get('probability', lead.probability)
        
        # Create opportunity if specified
        if data.get('create_opportunity', False):
            opportunity_data = {
                'deal_name': f"Opportunity from {lead.full_name}",
                'deal_value': lead.estimated_value,
                'probability': lead.probability,
                'expected_close_date': data.get('expected_close_date'),
                'lead_id': lead_id
            }
            opportunity = DatabaseUtils.create(Deal, opportunity_data)
            return jsonify({
                'success': True,
                'data': lead.to_dict(),
                'opportunity': opportunity.to_dict(),
                'message': 'Lead qualified and opportunity created'
            })
        
        return jsonify({
            'success': True,
            'data': lead.to_dict(),
            'message': 'Lead qualified successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 2. ACCOUNTS API - Company/organization management
# =============================================================================

@enhanced_crm_api.route('/accounts', methods=['GET'])
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

@enhanced_crm_api.route('/accounts', methods=['POST'])
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

@enhanced_crm_api.route('/accounts/<int:account_id>', methods=['GET'])
@require_auth
def get_account(account_id):
    """Get account by ID"""
    try:
        account = DatabaseUtils.get_by_id(Account, account_id)
        if not account:
            return jsonify({'success': False, 'error': 'Account not found'}), 404
        
        return jsonify({
            'success': True,
            'data': account.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/accounts/<int:account_id>', methods=['PUT'])
@require_auth
def update_account(account_id):
    """Update account"""
    try:
        data = request.get_json()
        
        # Set updated by
        current_user = get_current_user()
        if current_user:
            data['updated_by'] = current_user.username
        
        account = DatabaseUtils.update(Account, account_id, data)
        if not account:
            return jsonify({'success': False, 'error': 'Account not found'}), 404
        
        return jsonify({
            'success': True,
            'data': account.to_dict(),
            'message': 'Account updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/accounts/<int:account_id>', methods=['DELETE'])
@require_auth
def delete_account(account_id):
    """Delete account"""
    try:
        success = DatabaseUtils.delete(Account, account_id)
        if not success:
            return jsonify({'success': False, 'error': 'Account not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 3. CONTACTS API - Individual contact management
# =============================================================================

@enhanced_crm_api.route('/contacts', methods=['GET'])
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

@enhanced_crm_api.route('/contacts', methods=['POST'])
@require_auth
def create_contact():
    """Create new contact"""
    try:
        data = request.get_json()
        
        # Generate contact code if not provided
        if 'contact_code' not in data:
            data['contact_code'] = f"CONT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
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

@enhanced_crm_api.route('/contacts/<int:contact_id>', methods=['GET'])
@require_auth
def get_contact(contact_id):
    """Get contact by ID"""
    try:
        contact = DatabaseUtils.get_by_id(Contact, contact_id)
        if not contact:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        return jsonify({
            'success': True,
            'data': contact.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/contacts/<int:contact_id>', methods=['PUT'])
@require_auth
def update_contact(contact_id):
    """Update contact"""
    try:
        data = request.get_json()
        
        # Set updated by
        current_user = get_current_user()
        if current_user:
            data['updated_by'] = current_user.username
        
        contact = DatabaseUtils.update(Contact, contact_id, data)
        if not contact:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        return jsonify({
            'success': True,
            'data': contact.to_dict(),
            'message': 'Contact updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/contacts/<int:contact_id>', methods=['DELETE'])
@require_auth
def delete_contact(contact_id):
    """Delete contact"""
    try:
        success = DatabaseUtils.delete(Contact, contact_id)
        if not success:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Contact deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 4. DEALS API - Opportunity and pipeline management
# =============================================================================

@enhanced_crm_api.route('/deals', methods=['GET'])
@require_auth
def get_deals():
    """Get all deals"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        deals = DatabaseUtils.get_all(Deal, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [deal.to_dict() for deal in deals],
            'count': len(deals)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/deals', methods=['POST'])
@require_auth
def create_deal():
    """Create new deal"""
    try:
        data = request.get_json()
        
        # Generate deal code if not provided
        if 'deal_code' not in data:
            data['deal_code'] = f"DEAL-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        deal = DatabaseUtils.create(Deal, data)
        return jsonify({
            'success': True,
            'data': deal.to_dict(),
            'message': 'Deal created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/deals/<int:deal_id>', methods=['GET'])
@require_auth
def get_deal(deal_id):
    """Get deal by ID"""
    try:
        deal = DatabaseUtils.get_by_id(Deal, deal_id)
        if not deal:
            return jsonify({'success': False, 'error': 'Deal not found'}), 404
        
        return jsonify({
            'success': True,
            'data': deal.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/deals/<int:deal_id>', methods=['PUT'])
@require_auth
def update_deal(deal_id):
    """Update deal"""
    try:
        data = request.get_json()
        
        # Set updated by
        current_user = get_current_user()
        if current_user:
            data['updated_by'] = current_user.username
        
        deal = DatabaseUtils.update(Deal, deal_id, data)
        if not deal:
            return jsonify({'success': False, 'error': 'Deal not found'}), 404
        
        return jsonify({
            'success': True,
            'data': deal.to_dict(),
            'message': 'Deal updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/deals/<int:deal_id>', methods=['DELETE'])
@require_auth
def delete_deal(deal_id):
    """Delete deal"""
    try:
        success = DatabaseUtils.delete(Deal, deal_id)
        if not success:
            return jsonify({'success': False, 'error': 'Deal not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Deal deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/deals/<int:deal_id>/close', methods=['POST'])
@require_auth
def close_deal(deal_id):
    """Close deal (won or lost)"""
    try:
        data = request.get_json()
        deal = DatabaseUtils.get_by_id(Deal, deal_id)
        if not deal:
            return jsonify({'success': False, 'error': 'Deal not found'}), 404
        
        # Update deal status
        deal.deal_stage = data.get('deal_stage', 'Closed Won')
        deal.actual_close_date = datetime.now()
        deal.probability = 100.0 if deal.deal_stage == 'Closed Won' else 0.0
        
        return jsonify({
            'success': True,
            'data': deal.to_dict(),
            'message': f'Deal closed as {deal.deal_stage}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 5. SALES FORECASTING API - Revenue prediction and planning
# =============================================================================

@enhanced_crm_api.route('/sales-forecasts', methods=['GET'])
@require_auth
def get_sales_forecasts():
    """Get all sales forecasts"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        forecasts = DatabaseUtils.get_all(SalesForecast, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [forecast.to_dict() for forecast in forecasts],
            'count': len(forecasts)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/sales-forecasts', methods=['POST'])
@require_auth
def create_sales_forecast():
    """Create new sales forecast"""
    try:
        data = request.get_json()
        
        # Generate forecast code if not provided
        if 'forecast_code' not in data:
            data['forecast_code'] = f"FC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        forecast = DatabaseUtils.create(SalesForecast, data)
        return jsonify({
            'success': True,
            'data': forecast.to_dict(),
            'message': 'Sales forecast created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 6. TERRITORY FORECASTING API - Geographic sales planning
# =============================================================================

@enhanced_crm_api.route('/territory-forecasts', methods=['GET'])
@require_auth
def get_territory_forecasts():
    """Get all territory forecasts"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        forecasts = DatabaseUtils.get_all(TerritoryForecast, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [forecast.to_dict() for forecast in forecasts],
            'count': len(forecasts)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/territory-forecasts', methods=['POST'])
@require_auth
def create_territory_forecast():
    """Create new territory forecast"""
    try:
        data = request.get_json()
        
        # Generate territory code if not provided
        if 'territory_code' not in data:
            data['territory_code'] = f"TERR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        forecast = DatabaseUtils.create(TerritoryForecast, data)
        return jsonify({
            'success': True,
            'data': forecast.to_dict(),
            'message': 'Territory forecast created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 7. MACROS API - Automated action sequences
# =============================================================================

@enhanced_crm_api.route('/macros', methods=['GET'])
@require_auth
def get_macros():
    """Get all macros"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        macros = DatabaseUtils.get_all(Macro, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [macro.to_dict() for macro in macros],
            'count': len(macros)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/macros', methods=['POST'])
@require_auth
def create_macro():
    """Create new macro"""
    try:
        data = request.get_json()
        
        # Generate macro code if not provided
        if 'macro_code' not in data:
            data['macro_code'] = f"MACRO-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        macro = DatabaseUtils.create(Macro, data)
        return jsonify({
            'success': True,
            'data': macro.to_dict(),
            'message': 'Macro created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/macros/<int:macro_id>/execute', methods=['POST'])
@require_auth
def execute_macro(macro_id):
    """Execute macro"""
    try:
        macro = DatabaseUtils.get_by_id(Macro, macro_id)
        if not macro:
            return jsonify({'success': False, 'error': 'Macro not found'}), 404
        
        if not macro.is_active:
            return jsonify({'success': False, 'error': 'Macro is not active'}), 400
        
        # Execute macro actions
        # This would contain the actual macro execution logic
        macro.execution_count += 1
        macro.last_executed = datetime.now()
        
        return jsonify({
            'success': True,
            'data': macro.to_dict(),
            'message': 'Macro executed successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 8. FEEDS API - Activity streams and updates
# =============================================================================

@enhanced_crm_api.route('/feeds', methods=['GET'])
@require_auth
def get_feeds():
    """Get all feeds"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        feeds = DatabaseUtils.get_all(Feed, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [feed.to_dict() for feed in feeds],
            'count': len(feeds)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/feeds', methods=['POST'])
@require_auth
def create_feed():
    """Create new feed"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        feed = DatabaseUtils.create(Feed, data)
        return jsonify({
            'success': True,
            'data': feed.to_dict(),
            'message': 'Feed created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 9. SALES SIGNALS API - Intelligent sales insights
# =============================================================================

@enhanced_crm_api.route('/sales-signals', methods=['GET'])
@require_auth
def get_sales_signals():
    """Get all sales signals"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        signals = DatabaseUtils.get_all(SalesSignal, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [signal.to_dict() for signal in signals],
            'count': len(signals)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/sales-signals', methods=['POST'])
@require_auth
def create_sales_signal():
    """Create new sales signal"""
    try:
        data = request.get_json()
        
        # Generate signal code if not provided
        if 'signal_code' not in data:
            data['signal_code'] = f"SIG-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        signal = DatabaseUtils.create(SalesSignal, data)
        return jsonify({
            'success': True,
            'data': signal.to_dict(),
            'message': 'Sales signal created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 10. DOCUMENTS API - Sales document management
# =============================================================================

@enhanced_crm_api.route('/documents', methods=['GET'])
@require_auth
def get_documents():
    """Get all documents"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        documents = DatabaseUtils.get_all(Document, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [document.to_dict() for document in documents],
            'count': len(documents)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/documents', methods=['POST'])
@require_auth
def create_document():
    """Create new document"""
    try:
        data = request.get_json()
        
        # Generate document code if not provided
        if 'document_code' not in data:
            data['document_code'] = f"DOC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        document = DatabaseUtils.create(Document, data)
        return jsonify({
            'success': True,
            'data': document.to_dict(),
            'message': 'Document created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 11. ACTIVITIES API - Task and event management
# =============================================================================

@enhanced_crm_api.route('/activities', methods=['GET'])
@require_auth
def get_activities():
    """Get all activities"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        activities = DatabaseUtils.get_all(Activity, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [activity.to_dict() for activity in activities],
            'count': len(activities)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/activities', methods=['POST'])
@require_auth
def create_activity():
    """Create new activity"""
    try:
        data = request.get_json()
        
        # Generate activity code if not provided
        if 'activity_code' not in data:
            data['activity_code'] = f"ACT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        activity = DatabaseUtils.create(Activity, data)
        return jsonify({
            'success': True,
            'data': activity.to_dict(),
            'message': 'Activity created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 12. REMINDERS API - Automated notifications
# =============================================================================

@enhanced_crm_api.route('/reminders', methods=['GET'])
@require_auth
def get_reminders():
    """Get all reminders"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        reminders = DatabaseUtils.get_all(Reminder, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [reminder.to_dict() for reminder in reminders],
            'count': len(reminders)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/reminders', methods=['POST'])
@require_auth
def create_reminder():
    """Create new reminder"""
    try:
        data = request.get_json()
        
        # Generate reminder code if not provided
        if 'reminder_code' not in data:
            data['reminder_code'] = f"REM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        reminder = DatabaseUtils.create(Reminder, data)
        return jsonify({
            'success': True,
            'data': reminder.to_dict(),
            'message': 'Reminder created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 13. RECURRING ACTIVITIES API - Scheduled recurring tasks
# =============================================================================

@enhanced_crm_api.route('/recurring-activities', methods=['GET'])
@require_auth
def get_recurring_activities():
    """Get all recurring activities"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        activities = DatabaseUtils.get_all(RecurringActivity, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [activity.to_dict() for activity in activities],
            'count': len(activities)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/recurring-activities', methods=['POST'])
@require_auth
def create_recurring_activity():
    """Create new recurring activity"""
    try:
        data = request.get_json()
        
        # Generate recurring activity code if not provided
        if 'recurring_activity_code' not in data:
            data['recurring_activity_code'] = f"REC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        activity = DatabaseUtils.create(RecurringActivity, data)
        return jsonify({
            'success': True,
            'data': activity.to_dict(),
            'message': 'Recurring activity created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 14. CALENDAR BOOKING API - Meeting scheduling
# =============================================================================

@enhanced_crm_api.route('/calendar-bookings', methods=['GET'])
@require_auth
def get_calendar_bookings():
    """Get all calendar bookings"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        bookings = DatabaseUtils.get_all(CalendarBooking, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [booking.to_dict() for booking in bookings],
            'count': len(bookings)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/calendar-bookings', methods=['POST'])
@require_auth
def create_calendar_booking():
    """Create new calendar booking"""
    try:
        data = request.get_json()
        
        # Generate booking code if not provided
        if 'booking_code' not in data:
            data['booking_code'] = f"BOOK-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        booking = DatabaseUtils.create(CalendarBooking, data)
        return jsonify({
            'success': True,
            'data': booking.to_dict(),
            'message': 'Calendar booking created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 15. CURRENCIES API - International sales support
# =============================================================================

@enhanced_crm_api.route('/currencies', methods=['GET'])
@require_auth
def get_currencies():
    """Get all currencies"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        currencies = DatabaseUtils.get_all(Currency, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [currency.to_dict() for currency in currencies],
            'count': len(currencies)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/currencies', methods=['POST'])
@require_auth
def create_currency():
    """Create new currency"""
    try:
        data = request.get_json()
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        currency = DatabaseUtils.create(Currency, data)
        return jsonify({
            'success': True,
            'data': currency.to_dict(),
            'message': 'Currency created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 16. SOCIAL INTEGRATIONS API - Social media connectivity
# =============================================================================

@enhanced_crm_api.route('/social-integrations', methods=['GET'])
@require_auth
def get_social_integrations():
    """Get all social integrations"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        integrations = DatabaseUtils.get_all(SocialIntegration, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [integration.to_dict() for integration in integrations],
            'count': len(integrations)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/social-integrations', methods=['POST'])
@require_auth
def create_social_integration():
    """Create new social integration"""
    try:
        data = request.get_json()
        
        # Generate integration code if not provided
        if 'integration_code' not in data:
            data['integration_code'] = f"SOC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        integration = DatabaseUtils.create(SocialIntegration, data)
        return jsonify({
            'success': True,
            'data': integration.to_dict(),
            'message': 'Social integration created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 17. SCORING RULES API - Lead/deal scoring
# =============================================================================

@enhanced_crm_api.route('/scoring-rules', methods=['GET'])
@require_auth
def get_scoring_rules():
    """Get all scoring rules"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        rules = DatabaseUtils.get_all(ScoringRule, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [rule.to_dict() for rule in rules],
            'count': len(rules)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/scoring-rules', methods=['POST'])
@require_auth
def create_scoring_rule():
    """Create new scoring rule"""
    try:
        data = request.get_json()
        
        # Generate rule code if not provided
        if 'rule_code' not in data:
            data['rule_code'] = f"RULE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        rule = DatabaseUtils.create(ScoringRule, data)
        return jsonify({
            'success': True,
            'data': rule.to_dict(),
            'message': 'Scoring rule created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# 18. MULTIPLE SCORING RULES API - Advanced scoring systems
# =============================================================================

@enhanced_crm_api.route('/multiple-scoring-rules', methods=['GET'])
@require_auth
def get_multiple_scoring_rules():
    """Get all multiple scoring rules"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        rules = DatabaseUtils.get_all(MultipleScoringRule, filters, limit, offset)
        return jsonify({
            'success': True,
            'data': [rule.to_dict() for rule in rules],
            'count': len(rules)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enhanced_crm_api.route('/multiple-scoring-rules', methods=['POST'])
@require_auth
def create_multiple_scoring_rule():
    """Create new multiple scoring rule"""
    try:
        data = request.get_json()
        
        # Generate rule set code if not provided
        if 'rule_set_code' not in data:
            data['rule_set_code'] = f"RULESET-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Set created by
        current_user = get_current_user()
        if current_user:
            data['created_by'] = current_user.username
        
        rule = DatabaseUtils.create(MultipleScoringRule, data)
        return jsonify({
            'success': True,
            'data': rule.to_dict(),
            'message': 'Multiple scoring rule created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
