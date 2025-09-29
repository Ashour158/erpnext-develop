# Workflow Automation API
# API endpoints for smart workflows and conditional logic for automated business processes

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from .models import (
    WorkflowTemplate, Workflow, WorkflowStep, WorkflowExecution, WorkflowStepExecution,
    WorkflowCondition, WorkflowAction, WorkflowNotification, WorkflowApproval,
    WorkflowStatus, WorkflowTrigger, WorkflowStepType, WorkflowExecutionStatus
)
from datetime import datetime, timedelta, date
import json

workflow_automation_bp = Blueprint('workflow_automation', __name__)

# Workflow Templates
@workflow_automation_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_workflow_templates():
    """Get workflow templates"""
    try:
        company_id = request.args.get('company_id', type=int)
        category = request.args.get('category')
        is_public = request.args.get('is_public', type=bool)
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = WorkflowTemplate.query.filter(WorkflowTemplate.company_id == company_id)
        
        if category:
            query = query.filter(WorkflowTemplate.category == category)
        
        if is_public is not None:
            query = query.filter(WorkflowTemplate.is_public == is_public)
        
        if is_active is not None:
            query = query.filter(WorkflowTemplate.is_active == is_active)
        
        templates = query.order_by(WorkflowTemplate.usage_count.desc()).all()
        
        return jsonify([template.to_dict() for template in templates])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_automation_bp.route('/templates', methods=['POST'])
