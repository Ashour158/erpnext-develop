# Quality Management Models
# Complete quality control, inspection management, and compliance tracking

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

class InspectionStatus(enum.Enum):
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"

class InspectionType(enum.Enum):
    INCOMING = "Incoming"
    IN_PROCESS = "In Process"
    FINAL = "Final"
    FIRST_ARTICLE = "First Article"
    RANDOM = "Random"
    CUSTOMER = "Customer"

class NonConformanceStatus(enum.Enum):
    OPEN = "Open"
    INVESTIGATING = "Investigating"
    ROOT_CAUSE_ANALYSIS = "Root Cause Analysis"
    CORRECTIVE_ACTION = "Corrective Action"
    VERIFICATION = "Verification"
    CLOSED = "Closed"

class CAPAStatus(enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    IMPLEMENTED = "Implemented"
    VERIFIED = "Verified"
    CLOSED = "Closed"

class AuditStatus(enum.Enum):
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FOLLOW_UP = "Follow Up"
    CLOSED = "Closed"

# Quality Control Models
class QualityInspection(BaseModel):
    """Quality inspection model"""
    __tablename__ = 'quality_inspections'
    
    # Inspection Information
    inspection_number = db.Column(db.String(50), unique=True, nullable=False)
    inspection_name = db.Column(db.String(200), nullable=False)
    inspection_description = db.Column(db.Text)
    inspection_type = db.Column(db.Enum(InspectionType), nullable=False)
    
    # Inspection Details
    inspection_date = db.Column(db.Date, default=date.today)
    scheduled_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    status = db.Column(db.Enum(InspectionStatus), default=InspectionStatus.SCHEDULED)
    
    # Inspector Information
    inspector_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    inspector = relationship("Employee")
    
    # Inspection Criteria
    inspection_criteria = db.Column(db.JSON)  # Inspection criteria and specifications
    acceptance_criteria = db.Column(db.JSON)  # Acceptance criteria
    sampling_plan = db.Column(db.JSON)  # Sampling plan details
    
    # Inspection Results
    total_quantity = db.Column(db.Integer, default=0)
    inspected_quantity = db.Column(db.Integer, default=0)
    passed_quantity = db.Column(db.Integer, default=0)
    failed_quantity = db.Column(db.Integer, default=0)
    pass_rate = db.Column(db.Float, default=0.0)
    
    # Inspection Findings
    findings = db.Column(db.JSON)  # Detailed inspection findings
    defects_found = db.Column(db.JSON)  # List of defects found
    recommendations = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    inspection_items = relationship("InspectionItem", back_populates="inspection")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'inspection_number': self.inspection_number,
            'inspection_name': self.inspection_name,
            'inspection_description': self.inspection_description,
            'inspection_type': self.inspection_type.value if self.inspection_type else None,
            'inspection_date': self.inspection_date.isoformat() if self.inspection_date else None,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'status': self.status.value if self.status else None,
            'inspector_id': self.inspector_id,
            'inspection_criteria': self.inspection_criteria,
            'acceptance_criteria': self.acceptance_criteria,
            'sampling_plan': self.sampling_plan,
            'total_quantity': self.total_quantity,
            'inspected_quantity': self.inspected_quantity,
            'passed_quantity': self.passed_quantity,
            'failed_quantity': self.failed_quantity,
            'pass_rate': self.pass_rate,
            'findings': self.findings,
            'defects_found': self.defects_found,
            'recommendations': self.recommendations,
            'company_id': self.company_id
        })
        return data

