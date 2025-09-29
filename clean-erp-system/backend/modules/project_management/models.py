# Project Management Models
# Complete project management with Gantt charts, resource allocation, and project analytics

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

class ProjectStatus(enum.Enum):
    PLANNING = "Planning"
    ACTIVE = "Active"
    ON_HOLD = "On Hold"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class TaskStatus(enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"
    CANCELLED = "Cancelled"

class TaskPriority(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class ResourceType(enum.Enum):
    HUMAN = "Human"
    EQUIPMENT = "Equipment"
    MATERIAL = "Material"
    FACILITY = "Facility"

class RiskLevel(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

# Project Management Models
class Project(BaseModel):
    """Project model"""
    __tablename__ = 'projects'
    
    # Project Information
    project_name = db.Column(db.String(200), nullable=False)
    project_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Project Details
    project_type = db.Column(db.String(100), default='Internal')  # Internal, Client, R&D, etc.
    project_category = db.Column(db.String(100))
    project_manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    project_manager = relationship("Employee")
    
    # Project Timeline
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    actual_start_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    planned_duration_days = db.Column(db.Integer, default=0)
    actual_duration_days = db.Column(db.Integer, default=0)
    
    # Project Status
    status = db.Column(db.Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    progress_percentage = db.Column(db.Float, default=0.0)
    
    # Project Budget
    budget_allocated = db.Column(db.Float, default=0.0)
    budget_spent = db.Column(db.Float, default=0.0)
    budget_remaining = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Project Settings
    is_billable = db.Column(db.Boolean, default=False)
    is_confidential = db.Column(db.Boolean, default=False)
    requires_approval = db.Column(db.Boolean, default=False)
    
    # Client Information (if applicable)
    client_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    client = relationship("Customer")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    project_tasks = relationship("ProjectTask", back_populates="project")
    project_resources = relationship("ProjectResource", back_populates="project")
    project_risks = relationship("ProjectRisk", back_populates="project")
    project_milestones = relationship("ProjectMilestone", back_populates="project")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'project_name': self.project_name,
            'project_code': self.project_code,
            'description': self.description,
            'project_type': self.project_type,
            'project_category': self.project_category,
            'project_manager_id': self.project_manager_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'actual_start_date': self.actual_start_date.isoformat() if self.actual_start_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'planned_duration_days': self.planned_duration_days,
            'actual_duration_days': self.actual_duration_days,
            'status': self.status.value if self.status else None,
            'progress_percentage': self.progress_percentage,
            'budget_allocated': self.budget_allocated,
            'budget_spent': self.budget_spent,
            'budget_remaining': self.budget_remaining,
            'currency': self.currency,
            'is_billable': self.is_billable,
            'is_confidential': self.is_confidential,
            'requires_approval': self.requires_approval,
            'client_id': self.client_id,
            'company_id': self.company_id
        })
        return data

class ProjectTask(BaseModel):
    """Project task model"""
    __tablename__ = 'project_tasks'
    
    # Task Information
    task_name = db.Column(db.String(200), nullable=False)
    task_description = db.Column(db.Text)
    task_code = db.Column(db.String(50))
    
    # Project Association
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    project = relationship("Project", back_populates="project_tasks")
    
    # Task Hierarchy
    parent_task_id = db.Column(db.Integer, db.ForeignKey('project_tasks.id'))
    parent_task = relationship("ProjectTask", remote_side=[id])
    child_tasks = relationship("ProjectTask", back_populates="parent_task")
    
    # Task Assignment
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    assigned_to = relationship("Employee")
    
    # Task Timeline
    planned_start_date = db.Column(db.Date)
    planned_end_date = db.Column(db.Date)
    actual_start_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    planned_duration_hours = db.Column(db.Float, default=0.0)
    actual_duration_hours = db.Column(db.Float, default=0.0)
    
    # Task Status
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.NOT_STARTED)
    priority = db.Column(db.Enum(TaskPriority), default=TaskPriority.MEDIUM)
    progress_percentage = db.Column(db.Float, default=0.0)
    
    # Task Dependencies
    dependencies = db.Column(db.JSON)  # List of task IDs this task depends on
    
    # Task Budget
    estimated_cost = db.Column(db.Float, default=0.0)
    actual_cost = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    task_resources = relationship("TaskResource", back_populates="task")
    task_comments = relationship("TaskComment", back_populates="task")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'task_name': self.task_name,
            'task_description': self.task_description,
            'task_code': self.task_code,
            'project_id': self.project_id,
            'parent_task_id': self.parent_task_id,
            'assigned_to_id': self.assigned_to_id,
            'planned_start_date': self.planned_start_date.isoformat() if self.planned_start_date else None,
            'planned_end_date': self.planned_end_date.isoformat() if self.planned_end_date else None,
            'actual_start_date': self.actual_start_date.isoformat() if self.actual_start_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'planned_duration_hours': self.planned_duration_hours,
            'actual_duration_hours': self.actual_duration_hours,
            'status': self.status.value if self.status else None,
            'priority': self.priority.value if self.priority else None,
            'progress_percentage': self.progress_percentage,
            'dependencies': self.dependencies,
            'estimated_cost': self.estimated_cost,
            'actual_cost': self.actual_cost,
            'company_id': self.company_id
        })
        return data

