# Omnichannel Customer Engagement
# Advanced omnichannel capabilities to surpass Zoho CRM and Salesforce

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class ChannelType(enum.Enum):
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"
    CHAT = "chat"
    SOCIAL_MEDIA = "social_media"
    WEBSITE = "website"
    MOBILE_APP = "mobile_app"
    VIDEO_CALL = "video_call"
    IN_PERSON = "in_person"
    MAIL = "mail"

class EngagementStatus(enum.Enum):
    ACTIVE = "active"
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class Priority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class Sentiment(enum.Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

# Unified Customer Communication
class CustomerCommunication(Base):
    __tablename__ = 'customer_communications'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    
    # Communication Details
    channel = Column(Enum(ChannelType), nullable=False)
    direction = Column(String(20), nullable=False)  # inbound, outbound
    subject = Column(String(255))
    content = Column(Text, nullable=False)
    
    # Communication Metadata
    communication_id = Column(String(100))  # External system ID
    thread_id = Column(String(100))  # Conversation thread ID
    parent_communication_id = Column(Integer, ForeignKey('customer_communications.id'))
    
    # Status and Priority
    status = Column(Enum(EngagementStatus), default=EngagementStatus.ACTIVE)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Sentiment Analysis
    sentiment = Column(Enum(Sentiment))
    sentiment_score = Column(Float)  # -1 to 1
    emotion_tags = Column(JSON)  # Detected emotions
    intent_classification = Column(JSON)  # Classified intents
    
    # Response Management
    requires_response = Column(Boolean, default=False)
    response_deadline = Column(DateTime)
    assigned_to = Column(Integer, ForeignKey('users.id'))
    response_template = Column(String(255))
    
    # Engagement Metrics
    engagement_score = Column(Float, default=0.0)  # 0-100
    response_time = Column(Integer)  # Minutes to response
    resolution_time = Column(Integer)  # Minutes to resolution
    satisfaction_score = Column(Float)  # 0-100
    
    # Attachments and Media
    attachments = Column(JSON)  # File attachments
    media_files = Column(JSON)  # Media files
    links = Column(JSON)  # Related links
    
    # Automation
    is_automated = Column(Boolean, default=False)
    automation_rule_id = Column(Integer, ForeignKey('automation_rules.id'))
    automation_trigger = Column(String(100))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    customer = relationship("Customer")
    contact = relationship("Contact")
    assigned_user = relationship("User")
    parent_communication = relationship("CustomerCommunication", remote_side=[id])
    automation_rule = relationship("AutomationRule")

# Social Media Integration
class SocialMediaIntegration(Base):
    __tablename__ = 'social_media_integrations'
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)  # facebook, twitter, linkedin, instagram
    account_id = Column(String(100), nullable=False)  # Social media account ID
    account_name = Column(String(255), nullable=False)
    
    # Integration Settings
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)
    webhook_url = Column(String(255))
    webhook_secret = Column(String(255))
    
    # Platform Configuration
    platform_config = Column(JSON)  # Platform-specific configuration
    sync_settings = Column(JSON)  # Sync settings
    filtering_rules = Column(JSON)  # Content filtering rules
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    sync_status = Column(String(20), default='active')  # active, paused, error
    error_message = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    posts = relationship("SocialMediaPost", back_populates="integration")

