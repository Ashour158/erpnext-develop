# Workflow Automation Models
# Models for smart workflows and conditional logic for automated business processes

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime, time, date, timedelta
import enum

class WorkflowStatus(enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ARCHIVED = "Archived"

class WorkflowTrigger(enum.Enum):
    MANUAL = "Manual"
    SCHEDULED = "Scheduled"
    EVENT = "Event"
    CONDITION = "Condition"
    API = "API"
    WEBHOOK = "Webhook"

class WorkflowStepType(enum.Enum):
    ACTION = "Action"
    CONDITION = "Condition"
    DELAY = "Delay"
    NOTIFICATION = "Notification"
    APPROVAL = "Approval"
    INTEGRATION = "Integration"
    SCRIPT = "Script"

class WorkflowExecutionStatus(enum.Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
    PAUSED = "Paused"

class WorkflowTemplate(BaseModel):
    """Workflow template model"""
    __tablename__ = 'workflow_templates'
    
    # Template Information
    template_name = db.Column(db.String(200), nullable=False)
    template_description = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Template Configuration
    template_config = db.Column(db.JSON)  # Template configuration
    workflow_steps = db.Column(db.JSON)  # Workflow steps definition
    variables = db.Column(db.JSON)  # Template variables
    conditions = db.Column(db.JSON)  # Template conditions
    
    # Usage Information
    usage_count = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'template_name': self.template_name,
            'template_description': self.template_description,
            'category': self.category,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'template_config': self.template_config,
            'workflow_steps': self.workflow_steps,
            'variables': self.variables,
            'conditions': self.conditions,
            'usage_count': self.usage_count,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'company_id': self.company_id
        })
        return data

class Workflow(BaseModel):
    """Workflow model"""
    __tablename__ = 'workflows'
    
    # Workflow Information
    workflow_name = db.Column(db.String(200), nullable=False)
    workflow_description = db.Column(db.Text)
    status = db.Column(db.Enum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    
    # Workflow Configuration
    trigger_type = db.Column(db.Enum(WorkflowTrigger), nullable=False)
    trigger_config = db.Column(db.JSON)  # Trigger configuration
    workflow_steps = db.Column(db.JSON)  # Workflow steps
    variables = db.Column(db.JSON)  # Workflow variables
    conditions = db.Column(db.JSON)  # Workflow conditions
    
    # Execution Settings
    max_execution_time = db.Column(db.Integer, default=3600)  # seconds
    retry_count = db.Column(db.Integer, default=3)
    retry_delay = db.Column(db.Integer, default=300)  # seconds
    timeout_action = db.Column(db.String(50), default='Cancel')  # Cancel, Continue, Notify
    
    # Access Control
    allowed_users = db.Column(db.JSON)  # List of user IDs
    allowed_roles = db.Column(db.JSON)  # List of role IDs
    is_public = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'workflow_name': self.workflow_name,
            'workflow_description': self.workflow_description,
            'status': self.status.value if self.status else None,
            'trigger_type': self.trigger_type.value if self.trigger_type else None,
            'trigger_config': self.trigger_config,
            'workflow_steps': self.workflow_steps,
            'variables': self.variables,
            'conditions': self.conditions,
            'max_execution_time': self.max_execution_time,
            'retry_count': self.retry_count,
            'retry_delay': self.retry_delay,
            'timeout_action': self.timeout_action,
            'allowed_users': self.allowed_users,
            'allowed_roles': self.allowed_roles,
            'is_public': self.is_public,
            'company_id': self.company_id
        })
        return data