class ProjectResource(BaseModel):
    """Project resource model"""
    __tablename__ = 'project_resources'
    
    # Resource Information
    resource_name = db.Column(db.String(200), nullable=False)
    resource_type = db.Column(db.Enum(ResourceType), nullable=False)
    resource_description = db.Column(db.Text)
    
    # Project Association
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    project = relationship("Project", back_populates="project_resources")
    
    # Resource Assignment
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    assigned_to = relationship("Employee")
    
    # Resource Allocation
    allocation_percentage = db.Column(db.Float, default=100.0)  # Percentage of time allocated
    allocation_start_date = db.Column(db.Date)
    allocation_end_date = db.Column(db.Date)
    
    # Resource Cost
    hourly_rate = db.Column(db.Float, default=0.0)
    total_cost = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Resource Status
    is_active = db.Column(db.Boolean, default=True)
    is_available = db.Column(db.Boolean, default=True)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'resource_name': self.resource_name,
            'resource_type': self.resource_type.value if self.resource_type else None,
            'resource_description': self.resource_description,
            'project_id': self.project_id,
            'assigned_to_id': self.assigned_to_id,
            'allocation_percentage': self.allocation_percentage,
            'allocation_start_date': self.allocation_start_date.isoformat() if self.allocation_start_date else None,
            'allocation_end_date': self.allocation_end_date.isoformat() if self.allocation_end_date else None,
            'hourly_rate': self.hourly_rate,
            'total_cost': self.total_cost,
            'currency': self.currency,
            'is_active': self.is_active,
            'is_available': self.is_available,
            'company_id': self.company_id
        })
        return data

class TaskResource(BaseModel):
    """Task resource assignment model"""
    __tablename__ = 'task_resources'
    
    # Task Association
    task_id = db.Column(db.Integer, db.ForeignKey('project_tasks.id'), nullable=False)
    task = relationship("ProjectTask", back_populates="task_resources")
    
    # Resource Association
    resource_id = db.Column(db.Integer, db.ForeignKey('project_resources.id'), nullable=False)
    resource = relationship("ProjectResource")
    
    # Assignment Details
    allocation_percentage = db.Column(db.Float, default=100.0)
    hours_allocated = db.Column(db.Float, default=0.0)
    hours_worked = db.Column(db.Float, default=0.0)
    
    # Assignment Dates
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'task_id': self.task_id,
            'resource_id': self.resource_id,
            'allocation_percentage': self.allocation_percentage,
            'hours_allocated': self.hours_allocated,
            'hours_worked': self.hours_worked,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'company_id': self.company_id
        })
        return data

