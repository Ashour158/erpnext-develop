# Vigilance System API
# API endpoints for supply chain vigilance and corrective actions

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from .vigilance_system import (
    EnhancedVigilanceRecord, CorrectiveAction, PreventiveAction, VigilanceAttachment,
    VigilanceAlert, VigilanceMetric, VigilanceDashboard, VigilanceReport, VigilanceWorkflow,
    VigilanceWorkflowInstance, VigilanceType, VigilanceStatus, CorrectiveActionStatus,
    PreventiveActionStatus
)
from datetime import datetime, date, timedelta
import json
import os
from werkzeug.utils import secure_filename

vigilance_bp = Blueprint('vigilance', __name__)

# Vigilance Records Management
@vigilance_bp.route('/records', methods=['GET'])
@jwt_required()
def get_vigilance_records():
    """Get vigilance records with comprehensive filtering"""
    try:
        company_id = request.args.get('company_id', type=int)
        item_id = request.args.get('item_id', type=int)
        batch_id = request.args.get('batch_id', type=int)
        lot_id = request.args.get('lot_id', type=int)
        supplier_id = request.args.get('supplier_id', type=int)
        vigilance_type = request.args.get('vigilance_type')
        vigilance_level = request.args.get('vigilance_level')
        status = request.args.get('status')
        priority = request.args.get('priority')
        assigned_to = request.args.get('assigned_to', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = EnhancedVigilanceRecord.query.filter(EnhancedVigilanceRecord.company_id == company_id)
        
        if item_id:
            query = query.filter(EnhancedVigilanceRecord.item_id == item_id)
        
        if batch_id:
            query = query.filter(EnhancedVigilanceRecord.batch_id == batch_id)
        
        if lot_id:
            query = query.filter(EnhancedVigilanceRecord.lot_id == lot_id)
        
        if supplier_id:
            query = query.filter(EnhancedVigilanceRecord.supplier_id == supplier_id)
        
        if vigilance_type:
            query = query.filter(EnhancedVigilanceRecord.vigilance_type == VigilanceType(vigilance_type))
        
        if vigilance_level:
            query = query.filter(EnhancedVigilanceRecord.vigilance_level == vigilance_level)
        
        if status:
            query = query.filter(EnhancedVigilanceRecord.status == VigilanceStatus(status))
        
        if priority:
            query = query.filter(EnhancedVigilanceRecord.priority == priority)
        
        if assigned_to:
            query = query.filter(EnhancedVigilanceRecord.assigned_to == assigned_to)
        
        if start_date:
            query = query.filter(EnhancedVigilanceRecord.detected_date >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(EnhancedVigilanceRecord.detected_date <= datetime.fromisoformat(end_date))
        
        records = query.order_by(EnhancedVigilanceRecord.detected_date.desc()).all()
        
        return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vigilance_bp.route('/records', methods=['POST'])
@jwt_required()
def create_vigilance_record():
    """Create vigilance record"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['vigilance_type', 'vigilance_level', 'title', 'description', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate record number
        record_number = f"VR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create vigilance record
        record = EnhancedVigilanceRecord(
            record_number=record_number,
            item_id=data.get('item_id'),
            batch_id=data.get('batch_id'),
            lot_id=data.get('lot_id'),
            supplier_id=data.get('supplier_id'),
            customer_id=data.get('customer_id'),
            vigilance_type=VigilanceType(data['vigilance_type']),
            vigilance_level=data['vigilance_level'],
            title=data['title'],
            description=data['description'],
            impact_assessment=data.get('impact_assessment'),
            risk_level=data.get('risk_level'),
            detected_by=user_id,
            detection_method=data.get('detection_method'),
            detection_location=data.get('detection_location'),
            status=VigilanceStatus(data.get('status', 'open')),
            assigned_to=data.get('assigned_to'),
            assigned_date=datetime.utcnow() if data.get('assigned_to') else None,
            priority=data.get('priority', 'medium'),
            created_by=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(record)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('vigilance_record_created', record.to_dict(), data['company_id'])
        
        return jsonify(record.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vigilance_bp.route('/records/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_vigilance_record(record_id):
    """Update vigilance record"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        record = EnhancedVigilanceRecord.query.filter_by(id=record_id).first()
        if not record:
            return jsonify({'error': 'Vigilance record not found'}), 404
        
        # Update record fields
        for key, value in data.items():
            if hasattr(record, key) and key not in ['id', 'created_at', 'created_by']:
                if key in ['vigilance_type', 'status']:
                    setattr(record, key, getattr(VigilanceType if key == 'vigilance_type' else VigilanceStatus, value))
                else:
                    setattr(record, key, value)
        
        record.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('vigilance_record_updated', record.to_dict(), record.company_id)
        
        return jsonify(record.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Corrective Actions Management
@vigilance_bp.route('/records/<int:record_id>/corrective-actions', methods=['POST'])
@jwt_required()
def create_corrective_action(record_id):
    """Create corrective action for vigilance record"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate action number
        action_number = f"CA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create corrective action
        action = CorrectiveAction(
            vigilance_record_id=record_id,
            action_number=action_number,
            title=data['title'],
            description=data['description'],
            action_type=data.get('action_type', 'immediate'),
            status=CorrectiveActionStatus(data.get('status', 'pending')),
            assigned_to=data.get('assigned_to'),
            assigned_date=datetime.utcnow() if data.get('assigned_to') else None,
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            implementation_notes=data.get('implementation_notes'),
            resources_required=data.get('resources_required'),
            cost_estimate=data.get('cost_estimate'),
            verification_required=data.get('verification_required', True),
            created_by=user_id,
            company_id=data.get('company_id')
        )
        
        db.session.add(action)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('corrective_action_created', action.to_dict(), data.get('company_id'))
        
        return jsonify(action.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vigilance_bp.route('/corrective-actions/<int:action_id>/complete', methods=['POST'])
@jwt_required()
def complete_corrective_action(action_id):
    """Mark corrective action as completed"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        action = CorrectiveAction.query.filter_by(id=action_id).first()
        if not action:
            return jsonify({'error': 'Corrective action not found'}), 404
        
        # Update action status
        action.status = CorrectiveActionStatus.COMPLETED
        action.completed_date = datetime.utcnow()
        action.implementation_notes = data.get('implementation_notes', action.implementation_notes)
        action.actual_cost = data.get('actual_cost', action.actual_cost)
        action.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('corrective_action_completed', action.to_dict(), action.company_id)
        
        return jsonify(action.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Preventive Actions Management
@vigilance_bp.route('/records/<int:record_id>/preventive-actions', methods=['POST'])
@jwt_required()
def create_preventive_action(record_id):
    """Create preventive action for vigilance record"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate action number
        action_number = f"PA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create preventive action
        action = PreventiveAction(
            vigilance_record_id=record_id,
            action_number=action_number,
            title=data['title'],
            description=data['description'],
            action_type=data.get('action_type', 'process_improvement'),
            status=PreventiveActionStatus(data.get('status', 'pending')),
            assigned_to=data.get('assigned_to'),
            assigned_date=datetime.utcnow() if data.get('assigned_to') else None,
            implementation_date=datetime.fromisoformat(data['implementation_date']) if data.get('implementation_date') else None,
            implementation_notes=data.get('implementation_notes'),
            resources_required=data.get('resources_required'),
            cost_estimate=data.get('cost_estimate'),
            monitoring_required=data.get('monitoring_required', True),
            monitoring_period_days=data.get('monitoring_period_days', 90),
            monitoring_frequency=data.get('monitoring_frequency', 'weekly'),
            created_by=user_id,
            company_id=data.get('company_id')
        )
        
        db.session.add(action)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('preventive_action_created', action.to_dict(), data.get('company_id'))
        
        return jsonify(action.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Vigilance Alerts
@vigilance_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_vigilance_alerts():
    """Get vigilance alerts"""
    try:
        company_id = request.args.get('company_id', type=int)
        alert_type = request.args.get('alert_type')
        alert_level = request.args.get('alert_level')
        is_active = request.args.get('is_active', type=bool)
        is_sent = request.args.get('is_sent', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = VigilanceAlert.query.filter(VigilanceAlert.company_id == company_id)
        
        if alert_type:
            query = query.filter(VigilanceAlert.alert_type == alert_type)
        
        if alert_level:
            query = query.filter(VigilanceAlert.alert_level == alert_level)
        
        if is_active is not None:
            query = query.filter(VigilanceAlert.is_active == is_active)
        
        if is_sent is not None:
            query = query.filter(VigilanceAlert.is_sent == is_sent)
        
        alerts = query.order_by(VigilanceAlert.created_at.desc()).all()
        
        return jsonify([alert.to_dict() for alert in alerts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vigilance_bp.route('/alerts', methods=['POST'])
@jwt_required()
def create_vigilance_alert():
    """Create vigilance alert"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['alert_type', 'title', 'message', 'alert_level', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create alert
        alert = VigilanceAlert(
            alert_type=data['alert_type'],
            title=data['title'],
            message=data['message'],
            alert_level=data['alert_level'],
            item_id=data.get('item_id'),
            batch_id=data.get('batch_id'),
            lot_id=data.get('lot_id'),
            vigilance_record_id=data.get('vigilance_record_id'),
            is_active=data.get('is_active', True),
            recipients=data.get('recipients', []),
            company_id=data['company_id']
        )
        
        db.session.add(alert)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('vigilance_alert_created', alert.to_dict(), data['company_id'])
        
        return jsonify(alert.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Vigilance Metrics
@vigilance_bp.route('/metrics', methods=['GET'])
@jwt_required()
def get_vigilance_metrics():
    """Get vigilance metrics"""
    try:
        company_id = request.args.get('company_id', type=int)
        metric_name = request.args.get('metric_name')
        metric_type = request.args.get('metric_type')
        period_type = request.args.get('period_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = VigilanceMetric.query.filter(VigilanceMetric.company_id == company_id)
        
        if metric_name:
            query = query.filter(VigilanceMetric.metric_name == metric_name)
        
        if metric_type:
            query = query.filter(VigilanceMetric.metric_type == metric_type)
        
        if period_type:
            query = query.filter(VigilanceMetric.period_type == period_type)
        
        if start_date:
            query = query.filter(VigilanceMetric.period_start >= datetime.fromisoformat(start_date).date())
        
        if end_date:
            query = query.filter(VigilanceMetric.period_end <= datetime.fromisoformat(end_date).date())
        
        metrics = query.order_by(VigilanceMetric.calculated_at.desc()).all()
        
        return jsonify([metric.to_dict() for metric in metrics])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vigilance_bp.route('/metrics/calculate', methods=['POST'])
@jwt_required()
def calculate_vigilance_metrics():
    """Calculate vigilance metrics"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['company_id', 'period_start', 'period_end']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        start_date = datetime.fromisoformat(data['period_start']).date()
        end_date = datetime.fromisoformat(data['period_end']).date()
        company_id = data['company_id']
        
        # Calculate various metrics
        metrics = []
        
        # Total vigilance records
        total_records = EnhancedVigilanceRecord.query.filter(
            EnhancedVigilanceRecord.company_id == company_id,
            EnhancedVigilanceRecord.detected_date >= start_date,
            EnhancedVigilanceRecord.detected_date <= end_date
        ).count()
        
        metrics.append(VigilanceMetric(
            metric_name='total_vigilance_records',
            metric_type='count',
            metric_value=total_records,
            period_start=start_date,
            period_end=end_date,
            period_type=data.get('period_type', 'custom'),
            company_id=company_id
        ))
        
        # Records by type
        for vigilance_type in VigilanceType:
            count = EnhancedVigilanceRecord.query.filter(
                EnhancedVigilanceRecord.company_id == company_id,
                EnhancedVigilanceRecord.vigilance_type == vigilance_type,
                EnhancedVigilanceRecord.detected_date >= start_date,
                EnhancedVigilanceRecord.detected_date <= end_date
            ).count()
            
            if count > 0:
                metrics.append(VigilanceMetric(
                    metric_name=f'records_by_type_{vigilance_type.value}',
                    metric_type='count',
                    metric_value=count,
                    period_start=start_date,
                    period_end=end_date,
                    period_type=data.get('period_type', 'custom'),
                    vigilance_type=vigilance_type,
                    company_id=company_id
                ))
        
        # Records by status
        for status in VigilanceStatus:
            count = EnhancedVigilanceRecord.query.filter(
                EnhancedVigilanceRecord.company_id == company_id,
                EnhancedVigilanceRecord.status == status,
                EnhancedVigilanceRecord.detected_date >= start_date,
                EnhancedVigilanceRecord.detected_date <= end_date
            ).count()
            
            if count > 0:
                metrics.append(VigilanceMetric(
                    metric_name=f'records_by_status_{status.value}',
                    metric_type='count',
                    metric_value=count,
                    period_start=start_date,
                    period_end=end_date,
                    period_type=data.get('period_type', 'custom'),
                    company_id=company_id
                ))
        
        # Add all metrics to database
        for metric in metrics:
            db.session.add(metric)
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('vigilance_metrics_calculated', [m.to_dict() for m in metrics], company_id)
        
        return jsonify([metric.to_dict() for metric in metrics])
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Vigilance Reports
@vigilance_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_vigilance_reports():
    """Get vigilance reports"""
    try:
        company_id = request.args.get('company_id', type=int)
        report_type = request.args.get('report_type')
        report_period = request.args.get('report_period')
        generated_by = request.args.get('generated_by', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = VigilanceReport.query.filter(VigilanceReport.company_id == company_id)
        
        if report_type:
            query = query.filter(VigilanceReport.report_type == report_type)
        
        if report_period:
            query = query.filter(VigilanceReport.report_period == report_period)
        
        if generated_by:
            query = query.filter(VigilanceReport.generated_by == generated_by)
        
        reports = query.order_by(VigilanceReport.generated_at.desc()).all()
        
        return jsonify([report.to_dict() for report in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vigilance_bp.route('/reports/generate', methods=['POST'])
@jwt_required()
def generate_vigilance_report():
    """Generate vigilance report"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['report_name', 'report_type', 'report_period', 'period_start', 'period_end', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        start_date = datetime.fromisoformat(data['period_start']).date()
        end_date = datetime.fromisoformat(data['period_end']).date()
        company_id = data['company_id']
        
        # Generate report data based on type
        report_data = {}
        report_summary = {}
        
        if data['report_type'] == 'summary':
            # Summary report
            total_records = EnhancedVigilanceRecord.query.filter(
                EnhancedVigilanceRecord.company_id == company_id,
                EnhancedVigilanceRecord.detected_date >= start_date,
                EnhancedVigilanceRecord.detected_date <= end_date
            ).count()
            
            open_records = EnhancedVigilanceRecord.query.filter(
                EnhancedVigilanceRecord.company_id == company_id,
                EnhancedVigilanceRecord.status == VigilanceStatus.OPEN,
                EnhancedVigilanceRecord.detected_date >= start_date,
                EnhancedVigilanceRecord.detected_date <= end_date
            ).count()
            
            resolved_records = EnhancedVigilanceRecord.query.filter(
                EnhancedVigilanceRecord.company_id == company_id,
                EnhancedVigilanceRecord.status == VigilanceStatus.RESOLVED,
                EnhancedVigilanceRecord.detected_date >= start_date,
                EnhancedVigilanceRecord.detected_date <= end_date
            ).count()
            
            report_data = {
                'total_records': total_records,
                'open_records': open_records,
                'resolved_records': resolved_records,
                'resolution_rate': (resolved_records / total_records * 100) if total_records > 0 else 0
            }
            
            report_summary = {
                'period': f"{start_date} to {end_date}",
                'key_findings': [
                    f"Total vigilance records: {total_records}",
                    f"Open records: {open_records}",
                    f"Resolved records: {resolved_records}",
                    f"Resolution rate: {report_data['resolution_rate']:.1f}%"
                ]
            }
        
        elif data['report_type'] == 'detailed':
            # Detailed report with all records
            records = EnhancedVigilanceRecord.query.filter(
                EnhancedVigilanceRecord.company_id == company_id,
                EnhancedVigilanceRecord.detected_date >= start_date,
                EnhancedVigilanceRecord.detected_date <= end_date
            ).all()
            
            report_data = {
                'records': [record.to_dict() for record in records],
                'total_count': len(records)
            }
            
            report_summary = {
                'period': f"{start_date} to {end_date}",
                'total_records': len(records),
                'by_type': {},
                'by_status': {},
                'by_level': {}
            }
            
            # Analyze by type, status, and level
            for record in records:
                # By type
                type_key = record.vigilance_type.value
                if type_key not in report_summary['by_type']:
                    report_summary['by_type'][type_key] = 0
                report_summary['by_type'][type_key] += 1
                
                # By status
                status_key = record.status.value
                if status_key not in report_summary['by_status']:
                    report_summary['by_status'][status_key] = 0
                report_summary['by_status'][status_key] += 1
                
                # By level
                level_key = record.vigilance_level
                if level_key not in report_summary['by_level']:
                    report_summary['by_level'][level_key] = 0
                report_summary['by_level'][level_key] += 1
        
        # Create report record
        report = VigilanceReport(
            report_name=data['report_name'],
            report_type=data['report_type'],
            report_period=data['report_period'],
            period_start=start_date,
            period_end=end_date,
            report_data=report_data,
            report_summary=report_summary,
            recommendations=data.get('recommendations'),
            item_filters=data.get('item_filters'),
            supplier_filters=data.get('supplier_filters'),
            vigilance_type_filters=data.get('vigilance_type_filters'),
            status_filters=data.get('status_filters'),
            generated_by=user_id,
            company_id=company_id
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('vigilance_report_generated', report.to_dict(), company_id)
        
        return jsonify(report.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Vigilance Dashboard
@vigilance_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_vigilance_dashboard():
    """Get vigilance dashboard data"""
    try:
        company_id = request.args.get('company_id', type=int)
        user_id = get_jwt_identity()
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        # Get dashboard configuration
        dashboard = VigilanceDashboard.query.filter(
            VigilanceDashboard.user_id == user_id,
            VigilanceDashboard.company_id == company_id,
            VigilanceDashboard.is_default == True
        ).first()
        
        if not dashboard:
            # Create default dashboard
            dashboard = VigilanceDashboard(
                dashboard_name='Default Vigilance Dashboard',
                user_id=user_id,
                dashboard_config={
                    'widgets': [
                        {'type': 'vigilance_summary', 'position': {'x': 0, 'y': 0, 'w': 6, 'h': 4}},
                        {'type': 'records_by_type', 'position': {'x': 6, 'y': 0, 'w': 6, 'h': 4}},
                        {'type': 'records_by_status', 'position': {'x': 0, 'y': 4, 'w': 6, 'h': 4}},
                        {'type': 'recent_records', 'position': {'x': 6, 'y': 4, 'w': 6, 'h': 4}}
                    ]
                },
                is_default=True,
                company_id=company_id
            )
            db.session.add(dashboard)
            db.session.commit()
        
        # Get dashboard data
        dashboard_data = {
            'dashboard_config': dashboard.dashboard_config,
            'widgets_data': {}
        }
        
        # Calculate widget data
        # Vigilance summary
        total_records = EnhancedVigilanceRecord.query.filter(
            EnhancedVigilanceRecord.company_id == company_id
        ).count()
        
        open_records = EnhancedVigilanceRecord.query.filter(
            EnhancedVigilanceRecord.company_id == company_id,
            EnhancedVigilanceRecord.status == VigilanceStatus.OPEN
        ).count()
        
        resolved_records = EnhancedVigilanceRecord.query.filter(
            EnhancedVigilanceRecord.company_id == company_id,
            EnhancedVigilanceRecord.status == VigilanceStatus.RESOLVED
        ).count()
        
        dashboard_data['widgets_data']['vigilance_summary'] = {
            'total_records': total_records,
            'open_records': open_records,
            'resolved_records': resolved_records,
            'resolution_rate': (resolved_records / total_records * 100) if total_records > 0 else 0
        }
        
        # Records by type
        records_by_type = {}
        for vigilance_type in VigilanceType:
            count = EnhancedVigilanceRecord.query.filter(
                EnhancedVigilanceRecord.company_id == company_id,
                EnhancedVigilanceRecord.vigilance_type == vigilance_type
            ).count()
            if count > 0:
                records_by_type[vigilance_type.value] = count
        
        dashboard_data['widgets_data']['records_by_type'] = records_by_type
        
        # Records by status
        records_by_status = {}
        for status in VigilanceStatus:
            count = EnhancedVigilanceRecord.query.filter(
                EnhancedVigilanceRecord.company_id == company_id,
                EnhancedVigilanceRecord.status == status
            ).count()
            if count > 0:
                records_by_status[status.value] = count
        
        dashboard_data['widgets_data']['records_by_status'] = records_by_status
        
        # Recent records
        recent_records = EnhancedVigilanceRecord.query.filter(
            EnhancedVigilanceRecord.company_id == company_id
        ).order_by(EnhancedVigilanceRecord.detected_date.desc()).limit(10).all()
        
        dashboard_data['widgets_data']['recent_records'] = [record.to_dict() for record in recent_records]
        
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# File attachments for vigilance records
@vigilance_bp.route('/records/<int:record_id>/attachments', methods=['POST'])
@jwt_required()
def upload_vigilance_attachment(record_id):
    """Upload attachment for vigilance record"""
    try:
        user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        description = request.form.get('description', '')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type and size
        allowed_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'txt'}
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        if file_extension not in allowed_extensions:
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        upload_folder = 'uploads/vigilance'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, f"{record_id}_{filename}")
        file.save(file_path)
        
        # Create attachment record
        attachment = VigilanceAttachment(
            vigilance_record_id=record_id,
            file_name=filename,
            file_path=file_path,
            file_type=file_extension,
            file_size=len(file.read()),
            description=description,
            uploaded_by=user_id
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        return jsonify(attachment.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
