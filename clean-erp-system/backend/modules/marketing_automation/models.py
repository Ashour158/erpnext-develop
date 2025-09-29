# Marketing Automation Models
# Comprehensive marketing automation for online and offline activities

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class CampaignType(enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"
    WEB = "web"
    DIRECT_MAIL = "direct_mail"
    TELEMARKETING = "telemarketing"
    EVENTS = "events"
    CONTENT = "content"
    ADVERTISING = "advertising"
    SEO = "seo"
    PPC = "ppc"
    RETARGETING = "retargeting"

class CampaignStatus(enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class LeadSource(enum.Enum):
    WEBSITE = "website"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    REFERRAL = "referral"
    PAID_ADS = "paid_ads"
    ORGANIC_SEARCH = "organic_search"
    DIRECT_MAIL = "direct_mail"
    TELEMARKETING = "telemarketing"
    EVENTS = "events"
    PARTNERS = "partners"
    COLD_OUTREACH = "cold_outreach"

class ContentType(enum.Enum):
    BLOG_POST = "blog_post"
    WHITEPAPER = "whitepaper"
    EBOOK = "ebook"
    CASE_STUDY = "case_study"
    WEBINAR = "webinar"
    VIDEO = "video"
    PODCAST = "podcast"
    INFOGRAPHIC = "infographic"
    CHECKLIST = "checklist"
    TEMPLATE = "template"
    GUIDE = "guide"

# Marketing Campaigns
class MarketingCampaign(Base):
    __tablename__ = 'marketing_campaigns'
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(String(255), nullable=False)
    campaign_description = Column(Text)
    campaign_type = Column(Enum(CampaignType), nullable=False)
    
    # Campaign Configuration
    campaign_objectives = Column(JSON, nullable=False)  # Campaign objectives
    target_audience = Column(JSON, nullable=False)  # Target audience definition
    campaign_budget = Column(Float, default=0.0)
    campaign_duration = Column(Integer)  # Days
    
    # Campaign Schedule
    campaign_start = Column(DateTime, nullable=False)
    campaign_end = Column(DateTime, nullable=False)
    campaign_status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # Campaign Content
    campaign_content = Column(JSON)  # Campaign content and materials
    campaign_creative = Column(JSON)  # Creative assets
    campaign_messaging = Column(JSON)  # Key messages and copy
    
    # Campaign Channels
    campaign_channels = Column(JSON, nullable=False)  # Marketing channels
    channel_config = Column(JSON)  # Channel-specific configuration
    channel_budget = Column(JSON)  # Budget allocation per channel
    
    # Campaign Performance
    campaign_metrics = Column(JSON)  # Campaign performance metrics
    campaign_roi = Column(Float, default=0.0)  # Return on investment
    campaign_conversion_rate = Column(Float, default=0.0)  # Conversion rate
    campaign_cost_per_lead = Column(Float, default=0.0)  # Cost per lead
    
    # Campaign Optimization
    optimization_rules = Column(JSON)  # Optimization rules
    a_b_testing = Column(JSON)  # A/B testing configuration
    performance_insights = Column(JSON)  # Performance insights
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")
    email_campaigns = relationship("EmailCampaign", back_populates="campaign")
    social_campaigns = relationship("SocialMediaCampaign", back_populates="campaign")
    web_campaigns = relationship("WebCampaign", back_populates="campaign")

# Email Marketing
class EmailCampaign(Base):
    __tablename__ = 'email_campaigns'
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey('marketing_campaigns.id'), nullable=False)
    
    # Email Configuration
    email_subject = Column(String(255), nullable=False)
    email_from_name = Column(String(100), nullable=False)
    email_from_email = Column(String(255), nullable=False)
    email_reply_to = Column(String(255))
    
    # Email Content
    email_html = Column(Text)
    email_text = Column(Text)
    email_template = Column(String(255))
    email_preview = Column(Text)
    
    # Email Settings
    email_schedule = Column(DateTime)
    email_timezone = Column(String(50))
    email_frequency = Column(String(50))  # once, daily, weekly, monthly
    email_segments = Column(JSON)  # Email segments
    
    # Email Personalization
    personalization_rules = Column(JSON)  # Personalization rules
    dynamic_content = Column(JSON)  # Dynamic content blocks
    merge_fields = Column(JSON)  # Merge fields
    
    # Email Performance
    emails_sent = Column(Integer, default=0)
    emails_delivered = Column(Integer, default=0)
    emails_opened = Column(Integer, default=0)
    emails_clicked = Column(Integer, default=0)
    emails_bounced = Column(Integer, default=0)
    emails_unsubscribed = Column(Integer, default=0)
    
    # Email Metrics
    open_rate = Column(Float, default=0.0)  # Percentage
    click_rate = Column(Float, default=0.0)  # Percentage
    bounce_rate = Column(Float, default=0.0)  # Percentage
    unsubscribe_rate = Column(Float, default=0.0)  # Percentage
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    campaign = relationship("MarketingCampaign", back_populates="email_campaigns")

# Social Media Marketing
class SocialMediaCampaign(Base):
    __tablename__ = 'social_media_campaigns'
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey('marketing_campaigns.id'), nullable=False)
    
    # Social Media Configuration
    platform = Column(String(50), nullable=False)  # facebook, twitter, linkedin, instagram
    account_id = Column(String(100), nullable=False)
    campaign_objective = Column(String(100))  # awareness, engagement, conversions
    
    # Content Configuration
    content_type = Column(String(50))  # text, image, video, carousel
    content_text = Column(Text)
    content_media = Column(JSON)  # Media files
    content_hashtags = Column(JSON)  # Hashtags
    content_mentions = Column(JSON)  # Mentions
    
    # Targeting Configuration
    target_audience = Column(JSON)  # Target audience settings
    target_demographics = Column(JSON)  # Demographic targeting
    target_interests = Column(JSON)  # Interest targeting
    target_behaviors = Column(JSON)  # Behavioral targeting
    
    # Budget and Bidding
    daily_budget = Column(Float, default=0.0)
    total_budget = Column(Float, default=0.0)
    bid_strategy = Column(String(50))  # cpc, cpm, cpa
    bid_amount = Column(Float, default=0.0)
    
    # Performance Metrics
    impressions = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    engagements = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    
    # Performance Rates
    ctr = Column(Float, default=0.0)  # Click-through rate
    cpm = Column(Float, default=0.0)  # Cost per mille
    cpc = Column(Float, default=0.0)  # Cost per click
    cpa = Column(Float, default=0.0)  # Cost per acquisition
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    campaign = relationship("MarketingCampaign", back_populates="social_campaigns")

