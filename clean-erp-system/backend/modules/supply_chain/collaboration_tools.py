# Collaboration Tools for Supply Chain
# Enhanced team collaboration and communication features

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class CollaborationType(enum.Enum):
    PROJECT = "project"
    TASK = "task"
    DISCUSSION = "discussion"
    DOCUMENT = "document"
    MEETING = "meeting"
    WORKFLOW = "workflow"
    ANNOUNCEMENT = "announcement"
    POLL = "poll"
    SURVEY = "survey"

class Priority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Status(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class NotificationType(enum.Enum):
    MENTION = "mention"
    ASSIGNMENT = "assignment"
    DEADLINE = "deadline"
    UPDATE = "update"
    COMMENT = "comment"
    APPROVAL = "approval"
    REMINDER = "reminder"

# Collaboration Projects
class CollaborationProject(Base):
    __tablename__ = 'collaboration_projects'
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Project details
    project_name = Column(String(255), nullable=False)
    project_description = Column(Text)
    project_type = Column(Enum(CollaborationType), default=CollaborationType.PROJECT)
    
    # Project scope
    scope_items = Column(JSON)  # Items included in project
    scope_suppliers = Column(JSON)  # Suppliers included in project
    scope_facilities = Column(JSON)  # Facilities included in project
    scope_users = Column(JSON)  # Users included in project
    
    # Project timeline
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    deadline = Column(DateTime)
    is_milestone_based = Column(Boolean, default=False)
    
    # Project status
    status = Column(Enum(Status), default=Status.DRAFT)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    progress_percentage = Column(Float, default=0.0)
    
    # Project team
    project_owner = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_manager = Column(Integer, ForeignKey('users.id'))
    team_members = Column(JSON)  # List of team member IDs
    stakeholders = Column(JSON)  # List of stakeholder IDs
    
    # Project settings
    is_public = Column(Boolean, default=False)
    allow_guest_access = Column(Boolean, default=False)
    notification_settings = Column(JSON)  # Notification preferences
    
    # Project metrics
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    overdue_tasks = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    owner = relationship("User", foreign_keys=[project_owner])
    manager = relationship("User", foreign_keys=[project_manager])
    creator = relationship("User", foreign_keys=[created_by])
    tasks = relationship("CollaborationTask", back_populates="project", cascade="all, delete-orphan")
    discussions = relationship("CollaborationDiscussion", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("CollaborationDocument", back_populates="project", cascade="all, delete-orphan")
    meetings = relationship("CollaborationMeeting", back_populates="project", cascade="all, delete-orphan")

# Collaboration Tasks
class CollaborationTask(Base):
    __tablename__ = 'collaboration_tasks'
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey('collaboration_projects.id'), nullable=False)
    
    # Task details
    task_name = Column(String(255), nullable=False)
    task_description = Column(Text)
    task_type = Column(Enum(CollaborationType), default=CollaborationType.TASK)
    
    # Task assignment
    assigned_to = Column(Integer, ForeignKey('users.id'))
    assigned_by = Column(Integer, ForeignKey('users.id'))
    assigned_date = Column(DateTime, default=datetime.utcnow)
    
    # Task status
    status = Column(Enum(Status), default=Status.DRAFT)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    progress_percentage = Column(Float, default=0.0)
    
    # Task timeline
    start_date = Column(DateTime)
    due_date = Column(DateTime)
    completed_date = Column(DateTime)
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    
    # Task dependencies
    depends_on = Column(JSON)  # List of task IDs this task depends on
    blocks = Column(JSON)  # List of task IDs this task blocks
    
    # Task details
    task_notes = Column(Text)
    task_attachments = Column(JSON)  # List of attachment file paths
    task_tags = Column(JSON)  # List of tags
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    
    # Task metrics
    comment_count = Column(Integer, default=0)
    attachment_count = Column(Integer, default=0)
    time_logged = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    project = relationship("CollaborationProject", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assigned_to])
    assigner = relationship("User", foreign_keys=[assigned_by])
    creator = relationship("User", foreign_keys=[created_by])
    item = relationship("EnhancedItem")
    supplier = relationship("Supplier")
    facility = relationship("Facility")
    comments = relationship("CollaborationComment", back_populates="task", cascade="all, delete-orphan")
    time_entries = relationship("CollaborationTimeEntry", back_populates="task", cascade="all, delete-orphan")

