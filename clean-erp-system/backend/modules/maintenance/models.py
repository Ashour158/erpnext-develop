# Maintenance Models - Complete Asset and Maintenance Management
# Advanced maintenance models without Frappe dependencies

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

# Enums
class AssetStatus(enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    UNDER_MAINTENANCE = "Under Maintenance"
    RETIRED = "Retired"
    DISPOSED = "Disposed"

class MaintenanceType(enum.Enum):
    PREVENTIVE = "Preventive"
    CORRECTIVE = "Corrective"
    EMERGENCY = "Emergency"
    PREDICTIVE = "Predictive"

class WorkOrderStatus(enum.Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class Priority(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

# Asset Category Model
class AssetCategory(BaseModel):
    """Asset Category model"""
    __tablename__ = 'asset_categories'
    
    category_name = db.Column(db.String(200), nullable=False)
    category_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Category Settings
    depreciation_method = db.Column(db.String(50))  # Straight Line, Declining Balance, etc.
    useful_life_years = db.Column(db.Float, default=0.0)
    residual_value = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    assets = relationship("Asset", back_populates="category")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'category_name': self.category_name,
            'category_code': self.category_code,
            'description': self.description,
            'depreciation_method': self.depreciation_method,
            'useful_life_years': self.useful_life_years,
            'residual_value': self.residual_value,
            'company_id': self.company_id
        })
        return data

# Asset Location Model
class AssetLocation(BaseModel):
    """Asset Location model"""
    __tablename__ = 'asset_locations'
    
    location_name = db.Column(db.String(200), nullable=False)
    location_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Location Details
    address_line_1 = db.Column(db.String(200))
    address_line_2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Location Manager
    location_manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    location_manager = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    assets = relationship("Asset", back_populates="location")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'location_name': self.location_name,
            'location_code': self.location_code,
            'description': self.description,
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'location_manager_id': self.location_manager_id,
            'company_id': self.company_id
        })
        return data

# Asset Model
class Asset(BaseModel):
    """Asset model"""
    __tablename__ = 'assets'
    
    asset_name = db.Column(db.String(200), nullable=False)
    asset_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Asset Details
    asset_category_id = db.Column(db.Integer, db.ForeignKey('asset_categories.id'), nullable=False)
    category = relationship("AssetCategory", back_populates="assets")
    
    asset_location_id = db.Column(db.Integer, db.ForeignKey('asset_locations.id'))
    location = relationship("AssetLocation", back_populates="assets")
    
    # Asset Information
    manufacturer = db.Column(db.String(200))
    model_number = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    warranty_expiry_date = db.Column(db.Date)
    
    # Financial Information
    purchase_cost = db.Column(db.Float, default=0.0)
    current_value = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Asset Status
    status = db.Column(db.Enum(AssetStatus), default=AssetStatus.ACTIVE)
    is_critical = db.Column(db.Boolean, default=False)
    
    # Maintenance Information
    last_maintenance_date = db.Column(db.Date)
    next_maintenance_date = db.Column(db.Date)
    maintenance_frequency_days = db.Column(db.Integer, default=0)
    
    # Asset Custodian
    custodian_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    custodian = relationship("Employee", foreign_keys=[custodian_id])
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    maintenance_schedules = relationship("MaintenanceSchedule", back_populates="asset")
    work_orders = relationship("WorkOrder", back_populates="asset")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'asset_name': self.asset_name,
            'asset_code': self.asset_code,
            'description': self.description,
            'asset_category_id': self.asset_category_id,
            'asset_location_id': self.asset_location_id,
            'manufacturer': self.manufacturer,
            'model_number': self.model_number,
            'serial_number': self.serial_number,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'warranty_expiry_date': self.warranty_expiry_date.isoformat() if self.warranty_expiry_date else None,
            'purchase_cost': self.purchase_cost,
            'current_value': self.current_value,
            'currency': self.currency,
            'status': self.status.value if self.status else None,
            'is_critical': self.is_critical,
            'last_maintenance_date': self.last_maintenance_date.isoformat() if self.last_maintenance_date else None,
            'next_maintenance_date': self.next_maintenance_date.isoformat() if self.next_maintenance_date else None,
            'maintenance_frequency_days': self.maintenance_frequency_days,
            'custodian_id': self.custodian_id,
            'company_id': self.company_id
        })
        return data

# Maintenance Team Model
class MaintenanceTeam(BaseModel):
    """Maintenance Team model"""
    __tablename__ = 'maintenance_teams'
    
    team_name = db.Column(db.String(200), nullable=False)
    team_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Team Lead
    team_lead_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    team_lead = relationship("Employee")
    
    # Team Members (stored as JSON for simplicity)
    team_members = db.Column(db.JSON)
    
    # Specialization
    specialization = db.Column(db.String(200))
    skills = db.Column(db.JSON)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    work_orders = relationship("WorkOrder", back_populates="assigned_team")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'team_name': self.team_name,
            'team_code': self.team_code,
            'description': self.description,
            'team_lead_id': self.team_lead_id,
            'team_members': self.team_members,
            'specialization': self.specialization,
            'skills': self.skills,
            'company_id': self.company_id
        })
        return data