class InspectionItem(BaseModel):
    """Inspection item model"""
    __tablename__ = 'inspection_items'
    
    # Item Information
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item = relationship("Item")
    
    # Inspection Association
    inspection_id = db.Column(db.Integer, db.ForeignKey('quality_inspections.id'), nullable=False)
    inspection = relationship("QualityInspection", back_populates="inspection_items")
    
    # Item Details
    batch_number = db.Column(db.String(100))
    lot_number = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    quantity = db.Column(db.Integer, default=1)
    
    # Inspection Results
    is_conforming = db.Column(db.Boolean, default=True)
    defect_count = db.Column(db.Integer, default=0)
    defect_types = db.Column(db.JSON)  # Types of defects found
    measurements = db.Column(db.JSON)  # Measurement results
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'item_id': self.item_id,
            'inspection_id': self.inspection_id,
            'batch_number': self.batch_number,
            'lot_number': self.lot_number,
            'serial_number': self.serial_number,
            'quantity': self.quantity,
            'is_conforming': self.is_conforming,
            'defect_count': self.defect_count,
            'defect_types': self.defect_types,
            'measurements': self.measurements,
            'company_id': self.company_id
        })
        return data

# Non-Conformance Management
class NonConformance(BaseModel):
    """Non-conformance model"""
    __tablename__ = 'non_conformances'
    
    # Non-Conformance Information
    nc_number = db.Column(db.String(50), unique=True, nullable=False)
    nc_title = db.Column(db.String(200), nullable=False)
    nc_description = db.Column(db.Text, nullable=False)
    
    # Non-Conformance Details
    nc_date = db.Column(db.Date, default=date.today)
    discovered_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    discovered_by = relationship("Employee")
    
    # Classification
    nc_type = db.Column(db.String(100))  # Product, Process, System, etc.
    severity = db.Column(db.String(50), default='Medium')  # Low, Medium, High, Critical
    status = db.Column(db.Enum(NonConformanceStatus), default=NonConformanceStatus.OPEN)
    
    # Impact Assessment
    affected_products = db.Column(db.JSON)  # List of affected products
    affected_processes = db.Column(db.JSON)  # List of affected processes
    customer_impact = db.Column(db.Text)
    financial_impact = db.Column(db.Float, default=0.0)
    
    # Root Cause Analysis
    root_cause = db.Column(db.Text)
    root_cause_analysis_date = db.Column(db.Date)
    root_cause_analyst_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    root_cause_analyst = relationship("Employee", foreign_keys=[root_cause_analyst_id])
    
    # Corrective Actions
    corrective_actions = db.Column(db.JSON)  # List of corrective actions
    preventive_actions = db.Column(db.JSON)  # List of preventive actions
    action_owner_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    action_owner = relationship("Employee", foreign_keys=[action_owner_id])
    
    # Verification
    verification_date = db.Column(db.Date)
    verification_method = db.Column(db.Text)
    verification_results = db.Column(db.Text)
    verified_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    verified_by = relationship("Employee", foreign_keys=[verified_by_id])
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    nc_attachments = relationship("NCAttachment", back_populates="non_conformance")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'nc_number': self.nc_number,
            'nc_title': self.nc_title,
            'nc_description': self.nc_description,
            'nc_date': self.nc_date.isoformat() if self.nc_date else None,
            'discovered_by_id': self.discovered_by_id,
            'nc_type': self.nc_type,
            'severity': self.severity,
            'status': self.status.value if self.status else None,
            'affected_products': self.affected_products,
            'affected_processes': self.affected_processes,
            'customer_impact': self.customer_impact,
            'financial_impact': self.financial_impact,
            'root_cause': self.root_cause,
            'root_cause_analysis_date': self.root_cause_analysis_date.isoformat() if self.root_cause_analysis_date else None,
            'root_cause_analyst_id': self.root_cause_analyst_id,
            'corrective_actions': self.corrective_actions,
            'preventive_actions': self.preventive_actions,
            'action_owner_id': self.action_owner_id,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'verification_method': self.verification_method,
            'verification_results': self.verification_results,
            'verified_by_id': self.verified_by_id,
            'company_id': self.company_id
        })
        return data

class NCAttachment(BaseModel):
    """Non-conformance attachment model"""
    __tablename__ = 'nc_attachments'
    
    # Attachment Information
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(100))
    file_size = db.Column(db.Integer, default=0)
    
    # Non-Conformance Association
    nc_id = db.Column(db.Integer, db.ForeignKey('non_conformances.id'), nullable=False)
    non_conformance = relationship("NonConformance", back_populates="nc_attachments")
    
    # Attachment Details
    attachment_type = db.Column(db.String(100))  # Photo, Document, Report, etc.
    description = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'nc_id': self.nc_id,
            'attachment_type': self.attachment_type,
            'description': self.description,
            'company_id': self.company_id
        })
        return data

