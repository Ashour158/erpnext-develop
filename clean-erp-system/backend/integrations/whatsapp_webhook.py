# WhatsApp Webhook Handler
# Handles incoming WhatsApp webhooks and processes messages

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import json
import hashlib
import hmac
import base64
from urllib.parse import urlencode, parse_qs

# Import WhatsApp integration components
from .whatsapp_integration import WhatsAppBusinessAPI, whatsapp_integration_manager
from .whatsapp_ai_analyzer import WhatsAppAIAnalyzer, whatsapp_ai_analyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
whatsapp_webhook_bp = Blueprint('whatsapp_webhook', __name__, url_prefix='/api/whatsapp/webhook')

class WhatsAppWebhookHandler:
    """
    WhatsApp Webhook Handler
    Processes incoming WhatsApp webhooks and manages message flow
    """
    
    def __init__(self):
        self.webhook_secret = current_app.config.get('WHATSAPP_WEBHOOK_SECRET', '')
        self.message_processor = WhatsAppMessageProcessor()
        self.analytics_tracker = WhatsAppAnalyticsTracker()
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify WhatsApp webhook"""
        try:
            if mode == 'subscribe' and token == self.webhook_secret:
                logger.info("WhatsApp webhook verified successfully")
                return challenge
            else:
                logger.warning(f"Webhook verification failed: mode={mode}, token={token}")
                return None
        except Exception as e:
            logger.error(f"Error verifying webhook: {str(e)}")
            return None
    
    def handle_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming WhatsApp webhook"""
        try:
            logger.info(f"Received webhook: {json.dumps(webhook_data, indent=2)}")
            
            # Verify webhook signature
            if not self._verify_webhook_signature(webhook_data):
                logger.warning("Webhook signature verification failed")
                return {'status': 'error', 'message': 'Invalid signature'}
            
            # Process webhook data
            if 'entry' not in webhook_data:
                return {'status': 'error', 'message': 'Invalid webhook data'}
            
            processed_messages = []
            
            for entry in webhook_data['entry']:
                if 'changes' in entry:
                    for change in entry['changes']:
                        if change['field'] == 'messages':
                            messages = self._process_webhook_change(change)
                            processed_messages.extend(messages)
            
            # Track analytics
            self.analytics_tracker.track_webhook_received(len(processed_messages))
            
            return {
                'status': 'success',
                'message': 'Webhook processed successfully',
                'processed_messages': len(processed_messages)
            }
            
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _verify_webhook_signature(self, webhook_data: Dict[str, Any]) -> bool:
        """Verify webhook signature for security"""
        try:
            # Get signature from headers
            signature = request.headers.get('X-Hub-Signature-256', '')
            if not signature:
                logger.warning("No signature found in webhook headers")
                return False
            
            # Calculate expected signature
            expected_signature = 'sha256=' + hmac.new(
                self.webhook_secret.encode(),
                json.dumps(webhook_data, sort_keys=True).encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False
    
    def _process_webhook_change(self, change: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process webhook change and extract messages"""
        try:
            processed_messages = []
            
            if 'value' in change and 'messages' in change['value']:
                for message_data in change['value']['messages']:
                    # Process message
                    result = self.message_processor.process_message(message_data)
                    if result:
                        processed_messages.append(result)
            
            return processed_messages
            
        except Exception as e:
            logger.error(f"Error processing webhook change: {str(e)}")
            return []

class WhatsAppMessageProcessor:
    """
    WhatsApp Message Processor
    Processes incoming messages and triggers appropriate actions
    """
    
    def __init__(self):
        self.ai_analyzer = whatsapp_ai_analyzer
        self.integration_manager = whatsapp_integration_manager
    
    def process_message(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming WhatsApp message"""
        try:
            logger.info(f"Processing message: {message_data.get('id', 'unknown')}")
            
            # Extract message information
            message_id = message_data.get('id', '')
            from_number = message_data.get('from', '')
            to_number = message_data.get('to', '')
            timestamp = message_data.get('timestamp', '')
            
            # Get message content
            content = self._extract_message_content(message_data)
            
            if not content:
                logger.warning(f"No content found in message {message_id}")
                return None
            
            # Analyze message with AI
            analysis = self.ai_analyzer.analyze_message(message_id, content, from_number)
            
            # Determine action based on analysis
            action_result = self._determine_action(analysis, message_data)
            
            # Send appropriate response
            if action_result['should_respond']:
                self._send_response(from_number, analysis, action_result)
            
            # Track analytics
            self._track_message_analytics(analysis, action_result)
            
            return {
                'message_id': message_id,
                'from_number': from_number,
                'content': content,
                'analysis': analysis,
                'action_result': action_result,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return None
    
    def _extract_message_content(self, message_data: Dict[str, Any]) -> str:
        """Extract content from message data"""
        try:
            if 'text' in message_data:
                return message_data['text']['body']
            elif 'image' in message_data:
                return f"Image: {message_data['image'].get('caption', 'No caption')}"
            elif 'audio' in message_data:
                return "Audio message"
            elif 'video' in message_data:
                return f"Video: {message_data['video'].get('caption', 'No caption')}"
            elif 'document' in message_data:
                return f"Document: {message_data['document'].get('filename', 'Unknown file')}"
            elif 'location' in message_data:
                location = message_data['location']
                return f"Location: {location.get('latitude')}, {location.get('longitude')}"
            elif 'contacts' in message_data:
                return "Contact shared"
            else:
                return "Unknown message type"
                
        except Exception as e:
            logger.error(f"Error extracting message content: {str(e)}")
            return ""
    
    def _determine_action(self, analysis, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine action based on message analysis"""
        try:
            intent = analysis.intent
            priority = analysis.priority_score
            escalation_needed = analysis.escalation_needed
            
            action_result = {
                'should_respond': True,
                'action_type': 'auto_response',
                'response_template': 'default',
                'escalation_required': escalation_needed,
                'follow_up_required': analysis.follow_up_required,
                'priority': 'medium'
            }
            
            # Determine action based on intent
            if intent == 'lead_inquiry':
                action_result.update({
                    'action_type': 'create_lead',
                    'response_template': 'lead_acknowledgment',
                    'priority': 'high' if priority > 0.7 else 'medium'
                })
            elif intent == 'support_ticket':
                action_result.update({
                    'action_type': 'create_ticket',
                    'response_template': 'support_acknowledgment',
                    'priority': 'high' if priority > 0.8 else 'medium'
                })
            elif intent == 'complaint':
                action_result.update({
                    'action_type': 'create_complaint',
                    'response_template': 'complaint_acknowledgment',
                    'priority': 'urgent',
                    'escalation_required': True
                })
            elif intent == 'order_inquiry':
                action_result.update({
                    'action_type': 'check_order',
                    'response_template': 'order_inquiry_response',
                    'priority': 'medium'
                })
            elif intent == 'payment_inquiry':
                action_result.update({
                    'action_type': 'check_payment',
                    'response_template': 'payment_inquiry_response',
                    'priority': 'high'
                })
            elif intent == 'appointment_request':
                action_result.update({
                    'action_type': 'create_appointment',
                    'response_template': 'appointment_acknowledgment',
                    'priority': 'medium'
                })
            elif intent == 'feedback':
                action_result.update({
                    'action_type': 'record_feedback',
                    'response_template': 'feedback_thank_you',
                    'priority': 'low'
                })
            elif intent == 'spam':
                action_result.update({
                    'should_respond': False,
                    'action_type': 'ignore',
                    'priority': 'low'
                })
            else:
                action_result.update({
                    'action_type': 'general_response',
                    'response_template': 'general_acknowledgment',
                    'priority': 'low'
                })
            
            return action_result
            
        except Exception as e:
            logger.error(f"Error determining action: {str(e)}")
            return {
                'should_respond': True,
                'action_type': 'general_response',
                'response_template': 'default',
                'escalation_required': False,
                'follow_up_required': False,
                'priority': 'medium'
            }
    
    def _send_response(self, to_number: str, analysis, action_result: Dict[str, Any]):
        """Send response to WhatsApp user"""
        try:
            # Get integration
            integrations = list(self.integration_manager.integrations.values())
            if not integrations:
                logger.error("No WhatsApp integrations available")
                return
            
            integration = integrations[0]  # Use first available integration
            
            # Generate response message
            response_message = self._generate_response_message(analysis, action_result)
            
            # Send message
            result = integration._send_text_message(to_number, response_message)
            
            if result['success']:
                logger.info(f"Response sent successfully to {to_number}")
            else:
                logger.error(f"Failed to send response: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error sending response: {str(e)}")
    
    def _generate_response_message(self, analysis, action_result: Dict[str, Any]) -> str:
        """Generate appropriate response message"""
        try:
            template = action_result.get('response_template', 'default')
            intent = analysis.intent
            sentiment = analysis.sentiment.value
            
            # Base response templates
            templates = {
                'lead_acknowledgment': "Thank you for your interest! We've received your inquiry and our sales team will contact you shortly.",
                'support_acknowledgment': "Thank you for contacting support! We've created a ticket for your issue and will respond within 24 hours.",
                'complaint_acknowledgment': "We sincerely apologize for any inconvenience. We've logged your complaint and our management team will review it immediately.",
                'order_inquiry_response': "Thank you for your order inquiry. We're checking your order status and will provide an update shortly.",
                'payment_inquiry_response': "Thank you for your payment inquiry. Our finance team will review your payment status and respond shortly.",
                'appointment_acknowledgment': "Thank you for your appointment request! We'll confirm the details and get back to you soon.",
                'feedback_thank_you': "Thank you for your valuable feedback! We appreciate your input and will use it to improve our services.",
                'general_acknowledgment': "Thank you for your message. We've received it and will respond as soon as possible.",
                'default': "Thank you for your message. How can I help you today?"
            }
            
            # Get base message
            message = templates.get(template, templates['default'])
            
            # Customize based on sentiment
            if sentiment == 'angry':
                message = "I understand you're upset, and I want to help resolve this for you. " + message
            elif sentiment == 'frustrated':
                message = "I apologize for any frustration this has caused. " + message
            elif sentiment == 'positive':
                message = "I'm glad to hear from you! " + message
            
            # Add escalation notice if needed
            if action_result.get('escalation_required'):
                message += " This has been escalated to our management team for immediate attention."
            
            return message
            
        except Exception as e:
            logger.error(f"Error generating response message: {str(e)}")
            return "Thank you for your message. How can I help you today?"
    
    def _track_message_analytics(self, analysis, action_result: Dict[str, Any]):
        """Track message analytics"""
        try:
            # Track intent distribution
            self.analytics_tracker.track_intent(analysis.intent)
            
            # Track sentiment distribution
            self.analytics_tracker.track_sentiment(analysis.sentiment.value)
            
            # Track action taken
            self.analytics_tracker.track_action(action_result['action_type'])
            
            # Track priority distribution
            self.analytics_tracker.track_priority(analysis.priority_score)
            
        except Exception as e:
            logger.error(f"Error tracking analytics: {str(e)}")

class WhatsAppAnalyticsTracker:
    """
    WhatsApp Analytics Tracker
    Tracks and stores analytics data for WhatsApp integration
    """
    
    def __init__(self):
        self.analytics_data = {
            'webhooks_received': 0,
            'messages_processed': 0,
            'intent_distribution': {},
            'sentiment_distribution': {},
            'action_distribution': {},
            'priority_distribution': {},
            'response_times': [],
            'error_count': 0
        }
    
    def track_webhook_received(self, message_count: int):
        """Track webhook received"""
        self.analytics_data['webhooks_received'] += 1
        self.analytics_data['messages_processed'] += message_count
    
    def track_intent(self, intent: str):
        """Track intent distribution"""
        if intent not in self.analytics_data['intent_distribution']:
            self.analytics_data['intent_distribution'][intent] = 0
        self.analytics_data['intent_distribution'][intent] += 1
    
    def track_sentiment(self, sentiment: str):
        """Track sentiment distribution"""
        if sentiment not in self.analytics_data['sentiment_distribution']:
            self.analytics_data['sentiment_distribution'][sentiment] = 0
        self.analytics_data['sentiment_distribution'][sentiment] += 1
    
    def track_action(self, action: str):
        """Track action distribution"""
        if action not in self.analytics_data['action_distribution']:
            self.analytics_data['action_distribution'][action] = 0
        self.analytics_data['action_distribution'][action] += 1
    
    def track_priority(self, priority_score: float):
        """Track priority distribution"""
        priority_level = 'low'
        if priority_score > 0.8:
            priority_level = 'high'
        elif priority_score > 0.6:
            priority_level = 'medium'
        
        if priority_level not in self.analytics_data['priority_distribution']:
            self.analytics_data['priority_distribution'][priority_level] = 0
        self.analytics_data['priority_distribution'][priority_level] += 1
    
    def track_response_time(self, response_time: float):
        """Track response time"""
        self.analytics_data['response_times'].append(response_time)
        # Keep only last 1000 response times
        if len(self.analytics_data['response_times']) > 1000:
            self.analytics_data['response_times'] = self.analytics_data['response_times'][-1000:]
    
    def track_error(self):
        """Track error occurrence"""
        self.analytics_data['error_count'] += 1
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics data"""
        try:
            # Calculate averages
            avg_response_time = 0
            if self.analytics_data['response_times']:
                avg_response_time = sum(self.analytics_data['response_times']) / len(self.analytics_data['response_times'])
            
            return {
                'webhooks_received': self.analytics_data['webhooks_received'],
                'messages_processed': self.analytics_data['messages_processed'],
                'intent_distribution': self.analytics_data['intent_distribution'],
                'sentiment_distribution': self.analytics_data['sentiment_distribution'],
                'action_distribution': self.analytics_data['action_distribution'],
                'priority_distribution': self.analytics_data['priority_distribution'],
                'avg_response_time': avg_response_time,
                'error_count': self.analytics_data['error_count'],
                'error_rate': self.analytics_data['error_count'] / max(self.analytics_data['messages_processed'], 1)
            }
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}

# Global webhook handler
webhook_handler = WhatsAppWebhookHandler()

# API Endpoints
@whatsapp_webhook_bp.route('/', methods=['GET', 'POST'])
def webhook():
    """WhatsApp webhook endpoint"""
    try:
        if request.method == 'GET':
            # Webhook verification
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            
            result = webhook_handler.verify_webhook(mode, token, challenge)
            
            if result:
                return result, 200
            else:
                return jsonify({'error': 'Webhook verification failed'}), 403
        
        elif request.method == 'POST':
            # Handle incoming webhook
            webhook_data = request.get_json()
            
            if not webhook_data:
                return jsonify({'error': 'No webhook data received'}), 400
            
            result = webhook_handler.handle_webhook(webhook_data)
            
            return jsonify(result), 200 if result.get('status') == 'success' else 400
    
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_webhook_bp.route('/status', methods=['GET'])
def webhook_status():
    """Get webhook status"""
    try:
        analytics = webhook_handler.analytics_tracker.get_analytics()
        
        return jsonify({
            'status': 'active',
            'analytics': analytics,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting webhook status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@whatsapp_webhook_bp.route('/test', methods=['POST'])
def test_webhook():
    """Test webhook processing"""
    try:
        test_data = request.get_json()
        
        if not test_data:
            return jsonify({'error': 'No test data provided'}), 400
        
        # Process test data
        result = webhook_handler.handle_webhook(test_data)
        
        return jsonify({
            'status': 'success',
            'result': result,
            'message': 'Test webhook processed successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Error testing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500
