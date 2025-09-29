# AI Assistant System
# Notion-like AI assistant with natural language processing and intelligent features

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
import time
import re
import openai
from pathlib import Path
import hashlib
import hmac
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIActionType(Enum):
    CREATE_PAGE = "create_page"
    UPDATE_PAGE = "update_page"
    DELETE_PAGE = "delete_page"
    SEARCH_CONTENT = "search_content"
    SUMMARIZE_CONTENT = "summarize_content"
    TRANSLATE_CONTENT = "translate_content"
    GENERATE_CONTENT = "generate_content"
    ANALYZE_DATA = "analyze_data"
    CREATE_TASK = "create_task"
    SCHEDULE_EVENT = "schedule_event"
    SEND_MESSAGE = "send_message"
    CREATE_DATABASE = "create_database"
    UPDATE_DATABASE = "update_database"
    QUERY_DATABASE = "query_database"

class AIResponseType(Enum):
    TEXT = "text"
    ACTION = "action"
    SUGGESTION = "suggestion"
    QUESTION = "question"
    CONFIRMATION = "confirmation"
    ERROR = "error"

class AIContext(Enum):
    CHAT = "chat"
    PAGE = "page"
    DATABASE = "database"
    WORKSPACE = "workspace"
    TASK = "task"
    EVENT = "event"
    FILE = "file"

@dataclass
class AIRequest:
    request_id: str
    user_id: str
    content: str
    context: AIContext
    context_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    language: str = "en"

@dataclass
class AIResponse:
    response_id: str
    request_id: str
    content: str
    response_type: AIResponseType
    actions: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AIConversation:
    conversation_id: str
    user_id: str
    title: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    context: AIContext = AIContext.CHAT
    context_id: Optional[str] = None
    is_active: bool = True

@dataclass
class AITemplate:
    template_id: str
    name: str
    description: str
    category: str
    content: str
    variables: List[str] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    is_public: bool = False
    tags: List[str] = field(default_factory=list)

