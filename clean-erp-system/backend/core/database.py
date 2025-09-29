# Clean ERP System - Database Layer
# Complete database abstraction without Frappe dependencies

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import json

# Initialize database
db = SQLAlchemy()
migrate = Migrate()
Base = declarative_base()

class DatabaseManager:
    """Complete database management system"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize database with Flask app"""
        db.init_app(app)
        migrate.init_app(app, db)
        
        # Create tables
        with app.app_context():
            db.create_all()
    
    def get_session(self):
        """Get database session"""
        return db.session
    
    def commit(self):
        """Commit database changes"""
        db.session.commit()
    
    def rollback(self):
        """Rollback database changes"""
        db.session.rollback()
    
    def close(self):
        """Close database connection"""
        db.session.close()

# Base Model Class
class BaseModel(db.Model):
    """Base model with common fields"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    updated_by = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_active': self.is_active,
            'is_deleted': self.is_deleted
        }
    
    def save(self):
        """Save model to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Soft delete model"""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def hard_delete(self):
        """Permanently delete model"""
        db.session.delete(self)
        db.session.commit()
        return self

# User Management
class User(BaseModel):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(255))
    role = db.Column(db.String(50), default='user')
    permissions = db.Column(db.JSON)
    last_login = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        data = super().to_dict()
        data.update({
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'avatar': self.avatar,
            'role': self.role,
            'permissions': self.permissions,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_verified': self.is_verified
        })
        return data

# Company Management
class Company(BaseModel):
    """Company model for multi-tenant support"""
    __tablename__ = 'companies'
    
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    website = db.Column(db.String(200))
    logo = db.Column(db.String(255))
    currency = db.Column(db.String(3), default='USD')
    timezone = db.Column(db.String(50), default='UTC')
    settings = db.Column(db.JSON)
    
    def to_dict(self):
        """Convert company to dictionary"""
        data = super().to_dict()
        data.update({
            'name': self.name,
            'code': self.code,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'website': self.website,
            'logo': self.logo,
            'currency': self.currency,
            'timezone': self.timezone,
            'settings': self.settings
        })
        return data

# Audit Log
class AuditLog(BaseModel):
    """Audit log for tracking changes"""
    __tablename__ = 'audit_logs'
    
    table_name = db.Column(db.String(100), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)  # CREATE, UPDATE, DELETE
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    def to_dict(self):
        """Convert audit log to dictionary"""
        data = super().to_dict()
        data.update({
            'table_name': self.table_name,
            'record_id': self.record_id,
            'action': self.action,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        })
        return data

# Database Utility Functions
class DatabaseUtils:
    """Database utility functions"""
    
    @staticmethod
    def get_by_id(model_class, record_id):
        """Get record by ID"""
        return model_class.query.filter_by(id=record_id, is_deleted=False).first()
    
    @staticmethod
    def get_by_uuid(model_class, record_uuid):
        """Get record by UUID"""
        return model_class.query.filter_by(uuid=record_uuid, is_deleted=False).first()
    
    @staticmethod
    def get_all(model_class, filters=None, limit=None, offset=None):
        """Get all records with optional filters"""
        query = model_class.query.filter_by(is_deleted=False)
        
        if filters:
            for key, value in filters.items():
                if hasattr(model_class, key):
                    query = query.filter(getattr(model_class, key) == value)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def count(model_class, filters=None):
        """Count records with optional filters"""
        query = model_class.query.filter_by(is_deleted=False)
        
        if filters:
            for key, value in filters.items():
                if hasattr(model_class, key):
                    query = query.filter(getattr(model_class, key) == value)
        
        return query.count()
    
    @staticmethod
    def exists(model_class, filters):
        """Check if record exists"""
        query = model_class.query.filter_by(is_deleted=False)
        
        for key, value in filters.items():
            if hasattr(model_class, key):
                query = query.filter(getattr(model_class, key) == value)
        
        return query.first() is not None
    
    @staticmethod
    def create(model_class, data):
        """Create new record"""
        record = model_class(**data)
        return record.save()
    
    @staticmethod
    def update(model_class, record_id, data):
        """Update record"""
        record = DatabaseUtils.get_by_id(model_class, record_id)
        if record:
            for key, value in data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            record.updated_at = datetime.utcnow()
            record.save()
        return record
    
    @staticmethod
    def delete(model_class, record_id):
        """Soft delete record"""
        record = DatabaseUtils.get_by_id(model_class, record_id)
        if record:
            record.delete()
        return record

# Initialize database manager
db_manager = DatabaseManager()
