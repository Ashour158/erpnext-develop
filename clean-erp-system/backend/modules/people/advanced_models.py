# Advanced HR & People Models
# Comprehensive HR management with performance, learning, recruitment, and workforce analytics

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

class PerformanceRating(enum.Enum):
    EXCEEDS_EXPECTATIONS = "Exceeds Expectations"
    MEETS_EXPECTATIONS = "Meets Expectations"
    BELOW_EXPECTATIONS = "Below Expectations"
    UNSATISFACTORY = "Unsatisfactory"

class ReviewType(enum.Enum):
    ANNUAL = "Annual"
    QUARTERLY = "Quarterly"
    MONTHLY = "Monthly"
    PROJECT = "Project"
    PROBATION = "Probation"

class GoalStatus(enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"

class LearningStatus(enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"

class ApplicationStatus(enum.Enum):
    APPLIED = "Applied"
    SCREENING = "Screening"
    INTERVIEW = "Interview"
    ASSESSMENT = "Assessment"
    REFERENCE_CHECK = "Reference Check"
    OFFER = "Offer"
    HIRED = "Hired"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"

class EngagementLevel(enum.Enum):
    HIGHLY_ENGAGED = "Highly Engaged"
    ENGAGED = "Engaged"
    NEUTRAL = "Neutral"
    DISENGAGED = "Disengaged"
    HIGHLY_DISENGAGED = "Highly Disengaged"

# Performance Management Models
class PerformanceReview(BaseModel):
    """Performance review model"""
    __tablename__ = 'performance_reviews'
    
    # Review Information
    review_period_start = db.Column(db.Date, nullable=False)
    review_period_end = db.Column(db.Date, nullable=False)
    review_type = db.Column(db.Enum(ReviewType), nullable=False)
    review_year = db.Column(db.Integer, nullable=False)
    
    # Employee Information
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee")
    
    # Reviewers
    reviewer_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])
    
    # Review Details
    overall_rating = db.Column(db.Enum(PerformanceRating))
    overall_score = db.Column(db.Float, default=0.0)
    strengths = db.Column(db.Text)
    areas_for_improvement = db.Column(db.Text)
    goals_achieved = db.Column(db.Text)
    goals_not_achieved = db.Column(db.Text)
    development_plan = db.Column(db.Text)
    
    # Review Status
    status = db.Column(db.String(50), default='Draft')  # Draft, Submitted, Reviewed, Approved, Completed
    submitted_date = db.Column(db.DateTime)
    reviewed_date = db.Column(db.DateTime)
    approved_date = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    review_goals = relationship("ReviewGoal", back_populates="performance_review")
    review_competencies = relationship("ReviewCompetency", back_populates="performance_review")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'review_period_start': self.review_period_start.isoformat() if self.review_period_start else None,
            'review_period_end': self.review_period_end.isoformat() if self.review_period_end else None,
            'review_type': self.review_type.value if self.review_type else None,
            'review_year': self.review_year,
            'employee_id': self.employee_id,
            'reviewer_id': self.reviewer_id,
            'overall_rating': self.overall_rating.value if self.overall_rating else None,
            'overall_score': self.overall_score,
            'strengths': self.strengths,
            'areas_for_improvement': self.areas_for_improvement,
            'goals_achieved': self.goals_achieved,
            'goals_not_achieved': self.goals_not_achieved,
            'development_plan': self.development_plan,
            'status': self.status,
            'submitted_date': self.submitted_date.isoformat() if self.submitted_date else None,
            'reviewed_date': self.reviewed_date.isoformat() if self.reviewed_date else None,
            'approved_date': self.approved_date.isoformat() if self.approved_date else None,
            'company_id': self.company_id
        })
        return data

