# Advanced Attendance Management
# Enhanced attendance with geolocation, geo-restriction, policies, and work shifts

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Time, Date
from sqlalchemy.orm import relationship
from datetime import datetime, time, date, timedelta
import enum

class AttendanceStatus(enum.Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    EARLY_LEAVE = "Early Leave"
    HALF_DAY = "Half Day"
    HOLIDAY = "Holiday"
    LEAVE = "Leave"

class CheckInOutType(enum.Enum):
    CHECK_IN = "Check In"
    CHECK_OUT = "Check Out"
    BREAK_START = "Break Start"
    BREAK_END = "Break End"
    OVERTIME_START = "Overtime Start"
    OVERTIME_END = "Overtime End"

class WorkShiftType(enum.Enum):
    REGULAR = "Regular"
    NIGHT = "Night"
    ROTATING = "Rotating"
    FLEXIBLE = "Flexible"
    CUSTOM = "Custom"

class AttendancePolicy(BaseModel):
    """Attendance policies model"""
    __tablename__ = 'attendance_policies'
    
    # Policy Information
    policy_name = db.Column(db.String(200), nullable=False)
    policy_description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Working Hours
    working_hours_per_day = db.Column(db.Float, default=8.0)  # hours
    working_days_per_week = db.Column(db.Integer, default=5)
    working_days_per_month = db.Column(db.Integer, default=22)
    
    # Late Arrival Policy
    late_arrival_tolerance = db.Column(db.Integer, default=15)  # minutes
    late_arrival_penalty = db.Column(db.Float, default=0.0)  # percentage
    max_late_arrivals = db.Column(db.Integer, default=3)  # per month
    
    # Early Departure Policy
    early_departure_tolerance = db.Column(db.Integer, default=15)  # minutes
    early_departure_penalty = db.Column(db.Float, default=0.0)  # percentage
    max_early_departures = db.Column(db.Integer, default=3)  # per month
    
    # Break Policy
    break_duration = db.Column(db.Integer, default=60)  # minutes
    break_times = db.Column(db.JSON)  # List of break times
    
    # Overtime Policy
    overtime_threshold = db.Column(db.Float, default=8.0)  # hours
    overtime_rate = db.Column(db.Float, default=1.5)  # multiplier
    max_overtime_per_day = db.Column(db.Float, default=4.0)  # hours
    
    # Geolocation Policy
    geolocation_required = db.Column(db.Boolean, default=False)
    allowed_locations = db.Column(db.JSON)  # List of allowed locations
    restricted_locations = db.Column(db.JSON)  # List of restricted locations
    location_radius = db.Column(db.Float, default=100.0)  # meters
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'policy_name': self.policy_name,
            'policy_description': self.policy_description,
            'is_active': self.is_active,
            'working_hours_per_day': self.working_hours_per_day,
            'working_days_per_week': self.working_days_per_week,
            'working_days_per_month': self.working_days_per_month,
            'late_arrival_tolerance': self.late_arrival_tolerance,
            'late_arrival_penalty': self.late_arrival_penalty,
            'max_late_arrivals': self.max_late_arrivals,
            'early_departure_tolerance': self.early_departure_tolerance,
            'early_departure_penalty': self.early_departure_penalty,
            'max_early_departures': self.max_early_departures,
            'break_duration': self.break_duration,
            'break_times': self.break_times,
            'overtime_threshold': self.overtime_threshold,
            'overtime_rate': self.overtime_rate,
            'max_overtime_per_day': self.max_overtime_per_day,
            'geolocation_required': self.geolocation_required,
            'allowed_locations': self.allowed_locations,
            'restricted_locations': self.restricted_locations,
            'location_radius': self.location_radius,
            'company_id': self.company_id
        })
        return data

class WorkShift(BaseModel):
    """Work shift model"""
    __tablename__ = 'work_shifts'
    
    # Shift Information
    shift_name = db.Column(db.String(200), nullable=False)
    shift_description = db.Column(db.Text)
    shift_type = db.Column(db.Enum(WorkShiftType), default=WorkShiftType.REGULAR)
    is_active = db.Column(db.Boolean, default=True)
    
    # Shift Timing
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    break_start_time = db.Column(db.Time)
    break_end_time = db.Column(db.Time)
    
    # Shift Days
    working_days = db.Column(db.JSON)  # Days of week (0-6)
    is_rotating = db.Column(db.Boolean, default=False)
    rotation_pattern = db.Column(db.JSON)  # Rotation pattern details
    
    # Shift Settings
    grace_period = db.Column(db.Integer, default=15)  # minutes
    overtime_threshold = db.Column(db.Float, default=8.0)  # hours
    max_employees = db.Column(db.Integer, default=0)  # 0 = unlimited
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'shift_name': self.shift_name,
            'shift_description': self.shift_description,
            'shift_type': self.shift_type.value if self.shift_type else None,
            'is_active': self.is_active,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'break_start_time': self.break_start_time.isoformat() if self.break_start_time else None,
            'break_end_time': self.break_end_time.isoformat() if self.break_end_time else None,
            'working_days': self.working_days,
            'is_rotating': self.is_rotating,
            'rotation_pattern': self.rotation_pattern,
            'grace_period': self.grace_period,
            'overtime_threshold': self.overtime_threshold,
            'max_employees': self.max_employees,
            'company_id': self.company_id
        })
        return data