# Web Marketing
class WebCampaign(Base):
    __tablename__ = 'web_campaigns'
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey('marketing_campaigns.id'), nullable=False)
    
    # Web Configuration
    campaign_url = Column(String(500), nullable=False)
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_campaign = Column(String(100))
    utm_term = Column(String(100))
    utm_content = Column(String(100))
    
    # Landing Page Configuration
    landing_page_url = Column(String(500))
    landing_page_title = Column(String(255))
    landing_page_content = Column(Text)
    landing_page_conversion_goal = Column(String(100))
    
    # SEO Configuration
    seo_keywords = Column(JSON)  # Target keywords
    seo_meta_title = Column(String(255))
    seo_meta_description = Column(Text)
    seo_meta_tags = Column(JSON)
    
    # PPC Configuration
    ppc_keywords = Column(JSON)  # PPC keywords
    ppc_ad_groups = Column(JSON)  # Ad groups
    ppc_ads = Column(JSON)  # Ad copy
    ppc_budget = Column(Float, default=0.0)
    
    # Performance Metrics
    page_views = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    bounce_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    time_on_page = Column(Float, default=0.0)
    
    # Traffic Sources
    organic_traffic = Column(Integer, default=0)
    paid_traffic = Column(Integer, default=0)
    direct_traffic = Column(Integer, default=0)
    referral_traffic = Column(Integer, default=0)
    social_traffic = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    campaign = relationship("MarketingCampaign", back_populates="web_campaigns")

