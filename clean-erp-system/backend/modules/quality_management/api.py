# Quality Management API Endpoints
# Complete quality control, inspection management, and compliance tracking

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import require_auth, get_current_user
from .models import (
    QualityInspection, InspectionItem, NonConformance, NCAttachment,
    CAPA, QualityAudit, QualityMetric
)
from datetime import datetime, date
import json

# Create blueprint
quality_management_bp = Blueprint('quality_management', __name__, url_prefix='/quality-management')

# Quality Inspection Endpoints
@quality_management_bp.route('/inspections', methods=['GET'])
@require_auth
def get_quality_inspections():
    """Get all quality inspections with advanced filtering"""
    try:
        query = QualityInspection.query.filter_by(company_id=get_current_user().company_id)
        
        # Apply filters
        if request.args.get('status'):
            query = query.filter_by(status=request.args.get('status'))
        if request.args.get('inspection_type'):
            query = query.filter_by(inspection_type=request.args.get('inspection_type'))
        if request.args.get('inspector_id'):
            query = query.filter_by(inspector_id=request.args.get('inspector_id'))
        if request.args.get('date_from'):
            query = query.filter(QualityInspection.inspection_date >= datetime.strptime(request.args.get('date_from'), '%Y-%m-%d').date())
        if request.args.get('date_to'):
            query = query.filter(QualityInspection.inspection_date <= datetime.strptime(request.args.get('date_to'), '%Y-%m-%d').date())
        
        inspections = query.all()
        return jsonify({
            'success': True,
            'data': [inspection.to_dict() for inspection in inspections]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@quality_management_bp.route('/inspections', methods=['POST'])
@require_auth
def create_quality_inspection():
    """Create a new quality inspection"""
    try:
        data = request.get_json()
        
        # Generate inspection number
        inspection_number = f"QI-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        inspection = QualityInspection(
            inspection_number=inspection_number,
            inspection_name=data['inspection_name'],
            inspection_description=data.get('inspection_description'),
            inspection_type=data['inspection_type'],
            inspection_date=datetime.strptime(data['inspection_date'], '%Y-%m-%d').date() if data.get('inspection_date') else date.today(),
            scheduled_date=datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date() if data.get('scheduled_date') else None,
            status=data.get('status', 'Scheduled'),
            inspector_id=data.get('inspector_id'),
            inspection_criteria=data.get('inspection_criteria', {}),
            acceptance_criteria=data.get('acceptance_criteria', {}),
            sampling_plan=data.get('sampling_plan', {}),
            total_quantity=data.get('total_quantity', 0),
            company_id=get_current_user().company_id
        )
        
        db.session.add(inspection)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': inspection.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@quality_management_bp.route('/inspections/<int:inspection_id>/complete', methods=['POST'])
@require_auth
def complete_inspection(inspection_id):
    """Complete a quality inspection"""
    try:
        inspection = QualityInspection.query.get_or_404(inspection_id)
        data = request.get_json()
        
        # Update inspection results
        inspection.inspected_quantity = data.get('inspected_quantity', 0)
        inspection.passed_quantity = data.get('passed_quantity', 0)
        inspection.failed_quantity = data.get('failed_quantity', 0)
        inspection.findings = data.get('findings', {})
        inspection.defects_found = data.get('defects_found', [])
        inspection.recommendations = data.get('recommendations')
        
        # Calculate pass rate
        if inspection.inspected_quantity > 0:
            inspection.pass_rate = (inspection.passed_quantity / inspection.inspected_quantity) * 100
        
        # Update status
        inspection.status = 'Completed'
        inspection.completed_date = date.today()
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': inspection.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Non-Conformance Management Endpoints
@quality_management_bp.route('/non-conformances', methods=['GET'])
@require_auth
def get_non_conformances():
    """Get all non-conformances with advanced filtering"""
    try:
        query = NonConformance.query.filter_by(company_id=get_current_user().company_id)
        
        # Apply filters
        if request.args.get('status'):
            query = query.filter_by(status=request.args.get('status'))
        if request.args.get('severity'):
            query = query.filter_by(severity=request.args.get('severity'))
        if request.args.get('nc_type'):
            query = query.filter_by(nc_type=request.args.get('nc_type'))
        if request.args.get('discovered_by_id'):
            query = query.filter_by(discovered_by_id=request.args.get('discovered_by_id'))
        
        non_conformances = query.all()
        return jsonify({
            'success': True,
            'data': [nc.to_dict() for nc in non_conformances]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@quality_management_bp.route('/non-conformances', methods=['POST'])
@require_auth
def create_non_conformance():
    """Create a new non-conformance"""
    try:
        data = request.get_json()
        
        # Generate NC number
        nc_number = f"NC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        non_conformance = NonConformance(
            nc_number=nc_number,
            nc_title=data['nc_title'],
            nc_description=data['nc_description'],
            nc_date=datetime.strptime(data['nc_date'], '%Y-%m-%d').date() if data.get('nc_date') else date.today(),
            discovered_by_id=data.get('discovered_by_id'),
            nc_type=data.get('nc_type'),
            severity=data.get('severity', 'Medium'),
            status=data.get('status', 'Open'),
            affected_products=data.get('affected_products', []),
            affected_processes=data.get('affected_processes', []),
            customer_impact=data.get('customer_impact'),
            financial_impact=data.get('financial_impact', 0.0),
            company_id=get_current_user().company_id
        )
        
        db.session.add(non_conformance)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': non_conformance.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@quality_management_bp.route('/non-conformances/<int:nc_id>/root-cause', methods=['PUT'])
@require_auth
def update_root_cause_analysis(nc_id):
    """Update root cause analysis for a non-conformance"""
    try:
        non_conformance = NonConformance.query.get_or_404(nc_id)
        data = request.get_json()
        
        non_conformance.root_cause = data.get('root_cause')
        non_conformance.root_cause_analysis_date = datetime.strptime(data['root_cause_analysis_date'], '%Y-%m-%d').date() if data.get('root_cause_analysis_date') else date.today()
        non_conformance.root_cause_analyst_id = data.get('root_cause_analyst_id')
        non_conformance.status = 'Root Cause Analysis'
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': non_conformance.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@quality_management_bp.route('/non-conformances/<int:nc_id>/corrective-actions', methods=['PUT'])
@require_auth
def update_corrective_actions(nc_id):
    """Update corrective actions for a non-conformance"""
    try:
        non_conformance = NonConformance.query.get_or_404(nc_id)
        data = request.get_json()
        
        non_conformance.corrective_actions = data.get('corrective_actions', [])
        non_conformance.preventive_actions = data.get('preventive_actions', [])
        non_conformance.action_owner_id = data.get('action_owner_id')
        non_conformance.status = 'Corrective Action'
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': non_conformance.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# CAPA Management Endpoints
@quality_management_bp.route('/capas', methods=['GET'])
@require_auth
def get_capas():
    """Get all CAPAs with advanced filtering"""
    try:
        query = CAPA.query.filter_by(company_id=get_current_user().company_id)
        
        # Apply filters
        if request.args.get('status'):
            query = query.filter_by(status=request.args.get('status'))
        if request.args.get('capa_type'):
            query = query.filter_by(capa_type=request.args.get('capa_type'))
        if request.args.get('capa_owner_id'):
            query = query.filter_by(capa_owner_id=request.args.get('capa_owner_id'))
        
        capas = query.all()
        return jsonify({
            'success': True,
            'data': [capa.to_dict() for capa in capas]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@quality_management_bp.route('/capas', methods=['POST'])
@require_auth
def create_capa():
    """Create a new CAPA"""
    try:
        data = request.get_json()
        
        # Generate CAPA number
        capa_number = f"CAPA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        capa = CAPA(
            capa_number=capa_number,
            capa_title=data['capa_title'],
            capa_description=data['capa_description'],
            capa_date=datetime.strptime(data['capa_date'], '%Y-%m-%d').date() if data.get('capa_date') else date.today(),
            capa_type=data.get('capa_type', 'Corrective'),
            status=data.get('status', 'Open'),
            related_nc_id=data.get('related_nc_id'),
            capa_owner_id=data.get('capa_owner_id'),
            problem_description=data['problem_description'],
            problem_scope=data.get('problem_scope'),
            affected_areas=data.get('affected_areas', []),
            company_id=get_current_user().company_id
        )
        
        db.session.add(capa)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': capa.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@quality_management_bp.route('/capas/<int:capa_id>/root-cause', methods=['PUT'])
@require_auth
def update_capa_root_cause(capa_id):
    """Update root cause analysis for a CAPA"""
    try:
        capa = CAPA.query.get_or_404(capa_id)
        data = request.get_json()
        
        capa.root_cause_analysis = data.get('root_cause_analysis')
        capa.root_cause_method = data.get('root_cause_method')
        capa.root_cause_analyst_id = data.get('root_cause_analyst_id')
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': capa.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@quality_management_bp.route('/capas/<int:capa_id>/action-plan', methods=['PUT'])
@require_auth
def update_capa_action_plan(capa_id):
    """Update action plan for a CAPA"""
    try:
        capa = CAPA.query.get_or_404(capa_id)
        data = request.get_json()
        
        capa.action_plan = data.get('action_plan', {})
        capa.action_items = data.get('action_items', [])
        capa.responsible_persons = data.get('responsible_persons', [])
        capa.target_dates = data.get('target_dates', [])
        capa.status = 'In Progress'
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': capa.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Quality Audit Endpoints
@quality_management_bp.route('/audits', methods=['GET'])
@require_auth
def get_quality_audits():
    """Get all quality audits with advanced filtering"""
    try:
        query = QualityAudit.query.filter_by(company_id=get_current_user().company_id)
        
        # Apply filters
        if request.args.get('status'):
            query = query.filter_by(status=request.args.get('status'))
        if request.args.get('audit_type'):
            query = query.filter_by(audit_type=request.args.get('audit_type'))
        if request.args.get('lead_auditor_id'):
            query = query.filter_by(lead_auditor_id=request.args.get('lead_auditor_id'))
        if request.args.get('date_from'):
            query = query.filter(QualityAudit.audit_date >= datetime.strptime(request.args.get('date_from'), '%Y-%m-%d').date())
        if request.args.get('date_to'):
            query = query.filter(QualityAudit.audit_date <= datetime.strptime(request.args.get('date_to'), '%Y-%m-%d').date())
        
        audits = query.all()
        return jsonify({
            'success': True,
            'data': [audit.to_dict() for audit in audits]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@quality_management_bp.route('/audits', methods=['POST'])
@require_auth
def create_quality_audit():
    """Create a new quality audit"""
    try:
        data = request.get_json()
        
        # Generate audit number
        audit_number = f"QA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        audit = QualityAudit(
            audit_number=audit_number,
            audit_title=data['audit_title'],
            audit_description=data.get('audit_description'),
            audit_type=data['audit_type'],
            audit_scope=data['audit_scope'],
            audit_date=datetime.strptime(data['audit_date'], '%Y-%m-%d').date(),
            status=data.get('status', 'Planned'),
            lead_auditor_id=data.get('lead_auditor_id'),
            audit_team=data.get('audit_team', []),
            audited_areas=data.get('audited_areas', []),
            audit_criteria=data.get('audit_criteria', {}),
            audit_objectives=data.get('audit_objectives'),
            company_id=get_current_user().company_id
        )
        
        db.session.add(audit)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': audit.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@quality_management_bp.route('/audits/<int:audit_id>/complete', methods=['POST'])
@require_auth
def complete_audit(audit_id):
    """Complete a quality audit"""
    try:
        audit = QualityAudit.query.get_or_404(audit_id)
        data = request.get_json()
        
        # Update audit results
        audit.audit_findings = data.get('audit_findings', [])
        audit.non_conformities = data.get('non_conformities', [])
        audit.observations = data.get('observations', [])
        audit.opportunities_for_improvement = data.get('opportunities_for_improvement', [])
        audit.audit_report = data.get('audit_report')
        audit.audit_conclusion = data.get('audit_conclusion')
        audit.audit_recommendations = data.get('audit_recommendations')
        audit.follow_up_required = data.get('follow_up_required', False)
        audit.follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date() if data.get('follow_up_date') else None
        
        # Update status
        audit.status = 'Completed'
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': audit.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Quality Metrics Endpoints
@quality_management_bp.route('/metrics', methods=['GET'])
@require_auth
def get_quality_metrics():
    """Get all quality metrics"""
    try:
        metrics = QualityMetric.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [metric.to_dict() for metric in metrics]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@quality_management_bp.route('/metrics', methods=['POST'])
@require_auth
def create_quality_metric():
    """Create a new quality metric"""
    try:
        data = request.get_json()
        metric = QualityMetric(
            metric_name=data['metric_name'],
            metric_description=data.get('metric_description'),
            metric_type=data['metric_type'],
            measurement_period=data.get('measurement_period', 'Monthly'),
            target_value=data.get('target_value', 0.0),
            actual_value=data.get('actual_value', 0.0),
            unit_of_measure=data.get('unit_of_measure'),
            calculation_method=data.get('calculation_method'),
            data_sources=data.get('data_sources', []),
            calculation_formula=data.get('calculation_formula'),
            is_active=data.get('is_active', True),
            company_id=get_current_user().company_id
        )
        
        db.session.add(metric)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': metric.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@quality_management_bp.route('/metrics/<int:metric_id>/update', methods=['PUT'])
@require_auth
def update_quality_metric(metric_id):
    """Update a quality metric"""
    try:
        metric = QualityMetric.query.get_or_404(metric_id)
        data = request.get_json()
        
        metric.actual_value = data.get('actual_value', metric.actual_value)
        metric.last_updated = datetime.utcnow()
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': metric.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Analytics Endpoints
@quality_management_bp.route('/analytics/quality-summary', methods=['GET'])
@require_auth
def get_quality_summary():
    """Get quality summary analytics"""
    try:
        # Get inspection statistics
        total_inspections = QualityInspection.query.filter_by(company_id=get_current_user().company_id).count()
        completed_inspections = QualityInspection.query.filter_by(
            status='Completed',
            company_id=get_current_user().company_id
        ).count()
        
        # Get average pass rate
        avg_pass_rate = db.session.query(
            db.func.avg(QualityInspection.pass_rate)
        ).filter_by(
            company_id=get_current_user().company_id,
            status='Completed'
        ).scalar() or 0
        
        # Get non-conformance statistics
        total_ncs = NonConformance.query.filter_by(company_id=get_current_user().company_id).count()
        open_ncs = NonConformance.query.filter_by(
            status='Open',
            company_id=get_current_user().company_id
        ).count()
        closed_ncs = NonConformance.query.filter_by(
            status='Closed',
            company_id=get_current_user().company_id
        ).count()
        
        # Get CAPA statistics
        total_capas = CAPA.query.filter_by(company_id=get_current_user().company_id).count()
        open_capas = CAPA.query.filter_by(
            status='Open',
            company_id=get_current_user().company_id
        ).count()
        closed_capas = CAPA.query.filter_by(
            status='Closed',
            company_id=get_current_user().company_id
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_inspections': total_inspections,
                'completed_inspections': completed_inspections,
                'average_pass_rate': float(avg_pass_rate),
                'total_non_conformances': total_ncs,
                'open_non_conformances': open_ncs,
                'closed_non_conformances': closed_ncs,
                'total_capas': total_capas,
                'open_capas': open_capas,
                'closed_capas': closed_capas
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@quality_management_bp.route('/analytics/defect-analysis', methods=['GET'])
@require_auth
def get_defect_analysis():
    """Get defect analysis analytics"""
    try:
        # Get defect statistics by type
        inspections = QualityInspection.query.filter_by(
            company_id=get_current_user().company_id,
            status='Completed'
        ).all()
        
        defect_analysis = {}
        for inspection in inspections:
            if inspection.defects_found:
                for defect in inspection.defects_found:
                    defect_type = defect.get('type', 'Unknown')
                    if defect_type not in defect_analysis:
                        defect_analysis[defect_type] = {
                            'count': 0,
                            'frequency': 0.0
                        }
                    defect_analysis[defect_type]['count'] += 1
        
        # Calculate frequency percentages
        total_defects = sum(d['count'] for d in defect_analysis.values())
        for defect_type in defect_analysis:
            defect_analysis[defect_type]['frequency'] = (
                defect_analysis[defect_type]['count'] / total_defects * 100
            ) if total_defects > 0 else 0
        
        return jsonify({
            'success': True,
            'data': defect_analysis
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@quality_management_bp.route('/analytics/trend-analysis', methods=['GET'])
@require_auth
def get_trend_analysis():
    """Get quality trend analysis"""
    try:
        # Get trend data for the last 12 months
        from datetime import timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        
        # Get monthly inspection data
        monthly_data = []
        for i in range(12):
            month_start = start_date + timedelta(days=i*30)
            month_end = month_start + timedelta(days=30)
            
            inspections = QualityInspection.query.filter(
                QualityInspection.inspection_date >= month_start,
                QualityInspection.inspection_date < month_end,
                QualityInspection.company_id == get_current_user().company_id
            ).all()
            
            total_inspections = len(inspections)
            avg_pass_rate = sum(i.pass_rate for i in inspections) / total_inspections if total_inspections > 0 else 0
            
            monthly_data.append({
                'month': month_start.strftime('%Y-%m'),
                'total_inspections': total_inspections,
                'average_pass_rate': float(avg_pass_rate)
            })
        
        return jsonify({
            'success': True,
            'data': monthly_data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
