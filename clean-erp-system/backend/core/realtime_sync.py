# Real-Time Synchronization System
# Advanced real-time data synchronization across all modules

import asyncio
import json
import redis
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import current_app
from flask_socketio import SocketIO, emit, join_room, leave_room
from core.database import db
from core.auth import get_current_user

class RealtimeSyncManager:
    """Real-time synchronization manager"""
    
    def __init__(self, app=None):
        self.app = app
        self.redis_client = None
        self.socketio = None
        self.sync_settings = {}
        self.active_connections = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        self.redis_client = redis.Redis(
            host=app.config.get('REDIS_HOST', 'localhost'),
            port=app.config.get('REDIS_PORT', 6379),
            db=app.config.get('REDIS_DB', 0),
            decode_responses=True
        )
        
        # Initialize SocketIO
        self.socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
        
        # Load sync settings
        self.load_sync_settings()
        
        # Setup event handlers
        self.setup_event_handlers()
    
    def load_sync_settings(self):
        """Load synchronization settings from database"""
        try:
            # Load sync settings from database or config
            self.sync_settings = {
                'enabled_modules': ['crm', 'finance', 'people', 'supply_chain', 'maintenance', 'booking', 'moments', 'ai', 'workflow'],
                'sync_events': {
                    'crm': ['customer_created', 'customer_updated', 'contact_created', 'opportunity_created'],
                    'finance': ['invoice_created', 'payment_processed', 'journal_entry_created'],
                    'people': ['employee_created', 'leave_request_created', 'attendance_updated'],
                    'supply_chain': ['item_created', 'purchase_order_created', 'stock_movement'],
                    'maintenance': ['asset_created', 'work_order_created', 'maintenance_scheduled'],
                    'booking': ['booking_created', 'resource_updated', 'conflict_resolved'],
                    'moments': ['moment_created', 'comment_added', 'reaction_added'],
                    'ai': ['prediction_created', 'insight_generated', 'recommendation_created'],
                    'workflow': ['workflow_executed', 'approval_required', 'task_completed']
                },
                'sync_frequency': 'real_time',  # real_time, 5_seconds, 30_seconds, 1_minute
                'conflict_resolution': 'last_modified_wins',  # last_modified_wins, manual, custom
                'data_validation': True,
                'sync_logging': True
            }
        except Exception as e:
            current_app.logger.error(f"Error loading sync settings: {e}")
            self.sync_settings = {}
    
    def setup_event_handlers(self):
        """Setup SocketIO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            current_app.logger.info(f"Client connected: {request.sid}")
            self.active_connections[request.sid] = {
                'user_id': None,
                'company_id': None,
                'subscribed_modules': [],
                'connected_at': datetime.now()
            }
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            current_app.logger.info(f"Client disconnected: {request.sid}")
            if request.sid in self.active_connections:
                del self.active_connections[request.sid]
        
        @self.socketio.on('authenticate')
        def handle_authenticate(data):
            """Handle client authentication"""
            try:
                token = data.get('token')
                if token:
                    # Validate token and get user info
                    user = self.validate_token(token)
                    if user:
                        self.active_connections[request.sid]['user_id'] = user['id']
                        self.active_connections[request.sid]['company_id'] = user['company_id']
                        emit('authenticated', {'status': 'success', 'user_id': user['id']})
                    else:
                        emit('authentication_failed', {'error': 'Invalid token'})
                else:
                    emit('authentication_failed', {'error': 'No token provided'})
            except Exception as e:
                emit('authentication_failed', {'error': str(e)})
        
        @self.socketio.on('subscribe_module')
        def handle_subscribe_module(data):
            """Handle module subscription"""
            try:
                module = data.get('module')
                if module in self.sync_settings.get('enabled_modules', []):
                    join_room(f"module_{module}")
                    self.active_connections[request.sid]['subscribed_modules'].append(module)
                    emit('subscribed', {'module': module, 'status': 'success'})
                else:
                    emit('subscription_failed', {'error': f'Module {module} not available'})
            except Exception as e:
                emit('subscription_failed', {'error': str(e)})
        
        @self.socketio.on('unsubscribe_module')
        def handle_unsubscribe_module(data):
            """Handle module unsubscription"""
            try:
                module = data.get('module')
                leave_room(f"module_{module}")
                if module in self.active_connections[request.sid]['subscribed_modules']:
                    self.active_connections[request.sid]['subscribed_modules'].remove(module)
                emit('unsubscribed', {'module': module, 'status': 'success'})
            except Exception as e:
                emit('unsubscription_failed', {'error': str(e)})
        
        @self.socketio.on('sync_request')
        def handle_sync_request(data):
            """Handle synchronization request"""
            try:
                module = data.get('module')
                entity_id = data.get('entity_id')
                entity_type = data.get('entity_type')
                
                # Get latest data
                latest_data = self.get_latest_data(module, entity_type, entity_id)
                emit('sync_response', {
                    'module': module,
                    'entity_id': entity_id,
                    'entity_type': entity_type,
                    'data': latest_data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                emit('sync_failed', {'error': str(e)})
    
    def validate_token(self, token):
        """Validate authentication token"""
        try:
            # Implement token validation logic
            # This would typically decode JWT and verify signature
            return {'id': 1, 'company_id': 1}  # Placeholder
        except Exception:
            return None
    
    def get_latest_data(self, module, entity_type, entity_id):
        """Get latest data for synchronization"""
        try:
            # Implement data retrieval logic based on module and entity type
            # This would query the appropriate database table
            return {'id': entity_id, 'updated_at': datetime.now().isoformat()}
        except Exception as e:
            current_app.logger.error(f"Error getting latest data: {e}")
            return None
    
    def broadcast_change(self, module, event_type, data, company_id=None):
        """Broadcast change to subscribed clients"""
        try:
            room = f"module_{module}"
            event_data = {
                'module': module,
                'event_type': event_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            # Filter by company if specified
            if company_id:
                # Only send to clients from the same company
                for sid, connection in self.active_connections.items():
                    if connection.get('company_id') == company_id:
                        self.socketio.emit('data_change', event_data, room=room, to=sid)
            else:
                self.socketio.emit('data_change', event_data, room=room)
                
        except Exception as e:
            current_app.logger.error(f"Error broadcasting change: {e}")
    
    def sync_data(self, source_module, target_module, data, sync_type='bidirectional'):
        """Synchronize data between modules"""
        try:
            if sync_type == 'bidirectional':
                # Sync data both ways
                self.sync_to_target(source_module, target_module, data)
                self.sync_to_target(target_module, source_module, data)
            elif sync_type == 'unidirectional':
                # Sync data one way
                self.sync_to_target(source_module, target_module, data)
                
        except Exception as e:
            current_app.logger.error(f"Error syncing data: {e}")
    
    def sync_to_target(self, source_module, target_module, data):
        """Sync data to target module"""
        try:
            # Implement module-specific synchronization logic
            sync_mapping = {
                'crm_to_finance': self.sync_crm_to_finance,
                'finance_to_crm': self.sync_finance_to_crm,
                'people_to_maintenance': self.sync_people_to_maintenance,
                'supply_chain_to_finance': self.sync_supply_chain_to_finance,
                # Add more mappings as needed
            }
            
            sync_key = f"{source_module}_to_{target_module}"
            if sync_key in sync_mapping:
                sync_mapping[sync_key](data)
                
        except Exception as e:
            current_app.logger.error(f"Error syncing to target: {e}")
    
    def sync_crm_to_finance(self, data):
        """Sync CRM data to Finance module"""
        try:
            # When customer is created in CRM, create corresponding account in Finance
            if data.get('event_type') == 'customer_created':
                customer_data = data.get('data')
                # Create customer account in Finance module
                self.create_finance_customer_account(customer_data)
                
        except Exception as e:
            current_app.logger.error(f"Error syncing CRM to Finance: {e}")
    
    def sync_finance_to_crm(self, data):
        """Sync Finance data to CRM module"""
        try:
            # When invoice is created in Finance, update customer status in CRM
            if data.get('event_type') == 'invoice_created':
                invoice_data = data.get('data')
                # Update customer status in CRM
                self.update_crm_customer_status(invoice_data)
                
        except Exception as e:
            current_app.logger.error(f"Error syncing Finance to CRM: {e}")
    
    def sync_people_to_maintenance(self, data):
        """Sync People data to Maintenance module"""
        try:
            # When employee is assigned to asset, update maintenance records
            if data.get('event_type') == 'employee_assigned':
                assignment_data = data.get('data')
                # Update maintenance records
                self.update_maintenance_assignment(assignment_data)
                
        except Exception as e:
            current_app.logger.error(f"Error syncing People to Maintenance: {e}")
    
    def sync_supply_chain_to_finance(self, data):
        """Sync Supply Chain data to Finance module"""
        try:
            # When purchase order is created, create corresponding journal entry
            if data.get('event_type') == 'purchase_order_created':
                po_data = data.get('data')
                # Create journal entry in Finance
                self.create_purchase_journal_entry(po_data)
                
        except Exception as e:
            current_app.logger.error(f"Error syncing Supply Chain to Finance: {e}")
    
    def create_finance_customer_account(self, customer_data):
        """Create customer account in Finance module"""
        try:
            # Implement customer account creation logic
            pass
        except Exception as e:
            current_app.logger.error(f"Error creating finance customer account: {e}")
    
    def update_crm_customer_status(self, invoice_data):
        """Update customer status in CRM"""
        try:
            # Implement customer status update logic
            pass
        except Exception as e:
            current_app.logger.error(f"Error updating CRM customer status: {e}")
    
    def update_maintenance_assignment(self, assignment_data):
        """Update maintenance assignment"""
        try:
            # Implement maintenance assignment update logic
            pass
        except Exception as e:
            current_app.logger.error(f"Error updating maintenance assignment: {e}")
    
    def create_purchase_journal_entry(self, po_data):
        """Create purchase journal entry"""
        try:
            # Implement journal entry creation logic
            pass
        except Exception as e:
            current_app.logger.error(f"Error creating purchase journal entry: {e}")
    
    def get_sync_status(self, module=None):
        """Get synchronization status"""
        try:
            status = {
                'total_connections': len(self.active_connections),
                'enabled_modules': self.sync_settings.get('enabled_modules', []),
                'sync_frequency': self.sync_settings.get('sync_frequency', 'real_time'),
                'last_sync': datetime.now().isoformat()
            }
            
            if module:
                status['module_status'] = {
                    'subscribed_clients': len([c for c in self.active_connections.values() 
                                             if module in c.get('subscribed_modules', [])]),
                    'sync_events': self.sync_settings.get('sync_events', {}).get(module, [])
                }
            
            return status
        except Exception as e:
            current_app.logger.error(f"Error getting sync status: {e}")
            return {}

# Global sync manager instance
sync_manager = RealtimeSyncManager()