class ReviewGoal(BaseModel):
    """Review goal model"""
    __tablename__ = 'review_goals'
    
    # Goal Information
    goal_title = db.Column(db.String(200), nullable=False)
    goal_description = db.Column(db.Text)
    target_value = db.Column(db.Float, default=0.0)
    actual_value = db.Column(db.Float, default=0.0)
    achievement_percentage = db.Column(db.Float, default=0.0)
    
    # Goal Details
    goal_weight = db.Column(db.Float, default=1.0)
    goal_status = db.Column(db.Enum(GoalStatus), default=GoalStatus.NOT_STARTED)
    start_date = db.Column(db.Date)
    target_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    
    # Review Association
    performance_review_id = db.Column(db.Integer, db.ForeignKey('performance_reviews.id'), nullable=False)
    performance_review = relationship("PerformanceReview", back_populates="review_goals")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'goal_title': self.goal_title,
            'goal_description': self.goal_description,
            'target_value': self.target_value,
            'actual_value': self.actual_value,
            'achievement_percentage': self.achievement_percentage,
            'goal_weight': self.goal_weight,
            'goal_status': self.goal_status.value if self.goal_status else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'performance_review_id': self.performance_review_id,
            'company_id': self.company_id
        })
        return data

class ReviewCompetency(BaseModel):
    """Review competency model"""
    __tablename__ = 'review_competencies'
    
    # Competency Information
    competency_name = db.Column(db.String(200), nullable=False)
    competency_description = db.Column(db.Text)
    rating = db.Column(db.Enum(PerformanceRating))
    score = db.Column(db.Float, default=0.0)
    comments = db.Column(db.Text)
    
    # Review Association
    performance_review_id = db.Column(db.Integer, db.ForeignKey('performance_reviews.id'), nullable=False)
    performance_review = relationship("PerformanceReview", back_populates="review_competencies")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'competency_name': self.competency_name,
            'competency_description': self.competency_description,
            'rating': self.rating.value if self.rating else None,
            'score': self.score,
            'comments': self.comments,
            'performance_review_id': self.performance_review_id,
            'company_id': self.company_id
        })
        return data

# Learning Management Models
class LearningProgram(BaseModel):
    """Learning program model"""
    __tablename__ = 'learning_programs'
    
    # Program Information
    program_name = db.Column(db.String(200), nullable=False)
    program_description = db.Column(db.Text)
    program_type = db.Column(db.String(100), nullable=False)  # Training, Certification, Workshop, etc.
    
    # Program Details
    duration_hours = db.Column(db.Float, default=0.0)
    difficulty_level = db.Column(db.String(50), default='Beginner')  # Beginner, Intermediate, Advanced
    program_cost = db.Column(db.Float, default=0.0)
    
    # Program Settings
    is_mandatory = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    max_participants = db.Column(db.Integer, default=0)
    
    # Program Schedule
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    registration_deadline = db.Column(db.Date)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    program_enrollments = relationship("ProgramEnrollment", back_populates="learning_program")
    program_modules = relationship("ProgramModule", back_populates="learning_program")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'program_name': self.program_name,
            'program_description': self.program_description,
            'program_type': self.program_type,
            'duration_hours': self.duration_hours,
            'difficulty_level': self.difficulty_level,
            'program_cost': self.program_cost,
            'is_mandatory': self.is_mandatory,
            'is_active': self.is_active,
            'max_participants': self.max_participants,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            'company_id': self.company_id
        })
        return data

class ProgramEnrollment(BaseModel):
    """Program enrollment model"""
    __tablename__ = 'program_enrollments'
    
    # Enrollment Information
    enrollment_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.Enum(LearningStatus), default=LearningStatus.NOT_STARTED)
    completion_percentage = db.Column(db.Float, default=0.0)
    completion_date = db.Column(db.Date)
    score = db.Column(db.Float, default=0.0)
    certificate_issued = db.Column(db.Boolean, default=False)
    
    # Employee Association
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee")
    
    # Program Association
    program_id = db.Column(db.Integer, db.ForeignKey('learning_programs.id'), nullable=False)
    learning_program = relationship("LearningProgram", back_populates="program_enrollments")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'status': self.status.value if self.status else None,
            'completion_percentage': self.completion_percentage,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'score': self.score,
            'certificate_issued': self.certificate_issued,
            'employee_id': self.employee_id,
            'program_id': self.program_id,
            'company_id': self.company_id
        })
        return data

