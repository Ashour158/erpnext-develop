# Workflow Models - Complete Workflow Engine and Automation
# Advanced workflow models without Frappe dependencies

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

# Enums
class WorkflowStatus(enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ARCHIVED = "Archived"

class ExecutionStatus(enum.Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
    PAUSED = "Paused"

class StepType(enum.Enum):
    START = "Start"
    END = "End"
    TASK = "Task"
    DECISION = "Decision"
    APPROVAL = "Approval"
    NOTIFICATION = "Notification"
    ACTION = "Action"
    CONDITION = "Condition"

class TriggerType(enum.Enum):
    MANUAL = "Manual"
    SCHEDULED = "Scheduled"
    EVENT = "Event"
    CONDITION = "Condition"
    API = "API"

class ActionType(enum.Enum):
    EMAIL = "Email"
    SMS = "SMS"
    NOTIFICATION = "Notification"
    DATA_UPDATE = "Data Update"
    API_CALL = "API Call"
    APPROVAL = "Approval"
    ASSIGNMENT = "Assignment"

# Workflow Template Model
class WorkflowTemplate(BaseModel):
    """Workflow Template model"""
    __tablename__ = 'workflow_templates'
    
    template_name = db.Column(db.String(200), nullable=False)
    template_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Template Details
    category = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    complexity = db.Column(db.String(20), default='Medium')  # Low, Medium, High
    
    # Template Configuration
    template_config = db.Column(db.JSON)  # Template configuration
    is_public = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Usage Statistics
    usage_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    workflows = relationship("Workflow", back_populates="template")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'template_name': self.template_name,
            'template_code': self.template_code,
            'description': self.description,
            'category': self.category,
            'industry': self.industry,
            'complexity': self.complexity,
            'template_config': self.template_config,
            'is_public': self.is_public,
            'is_featured': self.is_featured,
            'usage_count': self.usage_count,
            'rating': self.rating,
            'company_id': self.company_id
        })
        return data

# Workflow Model
class Workflow(BaseModel):
    """Workflow model"""
    __tablename__ = 'workflows'
    
    workflow_name = db.Column(db.String(200), nullable=False)
    workflow_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Workflow Details
    workflow_type = db.Column(db.String(100))  # Approval, Process, Automation, etc.
    status = db.Column(db.Enum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    
    # Template
    template_id = db.Column(db.Integer, db.ForeignKey('workflow_templates.id'))
    template = relationship("WorkflowTemplate", back_populates="workflows")
    
    # Workflow Configuration
    workflow_config = db.Column(db.JSON)  # Workflow configuration
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=False)
    
    # Execution Settings
    max_execution_time = db.Column(db.Integer, default=3600)  # seconds
    retry_count = db.Column(db.Integer, default=3)
    timeout_action = db.Column(db.String(50), default='Cancel')
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    steps = relationship("WorkflowStep", back_populates="workflow")
    executions = relationship("WorkflowExecution", back_populates="workflow")
    triggers = relationship("WorkflowTrigger", back_populates="workflow")
    rules = relationship("WorkflowRule", back_populates="workflow")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'workflow_name': self.workflow_name,
            'workflow_code': self.workflow_code,
            'description': self.description,
            'workflow_type': self.workflow_type,
            'status': self.status.value if self.status else None,
            'template_id': self.template_id,
            'workflow_config': self.workflow_config,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'max_execution_time': self.max_execution_time,
            'retry_count': self.retry_count,
            'timeout_action': self.timeout_action,
            'company_id': self.company_id
        })
        return data

# Workflow Step Model
class WorkflowStep(BaseModel):
    """Workflow Step model"""
    __tablename__ = 'workflow_steps'
    
    # Workflow
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    workflow = relationship("Workflow", back_populates="steps")
    
    # Step Details
    step_name = db.Column(db.String(200), nullable=False)
    step_code = db.Column(db.String(50), nullable=False)
    step_type = db.Column(db.Enum(StepType), nullable=False)
    description = db.Column(db.Text)
    
    # Step Configuration
    step_config = db.Column(db.JSON)  # Step configuration
    step_order = db.Column(db.Integer, default=0)
    
    # Step Settings
    is_required = db.Column(db.Boolean, default=True)
    is_parallel = db.Column(db.Boolean, default=False)
    timeout_minutes = db.Column(db.Integer, default=0)
    
    # Assignment
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    assigned_to = relationship("Employee")
    assigned_role = db.Column(db.String(100))
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    actions = relationship("WorkflowAction", back_populates="step")
    conditions = relationship("WorkflowCondition", back_populates="step")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'workflow_id': self.workflow_id,
            'step_name': self.step_name,
            'step_code': self.step_code,
            'step_type': self.step_type.value if self.step_type else None,
            'description': self.description,
            'step_config': self.step_config,
            'step_order': self.step_order,
            'is_required': self.is_required,
            'is_parallel': self.is_parallel,
            'timeout_minutes': self.timeout_minutes,
            'assigned_to_id': self.assigned_to_id,
            'assigned_role': self.assigned_role,
            'company_id': self.company_id
        })
        return data

