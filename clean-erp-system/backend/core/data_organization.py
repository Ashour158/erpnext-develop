# Data Organization and Archiving System
# Advanced data management and archiving

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum

class DataCategory(enum.Enum):
    TRANSACTIONAL = "Transactional"
    REFERENCE = "Reference"
    AUDIT = "Audit"
    TEMPORARY = "Temporary"
    ARCHIVED = "Archived"

class DataRetentionPolicy(enum.Enum):
    KEEP_FOREVER = "Keep Forever"
    DELETE_AFTER = "Delete After"
    ARCHIVE_AFTER = "Archive After"
    COMPRESS_AFTER = "Compress After"

class DataArchive(BaseModel):
    """Data archive model"""
    __tablename__ = 'data_archives'
    
    # Archive Information
    archive_name = db.Column(db.String(200), nullable=False)
    archive_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Archive Configuration
    source_table = db.Column(db.String(200), nullable=False)
    archive_criteria = db.Column(db.JSON)  # Archive criteria configuration
    archive_schedule = db.Column(db.JSON)  # Archive schedule configuration
    
    # Archive Settings
    is_active = db.Column(db.Boolean, default=True)
    is_automatic = db.Column(db.Boolean, default=False)
    retention_period = db.Column(db.Integer, default=365)  # days
    
    # Archive Statistics
    total_records = db.Column(db.Integer, default=0)
    archived_records = db.Column(db.Integer, default=0)
    last_archive_date = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'archive_name': self.archive_name,
            'archive_code': self.archive_code,
            'description': self.description,
            'source_table': self.source_table,
            'archive_criteria': self.archive_criteria,
            'archive_schedule': self.archive_schedule,
            'is_active': self.is_active,
            'is_automatic': self.is_automatic,
            'retention_period': self.retention_period,
            'total_records': self.total_records,
            'archived_records': self.archived_records,
            'last_archive_date': self.last_archive_date.isoformat() if self.last_archive_date else None,
            'company_id': self.company_id
        })
        return data

class DataRetentionRule(BaseModel):
    """Data retention rule model"""
    __tablename__ = 'data_retention_rules'
    
    # Rule Information
    rule_name = db.Column(db.String(200), nullable=False)
    rule_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Rule Configuration
    target_table = db.Column(db.String(200), nullable=False)
    retention_policy = db.Column(db.Enum(DataRetentionPolicy), nullable=False)
    retention_period = db.Column(db.Integer, nullable=False)  # days
    retention_criteria = db.Column(db.JSON)  # Retention criteria configuration
    
    # Rule Settings
    is_active = db.Column(db.Boolean, default=True)
    is_automatic = db.Column(db.Boolean, default=False)
    notification_enabled = db.Column(db.Boolean, default=True)
    
    # Rule Statistics
    total_records = db.Column(db.Integer, default=0)
    processed_records = db.Column(db.Integer, default=0)
    last_processing_date = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'rule_name': self.rule_name,
            'rule_code': self.rule_code,
            'description': self.description,
            'target_table': self.target_table,
            'retention_policy': self.retention_policy.value if self.retention_policy else None,
            'retention_period': self.retention_period,
            'retention_criteria': self.retention_criteria,
            'is_active': self.is_active,
            'is_automatic': self.is_automatic,
            'notification_enabled': self.notification_enabled,
            'total_records': self.total_records,
            'processed_records': self.processed_records,
            'last_processing_date': self.last_processing_date.isoformat() if self.last_processing_date else None,
            'company_id': self.company_id
        })
        return data

