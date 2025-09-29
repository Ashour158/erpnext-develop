# Advanced HR & People API Endpoints
# Comprehensive HR management with performance, learning, recruitment, and workforce analytics

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import require_auth, get_current_user
from .advanced_models import (
    PerformanceReview, ReviewGoal, ReviewCompetency,
    LearningProgram, ProgramEnrollment, ProgramModule,
    JobPosting, JobApplication, ApplicationInterview,
    EngagementSurvey, SurveyResponse, SurveyQuestion, ResponseAnswer
)
from datetime import datetime, date
import json

# Create blueprint
advanced_people_bp = Blueprint('advanced_people', __name__, url_prefix='/advanced-people')

# Performance Management Endpoints
@advanced_people_bp.route('/performance-reviews', methods=['GET'])
@require_auth
def get_performance_reviews():
    """Get all performance reviews"""
    try:
        query = PerformanceReview.query.filter_by(company_id=get_current_user().company_id)
        
        # Apply filters
        if request.args.get('employee_id'):
            query = query.filter_by(employee_id=request.args.get('employee_id'))
        if request.args.get('review_year'):
            query = query.filter_by(review_year=request.args.get('review_year'))
        if request.args.get('status'):
            query = query.filter_by(status=request.args.get('status'))
        
        reviews = query.all()
        return jsonify({
            'success': True,
            'data': [review.to_dict() for review in reviews]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/performance-reviews', methods=['POST'])
@require_auth
def create_performance_review():
    """Create a new performance review"""
    try:
        data = request.get_json()
        review = PerformanceReview(
            review_period_start=datetime.strptime(data['review_period_start'], '%Y-%m-%d').date(),
            review_period_end=datetime.strptime(data['review_period_end'], '%Y-%m-%d').date(),
            review_type=data['review_type'],
            review_year=data['review_year'],
            employee_id=data['employee_id'],
            reviewer_id=data['reviewer_id'],
            overall_rating=data.get('overall_rating'),
            overall_score=data.get('overall_score', 0.0),
            strengths=data.get('strengths'),
            areas_for_improvement=data.get('areas_for_improvement'),
            goals_achieved=data.get('goals_achieved'),
            goals_not_achieved=data.get('goals_not_achieved'),
            development_plan=data.get('development_plan'),
            status=data.get('status', 'Draft'),
            company_id=get_current_user().company_id
        )
        db.session.add(review)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': review.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/performance-reviews/<int:review_id>/goals', methods=['POST'])
@require_auth
def add_review_goal(review_id):
    """Add a goal to a performance review"""
    try:
        data = request.get_json()
        goal = ReviewGoal(
            goal_title=data['goal_title'],
            goal_description=data.get('goal_description'),
            target_value=data.get('target_value', 0.0),
            goal_weight=data.get('goal_weight', 1.0),
            goal_status=data.get('goal_status', 'Not Started'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            target_date=datetime.strptime(data['target_date'], '%Y-%m-%d').date() if data.get('target_date') else None,
            performance_review_id=review_id,
            company_id=get_current_user().company_id
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': goal.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/performance-reviews/<int:review_id>/competencies', methods=['POST'])
@require_auth
def add_review_competency(review_id):
    """Add a competency to a performance review"""
    try:
        data = request.get_json()
        competency = ReviewCompetency(
            competency_name=data['competency_name'],
            competency_description=data.get('competency_description'),
            rating=data.get('rating'),
            score=data.get('score', 0.0),
            comments=data.get('comments'),
            performance_review_id=review_id,
            company_id=get_current_user().company_id
        )
        db.session.add(competency)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': competency.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Learning Management Endpoints
@advanced_people_bp.route('/learning-programs', methods=['GET'])
@require_auth
def get_learning_programs():
    """Get all learning programs"""
    try:
        programs = LearningProgram.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [program.to_dict() for program in programs]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/learning-programs', methods=['POST'])
@require_auth
def create_learning_program():
    """Create a new learning program"""
    try:
        data = request.get_json()
        program = LearningProgram(
            program_name=data['program_name'],
            program_description=data.get('program_description'),
            program_type=data['program_type'],
            duration_hours=data.get('duration_hours', 0.0),
            difficulty_level=data.get('difficulty_level', 'Beginner'),
            program_cost=data.get('program_cost', 0.0),
            is_mandatory=data.get('is_mandatory', False),
            is_active=data.get('is_active', True),
            max_participants=data.get('max_participants', 0),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            registration_deadline=datetime.strptime(data['registration_deadline'], '%Y-%m-%d').date() if data.get('registration_deadline') else None,
            company_id=get_current_user().company_id
        )
        db.session.add(program)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': program.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/learning-programs/<int:program_id>/enroll', methods=['POST'])
@require_auth
def enroll_in_program(program_id):
    """Enroll an employee in a learning program"""
    try:
        data = request.get_json()
        enrollment = ProgramEnrollment(
            enrollment_date=datetime.strptime(data['enrollment_date'], '%Y-%m-%d').date() if data.get('enrollment_date') else date.today(),
            status=data.get('status', 'Not Started'),
            employee_id=data['employee_id'],
            program_id=program_id,
            company_id=get_current_user().company_id
        )
        db.session.add(enrollment)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': enrollment.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/learning-programs/<int:program_id>/modules', methods=['POST'])