class ProgramModule(BaseModel):
    """Program module model"""
    __tablename__ = 'program_modules'
    
    # Module Information
    module_name = db.Column(db.String(200), nullable=False)
    module_description = db.Column(db.Text)
    module_order = db.Column(db.Integer, default=0)
    duration_minutes = db.Column(db.Integer, default=0)
    
    # Module Content
    content_type = db.Column(db.String(100), default='Video')  # Video, Text, Quiz, Assignment
    content_url = db.Column(db.String(500))
    content_text = db.Column(db.Text)
    
    # Module Settings
    is_required = db.Column(db.Boolean, default=True)
    passing_score = db.Column(db.Float, default=70.0)
    
    # Program Association
    program_id = db.Column(db.Integer, db.ForeignKey('learning_programs.id'), nullable=False)
    learning_program = relationship("LearningProgram", back_populates="program_modules")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'module_name': self.module_name,
            'module_description': self.module_description,
            'module_order': self.module_order,
            'duration_minutes': self.duration_minutes,
            'content_type': self.content_type,
            'content_url': self.content_url,
            'content_text': self.content_text,
            'is_required': self.is_required,
            'passing_score': self.passing_score,
            'program_id': self.program_id,
            'company_id': self.company_id
        })
        return data

# Recruitment Models
class JobPosting(BaseModel):
    """Job posting model"""
    __tablename__ = 'job_postings'
    
    # Job Information
    job_title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    job_requirements = db.Column(db.Text)
    job_responsibilities = db.Column(db.Text)
    
    # Job Details
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    department = relationship("Department")
    
    employment_type = db.Column(db.String(100), default='Full-time')  # Full-time, Part-time, Contract, Internship
    experience_level = db.Column(db.String(100), default='Mid-level')  # Entry-level, Mid-level, Senior, Executive
    salary_range_min = db.Column(db.Float, default=0.0)
    salary_range_max = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Job Settings
    is_active = db.Column(db.Boolean, default=True)
    is_remote = db.Column(db.Boolean, default=False)
    max_applications = db.Column(db.Integer, default=0)
    
    # Dates
    posting_date = db.Column(db.Date, default=date.today)
    application_deadline = db.Column(db.Date)
    start_date = db.Column(db.Date)
    
    # Hiring Manager
    hiring_manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    hiring_manager = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    job_applications = relationship("JobApplication", back_populates="job_posting")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'job_title': self.job_title,
            'job_description': self.job_description,
            'job_requirements': self.job_requirements,
            'job_responsibilities': self.job_responsibilities,
            'department_id': self.department_id,
            'employment_type': self.employment_type,
            'experience_level': self.experience_level,
            'salary_range_min': self.salary_range_min,
            'salary_range_max': self.salary_range_max,
            'currency': self.currency,
            'is_active': self.is_active,
            'is_remote': self.is_remote,
            'max_applications': self.max_applications,
            'posting_date': self.posting_date.isoformat() if self.posting_date else None,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'hiring_manager_id': self.hiring_manager_id,
            'company_id': self.company_id
        })
        return data

class JobApplication(BaseModel):
    """Job application model"""
    __tablename__ = 'job_applications'
    
    # Applicant Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    
    # Application Details
    application_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.APPLIED)
    cover_letter = db.Column(db.Text)
    resume_url = db.Column(db.String(500))
    
    # Application Scores
    initial_score = db.Column(db.Float, default=0.0)
    interview_score = db.Column(db.Float, default=0.0)
    assessment_score = db.Column(db.Float, default=0.0)
    final_score = db.Column(db.Float, default=0.0)
    
    # Job Association
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    job_posting = relationship("JobPosting", back_populates="job_applications")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    application_interviews = relationship("ApplicationInterview", back_populates="job_application")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'status': self.status.value if self.status else None,
            'cover_letter': self.cover_letter,
            'resume_url': self.resume_url,
            'initial_score': self.initial_score,
            'interview_score': self.interview_score,
            'assessment_score': self.assessment_score,
            'final_score': self.final_score,
            'job_posting_id': self.job_posting_id,
            'company_id': self.company_id
        })
        return data

class ApplicationInterview(BaseModel):
    """Application interview model"""
    __tablename__ = 'application_interviews'
    
    # Interview Information
    interview_type = db.Column(db.String(100), nullable=False)  # Phone, Video, In-person, Panel
    interview_date = db.Column(db.DateTime)
    interview_duration = db.Column(db.Integer, default=60)  # minutes
    
    # Interviewers
    interviewer_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    interviewer = relationship("Employee")
    
    # Interview Details
    interview_notes = db.Column(db.Text)
    interview_score = db.Column(db.Float, default=0.0)
    recommendation = db.Column(db.String(100))  # Hire, No Hire, Maybe
    
    # Application Association
    application_id = db.Column(db.Integer, db.ForeignKey('job_applications.id'), nullable=False)
    job_application = relationship("JobApplication", back_populates="application_interviews")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'interview_type': self.interview_type,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None,
            'interview_duration': self.interview_duration,
            'interviewer_id': self.interviewer_id,
            'interview_notes': self.interview_notes,
            'interview_score': self.interview_score,
            'recommendation': self.recommendation,
            'application_id': self.application_id,
            'company_id': self.company_id
        })
        return data