# Workflow Execution Model
class WorkflowExecution(BaseModel):
    """Workflow Execution model"""
    __tablename__ = 'workflow_executions'
    
    # Workflow
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    workflow = relationship("Workflow", back_populates="executions")
    
    # Execution Details
    execution_name = db.Column(db.String(200), nullable=False)
    execution_status = db.Column(db.Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    
    # Execution Data
    input_data = db.Column(db.JSON)  # Input data for execution
    output_data = db.Column(db.JSON)  # Output data from execution
    execution_log = db.Column(db.JSON)  # Execution log
    
    # Timing
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Float, default=0.0)
    
    # Trigger Information
    triggered_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    triggered_by = relationship("Employee")
    trigger_type = db.Column(db.Enum(TriggerType))
    trigger_data = db.Column(db.JSON)
    
    # Error Handling
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    max_retries = db.Column(db.Integer, default=3)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'workflow_id': self.workflow_id,
            'execution_name': self.execution_name,
            'execution_status': self.execution_status.value if self.execution_status else None,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'execution_log': self.execution_log,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'triggered_by_id': self.triggered_by_id,
            'trigger_type': self.trigger_type.value if self.trigger_type else None,
            'trigger_data': self.trigger_data,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'company_id': self.company_id
        })
        return data

# Workflow Rule Model
class WorkflowRule(BaseModel):
    """Workflow Rule model"""
    __tablename__ = 'workflow_rules'
    
    # Workflow
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    workflow = relationship("Workflow", back_populates="rules")
    
    # Rule Details
    rule_name = db.Column(db.String(200), nullable=False)
    rule_description = db.Column(db.Text)
    
    # Rule Configuration
    rule_conditions = db.Column(db.JSON)  # Rule conditions
    rule_actions = db.Column(db.JSON)  # Rule actions
    rule_priority = db.Column(db.Integer, default=0)
    
    # Rule Settings
    is_active = db.Column(db.Boolean, default=True)
    is_global = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'workflow_id': self.workflow_id,
            'rule_name': self.rule_name,
            'rule_description': self.rule_description,
            'rule_conditions': self.rule_conditions,
            'rule_actions': self.rule_actions,
            'rule_priority': self.rule_priority,
            'is_active': self.is_active,
            'is_global': self.is_global,
            'company_id': self.company_id
        })
        return data

# Workflow Trigger Model
class WorkflowTrigger(BaseModel):
    """Workflow Trigger model"""
    __tablename__ = 'workflow_triggers'
    
    # Workflow
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    workflow = relationship("Workflow", back_populates="triggers")
    
    # Trigger Details
    trigger_name = db.Column(db.String(200), nullable=False)
    trigger_type = db.Column(db.Enum(TriggerType), nullable=False)
    trigger_description = db.Column(db.Text)
    
    # Trigger Configuration
    trigger_config = db.Column(db.JSON)  # Trigger configuration
    trigger_conditions = db.Column(db.JSON)  # Trigger conditions
    
    # Trigger Settings
    is_active = db.Column(db.Boolean, default=True)
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(100))
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'workflow_id': self.workflow_id,
            'trigger_name': self.trigger_name,
            'trigger_type': self.trigger_type.value if self.trigger_type else None,
            'trigger_description': self.trigger_description,
            'trigger_config': self.trigger_config,
            'trigger_conditions': self.trigger_conditions,
            'is_active': self.is_active,
            'is_recurring': self.is_recurring,
            'recurrence_pattern': self.recurrence_pattern,
            'company_id': self.company_id
        })
        return data

# Workflow Action Model
class WorkflowAction(BaseModel):
    """Workflow Action model"""
    __tablename__ = 'workflow_actions'
    
    # Step
    step_id = db.Column(db.Integer, db.ForeignKey('workflow_steps.id'), nullable=False)
    step = relationship("WorkflowStep", back_populates="actions")
    
    # Action Details
    action_name = db.Column(db.String(200), nullable=False)
    action_type = db.Column(db.Enum(ActionType), nullable=False)
    action_description = db.Column(db.Text)
    
    # Action Configuration
    action_config = db.Column(db.JSON)  # Action configuration
    action_order = db.Column(db.Integer, default=0)
    
    # Action Settings
    is_required = db.Column(db.Boolean, default=True)
    is_conditional = db.Column(db.Boolean, default=False)
    condition_expression = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'step_id': self.step_id,
            'action_name': self.action_name,
            'action_type': self.action_type.value if self.action_type else None,
            'action_description': self.action_description,
            'action_config': self.action_config,
            'action_order': self.action_order,
            'is_required': self.is_required,
            'is_conditional': self.is_conditional,
            'condition_expression': self.condition_expression,
            'company_id': self.company_id
        })
        return data

# Workflow Condition Model
class WorkflowCondition(BaseModel):
    """Workflow Condition model"""
    __tablename__ = 'workflow_conditions'
    
    # Step
    step_id = db.Column(db.Integer, db.ForeignKey('workflow_steps.id'), nullable=False)
    step = relationship("WorkflowStep", back_populates="conditions")
    
    # Condition Details
    condition_name = db.Column(db.String(200), nullable=False)
    condition_expression = db.Column(db.Text, nullable=False)
    condition_description = db.Column(db.Text)
    
    # Condition Configuration
    condition_config = db.Column(db.JSON)  # Condition configuration
    condition_order = db.Column(db.Integer, default=0)
    
    # Condition Settings
    is_active = db.Column(db.Boolean, default=True)
    is_required = db.Column(db.Boolean, default=True)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'step_id': self.step_id,
            'condition_name': self.condition_name,
            'condition_expression': self.condition_expression,
            'condition_description': self.condition_description,
            'condition_config': self.condition_config,
            'condition_order': self.condition_order,
            'is_active': self.is_active,
            'is_required': self.is_required,
            'company_id': self.company_id
        })
        return data
