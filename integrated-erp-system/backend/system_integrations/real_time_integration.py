# Real-Time Integration System - Complete Real-Time Features

import frappe
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt
import json
from datetime import datetime, timedelta
import requests
import asyncio
import websockets
from flask_socketio import SocketIO, emit, join_room, leave_room
import redis
import threading
import time

class RealTimeIntegration:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.socketio = None
        self.connected_users = {}
        self.module_connections = {}
        
    def initialize_socketio(self, app):
        """Initialize SocketIO with the Flask app"""
        self.socketio = SocketIO(app, cors_allowed_origins="*")
        self.setup_socket_handlers()
        return self.socketio
    
    def setup_socket_handlers(self):
        """Setup SocketIO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle user connection"""
            user_id = frappe.session.user
            self.connected_users[user_id] = {
                'sid': request.sid,
                'connected_at': now(),
                'modules': []
            }
            emit('connected', {'user': user_id, 'timestamp': now()})
            
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle user disconnection"""
            user_id = frappe.session.user
            if user_id in self.connected_users:
                del self.connected_users[user_id]
            emit('disconnected', {'user': user_id, 'timestamp': now()})
            
        @self.socketio.on('join_module')
        def handle_join_module(data):
            """Handle user joining a module"""
            user_id = frappe.session.user
            module = data.get('module')
            
            if user_id in self.connected_users:
                if module not in self.connected_users[user_id]['modules']:
                    self.connected_users[user_id]['modules'].append(module)
                
                join_room(f"{module}_{user_id}")
                emit('joined_module', {'module': module, 'user': user_id})
                
        @self.socketio.on('leave_module')
        def handle_leave_module(data):
            """Handle user leaving a module"""
            user_id = frappe.session.user
            module = data.get('module')
            
            if user_id in self.connected_users:
                if module in self.connected_users[user_id]['modules']:
                    self.connected_users[user_id]['modules'].remove(module)
                
                leave_room(f"{module}_{user_id}")
                emit('left_module', {'module': module, 'user': user_id})
                
        @self.socketio.on('subscribe_to_updates')
        def handle_subscribe_updates(data):
            """Handle user subscribing to updates"""
            user_id = frappe.session.user
            module = data.get('module')
            doc_type = data.get('doc_type')
            
            room_name = f"{module}_{doc_type}_{user_id}"
            join_room(room_name)
            emit('subscribed', {'module': module, 'doc_type': doc_type})
            
        @self.socketio.on('unsubscribe_from_updates')
        def handle_unsubscribe_updates(data):
            """Handle user unsubscribing from updates"""
            user_id = frappe.session.user
            module = data.get('module')
            doc_type = data.get('doc_type')
            
            room_name = f"{module}_{doc_type}_{user_id}"
            leave_room(room_name)
            emit('unsubscribed', {'module': module, 'doc_type': doc_type})

    def broadcast_module_update(self, module, doc_type, doc_name, action, data):
        """Broadcast module update to all connected users"""
        if self.socketio:
            self.socketio.emit('module_update', {
                'module': module,
                'doc_type': doc_type,
                'doc_name': doc_name,
                'action': action,
                'data': data,
                'timestamp': now()
            }, room=f"{module}_{doc_type}")

    def broadcast_user_update(self, user_id, module, doc_type, doc_name, action, data):
        """Broadcast update to specific user"""
        if self.socketio:
            self.socketio.emit('user_update', {
                'module': module,
                'doc_type': doc_type,
                'doc_name': doc_name,
                'action': action,
                'data': data,
                'timestamp': now()
            }, room=f"{module}_{doc_type}_{user_id}")

    def broadcast_system_notification(self, notification_type, message, recipients=None):
        """Broadcast system notification"""
        if self.socketio:
            self.socketio.emit('system_notification', {
                'type': notification_type,
                'message': message,
                'recipients': recipients,
                'timestamp': now()
            })

    def setup_redis_subscriber(self):
        """Setup Redis subscriber for real-time updates"""
        def redis_subscriber():
            pubsub = self.redis_client.pubsub()
            pubsub.subscribe('erp_updates')
            
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        self.process_redis_message(data)
                    except Exception as e:
                        frappe.log_error(f"Redis message processing error: {str(e)}")
        
        # Start Redis subscriber in background thread
        thread = threading.Thread(target=redis_subscriber)
        thread.daemon = True
        thread.start()

    def process_redis_message(self, data):
        """Process Redis message and broadcast to connected users"""
        module = data.get('module')
        doc_type = data.get('doc_type')
        doc_name = data.get('doc_name')
        action = data.get('action')
        user_data = data.get('data')
        
        # Broadcast to module subscribers
        self.broadcast_module_update(module, doc_type, doc_name, action, user_data)
        
        # Broadcast to specific user if specified
        if 'user_id' in data:
            self.broadcast_user_update(
                data['user_id'], module, doc_type, doc_name, action, user_data
            )

    def publish_update(self, module, doc_type, doc_name, action, data, user_id=None):
        """Publish update to Redis"""
        message = {
            'module': module,
            'doc_type': doc_type,
            'doc_name': doc_name,
            'action': action,
            'data': data,
            'timestamp': now()
        }
        
        if user_id:
            message['user_id'] = user_id
        
        self.redis_client.publish('erp_updates', json.dumps(message))

    def setup_module_integrations(self):
        """Setup integrations for all modules"""
        # CRM Module Integration
        self.setup_crm_integration()
        
        # Finance Module Integration
        self.setup_finance_integration()
        
        # People Module Integration
        self.setup_people_integration()
        
        # Moments Module Integration
        self.setup_moments_integration()
        
        # Booking Module Integration
        self.setup_booking_integration()
        
        # Maintenance Module Integration
        self.setup_maintenance_integration()
        
        # Supply Chain Module Integration
        self.setup_supply_chain_integration()

    def setup_crm_integration(self):
        """Setup CRM module real-time integration"""
        # Customer updates
        frappe.get_doc("Customer").on_update = self.crm_customer_update
        
        # Contact updates
        frappe.get_doc("Contact").on_update = self.crm_contact_update
        
        # Opportunity updates
        frappe.get_doc("Opportunity").on_update = self.crm_opportunity_update

    def crm_customer_update(self, doc):
        """Handle CRM customer updates"""
        self.publish_update(
            'crm', 'Customer', doc.name, 'update',
            {
                'customer_name': doc.customer_name,
                'status': doc.status,
                'health_score': doc.health_score
            }
        )

    def crm_contact_update(self, doc):
        """Handle CRM contact updates"""
        self.publish_update(
            'crm', 'Contact', doc.name, 'update',
            {
                'contact_name': doc.contact_name,
                'email': doc.email,
                'phone': doc.phone
            }
        )

    def crm_opportunity_update(self, doc):
        """Handle CRM opportunity updates"""
        self.publish_update(
            'crm', 'Opportunity', doc.name, 'update',
            {
                'opportunity_name': doc.opportunity_name,
                'amount': doc.amount,
                'stage': doc.stage
            }
        )

    def setup_finance_integration(self):
        """Setup Finance module real-time integration"""
        # Invoice updates
        frappe.get_doc("Invoice").on_update = self.finance_invoice_update
        
        # Journal Entry updates
        frappe.get_doc("Journal Entry").on_update = self.finance_journal_update
        
        # Financial Statement updates
        frappe.get_doc("Financial Statement").on_update = self.finance_statement_update

    def finance_invoice_update(self, doc):
        """Handle Finance invoice updates"""
        self.publish_update(
            'finance', 'Invoice', doc.name, 'update',
            {
                'invoice_id': doc.invoice_id,
                'customer': doc.customer,
                'amount': doc.grand_total,
                'status': doc.status
            }
        )

    def finance_journal_update(self, doc):
        """Handle Finance journal entry updates"""
        self.publish_update(
            'finance', 'Journal Entry', doc.name, 'update',
            {
                'journal_entry_id': doc.journal_entry_id,
                'posting_date': doc.posting_date,
                'total_debit': sum([item.debit for item in doc.accounts]),
                'total_credit': sum([item.credit for item in doc.accounts])
            }
        )

    def finance_statement_update(self, doc):
        """Handle Finance statement updates"""
        self.publish_update(
            'finance', 'Financial Statement', doc.name, 'update',
            {
                'statement_id': doc.statement_id,
                'statement_type': doc.statement_type,
                'company': doc.company,
                'status': doc.status
            }
        )

    def setup_people_integration(self):
        """Setup People module real-time integration"""
        # Leave Request updates
        frappe.get_doc("Leave Request").on_update = self.people_leave_update
        
        # Attendance updates
        frappe.get_doc("Attendance").on_update = self.people_attendance_update
        
        # KPI updates
        frappe.get_doc("KPI").on_update = self.people_kpi_update

    def people_leave_update(self, doc):
        """Handle People leave request updates"""
        self.publish_update(
            'people', 'Leave Request', doc.name, 'update',
            {
                'leave_request_id': doc.leave_request_id,
                'employee': doc.employee,
                'leave_type': doc.leave_type,
                'status': doc.status
            }
        )

    def people_attendance_update(self, doc):
        """Handle People attendance updates"""
        self.publish_update(
            'people', 'Attendance', doc.name, 'update',
            {
                'attendance_id': doc.attendance_id,
                'employee': doc.employee,
                'check_in_time': doc.check_in_time,
                'check_out_time': doc.check_out_time,
                'status': doc.status
            }
        )

    def people_kpi_update(self, doc):
        """Handle People KPI updates"""
        self.publish_update(
            'people', 'KPI', doc.name, 'update',
            {
                'kpi_id': doc.kpi_id,
                'employee': doc.employee,
                'kpi_name': doc.kpi_name,
                'kpi_score': doc.kpi_score,
                'status': doc.status
            }
        )

    def setup_moments_integration(self):
        """Setup Moments module real-time integration"""
        # Moment updates
        frappe.get_doc("Moment").on_update = self.moments_moment_update
        
        # Moment Reaction updates
        frappe.get_doc("Moment Reaction").on_update = self.moments_reaction_update

    def moments_moment_update(self, doc):
        """Handle Moments moment updates"""
        self.publish_update(
            'moments', 'Moment', doc.name, 'update',
            {
                'moment_id': doc.moment_id,
                'user': doc.user,
                'content': doc.content[:100] + "..." if len(doc.content) > 100 else doc.content,
                'likes_count': doc.likes_count,
                'comments_count': doc.comments_count
            }
        )

    def moments_reaction_update(self, doc):
        """Handle Moments reaction updates"""
        self.publish_update(
            'moments', 'Moment Reaction', doc.name, 'update',
            {
                'reaction_id': doc.reaction_id,
                'moment': doc.moment,
                'user': doc.user,
                'reaction_type': doc.reaction_type
            }
        )

    def setup_booking_integration(self):
        """Setup Booking module real-time integration"""
        # Meeting updates
        frappe.get_doc("Meeting").on_update = self.booking_meeting_update
        
        # Resource Booking updates
        frappe.get_doc("Resource Booking").on_update = self.booking_resource_update

    def booking_meeting_update(self, doc):
        """Handle Booking meeting updates"""
        self.publish_update(
            'booking', 'Meeting', doc.name, 'update',
            {
                'meeting_id': doc.meeting_id,
                'meeting_title': doc.meeting_title,
                'meeting_date': doc.meeting_date,
                'start_time': doc.start_time,
                'status': doc.status
            }
        )

    def booking_resource_update(self, doc):
        """Handle Booking resource booking updates"""
        self.publish_update(
            'booking', 'Resource Booking', doc.name, 'update',
            {
                'booking_id': doc.booking_id,
                'resource': doc.resource,
                'booking_date': doc.booking_date,
                'start_time': doc.start_time,
                'status': doc.status
            }
        )

    def setup_maintenance_integration(self):
        """Setup Maintenance module real-time integration"""
        # Asset updates
        frappe.get_doc("Asset").on_update = self.maintenance_asset_update
        
        # Work Order updates
        frappe.get_doc("Work Order").on_update = self.maintenance_work_order_update

    def maintenance_asset_update(self, doc):
        """Handle Maintenance asset updates"""
        self.publish_update(
            'maintenance', 'Asset', doc.name, 'update',
            {
                'asset_id': doc.asset_id,
                'asset_name': doc.asset_name,
                'asset_type': doc.asset_type,
                'status': doc.status,
                'condition': doc.condition
            }
        )

    def maintenance_work_order_update(self, doc):
        """Handle Maintenance work order updates"""
        self.publish_update(
            'maintenance', 'Work Order', doc.name, 'update',
            {
                'work_order_id': doc.work_order_id,
                'work_order_title': doc.work_order_title,
                'asset': doc.asset,
                'status': doc.status,
                'priority': doc.priority
            }
        )

    def setup_supply_chain_integration(self):
        """Setup Supply Chain module real-time integration"""
        # Inventory Item updates
        frappe.get_doc("Inventory Item").on_update = self.supply_chain_inventory_update
        
        # Purchase Order updates
        frappe.get_doc("Purchase Order").on_update = self.supply_chain_purchase_order_update
        
        # Supplier updates
        frappe.get_doc("Supplier").on_update = self.supply_chain_supplier_update

    def supply_chain_inventory_update(self, doc):
        """Handle Supply Chain inventory updates"""
        self.publish_update(
            'supply_chain', 'Inventory Item', doc.name, 'update',
            {
                'item_id': doc.item_id,
                'item_name': doc.item_name,
                'quantity_on_hand': doc.quantity_on_hand,
                'reorder_status': doc.reorder_status,
                'status': doc.status
            }
        )

    def supply_chain_purchase_order_update(self, doc):
        """Handle Supply Chain purchase order updates"""
        self.publish_update(
            'supply_chain', 'Purchase Order', doc.name, 'update',
            {
                'purchase_order_id': doc.purchase_order_id,
                'supplier': doc.supplier,
                'total_amount': doc.total_amount,
                'status': doc.status
            }
        )

    def supply_chain_supplier_update(self, doc):
        """Handle Supply Chain supplier updates"""
        self.publish_update(
            'supply_chain', 'Supplier', doc.name, 'update',
            {
                'supplier_id': doc.supplier_id,
                'supplier_name': doc.supplier_name,
                'rating': doc.rating,
                'status': doc.status
            }
        )

    def setup_ai_analytics_integration(self):
        """Setup AI Analytics real-time integration"""
        # Start AI analytics background process
        self.start_ai_analytics_process()

    def start_ai_analytics_process(self):
        """Start AI analytics background process"""
        def ai_analytics_worker():
            while True:
                try:
                    # Process AI analytics for all modules
                    self.process_crm_ai_analytics()
                    self.process_finance_ai_analytics()
                    self.process_people_ai_analytics()
                    self.process_supply_chain_ai_analytics()
                    
                    time.sleep(300)  # Run every 5 minutes
                except Exception as e:
                    frappe.log_error(f"AI Analytics error: {str(e)}")
                    time.sleep(60)  # Wait 1 minute before retry
        
        thread = threading.Thread(target=ai_analytics_worker)
        thread.daemon = True
        thread.start()

    def process_crm_ai_analytics(self):
        """Process CRM AI analytics"""
        # Customer health scoring
        customers = frappe.get_list("Customer", fields=["name", "customer_name"])
        for customer in customers:
            health_score = self.calculate_customer_health_score(customer.name)
            self.publish_update(
                'crm', 'Customer', customer.name, 'ai_analytics',
                {'health_score': health_score, 'type': 'health_scoring'}
            )

    def process_finance_ai_analytics(self):
        """Process Finance AI analytics"""
        # Financial trend analysis
        self.publish_update(
            'finance', 'Financial Statement', 'system', 'ai_analytics',
            {'type': 'trend_analysis', 'data': self.analyze_financial_trends()}
        )

    def process_people_ai_analytics(self):
        """Process People AI analytics"""
        # Performance analytics
        self.publish_update(
            'people', 'KPI', 'system', 'ai_analytics',
            {'type': 'performance_analytics', 'data': self.analyze_performance_trends()}
        )

    def process_supply_chain_ai_analytics(self):
        """Process Supply Chain AI analytics"""
        # Demand forecasting
        self.publish_update(
            'supply_chain', 'Inventory Item', 'system', 'ai_analytics',
            {'type': 'demand_forecasting', 'data': self.forecast_demand()}
        )

    def calculate_customer_health_score(self, customer_name):
        """Calculate customer health score using AI"""
        # Simplified health score calculation
        # In a real system, this would use machine learning models
        return 85  # Placeholder value

    def analyze_financial_trends(self):
        """Analyze financial trends using AI"""
        # Simplified trend analysis
        return {'trend': 'positive', 'confidence': 0.85}

    def analyze_performance_trends(self):
        """Analyze performance trends using AI"""
        # Simplified performance analysis
        return {'trend': 'improving', 'confidence': 0.90}

    def forecast_demand(self):
        """Forecast demand using AI"""
        # Simplified demand forecasting
        return {'forecast': 'increasing', 'confidence': 0.80}

    def get_connected_users(self):
        """Get list of connected users"""
        return list(self.connected_users.keys())

    def get_module_subscribers(self, module):
        """Get list of users subscribed to a module"""
        subscribers = []
        for user_id, user_data in self.connected_users.items():
            if module in user_data.get('modules', []):
                subscribers.append(user_id)
        return subscribers

    def send_notification_to_user(self, user_id, notification_type, message, data=None):
        """Send notification to specific user"""
        if self.socketio:
            self.socketio.emit('notification', {
                'type': notification_type,
                'message': message,
                'data': data,
                'timestamp': now()
            }, room=f"user_{user_id}")

    def broadcast_system_alert(self, alert_type, message, severity='info'):
        """Broadcast system alert to all connected users"""
        if self.socketio:
            self.socketio.emit('system_alert', {
                'type': alert_type,
                'message': message,
                'severity': severity,
                'timestamp': now()
            })

    def setup_health_monitoring(self):
        """Setup system health monitoring"""
        def health_monitor():
            while True:
                try:
                    # Check system health
                    health_status = self.check_system_health()
                    
                    if health_status['status'] != 'healthy':
                        self.broadcast_system_alert(
                            'system_health',
                            f"System health issue: {health_status['message']}",
                            'warning'
                        )
                    
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    frappe.log_error(f"Health monitoring error: {str(e)}")
                    time.sleep(60)
        
        thread = threading.Thread(target=health_monitor)
        thread.daemon = True
        thread.start()

    def check_system_health(self):
        """Check system health status"""
        try:
            # Check database connection
            frappe.db.sql("SELECT 1")
            
            # Check Redis connection
            self.redis_client.ping()
            
            return {'status': 'healthy', 'message': 'All systems operational'}
        except Exception as e:
            return {'status': 'unhealthy', 'message': str(e)}

# Global real-time integration instance
real_time_integration = RealTimeIntegration()