# Lead Nurturing
class LeadNurturing(Base):
    __tablename__ = 'lead_nurturing'
    
    id = Column(Integer, primary_key=True, index=True)
    nurturing_name = Column(String(255), nullable=False)
    nurturing_description = Column(Text)
    
    # Nurturing Configuration
    nurturing_sequence = Column(JSON, nullable=False)  # Nurturing sequence steps
    nurturing_triggers = Column(JSON, nullable=False)  # Trigger conditions
    nurturing_goals = Column(JSON, nullable=False)  # Nurturing goals
    
    # Target Audience
    target_segments = Column(JSON)  # Target segments
    target_criteria = Column(JSON)  # Target criteria
    exclusion_criteria = Column(JSON)  # Exclusion criteria
    
    # Content Strategy
    content_assets = Column(JSON)  # Content assets
    content_schedule = Column(JSON)  # Content schedule
    content_personalization = Column(JSON)  # Content personalization
    
    # Performance Metrics
    total_leads = Column(Integer, default=0)
    nurtured_leads = Column(Integer, default=0)
    converted_leads = Column(Integer, default=0)
    nurturing_conversion_rate = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Content Marketing
class ContentMarketing(Base):
    __tablename__ = 'content_marketing'
    
    id = Column(Integer, primary_key=True, index=True)
    content_title = Column(String(255), nullable=False)
    content_description = Column(Text)
    content_type = Column(Enum(ContentType), nullable=False)
    
    # Content Details
    content_body = Column(Text, nullable=False)
    content_excerpt = Column(Text)
    content_tags = Column(JSON)  # Content tags
    content_categories = Column(JSON)  # Content categories
    
    # Content Assets
    content_media = Column(JSON)  # Media files
    content_attachments = Column(JSON)  # Attachments
    content_links = Column(JSON)  # Related links
    
    # SEO Configuration
    seo_title = Column(String(255))
    seo_description = Column(Text)
    seo_keywords = Column(JSON)  # SEO keywords
    seo_meta_tags = Column(JSON)  # Meta tags
    
    # Content Distribution
    distribution_channels = Column(JSON)  # Distribution channels
    distribution_schedule = Column(JSON)  # Distribution schedule
    distribution_automation = Column(JSON)  # Distribution automation
    
    # Content Performance
    content_views = Column(Integer, default=0)
    content_shares = Column(Integer, default=0)
    content_likes = Column(Integer, default=0)
    content_comments = Column(Integer, default=0)
    content_downloads = Column(Integer, default=0)
    
    # Content Metrics
    engagement_rate = Column(Float, default=0.0)  # Engagement rate
    conversion_rate = Column(Float, default=0.0)  # Conversion rate
    lead_generation = Column(Integer, default=0)  # Leads generated
    
    # Content Status
    content_status = Column(String(50), default='draft')  # draft, published, archived
    content_author = Column(Integer, ForeignKey('users.id'))
    content_editor = Column(Integer, ForeignKey('users.id'))
    
    # Metadata
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    author = relationship("User", foreign_keys=[content_author])
    editor = relationship("User", foreign_keys=[content_editor])