# CAPA Management
class CAPA(BaseModel):
    """Corrective and Preventive Action model"""
    __tablename__ = 'capas'
    
    # CAPA Information
    capa_number = db.Column(db.String(50), unique=True, nullable=False)
    capa_title = db.Column(db.String(200), nullable=False)
    capa_description = db.Column(db.Text, nullable=False)
    
    # CAPA Details
    capa_date = db.Column(db.Date, default=date.today)
    capa_type = db.Column(db.String(50), default='Corrective')  # Corrective, Preventive
    status = db.Column(db.Enum(CAPAStatus), default=CAPAStatus.OPEN)
    
    # Related Issues
    related_nc_id = db.Column(db.Integer, db.ForeignKey('non_conformances.id'))
    related_nc = relationship("NonConformance")
    
    # CAPA Team
    capa_owner_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    capa_owner = relationship("Employee")
    
    # Problem Description
    problem_description = db.Column(db.Text, nullable=False)
    problem_scope = db.Column(db.Text)
    affected_areas = db.Column(db.JSON)  # List of affected areas
    
    # Root Cause Analysis
    root_cause_analysis = db.Column(db.Text)
    root_cause_method = db.Column(db.String(100))  # 5-Why, Fishbone, etc.
    root_cause_analyst_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    root_cause_analyst = relationship("Employee", foreign_keys=[root_cause_analyst_id])
    
    # Action Plan
    action_plan = db.Column(db.JSON)  # Detailed action plan
    action_items = db.Column(db.JSON)  # List of action items
    responsible_persons = db.Column(db.JSON)  # List of responsible persons
    target_dates = db.Column(db.JSON)  # Target completion dates
    
    # Implementation
    implementation_status = db.Column(db.Text)
    implementation_date = db.Column(db.Date)
    implementation_notes = db.Column(db.Text)
    
    # Verification
    verification_method = db.Column(db.Text)
    verification_date = db.Column(db.Date)
    verification_results = db.Column(db.Text)
    verified_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    verified_by = relationship("Employee", foreign_keys=[verified_by_id])
    
    # Effectiveness Review
    effectiveness_review_date = db.Column(db.Date)
    effectiveness_review_results = db.Column(db.Text)
    effectiveness_reviewer_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    effectiveness_reviewer = relationship("Employee", foreign_keys=[effectiveness_reviewer_id])
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'capa_number': self.capa_number,
            'capa_title': self.capa_title,
            'capa_description': self.capa_description,
            'capa_date': self.capa_date.isoformat() if self.capa_date else None,
            'capa_type': self.capa_type,
            'status': self.status.value if self.status else None,
            'related_nc_id': self.related_nc_id,
            'capa_owner_id': self.capa_owner_id,
            'problem_description': self.problem_description,
            'problem_scope': self.problem_scope,
            'affected_areas': self.affected_areas,
            'root_cause_analysis': self.root_cause_analysis,
            'root_cause_method': self.root_cause_method,
            'root_cause_analyst_id': self.root_cause_analyst_id,
            'action_plan': self.action_plan,
            'action_items': self.action_items,
            'responsible_persons': self.responsible_persons,
            'target_dates': self.target_dates,
            'implementation_status': self.implementation_status,
            'implementation_date': self.implementation_date.isoformat() if self.implementation_date else None,
            'implementation_notes': self.implementation_notes,
            'verification_method': self.verification_method,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'verification_results': self.verification_results,
            'verified_by_id': self.verified_by_id,
            'effectiveness_review_date': self.effectiveness_review_date.isoformat() if self.effectiveness_review_date else None,
            'effectiveness_review_results': self.effectiveness_review_results,
            'effectiveness_reviewer_id': self.effectiveness_reviewer_id,
            'company_id': self.company_id
        })
        return data