@jwt_required()
def create_workflow_template():
    """Create workflow template"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['template_name', 'category', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create template
        template = WorkflowTemplate(
            template_name=data['template_name'],
            template_description=data.get('template_description'),
            category=data['category'],
            is_public=data.get('is_public', False),
            is_active=data.get('is_active', True),
            template_config=data.get('template_config'),
            workflow_steps=data.get('workflow_steps'),
            variables=data.get('variables'),
            conditions=data.get('conditions'),
            company_id=data['company_id']
        )
        
        db.session.add(template)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('workflow_template_created', template.to_dict(), data['company_id'])
        
        return jsonify(template.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Workflows
@workflow_automation_bp.route('/workflows', methods=['GET'])
@jwt_required()
def get_workflows():
    """Get workflows"""
    try:
        company_id = request.args.get('company_id', type=int)
        status = request.args.get('status')
        trigger_type = request.args.get('trigger_type')
        is_public = request.args.get('is_public', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = Workflow.query.filter(Workflow.company_id == company_id)
        
        if status:
            query = query.filter(Workflow.status == WorkflowStatus(status))
        
        if trigger_type:
            query = query.filter(Workflow.trigger_type == WorkflowTrigger(trigger_type))
        
        if is_public is not None:
            query = query.filter(Workflow.is_public == is_public)
        
        workflows = query.order_by(Workflow.created_at.desc()).all()
        
        return jsonify([workflow.to_dict() for workflow in workflows])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_automation_bp.route('/workflows', methods=['POST'])
@jwt_required()
def create_workflow():
    """Create workflow"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['workflow_name', 'trigger_type', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create workflow
        workflow = Workflow(
            workflow_name=data['workflow_name'],
            workflow_description=data.get('workflow_description'),
            status=WorkflowStatus(data.get('status', 'DRAFT')),
            trigger_type=WorkflowTrigger(data['trigger_type']),
            trigger_config=data.get('trigger_config'),
            workflow_steps=data.get('workflow_steps'),
            variables=data.get('variables'),
            conditions=data.get('conditions'),
            max_execution_time=data.get('max_execution_time', 3600),
            retry_count=data.get('retry_count', 3),
            retry_delay=data.get('retry_delay', 300),
            timeout_action=data.get('timeout_action', 'Cancel'),
            allowed_users=data.get('allowed_users'),
            allowed_roles=data.get('allowed_roles'),
            is_public=data.get('is_public', False),
            company_id=data['company_id']
        )
        
        db.session.add(workflow)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('workflow_created', workflow.to_dict(), data['company_id'])
        
        return jsonify(workflow.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@workflow_automation_bp.route('/workflows/<int:workflow_id>', methods=['GET'])
@jwt_required()
def get_workflow(workflow_id):
    """Get specific workflow"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        workflow = Workflow.query.filter(
            Workflow.id == workflow_id,
            Workflow.company_id == company_id
        ).first()
        
        if not workflow:
            return jsonify({'error': 'Workflow not found'}), 404
        
        return jsonify(workflow.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_automation_bp.route('/workflows/<int:workflow_id>', methods=['PUT'])
@jwt_required()
def update_workflow(workflow_id):
    """Update workflow"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        workflow = Workflow.query.filter(
            Workflow.id == workflow_id,
            Workflow.company_id == data.get('company_id')
        ).first()
        
        if not workflow:
            return jsonify({'error': 'Workflow not found'}), 404
        
        # Update fields
        for field in ['workflow_name', 'workflow_description', 'trigger_config',
                     'workflow_steps', 'variables', 'conditions', 'max_execution_time',
                     'retry_count', 'retry_delay', 'timeout_action', 'allowed_users',
                     'allowed_roles', 'is_public']:
            if field in data:
                setattr(workflow, field, data[field])
        
        if 'status' in data:
            workflow.status = WorkflowStatus(data['status'])
        
        if 'trigger_type' in data:
            workflow.trigger_type = WorkflowTrigger(data['trigger_type'])
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('workflow_updated', workflow.to_dict(), workflow.company_id)
        
        return jsonify(workflow.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Workflow Executions
@workflow_automation_bp.route('/executions', methods=['GET'])
@jwt_required()
def get_workflow_executions():
    """Get workflow executions"""
    try:
        company_id = request.args.get('company_id', type=int)
        workflow_id = request.args.get('workflow_id', type=int)
        execution_status = request.args.get('execution_status')
        triggered_by = request.args.get('triggered_by', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = WorkflowExecution.query.filter(WorkflowExecution.company_id == company_id)
        
        if workflow_id:
            query = query.filter(WorkflowExecution.workflow_id == workflow_id)
        
        if execution_status:
            query = query.filter(WorkflowExecution.execution_status == WorkflowExecutionStatus(execution_status))
        
        if triggered_by:
            query = query.filter(WorkflowExecution.triggered_by == triggered_by)
        
        if start_date:
            query = query.filter(WorkflowExecution.started_at >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(WorkflowExecution.started_at <= datetime.fromisoformat(end_date))
        
        executions = query.order_by(WorkflowExecution.started_at.desc()).limit(100).all()
        
        return jsonify([execution.to_dict() for execution in executions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_automation_bp.route('/executions', methods=['POST'])
@jwt_required()
def create_workflow_execution():
    """Create workflow execution"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['execution_name', 'workflow_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create execution
        execution = WorkflowExecution(
            execution_name=data['execution_name'],
            execution_status=WorkflowExecutionStatus(data.get('execution_status', 'PENDING')),
            workflow_id=data['workflow_id'],
            input_data=data.get('input_data'),
            output_data=data.get('output_data'),
            execution_log=data.get('execution_log'),
            error_message=data.get('error_message'),
            triggered_by=data.get('triggered_by', user_id),
            company_id=data['company_id']
        )
        
        db.session.add(execution)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('workflow_execution_created', execution.to_dict(), data['company_id'])
        
        return jsonify(execution.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@workflow_automation_bp.route('/executions/<int:execution_id>/start', methods=['POST'])
@jwt_required()
def start_workflow_execution(execution_id):
    """Start workflow execution"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        execution = WorkflowExecution.query.filter(
            WorkflowExecution.id == execution_id,
            WorkflowExecution.company_id == data.get('company_id')
        ).first()
        
        if not execution:
            return jsonify({'error': 'Workflow execution not found'}), 404
        
        # Update execution status
        execution.execution_status = WorkflowExecutionStatus.RUNNING
        execution.started_at = datetime.utcnow()
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('workflow_execution_started', execution.to_dict(), execution.company_id)
        
        return jsonify(execution.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@workflow_automation_bp.route('/executions/<int:execution_id>/complete', methods=['POST'])
@jwt_required()
def complete_workflow_execution(execution_id):
    """Complete workflow execution"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        execution = WorkflowExecution.query.filter(
            WorkflowExecution.id == execution_id,
            WorkflowExecution.company_id == data.get('company_id')
        ).first()
        
        if not execution:
            return jsonify({'error': 'Workflow execution not found'}), 404
        
        # Update execution status
        execution.execution_status = WorkflowExecutionStatus.COMPLETED
        execution.completed_at = datetime.utcnow()
        execution.execution_duration = (execution.completed_at - execution.started_at).total_seconds()
        
        if 'output_data' in data:
            execution.output_data = data['output_data']
        
        if 'execution_log' in data:
            execution.execution_log = data['execution_log']
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('workflow_execution_completed', execution.to_dict(), execution.company_id)
        
        return jsonify(execution.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Workflow Steps
@workflow_automation_bp.route('/workflows/<int:workflow_id>/steps', methods=['GET'])
@jwt_required()
def get_workflow_steps(workflow_id):
    """Get workflow steps"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        steps = WorkflowStep.query.filter(
            WorkflowStep.workflow_id == workflow_id,
            WorkflowStep.company_id == company_id
        ).order_by(WorkflowStep.step_order).all()
        
        return jsonify([step.to_dict() for step in steps])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_automation_bp.route('/workflows/<int:workflow_id>/steps', methods=['POST'])
@jwt_required()
def create_workflow_step(workflow_id):
    """Create workflow step"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['step_name', 'step_type', 'step_order', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create step
        step = WorkflowStep(
            step_name=data['step_name'],
            step_description=data.get('step_description'),
            step_type=WorkflowStepType(data['step_type']),
            step_order=data['step_order'],
            step_config=data.get('step_config'),
            conditions=data.get('conditions'),
            actions=data.get('actions'),
            parameters=data.get('parameters'),
            workflow_id=workflow_id,
            company_id=data['company_id']
        )
        
        db.session.add(step)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('workflow_step_created', step.to_dict(), data['company_id'])
        
        return jsonify(step.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Workflow Notifications
@workflow_automation_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_workflow_notifications():
    """Get workflow notifications"""
    try:
        company_id = request.args.get('company_id', type=int)
        workflow_id = request.args.get('workflow_id', type=int)
        workflow_execution_id = request.args.get('workflow_execution_id', type=int)
        is_sent = request.args.get('is_sent', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = WorkflowNotification.query.filter(WorkflowNotification.company_id == company_id)
        
        if workflow_id:
            query = query.filter(WorkflowNotification.workflow_id == workflow_id)
        
        if workflow_execution_id:
            query = query.filter(WorkflowNotification.workflow_execution_id == workflow_execution_id)
        
        if is_sent is not None:
            query = query.filter(WorkflowNotification.is_sent == is_sent)
        
        notifications = query.order_by(WorkflowNotification.created_at.desc()).all()
        
        return jsonify([notification.to_dict() for notification in notifications])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_automation_bp.route('/notifications', methods=['POST'])
@jwt_required()
def create_workflow_notification():
    """Create workflow notification"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['notification_title', 'notification_message', 'workflow_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create notification
        notification = WorkflowNotification(
            notification_title=data['notification_title'],
            notification_message=data['notification_message'],
            notification_type=data.get('notification_type', 'Info'),
            workflow_id=data['workflow_id'],
            workflow_execution_id=data.get('workflow_execution_id'),
            recipient_users=data.get('recipient_users'),
            recipient_roles=data.get('recipient_roles'),
            recipient_emails=data.get('recipient_emails'),
            delivery_method=data.get('delivery_method', 'Email'),
            is_sent=data.get('is_sent', False),
            sent_at=datetime.fromisoformat(data['sent_at']) if data.get('sent_at') else None,
            company_id=data['company_id']
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('workflow_notification_created', notification.to_dict(), data['company_id'])
        
        return jsonify(notification.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Workflow Approvals
@workflow_automation_bp.route('/approvals', methods=['GET'])
@jwt_required()
def get_workflow_approvals():
    """Get workflow approvals"""
    try:
        company_id = request.args.get('company_id', type=int)
        workflow_id = request.args.get('workflow_id', type=int)
        workflow_execution_id = request.args.get('workflow_execution_id', type=int)
        approval_status = request.args.get('approval_status')
        approver_user_id = request.args.get('approver_user_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = WorkflowApproval.query.filter(WorkflowApproval.company_id == company_id)
        
        if workflow_id:
            query = query.filter(WorkflowApproval.workflow_id == workflow_id)
        
        if workflow_execution_id:
            query = query.filter(WorkflowApproval.workflow_execution_id == workflow_execution_id)
        
        if approval_status:
            query = query.filter(WorkflowApproval.approval_status == approval_status)
        
        if approver_user_id:
            query = query.filter(WorkflowApproval.approved_by == approver_user_id)
        
        approvals = query.order_by(WorkflowApproval.created_at.desc()).all()
        
        return jsonify([approval.to_dict() for approval in approvals])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_automation_bp.route('/approvals', methods=['POST'])
@jwt_required()
def create_workflow_approval():
    """Create workflow approval"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['approval_title', 'approval_type', 'workflow_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create approval
        approval = WorkflowApproval(
            approval_title=data['approval_title'],
            approval_description=data.get('approval_description'),
            approval_type=data['approval_type'],
            workflow_id=data['workflow_id'],
            workflow_execution_id=data.get('workflow_execution_id'),
            approver_users=data.get('approver_users'),
            approver_roles=data.get('approver_roles'),
            required_approvals=data.get('required_approvals', 1),
            approval_status=data.get('approval_status', 'Pending'),
            approved_by=data.get('approved_by'),
            approved_at=datetime.fromisoformat(data['approved_at']) if data.get('approved_at') else None,
            approval_notes=data.get('approval_notes'),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            is_expired=data.get('is_expired', False),
            company_id=data['company_id']
        )
        
        db.session.add(approval)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('workflow_approval_created', approval.to_dict(), data['company_id'])
        
        return jsonify(approval.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@workflow_automation_bp.route('/approvals/<int:approval_id>/approve', methods=['POST'])
@jwt_required()
def approve_workflow_approval(approval_id):
    """Approve workflow approval"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        approval = WorkflowApproval.query.filter(
            WorkflowApproval.id == approval_id,
            WorkflowApproval.company_id == data.get('company_id')
        ).first()
        
        if not approval:
            return jsonify({'error': 'Workflow approval not found'}), 404
        
        # Update approval status
        approval.approval_status = 'Approved'
        approval.approved_by = user_id
        approval.approved_at = datetime.utcnow()
        approval.approval_notes = data.get('approval_notes')
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('workflow_approval_approved', approval.to_dict(), approval.company_id)
        
        return jsonify(approval.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@workflow_automation_bp.route('/approvals/<int:approval_id>/reject', methods=['POST'])
@jwt_required()
def reject_workflow_approval(approval_id):
    """Reject workflow approval"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        approval = WorkflowApproval.query.filter(
            WorkflowApproval.id == approval_id,
            WorkflowApproval.company_id == data.get('company_id')
        ).first()
        
        if not approval:
            return jsonify({'error': 'Workflow approval not found'}), 404
        
        # Update approval status
        approval.approval_status = 'Rejected'
        approval.approved_by = user_id
        approval.approved_at = datetime.utcnow()
        approval.approval_notes = data.get('approval_notes')
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('workflow_approval_rejected', approval.to_dict(), approval.company_id)
        
        return jsonify(approval.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
