# Workflow API - Complete Workflow Engine and Automation API
# Advanced workflow operations without Frappe dependencies

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import token_required, get_current_user
from .models import (
    Workflow, WorkflowStep, WorkflowExecution, WorkflowRule,
    WorkflowTrigger, WorkflowAction, WorkflowCondition, WorkflowTemplate
)
from datetime import datetime, date, timedelta
import json

workflow_api = Blueprint('workflow_api', __name__)

# Workflow Template Management
@workflow_api.route('/workflow-templates', methods=['GET'])
@token_required
def get_workflow_templates():
    """Get workflow templates"""
    try:
        company_id = request.args.get('company_id')
        category = request.args.get('category')
        is_public = request.args.get('is_public')
        is_featured = request.args.get('is_featured')
        
        query = WorkflowTemplate.query.filter_by(company_id=company_id)
        if category:
            query = query.filter_by(category=category)
        if is_public:
            query = query.filter_by(is_public=is_public.lower() == 'true')
        if is_featured:
            query = query.filter_by(is_featured=is_featured.lower() == 'true')
        
        templates = query.all()
        return jsonify({
            'success': True,
            'data': [template.to_dict() for template in templates]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_api.route('/workflow-templates', methods=['POST'])
@token_required
def create_workflow_template():
    """Create workflow template"""
    try:
        data = request.get_json()
        template = WorkflowTemplate(
            template_name=data['template_name'],
            template_code=data['template_code'],
            description=data.get('description'),
            category=data.get('category'),
            industry=data.get('industry'),
            complexity=data.get('complexity', 'Medium'),
            template_config=data.get('template_config', {}),
            is_public=data.get('is_public', False),
            is_featured=data.get('is_featured', False),
            company_id=data['company_id']
        )
        db.session.add(template)
        db.session.commit()
        return jsonify({'success': True, 'data': template.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Workflow Management
@workflow_api.route('/workflows', methods=['GET'])
@token_required
def get_workflows():
    """Get workflows"""
    try:
        company_id = request.args.get('company_id')
        workflow_type = request.args.get('workflow_type')
        status = request.args.get('status')
        is_active = request.args.get('is_active')
        
        query = Workflow.query.filter_by(company_id=company_id)
        if workflow_type:
            query = query.filter_by(workflow_type=workflow_type)
        if status:
            query = query.filter_by(status=status)
        if is_active:
            query = query.filter_by(is_active=is_active.lower() == 'true')
        
        workflows = query.all()
        return jsonify({
            'success': True,
            'data': [workflow.to_dict() for workflow in workflows]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_api.route('/workflows', methods=['POST'])
@token_required
def create_workflow():
    """Create workflow"""
    try:
        data = request.get_json()
        workflow = Workflow(
            workflow_name=data['workflow_name'],
            workflow_code=data['workflow_code'],
            description=data.get('description'),
            workflow_type=data.get('workflow_type'),
            template_id=data.get('template_id'),
            workflow_config=data.get('workflow_config', {}),
            is_active=data.get('is_active', True),
            is_public=data.get('is_public', False),
            max_execution_time=data.get('max_execution_time', 3600),
            retry_count=data.get('retry_count', 3),
            timeout_action=data.get('timeout_action', 'Cancel'),
            company_id=data['company_id']
        )
        db.session.add(workflow)
        db.session.commit()
        return jsonify({'success': True, 'data': workflow.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_api.route('/workflows/<int:workflow_id>', methods=['GET'])
@token_required
def get_workflow(workflow_id):
    """Get specific workflow"""
    try:
        workflow = Workflow.query.get_or_404(workflow_id)
        return jsonify({'success': True, 'data': workflow.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_api.route('/workflows/<int:workflow_id>/activate', methods=['POST'])
@token_required
def activate_workflow(workflow_id):
    """Activate workflow"""
    try:
        workflow = Workflow.query.get_or_404(workflow_id)
        workflow.status = 'Active'
        workflow.is_active = True
        db.session.commit()
        return jsonify({'success': True, 'data': workflow.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Workflow Step Management
@workflow_api.route('/workflows/<int:workflow_id>/steps', methods=['GET'])
@token_required
def get_workflow_steps(workflow_id):
    """Get workflow steps"""
    try:
        steps = WorkflowStep.query.filter_by(workflow_id=workflow_id).order_by(WorkflowStep.step_order).all()
        return jsonify({
            'success': True,
            'data': [step.to_dict() for step in steps]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_api.route('/workflows/<int:workflow_id>/steps', methods=['POST'])
@token_required
def create_workflow_step(workflow_id):
    """Create workflow step"""
    try:
        data = request.get_json()
        step = WorkflowStep(
            workflow_id=workflow_id,
            step_name=data['step_name'],
            step_code=data['step_code'],
            step_type=data['step_type'],
            description=data.get('description'),
            step_config=data.get('step_config', {}),
            step_order=data.get('step_order', 0),
            is_required=data.get('is_required', True),
            is_parallel=data.get('is_parallel', False),
            timeout_minutes=data.get('timeout_minutes', 0),
            assigned_to_id=data.get('assigned_to_id'),
            assigned_role=data.get('assigned_role'),
            company_id=data['company_id']
        )
        db.session.add(step)
        db.session.commit()
        return jsonify({'success': True, 'data': step.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Workflow Execution Management
@workflow_api.route('/workflow-executions', methods=['GET'])
@token_required
def get_workflow_executions():
    """Get workflow executions"""
    try:
        company_id = request.args.get('company_id')
        workflow_id = request.args.get('workflow_id')
        execution_status = request.args.get('execution_status')
        triggered_by_id = request.args.get('triggered_by_id')
        
        query = WorkflowExecution.query.filter_by(company_id=company_id)
        if workflow_id:
            query = query.filter_by(workflow_id=workflow_id)
        if execution_status:
            query = query.filter_by(execution_status=execution_status)
        if triggered_by_id:
            query = query.filter_by(triggered_by_id=triggered_by_id)
        
        executions = query.all()
        return jsonify({
            'success': True,
            'data': [execution.to_dict() for execution in executions]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_api.route('/workflow-executions', methods=['POST'])
@token_required
def create_workflow_execution():
    """Create workflow execution"""
    try:
        data = request.get_json()
        execution = WorkflowExecution(
            workflow_id=data['workflow_id'],
            execution_name=data['execution_name'],
            input_data=data.get('input_data', {}),
            triggered_by_id=data.get('triggered_by_id'),
            trigger_type=data.get('trigger_type'),
            trigger_data=data.get('trigger_data', {}),
            max_retries=data.get('max_retries', 3),
            company_id=data['company_id']
        )
        db.session.add(execution)
        db.session.commit()
        return jsonify({'success': True, 'data': execution.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_api.route('/workflow-executions/<int:execution_id>/start', methods=['POST'])
@token_required
def start_workflow_execution(execution_id):
    """Start workflow execution"""
    try:
        execution = WorkflowExecution.query.get_or_404(execution_id)
        execution.execution_status = 'Running'
        execution.start_time = datetime.now()
        db.session.commit()
        return jsonify({'success': True, 'data': execution.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_api.route('/workflow-executions/<int:execution_id>/complete', methods=['POST'])
@token_required
def complete_workflow_execution(execution_id):
    """Complete workflow execution"""
    try:
        data = request.get_json()
        execution = WorkflowExecution.query.get_or_404(execution_id)
        execution.execution_status = 'Completed'
        execution.end_time = datetime.now()
        execution.output_data = data.get('output_data', {})
        execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds() if execution.start_time else 0
        db.session.commit()
        return jsonify({'success': True, 'data': execution.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Workflow Rule Management
@workflow_api.route('/workflow-rules', methods=['GET'])
@token_required
def get_workflow_rules():
    """Get workflow rules"""
    try:
        company_id = request.args.get('company_id')
        workflow_id = request.args.get('workflow_id')
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        is_global = request.args.get('is_global')
        
        query = WorkflowRule.query.filter_by(company_id=company_id)
        if workflow_id:
            query = query.filter_by(workflow_id=workflow_id)
        if is_active:
            query = query.filter_by(is_active=True)
        if is_global:
            query = query.filter_by(is_global=is_global.lower() == 'true')
        
        rules = query.all()
        return jsonify({
            'success': True,
            'data': [rule.to_dict() for rule in rules]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_api.route('/workflow-rules', methods=['POST'])
@token_required
def create_workflow_rule():
    """Create workflow rule"""
    try:
        data = request.get_json()
        rule = WorkflowRule(
            workflow_id=data['workflow_id'],
            rule_name=data['rule_name'],
            rule_description=data.get('rule_description'),
            rule_conditions=data.get('rule_conditions', {}),
            rule_actions=data.get('rule_actions', {}),
            rule_priority=data.get('rule_priority', 0),
            is_active=data.get('is_active', True),
            is_global=data.get('is_global', False),
            company_id=data['company_id']
        )
        db.session.add(rule)
        db.session.commit()
        return jsonify({'success': True, 'data': rule.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Workflow Trigger Management
@workflow_api.route('/workflow-triggers', methods=['GET'])
@token_required
def get_workflow_triggers():
    """Get workflow triggers"""
    try:
        company_id = request.args.get('company_id')
        workflow_id = request.args.get('workflow_id')
        trigger_type = request.args.get('trigger_type')
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        
        query = WorkflowTrigger.query.filter_by(company_id=company_id)
        if workflow_id:
            query = query.filter_by(workflow_id=workflow_id)
        if trigger_type:
            query = query.filter_by(trigger_type=trigger_type)
        if is_active:
            query = query.filter_by(is_active=True)
        
        triggers = query.all()
        return jsonify({
            'success': True,
            'data': [trigger.to_dict() for trigger in triggers]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_api.route('/workflow-triggers', methods=['POST'])
@token_required
def create_workflow_trigger():
    """Create workflow trigger"""
    try:
        data = request.get_json()
        trigger = WorkflowTrigger(
            workflow_id=data['workflow_id'],
            trigger_name=data['trigger_name'],
            trigger_type=data['trigger_type'],
            trigger_description=data.get('trigger_description'),
            trigger_config=data.get('trigger_config', {}),
            trigger_conditions=data.get('trigger_conditions', {}),
            is_active=data.get('is_active', True),
            is_recurring=data.get('is_recurring', False),
            recurrence_pattern=data.get('recurrence_pattern'),
            company_id=data['company_id']
        )
        db.session.add(trigger)
        db.session.commit()
        return jsonify({'success': True, 'data': trigger.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Workflow Action Management
@workflow_api.route('/workflow-actions', methods=['GET'])
@token_required
def get_workflow_actions():
    """Get workflow actions"""
    try:
        company_id = request.args.get('company_id')
        step_id = request.args.get('step_id')
        action_type = request.args.get('action_type')
        
        query = WorkflowAction.query.filter_by(company_id=company_id)
        if step_id:
            query = query.filter_by(step_id=step_id)
        if action_type:
            query = query.filter_by(action_type=action_type)
        
        actions = query.all()
        return jsonify({
            'success': True,
            'data': [action.to_dict() for action in actions]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_api.route('/workflow-actions', methods=['POST'])
@token_required
def create_workflow_action():
    """Create workflow action"""
    try:
        data = request.get_json()
        action = WorkflowAction(
            step_id=data['step_id'],
            action_name=data['action_name'],
            action_type=data['action_type'],
            action_description=data.get('action_description'),
            action_config=data.get('action_config', {}),
            action_order=data.get('action_order', 0),
            is_required=data.get('is_required', True),
            is_conditional=data.get('is_conditional', False),
            condition_expression=data.get('condition_expression'),
            company_id=data['company_id']
        )
        db.session.add(action)
        db.session.commit()
        return jsonify({'success': True, 'data': action.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Workflow Condition Management
@workflow_api.route('/workflow-conditions', methods=['GET'])
@token_required
def get_workflow_conditions():
    """Get workflow conditions"""
    try:
        company_id = request.args.get('company_id')
        step_id = request.args.get('step_id')
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        
        query = WorkflowCondition.query.filter_by(company_id=company_id)
        if step_id:
            query = query.filter_by(step_id=step_id)
        if is_active:
            query = query.filter_by(is_active=True)
        
        conditions = query.all()
        return jsonify({
            'success': True,
            'data': [condition.to_dict() for condition in conditions]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_api.route('/workflow-conditions', methods=['POST'])
@token_required
def create_workflow_condition():
    """Create workflow condition"""
    try:
        data = request.get_json()
        condition = WorkflowCondition(
            step_id=data['step_id'],
            condition_name=data['condition_name'],
            condition_expression=data['condition_expression'],
            condition_description=data.get('condition_description'),
            condition_config=data.get('condition_config', {}),
            condition_order=data.get('condition_order', 0),
            is_active=data.get('is_active', True),
            is_required=data.get('is_required', True),
            company_id=data['company_id']
        )
        db.session.add(condition)
        db.session.commit()
        return jsonify({'success': True, 'data': condition.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Workflow Analytics
@workflow_api.route('/workflow-analytics', methods=['GET'])
@token_required
def get_workflow_analytics():
    """Get workflow analytics"""
    try:
        company_id = request.args.get('company_id')
        
        # Calculate analytics
        total_workflows = Workflow.query.filter_by(company_id=company_id).count()
        active_workflows = Workflow.query.filter_by(company_id=company_id, is_active=True).count()
        total_executions = WorkflowExecution.query.filter_by(company_id=company_id).count()
        completed_executions = WorkflowExecution.query.filter_by(company_id=company_id, execution_status='Completed').count()
        failed_executions = WorkflowExecution.query.filter_by(company_id=company_id, execution_status='Failed').count()
        running_executions = WorkflowExecution.query.filter_by(company_id=company_id, execution_status='Running').count()
        
        analytics = {
            'total_workflows': total_workflows,
            'active_workflows': active_workflows,
            'total_executions': total_executions,
            'completed_executions': completed_executions,
            'failed_executions': failed_executions,
            'running_executions': running_executions,
            'success_rate': (completed_executions / total_executions * 100) if total_executions > 0 else 0,
            'failure_rate': (failed_executions / total_executions * 100) if total_executions > 0 else 0
        }
        
        return jsonify({'success': True, 'data': analytics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
