# Advanced Sales Automation
# Comprehensive sales automation to surpass Zoho CRM and Salesforce

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class AutomationType(enum.Enum):
    LEAD_SCORING = "lead_scoring"
    LEAD_ASSIGNMENT = "lead_assignment"
    FOLLOW_UP = "follow_up"
    DEAL_STAGE = "deal_stage"
    TASK_CREATION = "task_creation"
    EMAIL_SEQUENCE = "email_sequence"
    CALL_SCHEDULING = "call_scheduling"
    MEETING_SCHEDULING = "meeting_scheduling"
    DEAL_CREATION = "deal_creation"
    QUOTE_GENERATION = "quote_generation"
    CONTRACT_GENERATION = "contract_generation"
    RENEWAL_REMINDER = "renewal_reminder"
    CHURN_PREVENTION = "churn_prevention"
    CROSS_SELL = "cross_sell"
    UPSELL = "upsell"

class TriggerType(enum.Enum):
    FIELD_CHANGE = "field_change"
    STATUS_CHANGE = "status_change"
    STAGE_CHANGE = "stage_change"
    TIME_BASED = "time_based"
    CONDITION_BASED = "condition_based"
    EVENT_BASED = "event_based"
    SCORE_BASED = "score_based"
    BEHAVIOR_BASED = "behavior_based"

class ActionType(enum.Enum):
    SEND_EMAIL = "send_email"
    CREATE_TASK = "create_task"
    SCHEDULE_CALL = "schedule_call"
    SCHEDULE_MEETING = "schedule_meeting"
    UPDATE_FIELD = "update_field"
    ASSIGN_USER = "assign_user"
    CREATE_DEAL = "create_deal"
    GENERATE_QUOTE = "generate_quote"
    SEND_NOTIFICATION = "send_notification"
    CREATE_REMINDER = "create_reminder"
    UPDATE_SCORE = "update_score"
    TRIGGER_WORKFLOW = "trigger_workflow"