# Social Media Posts
class SocialMediaPost(Base):
    __tablename__ = 'social_media_posts'
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey('social_media_integrations.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    
    # Post Details
    post_id = Column(String(100), nullable=False)  # Platform post ID
    post_type = Column(String(50))  # text, image, video, link
    content = Column(Text, nullable=False)
    media_urls = Column(JSON)  # Media file URLs
    
    # Engagement Metrics
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    
    # Sentiment Analysis
    sentiment = Column(Enum(Sentiment))
    sentiment_score = Column(Float)
    emotion_tags = Column(JSON)
    
    # Response Management
    requires_response = Column(Boolean, default=False)
    is_responded = Column(Boolean, default=False)
    response_content = Column(Text)
    response_sentiment = Column(Enum(Sentiment))
    
    # Metadata
    posted_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    integration = relationship("SocialMediaIntegration", back_populates="posts")
    customer = relationship("Customer")

# Live Chat Integration
class LiveChatSession(Base):
    __tablename__ = 'live_chat_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    
    # Session Details
    visitor_id = Column(String(100))  # Anonymous visitor ID
    visitor_name = Column(String(255))
    visitor_email = Column(String(255))
    visitor_phone = Column(String(20))
    
    # Session Status
    status = Column(Enum(EngagementStatus), default=EngagementStatus.ACTIVE)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    assigned_agent = Column(Integer, ForeignKey('users.id'))
    
    # Session Metrics
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration = Column(Integer)  # Seconds
    message_count = Column(Integer, default=0)
    response_time = Column(Integer)  # Average response time in seconds
    
    # Session Context
    page_url = Column(String(500))  # Page where chat started
    referrer_url = Column(String(500))
    user_agent = Column(Text)
    ip_address = Column(String(45))
    location = Column(JSON)  # Geographic location
    
    # Session Data
    session_data = Column(JSON)  # Additional session data
    tags = Column(JSON)  # Session tags
    notes = Column(Text)  # Agent notes
    
    # Satisfaction
    satisfaction_score = Column(Float)  # 0-100
    satisfaction_feedback = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    customer = relationship("Customer")
    agent = relationship("User")
    messages = relationship("ChatMessage", back_populates="session")

# Chat Messages
class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('live_chat_sessions.id'), nullable=False)
    
    # Message Details
    message_id = Column(String(100), unique=True, nullable=False)
    sender_type = Column(String(20), nullable=False)  # customer, agent, system
    sender_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text, nullable=False)
    
    # Message Metadata
    message_type = Column(String(50), default='text')  # text, image, file, system
    attachments = Column(JSON)  # File attachments
    media_urls = Column(JSON)  # Media URLs
    
    # Message Status
    is_read = Column(Boolean, default=False)
    is_delivered = Column(Boolean, default=True)
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime)
    
    # Sentiment Analysis
    sentiment = Column(Enum(Sentiment))
    sentiment_score = Column(Float)
    emotion_tags = Column(JSON)
    
    # Metadata
    sent_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    session = relationship("LiveChatSession", back_populates="messages")
    sender = relationship("User")

# Email Integration
class EmailIntegration(Base):
    __tablename__ = 'email_integrations'
    
    id = Column(Integer, primary_key=True, index=True)
    email_provider = Column(String(50), nullable=False)  # gmail, outlook, exchange
    email_address = Column(String(255), nullable=False)
    
    # Authentication
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)
    
    # Configuration
    provider_config = Column(JSON)  # Provider-specific configuration
    sync_settings = Column(JSON)  # Email sync settings
    filtering_rules = Column(JSON)  # Email filtering rules
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    sync_status = Column(String(20), default='active')
    error_message = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))

# Email Communications
class EmailCommunication(Base):
    __tablename__ = 'email_communications'
    
    id = Column(Integer, primary_key=True, index=True)
    communication_id = Column(Integer, ForeignKey('customer_communications.id'), nullable=False)
    email_integration_id = Column(Integer, ForeignKey('email_integrations.id'), nullable=False)
    
    # Email Details
    message_id = Column(String(255), unique=True, nullable=False)
    thread_id = Column(String(255))
    subject = Column(String(500))
    sender_email = Column(String(255), nullable=False)
    recipient_email = Column(String(255), nullable=False)
    
    # Email Content
    html_content = Column(Text)
    text_content = Column(Text)
    attachments = Column(JSON)
    inline_images = Column(JSON)
    
    # Email Status
    is_read = Column(Boolean, default=False)
    is_replied = Column(Boolean, default=False)
    is_forwarded = Column(Boolean, default=False)
    is_important = Column(Boolean, default=False)
    
    # Email Metrics
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    forward_count = Column(Integer, default=0)
    
    # Metadata
    sent_at = Column(DateTime, nullable=False)
    received_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    communication = relationship("CustomerCommunication")
    email_integration = relationship("EmailIntegration")

# Phone Integration
class PhoneIntegration(Base):
    __tablename__ = 'phone_integrations'
    
    id = Column(Integer, primary_key=True, index=True)
    phone_provider = Column(String(50), nullable=False)  # twilio, vonage, ringcentral
    phone_number = Column(String(20), nullable=False)
    
    # Provider Configuration
    provider_config = Column(JSON, nullable=False)
    api_credentials = Column(JSON, nullable=False)
    
    # Features
    call_recording = Column(Boolean, default=True)
    call_transcription = Column(Boolean, default=True)
    voicemail = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    sync_status = Column(String(20), default='active')
    error_message = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))

