# Business Intelligence API Endpoints
# Advanced analytics, reporting, and data visualization

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import require_auth, get_current_user
from .models import (
    Dashboard, DashboardWidget, Report, ReportExecution, KPI, KPIHistory,
    DataSource, AnalyticsQuery, DataVisualization
)
from datetime import datetime, date
import json

# Create blueprint
business_intelligence_bp = Blueprint('business_intelligence', __name__, url_prefix='/business-intelligence')

# Dashboard Endpoints
@business_intelligence_bp.route('/dashboards', methods=['GET'])
@require_auth
def get_dashboards():
    """Get all dashboards"""
    try:
        dashboards = Dashboard.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [dashboard.to_dict() for dashboard in dashboards]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@business_intelligence_bp.route('/dashboards', methods=['POST'])
@require_auth
def create_dashboard():
    """Create a new dashboard"""
    try:
        data = request.get_json()
        dashboard = Dashboard(
            dashboard_name=data['dashboard_name'],
            dashboard_description=data.get('dashboard_description'),
            dashboard_type=data['dashboard_type'],
            layout_config=data.get('layout_config', {}),
            widget_config=data.get('widget_config', {}),
            filters_config=data.get('filters_config', {}),
            is_public=data.get('is_public', False),
            is_default=data.get('is_default', False),
            refresh_interval=data.get('refresh_interval', 300),
            allowed_users=data.get('allowed_users', []),
            allowed_roles=data.get('allowed_roles', []),
            company_id=get_current_user().company_id
        )
        
        db.session.add(dashboard)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': dashboard.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@business_intelligence_bp.route('/dashboards/<int:dashboard_id>/widgets', methods=['POST'])
@require_auth
def add_dashboard_widget(dashboard_id):
    """Add a widget to a dashboard"""
    try:
        data = request.get_json()
        widget = DashboardWidget(
            widget_name=data['widget_name'],
            widget_type=data['widget_type'],
            widget_title=data.get('widget_title'),
            widget_description=data.get('widget_description'),
            dashboard_id=dashboard_id,
            position_x=data.get('position_x', 0),
            position_y=data.get('position_y', 0),
            width=data.get('width', 4),
            height=data.get('height', 3),
            data_source=data.get('data_source', 'Database'),
            query_config=data.get('query_config', {}),
            chart_config=data.get('chart_config', {}),
            filter_config=data.get('filter_config', {}),
            is_visible=data.get('is_visible', True),
            refresh_interval=data.get('refresh_interval', 300),
            company_id=get_current_user().company_id
        )
        
        db.session.add(widget)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': widget.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Report Endpoints
@business_intelligence_bp.route('/reports', methods=['GET'])
@require_auth
def get_reports():
    """Get all reports"""
    try:
        reports = Report.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [report.to_dict() for report in reports]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@business_intelligence_bp.route('/reports', methods=['POST'])
@require_auth
def create_report():
    """Create a new report"""
    try:
        data = request.get_json()
        report = Report(
            report_name=data['report_name'],
            report_description=data.get('report_description'),
            report_type=data['report_type'],
            report_config=data.get('report_config', {}),
            query_config=data.get('query_config', {}),
            chart_config=data.get('chart_config', {}),
            filter_config=data.get('filter_config', {}),
            is_scheduled=data.get('is_scheduled', False),
            schedule_config=data.get('schedule_config', {}),
            is_public=data.get('is_public', False),
            allowed_users=data.get('allowed_users', []),
            allowed_roles=data.get('allowed_roles', []),
            company_id=get_current_user().company_id
        )
        
        db.session.add(report)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': report.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@business_intelligence_bp.route('/reports/<int:report_id>/execute', methods=['POST'])
@require_auth
def execute_report(report_id):
    """Execute a report"""
    try:
        report = Report.query.get_or_404(report_id)
        data = request.get_json()
        
        # Create execution record
        execution = ReportExecution(
            report_id=report_id,
            parameters=data.get('parameters', {}),
            filters=data.get('filters', {}),
            executed_by_id=get_current_user().id,
            company_id=get_current_user().company_id
        )
        
        # Simulate report execution
        execution.execution_status = 'Running'
        db.session.add(execution)
        db.session.flush()
        
        # Simulate data processing
        execution.result_data = {
            'columns': ['Date', 'Revenue', 'Profit'],
            'data': [
                ['2024-01-01', 100000, 15000],
                ['2024-01-02', 120000, 18000],
                ['2024-01-03', 110000, 16500]
            ]
        }
        execution.execution_status = 'Completed'
        execution.execution_time = 2.5
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': execution.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# KPI Endpoints
@business_intelligence_bp.route('/kpis', methods=['GET'])
@require_auth
def get_kpis():
    """Get all KPIs"""
    try:
        kpis = KPI.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [kpi.to_dict() for kpi in kpis]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@business_intelligence_bp.route('/kpis', methods=['POST'])
