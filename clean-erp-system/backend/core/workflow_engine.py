# Workflow Engine
# Backend core workflow system for all modules

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class WorkflowStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class WorkflowTrigger(enum.Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    CONDITIONAL = "conditional"

class StepType(enum.Enum):
    ACTION = "action"
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    CONDITION = "condition"
    DELAY = "delay"
    INTEGRATION = "integration"

class InstanceStatus(enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TaskStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"

# Workflow Definition
class Workflow(Base):
    __tablename__ = 'workflows'
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String(255), nullable=False)
    workflow_description = Column(Text)
    
    # Workflow Classification
    workflow_category = Column(String(100), nullable=False)  # CRM, Finance, HR, etc.
    workflow_type = Column(String(50), nullable=False)  # approval, notification, automation, etc.
    workflow_trigger = Column(Enum(WorkflowTrigger), default=WorkflowTrigger.MANUAL)
    
    # Workflow Configuration
    workflow_config = Column(JSON, nullable=False)  # Workflow configuration
    trigger_conditions = Column(JSON)  # Trigger conditions
    workflow_rules = Column(JSON)  # Workflow rules
    workflow_settings = Column(JSON)  # Workflow settings
    
    # Workflow Scope
    applicable_modules = Column(JSON, nullable=False)  # Modules where workflow can be used
    applicable_entities = Column(JSON)  # Specific entities (Customer, Invoice, etc.)
    applicable_conditions = Column(JSON)  # Conditions for workflow application
    
    # Workflow Status
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    is_system_workflow = Column(Boolean, default=False)  # System vs user-created
    is_template = Column(Boolean, default=False)  # Template for creating new workflows
    
    # Workflow Performance
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    average_execution_time = Column(Float, default=0.0)  # Seconds
    success_rate = Column(Float, default=0.0)  # Percentage
    
    # Workflow Versioning
    version = Column(Integer, default=1)
    parent_workflow_id = Column(Integer, ForeignKey('workflows.id'))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")
    parent_workflow = relationship("Workflow", remote_side=[id])
    steps = relationship("WorkflowStep", back_populates="workflow", cascade="all, delete-orphan")
    instances = relationship("WorkflowInstance", back_populates="workflow", cascade="all, delete-orphan")

# Workflow Steps
class WorkflowStep(Base):
    __tablename__ = 'workflow_steps'
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey('workflows.id'), nullable=False)
    step_name = Column(String(255), nullable=False)
    step_description = Column(Text)
    
    # Step Configuration
    step_type = Column(Enum(StepType), nullable=False)
    step_order = Column(Integer, nullable=False)  # Order in workflow
    step_config = Column(JSON, nullable=False)  # Step configuration
    step_conditions = Column(JSON)  # Step conditions
    step_actions = Column(JSON)  # Step actions
    
    # Step Assignment
    assigned_to_role = Column(String(100))  # Role-based assignment
    assigned_to_user = Column(Integer, ForeignKey('users.id'))  # User-based assignment
    assigned_to_department = Column(Integer, ForeignKey('departments.id'))  # Department-based assignment
    assigned_to_team = Column(Integer, ForeignKey('teams.id'))  # Team-based assignment
    
    # Step Timing
    estimated_duration = Column(Integer)  # Minutes
    deadline_hours = Column(Integer)  # Hours from workflow start
    is_parallel = Column(Boolean, default=False)  # Can run in parallel
    parallel_group = Column(String(50))  # Parallel execution group
    
    # Step Dependencies
    depends_on_steps = Column(JSON)  # Steps this step depends on
    blocks_steps = Column(JSON)  # Steps this step blocks
    
    # Step Status
    is_required = Column(Boolean, default=True)
    is_skippable = Column(Boolean, default=False)
    is_approval_step = Column(Boolean, default=False)
    
    # Step Integration
    integration_config = Column(JSON)  # Integration configuration
    notification_config = Column(JSON)  # Notification configuration
    approval_config = Column(JSON)  # Approval configuration
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="steps")
    assigned_user = relationship("User")
    assigned_department = relationship("Department")
    assigned_team = relationship("Team")
    tasks = relationship("WorkflowTask", back_populates="step", cascade="all, delete-orphan")

# Workflow Instances
class WorkflowInstance(Base):
    __tablename__ = 'workflow_instances'
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey('workflows.id'), nullable=False)
    instance_name = Column(String(255), nullable=False)
    
    # Instance Context
    context_module = Column(String(50), nullable=False)  # CRM, Finance, HR, etc.
    context_entity = Column(String(50), nullable=False)  # Customer, Invoice, Employee, etc.
    context_record_id = Column(Integer, nullable=False)  # ID of the record
    context_data = Column(JSON)  # Context data for the workflow
    
    # Instance Status
    status = Column(Enum(InstanceStatus), default=InstanceStatus.RUNNING)
    current_step_id = Column(Integer, ForeignKey('workflow_steps.id'))
    progress_percentage = Column(Float, default=0.0)  # 0-100
    
    # Instance Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    estimated_completion = Column(DateTime)
    actual_duration = Column(Integer)  # Minutes
    
    # Instance Results
    result_data = Column(JSON)  # Workflow result data
    error_message = Column(Text)  # Error message if failed
    completion_notes = Column(Text)  # Completion notes
    
    # Instance Assignment
    initiated_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    assigned_to = Column(Integer, ForeignKey('users.id'))
    assigned_team = Column(Integer, ForeignKey('teams.id'))
    assigned_department = Column(Integer, ForeignKey('departments.id'))
    
    # Instance Priority
    priority = Column(String(20), default='medium')  # low, medium, high, urgent
    due_date = Column(DateTime)
    
    # Instance Integration
    external_workflow_id = Column(String(100))  # External system workflow ID
    integration_data = Column(JSON)  # Integration data
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    workflow = relationship("Workflow", back_populates="instances")
    current_step = relationship("WorkflowStep")
    initiated_by_user = relationship("User", foreign_keys=[initiated_by])
    assigned_to_user = relationship("User", foreign_keys=[assigned_to])
    assigned_team_rel = relationship("Team")
    assigned_department_rel = relationship("Department")
    tasks = relationship("WorkflowTask", back_populates="instance", cascade="all, delete-orphan")

