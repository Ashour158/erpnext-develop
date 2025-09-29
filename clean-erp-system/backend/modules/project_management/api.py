# Project Management API Endpoints
# Complete project management with Gantt charts, resource allocation, and project analytics

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import require_auth, get_current_user
from .models import (
    Project, ProjectTask, ProjectResource, TaskResource, ProjectRisk,
    ProjectMilestone, TaskComment, ProjectTemplate
)
from datetime import datetime, date
import json

# Create blueprint
project_management_bp = Blueprint('project_management', __name__, url_prefix='/project-management')

# Project Management Endpoints
@project_management_bp.route('/projects', methods=['GET'])
@require_auth
def get_projects():
    """Get all projects with advanced filtering"""
    try:
        query = Project.query.filter_by(company_id=get_current_user().company_id)
        
        # Apply filters
        if request.args.get('status'):
            query = query.filter_by(status=request.args.get('status'))
        if request.args.get('project_manager_id'):
            query = query.filter_by(project_manager_id=request.args.get('project_manager_id'))
        if request.args.get('client_id'):
            query = query.filter_by(client_id=request.args.get('client_id'))
        if request.args.get('project_type'):
            query = query.filter_by(project_type=request.args.get('project_type'))
        
        projects = query.all()
        return jsonify({
            'success': True,
            'data': [project.to_dict() for project in projects]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@project_management_bp.route('/projects', methods=['POST'])
@require_auth
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        
        # Generate project code
        project_code = f"PRJ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        project = Project(
            project_name=data['project_name'],
            project_code=project_code,
            description=data.get('description'),
            project_type=data.get('project_type', 'Internal'),
            project_category=data.get('project_category'),
            project_manager_id=data.get('project_manager_id'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            status=data.get('status', 'Planning'),
            budget_allocated=data.get('budget_allocated', 0.0),
            currency=data.get('currency', 'USD'),
            is_billable=data.get('is_billable', False),
            is_confidential=data.get('is_confidential', False),
            requires_approval=data.get('requires_approval', False),
            client_id=data.get('client_id'),
            company_id=get_current_user().company_id
        )
        
        # Calculate planned duration
        if project.start_date and project.end_date:
            project.planned_duration_days = (project.end_date - project.start_date).days
        
        db.session.add(project)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': project.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@project_management_bp.route('/projects/<int:project_id>', methods=['PUT'])
@require_auth
def update_project(project_id):
    """Update a project"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        # Update project fields
        for key, value in data.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        # Recalculate duration if dates changed
        if project.start_date and project.end_date:
            project.planned_duration_days = (project.end_date - project.start_date).days
        
        # Calculate budget remaining
        project.budget_remaining = project.budget_allocated - project.budget_spent
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': project.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Project Task Endpoints
@project_management_bp.route('/projects/<int:project_id>/tasks', methods=['GET'])
@require_auth
def get_project_tasks(project_id):
    """Get all tasks for a project"""
    try:
        tasks = ProjectTask.query.filter_by(
            project_id=project_id,
            company_id=get_current_user().company_id
        ).all()
        return jsonify({
            'success': True,
            'data': [task.to_dict() for task in tasks]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@project_management_bp.route('/projects/<int:project_id>/tasks', methods=['POST'])
@require_auth
def create_project_task(project_id):
    """Create a new task for a project"""
    try:
        data = request.get_json()
        
        # Generate task code
        task_code = f"TSK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        task = ProjectTask(
            task_name=data['task_name'],
            task_description=data.get('task_description'),
            task_code=task_code,
            project_id=project_id,
            parent_task_id=data.get('parent_task_id'),
            assigned_to_id=data.get('assigned_to_id'),
            planned_start_date=datetime.strptime(data['planned_start_date'], '%Y-%m-%d').date() if data.get('planned_start_date') else None,
            planned_end_date=datetime.strptime(data['planned_end_date'], '%Y-%m-%d').date() if data.get('planned_end_date') else None,
            planned_duration_hours=data.get('planned_duration_hours', 0.0),
            status=data.get('status', 'Not Started'),
            priority=data.get('priority', 'Medium'),
            dependencies=data.get('dependencies', []),
            estimated_cost=data.get('estimated_cost', 0.0),
            company_id=get_current_user().company_id
        )
        
        db.session.add(task)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': task.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@project_management_bp.route('/tasks/<int:task_id>/update-progress', methods=['PUT'])
@require_auth
def update_task_progress(task_id):
    """Update task progress"""
    try:
        task = ProjectTask.query.get_or_404(task_id)
        data = request.get_json()
        
        task.progress_percentage = data.get('progress_percentage', task.progress_percentage)
        task.actual_duration_hours = data.get('actual_duration_hours', task.actual_duration_hours)
        task.actual_cost = data.get('actual_cost', task.actual_cost)
        
        # Update status based on progress
        if task.progress_percentage >= 100:
            task.status = 'Completed'
            task.actual_end_date = date.today()
        elif task.progress_percentage > 0:
            task.status = 'In Progress'
            if not task.actual_start_date:
                task.actual_start_date = date.today()
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': task.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Project Resource Endpoints
@project_management_bp.route('/projects/<int:project_id>/resources', methods=['GET'])
@require_auth
def get_project_resources(project_id):
    """Get all resources for a project"""
    try:
        resources = ProjectResource.query.filter_by(
            project_id=project_id,
            company_id=get_current_user().company_id
        ).all()
        return jsonify({
            'success': True,
            'data': [resource.to_dict() for resource in resources]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@project_management_bp.route('/projects/<int:project_id>/resources', methods=['POST'])
@require_auth
def create_project_resource(project_id):
    """Create a new resource for a project"""
    try:
        data = request.get_json()
        resource = ProjectResource(
            resource_name=data['resource_name'],
            resource_type=data['resource_type'],
            resource_description=data.get('resource_description'),
            project_id=project_id,
            assigned_to_id=data.get('assigned_to_id'),
            allocation_percentage=data.get('allocation_percentage', 100.0),
            allocation_start_date=datetime.strptime(data['allocation_start_date'], '%Y-%m-%d').date() if data.get('allocation_start_date') else None,
            allocation_end_date=datetime.strptime(data['allocation_end_date'], '%Y-%m-%d').date() if data.get('allocation_end_date') else None,
            hourly_rate=data.get('hourly_rate', 0.0),
            currency=data.get('currency', 'USD'),
            is_active=data.get('is_active', True),
            is_available=data.get('is_available', True),
            company_id=get_current_user().company_id
        )
        
        db.session.add(resource)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': resource.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Project Risk Endpoints
@project_management_bp.route('/projects/<int:project_id>/risks', methods=['GET'])
@require_auth
def get_project_risks(project_id):
    """Get all risks for a project"""
    try:
        risks = ProjectRisk.query.filter_by(
            project_id=project_id,
            company_id=get_current_user().company_id
        ).all()
        return jsonify({
            'success': True,
            'data': [risk.to_dict() for risk in risks]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@project_management_bp.route('/projects/<int:project_id>/risks', methods=['POST'])
@require_auth
def create_project_risk(project_id):
    """Create a new risk for a project"""
    try:
        data = request.get_json()
        risk = ProjectRisk(
            risk_name=data['risk_name'],
            risk_description=data['risk_description'],
            risk_category=data.get('risk_category'),
            project_id=project_id,
            probability=data.get('probability', 0.0),
            impact=data.get('impact', 0.0),
            risk_level=data.get('risk_level', 'Medium'),
            mitigation_strategy=data.get('mitigation_strategy'),
            contingency_plan=data.get('contingency_plan'),
            risk_owner_id=data.get('risk_owner_id'),
            status=data.get('status', 'Open'),
            company_id=get_current_user().company_id
        )
        
        # Calculate risk score
        risk.risk_score = risk.probability * risk.impact / 100
        
        db.session.add(risk)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': risk.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Project Milestone Endpoints
@project_management_bp.route('/projects/<int:project_id>/milestones', methods=['GET'])
@require_auth
def get_project_milestones(project_id):
    """Get all milestones for a project"""
    try:
        milestones = ProjectMilestone.query.filter_by(
            project_id=project_id,
            company_id=get_current_user().company_id
        ).all()
        return jsonify({
            'success': True,
            'data': [milestone.to_dict() for milestone in milestones]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@project_management_bp.route('/projects/<int:project_id>/milestones', methods=['POST'])
@require_auth
def create_project_milestone(project_id):
    """Create a new milestone for a project"""
    try:
        data = request.get_json()
        milestone = ProjectMilestone(
            milestone_name=data['milestone_name'],
            milestone_description=data.get('milestone_description'),
            project_id=project_id,
            planned_date=datetime.strptime(data['planned_date'], '%Y-%m-%d').date(),
            deliverables=data.get('deliverables', []),
            company_id=get_current_user().company_id
        )
        
        db.session.add(milestone)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': milestone.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Project Template Endpoints
@project_management_bp.route('/templates', methods=['GET'])
@require_auth
def get_project_templates():
    """Get all project templates"""
    try:
        templates = ProjectTemplate.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [template.to_dict() for template in templates]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@project_management_bp.route('/templates', methods=['POST'])
@require_auth
def create_project_template():
    """Create a new project template"""
    try:
        data = request.get_json()
        template = ProjectTemplate(
            template_name=data['template_name'],
            template_description=data.get('template_description'),
            template_category=data.get('template_category'),
            template_config=data.get('template_config', {}),
            default_tasks=data.get('default_tasks', []),
            default_resources=data.get('default_resources', []),
            default_milestones=data.get('default_milestones', []),
            is_active=data.get('is_active', True),
            is_public=data.get('is_public', False),
            company_id=get_current_user().company_id
        )
        
        db.session.add(template)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': template.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@project_management_bp.route('/templates/<int:template_id>/create-project', methods=['POST'])
@require_auth
def create_project_from_template(template_id):
    """Create a new project from a template"""
    try:
        template = ProjectTemplate.query.get_or_404(template_id)
        data = request.get_json()
        
        # Create project from template
        project = Project(
            project_name=data['project_name'],
            project_code=f"PRJ-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            description=data.get('description'),
            project_type=data.get('project_type', 'Internal'),
            project_category=template.template_category,
            project_manager_id=data.get('project_manager_id'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            status='Planning',
            budget_allocated=data.get('budget_allocated', 0.0),
            currency=data.get('currency', 'USD'),
            company_id=get_current_user().company_id
        )
        
        db.session.add(project)
        db.session.flush()  # Get the project ID
        
        # Create tasks from template
        for task_data in template.default_tasks:
            task = ProjectTask(
                task_name=task_data['task_name'],
                task_description=task_data.get('task_description'),
                task_code=f"TSK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                project_id=project.id,
                planned_start_date=datetime.strptime(task_data['planned_start_date'], '%Y-%m-%d').date() if task_data.get('planned_start_date') else None,
                planned_end_date=datetime.strptime(task_data['planned_end_date'], '%Y-%m-%d').date() if task_data.get('planned_end_date') else None,
                planned_duration_hours=task_data.get('planned_duration_hours', 0.0),
                status='Not Started',
                priority=task_data.get('priority', 'Medium'),
                estimated_cost=task_data.get('estimated_cost', 0.0),
                company_id=get_current_user().company_id
            )
            db.session.add(task)
        
        # Create milestones from template
        for milestone_data in template.default_milestones:
            milestone = ProjectMilestone(
                milestone_name=milestone_data['milestone_name'],
                milestone_description=milestone_data.get('milestone_description'),
                project_id=project.id,
                planned_date=datetime.strptime(milestone_data['planned_date'], '%Y-%m-%d').date(),
                deliverables=milestone_data.get('deliverables', []),
                company_id=get_current_user().company_id
            )
            db.session.add(milestone)
        
        # Update template usage count
        template.usage_count += 1
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': project.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Analytics Endpoints
@project_management_bp.route('/analytics/project-summary', methods=['GET'])
@require_auth
def get_project_summary():
    """Get project summary analytics"""
    try:
        projects = Project.query.filter_by(company_id=get_current_user().company_id).all()
        
        # Calculate summary statistics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.status == 'Active'])
        completed_projects = len([p for p in projects if p.status == 'Completed'])
        on_hold_projects = len([p for p in projects if p.status == 'On Hold'])
        
        # Calculate budget statistics
        total_budget = sum(p.budget_allocated for p in projects)
        total_spent = sum(p.budget_spent for p in projects)
        budget_utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0
        
        # Calculate average project duration
        completed_projects_with_duration = [p for p in projects if p.status == 'Completed' and p.actual_duration_days > 0]
        avg_duration = sum(p.actual_duration_days for p in completed_projects_with_duration) / len(completed_projects_with_duration) if completed_projects_with_duration else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_projects': total_projects,
                'active_projects': active_projects,
                'completed_projects': completed_projects,
                'on_hold_projects': on_hold_projects,
                'total_budget': total_budget,
                'total_spent': total_spent,
                'budget_utilization': budget_utilization,
                'average_duration_days': avg_duration
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@project_management_bp.route('/analytics/resource-utilization', methods=['GET'])
@require_auth
def get_resource_utilization():
    """Get resource utilization analytics"""
    try:
        resources = ProjectResource.query.filter_by(company_id=get_current_user().company_id).all()
        
        utilization_data = []
        for resource in resources:
            # Calculate utilization percentage
            total_allocation = sum(r.allocation_percentage for r in resources if r.assigned_to_id == resource.assigned_to_id)
            utilization_data.append({
                'resource_id': resource.id,
                'resource_name': resource.resource_name,
                'assigned_to': resource.assigned_to.first_name + ' ' + resource.assigned_to.last_name if resource.assigned_to else 'Unassigned',
                'allocation_percentage': resource.allocation_percentage,
                'total_allocation': total_allocation,
                'is_overallocated': total_allocation > 100
            })
        
        return jsonify({
            'success': True,
            'data': utilization_data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@project_management_bp.route('/analytics/risk-analysis', methods=['GET'])
@require_auth
def get_risk_analysis():
    """Get project risk analysis"""
    try:
        risks = ProjectRisk.query.filter_by(company_id=get_current_user().company_id).all()
        
        # Group risks by level
        risk_distribution = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
        for risk in risks:
            risk_distribution[risk.risk_level.value] += 1
        
        # Get high-risk projects
        high_risk_projects = []
        for risk in risks:
            if risk.risk_level.value in ['High', 'Critical']:
                high_risk_projects.append({
                    'project_id': risk.project_id,
                    'project_name': risk.project.project_name,
                    'risk_name': risk.risk_name,
                    'risk_level': risk.risk_level.value,
                    'risk_score': risk.risk_score
                })
        
        return jsonify({
            'success': True,
            'data': {
                'risk_distribution': risk_distribution,
                'high_risk_projects': high_risk_projects,
                'total_risks': len(risks)
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
