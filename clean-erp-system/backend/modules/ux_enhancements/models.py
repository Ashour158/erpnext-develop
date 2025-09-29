# UX Enhancements Models
# Database models for personalization and accessibility features

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from core.database import Base

class UserPreference(Base):
    """User preferences for personalization"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    preference_key = Column(String(100), nullable=False)
    preference_value = Column(Text)
    preference_type = Column(String(50), default='string')  # string, number, boolean, json
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="preferences")

class UserTheme(Base):
    """User theme preferences"""
    __tablename__ = 'user_themes'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    theme_name = Column(String(100), nullable=False)
    theme_type = Column(String(50), default='light')  # light, dark, auto
    primary_color = Column(String(7))  # Hex color code
    secondary_color = Column(String(7))
    accent_color = Column(String(7))
    background_color = Column(String(7))
    text_color = Column(String(7))
    font_family = Column(String(100))
    font_size = Column(String(20), default='medium')  # small, medium, large
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="themes")

class UserLayout(Base):
    """User layout preferences"""
    __tablename__ = 'user_layouts'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    layout_name = Column(String(100), nullable=False)
    layout_type = Column(String(50), default='default')  # default, compact, spacious
    sidebar_position = Column(String(20), default='left')  # left, right, hidden
    sidebar_width = Column(Integer, default=250)
    header_height = Column(Integer, default=60)
    footer_visible = Column(Boolean, default=True)
    grid_columns = Column(Integer, default=12)
    card_size = Column(String(20), default='medium')  # small, medium, large
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="layouts")

class UserDashboard(Base):
    """User dashboard configuration"""
    __tablename__ = 'user_dashboards'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    dashboard_name = Column(String(100), nullable=False)
    dashboard_type = Column(String(50), default='personal')  # personal, shared, template
    widgets = Column(JSON)  # Array of widget configurations
    layout_config = Column(JSON)  # Dashboard layout configuration
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="dashboards")

class AccessibilitySetting(Base):
    """Accessibility settings for users"""
    __tablename__ = 'accessibility_settings'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    setting_name = Column(String(100), nullable=False)
    setting_value = Column(Text)
    setting_type = Column(String(50), default='boolean')  # boolean, string, number
    category = Column(String(50), default='general')  # general, visual, auditory, motor, cognitive
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="accessibility_settings")

class UserNotification(Base):
    """User notification preferences"""
    __tablename__ = 'user_notifications'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    notification_type = Column(String(100), nullable=False)
    notification_channel = Column(String(50), default='email')  # email, sms, push, in_app
    is_enabled = Column(Boolean, default=True)
    frequency = Column(String(20), default='immediate')  # immediate, daily, weekly, monthly
    quiet_hours_start = Column(String(5))  # HH:MM format
    quiet_hours_end = Column(String(5))  # HH:MM format
    timezone = Column(String(50), default='UTC')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="notifications")

class UserShortcut(Base):
    """User keyboard shortcuts"""
    __tablename__ = 'user_shortcuts'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shortcut_name = Column(String(100), nullable=False)
    shortcut_key = Column(String(50), nullable=False)  # e.g., "Ctrl+S"
    shortcut_action = Column(String(200), nullable=False)  # Action to perform
    shortcut_category = Column(String(50), default='general')  # general, navigation, editing
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="shortcuts")

class UserWorkspace(Base):
    """User workspace configuration"""
    __tablename__ = 'user_workspaces'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    workspace_name = Column(String(100), nullable=False)
    workspace_type = Column(String(50), default='personal')  # personal, shared, template
    modules = Column(JSON)  # Array of enabled modules
    module_order = Column(JSON)  # Order of modules in workspace
    module_config = Column(JSON)  # Module-specific configuration
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="workspaces")

class UserActivity(Base):
    """User activity tracking for personalization"""
    __tablename__ = 'user_activities'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    activity_type = Column(String(100), nullable=False)  # login, module_access, feature_use, etc.
    activity_data = Column(JSON)  # Additional activity data
    module_name = Column(String(100))
    feature_name = Column(String(100))
    duration_seconds = Column(Integer, default=0)
    activity_timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(Text)
    
    user = relationship("User", back_populates="activities")

class UserRecommendation(Base):
    """User recommendations based on activity"""
    __tablename__ = 'user_recommendations'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    recommendation_type = Column(String(100), nullable=False)  # feature, module, shortcut, etc.
    recommendation_title = Column(String(200), nullable=False)
    recommendation_description = Column(Text)
    recommendation_data = Column(JSON)  # Recommendation-specific data
    priority = Column(Integer, default=1)  # 1-5, higher is more important
    is_read = Column(Boolean, default=False)
    is_accepted = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    user = relationship("User", back_populates="recommendations")

class UserFeedback(Base):
    """User feedback for UX improvements"""
    __tablename__ = 'user_feedback'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    feedback_type = Column(String(50), default='general')  # general, bug, feature, accessibility
    feedback_title = Column(String(200), nullable=False)
    feedback_description = Column(Text, nullable=False)
    feedback_rating = Column(Integer)  # 1-5 rating
    module_name = Column(String(100))
    feature_name = Column(String(100))
    feedback_data = Column(JSON)  # Additional feedback data
    status = Column(String(20), default='pending')  # pending, reviewed, resolved, closed
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="feedback")

class UserTutorial(Base):
    """User tutorial progress"""
    __tablename__ = 'user_tutorials'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    tutorial_name = Column(String(100), nullable=False)
    tutorial_type = Column(String(50), default='interactive')  # interactive, video, text
    tutorial_module = Column(String(100))
    tutorial_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=1)
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="tutorials")

class UserHelp(Base):
    """User help and support requests"""
    __tablename__ = 'user_help'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    help_type = Column(String(50), default='question')  # question, issue, feature_request
    help_title = Column(String(200), nullable=False)
    help_description = Column(Text, nullable=False)
    help_category = Column(String(100))
    help_priority = Column(String(20), default='medium')  # low, medium, high, urgent
    status = Column(String(20), default='open')  # open, in_progress, resolved, closed
    assigned_to = Column(Integer, ForeignKey('users.id'))
    resolution = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="help_requests", foreign_keys=[user_id])
    assignee = relationship("User", back_populates="assigned_help", foreign_keys=[assigned_to])

class UserSession(Base):
    """User session tracking for personalization"""
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(String(100), nullable=False, unique=True)
    session_data = Column(JSON)  # Session-specific data
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    user = relationship("User", back_populates="sessions")