# Collaboration Discussions
class CollaborationDiscussion(Base):
    __tablename__ = 'collaboration_discussions'
    
    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(String(100), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey('collaboration_projects.id'), nullable=False)
    
    # Discussion details
    discussion_title = Column(String(255), nullable=False)
    discussion_description = Column(Text)
    discussion_type = Column(Enum(CollaborationType), default=CollaborationType.DISCUSSION)
    
    # Discussion settings
    is_public = Column(Boolean, default=True)
    allow_anonymous = Column(Boolean, default=False)
    moderation_required = Column(Boolean, default=False)
    
    # Discussion status
    status = Column(Enum(Status), default=Status.ACTIVE)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    
    # Discussion metrics
    view_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Discussion tags
    tags = Column(JSON)  # List of discussion tags
    categories = Column(JSON)  # List of discussion categories
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    project = relationship("CollaborationProject", back_populates="discussions")
    creator = relationship("User")
    item = relationship("EnhancedItem")
    supplier = relationship("Supplier")
    facility = relationship("Facility")
    comments = relationship("CollaborationComment", back_populates="discussion", cascade="all, delete-orphan")

# Collaboration Comments
class CollaborationComment(Base):
    __tablename__ = 'collaboration_comments'
    
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Comment details
    comment_content = Column(Text, nullable=False)
    comment_type = Column(String(50), default='text')  # text, image, file, link
    
    # Comment threading
    parent_comment_id = Column(Integer, ForeignKey('collaboration_comments.id'))
    thread_id = Column(Integer, ForeignKey('collaboration_comments.id'))
    depth_level = Column(Integer, default=0)
    
    # Comment targets
    task_id = Column(Integer, ForeignKey('collaboration_tasks.id'))
    discussion_id = Column(Integer, ForeignKey('collaboration_discussions.id'))
    document_id = Column(Integer, ForeignKey('collaboration_documents.id'))
    meeting_id = Column(Integer, ForeignKey('collaboration_meetings.id'))
    
    # Comment status
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    # Comment interactions
    like_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    
    # Comment attachments
    attachments = Column(JSON)  # List of attachment file paths
    mentions = Column(JSON)  # List of mentioned user IDs
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    parent_comment = relationship("CollaborationComment", remote_side=[id], foreign_keys=[parent_comment_id])
    thread = relationship("CollaborationComment", remote_side=[id], foreign_keys=[thread_id])
    task = relationship("CollaborationTask", back_populates="comments")
    discussion = relationship("CollaborationDiscussion", back_populates="comments")
    document = relationship("CollaborationDocument")
    meeting = relationship("CollaborationMeeting")
    creator = relationship("User")

# Collaboration Documents
class CollaborationDocument(Base):
    __tablename__ = 'collaboration_documents'
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(100), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey('collaboration_projects.id'), nullable=False)
    
    # Document details
    document_name = Column(String(255), nullable=False)
    document_description = Column(Text)
    document_type = Column(Enum(CollaborationType), default=CollaborationType.DOCUMENT)
    
    # Document content
    document_content = Column(Text)  # Document content
    document_format = Column(String(20), default='text')  # text, markdown, html, pdf
    document_size = Column(Integer)  # Document size in bytes
    
    # Document files
    file_path = Column(String(500))  # Path to document file
    file_type = Column(String(20))  # File type
    file_version = Column(String(20), default='1.0')  # Document version
    
    # Document settings
    is_public = Column(Boolean, default=False)
    allow_comments = Column(Boolean, default=True)
    allow_editing = Column(Boolean, default=True)
    require_approval = Column(Boolean, default=False)
    
    # Document status
    status = Column(Enum(Status), default=Status.DRAFT)
    is_locked = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Document metrics
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    version_count = Column(Integer, default=1)
    
    # Document tags
    tags = Column(JSON)  # List of document tags
    categories = Column(JSON)  # List of document categories
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    project = relationship("CollaborationProject", back_populates="documents")
    creator = relationship("User")
    item = relationship("EnhancedItem")
    supplier = relationship("Supplier")
    facility = relationship("Facility")
    comments = relationship("CollaborationComment", back_populates="document", cascade="all, delete-orphan")
    versions = relationship("CollaborationDocumentVersion", back_populates="document", cascade="all, delete-orphan")

