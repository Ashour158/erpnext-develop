# People Models - Complete Human Resources Management
# Advanced HR models without Frappe dependencies

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

# Enums
class Gender(enum.Enum):
    MALE = "Male"
    FEMALE = "Other"
    OTHER = "Other"

class MaritalStatus(enum.Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"

class EmploymentStatus(enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    TERMINATED = "Terminated"
    ON_LEAVE = "On Leave"

class LeaveStatus(enum.Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"

class AttendanceStatus(enum.Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    HALF_DAY = "Half Day"
    ON_LEAVE = "On Leave"

# Employee Model
class Employee(BaseModel):
    """Employee model"""
    __tablename__ = 'employees'
    
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    
    # Personal Information
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum(Gender))
    marital_status = db.Column(db.Enum(MaritalStatus))
    nationality = db.Column(db.String(100))
    
    # Contact Information
    personal_email = db.Column(db.String(120))
    work_email = db.Column(db.String(120))
    personal_phone = db.Column(db.String(20))
    work_phone = db.Column(db.String(20))
    
    # Address
    address_line_1 = db.Column(db.String(200))
    address_line_2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Employment Information
    employee_type = db.Column(db.String(50))  # Full-time, Part-time, Contract, etc.
    employment_status = db.Column(db.Enum(EmploymentStatus), default=EmploymentStatus.ACTIVE)
    date_of_joining = db.Column(db.Date)
    date_of_leaving = db.Column(db.Date)
    
    # Department and Designation
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    department = relationship("Department", back_populates="employees")
    designation_id = db.Column(db.Integer, db.ForeignKey('designations.id'))
    designation = relationship("Designation", back_populates="employees")
    
    # Manager
    reports_to_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    reports_to = relationship("Employee", remote_side=[id])
    subordinates = relationship("Employee", back_populates="reports_to")
    
    # Salary Information
    basic_salary = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(200))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relationship = db.Column(db.String(100))
    
    # Additional Information
    profile_picture = db.Column(db.String(255))
    bio = db.Column(db.Text)
    skills = db.Column(db.JSON)
    certifications = db.Column(db.JSON)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    leave_requests = relationship("LeaveRequest", back_populates="employee")
    attendance_records = relationship("Attendance", back_populates="employee")
    payroll_records = relationship("Payroll", back_populates="employee")
    performance_records = relationship("Performance", back_populates="employee")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'middle_name': self.middle_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender.value if self.gender else None,
            'marital_status': self.marital_status.value if self.marital_status else None,
            'nationality': self.nationality,
            'personal_email': self.personal_email,
            'work_email': self.work_email,
            'personal_phone': self.personal_phone,
            'work_phone': self.work_phone,
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'employee_type': self.employee_type,
            'employment_status': self.employment_status.value if self.employment_status else None,
            'date_of_joining': self.date_of_joining.isoformat() if self.date_of_joining else None,
            'date_of_leaving': self.date_of_leaving.isoformat() if self.date_of_leaving else None,
            'department_id': self.department_id,
            'designation_id': self.designation_id,
            'reports_to_id': self.reports_to_id,
            'basic_salary': self.basic_salary,
            'currency': self.currency,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'emergency_contact_relationship': self.emergency_contact_relationship,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'skills': self.skills,
            'certifications': self.certifications,
            'company_id': self.company_id
        })
        return data

# Department Model
class Department(BaseModel):
    """Department model"""
    __tablename__ = 'departments'
    
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Department Hierarchy
    parent_department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    parent_department = relationship("Department", remote_side=[id])
    child_departments = relationship("Department", back_populates="parent_department")
    
    # Department Head
    department_head_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    department_head = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    employees = relationship("Employee", back_populates="department")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'parent_department_id': self.parent_department_id,
            'department_head_id': self.department_head_id,
            'company_id': self.company_id
        })
        return data

# Designation Model
class Designation(BaseModel):
    """Designation model"""
    __tablename__ = 'designations'
    
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Salary Information
    min_salary = db.Column(db.Float, default=0.0)
    max_salary = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    employees = relationship("Employee", back_populates="designation")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'min_salary': self.min_salary,
            'max_salary': self.max_salary,
            'currency': self.currency,
            'company_id': self.company_id
        })
        return data