@require_auth
def add_program_module(program_id):
    """Add a module to a learning program"""
    try:
        data = request.get_json()
        module = ProgramModule(
            module_name=data['module_name'],
            module_description=data.get('module_description'),
            module_order=data.get('module_order', 0),
            duration_minutes=data.get('duration_minutes', 0),
            content_type=data.get('content_type', 'Video'),
            content_url=data.get('content_url'),
            content_text=data.get('content_text'),
            is_required=data.get('is_required', True),
            passing_score=data.get('passing_score', 70.0),
            program_id=program_id,
            company_id=get_current_user().company_id
        )
        db.session.add(module)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': module.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Recruitment Endpoints
@advanced_people_bp.route('/job-postings', methods=['GET'])
@require_auth
def get_job_postings():
    """Get all job postings"""
    try:
        query = JobPosting.query.filter_by(company_id=get_current_user().company_id)
        
        # Apply filters
        if request.args.get('department_id'):
            query = query.filter_by(department_id=request.args.get('department_id'))
        if request.args.get('employment_type'):
            query = query.filter_by(employment_type=request.args.get('employment_type'))
        if request.args.get('is_active'):
            query = query.filter_by(is_active=request.args.get('is_active') == 'true')
        
        postings = query.all()
        return jsonify({
            'success': True,
            'data': [posting.to_dict() for posting in postings]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/job-postings', methods=['POST'])
@require_auth
def create_job_posting():
    """Create a new job posting"""
    try:
        data = request.get_json()
        posting = JobPosting(
            job_title=data['job_title'],
            job_description=data['job_description'],
            job_requirements=data.get('job_requirements'),
            job_responsibilities=data.get('job_responsibilities'),
            department_id=data.get('department_id'),
            employment_type=data.get('employment_type', 'Full-time'),
            experience_level=data.get('experience_level', 'Mid-level'),
            salary_range_min=data.get('salary_range_min', 0.0),
            salary_range_max=data.get('salary_range_max', 0.0),
            currency=data.get('currency', 'USD'),
            is_active=data.get('is_active', True),
            is_remote=data.get('is_remote', False),
            max_applications=data.get('max_applications', 0),
            posting_date=datetime.strptime(data['posting_date'], '%Y-%m-%d').date() if data.get('posting_date') else date.today(),
            application_deadline=datetime.strptime(data['application_deadline'], '%Y-%m-%d').date() if data.get('application_deadline') else None,
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            hiring_manager_id=data.get('hiring_manager_id'),
            company_id=get_current_user().company_id
        )
        db.session.add(posting)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': posting.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/job-applications', methods=['GET'])
@require_auth
def get_job_applications():
    """Get all job applications"""
    try:
        query = JobApplication.query.filter_by(company_id=get_current_user().company_id)
        
        # Apply filters
        if request.args.get('job_posting_id'):
            query = query.filter_by(job_posting_id=request.args.get('job_posting_id'))
        if request.args.get('status'):
            query = query.filter_by(status=request.args.get('status'))
        
        applications = query.all()
        return jsonify({
            'success': True,
            'data': [application.to_dict() for application in applications]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/job-applications', methods=['POST'])
@require_auth
def create_job_application():
    """Create a new job application"""
    try:
        data = request.get_json()
        application = JobApplication(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            application_date=datetime.strptime(data['application_date'], '%Y-%m-%d').date() if data.get('application_date') else date.today(),
            status=data.get('status', 'Applied'),
            cover_letter=data.get('cover_letter'),
            resume_url=data.get('resume_url'),
            job_posting_id=data['job_posting_id'],
            company_id=get_current_user().company_id
        )
        db.session.add(application)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': application.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/job-applications/<int:application_id>/interviews', methods=['POST'])
@require_auth
def schedule_interview(application_id):
    """Schedule an interview for a job application"""
    try:
        data = request.get_json()
        interview = ApplicationInterview(
            interview_type=data['interview_type'],
            interview_date=datetime.strptime(data['interview_date'], '%Y-%m-%dT%H:%M:%S') if data.get('interview_date') else None,
            interview_duration=data.get('interview_duration', 60),
            interviewer_id=data.get('interviewer_id'),
            application_id=application_id,
            company_id=get_current_user().company_id
        )
        db.session.add(interview)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': interview.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Employee Engagement Endpoints
@advanced_people_bp.route('/engagement-surveys', methods=['GET'])
@require_auth
def get_engagement_surveys():
    """Get all engagement surveys"""
    try:
        surveys = EngagementSurvey.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [survey.to_dict() for survey in surveys]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/engagement-surveys', methods=['POST'])
@require_auth
def create_engagement_survey():
    """Create a new engagement survey"""
    try:
        data = request.get_json()
        survey = EngagementSurvey(
            survey_name=data['survey_name'],
            survey_description=data.get('survey_description'),
            survey_year=data['survey_year'],
            survey_quarter=data.get('survey_quarter', 0),
            is_anonymous=data.get('is_anonymous', True),
            is_active=data.get('is_active', True),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            company_id=get_current_user().company_id
        )
        db.session.add(survey)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': survey.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/engagement-surveys/<int:survey_id>/questions', methods=['POST'])
@require_auth
def add_survey_question(survey_id):
    """Add a question to an engagement survey"""
    try:
        data = request.get_json()
        question = SurveyQuestion(
            question_text=data['question_text'],
            question_type=data.get('question_type', 'Rating'),
            question_order=data.get('question_order', 0),
            is_required=data.get('is_required', True),
            question_options=data.get('question_options'),
            survey_id=survey_id,
            company_id=get_current_user().company_id
        )
        db.session.add(question)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': question.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/engagement-surveys/<int:survey_id>/responses', methods=['POST'])