class DataBackup(BaseModel):
    """Data backup model"""
    __tablename__ = 'data_backups'
    
    # Backup Information
    backup_name = db.Column(db.String(200), nullable=False)
    backup_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Backup Configuration
    backup_type = db.Column(db.String(50), nullable=False)  # Full, Incremental, Differential
    backup_schedule = db.Column(db.JSON)  # Backup schedule configuration
    backup_location = db.Column(db.String(500), nullable=False)
    
    # Backup Settings
    is_active = db.Column(db.Boolean, default=True)
    is_automatic = db.Column(db.Boolean, default=False)
    compression_enabled = db.Column(db.Boolean, default=True)
    encryption_enabled = db.Column(db.Boolean, default=False)
    
    # Backup Statistics
    backup_size = db.Column(db.Float, default=0.0)  # MB
    backup_duration = db.Column(db.Integer, default=0)  # seconds
    last_backup_date = db.Column(db.DateTime)
    backup_status = db.Column(db.String(50), default='Pending')
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'backup_name': self.backup_name,
            'backup_code': self.backup_code,
            'description': self.description,
            'backup_type': self.backup_type,
            'backup_schedule': self.backup_schedule,
            'backup_location': self.backup_location,
            'is_active': self.is_active,
            'is_automatic': self.is_automatic,
            'compression_enabled': self.compression_enabled,
            'encryption_enabled': self.encryption_enabled,
            'backup_size': self.backup_size,
            'backup_duration': self.backup_duration,
            'last_backup_date': self.last_backup_date.isoformat() if self.last_backup_date else None,
            'backup_status': self.backup_status,
            'company_id': self.company_id
        })
        return data

class DataIndex(BaseModel):
    """Data index model"""
    __tablename__ = 'data_indexes'
    
    # Index Information
    index_name = db.Column(db.String(200), nullable=False)
    index_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Index Configuration
    target_table = db.Column(db.String(200), nullable=False)
    index_columns = db.Column(db.JSON)  # Index columns configuration
    index_type = db.Column(db.String(50), default='BTree')  # BTree, Hash, GIN, etc.
    
    # Index Settings
    is_active = db.Column(db.Boolean, default=True)
    is_unique = db.Column(db.Boolean, default=False)
    is_primary = db.Column(db.Boolean, default=False)
    
    # Index Statistics
    index_size = db.Column(db.Float, default=0.0)  # MB
    index_usage = db.Column(db.Integer, default=0)
    last_usage_date = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'index_name': self.index_name,
            'index_code': self.index_code,
            'description': self.description,
            'target_table': self.target_table,
            'index_columns': self.index_columns,
            'index_type': self.index_type,
            'is_active': self.is_active,
            'is_unique': self.is_unique,
            'is_primary': self.is_primary,
            'index_size': self.index_size,
            'index_usage': self.index_usage,
            'last_usage_date': self.last_usage_date.isoformat() if self.last_usage_date else None,
            'company_id': self.company_id
        })
        return data

class DataPartition(BaseModel):
    """Data partition model"""
    __tablename__ = 'data_partitions'
    
    # Partition Information
    partition_name = db.Column(db.String(200), nullable=False)
    partition_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Partition Configuration
    target_table = db.Column(db.String(200), nullable=False)
    partition_key = db.Column(db.String(200), nullable=False)
    partition_type = db.Column(db.String(50), default='Range')  # Range, List, Hash
    partition_criteria = db.Column(db.JSON)  # Partition criteria configuration
    
    # Partition Settings
    is_active = db.Column(db.Boolean, default=True)
    is_automatic = db.Column(db.Boolean, default=False)
    partition_size = db.Column(db.Integer, default=1000000)  # records per partition
    
    # Partition Statistics
    total_partitions = db.Column(db.Integer, default=0)
    active_partitions = db.Column(db.Integer, default=0)
    last_partition_date = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'partition_name': self.partition_name,
            'partition_code': self.partition_code,
            'description': self.description,
            'target_table': self.target_table,
            'partition_key': self.partition_key,
            'partition_type': self.partition_type,
            'partition_criteria': self.partition_criteria,
            'is_active': self.is_active,
            'is_automatic': self.is_automatic,
            'partition_size': self.partition_size,
            'total_partitions': self.total_partitions,
            'active_partitions': self.active_partitions,
            'last_partition_date': self.last_partition_date.isoformat() if self.last_partition_date else None,
            'company_id': self.company_id
        })
        return data