# Collaboration Document Versions
class CollaborationDocumentVersion(Base):
    __tablename__ = 'collaboration_document_versions'
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('collaboration_documents.id'), nullable=False)
    
    # Version details
    version_number = Column(String(20), nullable=False)
    version_notes = Column(Text)
    version_changes = Column(Text)  # Summary of changes
    
    # Version content
    document_content = Column(Text)
    file_path = Column(String(500))
    file_size = Column(Integer)
    
    # Version status
    is_current = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey('users.id'))
    approved_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    document = relationship("CollaborationDocument", back_populates="versions")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])

# Collaboration Meetings
class CollaborationMeeting(Base):
    __tablename__ = 'collaboration_meetings'
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(String(100), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey('collaboration_projects.id'), nullable=False)
    
    # Meeting details
    meeting_title = Column(String(255), nullable=False)
    meeting_description = Column(Text)
    meeting_type = Column(Enum(CollaborationType), default=CollaborationType.MEETING)
    
    # Meeting schedule
    meeting_date = Column(DateTime, nullable=False)
    meeting_duration = Column(Integer, default=60)  # Duration in minutes
    timezone = Column(String(50), default='UTC')
    
    # Meeting location
    meeting_location = Column(String(255))
    meeting_room = Column(String(255))
    is_virtual = Column(Boolean, default=False)
    meeting_url = Column(String(500))  # Virtual meeting URL
    
    # Meeting participants
    organizer = Column(Integer, ForeignKey('users.id'), nullable=False)
    attendees = Column(JSON)  # List of attendee IDs
    required_attendees = Column(JSON)  # List of required attendee IDs
    optional_attendees = Column(JSON)  # List of optional attendee IDs
    
    # Meeting status
    status = Column(Enum(Status), default=Status.DRAFT)
    meeting_agenda = Column(Text)
    meeting_notes = Column(Text)
    action_items = Column(JSON)  # List of action items
    
    # Meeting materials
    meeting_materials = Column(JSON)  # List of material file paths
    meeting_recording = Column(String(500))  # Path to meeting recording
    
    # Meeting metrics
    attendance_count = Column(Integer, default=0)
    duration_actual = Column(Integer)  # Actual duration in minutes
    satisfaction_score = Column(Float)  # Meeting satisfaction score
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    project = relationship("CollaborationProject", back_populates="meetings")
    meeting_organizer = relationship("User", foreign_keys=[organizer])
    creator = relationship("User", foreign_keys=[created_by])
    item = relationship("EnhancedItem")
    supplier = relationship("Supplier")
    facility = relationship("Facility")
    comments = relationship("CollaborationComment", back_populates="meeting", cascade="all, delete-orphan")
    attendees_records = relationship("CollaborationMeetingAttendance", back_populates="meeting", cascade="all, delete-orphan")

# Collaboration Meeting Attendance
class CollaborationMeetingAttendance(Base):
    __tablename__ = 'collaboration_meeting_attendance'
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey('collaboration_meetings.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Attendance details
    attendance_status = Column(String(20), default='invited')  # invited, accepted, declined, attended, absent
    response_date = Column(DateTime)
    attendance_date = Column(DateTime)
    
    # Attendance metrics
    join_time = Column(DateTime)
    leave_time = Column(DateTime)
    attendance_duration = Column(Integer)  # Duration in minutes
    participation_score = Column(Float)  # Participation score
    
    # Feedback
    feedback_rating = Column(Integer)  # 1-5 rating
    feedback_comments = Column(Text)
    suggestions = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    meeting = relationship("CollaborationMeeting", back_populates="attendees_records")
    user = relationship("User")

# Collaboration Time Entries
class CollaborationTimeEntry(Base):
    __tablename__ = 'collaboration_time_entries'
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('collaboration_tasks.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Time entry details
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration = Column(Float)  # Duration in hours
    description = Column(Text)
    
    # Time entry status
    is_billable = Column(Boolean, default=False)
    hourly_rate = Column(Float)
    total_cost = Column(Float)
    
    # Time entry approval
    is_approved = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey('users.id'))
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    task = relationship("CollaborationTask", back_populates="time_entries")
    user = relationship("User", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approved_by])

