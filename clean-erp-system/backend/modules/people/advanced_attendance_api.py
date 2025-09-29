# Advanced Attendance API
# API endpoints for enhanced attendance management with geolocation and policies

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from .advanced_attendance import (
    AttendancePolicy, WorkShift, EmployeeShift, AttendanceRecord,
    AttendanceCheckInOut, AttendanceException,
    AttendanceStatus, CheckInOutType, WorkShiftType,
    calculate_working_hours, calculate_overtime_hours,
    validate_attendance_location, create_attendance_record,
    check_in_employee, check_out_employee
)
from datetime import datetime, date, time
import json

advanced_attendance_bp = Blueprint('advanced_attendance', __name__)

# Attendance Policies
@advanced_attendance_bp.route('/policies', methods=['GET'])
@jwt_required()
def get_attendance_policies():
    """Get attendance policies"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        policies = AttendancePolicy.query.filter(
            AttendancePolicy.company_id == company_id,
            AttendancePolicy.is_active == True
        ).all()
        
        return jsonify([policy.to_dict() for policy in policies])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_attendance_bp.route('/policies', methods=['POST'])
@jwt_required()
def create_attendance_policy():
    """Create attendance policy"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['policy_name', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create policy
        policy = AttendancePolicy(
            policy_name=data['policy_name'],
            policy_description=data.get('policy_description'),
            working_hours_per_day=data.get('working_hours_per_day', 8.0),
            working_days_per_week=data.get('working_days_per_week', 5),
            working_days_per_month=data.get('working_days_per_month', 22),
            late_arrival_tolerance=data.get('late_arrival_tolerance', 15),
            late_arrival_penalty=data.get('late_arrival_penalty', 0.0),
            max_late_arrivals=data.get('max_late_arrivals', 3),
            early_departure_tolerance=data.get('early_departure_tolerance', 15),
            early_departure_penalty=data.get('early_departure_penalty', 0.0),
            max_early_departures=data.get('max_early_departures', 3),
            break_duration=data.get('break_duration', 60),
            break_times=data.get('break_times'),
            overtime_threshold=data.get('overtime_threshold', 8.0),
            overtime_rate=data.get('overtime_rate', 1.5),
            max_overtime_per_day=data.get('max_overtime_per_day', 4.0),
            geolocation_required=data.get('geolocation_required', False),
            allowed_locations=data.get('allowed_locations'),
            restricted_locations=data.get('restricted_locations'),
            location_radius=data.get('location_radius', 100.0),
            company_id=data['company_id']
        )
        
        db.session.add(policy)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('attendance_policy_created', policy.to_dict(), data['company_id'])
        
        return jsonify(policy.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_attendance_bp.route('/policies/<int:policy_id>', methods=['GET'])
@jwt_required()
def get_attendance_policy(policy_id):
    """Get specific attendance policy"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        policy = AttendancePolicy.query.filter(
            AttendancePolicy.id == policy_id,
            AttendancePolicy.company_id == company_id
        ).first()
        
        if not policy:
            return jsonify({'error': 'Policy not found'}), 404
        
        return jsonify(policy.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_attendance_bp.route('/policies/<int:policy_id>', methods=['PUT'])
@jwt_required()
def update_attendance_policy(policy_id):
    """Update attendance policy"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        policy = AttendancePolicy.query.filter(
            AttendancePolicy.id == policy_id,
            AttendancePolicy.company_id == data.get('company_id')
        ).first()
        
        if not policy:
            return jsonify({'error': 'Policy not found'}), 404
        
        # Update fields
        for field in ['policy_name', 'policy_description', 'is_active', 'working_hours_per_day',
                     'working_days_per_week', 'working_days_per_month', 'late_arrival_tolerance',
                     'late_arrival_penalty', 'max_late_arrivals', 'early_departure_tolerance',
                     'early_departure_penalty', 'max_early_departures', 'break_duration',
                     'break_times', 'overtime_threshold', 'overtime_rate', 'max_overtime_per_day',
                     'geolocation_required', 'allowed_locations', 'restricted_locations', 'location_radius']:
            if field in data:
                setattr(policy, field, data[field])
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('attendance_policy_updated', policy.to_dict(), policy.company_id)
        
        return jsonify(policy.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Work Shifts
@advanced_attendance_bp.route('/shifts', methods=['GET'])
@jwt_required()
def get_work_shifts():
    """Get work shifts"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        shifts = WorkShift.query.filter(
            WorkShift.company_id == company_id,
            WorkShift.is_active == True
        ).all()
        
        return jsonify([shift.to_dict() for shift in shifts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_attendance_bp.route('/shifts', methods=['POST'])
@jwt_required()
def create_work_shift():
    """Create work shift"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['shift_name', 'start_time', 'end_time', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create shift
        shift = WorkShift(
            shift_name=data['shift_name'],
            shift_description=data.get('shift_description'),
            shift_type=WorkShiftType(data.get('shift_type', 'REGULAR')),
            start_time=time.fromisoformat(data['start_time']),
            end_time=time.fromisoformat(data['end_time']),
            break_start_time=time.fromisoformat(data['break_start_time']) if data.get('break_start_time') else None,
            break_end_time=time.fromisoformat(data['break_end_time']) if data.get('break_end_time') else None,
            working_days=data.get('working_days'),
            is_rotating=data.get('is_rotating', False),
            rotation_pattern=data.get('rotation_pattern'),
            grace_period=data.get('grace_period', 15),
            overtime_threshold=data.get('overtime_threshold', 8.0),
            max_employees=data.get('max_employees', 0),
            company_id=data['company_id']
        )
        
        db.session.add(shift)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('work_shift_created', shift.to_dict(), data['company_id'])
        
        return jsonify(shift.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_attendance_bp.route('/shifts/<int:shift_id>', methods=['GET'])
@jwt_required()
def get_work_shift(shift_id):
    """Get specific work shift"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        shift = WorkShift.query.filter(
            WorkShift.id == shift_id,
            WorkShift.company_id == company_id
        ).first()
        
        if not shift:
            return jsonify({'error': 'Shift not found'}), 404
        
        return jsonify(shift.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_attendance_bp.route('/shifts/<int:shift_id>', methods=['PUT'])
@jwt_required()
def update_work_shift(shift_id):
    """Update work shift"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        shift = WorkShift.query.filter(
            WorkShift.id == shift_id,
            WorkShift.company_id == data.get('company_id')
        ).first()
        
        if not shift:
            return jsonify({'error': 'Shift not found'}), 404
        
        # Update fields
        for field in ['shift_name', 'shift_description', 'is_active', 'working_days',
                     'is_rotating', 'rotation_pattern', 'grace_period', 'overtime_threshold',
                     'max_employees']:
            if field in data:
                setattr(shift, field, data[field])
        
        if 'shift_type' in data:
            shift.shift_type = WorkShiftType(data['shift_type'])
        
        if 'start_time' in data:
            shift.start_time = time.fromisoformat(data['start_time'])
        
        if 'end_time' in data:
            shift.end_time = time.fromisoformat(data['end_time'])
        
        if 'break_start_time' in data and data['break_start_time']:
            shift.break_start_time = time.fromisoformat(data['break_start_time'])
        
        if 'break_end_time' in data and data['break_end_time']:
            shift.break_end_time = time.fromisoformat(data['break_end_time'])
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('work_shift_updated', shift.to_dict(), shift.company_id)
        
        return jsonify(shift.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Employee Shifts
@advanced_attendance_bp.route('/employee-shifts', methods=['GET'])
@jwt_required()
def get_employee_shifts():
    """Get employee shifts"""
    try:
        company_id = request.args.get('company_id', type=int)
        employee_id = request.args.get('employee_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = EmployeeShift.query.filter(EmployeeShift.company_id == company_id)
        
        if employee_id:
            query = query.filter(EmployeeShift.employee_id == employee_id)
        
        shifts = query.all()
        
        return jsonify([shift.to_dict() for shift in shifts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_attendance_bp.route('/employee-shifts', methods=['POST'])
@jwt_required()
def assign_employee_shift():
    """Assign employee to shift"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['employee_id', 'shift_id', 'start_date', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create employee shift
        employee_shift = EmployeeShift(
            employee_id=data['employee_id'],
            shift_id=data['shift_id'],
            start_date=date.fromisoformat(data['start_date']),
            end_date=date.fromisoformat(data['end_date']) if data.get('end_date') else None,
            company_id=data['company_id']
        )
        
        db.session.add(employee_shift)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('employee_shift_assigned', employee_shift.to_dict(), data['company_id'])
        
        return jsonify(employee_shift.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Attendance Records
@advanced_attendance_bp.route('/records', methods=['GET'])
@jwt_required()
def get_attendance_records():
    """Get attendance records"""
    try:
        company_id = request.args.get('company_id', type=int)
        employee_id = request.args.get('employee_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = AttendanceRecord.query.filter(AttendanceRecord.company_id == company_id)
        
        if employee_id:
            query = query.filter(AttendanceRecord.employee_id == employee_id)
        
        if start_date:
            query = query.filter(AttendanceRecord.attendance_date >= date.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(AttendanceRecord.attendance_date <= date.fromisoformat(end_date))
        
        records = query.all()
        
        return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_attendance_bp.route('/records/<int:record_id>', methods=['GET'])
@jwt_required()
def get_attendance_record(record_id):
    """Get specific attendance record"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        record = AttendanceRecord.query.filter(
            AttendanceRecord.id == record_id,
            AttendanceRecord.company_id == company_id
        ).first()
        
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        return jsonify(record.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Check In/Out
@advanced_attendance_bp.route('/check-in', methods=['POST'])
@jwt_required()
def check_in():
    """Check in employee with geolocation"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['employee_id', 'latitude', 'longitude', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check in employee
        record, message = check_in_employee(
            employee_id=data['employee_id'],
            check_in_time=datetime.fromisoformat(data['check_in_time']) if data.get('check_in_time') else datetime.utcnow(),
            latitude=data['latitude'],
            longitude=data['longitude'],
            company_id=data['company_id'],
            accuracy=data.get('accuracy', 0.0),
            address=data.get('address')
        )
        
        if not record:
            return jsonify({'error': message}), 400
        
        # Emit real-time update
        emit_realtime_update('employee_checked_in', record.to_dict(), data['company_id'])
        
        return jsonify(record.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_attendance_bp.route('/check-out', methods=['POST'])
@jwt_required()
def check_out():
    """Check out employee with geolocation"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['employee_id', 'latitude', 'longitude', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check out employee
        record, message = check_out_employee(
            employee_id=data['employee_id'],
            check_out_time=datetime.fromisoformat(data['check_out_time']) if data.get('check_out_time') else datetime.utcnow(),
            latitude=data['latitude'],
            longitude=data['longitude'],
            company_id=data['company_id'],
            accuracy=data.get('accuracy', 0.0),
            address=data.get('address')
        )
        
        if not record:
            return jsonify({'error': message}), 400
        
        # Emit real-time update
        emit_realtime_update('employee_checked_out', record.to_dict(), data['company_id'])
        
        return jsonify(record.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Attendance Exceptions
@advanced_attendance_bp.route('/exceptions', methods=['GET'])
@jwt_required()
def get_attendance_exceptions():
    """Get attendance exceptions"""
    try:
        company_id = request.args.get('company_id', type=int)
        employee_id = request.args.get('employee_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = AttendanceException.query.filter(AttendanceException.company_id == company_id)
        
        if employee_id:
            query = query.filter(AttendanceException.employee_id == employee_id)
        
        exceptions = query.all()
        
        return jsonify([exception.to_dict() for exception in exceptions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@advanced_attendance_bp.route('/exceptions', methods=['POST'])
@jwt_required()
def create_attendance_exception():
    """Create attendance exception"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['exception_type', 'exception_reason', 'exception_date', 'employee_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create exception
        exception = AttendanceException(
            exception_type=data['exception_type'],
            exception_reason=data['exception_reason'],
            exception_date=date.fromisoformat(data['exception_date']),
            employee_id=data['employee_id'],
            company_id=data['company_id']
        )
        
        db.session.add(exception)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('attendance_exception_created', exception.to_dict(), data['company_id'])
        
        return jsonify(exception.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@advanced_attendance_bp.route('/exceptions/<int:exception_id>/approve', methods=['POST'])
@jwt_required()
def approve_attendance_exception(exception_id):
    """Approve attendance exception"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        exception = AttendanceException.query.filter(
            AttendanceException.id == exception_id,
            AttendanceException.company_id == data.get('company_id')
        ).first()
        
        if not exception:
            return jsonify({'error': 'Exception not found'}), 404
        
        # Update approval
        exception.approved_by = user_id
        exception.approval_date = datetime.utcnow()
        exception.approval_notes = data.get('approval_notes')
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('attendance_exception_approved', exception.to_dict(), exception.company_id)
        
        return jsonify(exception.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Analytics
@advanced_attendance_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_attendance_analytics():
    """Get attendance analytics"""
    try:
        company_id = request.args.get('company_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        # Parse dates
        start_date = date.fromisoformat(start_date) if start_date else None
        end_date = date.fromisoformat(end_date) if end_date else None
        
        # Get attendance records
        query = AttendanceRecord.query.filter(AttendanceRecord.company_id == company_id)
        
        if start_date:
            query = query.filter(AttendanceRecord.attendance_date >= start_date)
        
        if end_date:
            query = query.filter(AttendanceRecord.attendance_date <= end_date)
        
        records = query.all()
        
        # Calculate analytics
        total_records = len(records)
        present_count = len([r for r in records if r.attendance_status == AttendanceStatus.PRESENT])
        absent_count = len([r for r in records if r.attendance_status == AttendanceStatus.ABSENT])
        late_count = len([r for r in records if r.attendance_status == AttendanceStatus.LATE])
        
        total_hours = sum(r.total_hours for r in records if r.total_hours)
        total_overtime = sum(r.overtime_hours for r in records if r.overtime_hours)
        
        analytics = {
            'total_records': total_records,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'attendance_rate': (present_count / total_records * 100) if total_records > 0 else 0,
            'total_hours': total_hours,
            'total_overtime': total_overtime,
            'date_range': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }
        }
        
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