# Leave Type Model
class LeaveType(BaseModel):
    """Leave Type model"""
    __tablename__ = 'leave_types'
    
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Leave Settings
    max_days_per_year = db.Column(db.Integer, default=0)
    max_consecutive_days = db.Column(db.Integer, default=0)
    requires_approval = db.Column(db.Boolean, default=True)
    is_paid = db.Column(db.Boolean, default=True)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    leave_requests = relationship("LeaveRequest", back_populates="leave_type")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'max_days_per_year': self.max_days_per_year,
            'max_consecutive_days': self.max_consecutive_days,
            'requires_approval': self.requires_approval,
            'is_paid': self.is_paid,
            'company_id': self.company_id
        })
        return data

# Leave Request Model
class LeaveRequest(BaseModel):
    """Leave Request model"""
    __tablename__ = 'leave_requests'
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee", back_populates="leave_requests")
    
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_types.id'), nullable=False)
    leave_type = relationship("LeaveType", back_populates="leave_requests")
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Integer, nullable=False)
    
    # Request Details
    reason = db.Column(db.Text)
    status = db.Column(db.Enum(LeaveStatus), default=LeaveStatus.DRAFT)
    
    # Approval Information
    approved_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    approved_date = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'employee_id': self.employee_id,
            'leave_type_id': self.leave_type_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'total_days': self.total_days,
            'reason': self.reason,
            'status': self.status.value if self.status else None,
            'approved_by_id': self.approved_by_id,
            'approved_date': self.approved_date.isoformat() if self.approved_date else None,
            'rejection_reason': self.rejection_reason,
            'company_id': self.company_id
        })
        return data

# Attendance Model
class Attendance(BaseModel):
    """Attendance model"""
    __tablename__ = 'attendance'
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee", back_populates="attendance_records")
    
    attendance_date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    
    # Attendance Details
    status = db.Column(db.Enum(AttendanceStatus), default=AttendanceStatus.PRESENT)
    hours_worked = db.Column(db.Float, default=0.0)
    overtime_hours = db.Column(db.Float, default=0.0)
    
    # Location (for remote work tracking)
    check_in_location = db.Column(db.String(200))
    check_out_location = db.Column(db.String(200))
    
    # Notes
    notes = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'employee_id': self.employee_id,
            'attendance_date': self.attendance_date.isoformat() if self.attendance_date else None,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'status': self.status.value if self.status else None,
            'hours_worked': self.hours_worked,
            'overtime_hours': self.overtime_hours,
            'check_in_location': self.check_in_location,
            'check_out_location': self.check_out_location,
            'notes': self.notes,
            'company_id': self.company_id
        })
        return data

# Payroll Model
class Payroll(BaseModel):
    """Payroll model"""
    __tablename__ = 'payroll'
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee", back_populates="payroll_records")
    
    # Payroll Period
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    pay_date = db.Column(db.Date, nullable=False)
    
    # Salary Components
    basic_salary = db.Column(db.Float, default=0.0)
    allowances = db.Column(db.JSON)  # Housing, Transport, etc.
    deductions = db.Column(db.JSON)  # Tax, Insurance, etc.
    overtime_pay = db.Column(db.Float, default=0.0)
    bonus = db.Column(db.Float, default=0.0)
    
    # Totals
    gross_salary = db.Column(db.Float, default=0.0)
    total_deductions = db.Column(db.Float, default=0.0)
    net_salary = db.Column(db.Float, default=0.0)
    
    # Status
    status = db.Column(db.String(20), default='Draft')  # Draft, Processed, Paid
    currency = db.Column(db.String(3), default='USD')
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'employee_id': self.employee_id,
            'pay_period_start': self.pay_period_start.isoformat() if self.pay_period_start else None,
            'pay_period_end': self.pay_period_end.isoformat() if self.pay_period_end else None,
            'pay_date': self.pay_date.isoformat() if self.pay_date else None,
            'basic_salary': self.basic_salary,
            'allowances': self.allowances,
            'deductions': self.deductions,
            'overtime_pay': self.overtime_pay,
            'bonus': self.bonus,
            'gross_salary': self.gross_salary,
            'total_deductions': self.total_deductions,
            'net_salary': self.net_salary,
            'status': self.status,
            'currency': self.currency,
            'company_id': self.company_id
        })
        return data