# Maintenance Schedule Model
class MaintenanceSchedule(BaseModel):
    """Maintenance Schedule model"""
    __tablename__ = 'maintenance_schedules'
    
    # Asset
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    asset = relationship("Asset", back_populates="maintenance_schedules")
    
    # Schedule Details
    schedule_name = db.Column(db.String(200), nullable=False)
    maintenance_type = db.Column(db.Enum(MaintenanceType), nullable=False)
    
    # Schedule Information
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    frequency_days = db.Column(db.Integer, default=0)
    
    # Maintenance Details
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    estimated_duration_hours = db.Column(db.Float, default=0.0)
    
    # Status
    status = db.Column(db.String(20), default='Active')  # Active, Inactive, Completed
    is_recurring = db.Column(db.Boolean, default=True)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    maintenance_tasks = relationship("MaintenanceTask", back_populates="schedule")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'asset_id': self.asset_id,
            'schedule_name': self.schedule_name,
            'maintenance_type': self.maintenance_type.value if self.maintenance_type else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'frequency_days': self.frequency_days,
            'description': self.description,
            'instructions': self.instructions,
            'estimated_duration_hours': self.estimated_duration_hours,
            'status': self.status,
            'is_recurring': self.is_recurring,
            'company_id': self.company_id
        })
        return data

# Maintenance Task Model
class MaintenanceTask(BaseModel):
    """Maintenance Task model"""
    __tablename__ = 'maintenance_tasks'
    
    # Schedule
    schedule_id = db.Column(db.Integer, db.ForeignKey('maintenance_schedules.id'), nullable=False)
    schedule = relationship("MaintenanceSchedule", back_populates="maintenance_tasks")
    
    # Task Details
    task_name = db.Column(db.String(200), nullable=False)
    task_description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    
    # Task Information
    estimated_duration_hours = db.Column(db.Float, default=0.0)
    actual_duration_hours = db.Column(db.Float, default=0.0)
    priority = db.Column(db.Enum(Priority), default=Priority.MEDIUM)
    
    # Status
    status = db.Column(db.String(20), default='Pending')  # Pending, In Progress, Completed, Cancelled
    
    # Assigned To
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    assigned_to = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'schedule_id': self.schedule_id,
            'task_name': self.task_name,
            'task_description': self.task_description,
            'instructions': self.instructions,
            'estimated_duration_hours': self.estimated_duration_hours,
            'actual_duration_hours': self.actual_duration_hours,
            'priority': self.priority.value if self.priority else None,
            'status': self.status,
            'assigned_to_id': self.assigned_to_id,
            'company_id': self.company_id
        })
        return data

# Work Order Model
class WorkOrder(BaseModel):
    """Work Order model"""
    __tablename__ = 'work_orders'
    
    work_order_number = db.Column(db.String(50), unique=True, nullable=False)
    work_order_date = db.Column(db.DateTime, nullable=False)
    
    # Asset
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    asset = relationship("Asset", back_populates="work_orders")
    
    # Assigned Team
    assigned_team_id = db.Column(db.Integer, db.ForeignKey('maintenance_teams.id'))
    assigned_team = relationship("MaintenanceTeam", back_populates="work_orders")
    
    # Work Order Details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    
    # Priority and Status
    priority = db.Column(db.Enum(Priority), default=Priority.MEDIUM)
    status = db.Column(db.Enum(WorkOrderStatus), default=WorkOrderStatus.DRAFT)
    
    # Scheduling
    scheduled_start_date = db.Column(db.DateTime)
    scheduled_end_date = db.Column(db.DateTime)
    actual_start_date = db.Column(db.DateTime)
    actual_end_date = db.Column(db.DateTime)
    
    # Cost Information
    estimated_cost = db.Column(db.Float, default=0.0)
    actual_cost = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Additional Information
    notes = db.Column(db.Text)
    completion_notes = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'work_order_number': self.work_order_number,
            'work_order_date': self.work_order_date.isoformat() if self.work_order_date else None,
            'asset_id': self.asset_id,
            'assigned_team_id': self.assigned_team_id,
            'title': self.title,
            'description': self.description,
            'instructions': self.instructions,
            'priority': self.priority.value if self.priority else None,
            'status': self.status.value if self.status else None,
            'scheduled_start_date': self.scheduled_start_date.isoformat() if self.scheduled_start_date else None,
            'scheduled_end_date': self.scheduled_end_date.isoformat() if self.scheduled_end_date else None,
            'actual_start_date': self.actual_start_date.isoformat() if self.actual_start_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'estimated_cost': self.estimated_cost,
            'actual_cost': self.actual_cost,
            'currency': self.currency,
            'notes': self.notes,
            'completion_notes': self.completion_notes,
            'company_id': self.company_id
        })
        return data

# Spare Part Model
class SparePart(BaseModel):
    """Spare Part model"""
    __tablename__ = 'spare_parts'
    
    part_name = db.Column(db.String(200), nullable=False)
    part_number = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Part Details
    manufacturer = db.Column(db.String(200))
    model_number = db.Column(db.String(100))
    category = db.Column(db.String(100))
    
    # Inventory Information
    current_stock = db.Column(db.Float, default=0.0)
    minimum_stock_level = db.Column(db.Float, default=0.0)
    maximum_stock_level = db.Column(db.Float, default=0.0)
    reorder_level = db.Column(db.Float, default=0.0)
    
    # Pricing
    unit_cost = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Supplier Information
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    supplier = relationship("Supplier")
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_critical = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'part_name': self.part_name,
            'part_number': self.part_number,
            'description': self.description,
            'manufacturer': self.manufacturer,
            'model_number': self.model_number,
            'category': self.category,
            'current_stock': self.current_stock,
            'minimum_stock_level': self.minimum_stock_level,
            'maximum_stock_level': self.maximum_stock_level,
            'reorder_level': self.reorder_level,
            'unit_cost': self.unit_cost,
            'currency': self.currency,
            'supplier_id': self.supplier_id,
            'is_active': self.is_active,
            'is_critical': self.is_critical,
            'company_id': self.company_id
        })
        return data