class SequenceStatus(enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

# Lead Scoring Automation
class LeadScoringAutomation(Base):
    __tablename__ = 'lead_scoring_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    
    # Scoring Rules
    scoring_rules = Column(JSON, nullable=False)  # Scoring criteria and weights
    score_thresholds = Column(JSON, nullable=False)  # Score thresholds for actions
    auto_assign_threshold = Column(Float, default=70.0)  # Auto-assign threshold
    
    # Behavioral Scoring
    behavioral_factors = Column(JSON)  # Behavioral scoring factors
    demographic_factors = Column(JSON)  # Demographic scoring factors
    engagement_factors = Column(JSON)  # Engagement scoring factors
    intent_factors = Column(JSON)  # Intent scoring factors
    
    # Automation Settings
    is_active = Column(Boolean, default=True)
    auto_assign = Column(Boolean, default=True)
    auto_qualify = Column(Boolean, default=True)
    auto_nurture = Column(Boolean, default=True)
    
    # Performance Metrics
    total_leads_scored = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    accuracy_rate = Column(Float, default=0.0)
    last_updated = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Lead Assignment Automation
class LeadAssignmentAutomation(Base):
    __tablename__ = 'lead_assignment_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    
    # Assignment Rules
    assignment_rules = Column(JSON, nullable=False)  # Assignment criteria
    assignment_method = Column(String(50), nullable=False)  # round_robin, load_balanced, skill_based, territory_based
    fallback_assignment = Column(String(50))  # Fallback assignment method
    
    # Territory Management
    territory_rules = Column(JSON)  # Territory-based assignment rules
    geographic_rules = Column(JSON)  # Geographic assignment rules
    industry_rules = Column(JSON)  # Industry-based assignment rules
    
    # Load Balancing
    max_leads_per_user = Column(Integer, default=50)
    workload_threshold = Column(Float, default=80.0)  # Percentage
    skill_requirements = Column(JSON)  # Required skills for assignment
    
    # Assignment Logic
    priority_rules = Column(JSON)  # Priority-based assignment
    time_based_rules = Column(JSON)  # Time-based assignment
    availability_rules = Column(JSON)  # Availability-based assignment
    
    # Performance Metrics
    total_assignments = Column(Integer, default=0)
    successful_assignments = Column(Integer, default=0)
    assignment_accuracy = Column(Float, default=0.0)
    average_response_time = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Follow-up Automation
class FollowUpAutomation(Base):
    __tablename__ = 'follow_up_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    
    # Follow-up Rules
    follow_up_rules = Column(JSON, nullable=False)  # Follow-up criteria
    follow_up_sequence = Column(JSON, nullable=False)  # Follow-up sequence
    follow_up_timing = Column(JSON, nullable=False)  # Timing rules
    
    # Communication Channels
    email_templates = Column(JSON)  # Email templates
    sms_templates = Column(JSON)  # SMS templates
    call_scripts = Column(JSON)  # Call scripts
    meeting_templates = Column(JSON)  # Meeting templates
    
    # Personalization
    personalization_rules = Column(JSON)  # Personalization rules
    dynamic_content = Column(JSON)  # Dynamic content rules
    a_b_testing = Column(JSON)  # A/B testing configuration
    
    # Performance Metrics
    total_follow_ups = Column(Integer, default=0)
    successful_follow_ups = Column(Integer, default=0)
    response_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Deal Stage Automation
class DealStageAutomation(Base):
    __tablename__ = 'deal_stage_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    
    # Stage Rules
    stage_rules = Column(JSON, nullable=False)  # Stage progression rules
    stage_triggers = Column(JSON, nullable=False)  # Stage trigger conditions
    stage_actions = Column(JSON, nullable=False)  # Actions for each stage
    
    # Stage Management
    auto_progression = Column(Boolean, default=True)
    stage_timeouts = Column(JSON)  # Stage timeout rules
    stage_escalation = Column(JSON)  # Escalation rules
    
    # Stage Analytics
    stage_analytics = Column(JSON)  # Stage performance analytics
    stage_optimization = Column(JSON)  # Stage optimization rules
    stage_predictions = Column(JSON)  # Stage prediction rules
    
    # Performance Metrics
    total_deals = Column(Integer, default=0)
    successful_progressions = Column(Integer, default=0)
    stage_conversion_rate = Column(Float, default=0.0)
    average_stage_duration = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Task Creation Automation
class TaskCreationAutomation(Base):
    __tablename__ = 'task_creation_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    
    # Task Rules
    task_rules = Column(JSON, nullable=False)  # Task creation rules
    task_templates = Column(JSON, nullable=False)  # Task templates
    task_priorities = Column(JSON, nullable=False)  # Task priority rules
    
    # Task Management
    auto_assign_tasks = Column(Boolean, default=True)
    task_dependencies = Column(JSON)  # Task dependency rules
    task_scheduling = Column(JSON)  # Task scheduling rules
    
    # Task Types
    follow_up_tasks = Column(JSON)  # Follow-up task rules
    research_tasks = Column(JSON)  # Research task rules
    preparation_tasks = Column(JSON)  # Preparation task rules
    follow_through_tasks = Column(JSON)  # Follow-through task rules
    
    # Performance Metrics
    total_tasks_created = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    task_completion_rate = Column(Float, default=0.0)
    average_task_duration = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Email Sequence Automation
class EmailSequenceAutomation(Base):
    __tablename__ = 'email_sequence_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    sequence_name = Column(String(255), nullable=False)
    sequence_description = Column(Text)
    
    # Sequence Configuration
    sequence_steps = Column(JSON, nullable=False)  # Email sequence steps
    sequence_timing = Column(JSON, nullable=False)  # Timing between emails
    sequence_conditions = Column(JSON, nullable=False)  # Sequence conditions
    
    # Email Templates
    email_templates = Column(JSON, nullable=False)  # Email templates
    personalization_rules = Column(JSON)  # Personalization rules
    dynamic_content = Column(JSON)  # Dynamic content rules
    
    # Sequence Management
    auto_start = Column(Boolean, default=True)
    auto_pause = Column(Boolean, default=True)
    auto_stop = Column(Boolean, default=True)
    sequence_triggers = Column(JSON)  # Sequence trigger conditions
    
    # A/B Testing
    ab_testing = Column(JSON)  # A/B testing configuration
    test_variants = Column(JSON)  # Test variants
    test_metrics = Column(JSON)  # Test success metrics
    
    # Performance Metrics
    total_sequences = Column(Integer, default=0)
    completed_sequences = Column(Integer, default=0)
    sequence_completion_rate = Column(Float, default=0.0)
    average_sequence_duration = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Call Scheduling Automation
class CallSchedulingAutomation(Base):
    __tablename__ = 'call_scheduling_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    
    # Call Rules
    call_rules = Column(JSON, nullable=False)  # Call scheduling rules
    call_priorities = Column(JSON, nullable=False)  # Call priority rules
    call_timing = Column(JSON, nullable=False)  # Call timing rules
    
    # Call Management
    auto_schedule = Column(Boolean, default=True)
    auto_remind = Column(Boolean, default=True)
    auto_reschedule = Column(Boolean, default=True)
    call_scripts = Column(JSON)  # Call scripts
    
    # Call Analytics
    call_analytics = Column(JSON)  # Call performance analytics
    call_optimization = Column(JSON)  # Call optimization rules
    call_predictions = Column(JSON)  # Call outcome predictions
    
    # Performance Metrics
    total_calls_scheduled = Column(Integer, default=0)
    successful_calls = Column(Integer, default=0)
    call_success_rate = Column(Float, default=0.0)
    average_call_duration = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Meeting Scheduling Automation
class MeetingSchedulingAutomation(Base):
    __tablename__ = 'meeting_scheduling_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    
    # Meeting Rules
    meeting_rules = Column(JSON, nullable=False)  # Meeting scheduling rules
    meeting_templates = Column(JSON, nullable=False)  # Meeting templates
    meeting_priorities = Column(JSON, nullable=False)  # Meeting priority rules
    
    # Meeting Management
    auto_schedule = Column(Boolean, default=True)
    auto_remind = Column(Boolean, default=True)
    auto_follow_up = Column(Boolean, default=True)
    meeting_preparation = Column(JSON)  # Meeting preparation rules
    
    # Meeting Analytics
    meeting_analytics = Column(JSON)  # Meeting performance analytics
    meeting_optimization = Column(JSON)  # Meeting optimization rules
    meeting_predictions = Column(JSON)  # Meeting outcome predictions
    
    # Performance Metrics
    total_meetings_scheduled = Column(Integer, default=0)
    successful_meetings = Column(Integer, default=0)
    meeting_success_rate = Column(Float, default=0.0)
    average_meeting_duration = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Deal Creation Automation
class DealCreationAutomation(Base):
    __tablename__ = 'deal_creation_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    
    # Deal Rules
    deal_rules = Column(JSON, nullable=False)  # Deal creation rules
    deal_templates = Column(JSON, nullable=False)  # Deal templates
    deal_priorities = Column(JSON, nullable=False)  # Deal priority rules
    
    # Deal Management
    auto_create = Column(Boolean, default=True)
    auto_assign = Column(Boolean, default=True)
    auto_qualify = Column(Boolean, default=True)
    deal_validation = Column(JSON)  # Deal validation rules
    
    # Deal Analytics
    deal_analytics = Column(JSON)  # Deal performance analytics
    deal_optimization = Column(JSON)  # Deal optimization rules
    deal_predictions = Column(JSON)  # Deal outcome predictions
    
    # Performance Metrics
    total_deals_created = Column(Integer, default=0)
    successful_deals = Column(Integer, default=0)
    deal_success_rate = Column(Float, default=0.0)
    average_deal_value = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Quote Generation Automation
class QuoteGenerationAutomation(Base):
    __tablename__ = 'quote_generation_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    
    # Quote Rules
    quote_rules = Column(JSON, nullable=False)  # Quote generation rules
    quote_templates = Column(JSON, nullable=False)  # Quote templates
    pricing_rules = Column(JSON, nullable=False)  # Pricing rules
    
    # Quote Management
    auto_generate = Column(Boolean, default=True)
    auto_send = Column(Boolean, default=True)
    auto_follow_up = Column(Boolean, default=True)
    quote_validation = Column(JSON)  # Quote validation rules
    
    # Quote Analytics
    quote_analytics = Column(JSON)  # Quote performance analytics
    quote_optimization = Column(JSON)  # Quote optimization rules
    quote_predictions = Column(JSON)  # Quote outcome predictions
    
    # Performance Metrics
    total_quotes_generated = Column(Integer, default=0)
    successful_quotes = Column(Integer, default=0)
    quote_success_rate = Column(Float, default=0.0)
    average_quote_value = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Contract Generation Automation
class ContractGenerationAutomation(Base):
    __tablename__ = 'contract_generation_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    
    # Contract Rules
    contract_rules = Column(JSON, nullable=False)  # Contract generation rules
    contract_templates = Column(JSON, nullable=False)  # Contract templates
    contract_clauses = Column(JSON, nullable=False)  # Contract clauses
    
    # Contract Management
    auto_generate = Column(Boolean, default=True)
    auto_send = Column(Boolean, default=True)
    auto_escalate = Column(Boolean, default=True)
    contract_validation = Column(JSON)  # Contract validation rules
    
    # Contract Analytics
    contract_analytics = Column(JSON)  # Contract performance analytics
    contract_optimization = Column(JSON)  # Contract optimization rules
    contract_predictions = Column(JSON)  # Contract outcome predictions
    
    # Performance Metrics
    total_contracts_generated = Column(Integer, default=0)
    successful_contracts = Column(Integer, default=0)
    contract_success_rate = Column(Float, default=0.0)
    average_contract_value = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Renewal Reminder Automation
class RenewalReminderAutomation(Base):
    __tablename__ = 'renewal_reminder_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    
    # Renewal Rules
    renewal_rules = Column(JSON, nullable=False)  # Renewal reminder rules
    reminder_templates = Column(JSON, nullable=False)  # Reminder templates
    reminder_timing = Column(JSON, nullable=False)  # Reminder timing rules
    
    # Renewal Management
    auto_remind = Column(Boolean, default=True)
    auto_escalate = Column(Boolean, default=True)
    auto_follow_up = Column(Boolean, default=True)
    renewal_validation = Column(JSON)  # Renewal validation rules
    
    # Renewal Analytics
    renewal_analytics = Column(JSON)  # Renewal performance analytics
    renewal_optimization = Column(JSON)  # Renewal optimization rules
    renewal_predictions = Column(JSON)  # Renewal outcome predictions
    
    # Performance Metrics
    total_reminders_sent = Column(Integer, default=0)
    successful_renewals = Column(Integer, default=0)
    renewal_success_rate = Column(Float, default=0.0)
    average_renewal_value = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Churn Prevention Automation
class ChurnPreventionAutomation(Base):
    __tablename__ = 'churn_prevention_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    
    # Churn Rules
    churn_rules = Column(JSON, nullable=False)  # Churn detection rules
    prevention_actions = Column(JSON, nullable=False)  # Prevention actions
    intervention_timing = Column(JSON, nullable=False)  # Intervention timing
    
    # Churn Management
    auto_detect = Column(Boolean, default=True)
    auto_intervene = Column(Boolean, default=True)
    auto_escalate = Column(Boolean, default=True)
    churn_validation = Column(JSON)  # Churn validation rules
    
    # Churn Analytics
    churn_analytics = Column(JSON)  # Churn performance analytics
    churn_optimization = Column(JSON)  # Churn optimization rules
    churn_predictions = Column(JSON)  # Churn outcome predictions
    
    # Performance Metrics
    total_churn_detected = Column(Integer, default=0)
    successful_preventions = Column(Integer, default=0)
    churn_prevention_rate = Column(Float, default=0.0)
    average_customer_value = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Cross-sell Automation
class CrossSellAutomation(Base):
    __tablename__ = 'cross_sell_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    
    # Cross-sell Rules
    cross_sell_rules = Column(JSON, nullable=False)  # Cross-sell detection rules
    product_recommendations = Column(JSON, nullable=False)  # Product recommendations
    offer_templates = Column(JSON, nullable=False)  # Offer templates
    
    # Cross-sell Management
    auto_recommend = Column(Boolean, default=True)
    auto_offer = Column(Boolean, default=True)
    auto_follow_up = Column(Boolean, default=True)
    cross_sell_validation = Column(JSON)  # Cross-sell validation rules
    
    # Cross-sell Analytics
    cross_sell_analytics = Column(JSON)  # Cross-sell performance analytics
    cross_sell_optimization = Column(JSON)  # Cross-sell optimization rules
    cross_sell_predictions = Column(JSON)  # Cross-sell outcome predictions
    
    # Performance Metrics
    total_recommendations = Column(Integer, default=0)
    successful_cross_sells = Column(Integer, default=0)
    cross_sell_success_rate = Column(Float, default=0.0)
    average_cross_sell_value = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Upsell Automation
class UpsellAutomation(Base):
    __tablename__ = 'upsell_automation'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_name = Column(String(255), nullable=False)
    automation_description = Column(Text)
    
    # Upsell Rules
    upsell_rules = Column(JSON, nullable=False)  # Upsell detection rules
    upgrade_recommendations = Column(JSON, nullable=False)  # Upgrade recommendations
    offer_templates = Column(JSON, nullable=False)  # Offer templates
    
    # Upsell Management
    auto_recommend = Column(Boolean, default=True)
    auto_offer = Column(Boolean, default=True)
    auto_follow_up = Column(Boolean, default=True)
    upsell_validation = Column(JSON)  # Upsell validation rules
    
    # Upsell Analytics
    upsell_analytics = Column(JSON)  # Upsell performance analytics
    upsell_optimization = Column(JSON)  # Upsell optimization rules
    upsell_predictions = Column(JSON)  # Upsell outcome predictions
    
    # Performance Metrics
    total_recommendations = Column(Integer, default=0)
    successful_upsells = Column(Integer, default=0)
    upsell_success_rate = Column(Float, default=0.0)
    average_upsell_value = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Automation Execution Log
class AutomationExecutionLog(Base):
    __tablename__ = 'automation_execution_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    automation_id = Column(Integer, nullable=False)
    automation_type = Column(Enum(AutomationType), nullable=False)
    
    # Execution Details
    execution_status = Column(String(20), nullable=False)  # success, failed, partial
    execution_start = Column(DateTime, nullable=False)
    execution_end = Column(DateTime)
    execution_duration = Column(Integer)  # Seconds
    
    # Execution Results
    total_processed = Column(Integer, default=0)
    successful_processed = Column(Integer, default=0)
    failed_processed = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Execution Context
    execution_context = Column(JSON)  # Execution context
    execution_parameters = Column(JSON)  # Execution parameters
    execution_results = Column(JSON)  # Execution results
    
    # Performance Metrics
    execution_time = Column(Float)  # Execution time in seconds
    memory_usage = Column(Float)  # Memory usage in MB
    cpu_usage = Column(Float)  # CPU usage percentage
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