# Workflow Tasks
class WorkflowTask(Base):
    __tablename__ = 'workflow_tasks'
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_instance_id = Column(Integer, ForeignKey('workflow_instances.id'), nullable=False)
    workflow_step_id = Column(Integer, ForeignKey('workflow_steps.id'), nullable=False)
    task_name = Column(String(255), nullable=False)
    task_description = Column(Text)
    
    # Task Status
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    assigned_to = Column(Integer, ForeignKey('users.id'))
    assigned_team = Column(Integer, ForeignKey('teams.id'))
    assigned_department = Column(Integer, ForeignKey('departments.id'))
    
    # Task Timing
    due_date = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_duration = Column(Integer)  # Minutes
    actual_duration = Column(Integer)  # Minutes
    
    # Task Data
    task_data = Column(JSON)  # Task-specific data
    input_data = Column(JSON)  # Input data for the task
    output_data = Column(JSON)  # Output data from the task
    result_data = Column(JSON)  # Task result data
    
    # Task Actions
    actions_required = Column(JSON)  # Actions required for the task
    actions_completed = Column(JSON)  # Actions completed
    approval_required = Column(Boolean, default=False)
    approval_given = Column(Boolean, default=False)
    approval_notes = Column(Text)
    
    # Task Integration
    integration_required = Column(Boolean, default=False)
    integration_config = Column(JSON)  # Integration configuration
    integration_result = Column(JSON)  # Integration result
    
    # Task Notifications
    notification_sent = Column(Boolean, default=False)
    notification_config = Column(JSON)  # Notification configuration
    reminder_sent = Column(Boolean, default=False)
    reminder_count = Column(Integer, default=0)
    
    # Task Comments
    comments = Column(JSON)  # Task comments
    attachments = Column(JSON)  # Task attachments
    
    # Task Priority
    priority = Column(String(20), default='medium')  # low, medium, high, urgent
    is_urgent = Column(Boolean, default=False)
    
    # Task Dependencies
    depends_on_tasks = Column(JSON)  # Tasks this task depends on
    blocks_tasks = Column(JSON)  # Tasks this task blocks
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    instance = relationship("WorkflowInstance", back_populates="tasks")
    step = relationship("WorkflowStep", back_populates="tasks")
    assigned_user = relationship("User")
    assigned_team_rel = relationship("Team")
    assigned_department_rel = relationship("Department")

# Workflow Templates
class WorkflowTemplate(Base):
    __tablename__ = 'workflow_templates'
    
    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(255), nullable=False)
    template_description = Column(Text)
    
    # Template Classification
    template_category = Column(String(100), nullable=False)  # CRM, Finance, HR, etc.
    template_type = Column(String(50), nullable=False)  # approval, notification, automation, etc.
    template_tags = Column(JSON)  # Template tags
    
    # Template Configuration
    template_config = Column(JSON, nullable=False)  # Template configuration
    template_steps = Column(JSON, nullable=False)  # Template steps
    template_settings = Column(JSON)  # Template settings
    
    # Template Usage
    usage_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    is_system_template = Column(Boolean, default=False)
    
    # Template Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Template Metrics
    success_rate = Column(Float, default=0.0)  # Success rate percentage
    average_rating = Column(Float, default=0.0)  # User rating
    download_count = Column(Integer, default=0)
    
    # Template Versioning
    version = Column(Integer, default=1)
    parent_template_id = Column(Integer, ForeignKey('workflow_templates.id'))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")
    parent_template = relationship("WorkflowTemplate", remote_side=[id])

# Workflow Analytics
class WorkflowAnalytics(Base):
    __tablename__ = 'workflow_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    analytics_name = Column(String(255), nullable=False)
    analytics_type = Column(String(50), nullable=False)  # performance, usage, efficiency, etc.
    analytics_period = Column(String(50), nullable=False)  # daily, weekly, monthly, quarterly
    
    # Analytics Data
    analytics_data = Column(JSON, nullable=False)  # Analytics data
    analytics_metrics = Column(JSON, nullable=False)  # Key metrics
    analytics_insights = Column(JSON)  # Analytics insights
    analytics_recommendations = Column(JSON)  # Recommendations
    
    # Workflow Metrics
    total_workflows = Column(Integer, default=0)
    active_workflows = Column(Integer, default=0)
    completed_workflows = Column(Integer, default=0)
    failed_workflows = Column(Integer, default=0)
    
    # Performance Metrics
    average_execution_time = Column(Float, default=0.0)  # Minutes
    success_rate = Column(Float, default=0.0)  # Percentage
    failure_rate = Column(Float, default=0.0)  # Percentage
    average_steps_per_workflow = Column(Float, default=0.0)
    
    # Usage Metrics
    most_used_workflows = Column(JSON)  # Most used workflows
    most_used_steps = Column(JSON)  # Most used steps
    user_adoption_rate = Column(Float, default=0.0)  # User adoption percentage
    
    # Efficiency Metrics
    workflow_efficiency = Column(Float, default=0.0)  # Efficiency score
    bottleneck_steps = Column(JSON)  # Steps causing bottlenecks
    optimization_opportunities = Column(JSON)  # Optimization opportunities
    
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
    workflows = relationship("Workflow")
    instances = relationship("WorkflowInstance")
    tasks = relationship("WorkflowTask")