@require_auth
def create_kpi():
    """Create a new KPI"""
    try:
        data = request.get_json()
        kpi = KPI(
            kpi_name=data['kpi_name'],
            kpi_description=data.get('kpi_description'),
            kpi_category=data.get('kpi_category'),
            calculation_method=data['calculation_method'],
            data_sources=data.get('data_sources', []),
            calculation_formula=data.get('calculation_formula'),
            current_value=data.get('current_value', 0.0),
            target_value=data.get('target_value', 0.0),
            previous_value=data.get('previous_value', 0.0),
            unit_of_measure=data.get('unit_of_measure'),
            status=data.get('status', 'Average'),
            trend_direction=data.get('trend_direction'),
            trend_percentage=data.get('trend_percentage', 0.0),
            is_active=data.get('is_active', True),
            update_frequency=data.get('update_frequency', 'Daily'),
            company_id=get_current_user().company_id
        )
        
        db.session.add(kpi)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': kpi.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@business_intelligence_bp.route('/kpis/<int:kpi_id>/update', methods=['PUT'])
@require_auth
def update_kpi(kpi_id):
    """Update a KPI"""
    try:
        kpi = KPI.query.get_or_404(kpi_id)
        data = request.get_json()
        
        # Update KPI values
        kpi.current_value = data.get('current_value', kpi.current_value)
        kpi.target_value = data.get('target_value', kpi.target_value)
        kpi.previous_value = kpi.current_value  # Store previous value
        kpi.last_updated = datetime.utcnow()
        
        # Calculate trend
        if kpi.previous_value > 0:
            kpi.trend_percentage = ((kpi.current_value - kpi.previous_value) / kpi.previous_value) * 100
            if kpi.trend_percentage > 0:
                kpi.trend_direction = 'Up'
            elif kpi.trend_percentage < 0:
                kpi.trend_direction = 'Down'
            else:
                kpi.trend_direction = 'Stable'
        
        # Update status based on performance
        if kpi.current_value >= kpi.target_value:
            kpi.status = 'Excellent'
        elif kpi.current_value >= kpi.target_value * 0.8:
            kpi.status = 'Good'
        elif kpi.current_value >= kpi.target_value * 0.6:
            kpi.status = 'Average'
        elif kpi.current_value >= kpi.target_value * 0.4:
            kpi.status = 'Poor'
        else:
            kpi.status = 'Critical'
        
        # Create history record
        history = KPIHistory(
            kpi_id=kpi_id,
            recorded_date=date.today(),
            recorded_value=kpi.current_value,
            target_value=kpi.target_value,
            variance=kpi.current_value - kpi.target_value,
            variance_percentage=((kpi.current_value - kpi.target_value) / kpi.target_value * 100) if kpi.target_value > 0 else 0,
            company_id=get_current_user().company_id
        )
        db.session.add(history)
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': kpi.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Data Source Endpoints
@business_intelligence_bp.route('/data-sources', methods=['GET'])
@require_auth
def get_data_sources():
    """Get all data sources"""
    try:
        data_sources = DataSource.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [source.to_dict() for source in data_sources]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@business_intelligence_bp.route('/data-sources', methods=['POST'])
@require_auth
def create_data_source():
    """Create a new data source"""
    try:
        data = request.get_json()
        data_source = DataSource(
            source_name=data['source_name'],
            source_description=data.get('source_description'),
            source_type=data['source_type'],
            connection_config=data.get('connection_config', {}),
            authentication_config=data.get('authentication_config', {}),
            is_active=data.get('is_active', True),
            refresh_interval=data.get('refresh_interval', 3600),
            company_id=get_current_user().company_id
        )
        
        db.session.add(data_source)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': data_source.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Analytics Query Endpoints
@business_intelligence_bp.route('/queries', methods=['GET'])
@require_auth
def get_analytics_queries():
    """Get all analytics queries"""
    try:
        queries = AnalyticsQuery.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [query.to_dict() for query in queries]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@business_intelligence_bp.route('/queries', methods=['POST'])
@require_auth
def create_analytics_query():
    """Create a new analytics query"""
    try:
        data = request.get_json()
        query = AnalyticsQuery(
            query_name=data['query_name'],
            query_description=data.get('query_description'),
            query_sql=data['query_sql'],
            parameters=data.get('parameters', {}),
            filters=data.get('filters', {}),
            grouping=data.get('grouping', {}),
            sorting=data.get('sorting', {}),
            is_public=data.get('is_public', False),
            execution_timeout=data.get('execution_timeout', 300),
            allowed_users=data.get('allowed_users', []),
            allowed_roles=data.get('allowed_roles', []),
            company_id=get_current_user().company_id
        )
        
        db.session.add(query)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': query.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@business_intelligence_bp.route('/queries/<int:query_id>/execute', methods=['POST'])
