# People API - Complete Human Resources Management API
# Advanced HR operations without Frappe dependencies

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import token_required, get_current_user
from .models import (
    Employee, Department, Designation, LeaveRequest, LeaveType,
    Attendance, Payroll, Performance, Training, Recruitment
)
from datetime import datetime, date, timedelta
import json

people_api = Blueprint('people_api', __name__)

# Employee Management
@people_api.route('/employees', methods=['GET'])
@token_required
def get_employees():
    """Get all employees"""
    try:
        company_id = request.args.get('company_id')
        department_id = request.args.get('department_id')
        status = request.args.get('status')
        
        query = Employee.query.filter_by(company_id=company_id)
        if department_id:
            query = query.filter_by(department_id=department_id)
        if status:
            query = query.filter_by(employment_status=status)
        
        employees = query.all()
        return jsonify({
            'success': True,
            'data': [employee.to_dict() for employee in employees]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@people_api.route('/employees', methods=['POST'])
@token_required
def create_employee():
    """Create new employee"""
    try:
        data = request.get_json()
        employee = Employee(
            employee_id=data['employee_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            middle_name=data.get('middle_name'),
            date_of_birth=datetime.fromisoformat(data['date_of_birth']).date() if data.get('date_of_birth') else None,
            gender=data.get('gender'),
            personal_email=data.get('personal_email'),
            work_email=data.get('work_email'),
            personal_phone=data.get('personal_phone'),
            work_phone=data.get('work_phone'),
            employee_type=data.get('employee_type'),
            date_of_joining=datetime.fromisoformat(data['date_of_joining']).date() if data.get('date_of_joining') else None,
            department_id=data.get('department_id'),
            designation_id=data.get('designation_id'),
            reports_to_id=data.get('reports_to_id'),
            basic_salary=data.get('basic_salary', 0),
            currency=data.get('currency', 'USD'),
            company_id=data['company_id']
        )
        db.session.add(employee)
        db.session.commit()
        return jsonify({'success': True, 'data': employee.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@people_api.route('/employees/<int:employee_id>', methods=['GET'])
@token_required
def get_employee(employee_id):
    """Get specific employee"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        return jsonify({'success': True, 'data': employee.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Department Management
@people_api.route('/departments', methods=['GET'])
@token_required
def get_departments():
    """Get all departments"""
    try:
        company_id = request.args.get('company_id')
        departments = Department.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [department.to_dict() for department in departments]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@people_api.route('/departments', methods=['POST'])
@token_required
def create_department():
    """Create new department"""
    try:
        data = request.get_json()
        department = Department(
            name=data['name'],
            code=data['code'],
            description=data.get('description'),
            parent_department_id=data.get('parent_department_id'),
            department_head_id=data.get('department_head_id'),
            company_id=data['company_id']
        )
        db.session.add(department)
        db.session.commit()
        return jsonify({'success': True, 'data': department.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Designation Management
@people_api.route('/designations', methods=['GET'])
@token_required
def get_designations():
    """Get all designations"""
    try:
        company_id = request.args.get('company_id')
        designations = Designation.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [designation.to_dict() for designation in designations]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@people_api.route('/designations', methods=['POST'])
@token_required
def create_designation():
    """Create new designation"""
    try:
        data = request.get_json()
        designation = Designation(
            name=data['name'],
            code=data['code'],
            description=data.get('description'),
            min_salary=data.get('min_salary', 0),
            max_salary=data.get('max_salary', 0),
            currency=data.get('currency', 'USD'),
            company_id=data['company_id']
        )
        db.session.add(designation)
        db.session.commit()
        return jsonify({'success': True, 'data': designation.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Leave Management
@people_api.route('/leave-types', methods=['GET'])
@token_required
def get_leave_types():
    """Get all leave types"""
    try:
        company_id = request.args.get('company_id')
        leave_types = LeaveType.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [leave_type.to_dict() for leave_type in leave_types]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@people_api.route('/leave-types', methods=['POST'])
@token_required
def create_leave_type():
    """Create new leave type"""
    try:
        data = request.get_json()
        leave_type = LeaveType(
            name=data['name'],
            code=data['code'],
            description=data.get('description'),
            max_days_per_year=data.get('max_days_per_year', 0),
            max_consecutive_days=data.get('max_consecutive_days', 0),
            requires_approval=data.get('requires_approval', True),
            is_paid=data.get('is_paid', True),
            company_id=data['company_id']
        )
        db.session.add(leave_type)
        db.session.commit()
        return jsonify({'success': True, 'data': leave_type.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@people_api.route('/leave-requests', methods=['GET'])
@token_required
def get_leave_requests():
    """Get leave requests"""
    try:
        company_id = request.args.get('company_id')
        employee_id = request.args.get('employee_id')
        status = request.args.get('status')
        
        query = LeaveRequest.query.filter_by(company_id=company_id)
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        if status:
            query = query.filter_by(status=status)
        
        leave_requests = query.all()
        return jsonify({
            'success': True,
            'data': [request.to_dict() for request in leave_requests]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@people_api.route('/leave-requests', methods=['POST'])
@token_required
def create_leave_request():
    """Create leave request"""
    try:
        data = request.get_json()
        leave_request = LeaveRequest(
            employee_id=data['employee_id'],
            leave_type_id=data['leave_type_id'],
            start_date=datetime.fromisoformat(data['start_date']).date(),
            end_date=datetime.fromisoformat(data['end_date']).date(),
            total_days=data['total_days'],
            reason=data.get('reason'),
            company_id=data['company_id']
        )
        db.session.add(leave_request)
        db.session.commit()
        return jsonify({'success': True, 'data': leave_request.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@people_api.route('/leave-requests/<int:request_id>/approve', methods=['POST'])
@token_required
def approve_leave_request(request_id):
    """Approve leave request"""
    try:
        data = request.get_json()
        leave_request = LeaveRequest.query.get_or_404(request_id)
        leave_request.status = 'Approved'
        leave_request.approved_by_id = data.get('approved_by_id')
        leave_request.approved_date = datetime.now()
        db.session.commit()
        return jsonify({'success': True, 'data': leave_request.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Attendance Management
@people_api.route('/attendance', methods=['GET'])
@token_required
def get_attendance():
    """Get attendance records"""
    try:
        company_id = request.args.get('company_id')
        employee_id = request.args.get('employee_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Attendance.query.filter_by(company_id=company_id)
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        if start_date:
            query = query.filter(Attendance.attendance_date >= datetime.fromisoformat(start_date).date())
        if end_date:
            query = query.filter(Attendance.attendance_date <= datetime.fromisoformat(end_date).date())
        
        attendance_records = query.all()
        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in attendance_records]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@people_api.route('/attendance', methods=['POST'])
@token_required
def create_attendance():
    """Create attendance record"""
    try:
        data = request.get_json()
        attendance = Attendance(
            employee_id=data['employee_id'],
            attendance_date=datetime.fromisoformat(data['attendance_date']).date(),
            check_in_time=datetime.fromisoformat(data['check_in_time']) if data.get('check_in_time') else None,
            check_out_time=datetime.fromisoformat(data['check_out_time']) if data.get('check_out_time') else None,
            status=data.get('status', 'Present'),
            hours_worked=data.get('hours_worked', 0),
            overtime_hours=data.get('overtime_hours', 0),
            notes=data.get('notes'),
            company_id=data['company_id']
        )
        db.session.add(attendance)
        db.session.commit()
        return jsonify({'success': True, 'data': attendance.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Payroll Management
@people_api.route('/payroll', methods=['GET'])
@token_required
def get_payroll():
    """Get payroll records"""
    try:
        company_id = request.args.get('company_id')
        employee_id = request.args.get('employee_id')
        pay_period = request.args.get('pay_period')
        
        query = Payroll.query.filter_by(company_id=company_id)
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        if pay_period:
            query = query.filter(Payroll.pay_period_start <= datetime.fromisoformat(pay_period).date())
            query = query.filter(Payroll.pay_period_end >= datetime.fromisoformat(pay_period).date())
        
        payroll_records = query.all()
        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in payroll_records]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@people_api.route('/payroll', methods=['POST'])
@token_required
def create_payroll():
    """Create payroll record"""
    try:
        data = request.get_json()
        payroll = Payroll(
            employee_id=data['employee_id'],
            pay_period_start=datetime.fromisoformat(data['pay_period_start']).date(),
            pay_period_end=datetime.fromisoformat(data['pay_period_end']).date(),
            pay_date=datetime.fromisoformat(data['pay_date']).date(),
            basic_salary=data.get('basic_salary', 0),
            allowances=data.get('allowances', {}),
            deductions=data.get('deductions', {}),
            overtime_pay=data.get('overtime_pay', 0),
            bonus=data.get('bonus', 0),
            gross_salary=data.get('gross_salary', 0),
            total_deductions=data.get('total_deductions', 0),
            net_salary=data.get('net_salary', 0),
            currency=data.get('currency', 'USD'),
            company_id=data['company_id']
        )
        db.session.add(payroll)
        db.session.commit()
        return jsonify({'success': True, 'data': payroll.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Performance Management
@people_api.route('/performance', methods=['GET'])
@token_required
def get_performance():
    """Get performance records"""
    try:
        company_id = request.args.get('company_id')
        employee_id = request.args.get('employee_id')
        
        query = Performance.query.filter_by(company_id=company_id)
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        
        performance_records = query.all()
        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in performance_records]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@people_api.route('/performance', methods=['POST'])
@token_required
def create_performance():
    """Create performance record"""
    try:
        data = request.get_json()
        performance = Performance(
            employee_id=data['employee_id'],
            review_period_start=datetime.fromisoformat(data['review_period_start']).date(),
            review_period_end=datetime.fromisoformat(data['review_period_end']).date(),
            review_date=datetime.fromisoformat(data['review_date']).date(),
            overall_rating=data.get('overall_rating', 0),
            goals_achieved=data.get('goals_achieved', 0),
            total_goals=data.get('total_goals', 0),
            strengths=data.get('strengths'),
            areas_for_improvement=data.get('areas_for_improvement'),
            goals_for_next_period=data.get('goals_for_next_period'),
            reviewer_comments=data.get('reviewer_comments'),
            reviewed_by_id=data.get('reviewed_by_id'),
            company_id=data['company_id']
        )
        db.session.add(performance)
        db.session.commit()
        return jsonify({'success': True, 'data': performance.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Training Management
@people_api.route('/training', methods=['GET'])
@token_required
def get_training():
    """Get training records"""
    try:
        company_id = request.args.get('company_id')
        training_records = Training.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in training_records]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@people_api.route('/training', methods=['POST'])
@token_required
def create_training():
    """Create training record"""
    try:
        data = request.get_json()
        training = Training(
            training_name=data['training_name'],
            description=data.get('description'),
            training_type=data.get('training_type'),
            start_date=datetime.fromisoformat(data['start_date']).date() if data.get('start_date') else None,
            end_date=datetime.fromisoformat(data['end_date']).date() if data.get('end_date') else None,
            duration_hours=data.get('duration_hours', 0),
            cost=data.get('cost', 0),
            currency=data.get('currency', 'USD'),
            trainer_name=data.get('trainer_name'),
            trainer_email=data.get('trainer_email'),
            trainer_phone=data.get('trainer_phone'),
            company_id=data['company_id']
        )
        db.session.add(training)
        db.session.commit()
        return jsonify({'success': True, 'data': training.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Recruitment Management
@people_api.route('/recruitment', methods=['GET'])
@token_required
def get_recruitment():
    """Get recruitment records"""
    try:
        company_id = request.args.get('company_id')
        status = request.args.get('status')
        
        query = Recruitment.query.filter_by(company_id=company_id)
        if status:
            query = query.filter_by(status=status)
        
        recruitment_records = query.all()
        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in recruitment_records]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@people_api.route('/recruitment', methods=['POST'])
@token_required
def create_recruitment():
    """Create recruitment record"""
    try:
        data = request.get_json()
        recruitment = Recruitment(
            job_title=data['job_title'],
            job_description=data.get('job_description'),
            department_id=data.get('department_id'),
            required_skills=data.get('required_skills', []),
            experience_required=data.get('experience_required'),
            education_required=data.get('education_required'),
            employment_type=data.get('employment_type'),
            salary_range_min=data.get('salary_range_min', 0),
            salary_range_max=data.get('salary_range_max', 0),
            currency=data.get('currency', 'USD'),
            application_deadline=datetime.fromisoformat(data['application_deadline']).date() if data.get('application_deadline') else None,
            hiring_manager_id=data.get('hiring_manager_id'),
            company_id=data['company_id']
        )
        db.session.add(recruitment)
        db.session.commit()
        return jsonify({'success': True, 'data': recruitment.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