class WorkflowStep(BaseModel):
    """Workflow step model"""
    __tablename__ = 'workflow_steps'
    
    # Step Information
    step_name = db.Column(db.String(200), nullable=False)
    step_description = db.Column(db.Text)
    step_type = db.Column(db.Enum(WorkflowStepType), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)
    
    # Step Configuration
    step_config = db.Column(db.JSON)  # Step configuration
    conditions = db.Column(db.JSON)  # Step conditions
    actions = db.Column(db.JSON)  # Step actions
    parameters = db.Column(db.JSON)  # Step parameters
    
    # Workflow Association
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    workflow = relationship("Workflow")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'step_name': self.step_name,
            'step_description': self.step_description,
            'step_type': self.step_type.value if self.step_type else None,
            'step_order': self.step_order,
            'step_config': self.step_config,
            'conditions': self.conditions,
            'actions': self.actions,
            'parameters': self.parameters,
            'workflow_id': self.workflow_id,
            'company_id': self.company_id
        })
        return data

class WorkflowExecution(BaseModel):
    """Workflow execution model"""
    __tablename__ = 'workflow_executions'
    
    # Execution Information
    execution_name = db.Column(db.String(200), nullable=False)
    execution_status = db.Column(db.Enum(WorkflowExecutionStatus), default=WorkflowExecutionStatus.PENDING)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    execution_duration = db.Column(db.Float, default=0.0)  # seconds
    
    # Workflow Association
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    workflow = relationship("Workflow")
    
    # Execution Data
    input_data = db.Column(db.JSON)  # Input data
    output_data = db.Column(db.JSON)  # Output data
    execution_log = db.Column(db.JSON)  # Execution log
    error_message = db.Column(db.Text)
    
    # User Information
    triggered_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    triggerer = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'execution_name': self.execution_name,
            'execution_status': self.execution_status.value if self.execution_status else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'execution_duration': self.execution_duration,
            'workflow_id': self.workflow_id,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'execution_log': self.execution_log,
            'error_message': self.error_message,
            'triggered_by': self.triggered_by,
            'company_id': self.company_id
        })
        return data

class WorkflowStepExecution(BaseModel):
    """Workflow step execution model"""
    __tablename__ = 'workflow_step_executions'
    
    # Step Execution Information
    step_name = db.Column(db.String(200), nullable=False)
    step_type = db.Column(db.Enum(WorkflowStepType), nullable=False)
    execution_status = db.Column(db.Enum(WorkflowExecutionStatus), default=WorkflowExecutionStatus.PENDING)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    execution_duration = db.Column(db.Float, default=0.0)  # seconds
    
    # Workflow Execution Association
    workflow_execution_id = db.Column(db.Integer, db.ForeignKey('workflow_executions.id'), nullable=False)
    workflow_execution = relationship("WorkflowExecution")
    
    # Step Execution Data
    input_data = db.Column(db.JSON)  # Step input data
    output_data = db.Column(db.JSON)  # Step output data
    execution_log = db.Column(db.JSON)  # Step execution log
    error_message = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'step_name': self.step_name,
            'step_type': self.step_type.value if self.step_type else None,
            'execution_status': self.execution_status.value if self.execution_status else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'execution_duration': self.execution_duration,
            'workflow_execution_id': self.workflow_execution_id,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'execution_log': self.execution_log,
            'error_message': self.error_message,
            'company_id': self.company_id
        })
        return data

class WorkflowCondition(BaseModel):
    """Workflow condition model"""
    __tablename__ = 'workflow_conditions'
    
    # Condition Information
    condition_name = db.Column(db.String(200), nullable=False)
    condition_description = db.Column(db.Text)
    condition_type = db.Column(db.String(100), nullable=False)  # Field, Expression, Custom
    
    # Condition Configuration
    condition_config = db.Column(db.JSON)  # Condition configuration
    field_name = db.Column(db.String(100))
    operator = db.Column(db.String(50))  # equals, not_equals, greater_than, etc.
    expected_value = db.Column(db.Text)
    expression = db.Column(db.Text)  # Custom expression
    
    # Workflow Association
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    workflow = relationship("Workflow")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'condition_name': self.condition_name,
            'condition_description': self.condition_description,
            'condition_type': self.condition_type,
            'condition_config': self.condition_config,
            'field_name': self.field_name,
            'operator': self.operator,
            'expected_value': self.expected_value,
            'expression': self.expression,
            'workflow_id': self.workflow_id,
            'company_id': self.company_id
        })
        return data