class EmployeeShift(BaseModel):
    """Employee shift assignment model"""
    __tablename__ = 'employee_shifts'
    
    # Assignment Information
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    
    # Employee Information
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee")
    
    # Shift Information
    shift_id = db.Column(db.Integer, db.ForeignKey('work_shifts.id'), nullable=False)
    shift = relationship("WorkShift")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'employee_id': self.employee_id,
            'shift_id': self.shift_id,
            'company_id': self.company_id
        })
        return data

class AttendanceRecord(BaseModel):
    """Enhanced attendance record model"""
    __tablename__ = 'attendance_records'
    
    # Attendance Information
    attendance_date = db.Column(db.Date, nullable=False)
    attendance_status = db.Column(db.Enum(AttendanceStatus), default=AttendanceStatus.PRESENT)
    
    # Check In/Out Information
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    check_in_location = db.Column(db.JSON)  # Geolocation data
    check_out_location = db.Column(db.JSON)  # Geolocation data
    
    # Working Hours
    total_hours = db.Column(db.Float, default=0.0)
    overtime_hours = db.Column(db.Float, default=0.0)
    break_hours = db.Column(db.Float, default=0.0)
    
    # Employee Information
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee")
    
    # Shift Information
    shift_id = db.Column(db.Integer, db.ForeignKey('work_shifts.id'))
    shift = relationship("WorkShift")
    
    # Policy Information
    policy_id = db.Column(db.Integer, db.ForeignKey('attendance_policies.id'))
    policy = relationship("AttendancePolicy")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'attendance_date': self.attendance_date.isoformat() if self.attendance_date else None,
            'attendance_status': self.attendance_status.value if self.attendance_status else None,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'check_in_location': self.check_in_location,
            'check_out_location': self.check_out_location,
            'total_hours': self.total_hours,
            'overtime_hours': self.overtime_hours,
            'break_hours': self.break_hours,
            'employee_id': self.employee_id,
            'shift_id': self.shift_id,
            'policy_id': self.policy_id,
            'company_id': self.company_id
        })
        return data

class AttendanceCheckInOut(BaseModel):
    """Attendance check in/out model"""
    __tablename__ = 'attendance_check_in_out'
    
    # Check In/Out Information
    check_type = db.Column(db.Enum(CheckInOutType), nullable=False)
    check_time = db.Column(db.DateTime, default=datetime.utcnow)
    check_location = db.Column(db.JSON)  # Geolocation data
    
    # Employee Information
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee")
    
    # Attendance Record
    attendance_record_id = db.Column(db.Integer, db.ForeignKey('attendance_records.id'))
    attendance_record = relationship("AttendanceRecord")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'check_type': self.check_type.value if self.check_type else None,
            'check_time': self.check_time.isoformat() if self.check_time else None,
            'check_location': self.check_location,
            'employee_id': self.employee_id,
            'attendance_record_id': self.attendance_record_id,
            'company_id': self.company_id
        })
        return data

class AttendanceException(BaseModel):
    """Attendance exception model"""
    __tablename__ = 'attendance_exceptions'
    
    # Exception Information
    exception_type = db.Column(db.String(100), nullable=False)  # Late, Early, Absent, etc.
    exception_reason = db.Column(db.Text)
    exception_date = db.Column(db.Date, nullable=False)
    
    # Employee Information
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee")
    
    # Approval Information
    approved_by = db.Column(db.Integer, db.ForeignKey('employees.id'))
    approver = relationship("Employee", foreign_keys=[approved_by])
    approval_date = db.Column(db.DateTime)
    approval_notes = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'exception_type': self.exception_type,
            'exception_reason': self.exception_reason,
            'exception_date': self.exception_date.isoformat() if self.exception_date else None,
            'employee_id': self.employee_id,
            'approved_by': self.approved_by,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'approval_notes': self.approval_notes,
            'company_id': self.company_id
        })
        return data

# Utility Functions
def calculate_working_hours(check_in_time, check_out_time, break_hours=0):
    """Calculate working hours"""
    if not check_in_time or not check_out_time:
        return 0.0
    
    total_hours = (check_out_time - check_in_time).total_seconds() / 3600
    return max(0.0, total_hours - break_hours)

def calculate_overtime_hours(total_hours, overtime_threshold=8.0):
    """Calculate overtime hours"""
    return max(0.0, total_hours - overtime_threshold)