# Audit Management
class QualityAudit(BaseModel):
    """Quality audit model"""
    __tablename__ = 'quality_audits'
    
    # Audit Information
    audit_number = db.Column(db.String(50), unique=True, nullable=False)
    audit_title = db.Column(db.String(200), nullable=False)
    audit_description = db.Column(db.Text)
    
    # Audit Details
    audit_type = db.Column(db.String(100), nullable=False)  # Internal, External, Customer, Regulatory
    audit_scope = db.Column(db.Text, nullable=False)
    audit_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(AuditStatus), default=AuditStatus.PLANNED)
    
    # Audit Team
    lead_auditor_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    lead_auditor = relationship("Employee")
    audit_team = db.Column(db.JSON)  # List of audit team members
    
    # Audit Scope
    audited_areas = db.Column(db.JSON)  # List of audited areas
    audit_criteria = db.Column(db.JSON)  # Audit criteria and standards
    audit_objectives = db.Column(db.Text)
    
    # Audit Results
    audit_findings = db.Column(db.JSON)  # List of audit findings
    non_conformities = db.Column(db.JSON)  # List of non-conformities
    observations = db.Column(db.JSON)  # List of observations
    opportunities_for_improvement = db.Column(db.JSON)  # List of OFIs
    
    # Audit Report
    audit_report = db.Column(db.Text)
    audit_conclusion = db.Column(db.Text)
    audit_recommendations = db.Column(db.Text)
    
    # Follow-up
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date)
    follow_up_status = db.Column(db.String(50))
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'audit_number': self.audit_number,
            'audit_title': self.audit_title,
            'audit_description': self.audit_description,
            'audit_type': self.audit_type,
            'audit_scope': self.audit_scope,
            'audit_date': self.audit_date.isoformat() if self.audit_date else None,
            'status': self.status.value if self.status else None,
            'lead_auditor_id': self.lead_auditor_id,
            'audit_team': self.audit_team,
            'audited_areas': self.audited_areas,
            'audit_criteria': self.audit_criteria,
            'audit_objectives': self.audit_objectives,
            'audit_findings': self.audit_findings,
            'non_conformities': self.non_conformities,
            'observations': self.observations,
            'opportunities_for_improvement': self.opportunities_for_improvement,
            'audit_report': self.audit_report,
            'audit_conclusion': self.audit_conclusion,
            'audit_recommendations': self.audit_recommendations,
            'follow_up_required': self.follow_up_required,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'follow_up_status': self.follow_up_status,
            'company_id': self.company_id
        })
        return data

# Quality Metrics
class QualityMetric(BaseModel):
    """Quality metric model"""
    __tablename__ = 'quality_metrics'
    
    # Metric Information
    metric_name = db.Column(db.String(200), nullable=False)
    metric_description = db.Column(db.Text)
    metric_type = db.Column(db.String(100), nullable=False)  # KPI, KRI, etc.
    
    # Metric Details
    measurement_period = db.Column(db.String(50), default='Monthly')  # Daily, Weekly, Monthly, Quarterly, Annual
    target_value = db.Column(db.Float, default=0.0)
    actual_value = db.Column(db.Float, default=0.0)
    unit_of_measure = db.Column(db.String(50))
    
    # Metric Calculation
    calculation_method = db.Column(db.Text)
    data_sources = db.Column(db.JSON)  # List of data sources
    calculation_formula = db.Column(db.Text)
    
    # Metric Status
    is_active = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'metric_name': self.metric_name,
            'metric_description': self.metric_description,
            'metric_type': self.metric_type,
            'measurement_period': self.measurement_period,
            'target_value': self.target_value,
            'actual_value': self.actual_value,
            'unit_of_measure': self.unit_of_measure,
            'calculation_method': self.calculation_method,
            'data_sources': self.data_sources,
            'calculation_formula': self.calculation_formula,
            'is_active': self.is_active,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'company_id': self.company_id
        })
        return data