class WorkflowAction(BaseModel):
    """Workflow action model"""
    __tablename__ = 'workflow_actions'
    
    # Action Information
    action_name = db.Column(db.String(200), nullable=False)
    action_description = db.Column(db.Text)
    action_type = db.Column(db.String(100), nullable=False)  # Email, SMS, API, Database, etc.
    
    # Action Configuration
    action_config = db.Column(db.JSON)  # Action configuration
    parameters = db.Column(db.JSON)  # Action parameters
    template = db.Column(db.Text)  # Action template
    
    # Workflow Association
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    workflow = relationship("Workflow")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'action_name': self.action_name,
            'action_description': self.action_description,
            'action_type': self.action_type,
            'action_config': self.action_config,
            'parameters': self.parameters,
            'template': self.template,
            'workflow_id': self.workflow_id,
            'company_id': self.company_id
        })
        return data

class WorkflowNotification(BaseModel):
    """Workflow notification model"""
    __tablename__ = 'workflow_notifications'
    
    # Notification Information
    notification_title = db.Column(db.String(200), nullable=False)
    notification_message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='Info')  # Info, Warning, Error, Success
    
    # Workflow Association
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    workflow = relationship("Workflow")
    workflow_execution_id = db.Column(db.Integer, db.ForeignKey('workflow_executions.id'))
    workflow_execution = relationship("WorkflowExecution")
    
    # Recipients
    recipient_users = db.Column(db.JSON)  # List of user IDs
    recipient_roles = db.Column(db.JSON)  # List of role IDs
    recipient_emails = db.Column(db.JSON)  # List of email addresses
    
    # Delivery Settings
    delivery_method = db.Column(db.String(50), default='Email')  # Email, SMS, Push, In-app
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'notification_title': self.notification_title,
            'notification_message': self.notification_message,
            'notification_type': self.notification_type,
            'workflow_id': self.workflow_id,
            'workflow_execution_id': self.workflow_execution_id,
            'recipient_users': self.recipient_users,
            'recipient_roles': self.recipient_roles,
            'recipient_emails': self.recipient_emails,
            'delivery_method': self.delivery_method,
            'is_sent': self.is_sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'company_id': self.company_id
        })
        return data

class WorkflowApproval(BaseModel):
    """Workflow approval model"""
    __tablename__ = 'workflow_approvals'
    
    # Approval Information
    approval_title = db.Column(db.String(200), nullable=False)
    approval_description = db.Column(db.Text)
    approval_type = db.Column(db.String(100), nullable=False)  # Single, Multiple, Sequential, Parallel
    
    # Workflow Association
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    workflow = relationship("Workflow")
    workflow_execution_id = db.Column(db.Integer, db.ForeignKey('workflow_executions.id'))
    workflow_execution = relationship("WorkflowExecution")
    
    # Approvers
    approver_users = db.Column(db.JSON)  # List of user IDs
    approver_roles = db.Column(db.JSON)  # List of role IDs
    required_approvals = db.Column(db.Integer, default=1)
    
    # Approval Status
    approval_status = db.Column(db.String(50), default='Pending')  # Pending, Approved, Rejected, Expired
    approved_by = db.Column(db.Integer, db.ForeignKey('employees.id'))
    approver = relationship("Employee")
    approved_at = db.Column(db.DateTime)
    approval_notes = db.Column(db.Text)
    
    # Expiration
    expires_at = db.Column(db.DateTime)
    is_expired = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'approval_title': self.approval_title,
            'approval_description': self.approval_description,
            'approval_type': self.approval_type,
            'workflow_id': self.workflow_id,
            'workflow_execution_id': self.workflow_execution_id,
            'approver_users': self.approver_users,
            'approver_roles': self.approver_roles,
            'required_approvals': self.required_approvals,
            'approval_status': self.approval_status,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approval_notes': self.approval_notes,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired,
            'company_id': self.company_id
        })
        return data