class AIAssistant:
    """
    AI Assistant System
    Notion-like AI assistant with natural language processing and intelligent features
    """
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key
        self.conversations: Dict[str, AIConversation] = {}
        self.templates: Dict[str, AITemplate] = {}
        self.request_queue = queue.Queue()
        self.is_processing = True
        
        # Initialize OpenAI
        if openai_api_key:
            openai.api_key = openai_api_key
        
        # Start background processing
        self._start_ai_processing()
        
        # Initialize AI patterns and templates
        self._initialize_ai_patterns()
        self._initialize_default_templates()
    
    def _start_ai_processing(self):
        """Start background AI processing"""
        self.is_processing = True
        
        # Start processing thread
        thread = threading.Thread(target=self._process_ai_requests, daemon=True)
        thread.start()
        
        logger.info("AI Assistant processing started")
    
    def _process_ai_requests(self):
        """Process AI requests in background"""
        while self.is_processing:
            try:
                request = self.request_queue.get(timeout=1)
                self._handle_ai_request(request)
                self.request_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing AI request: {str(e)}")
    
    def _initialize_ai_patterns(self):
        """Initialize AI patterns for natural language processing"""
        self.action_patterns = {
            AIActionType.CREATE_PAGE: [
                r'\b(create|make|new)\s+(page|document|note)\b',
                r'\b(write|draft)\s+(a|an|the)\s+(page|document|note)\b',
                r'\b(start|begin)\s+(a|an|the)\s+(page|document|note)\b'
            ],
            AIActionType.UPDATE_PAGE: [
                r'\b(update|edit|modify|change)\s+(page|document|note)\b',
                r'\b(revise|amend|correct)\s+(page|document|note)\b',
                r'\b(improve|enhance)\s+(page|document|note)\b'
            ],
            AIActionType.SEARCH_CONTENT: [
                r'\b(search|find|look for)\b',
                r'\b(where is|locate)\b',
                r'\b(show me|display)\b'
            ],
            AIActionType.SUMMARIZE_CONTENT: [
                r'\b(summarize|summary|sum up)\b',
                r'\b(brief|overview|outline)\b',
                r'\b(key points|main points)\b'
            ],
            AIActionType.TRANSLATE_CONTENT: [
                r'\b(translate|convert)\s+(to|into)\b',
                r'\b(in|to)\s+(english|spanish|french|german|chinese|japanese)\b'
            ],
            AIActionType.GENERATE_CONTENT: [
                r'\b(generate|create|write)\s+(content|text|article|blog|report)\b',
                r'\b(draft|compose|author)\s+(a|an|the)\b',
                r'\b(brainstorm|ideate|think of)\b'
            ],
            AIActionType.ANALYZE_DATA: [
                r'\b(analyze|examine|study)\s+(data|information|content)\b',
                r'\b(insights|trends|patterns)\b',
                r'\b(statistics|metrics|analytics)\b'
            ],
            AIActionType.CREATE_TASK: [
                r'\b(create|add|new)\s+(task|todo|reminder)\b',
                r'\b(assign|delegate)\s+(task|work)\b',
                r'\b(schedule|plan)\s+(task|work)\b'
            ],
            AIActionType.SCHEDULE_EVENT: [
                r'\b(schedule|plan|book)\s+(meeting|event|appointment)\b',
                r'\b(create|add)\s+(meeting|event|appointment)\b',
                r'\b(set up|arrange)\s+(meeting|event|appointment)\b'
            ],
            AIActionType.SEND_MESSAGE: [
                r'\b(send|message|notify)\s+(user|person|team)\b',
                r'\b(contact|reach out to)\b',
                r'\b(inform|tell|update)\b'
            ],
            AIActionType.CREATE_DATABASE: [
                r'\b(create|make|new)\s+(database|table|spreadsheet)\b',
                r'\b(set up|build)\s+(database|table|spreadsheet)\b',
                r'\b(organize|structure)\s+(data|information)\b'
            ],
            AIActionType.QUERY_DATABASE: [
                r'\b(query|search|filter)\s+(database|table|data)\b',
                r'\b(find|get|retrieve)\s+(records|entries|data)\b',
                r'\b(show|display)\s+(all|some|specific)\b'
            ]
        }
        
        # Intent patterns
        self.intent_patterns = {
            'question': [
                r'\b(what|how|when|where|why|who|which)\b',
                r'\b(can you|could you|would you)\b',
                r'\b(help|assist|support)\b'
            ],
            'command': [
                r'\b(create|make|new|add|build)\b',
                r'\b(update|edit|modify|change)\b',
                r'\b(delete|remove|clear)\b',
                r'\b(find|search|look)\b'
            ],
            'request': [
                r'\b(please|kindly|could you|would you)\b',
                r'\b(I need|I want|I would like)\b',
                r'\b(can you help|assist me)\b'
            ]
        }
    
    def _initialize_default_templates(self):
        """Initialize default AI templates"""
        default_templates = [
            {
                'name': 'Meeting Notes',
                'description': 'Template for meeting notes and minutes',
                'category': 'meeting',
                'content': '''# Meeting Notes

**Date:** {date}
**Time:** {time}
**Attendees:** {attendees}
**Location:** {location}

## Agenda
- {agenda_item_1}
- {agenda_item_2}
- {agenda_item_3}

## Discussion Points
- {discussion_point_1}
- {discussion_point_2}

## Action Items
- [ ] {action_item_1} - {assignee_1} - {due_date_1}
- [ ] {action_item_2} - {assignee_2} - {due_date_2}

## Next Meeting
**Date:** {next_meeting_date}
**Time:** {next_meeting_time}
**Agenda:** {next_meeting_agenda}''',
                'variables': ['date', 'time', 'attendees', 'location', 'agenda_item_1', 'agenda_item_2', 'agenda_item_3', 'discussion_point_1', 'discussion_point_2', 'action_item_1', 'assignee_1', 'due_date_1', 'action_item_2', 'assignee_2', 'due_date_2', 'next_meeting_date', 'next_meeting_time', 'next_meeting_agenda']
            },
            {
                'name': 'Project Plan',
                'description': 'Template for project planning and management',
                'category': 'project',
                'content': '''# Project Plan: {project_name}

**Project Manager:** {project_manager}
**Start Date:** {start_date}
**End Date:** {end_date}
**Status:** {status}

## Project Overview
{project_description}

## Objectives
- {objective_1}
- {objective_2}
- {objective_3}

## Timeline
- **Phase 1:** {phase_1_name} - {phase_1_duration}
- **Phase 2:** {phase_2_name} - {phase_2_duration}
- **Phase 3:** {phase_3_name} - {phase_3_duration}

## Resources
- **Team Members:** {team_members}
- **Budget:** {budget}
- **Tools:** {tools}

## Risks and Mitigation
- **Risk 1:** {risk_1} - **Mitigation:** {mitigation_1}
- **Risk 2:** {risk_2} - **Mitigation:** {mitigation_2}

## Success Metrics
- {metric_1}
- {metric_2}
- {metric_3}''',
                'variables': ['project_name', 'project_manager', 'start_date', 'end_date', 'status', 'project_description', 'objective_1', 'objective_2', 'objective_3', 'phase_1_name', 'phase_1_duration', 'phase_2_name', 'phase_2_duration', 'phase_3_name', 'phase_3_duration', 'team_members', 'budget', 'tools', 'risk_1', 'mitigation_1', 'risk_2', 'mitigation_2', 'metric_1', 'metric_2', 'metric_3']
            },
            {
                'name': 'Task List',
                'description': 'Template for task management and tracking',
                'category': 'task',
                'content': '''# Task List: {list_name}

**Created:** {created_date}
**Updated:** {updated_date}
**Status:** {status}

## Tasks
- [ ] {task_1} - {assignee_1} - {due_date_1} - {priority_1}
- [ ] {task_2} - {assignee_2} - {due_date_2} - {priority_2}
- [ ] {task_3} - {assignee_3} - {due_date_3} - {priority_3}

## Completed Tasks
- [x] {completed_task_1} - {completed_by_1} - {completed_date_1}
- [x] {completed_task_2} - {completed_by_2} - {completed_date_2}

## Notes
{notes}''',
                'variables': ['list_name', 'created_date', 'updated_date', 'status', 'task_1', 'assignee_1', 'due_date_1', 'priority_1', 'task_2', 'assignee_2', 'due_date_2', 'priority_2', 'task_3', 'assignee_3', 'due_date_3', 'priority_3', 'completed_task_1', 'completed_by_1', 'completed_date_1', 'completed_task_2', 'completed_by_2', 'completed_date_2', 'notes']
            },
            {
                'name': 'Research Notes',
                'description': 'Template for research and analysis',
                'category': 'research',
                'content': '''# Research Notes: {research_topic}

**Researcher:** {researcher}
**Date:** {date}
**Source:** {source}

## Research Question
{research_question}

## Key Findings
- {finding_1}
- {finding_2}
- {finding_3}

## Sources
1. {source_1} - {url_1}
2. {source_2} - {url_2}
3. {source_3} - {url_3}

## Analysis
{analysis}

## Conclusions
{conclusions}

## Next Steps
- {next_step_1}
- {next_step_2}
- {next_step_3}''',
                'variables': ['research_topic', 'researcher', 'date', 'source', 'research_question', 'finding_1', 'finding_2', 'finding_3', 'source_1', 'url_1', 'source_2', 'url_2', 'source_3', 'url_3', 'analysis', 'conclusions', 'next_step_1', 'next_step_2', 'next_step_3']
            }
        ]
        
        for template_data in default_templates:
            template = AITemplate(
                template_id=str(uuid.uuid4()),
                name=template_data['name'],
                description=template_data['description'],
                category=template_data['category'],
                content=template_data['content'],
                variables=template_data['variables'],
                created_by='system',
                is_public=True
            )
            self.templates[template.template_id] = template
    
    def process_request(self, user_id: str, content: str, context: AIContext, 
                       context_id: str = None) -> AIResponse:
        """Process AI request and return response"""
        try:
            # Create request
            request = AIRequest(
                request_id=str(uuid.uuid4()),
                user_id=user_id,
                content=content,
                context=context,
                context_id=context_id
            )
            
            # Analyze request
            analysis = self._analyze_request(request)
            
            # Generate response
            response = self._generate_response(request, analysis)
            
            # Queue for processing
            self.request_queue.put(request)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing AI request: {str(e)}")
            return self._create_error_response(str(e))
    
    def _analyze_request(self, request: AIRequest) -> Dict[str, Any]:
        """Analyze AI request to determine intent and actions"""
        try:
            content_lower = request.content.lower()
            
            # Detect intent
            intent = self._detect_intent(content_lower)
            
            # Detect actions
            actions = self._detect_actions(content_lower)
            
            # Extract entities
            entities = self._extract_entities(request.content)
            
            # Determine confidence
            confidence = self._calculate_confidence(intent, actions, entities)
            
            return {
                'intent': intent,
                'actions': actions,
                'entities': entities,
                'confidence': confidence,
                'language': self._detect_language(request.content)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing request: {str(e)}")
            return {
                'intent': 'unknown',
                'actions': [],
                'entities': {},
                'confidence': 0.0,
                'language': 'en'
            }
    
    def _detect_intent(self, content: str) -> str:
        """Detect user intent from content"""
        try:
            for intent, patterns in self.intent_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return intent
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Error detecting intent: {str(e)}")
            return 'unknown'
    
    def _detect_actions(self, content: str) -> List[AIActionType]:
        """Detect actions from content"""
        try:
            actions = []
            
            for action_type, patterns in self.action_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        actions.append(action_type)
                        break
            
            return actions
            
        except Exception as e:
            logger.error(f"Error detecting actions: {str(e)}")
            return []
    
    def _extract_entities(self, content: str) -> Dict[str, Any]:
        """Extract entities from content"""
        try:
            entities = {}
            
            # Extract dates
            date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b'
            dates = re.findall(date_pattern, content)
            if dates:
                entities['dates'] = dates
            
            # Extract times
            time_pattern = r'\b(\d{1,2}:\d{2}(?::\d{2})?(?:\s?[AP]M)?)\b'
            times = re.findall(time_pattern, content)
            if times:
                entities['times'] = times
            
            # Extract names (capitalized words)
            name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
            names = re.findall(name_pattern, content)
            if names:
                entities['names'] = names
            
            # Extract URLs
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, content)
            if urls:
                entities['urls'] = urls
            
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, content)
            if emails:
                entities['emails'] = emails
            
            # Extract phone numbers
            phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            phones = re.findall(phone_pattern, content)
            if phones:
                entities['phones'] = phones
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return {}
    
    def _calculate_confidence(self, intent: str, actions: List[AIActionType], 
                            entities: Dict[str, Any]) -> float:
        """Calculate confidence score for analysis"""
        try:
            confidence = 0.0
            
            # Intent confidence
            if intent != 'unknown':
                confidence += 0.3
            
            # Actions confidence
            if actions:
                confidence += 0.4
            
            # Entities confidence
            if entities:
                confidence += 0.3
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 0.0
    
    def _detect_language(self, content: str) -> str:
        """Detect language of content"""
        try:
            # Simple language detection based on common words
            english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
            spanish_words = ['el', 'la', 'los', 'las', 'de', 'del', 'en', 'con', 'por', 'para', 'que', 'como']
            french_words = ['le', 'la', 'les', 'de', 'du', 'des', 'en', 'avec', 'pour', 'que', 'comme']
            
            content_lower = content.lower()
            
            english_count = sum(1 for word in english_words if word in content_lower)
            spanish_count = sum(1 for word in spanish_words if word in content_lower)
            french_count = sum(1 for word in french_words if word in content_lower)
            
            if english_count > spanish_count and english_count > french_count:
                return 'en'
            elif spanish_count > french_count:
                return 'es'
            elif french_count > 0:
                return 'fr'
            else:
                return 'en'
                
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return 'en'
    
    def _generate_response(self, request: AIRequest, analysis: Dict[str, Any]) -> AIResponse:
        """Generate AI response based on analysis"""
        try:
            response_id = str(uuid.uuid4())
            
            # Determine response type
            if analysis['actions']:
                response_type = AIResponseType.ACTION
                content = self._generate_action_response(request, analysis)
            elif analysis['intent'] == 'question':
                response_type = AIResponseType.TEXT
                content = self._generate_question_response(request, analysis)
            else:
                response_type = AIResponseType.SUGGESTION
                content = self._generate_suggestion_response(request, analysis)
            
            # Generate actions
            actions = self._generate_actions(request, analysis)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(request, analysis)
            
            return AIResponse(
                response_id=response_id,
                request_id=request.request_id,
                content=content,
                response_type=response_type,
                actions=actions,
                suggestions=suggestions,
                confidence=analysis['confidence'],
                metadata=analysis
            )
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._create_error_response(str(e))
    
    def _generate_action_response(self, request: AIRequest, analysis: Dict[str, Any]) -> str:
        """Generate response for action requests"""
        try:
            actions = analysis['actions']
            
            if AIActionType.CREATE_PAGE in actions:
                return "I'll help you create a new page. What would you like to name it and what content should it contain?"
            elif AIActionType.UPDATE_PAGE in actions:
                return "I'll help you update the page. What changes would you like to make?"
            elif AIActionType.SEARCH_CONTENT in actions:
                return "I'll search for that content. What specifically are you looking for?"
            elif AIActionType.SUMMARIZE_CONTENT in actions:
                return "I'll summarize the content for you. Which content would you like me to summarize?"
            elif AIActionType.TRANSLATE_CONTENT in actions:
                return "I'll translate the content for you. What language would you like me to translate it to?"
            elif AIActionType.GENERATE_CONTENT in actions:
                return "I'll help you generate content. What type of content would you like me to create?"
            elif AIActionType.ANALYZE_DATA in actions:
                return "I'll analyze the data for you. What data would you like me to analyze?"
            elif AIActionType.CREATE_TASK in actions:
                return "I'll create a task for you. What task would you like me to create?"
            elif AIActionType.SCHEDULE_EVENT in actions:
                return "I'll schedule an event for you. What event would you like me to schedule?"
            elif AIActionType.SEND_MESSAGE in actions:
                return "I'll send a message for you. Who would you like me to send it to and what should it say?"
            elif AIActionType.CREATE_DATABASE in actions:
                return "I'll help you create a database. What type of database would you like me to create?"
            elif AIActionType.QUERY_DATABASE in actions:
                return "I'll query the database for you. What information are you looking for?"
            else:
                return "I understand you want me to help with something. Could you provide more details?"
                
        except Exception as e:
            logger.error(f"Error generating action response: {str(e)}")
            return "I'll help you with that. Could you provide more details?"
    
    def _generate_question_response(self, request: AIRequest, analysis: Dict[str, Any]) -> str:
        """Generate response for questions"""
        try:
            # This would use OpenAI API for intelligent responses
            if self.openai_api_key:
                return self._generate_openai_response(request.content)
            else:
                return self._generate_fallback_response(request.content)
                
        except Exception as e:
            logger.error(f"Error generating question response: {str(e)}")
            return "I'd be happy to help answer your question. Could you provide more details?"
    
    def _generate_suggestion_response(self, request: AIRequest, analysis: Dict[str, Any]) -> str:
        """Generate response for suggestions"""
        try:
            return "Here are some suggestions based on your request:"
            
        except Exception as e:
            logger.error(f"Error generating suggestion response: {str(e)}")
            return "I have some suggestions for you."
    
    def _generate_openai_response(self, content: str) -> str:
        """Generate response using OpenAI API"""
        try:
            # This would use OpenAI API
            # For now, return a placeholder
            return "I understand your request. Let me help you with that."
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            return "I'd be happy to help. Could you provide more details?"
    
    def _generate_fallback_response(self, content: str) -> str:
        """Generate fallback response without OpenAI"""
        try:
            # Simple keyword-based responses
            content_lower = content.lower()
            
            if 'help' in content_lower:
                return "I'm here to help! What would you like me to assist you with?"
            elif 'create' in content_lower:
                return "I can help you create content. What would you like to create?"
            elif 'search' in content_lower:
                return "I can help you search for information. What are you looking for?"
            elif 'schedule' in content_lower:
                return "I can help you schedule events. What would you like to schedule?"
            else:
                return "I understand your request. How can I help you?"
                
        except Exception as e:
            logger.error(f"Error generating fallback response: {str(e)}")
            return "I'm here to help! What would you like me to assist you with?"
    
    def _generate_actions(self, request: AIRequest, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actions based on analysis"""
        try:
            actions = []
            
            for action_type in analysis['actions']:
                action = {
                    'type': action_type.value,
                    'context': request.context.value,
                    'context_id': request.context_id,
                    'parameters': self._extract_action_parameters(request.content, action_type)
                }
                actions.append(action)
            
            return actions
            
        except Exception as e:
            logger.error(f"Error generating actions: {str(e)}")
            return []
    
    def _extract_action_parameters(self, content: str, action_type: AIActionType) -> Dict[str, Any]:
        """Extract parameters for specific actions"""
        try:
            parameters = {}
            
            if action_type == AIActionType.CREATE_PAGE:
                # Extract page title and content
                title_match = re.search(r'"(.*?)"', content)
                if title_match:
                    parameters['title'] = title_match.group(1)
                
                # Extract content after "about" or "regarding"
                content_match = re.search(r'(?:about|regarding|on)\s+(.+)', content, re.IGNORECASE)
                if content_match:
                    parameters['content'] = content_match.group(1)
            
            elif action_type == AIActionType.SEARCH_CONTENT:
                # Extract search query
                query_match = re.search(r'(?:search|find|look for)\s+(.+)', content, re.IGNORECASE)
                if query_match:
                    parameters['query'] = query_match.group(1)
            
            elif action_type == AIActionType.CREATE_TASK:
                # Extract task details
                task_match = re.search(r'(?:create|add|new)\s+(?:task|todo|reminder)\s+(?:for|about|to)\s+(.+)', content, re.IGNORECASE)
                if task_match:
                    parameters['description'] = task_match.group(1)
                
                # Extract due date
                date_match = re.search(r'(?:due|by|before)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', content, re.IGNORECASE)
                if date_match:
                    parameters['due_date'] = date_match.group(1)
            
            elif action_type == AIActionType.SCHEDULE_EVENT:
                # Extract event details
                event_match = re.search(r'(?:schedule|plan|book)\s+(?:meeting|event|appointment)\s+(?:for|about|on)\s+(.+)', content, re.IGNORECASE)
                if event_match:
                    parameters['title'] = event_match.group(1)
                
                # Extract date and time
                datetime_match = re.search(r'(?:on|at)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(?:at\s+)?(\d{1,2}:\d{2})', content, re.IGNORECASE)
                if datetime_match:
                    parameters['date'] = datetime_match.group(1)
                    parameters['time'] = datetime_match.group(2)
            
            return parameters
            
        except Exception as e:
            logger.error(f"Error extracting action parameters: {str(e)}")
            return {}
    
    def _generate_suggestions(self, request: AIRequest, analysis: Dict[str, Any]) -> List[str]:
        """Generate suggestions based on context"""
        try:
            suggestions = []
            
            # Context-based suggestions
            if request.context == AIContext.CHAT:
                suggestions.extend([
                    "Create a new page",
                    "Search for information",
                    "Schedule a meeting",
                    "Create a task"
                ])
            elif request.context == AIContext.PAGE:
                suggestions.extend([
                    "Update this page",
                    "Create a related page",
                    "Add a comment",
                    "Share this page"
                ])
            elif request.context == AIContext.DATABASE:
                suggestions.extend([
                    "Add a new record",
                    "Filter the data",
                    "Create a view",
                    "Export the data"
                ])
            elif request.context == AIContext.TASK:
                suggestions.extend([
                    "Mark as complete",
                    "Set a due date",
                    "Assign to someone",
                    "Add a comment"
                ])
            
            # Intent-based suggestions
            if analysis['intent'] == 'question':
                suggestions.extend([
                    "Search for more information",
                    "Create a knowledge base entry",
                    "Ask a team member",
                    "Schedule a discussion"
                ])
            elif analysis['intent'] == 'command':
                suggestions.extend([
                    "Confirm the action",
                    "Provide more details",
                    "Choose from options",
                    "Cancel the action"
                ])
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return []
    
    def _handle_ai_request(self, request: AIRequest):
        """Handle AI request processing"""
        try:
            # This would implement the actual AI processing
            # For now, we'll just log the request
            logger.info(f"Processing AI request: {request.request_id}")
            
        except Exception as e:
            logger.error(f"Error handling AI request: {str(e)}")
    
    def _create_error_response(self, error_message: str) -> AIResponse:
        """Create error response"""
        return AIResponse(
            response_id=str(uuid.uuid4()),
            request_id="",
            content=f"I apologize, but I encountered an error: {error_message}",
            response_type=AIResponseType.ERROR,
            confidence=0.0
        )
    
    def create_conversation(self, user_id: str, title: str, context: AIContext = AIContext.CHAT, 
                           context_id: str = None) -> AIConversation:
        """Create a new AI conversation"""
        try:
            conversation = AIConversation(
                conversation_id=str(uuid.uuid4()),
                user_id=user_id,
                title=title,
                context=context,
                context_id=context_id
            )
            
            self.conversations[conversation.conversation_id] = conversation
            
            logger.info(f"AI conversation created: {conversation.conversation_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise
    
    def add_message_to_conversation(self, conversation_id: str, role: str, content: str) -> bool:
        """Add message to conversation"""
        try:
            if conversation_id not in self.conversations:
                return False
            
            conversation = self.conversations[conversation_id]
            message = {
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat()
            }
            
            conversation.messages.append(message)
            conversation.updated_at = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding message to conversation: {str(e)}")
            return False
    
    def get_conversation(self, conversation_id: str) -> Optional[AIConversation]:
        """Get conversation by ID"""
        return self.conversations.get(conversation_id)
    
    def get_user_conversations(self, user_id: str) -> List[AIConversation]:
        """Get all conversations for a user"""
        try:
            user_conversations = [
                conv for conv in self.conversations.values()
                if conv.user_id == user_id and conv.is_active
            ]
            
            # Sort by updated date (newest first)
            user_conversations.sort(key=lambda x: x.updated_at, reverse=True)
            
            return user_conversations
            
        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            return []
    
    def create_template(self, name: str, description: str, category: str, 
                      content: str, created_by: str, variables: List[str] = None,
                      is_public: bool = False, tags: List[str] = None) -> AITemplate:
        """Create a new AI template"""
        try:
            template = AITemplate(
                template_id=str(uuid.uuid4()),
                name=name,
                description=description,
                category=category,
                content=content,
                variables=variables or [],
                created_by=created_by,
                is_public=is_public,
                tags=tags or []
            )
            
            self.templates[template.template_id] = template
            
            logger.info(f"AI template created: {template.template_id}")
            return template
            
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            raise
    
    def get_template(self, template_id: str) -> Optional[AITemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def get_templates_by_category(self, category: str) -> List[AITemplate]:
        """Get templates by category"""
        try:
            return [
                template for template in self.templates.values()
                if template.category == category and template.is_public
            ]
            
        except Exception as e:
            logger.error(f"Error getting templates by category: {str(e)}")
            return []
    
    def search_templates(self, query: str) -> List[AITemplate]:
        """Search templates by query"""
        try:
            query_lower = query.lower()
            results = []
            
            for template in self.templates.values():
                if (query_lower in template.name.lower() or 
                    query_lower in template.description.lower() or
                    query_lower in template.content.lower() or
                    any(query_lower in tag.lower() for tag in template.tags)):
                    results.append(template)
            
            # Sort by usage count (most used first)
            results.sort(key=lambda x: x.usage_count, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching templates: {str(e)}")
            return []
    
    def use_template(self, template_id: str, variables: Dict[str, str]) -> str:
        """Use template with variables"""
        try:
            template = self.templates.get(template_id)
            if not template:
                return ""
            
            # Replace variables in template content
            content = template.content
            for variable, value in variables.items():
                content = content.replace(f"{{{variable}}}", value)
            
            # Update usage count
            template.usage_count += 1
            
            return content
            
        except Exception as e:
            logger.error(f"Error using template: {str(e)}")
            return ""
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get AI assistant analytics"""
        try:
            return {
                'total_conversations': len(self.conversations),
                'active_conversations': len([c for c in self.conversations.values() if c.is_active]),
                'total_templates': len(self.templates),
                'public_templates': len([t for t in self.templates.values() if t.is_public]),
                'total_requests': 0,  # Would track actual requests
                'average_confidence': 0.0,  # Would calculate from actual data
                'most_used_templates': sorted(
                    [t for t in self.templates.values() if t.is_public],
                    key=lambda x: x.usage_count,
                    reverse=True
                )[:5]
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}

# Global AI assistant instance
ai_assistant = AIAssistant()