# Phone Calls
class PhoneCall(Base):
    __tablename__ = 'phone_calls'
    
    id = Column(Integer, primary_key=True, index=True)
    communication_id = Column(Integer, ForeignKey('customer_communications.id'), nullable=False)
    phone_integration_id = Column(Integer, ForeignKey('phone_integrations.id'), nullable=False)
    
    # Call Details
    call_sid = Column(String(100), unique=True, nullable=False)
    from_number = Column(String(20), nullable=False)
    to_number = Column(String(20), nullable=False)
    call_direction = Column(String(20), nullable=False)  # inbound, outbound
    
    # Call Status
    call_status = Column(String(20), nullable=False)  # initiated, ringing, in-progress, completed, failed
    call_duration = Column(Integer)  # Seconds
    call_cost = Column(Float)  # Cost of the call
    
    # Call Recording
    recording_url = Column(String(500))
    recording_duration = Column(Integer)  # Seconds
    transcription = Column(Text)
    transcription_confidence = Column(Float)
    
    # Call Quality
    call_quality_score = Column(Float)  # 0-100
    audio_quality = Column(String(20))  # excellent, good, fair, poor
    connection_quality = Column(String(20))  # excellent, good, fair, poor
    
    # Metadata
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    communication = relationship("CustomerCommunication")
    phone_integration = relationship("PhoneIntegration")

# SMS Integration
class SMSIntegration(Base):
    __tablename__ = 'sms_integrations'
    
    id = Column(Integer, primary_key=True, index=True)
    sms_provider = Column(String(50), nullable=False)  # twilio, vonage, messagebird
    phone_number = Column(String(20), nullable=False)
    
    # Provider Configuration
    provider_config = Column(JSON, nullable=False)
    api_credentials = Column(JSON, nullable=False)
    
    # Features
    two_way_sms = Column(Boolean, default=True)
    mms_enabled = Column(Boolean, default=True)
    delivery_reports = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    sync_status = Column(String(20), default='active')
    error_message = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))

# SMS Messages
class SMSMessage(Base):
    __tablename__ = 'sms_messages'
    
    id = Column(Integer, primary_key=True, index=True)
    communication_id = Column(Integer, ForeignKey('customer_communications.id'), nullable=False)
    sms_integration_id = Column(Integer, ForeignKey('sms_integrations.id'), nullable=False)
    
    # SMS Details
    message_sid = Column(String(100), unique=True, nullable=False)
    from_number = Column(String(20), nullable=False)
    to_number = Column(String(20), nullable=False)
    message_direction = Column(String(20), nullable=False)  # inbound, outbound
    
    # Message Content
    message_body = Column(Text, nullable=False)
    media_urls = Column(JSON)  # MMS media URLs
    
    # Message Status
    message_status = Column(String(20), nullable=False)  # sent, delivered, failed, received
    delivery_status = Column(String(20))  # delivered, failed, pending
    error_code = Column(String(50))
    error_message = Column(Text)
    
    # Message Metrics
    delivery_time = Column(Integer)  # Seconds to delivery
    read_receipt = Column(Boolean, default=False)
    read_at = Column(DateTime)
    
    # Metadata
    sent_at = Column(DateTime, nullable=False)
    delivered_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    communication = relationship("CustomerCommunication")
    sms_integration = relationship("SMSIntegration")

# Automation Rules
class AutomationRule(Base):
    __tablename__ = 'automation_rules'
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(255), nullable=False)
    rule_description = Column(Text)
    
    # Rule Configuration
    trigger_conditions = Column(JSON, nullable=False)  # When to trigger
    action_conditions = Column(JSON, nullable=False)  # What actions to take
    rule_priority = Column(Integer, default=0)  # Higher number = higher priority
    
    # Rule Settings
    is_active = Column(Boolean, default=True)
    is_global = Column(Boolean, default=False)  # Apply to all customers
    customer_segments = Column(JSON)  # Specific customer segments
    
    # Rule Execution
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_executed = Column(DateTime)
    
    # Rule Performance
    average_execution_time = Column(Float)  # Seconds
    success_rate = Column(Float)  # Percentage
    error_rate = Column(Float)  # Percentage
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Customer Journey Mapping
class CustomerJourney(Base):
    __tablename__ = 'customer_journeys'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    journey_name = Column(String(255), nullable=False)
    
    # Journey Details
    journey_stage = Column(String(50), nullable=False)  # awareness, consideration, purchase, retention, advocacy
    journey_status = Column(String(20), default='active')  # active, completed, abandoned
    
    # Journey Metrics
    touchpoint_count = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)  # 0-100
    satisfaction_score = Column(Float, default=0.0)  # 0-100
    conversion_probability = Column(Float, default=0.0)  # 0-100%
    
    # Journey Timeline
    journey_start = Column(DateTime, nullable=False)
    journey_end = Column(DateTime)
    journey_duration = Column(Integer)  # Days
    
    # Journey Data
    touchpoints = Column(JSON)  # Customer touchpoints
    interactions = Column(JSON)  # Customer interactions
    preferences = Column(JSON)  # Customer preferences
    behaviors = Column(JSON)  # Customer behaviors
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    customer = relationship("Customer")