@require_auth
def submit_survey_response(survey_id):
    """Submit a survey response"""
    try:
        data = request.get_json()
        response = SurveyResponse(
            response_date=datetime.strptime(data['response_date'], '%Y-%m-%dT%H:%M:%S') if data.get('response_date') else datetime.utcnow(),
            overall_engagement_score=data.get('overall_engagement_score', 0.0),
            engagement_level=data.get('engagement_level'),
            employee_id=data.get('employee_id'),
            survey_id=survey_id,
            company_id=get_current_user().company_id
        )
        db.session.add(response)
        db.session.commit()
        
        # Add response answers
        for answer_data in data.get('answers', []):
            answer = ResponseAnswer(
                answer_text=answer_data.get('answer_text'),
                answer_numeric=answer_data.get('answer_numeric', 0.0),
                answer_boolean=answer_data.get('answer_boolean'),
                response_id=response.id,
                question_id=answer_data['question_id'],
                company_id=get_current_user().company_id
            )
            db.session.add(answer)
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': response.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Analytics Endpoints
@advanced_people_bp.route('/analytics/performance-summary', methods=['GET'])
@require_auth
def get_performance_summary():
    """Get performance analytics summary"""
    try:
        # Get performance review statistics
        total_reviews = PerformanceReview.query.filter_by(company_id=get_current_user().company_id).count()
        
        # Get rating distribution
        rating_distribution = {}
        for rating in ['Exceeds Expectations', 'Meets Expectations', 'Below Expectations', 'Unsatisfactory']:
            count = PerformanceReview.query.filter_by(
                overall_rating=rating,
                company_id=get_current_user().company_id
            ).count()
            rating_distribution[rating] = count
        
        # Get average scores by department
        avg_scores = db.session.query(
            db.func.avg(PerformanceReview.overall_score)
        ).join(Employee).join(Department).filter(
            PerformanceReview.company_id == get_current_user().company_id
        ).group_by(Department.name).all()
        
        return jsonify({
            'success': True,
            'data': {
                'total_reviews': total_reviews,
                'rating_distribution': rating_distribution,
                'average_scores_by_department': [float(score[0]) for score in avg_scores]
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/analytics/learning-progress', methods=['GET'])
@require_auth
def get_learning_progress():
    """Get learning progress analytics"""
    try:
        # Get enrollment statistics
        total_enrollments = ProgramEnrollment.query.filter_by(company_id=get_current_user().company_id).count()
        completed_programs = ProgramEnrollment.query.filter_by(
            status='Completed',
            company_id=get_current_user().company_id
        ).count()
        
        # Get completion rates by program
        program_completion = {}
        programs = LearningProgram.query.filter_by(company_id=get_current_user().company_id).all()
        for program in programs:
            total_enrolled = ProgramEnrollment.query.filter_by(program_id=program.id).count()
            completed = ProgramEnrollment.query.filter_by(
                program_id=program.id,
                status='Completed'
            ).count()
            completion_rate = (completed / total_enrolled * 100) if total_enrolled > 0 else 0
            program_completion[program.program_name] = completion_rate
        
        return jsonify({
            'success': True,
            'data': {
                'total_enrollments': total_enrollments,
                'completed_programs': completed_programs,
                'overall_completion_rate': (completed_programs / total_enrollments * 100) if total_enrollments > 0 else 0,
                'program_completion_rates': program_completion
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/analytics/recruitment-metrics', methods=['GET'])
@require_auth
def get_recruitment_metrics():
    """Get recruitment analytics"""
    try:
        # Get application statistics
        total_applications = JobApplication.query.filter_by(company_id=get_current_user().company_id).count()
        hired_applications = JobApplication.query.filter_by(
            status='Hired',
            company_id=get_current_user().company_id
        ).count()
        
        # Get application status distribution
        status_distribution = {}
        for status in ['Applied', 'Screening', 'Interview', 'Assessment', 'Reference Check', 'Offer', 'Hired', 'Rejected', 'Withdrawn']:
            count = JobApplication.query.filter_by(
                status=status,
                company_id=get_current_user().company_id
            ).count()
            status_distribution[status] = count
        
        # Calculate hire rate
        hire_rate = (hired_applications / total_applications * 100) if total_applications > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_applications': total_applications,
                'hired_applications': hired_applications,
                'hire_rate': hire_rate,
                'status_distribution': status_distribution
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_people_bp.route('/analytics/engagement-metrics', methods=['GET'])
@require_auth
def get_engagement_metrics():
    """Get employee engagement analytics"""
    try:
        # Get engagement survey statistics
        total_responses = SurveyResponse.query.filter_by(company_id=get_current_user().company_id).count()
        avg_engagement_score = db.session.query(
            db.func.avg(SurveyResponse.overall_engagement_score)
        ).filter_by(company_id=get_current_user().company_id).scalar() or 0
        
        # Get engagement level distribution
        engagement_distribution = {}
        for level in ['Highly Engaged', 'Engaged', 'Neutral', 'Disengaged', 'Highly Disengaged']:
            count = SurveyResponse.query.filter_by(
                engagement_level=level,
                company_id=get_current_user().company_id
            ).count()
            engagement_distribution[level] = count
        
        return jsonify({
            'success': True,
            'data': {
                'total_responses': total_responses,
                'average_engagement_score': float(avg_engagement_score),
                'engagement_distribution': engagement_distribution
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
