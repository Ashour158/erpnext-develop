# WhatsApp AI Message Analyzer
# Advanced AI-powered message analysis and intent classification

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import time
import hashlib
import hmac
import base64
from urllib.parse import urlencode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentType(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"

class UrgencyLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class LanguageType(Enum):
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    ARABIC = "ar"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"

@dataclass
class MessageAnalysis:
    message_id: str
    content: str
    intent: str
    confidence: float
    sentiment: SentimentType
    urgency: UrgencyLevel
    language: LanguageType
    entities: List[Dict[str, Any]]
    keywords: List[str]
    categories: List[str]
    priority_score: float
    response_suggestions: List[str]
    follow_up_required: bool
    escalation_needed: bool
    metadata: Dict[str, Any]

@dataclass
class ConversationContext:
    contact_id: str
    conversation_history: List[Dict[str, Any]]
    customer_profile: Dict[str, Any]
    previous_intents: List[str]
    satisfaction_score: float
    last_interaction: datetime
    preferred_language: LanguageType
    communication_style: str

class WhatsAppAIAnalyzer:
    """
    Advanced AI-powered WhatsApp message analyzer
    Provides intelligent message analysis, intent classification, and response suggestions
    """
    
    def __init__(self, openai_api_key: str = None, anthropic_api_key: str = None):
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key
        self.analysis_cache = {}
        self.conversation_contexts = {}
        
        # Initialize AI models
        self._initialize_models()
        
        # Start background processing
        self._start_background_processing()
    
    def _initialize_models(self):
        """Initialize AI models and patterns"""
        # Intent classification patterns
        self.intent_patterns = {
            'lead_inquiry': [
                r'\b(price|cost|quote|buy|purchase|interested|product|service|information|details|catalog|brochure)\b',
                r'\b(how much|what is the price|can i buy|where can i get|tell me about)\b',
                r'\b(availability|in stock|delivery|shipping|payment)\b'
            ],
            'support_ticket': [
                r'\b(help|support|issue|problem|error|bug|not working|broken|fix|repair|technical|troubleshoot)\b',
                r'\b(can\'t|unable to|doesn\'t work|stopped working|not responding)\b',
                r'\b(how to|how do i|what should i do|need help with)\b'
            ],
            'complaint': [
                r'\b(complaint|dissatisfied|unhappy|angry|frustrated|disappointed|poor service|bad experience|refund)\b',
                r'\b(terrible|awful|worst|horrible|disgusting|unacceptable)\b',
                r'\b(want my money back|cancel|stop|never again)\b'
            ],
            'order_inquiry': [
                r'\b(order|delivery|shipping|track|status|when|where|dispatch|arrive)\b',
                r'\b(my order|order number|tracking|delivery date|when will it arrive)\b',
                r'\b(update|change|modify|cancel order)\b'
            ],
            'payment_inquiry': [
                r'\b(payment|invoice|bill|charge|fee|money|transaction|receipt)\b',
                r'\b(paid|payment failed|billing|credit card|bank transfer)\b',
                r'\b(refund|charge back|dispute|fraud)\b'
            ],
            'appointment_request': [
                r'\b(appointment|meeting|schedule|book|reserve|visit|consultation|demo)\b',
                r'\b(available|free|time|calendar|when can we meet)\b',
                r'\b(call|phone|video|zoom|teams)\b'
            ],
            'feedback': [
                r'\b(feedback|review|rating|opinion|suggestion|recommend|improve)\b',
                r'\b(like|love|enjoy|satisfied|happy|pleased)\b',
                r'\b(thank you|thanks|appreciate|grateful)\b'
            ],
            'spam': [
                r'\b(spam|scam|fake|bot|automated|promotional)\b',
                r'\b(click here|free money|win|prize|lottery)\b',
                r'\b(urgent|act now|limited time|exclusive offer)\b'
            ]
        }
        
        # Sentiment analysis patterns
        self.sentiment_patterns = {
            'positive': [
                r'\b(good|great|excellent|amazing|wonderful|fantastic|perfect|love|like|enjoy|happy|pleased|satisfied)\b',
                r'\b(thank you|thanks|appreciate|grateful|blessed|fortunate)\b'
            ],
            'negative': [
                r'\b(bad|terrible|awful|horrible|disgusting|hate|dislike|angry|frustrated|disappointed|upset)\b',
                r'\b(problem|issue|error|bug|broken|not working|failed)\b'
            ],
            'angry': [
                r'\b(angry|mad|furious|rage|irritated|annoyed|pissed|fuming)\b',
                r'\b(damn|hell|shit|fuck|bitch|asshole)\b'
            ],
            'frustrated': [
                r'\b(frustrated|annoyed|irritated|fed up|tired of|sick of)\b',
                r'\b(why|how|what|seriously|really|come on)\b'
            ],
            'excited': [
                r'\b(excited|thrilled|ecstatic|overjoyed|delighted|elated)\b',
                r'\b(wow|awesome|cool|amazing|incredible|fantastic)\b'
            ]
        }
        
        # Urgency detection patterns
        self.urgency_patterns = {
            'urgent': [
                r'\b(urgent|asap|immediately|right now|emergency|critical|important)\b',
                r'\b(help|assist|support|issue|problem|error|bug)\b'
            ],
            'high': [
                r'\b(soon|quickly|fast|priority|important|need|require)\b',
                r'\b(deadline|due|schedule|appointment|meeting)\b'
            ],
            'medium': [
                r'\b(when|where|how|what|information|details|question)\b',
                r'\b(available|possible|can you|could you)\b'
            ],
            'low': [
                r'\b(just|only|simple|basic|general|curious|wondering)\b',
                r'\b(if|maybe|perhaps|might|could|would)\b'
            ]
        }
        
        # Language detection patterns
        self.language_patterns = {
            'en': [r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b'],
            'es': [r'\b(el|la|los|las|de|del|en|con|por|para|que|como)\b'],
            'fr': [r'\b(le|la|les|de|du|des|en|avec|pour|que|comme)\b'],
            'de': [r'\b(der|die|das|und|oder|aber|in|auf|mit|für|von)\b'],
            'it': [r'\b(il|la|i|le|di|del|della|in|con|per|che|come)\b'],
            'pt': [r'\b(o|a|os|as|de|do|da|em|com|para|que|como)\b'],
            'ar': [r'[\u0600-\u06FF]'],
            'zh': [r'[\u4e00-\u9fff]'],
            'ja': [r'[\u3040-\u309f\u30a0-\u30ff]'],
            'ko': [r'[\uac00-\ud7af]']
        }
    
    def _start_background_processing(self):
        """Start background processing for AI analysis"""
        self.processing_queue = queue.Queue()
        self.is_processing = True
        
        # Start processing threads
        for i in range(2):  # 2 AI processing threads
            thread = threading.Thread(target=self._process_ai_analysis, daemon=True)
            thread.start()
    
    def _process_ai_analysis(self):
        """Process AI analysis in background"""
        while self.is_processing:
            try:
                analysis_request = self.processing_queue.get(timeout=1)
                self._perform_ai_analysis(analysis_request)
                self.processing_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in AI analysis: {str(e)}")
    
    async def analyze_message(self, message_id: str, content: str, contact_id: str = None) -> MessageAnalysis:
        """
        Analyze WhatsApp message using AI
        Returns comprehensive message analysis
        """
        try:
            # Check cache first
            cache_key = hashlib.md5(f"{message_id}_{content}".encode()).hexdigest()
            if cache_key in self.analysis_cache:
                return self.analysis_cache[cache_key]
            
            # Get conversation context
            context = self._get_conversation_context(contact_id) if contact_id else None
            
            # Perform analysis
            analysis = await self._perform_comprehensive_analysis(
                message_id, content, context
            )
            
            # Cache result
            self.analysis_cache[cache_key] = analysis
            
            # Update conversation context
            if context:
                self._update_conversation_context(contact_id, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing message: {str(e)}")
            return self._create_default_analysis(message_id, content)
    
    async def _perform_comprehensive_analysis(self, message_id: str, content: str, context: ConversationContext = None) -> MessageAnalysis:
        """Perform comprehensive message analysis"""
        try:
            # Basic text preprocessing
            processed_content = self._preprocess_text(content)
            
            # Intent classification
            intent_result = await self._classify_intent(processed_content, context)
            
            # Sentiment analysis
            sentiment_result = await self._analyze_sentiment(processed_content, context)
            
            # Urgency detection
            urgency_result = await self._detect_urgency(processed_content, context)
            
            # Language detection
            language_result = await self._detect_language(processed_content)
            
            # Entity extraction
            entities = await self._extract_entities(processed_content)
            
            # Keyword extraction
            keywords = await self._extract_keywords(processed_content)
            
            # Category classification
            categories = await self._classify_categories(processed_content, intent_result['intent'])
            
            # Priority scoring
            priority_score = await self._calculate_priority_score(
                intent_result, sentiment_result, urgency_result, context
            )
            
            # Response suggestions
            response_suggestions = await self._generate_response_suggestions(
                intent_result, sentiment_result, context
            )
            
            # Follow-up determination
            follow_up_required = await self._determine_follow_up_required(
                intent_result, sentiment_result, context
            )
            
            # Escalation determination
            escalation_needed = await self._determine_escalation_needed(
                intent_result, sentiment_result, urgency_result, context
            )
            
            return MessageAnalysis(
                message_id=message_id,
                content=content,
                intent=intent_result['intent'],
                confidence=intent_result['confidence'],
                sentiment=sentiment_result['sentiment'],
                urgency=urgency_result['urgency'],
                language=language_result['language'],
                entities=entities,
                keywords=keywords,
                categories=categories,
                priority_score=priority_score,
                response_suggestions=response_suggestions,
                follow_up_required=follow_up_required,
                escalation_needed=escalation_needed,
                metadata={
                    'processed_content': processed_content,
                    'analysis_timestamp': datetime.now().isoformat(),
                    'context_used': context is not None
                }
            )
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            return self._create_default_analysis(message_id, content)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?]', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        return text.strip()
    
    async def _classify_intent(self, content: str, context: ConversationContext = None) -> Dict[str, Any]:
        """Classify message intent"""
        try:
            intent_scores = {}
            
            # Calculate scores for each intent
            for intent, patterns in self.intent_patterns.items():
                score = 0
                for pattern in patterns:
                    matches = len(re.findall(pattern, content, re.IGNORECASE))
                    score += matches
                
                # Normalize score
                intent_scores[intent] = score / len(patterns) if patterns else 0
            
            # Apply context boost
            if context and context.previous_intents:
                for prev_intent in context.previous_intents:
                    if prev_intent in intent_scores:
                        intent_scores[prev_intent] *= 1.2  # 20% boost for context
            
            # Find best intent
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
            
            # Use AI model for complex cases
            if confidence < 0.3 and self.openai_api_key:
                ai_result = await self._ai_classify_intent(content, context)
                if ai_result['confidence'] > confidence:
                    return ai_result
            
            return {
                'intent': best_intent,
                'confidence': min(confidence, 1.0),
                'scores': intent_scores
            }
            
        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}")
            return {'intent': 'general_question', 'confidence': 0.0, 'scores': {}}
    
    async def _analyze_sentiment(self, content: str, context: ConversationContext = None) -> Dict[str, Any]:
        """Analyze message sentiment"""
        try:
            sentiment_scores = {}
            
            # Calculate scores for each sentiment
            for sentiment, patterns in self.sentiment_patterns.items():
                score = 0
                for pattern in patterns:
                    matches = len(re.findall(pattern, content, re.IGNORECASE))
                    score += matches
                
                sentiment_scores[sentiment] = score / len(patterns) if patterns else 0
            
            # Find best sentiment
            best_sentiment = max(sentiment_scores, key=sentiment_scores.get)
            confidence = sentiment_scores[best_sentiment]
            
            # Use AI model for complex cases
            if confidence < 0.3 and self.openai_api_key:
                ai_result = await self._ai_analyze_sentiment(content, context)
                if ai_result['confidence'] > confidence:
                    return ai_result
            
            return {
                'sentiment': SentimentType(best_sentiment),
                'confidence': min(confidence, 1.0),
                'scores': sentiment_scores
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {'sentiment': SentimentType.NEUTRAL, 'confidence': 0.0, 'scores': {}}
    
    async def _detect_urgency(self, content: str, context: ConversationContext = None) -> Dict[str, Any]:
        """Detect message urgency"""
        try:
            urgency_scores = {}
            
            # Calculate scores for each urgency level
            for urgency, patterns in self.urgency_patterns.items():
                score = 0
                for pattern in patterns:
                    matches = len(re.findall(pattern, content, re.IGNORECASE))
                    score += matches
                
                urgency_scores[urgency] = score / len(patterns) if patterns else 0
            
            # Find best urgency
            best_urgency = max(urgency_scores, key=urgency_scores.get)
            confidence = urgency_scores[best_urgency]
            
            return {
                'urgency': UrgencyLevel(best_urgency),
                'confidence': min(confidence, 1.0),
                'scores': urgency_scores
            }
            
        except Exception as e:
            logger.error(f"Error detecting urgency: {str(e)}")
            return {'urgency': UrgencyLevel.MEDIUM, 'confidence': 0.0, 'scores': {}}
    
    async def _detect_language(self, content: str) -> Dict[str, Any]:
        """Detect message language"""
        try:
            language_scores = {}
            
            # Calculate scores for each language
            for language, patterns in self.language_patterns.items():
                score = 0
                for pattern in patterns:
                    matches = len(re.findall(pattern, content, re.IGNORECASE))
                    score += matches
                
                language_scores[language] = score / len(patterns) if patterns else 0
            
            # Find best language
            best_language = max(language_scores, key=language_scores.get)
            confidence = language_scores[best_language]
            
            return {
                'language': LanguageType(best_language),
                'confidence': min(confidence, 1.0),
                'scores': language_scores
            }
            
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return {'language': LanguageType.ENGLISH, 'confidence': 0.0, 'scores': {}}
    
    async def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract entities from message"""
        try:
            entities = []
            
            # Extract phone numbers
            phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            phones = re.findall(phone_pattern, content)
            for phone in phones:
                entities.append({
                    'type': 'phone',
                    'value': phone,
                    'confidence': 0.9
                })
            
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, content)
            for email in emails:
                entities.append({
                    'type': 'email',
                    'value': email,
                    'confidence': 0.9
                })
            
            # Extract URLs
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, content)
            for url in urls:
                entities.append({
                    'type': 'url',
                    'value': url,
                    'confidence': 0.9
                })
            
            # Extract monetary amounts
            money_pattern = r'\$?\d+(?:\.\d{2})?(?:\s*(?:dollars?|USD|euros?|EUR|pounds?|GBP))?'
            money = re.findall(money_pattern, content)
            for amount in money:
                entities.append({
                    'type': 'money',
                    'value': amount,
                    'confidence': 0.8
                })
            
            # Extract dates
            date_pattern = r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s+\d{4})?\b'
            dates = re.findall(date_pattern, content, re.IGNORECASE)
            for date in dates:
                entities.append({
                    'type': 'date',
                    'value': date,
                    'confidence': 0.7
                })
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return []
    
    async def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from message"""
        try:
            # Simple keyword extraction
            words = content.split()
            
            # Filter out common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
                'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
            }
            
            keywords = [word for word in words if word not in stop_words and len(word) > 2]
            
            # Count frequency
            keyword_counts = {}
            for keyword in keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            # Sort by frequency and return top keywords
            sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
            return [keyword for keyword, count in sorted_keywords[:10]]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    async def _classify_categories(self, content: str, intent: str) -> List[str]:
        """Classify message categories"""
        try:
            categories = []
            
            # Add intent as category
            categories.append(intent)
            
            # Add sentiment-based categories
            if 'angry' in content.lower() or 'frustrated' in content.lower():
                categories.append('emotional')
            
            if 'urgent' in content.lower() or 'asap' in content.lower():
                categories.append('time_sensitive')
            
            if 'refund' in content.lower() or 'money' in content.lower():
                categories.append('financial')
            
            if 'technical' in content.lower() or 'bug' in content.lower():
                categories.append('technical')
            
            if 'delivery' in content.lower() or 'shipping' in content.lower():
                categories.append('logistics')
            
            return list(set(categories))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error classifying categories: {str(e)}")
            return [intent]
    
    async def _calculate_priority_score(self, intent_result: Dict, sentiment_result: Dict, urgency_result: Dict, context: ConversationContext = None) -> float:
        """Calculate priority score for message"""
        try:
            score = 0.0
            
            # Base score from intent
            intent_weights = {
                'complaint': 0.9,
                'support_ticket': 0.7,
                'lead_inquiry': 0.5,
                'order_inquiry': 0.6,
                'payment_inquiry': 0.8,
                'appointment_request': 0.4,
                'feedback': 0.3,
                'spam': 0.1,
                'general_question': 0.4
            }
            score += intent_weights.get(intent_result['intent'], 0.5) * intent_result['confidence']
            
            # Sentiment boost
            sentiment_weights = {
                'angry': 0.9,
                'frustrated': 0.8,
                'negative': 0.7,
                'neutral': 0.5,
                'positive': 0.3,
                'excited': 0.2
            }
            score += sentiment_weights.get(sentiment_result['sentiment'].value, 0.5) * sentiment_result['confidence']
            
            # Urgency boost
            urgency_weights = {
                'critical': 0.9,
                'urgent': 0.8,
                'high': 0.6,
                'medium': 0.4,
                'low': 0.2
            }
            score += urgency_weights.get(urgency_result['urgency'].value, 0.5) * urgency_result['confidence']
            
            # Context boost
            if context:
                if context.satisfaction_score < 0.3:  # Unhappy customer
                    score += 0.2
                if context.escalation_needed:
                    score += 0.3
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error calculating priority score: {str(e)}")
            return 0.5
    
    async def _generate_response_suggestions(self, intent_result: Dict, sentiment_result: Dict, context: ConversationContext = None) -> List[str]:
        """Generate response suggestions"""
        try:
            suggestions = []
            
            intent = intent_result['intent']
            sentiment = sentiment_result['sentiment'].value
            
            # Intent-based suggestions
            if intent == 'lead_inquiry':
                suggestions.extend([
                    "Thank you for your interest! I'd be happy to provide you with more information about our products/services.",
                    "I'll connect you with our sales team who can provide you with a detailed quote.",
                    "Let me gather some information about your requirements to better assist you."
                ])
            elif intent == 'support_ticket':
                suggestions.extend([
                    "I understand you're experiencing an issue. Let me help you resolve this.",
                    "I'll create a support ticket for you and our technical team will investigate.",
                    "Can you provide more details about the problem you're experiencing?"
                ])
            elif intent == 'complaint':
                suggestions.extend([
                    "I sincerely apologize for the inconvenience. Let me address this immediately.",
                    "I understand your frustration. Let me escalate this to our management team.",
                    "I want to make this right. Let me connect you with someone who can help resolve this."
                ])
            elif intent == 'order_inquiry':
                suggestions.extend([
                    "Let me check the status of your order for you.",
                    "I'll look into your order and provide you with an update.",
                    "Can you provide your order number so I can track it for you?"
                ])
            elif intent == 'payment_inquiry':
                suggestions.extend([
                    "Let me check your payment status and provide you with details.",
                    "I'll connect you with our finance team to resolve any payment issues.",
                    "Can you provide your invoice number so I can look into this?"
                ])
            
            # Sentiment-based suggestions
            if sentiment in ['angry', 'frustrated']:
                suggestions.extend([
                    "I understand you're upset, and I want to help resolve this for you.",
                    "I apologize for any frustration this has caused. Let me make this right.",
                    "I hear your concerns, and I'm committed to finding a solution."
                ])
            elif sentiment == 'positive':
                suggestions.extend([
                    "I'm glad to hear you're happy with our service!",
                    "Thank you for your positive feedback!",
                    "I'm delighted that we could help you!"
                ])
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error generating response suggestions: {str(e)}")
            return ["Thank you for your message. How can I help you today?"]
    
    async def _determine_follow_up_required(self, intent_result: Dict, sentiment_result: Dict, context: ConversationContext = None) -> bool:
        """Determine if follow-up is required"""
        try:
            intent = intent_result['intent']
            sentiment = sentiment_result['sentiment'].value
            
            # High-priority intents require follow-up
            if intent in ['complaint', 'support_ticket', 'payment_inquiry']:
                return True
            
            # Negative sentiment requires follow-up
            if sentiment in ['angry', 'frustrated', 'negative']:
                return True
            
            # Context-based follow-up
            if context and context.satisfaction_score < 0.5:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error determining follow-up: {str(e)}")
            return False
    
    async def _determine_escalation_needed(self, intent_result: Dict, sentiment_result: Dict, urgency_result: Dict, context: ConversationContext = None) -> bool:
        """Determine if escalation is needed"""
        try:
            intent = intent_result['intent']
            sentiment = sentiment_result['sentiment'].value
            urgency = urgency_result['urgency'].value
            
            # High-priority intents need escalation
            if intent == 'complaint' and sentiment in ['angry', 'frustrated']:
                return True
            
            # Urgent messages need escalation
            if urgency in ['urgent', 'critical']:
                return True
            
            # Context-based escalation
            if context and context.satisfaction_score < 0.3:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error determining escalation: {str(e)}")
            return False
    
    async def _ai_classify_intent(self, content: str, context: ConversationContext = None) -> Dict[str, Any]:
        """Use AI model to classify intent"""
        try:
            if not self.openai_api_key:
                return {'intent': 'general_question', 'confidence': 0.0}
            
            # This would integrate with OpenAI API
            # For now, return default
            return {'intent': 'general_question', 'confidence': 0.0}
            
        except Exception as e:
            logger.error(f"Error in AI intent classification: {str(e)}")
            return {'intent': 'general_question', 'confidence': 0.0}
    
    async def _ai_analyze_sentiment(self, content: str, context: ConversationContext = None) -> Dict[str, Any]:
        """Use AI model to analyze sentiment"""
        try:
            if not self.openai_api_key:
                return {'sentiment': SentimentType.NEUTRAL, 'confidence': 0.0}
            
            # This would integrate with OpenAI API
            # For now, return default
            return {'sentiment': SentimentType.NEUTRAL, 'confidence': 0.0}
            
        except Exception as e:
            logger.error(f"Error in AI sentiment analysis: {str(e)}")
            return {'sentiment': SentimentType.NEUTRAL, 'confidence': 0.0}
    
    def _get_conversation_context(self, contact_id: str) -> Optional[ConversationContext]:
        """Get conversation context for contact"""
        try:
            return self.conversation_contexts.get(contact_id)
        except Exception as e:
            logger.error(f"Error getting conversation context: {str(e)}")
            return None
    
    def _update_conversation_context(self, contact_id: str, analysis: MessageAnalysis):
        """Update conversation context"""
        try:
            if contact_id not in self.conversation_contexts:
                self.conversation_contexts[contact_id] = ConversationContext(
                    contact_id=contact_id,
                    conversation_history=[],
                    customer_profile={},
                    previous_intents=[],
                    satisfaction_score=0.5,
                    last_interaction=datetime.now(),
                    preferred_language=analysis.language,
                    communication_style='neutral'
                )
            
            context = self.conversation_contexts[contact_id]
            
            # Update context with new analysis
            context.previous_intents.append(analysis.intent)
            context.last_interaction = datetime.now()
            context.preferred_language = analysis.language
            
            # Update satisfaction score based on sentiment
            if analysis.sentiment == SentimentType.POSITIVE:
                context.satisfaction_score = min(context.satisfaction_score + 0.1, 1.0)
            elif analysis.sentiment in [SentimentType.NEGATIVE, SentimentType.ANGRY]:
                context.satisfaction_score = max(context.satisfaction_score - 0.1, 0.0)
            
            # Update communication style
            if analysis.sentiment == SentimentType.ANGRY:
                context.communication_style = 'aggressive'
            elif analysis.sentiment == SentimentType.POSITIVE:
                context.communication_style = 'friendly'
            else:
                context.communication_style = 'neutral'
            
        except Exception as e:
            logger.error(f"Error updating conversation context: {str(e)}")
    
    def _create_default_analysis(self, message_id: str, content: str) -> MessageAnalysis:
        """Create default analysis when errors occur"""
        return MessageAnalysis(
            message_id=message_id,
            content=content,
            intent='general_question',
            confidence=0.0,
            sentiment=SentimentType.NEUTRAL,
            urgency=UrgencyLevel.MEDIUM,
            language=LanguageType.ENGLISH,
            entities=[],
            keywords=[],
            categories=['general'],
            priority_score=0.5,
            response_suggestions=["Thank you for your message. How can I help you today?"],
            follow_up_required=False,
            escalation_needed=False,
            metadata={'error': 'Default analysis due to processing error'}
        )
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get AI analyzer analytics"""
        try:
            return {
                'total_analyses': len(self.analysis_cache),
                'active_contexts': len(self.conversation_contexts),
                'cache_hit_rate': 0.0,  # Would calculate actual hit rate
                'avg_processing_time': 0.0,  # Would calculate actual processing time
                'model_accuracy': 0.0  # Would calculate actual accuracy
            }
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}

# Global AI Analyzer instance
whatsapp_ai_analyzer = WhatsAppAIAnalyzer()
