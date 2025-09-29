# Natural Language Interface
# AI-powered natural language processing for ERP system interaction

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentType(Enum):
    QUERY = "query"
    COMMAND = "command"
    REPORT = "report"
    ANALYSIS = "analysis"
    UPDATE = "update"
    CREATE = "create"
    DELETE = "delete"
    HELP = "help"
    UNKNOWN = "unknown"

class EntityType(Enum):
    DATE = "date"
    NUMBER = "number"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    EMAIL = "email"
    PHONE = "phone"
    PRODUCT = "product"
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    EMPLOYEE = "employee"
    DEPARTMENT = "department"
    LOCATION = "location"

@dataclass
class Intent:
    intent_type: IntentType
    confidence: float
    entities: List[Dict[str, Any]]
    parameters: Dict[str, Any]
    original_text: str
    processed_text: str

@dataclass
class QueryResult:
    query_id: str
    intent: Intent
    results: List[Dict[str, Any]]
    execution_time: float
    success: bool
    error_message: Optional[str] = None
    suggestions: List[str] = None

@dataclass
class VoiceCommand:
    command_id: str
    text: str
    intent: Intent
    executed: bool
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class NaturalLanguageInterface:
    """
    Advanced Natural Language Interface for ERP System
    Provides voice commands, chat interface, and natural language queries
    """
    
    def __init__(self):
        self.intent_patterns = {
            IntentType.QUERY: [
                r"show me|display|get|find|search|what is|how many|how much",
                r"list|show|view|see|look at"
            ],
            IntentType.COMMAND: [
                r"create|add|new|insert|make",
                r"update|edit|modify|change|set",
                r"delete|remove|cancel|stop",
                r"send|email|notify|alert"
            ],
            IntentType.REPORT: [
                r"report|generate|create report|show report",
                r"dashboard|analytics|statistics|metrics"
            ],
            IntentType.ANALYSIS: [
                r"analyze|analysis|insights|trends|forecast",
                r"compare|vs|versus|difference|change"
            ],
            IntentType.HELP: [
                r"help|assist|support|guide|how to|what can|commands"
            ]
        }
        
        self.entity_patterns = {
            EntityType.DATE: [
                r'\b(today|yesterday|tomorrow)\b',
                r'\b(this|last|next)\s+(week|month|quarter|year)\b',
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b'
            ],
            EntityType.NUMBER: [
                r'\b\d+\b',
                r'\b\d+\.\d+\b'
            ],
            EntityType.CURRENCY: [
                r'\$\d+(?:\.\d{2})?\b',
                r'\b\d+(?:\.\d{2})?\s*(?:dollars?|usd|us\$)\b'
            ],
            EntityType.PERCENTAGE: [
                r'\b\d+(?:\.\d+)?%\b'
            ],
            EntityType.EMAIL: [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            EntityType.PHONE: [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                r'\(\d{3}\)\s*\d{3}[-.]?\d{4}'
            ]
        }
        
        self.module_keywords = {
            'crm': ['customer', 'client', 'lead', 'prospect', 'contact', 'sales', 'opportunity'],
            'finance': ['invoice', 'payment', 'billing', 'accounting', 'budget', 'expense', 'revenue'],
            'inventory': ['stock', 'inventory', 'product', 'item', 'warehouse', 'supply'],
            'hr': ['employee', 'staff', 'personnel', 'payroll', 'attendance', 'leave'],
            'projects': ['project', 'task', 'milestone', 'deadline', 'resource'],
            'reports': ['report', 'dashboard', 'analytics', 'statistics', 'metrics']
        }
        
        self.query_executors = {
            IntentType.QUERY: self._execute_query,
            IntentType.COMMAND: self._execute_command,
            IntentType.REPORT: self._execute_report,
            IntentType.ANALYSIS: self._execute_analysis,
            IntentType.HELP: self._execute_help
        }
    
    def process_natural_language(self, text: str, user_id: str = None) -> Intent:
        """
        Process natural language input and extract intent
        """
        try:
            # Clean and normalize text
            processed_text = self._normalize_text(text)
            
            # Extract entities
            entities = self._extract_entities(processed_text)
            
            # Determine intent
            intent_type, confidence = self._classify_intent(processed_text)
            
            # Extract parameters
            parameters = self._extract_parameters(processed_text, entities)
            
            intent = Intent(
                intent_type=intent_type,
                confidence=confidence,
                entities=entities,
                parameters=parameters,
                original_text=text,
                processed_text=processed_text
            )
            
            logger.info(f"Processed NL input: '{text}' -> {intent_type.value} (confidence: {confidence:.2f})")
            return intent
            
        except Exception as e:
            logger.error(f"Error processing natural language: {str(e)}")
            return Intent(
                intent_type=IntentType.UNKNOWN,
                confidence=0.0,
                entities=[],
                parameters={},
                original_text=text,
                processed_text=text
            )
    
    def execute_voice_command(self, text: str, user_id: str = None) -> VoiceCommand:
        """
        Execute a voice command
        """
        try:
            command_id = str(uuid.uuid4())
            
            # Process the command
            intent = self.process_natural_language(text, user_id)
            
            # Execute the command
            result = None
            error_message = None
            executed = False
            
            try:
                if intent.intent_type in self.query_executors:
                    result = self.query_executors[intent.intent_type](intent, user_id)
                    executed = True
                else:
                    error_message = f"Unknown command type: {intent.intent_type.value}"
            except Exception as e:
                error_message = str(e)
            
            command = VoiceCommand(
                command_id=command_id,
                text=text,
                intent=intent,
                executed=executed,
                result=result,
                error_message=error_message
            )
            
            logger.info(f"Executed voice command: '{text}' -> {executed}")
            return command
            
        except Exception as e:
            logger.error(f"Error executing voice command: {str(e)}")
            return VoiceCommand(
                command_id=str(uuid.uuid4()),
                text=text,
                intent=Intent(intent_type=IntentType.UNKNOWN, confidence=0.0, entities=[], parameters={}, original_text=text, processed_text=text),
                executed=False,
                error_message=str(e)
            )
    
    def chat_with_data(self, message: str, user_id: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Chat interface for data interaction
        """
        try:
            # Process the message
            intent = self.process_natural_language(message, user_id)
            
            # Generate response based on intent
            response = self._generate_chat_response(intent, context or {})
            
            return {
                'message': message,
                'intent': intent.intent_type.value,
                'confidence': intent.confidence,
                'response': response,
                'suggestions': self._generate_suggestions(intent),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in chat interface: {str(e)}")
            return {
                'message': message,
                'error': str(e),
                'response': "I'm sorry, I couldn't process your request. Please try again.",
                'timestamp': datetime.now().isoformat()
            }
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize and clean text input
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?]', '', text)
        
        return text
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from text
        """
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'type': entity_type.value,
                        'value': match.group(),
                        'start': match.start(),
                        'end': match.end()
                    })
        
        return entities
    
    def _classify_intent(self, text: str) -> Tuple[IntentType, float]:
        """
        Classify the intent of the text
        """
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0
        
        for intent_type, patterns in self.intent_patterns.items():
            confidence = 0.0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matches += 1
            
            if matches > 0:
                confidence = min(1.0, matches / len(patterns) + 0.3)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_intent = intent_type
        
        return best_intent, best_confidence
    
    def _extract_parameters(self, text: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract parameters from text and entities
        """
        parameters = {}
        
        # Extract dates
        date_entities = [e for e in entities if e['type'] == 'date']
        if date_entities:
            parameters['dates'] = [e['value'] for e in date_entities]
        
        # Extract numbers
        number_entities = [e for e in entities if e['type'] == 'number']
        if number_entities:
            parameters['numbers'] = [float(e['value']) for e in number_entities]
        
        # Extract currency
        currency_entities = [e for e in entities if e['type'] == 'currency']
        if currency_entities:
            parameters['currency'] = [e['value'] for e in currency_entities]
        
        # Extract module context
        for module, keywords in self.module_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    parameters['module'] = module
                    break
        
        return parameters
    
    def _execute_query(self, intent: Intent, user_id: str = None) -> Dict[str, Any]:
        """
        Execute a data query
        """
        try:
            # This would integrate with the actual data layer
            # For now, return mock data based on the query
            
            query_type = intent.parameters.get('module', 'general')
            
            if query_type == 'crm':
                return {
                    'type': 'customer_data',
                    'results': [
                        {'customer': 'John Doe', 'email': 'john@example.com', 'status': 'active'},
                        {'customer': 'Jane Smith', 'email': 'jane@example.com', 'status': 'active'}
                    ],
                    'count': 2
                }
            elif query_type == 'finance':
                return {
                    'type': 'financial_data',
                    'results': [
                        {'invoice': 'INV-001', 'amount': 1500.00, 'status': 'paid'},
                        {'invoice': 'INV-002', 'amount': 2300.00, 'status': 'pending'}
                    ],
                    'count': 2
                }
            else:
                return {
                    'type': 'general_data',
                    'results': [{'message': 'Query executed successfully'}],
                    'count': 1
                }
                
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return {'error': str(e)}
    
    def _execute_command(self, intent: Intent, user_id: str = None) -> Dict[str, Any]:
        """
        Execute a command
        """
        try:
            # This would integrate with the actual command execution layer
            return {
                'type': 'command_executed',
                'message': f"Command '{intent.original_text}' executed successfully",
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return {'error': str(e)}
    
    def _execute_report(self, intent: Intent, user_id: str = None) -> Dict[str, Any]:
        """
        Execute a report generation
        """
        try:
            # This would integrate with the report generation system
            return {
                'type': 'report_generated',
                'message': 'Report generated successfully',
                'report_id': str(uuid.uuid4()),
                'download_url': '/reports/download/' + str(uuid.uuid4())
            }
            
        except Exception as e:
            logger.error(f"Error executing report: {str(e)}")
            return {'error': str(e)}
    
    def _execute_analysis(self, intent: Intent, user_id: str = None) -> Dict[str, Any]:
        """
        Execute data analysis
        """
        try:
            # This would integrate with the analytics engine
            return {
                'type': 'analysis_completed',
                'message': 'Analysis completed successfully',
                'insights': [
                    'Sales increased by 15% this month',
                    'Customer satisfaction improved by 8%',
                    'Inventory turnover rate is optimal'
                ],
                'recommendations': [
                    'Consider expanding marketing efforts',
                    'Focus on customer retention strategies',
                    'Optimize inventory levels'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error executing analysis: {str(e)}")
            return {'error': str(e)}
    
    def _execute_help(self, intent: Intent, user_id: str = None) -> Dict[str, Any]:
        """
        Execute help command
        """
        return {
            'type': 'help',
            'message': 'Here are some things you can ask me:',
            'examples': [
                'Show me sales data for this month',
                'Create a new customer',
                'Generate a financial report',
                'Analyze customer trends',
                'What are my top products?',
                'Show me inventory levels'
            ],
            'commands': [
                'Query data: "Show me...", "What is...", "How many..."',
                'Create records: "Create new...", "Add...", "New..."',
                'Generate reports: "Generate report...", "Create dashboard..."',
                'Get analysis: "Analyze...", "Compare...", "Trends..."'
            ]
        }
    
    def _generate_chat_response(self, intent: Intent, context: Dict[str, Any]) -> str:
        """
        Generate a natural language response
        """
        try:
            if intent.intent_type == IntentType.QUERY:
                return "I found the data you requested. Here are the results..."
            elif intent.intent_type == IntentType.COMMAND:
                return "I've executed your command successfully."
            elif intent.intent_type == IntentType.REPORT:
                return "I've generated the report for you. You can download it from the reports section."
            elif intent.intent_type == IntentType.ANALYSIS:
                return "I've completed the analysis. Here are the key insights and recommendations..."
            elif intent.intent_type == IntentType.HELP:
                return "I'm here to help! You can ask me about data, create records, generate reports, or get analysis."
            else:
                return "I'm not sure I understand. Could you please rephrase your request?"
                
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            return "I'm sorry, I couldn't process your request. Please try again."
    
    def _generate_suggestions(self, intent: Intent) -> List[str]:
        """
        Generate follow-up suggestions
        """
        suggestions = []
        
        if intent.intent_type == IntentType.QUERY:
            suggestions.extend([
                "Would you like to see more details?",
                "Should I create a report for this data?",
                "Would you like to analyze trends?"
            ])
        elif intent.intent_type == IntentType.COMMAND:
            suggestions.extend([
                "Would you like to see the updated data?",
                "Should I send a notification about this change?",
                "Would you like to create a follow-up task?"
            ])
        elif intent.intent_type == IntentType.REPORT:
            suggestions.extend([
                "Would you like to schedule this report?",
                "Should I email this report to stakeholders?",
                "Would you like to customize the report format?"
            ])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def get_voice_commands_help(self) -> Dict[str, List[str]]:
        """
        Get help for voice commands
        """
        return {
            'data_queries': [
                'Show me sales data',
                'What are my top customers?',
                'How many orders this month?',
                'Display inventory levels',
                'Show employee attendance'
            ],
            'commands': [
                'Create new customer',
                'Update product information',
                'Send email notification',
                'Generate monthly report',
                'Schedule meeting'
            ],
            'analysis': [
                'Analyze sales trends',
                'Compare this month to last month',
                'Show customer growth',
                'Identify top performing products',
                'Analyze employee productivity'
            ],
            'reports': [
                'Generate financial report',
                'Create sales dashboard',
                'Show inventory report',
                'Generate customer report',
                'Create performance metrics'
            ]
        }

# Global Natural Language Interface instance
natural_language_interface = NaturalLanguageInterface()