class ProjectRisk(BaseModel):
    """Project risk model"""
    __tablename__ = 'project_risks'
    
    # Risk Information
    risk_name = db.Column(db.String(200), nullable=False)
    risk_description = db.Column(db.Text, nullable=False)
    risk_category = db.Column(db.String(100))  # Technical, Financial, Schedule, etc.
    
    # Project Association
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    project = relationship("Project", back_populates="project_risks")
    
    # Risk Assessment
    probability = db.Column(db.Float, default=0.0)  # 0-100%
    impact = db.Column(db.Float, default=0.0)  # 0-100%
    risk_level = db.Column(db.Enum(RiskLevel), default=RiskLevel.MEDIUM)
    risk_score = db.Column(db.Float, default=0.0)  # Probability * Impact
    
    # Risk Management
    mitigation_strategy = db.Column(db.Text)
    contingency_plan = db.Column(db.Text)
    risk_owner_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    risk_owner = relationship("Employee")
    
    # Risk Status
    status = db.Column(db.String(50), default='Open')  # Open, Mitigated, Accepted, Transferred
    mitigation_date = db.Column(db.Date)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'risk_name': self.risk_name,
            'risk_description': self.risk_description,
            'risk_category': self.risk_category,
            'project_id': self.project_id,
            'probability': self.probability,
            'impact': self.impact,
            'risk_level': self.risk_level.value if self.risk_level else None,
            'risk_score': self.risk_score,
            'mitigation_strategy': self.mitigation_strategy,
            'contingency_plan': self.contingency_plan,
            'risk_owner_id': self.risk_owner_id,
            'status': self.status,
            'mitigation_date': self.mitigation_date.isoformat() if self.mitigation_date else None,
            'company_id': self.company_id
        })
        return data

class ProjectMilestone(BaseModel):
    """Project milestone model"""
    __tablename__ = 'project_milestones'
    
    # Milestone Information
    milestone_name = db.Column(db.String(200), nullable=False)
    milestone_description = db.Column(db.Text)
    
    # Project Association
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    project = relationship("Project", back_populates="project_milestones")
    
    # Milestone Timeline
    planned_date = db.Column(db.Date, nullable=False)
    actual_date = db.Column(db.Date)
    
    # Milestone Status
    is_completed = db.Column(db.Boolean, default=False)
    completion_percentage = db.Column(db.Float, default=0.0)
    
    # Milestone Deliverables
    deliverables = db.Column(db.JSON)  # List of deliverables for this milestone
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'milestone_name': self.milestone_name,
            'milestone_description': self.milestone_description,
            'project_id': self.project_id,
            'planned_date': self.planned_date.isoformat() if self.planned_date else None,
            'actual_date': self.actual_date.isoformat() if self.actual_date else None,
            'is_completed': self.is_completed,
            'completion_percentage': self.completion_percentage,
            'deliverables': self.deliverables,
            'company_id': self.company_id
        })
        return data

class TaskComment(BaseModel):
    """Task comment model"""
    __tablename__ = 'task_comments'
    
    # Comment Information
    comment_text = db.Column(db.Text, nullable=False)
    comment_type = db.Column(db.String(50), default='General')  # General, Update, Issue, Resolution
    
    # Task Association
    task_id = db.Column(db.Integer, db.ForeignKey('project_tasks.id'), nullable=False)
    task = relationship("ProjectTask", back_populates="task_comments")
    
    # Comment Author
    author_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    author = relationship("Employee")
    
    # Comment Settings
    is_internal = db.Column(db.Boolean, default=False)
    is_urgent = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'comment_text': self.comment_text,
            'comment_type': self.comment_type,
            'task_id': self.task_id,
            'author_id': self.author_id,
            'is_internal': self.is_internal,
            'is_urgent': self.is_urgent,
            'company_id': self.company_id
        })
        return data

class ProjectTemplate(BaseModel):
    """Project template model"""
    __tablename__ = 'project_templates'
    
    # Template Information
    template_name = db.Column(db.String(200), nullable=False)
    template_description = db.Column(db.Text)
    template_category = db.Column(db.String(100))
    
    # Template Configuration
    template_config = db.Column(db.JSON)  # Template configuration
    default_tasks = db.Column(db.JSON)  # Default tasks for this template
    default_resources = db.Column(db.JSON)  # Default resources for this template
    default_milestones = db.Column(db.JSON)  # Default milestones for this template
    
    # Template Settings
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=False)
    usage_count = db.Column(db.Integer, default=0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'template_name': self.template_name,
            'template_description': self.template_description,
            'template_category': self.template_category,
            'template_config': self.template_config,
            'default_tasks': self.default_tasks,
            'default_resources': self.default_resources,
            'default_milestones': self.default_milestones,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'usage_count': self.usage_count,
            'company_id': self.company_id
        })
        return data
