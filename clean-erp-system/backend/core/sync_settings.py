# Synchronization Settings Management
# Advanced configuration for real-time synchronization

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class SyncSettings(BaseModel):
    """Synchronization settings model"""
    __tablename__ = 'sync_settings'
    
    # Basic Settings
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Module Configuration
    source_module = db.Column(db.String(100), nullable=False)
    target_module = db.Column(db.String(100), nullable=False)
    
    # Sync Configuration
    sync_enabled = db.Column(db.Boolean, default=True)
    sync_frequency = db.Column(db.String(50), default='real_time')  # real_time, 5_seconds, 30_seconds, 1_minute
    sync_direction = db.Column(db.String(50), default='bidirectional')  # unidirectional, bidirectional
    
    # Event Configuration
    sync_events = db.Column(db.JSON)  # List of events to sync
    event_filters = db.Column(db.JSON)  # Filters for events
    
    # Data Configuration
    data_mapping = db.Column(db.JSON)  # Field mapping between modules
    data_transformation = db.Column(db.JSON)  # Data transformation rules
    data_validation = db.Column(db.Boolean, default=True)
    
    # Conflict Resolution
    conflict_resolution = db.Column(db.String(50), default='last_modified_wins')  # last_modified_wins, manual, custom
    conflict_resolution_rules = db.Column(db.JSON)  # Custom conflict resolution rules
    
    # Error Handling
    retry_count = db.Column(db.Integer, default=3)
    retry_delay = db.Column(db.Integer, default=5)  # seconds
    error_notification = db.Column(db.Boolean, default=True)
    
    # Logging
    sync_logging = db.Column(db.Boolean, default=True)
    log_level = db.Column(db.String(20), default='INFO')  # DEBUG, INFO, WARNING, ERROR
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'name': self.name,
            'description': self.description,
            'source_module': self.source_module,
            'target_module': self.target_module,
            'sync_enabled': self.sync_enabled,
            'sync_frequency': self.sync_frequency,
            'sync_direction': self.sync_direction,
            'sync_events': self.sync_events,
            'event_filters': self.event_filters,
            'data_mapping': self.data_mapping,
            'data_transformation': self.data_transformation,
            'data_validation': self.data_validation,
            'conflict_resolution': self.conflict_resolution,
            'conflict_resolution_rules': self.conflict_resolution_rules,
            'retry_count': self.retry_count,
            'retry_delay': self.retry_delay,
            'error_notification': self.error_notification,
            'sync_logging': self.sync_logging,
            'log_level': self.log_level,
            'company_id': self.company_id
        })
        return data

class SyncLog(BaseModel):
    """Synchronization log model"""
    __tablename__ = 'sync_logs'
    
    # Sync Reference
    sync_settings_id = db.Column(db.Integer, db.ForeignKey('sync_settings.id'), nullable=False)
    sync_settings = relationship("SyncSettings")
    
    # Sync Details
    sync_type = db.Column(db.String(50), nullable=False)  # data_sync, event_sync, conflict_resolution
    source_entity = db.Column(db.String(100))
    target_entity = db.Column(db.String(100))
    entity_id = db.Column(db.String(100))
    
    # Sync Data
    sync_data = db.Column(db.JSON)
    sync_result = db.Column(db.JSON)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, success, failed, retry
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    
    # Timing
    started_at = db.Column(db.DateTime, default=datetime.now)
    completed_at = db.Column(db.DateTime)
    duration_ms = db.Column(db.Integer)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'sync_settings_id': self.sync_settings_id,
            'sync_type': self.sync_type,
            'source_entity': self.source_entity,
            'target_entity': self.target_entity,
            'entity_id': self.entity_id,
            'sync_data': self.sync_data,
            'sync_result': self.sync_result,
            'status': self.status,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': self.duration_ms,
            'company_id': self.company_id
        })
        return data

class SyncConflict(BaseModel):
    """Synchronization conflict model"""
    __tablename__ = 'sync_conflicts'
    
    # Conflict Reference
    sync_settings_id = db.Column(db.Integer, db.ForeignKey('sync_settings.id'), nullable=False)
    sync_settings = relationship("SyncSettings")
    
    # Conflict Details
    entity_type = db.Column(db.String(100), nullable=False)
    entity_id = db.Column(db.String(100), nullable=False)
    conflict_type = db.Column(db.String(50), nullable=False)  # data_conflict, version_conflict, dependency_conflict
    
    # Conflict Data
    source_data = db.Column(db.JSON)
    target_data = db.Column(db.JSON)
    conflict_details = db.Column(db.JSON)
    
    # Resolution
    resolution_status = db.Column(db.String(20), default='pending')  # pending, resolved, ignored
    resolution_method = db.Column(db.String(50))  # manual, automatic, custom
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    resolved_by = relationship("Employee")
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'sync_settings_id': self.sync_settings_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'conflict_type': self.conflict_type,
            'source_data': self.source_data,
            'target_data': self.target_data,
            'conflict_details': self.conflict_details,
            'resolution_status': self.resolution_status,
            'resolution_method': self.resolution_method,
            'resolved_by_id': self.resolved_by_id,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_notes': self.resolution_notes,
            'company_id': self.company_id
        })
        return data