# Event Marketing
class EventMarketing(Base):
    __tablename__ = 'event_marketing'
    
    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(255), nullable=False)
    event_description = Column(Text)
    event_type = Column(String(50), nullable=False)  # webinar, conference, workshop, seminar
    
    # Event Details
    event_start = Column(DateTime, nullable=False)
    event_end = Column(DateTime, nullable=False)
    event_timezone = Column(String(50))
    event_duration = Column(Integer)  # Minutes
    
    # Event Location
    event_location = Column(String(255))
    event_address = Column(Text)
    event_city = Column(String(100))
    event_country = Column(String(100))
    event_online = Column(Boolean, default=False)
    event_url = Column(String(500))
    
    # Event Configuration
    event_capacity = Column(Integer, default=0)
    event_registration_required = Column(Boolean, default=True)
    event_registration_fee = Column(Float, default=0.0)
    event_registration_deadline = Column(DateTime)
    
    # Event Content
    event_agenda = Column(JSON)  # Event agenda
    event_speakers = Column(JSON)  # Event speakers
    event_materials = Column(JSON)  # Event materials
    event_sponsors = Column(JSON)  # Event sponsors
    
    # Event Marketing
    event_promotion = Column(JSON)  # Promotion strategy
    event_channels = Column(JSON)  # Marketing channels
    event_budget = Column(Float, default=0.0)
    event_roi = Column(Float, default=0.0)
    
    # Event Performance
    event_registrations = Column(Integer, default=0)
    event_attendees = Column(Integer, default=0)
    event_no_shows = Column(Integer, default=0)
    event_satisfaction = Column(Float, default=0.0)  # Satisfaction rating
    
    # Event Follow-up
    follow_up_automation = Column(JSON)  # Follow-up automation
    follow_up_content = Column(JSON)  # Follow-up content
    follow_up_schedule = Column(JSON)  # Follow-up schedule
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Marketing Automation
class MarketingAutomation(Base):
    __tablename__ = 'marketing_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    automation_type = Column(String(50), nullable=False)  # lead_scoring, nurturing, segmentation
    
    # Automation Configuration
    automation_rules = Column(JSON, nullable=False)  # Automation rules
    automation_triggers = Column(JSON, nullable=False)  # Trigger conditions
    automation_actions = Column(JSON, nullable=False)  # Automation actions
    
    # Automation Schedule
    automation_start = Column(DateTime, nullable=False)
    automation_end = Column(DateTime)
    automation_frequency = Column(String(50))  # once, daily, weekly, monthly
    automation_timezone = Column(String(50))
    
    # Automation Performance
    automation_status = Column(String(50), default='active')  # active, paused, completed
    total_executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    automation_roi = Column(Float, default=0.0)
    
    # Automation Optimization
    optimization_rules = Column(JSON)  # Optimization rules
    performance_insights = Column(JSON)  # Performance insights
    improvement_suggestions = Column(JSON)  # Improvement suggestions
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Marketing Analytics
class MarketingAnalytics(Base):
    __tablename__ = 'marketing_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    analytics_name = Column(String(255), nullable=False)
    analytics_type = Column(String(50), nullable=False)  # campaign, lead, content, event
    analytics_period = Column(String(50), nullable=False)  # daily, weekly, monthly, quarterly
    
    # Analytics Data
    analytics_data = Column(JSON, nullable=False)  # Analytics data
    analytics_metrics = Column(JSON, nullable=False)  # Key metrics
    analytics_insights = Column(JSON)  # Analytics insights
    analytics_recommendations = Column(JSON)  # Recommendations
    
    # Performance Metrics
    total_reach = Column(Integer, default=0)
    total_engagement = Column(Integer, default=0)
    total_conversions = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Performance Rates
    engagement_rate = Column(Float, default=0.0)  # Engagement rate
    conversion_rate = Column(Float, default=0.0)  # Conversion rate
    roi = Column(Float, default=0.0)  # Return on investment
    cost_per_lead = Column(Float, default=0.0)  # Cost per lead
    cost_per_conversion = Column(Float, default=0.0)  # Cost per conversion
    
    # Analytics Trends
    trend_direction = Column(String(20))  # increasing, stable, decreasing
    trend_strength = Column(Float, default=0.0)  # Trend strength
    seasonal_adjustment = Column(Float, default=0.0)  # Seasonal adjustment
    
    # Metadata
    analytics_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    campaigns = relationship("MarketingCampaign")

# Marketing Attribution
class MarketingAttribution(Base):
    __tablename__ = 'marketing_attribution'
    
    id = Column(Integer, primary_key=True, index=True)
    attribution_model = Column(String(50), nullable=False)  # first_touch, last_touch, linear, time_decay
    attribution_period = Column(String(50), nullable=False)  # daily, weekly, monthly
    
    # Attribution Data
    attribution_data = Column(JSON, nullable=False)  # Attribution data
    touchpoint_analysis = Column(JSON)  # Touchpoint analysis
    conversion_paths = Column(JSON)  # Conversion paths
    attribution_weights = Column(JSON)  # Attribution weights
    
    # Channel Performance
    channel_performance = Column(JSON)  # Channel performance
    channel_attribution = Column(JSON)  # Channel attribution
    channel_roi = Column(JSON)  # Channel ROI
    channel_efficiency = Column(JSON)  # Channel efficiency
    
    # Attribution Insights
    attribution_insights = Column(JSON)  # Attribution insights
    optimization_opportunities = Column(JSON)  # Optimization opportunities
    budget_recommendations = Column(JSON)  # Budget recommendations
    
    # Metadata
    attribution_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