# Employee Engagement Models
class EngagementSurvey(BaseModel):
    """Employee engagement survey model"""
    __tablename__ = 'engagement_surveys'
    
    # Survey Information
    survey_name = db.Column(db.String(200), nullable=False)
    survey_description = db.Column(db.Text)
    survey_year = db.Column(db.Integer, nullable=False)
    survey_quarter = db.Column(db.Integer, default=0)  # 0 for annual, 1-4 for quarterly
    
    # Survey Settings
    is_anonymous = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Survey Dates
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    survey_responses = relationship("SurveyResponse", back_populates="engagement_survey")
    survey_questions = relationship("SurveyQuestion", back_populates="engagement_survey")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'survey_name': self.survey_name,
            'survey_description': self.survey_description,
            'survey_year': self.survey_year,
            'survey_quarter': self.survey_quarter,
            'is_anonymous': self.is_anonymous,
            'is_active': self.is_active,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'company_id': self.company_id
        })
        return data

class SurveyResponse(BaseModel):
    """Survey response model"""
    __tablename__ = 'survey_responses'
    
    # Response Information
    response_date = db.Column(db.DateTime, default=datetime.utcnow)
    overall_engagement_score = db.Column(db.Float, default=0.0)
    engagement_level = db.Column(db.Enum(EngagementLevel))
    
    # Employee Information (if not anonymous)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    employee = relationship("Employee")
    
    # Survey Association
    survey_id = db.Column(db.Integer, db.ForeignKey('engagement_surveys.id'), nullable=False)
    engagement_survey = relationship("EngagementSurvey", back_populates="survey_responses")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    response_answers = relationship("ResponseAnswer", back_populates="survey_response")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'response_date': self.response_date.isoformat() if self.response_date else None,
            'overall_engagement_score': self.overall_engagement_score,
            'engagement_level': self.engagement_level.value if self.engagement_level else None,
            'employee_id': self.employee_id,
            'survey_id': self.survey_id,
            'company_id': self.company_id
        })
        return data

class SurveyQuestion(BaseModel):
    """Survey question model"""
    __tablename__ = 'survey_questions'
    
    # Question Information
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), default='Rating')  # Rating, Multiple Choice, Text, Yes/No
    question_order = db.Column(db.Integer, default=0)
    is_required = db.Column(db.Boolean, default=True)
    
    # Question Options (for multiple choice)
    question_options = db.Column(db.JSON)
    
    # Survey Association
    survey_id = db.Column(db.Integer, db.ForeignKey('engagement_surveys.id'), nullable=False)
    engagement_survey = relationship("EngagementSurvey", back_populates="survey_questions")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    response_answers = relationship("ResponseAnswer", back_populates="survey_question")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'question_text': self.question_text,
            'question_type': self.question_type,
            'question_order': self.question_order,
            'is_required': self.is_required,
            'question_options': self.question_options,
            'survey_id': self.survey_id,
            'company_id': self.company_id
        })
        return data

class ResponseAnswer(BaseModel):
    """Response answer model"""
    __tablename__ = 'response_answers'
    
    # Answer Information
    answer_text = db.Column(db.Text)
    answer_numeric = db.Column(db.Float, default=0.0)
    answer_boolean = db.Column(db.Boolean)
    
    # Response Association
    response_id = db.Column(db.Integer, db.ForeignKey('survey_responses.id'), nullable=False)
    survey_response = relationship("SurveyResponse", back_populates="response_answers")
    
    # Question Association
    question_id = db.Column(db.Integer, db.ForeignKey('survey_questions.id'), nullable=False)
    survey_question = relationship("SurveyQuestion", back_populates="response_answers")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'answer_text': self.answer_text,
            'answer_numeric': self.answer_numeric,
            'answer_boolean': self.answer_boolean,
            'response_id': self.response_id,
            'question_id': self.question_id,
            'company_id': self.company_id
        })
        return data