# Collaboration Notifications
class CollaborationNotification(Base):
    __tablename__ = 'collaboration_notifications'
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Notification details
    notification_type = Column(Enum(NotificationType), nullable=False)
    notification_title = Column(String(255), nullable=False)
    notification_message = Column(Text, nullable=False)
    
    # Notification targets
    recipient_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'))
    
    # Notification content
    notification_data = Column(JSON)  # Additional notification data
    notification_url = Column(String(500))  # URL to related content
    
    # Related entities
    project_id = Column(Integer, ForeignKey('collaboration_projects.id'))
    task_id = Column(Integer, ForeignKey('collaboration_tasks.id'))
    discussion_id = Column(Integer, ForeignKey('collaboration_discussions.id'))
    document_id = Column(Integer, ForeignKey('collaboration_documents.id'))
    meeting_id = Column(Integer, ForeignKey('collaboration_meetings.id'))
    
    # Notification status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    
    # Notification delivery
    delivery_method = Column(String(20), default='in_app')  # in_app, email, sms, push
    delivery_status = Column(String(20), default='pending')  # pending, sent, delivered, failed
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    recipient = relationship("User", foreign_keys=[recipient_id])
    sender = relationship("User", foreign_keys=[sender_id])
    project = relationship("CollaborationProject")
    task = relationship("CollaborationTask")
    discussion = relationship("CollaborationDiscussion")
    document = relationship("CollaborationDocument")
    meeting = relationship("CollaborationMeeting")

# Collaboration Workspaces
class CollaborationWorkspace(Base):
    __tablename__ = 'collaboration_workspaces'
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Workspace details
    workspace_name = Column(String(255), nullable=False)
    workspace_description = Column(Text)
    workspace_type = Column(String(50), default='general')  # general, project, department, team
    
    # Workspace settings
    is_public = Column(Boolean, default=False)
    allow_guest_access = Column(Boolean, default=False)
    require_approval = Column(Boolean, default=False)
    
    # Workspace members
    workspace_owner = Column(Integer, ForeignKey('users.id'), nullable=False)
    workspace_members = Column(JSON)  # List of member IDs
    workspace_admins = Column(JSON)  # List of admin IDs
    
    # Workspace content
    total_projects = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    total_discussions = Column(Integer, default=0)
    total_documents = Column(Integer, default=0)
    total_meetings = Column(Integer, default=0)
    
    # Workspace status
    status = Column(Enum(Status), default=Status.ACTIVE)
    is_archived = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    owner = relationship("User", foreign_keys=[workspace_owner])
    creator = relationship("User", foreign_keys=[created_by])
    projects = relationship("CollaborationProject", cascade="all, delete-orphan")

# Collaboration Analytics
class CollaborationAnalytics(Base):
    __tablename__ = 'collaboration_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    analytics_type = Column(String(50), nullable=False)  # engagement, productivity, collaboration, performance
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Analytics data
    analytics_data = Column(JSON, nullable=False)
    key_metrics = Column(JSON)  # Key metrics
    trends = Column(JSON)  # Trend analysis
    insights = Column(JSON)  # Key insights
    recommendations = Column(JSON)  # Recommendations
    
    # User analytics
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    user_engagement_score = Column(Float, default=0.0)
    user_productivity_score = Column(Float, default=0.0)
    
    # Content analytics
    total_projects = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    total_discussions = Column(Integer, default=0)
    total_documents = Column(Integer, default=0)
    total_meetings = Column(Integer, default=0)
    
    # Collaboration metrics
    collaboration_score = Column(Float, default=0.0)
    communication_frequency = Column(Float, default=0.0)
    response_time = Column(Float, default=0.0)
    meeting_effectiveness = Column(Float, default=0.0)
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    calculated_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    calculator = relationship("User")