# Performance Model
class Performance(BaseModel):
    """Performance model"""
    __tablename__ = 'performance'
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee", back_populates="performance_records")
    
    # Performance Period
    review_period_start = db.Column(db.Date, nullable=False)
    review_period_end = db.Column(db.Date, nullable=False)
    review_date = db.Column(db.Date, nullable=False)
    
    # Performance Ratings
    overall_rating = db.Column(db.Float, default=0.0)
    goals_achieved = db.Column(db.Integer, default=0)
    total_goals = db.Column(db.Integer, default=0)
    
    # Review Details
    strengths = db.Column(db.Text)
    areas_for_improvement = db.Column(db.Text)
    goals_for_next_period = db.Column(db.Text)
    reviewer_comments = db.Column(db.Text)
    
    # Reviewer
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    reviewed_by = relationship("Employee", foreign_keys=[reviewed_by_id])
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'employee_id': self.employee_id,
            'review_period_start': self.review_period_start.isoformat() if self.review_period_start else None,
            'review_period_end': self.review_period_end.isoformat() if self.review_period_end else None,
            'review_date': self.review_date.isoformat() if self.review_date else None,
            'overall_rating': self.overall_rating,
            'goals_achieved': self.goals_achieved,
            'total_goals': self.total_goals,
            'strengths': self.strengths,
            'areas_for_improvement': self.areas_for_improvement,
            'goals_for_next_period': self.goals_for_next_period,
            'reviewer_comments': self.reviewer_comments,
            'reviewed_by_id': self.reviewed_by_id,
            'company_id': self.company_id
        })
        return data

# Training Model
class Training(BaseModel):
    """Training model"""
    __tablename__ = 'training'
    
    training_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    training_type = db.Column(db.String(100))  # Internal, External, Online
    
    # Training Details
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    duration_hours = db.Column(db.Float, default=0.0)
    cost = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Trainer Information
    trainer_name = db.Column(db.String(200))
    trainer_email = db.Column(db.String(120))
    trainer_phone = db.Column(db.String(20))
    
    # Status
    status = db.Column(db.String(20), default='Planned')  # Planned, In Progress, Completed, Cancelled
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'training_name': self.training_name,
            'description': self.description,
            'training_type': self.training_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'duration_hours': self.duration_hours,
            'cost': self.cost,
            'currency': self.currency,
            'trainer_name': self.trainer_name,
            'trainer_email': self.trainer_email,
            'trainer_phone': self.trainer_phone,
            'status': self.status,
            'company_id': self.company_id
        })
        return data

# Recruitment Model
class Recruitment(BaseModel):
    """Recruitment model"""
    __tablename__ = 'recruitment'
    
    job_title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    department = relationship("Department")
    
    # Job Requirements
    required_skills = db.Column(db.JSON)
    experience_required = db.Column(db.String(100))
    education_required = db.Column(db.String(200))
    
    # Job Details
    employment_type = db.Column(db.String(50))  # Full-time, Part-time, Contract
    salary_range_min = db.Column(db.Float, default=0.0)
    salary_range_max = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Application Details
    application_deadline = db.Column(db.Date)
    status = db.Column(db.String(20), default='Open')  # Open, Closed, Filled
    
    # Hiring Manager
    hiring_manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    hiring_manager = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'job_title': self.job_title,
            'job_description': self.job_description,
            'department_id': self.department_id,
            'required_skills': self.required_skills,
            'experience_required': self.experience_required,
            'education_required': self.education_required,
            'employment_type': self.employment_type,
            'salary_range_min': self.salary_range_min,
            'salary_range_max': self.salary_range_max,
            'currency': self.currency,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'status': self.status,
            'hiring_manager_id': self.hiring_manager_id,
            'company_id': self.company_id
        })
        return data