def validate_attendance_location(employee_id, latitude, longitude, company_id):
    """Validate attendance location"""
    from core.geolocation_tracking import validate_geolocation, ActivityType
    
    # Check if geolocation is required
    policy = AttendancePolicy.query.filter(
        AttendancePolicy.company_id == company_id,
        AttendancePolicy.is_active == True
    ).first()
    
    if not policy or not policy.geolocation_required:
        return True, "Geolocation not required"
    
    # Validate against allowed locations
    if policy.allowed_locations:
        for location in policy.allowed_locations:
            if abs(location['latitude'] - latitude) < 0.001 and abs(location['longitude'] - longitude) < 0.001:
                return True, "Location validated"
        return False, "Location not in allowed areas"
    
    # Validate against restricted locations
    if policy.restricted_locations:
        for location in policy.restricted_locations:
            if abs(location['latitude'] - latitude) < 0.001 and abs(location['longitude'] - longitude) < 0.001:
                return False, "Location is restricted"
    
    return True, "Location validated"

def create_attendance_record(employee_id, attendance_date, company_id, **kwargs):
    """Create attendance record"""
    # Check if record already exists
    existing_record = AttendanceRecord.query.filter(
        AttendanceRecord.employee_id == employee_id,
        AttendanceRecord.attendance_date == attendance_date,
        AttendanceRecord.company_id == company_id
    ).first()
    
    if existing_record:
        return existing_record, "Record already exists"
    
    # Get employee's current shift
    employee_shift = EmployeeShift.query.filter(
        EmployeeShift.employee_id == employee_id,
        EmployeeShift.is_active == True,
        EmployeeShift.start_date <= attendance_date,
        db.or_(
            EmployeeShift.end_date.is_(None),
            EmployeeShift.end_date >= attendance_date
        )
    ).first()
    
    # Get attendance policy
    policy = AttendancePolicy.query.filter(
        AttendancePolicy.company_id == company_id,
        AttendancePolicy.is_active == True
    ).first()
    
    # Create attendance record
    record = AttendanceRecord(
        attendance_date=attendance_date,
        employee_id=employee_id,
        shift_id=employee_shift.shift_id if employee_shift else None,
        policy_id=policy.id if policy else None,
        company_id=company_id
    )
    
    db.session.add(record)
    db.session.commit()
    
    return record, "Record created successfully"

def check_in_employee(employee_id, check_in_time, latitude, longitude, company_id, **kwargs):
    """Check in employee with geolocation"""
    # Validate location
    is_valid, message = validate_attendance_location(employee_id, latitude, longitude, company_id)
    
    if not is_valid:
        return None, message
    
    # Get or create attendance record
    attendance_date = check_in_time.date()
    record, message = create_attendance_record(employee_id, attendance_date, company_id)
    
    if not record:
        return None, message
    
    # Update check-in information
    record.check_in_time = check_in_time
    record.check_in_location = {
        'latitude': latitude,
        'longitude': longitude,
        'accuracy': kwargs.get('accuracy', 0.0),
        'address': kwargs.get('address'),
        'timestamp': check_in_time.isoformat()
    }
    
    # Create check-in record
    check_in_record = AttendanceCheckInOut(
        check_type=CheckInOutType.CHECK_IN,
        check_time=check_in_time,
        check_location=record.check_in_location,
        employee_id=employee_id,
        attendance_record_id=record.id,
        company_id=company_id
    )
    
    db.session.add(check_in_record)
    db.session.commit()
    
    return record, "Check-in successful"

def check_out_employee(employee_id, check_out_time, latitude, longitude, company_id, **kwargs):
    """Check out employee with geolocation"""
    # Validate location
    is_valid, message = validate_attendance_location(employee_id, latitude, longitude, company_id)
    
    if not is_valid:
        return None, message
    
    # Get attendance record
    attendance_date = check_out_time.date()
    record = AttendanceRecord.query.filter(
        AttendanceRecord.employee_id == employee_id,
        AttendanceRecord.attendance_date == attendance_date,
        AttendanceRecord.company_id == company_id
    ).first()
    
    if not record:
        return None, "No check-in record found"
    
    # Update check-out information
    record.check_out_time = check_out_time
    record.check_out_location = {
        'latitude': latitude,
        'longitude': longitude,
        'accuracy': kwargs.get('accuracy', 0.0),
        'address': kwargs.get('address'),
        'timestamp': check_out_time.isoformat()
    }
    
    # Calculate working hours
    if record.check_in_time:
        record.total_hours = calculate_working_hours(record.check_in_time, check_out_time)
        
        # Get overtime threshold from policy
        policy = AttendancePolicy.query.get(record.policy_id) if record.policy_id else None
        overtime_threshold = policy.overtime_threshold if policy else 8.0
        
        record.overtime_hours = calculate_overtime_hours(record.total_hours, overtime_threshold)
    
    # Create check-out record
    check_out_record = AttendanceCheckInOut(
        check_type=CheckInOutType.CHECK_OUT,
        check_time=check_out_time,
        check_location=record.check_out_location,
        employee_id=employee_id,
        attendance_record_id=record.id,
        company_id=company_id
    )
    
    db.session.add(check_out_record)
    db.session.commit()
    
    return record, "Check-out successful"