@require_auth
def execute_analytics_query(query_id):
    """Execute an analytics query"""
    try:
        query = AnalyticsQuery.query.get_or_404(query_id)
        data = request.get_json()
        
        # Simulate query execution
        # In a real implementation, this would execute the SQL query
        result = {
            'columns': ['Name', 'Value', 'Date'],
            'data': [
                ['Sales Revenue', 150000, '2024-01-01'],
                ['Marketing Cost', 25000, '2024-01-01'],
                ['Net Profit', 125000, '2024-01-01']
            ],
            'execution_time': 1.2,
            'row_count': 3
        }
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Data Visualization Endpoints
@business_intelligence_bp.route('/visualizations', methods=['GET'])
@require_auth
def get_data_visualizations():
    """Get all data visualizations"""
    try:
        visualizations = DataVisualization.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [viz.to_dict() for viz in visualizations]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@business_intelligence_bp.route('/visualizations', methods=['POST'])
@require_auth
def create_data_visualization():
    """Create a new data visualization"""
    try:
        data = request.get_json()
        visualization = DataVisualization(
            visualization_name=data['visualization_name'],
            visualization_description=data.get('visualization_description'),
            chart_type=data['chart_type'],
            data_source_id=data.get('data_source_id'),
            query_id=data.get('query_id'),
            chart_config=data.get('chart_config', {}),
            color_scheme=data.get('color_scheme', 'default'),
            chart_options=data.get('chart_options', {}),
            is_public=data.get('is_public', False),
            is_interactive=data.get('is_interactive', True),
            company_id=get_current_user().company_id
        )
        
        db.session.add(visualization)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': visualization.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Analytics Endpoints
@business_intelligence_bp.route('/analytics/executive-summary', methods=['GET'])
@require_auth
def get_executive_summary():
    """Get executive summary analytics"""
    try:
        # Get key metrics
        total_kpis = KPI.query.filter_by(company_id=get_current_user().company_id).count()
        active_kpis = KPI.query.filter_by(
            company_id=get_current_user().company_id,
            is_active=True
        ).count()
        
        # Get KPI performance summary
        excellent_kpis = KPI.query.filter_by(
            company_id=get_current_user().company_id,
            status='Excellent'
        ).count()
        good_kpis = KPI.query.filter_by(
            company_id=get_current_user().company_id,
            status='Good'
        ).count()
        poor_kpis = KPI.query.filter_by(
            company_id=get_current_user().company_id,
            status='Poor'
        ).count()
        
        # Get dashboard usage
        total_dashboards = Dashboard.query.filter_by(company_id=get_current_user().company_id).count()
        public_dashboards = Dashboard.query.filter_by(
            company_id=get_current_user().company_id,
            is_public=True
        ).count()
        
        # Get report statistics
        total_reports = Report.query.filter_by(company_id=get_current_user().company_id).count()
        scheduled_reports = Report.query.filter_by(
            company_id=get_current_user().company_id,
            is_scheduled=True
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_kpis': total_kpis,
                'active_kpis': active_kpis,
                'excellent_kpis': excellent_kpis,
                'good_kpis': good_kpis,
                'poor_kpis': poor_kpis,
                'total_dashboards': total_dashboards,
                'public_dashboards': public_dashboards,
                'total_reports': total_reports,
                'scheduled_reports': scheduled_reports
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@business_intelligence_bp.route('/analytics/kpi-trends', methods=['GET'])
@require_auth
def get_kpi_trends():
    """Get KPI trends analysis"""
    try:
        kpi_id = request.args.get('kpi_id')
        if not kpi_id:
            return jsonify({
                'success': False,
                'message': 'KPI ID is required'
            }), 400
        
        # Get KPI history for trend analysis
        history = KPIHistory.query.filter_by(
            kpi_id=kpi_id,
            company_id=get_current_user().company_id
        ).order_by(KPIHistory.recorded_date.desc()).limit(30).all()
        
        trend_data = []
        for record in history:
            trend_data.append({
                'date': record.recorded_date.isoformat(),
                'value': record.recorded_value,
                'target': record.target_value,
                'variance': record.variance,
                'variance_percentage': record.variance_percentage
            })
        
        return jsonify({
            'success': True,
            'data': trend_data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@business_intelligence_bp.route('/analytics/performance-scorecard', methods=['GET'])
@require_auth
def get_performance_scorecard():
    """Get performance scorecard"""
    try:
        # Get KPI performance by category
        kpis = KPI.query.filter_by(
            company_id=get_current_user().company_id,
            is_active=True
        ).all()
        
        scorecard = {}
        for kpi in kpis:
            category = kpi.kpi_category or 'Other'
            if category not in scorecard:
                scorecard[category] = {
                    'total': 0,
                    'excellent': 0,
                    'good': 0,
                    'average': 0,
                    'poor': 0,
                    'critical': 0
                }
            
            scorecard[category]['total'] += 1
            scorecard[category][kpi.status.value.lower()] += 1
        
        return jsonify({
            'success': True,
            'data': scorecard
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
