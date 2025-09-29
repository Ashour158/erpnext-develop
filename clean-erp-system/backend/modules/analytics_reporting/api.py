# Analytics & Reporting API
# API endpoints for advanced analytics and reporting system with productivity insights, attendance analytics, and performance metrics

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from .models import (
    ProductivityAnalytics, AttendanceAnalytics, LocationAnalytics, PerformanceMetric,
    Report, Dashboard, KPI, DataVisualization,
    ReportType, ReportFrequency, MetricType, DashboardType
)
from datetime import datetime, timedelta, date
import json

analytics_reporting_bp = Blueprint('analytics_reporting', __name__)

# Productivity Analytics
@analytics_reporting_bp.route('/productivity', methods=['GET'])
@jwt_required()
def get_productivity_analytics():
    """Get productivity analytics"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        target_user_id = request.args.get('target_user_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = ProductivityAnalytics.query.filter(ProductivityAnalytics.company_id == company_id)
        
        if target_user_id:
            query = query.filter(ProductivityAnalytics.user_id == target_user_id)
        else:
            query = query.filter(ProductivityAnalytics.user_id == user_id)
        
        if start_date:
            query = query.filter(ProductivityAnalytics.analytics_date >= date.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(ProductivityAnalytics.analytics_date <= date.fromisoformat(end_date))
        
        analytics = query.order_by(ProductivityAnalytics.analytics_date.desc()).limit(100).all()
        
        return jsonify([analytic.to_dict() for analytic in analytics])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_reporting_bp.route('/productivity', methods=['POST'])
@jwt_required()
def create_productivity_analytics():
    """Create productivity analytics"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['analytics_date', 'user_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create analytics
        analytics = ProductivityAnalytics(
            analytics_date=date.fromisoformat(data['analytics_date']),
            user_id=data['user_id'],
            total_work_hours=data.get('total_work_hours', 0.0),
            productive_hours=data.get('productive_hours', 0.0),
            productivity_score=data.get('productivity_score', 0.0),
            efficiency_rating=data.get('efficiency_rating', 0.0),
            tasks_completed=data.get('tasks_completed', 0),
            tasks_pending=data.get('tasks_pending', 0),
            tasks_overdue=data.get('tasks_overdue', 0),
            task_completion_rate=data.get('task_completion_rate', 0.0),
            meetings_attended=data.get('meetings_attended', 0),
            meeting_hours=data.get('meeting_hours', 0.0),
            meeting_effectiveness=data.get('meeting_effectiveness', 0.0),
            time_at_office=data.get('time_at_office', 0.0),
            time_remote=data.get('time_remote', 0.0),
            travel_time=data.get('travel_time', 0.0),
            company_id=data['company_id']
        )
        
        db.session.add(analytics)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('productivity_analytics_created', analytics.to_dict(), data['company_id'])
        
        return jsonify(analytics.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Attendance Analytics
@analytics_reporting_bp.route('/attendance', methods=['GET'])
@jwt_required()
def get_attendance_analytics():
    """Get attendance analytics"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        target_user_id = request.args.get('target_user_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = AttendanceAnalytics.query.filter(AttendanceAnalytics.company_id == company_id)
        
        if target_user_id:
            query = query.filter(AttendanceAnalytics.user_id == target_user_id)
        else:
            query = query.filter(AttendanceAnalytics.user_id == user_id)
        
        if start_date:
            query = query.filter(AttendanceAnalytics.analytics_date >= date.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(AttendanceAnalytics.analytics_date <= date.fromisoformat(end_date))
        
        analytics = query.order_by(AttendanceAnalytics.analytics_date.desc()).limit(100).all()
        
        return jsonify([analytic.to_dict() for analytic in analytics])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_reporting_bp.route('/attendance', methods=['POST'])
@jwt_required()
def create_attendance_analytics():
    """Create attendance analytics"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['analytics_date', 'user_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create analytics
        analytics = AttendanceAnalytics(
            analytics_date=date.fromisoformat(data['analytics_date']),
            user_id=data['user_id'],
            total_days=data.get('total_days', 0),
            present_days=data.get('present_days', 0),
            absent_days=data.get('absent_days', 0),
            late_days=data.get('late_days', 0),
            early_leave_days=data.get('early_leave_days', 0),
            attendance_rate=data.get('attendance_rate', 0.0),
            total_work_hours=data.get('total_work_hours', 0.0),
            overtime_hours=data.get('overtime_hours', 0.0),
            break_hours=data.get('break_hours', 0.0),
            average_daily_hours=data.get('average_daily_hours', 0.0),
            average_check_in_time=datetime.strptime(data['average_check_in_time'], '%H:%M').time() if data.get('average_check_in_time') else None,
            average_check_out_time=datetime.strptime(data['average_check_out_time'], '%H:%M').time() if data.get('average_check_out_time') else None,
            punctuality_score=data.get('punctuality_score', 0.0),
            company_id=data['company_id']
        )
        
        db.session.add(analytics)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('attendance_analytics_created', analytics.to_dict(), data['company_id'])
        
        return jsonify(analytics.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Location Analytics
@analytics_reporting_bp.route('/location', methods=['GET'])
@jwt_required()
def get_location_analytics():
    """Get location analytics"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        target_user_id = request.args.get('target_user_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = LocationAnalytics.query.filter(LocationAnalytics.company_id == company_id)
        
        if target_user_id:
            query = query.filter(LocationAnalytics.user_id == target_user_id)
        else:
            query = query.filter(LocationAnalytics.user_id == user_id)
        
        if start_date:
            query = query.filter(LocationAnalytics.analytics_date >= date.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(LocationAnalytics.analytics_date <= date.fromisoformat(end_date))
        
        analytics = query.order_by(LocationAnalytics.analytics_date.desc()).limit(100).all()
        
        return jsonify([analytic.to_dict() for analytic in analytics])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_reporting_bp.route('/location', methods=['POST'])
@jwt_required()
def create_location_analytics():
    """Create location analytics"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['analytics_date', 'user_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create analytics
        analytics = LocationAnalytics(
            analytics_date=date.fromisoformat(data['analytics_date']),
            user_id=data['user_id'],
            total_locations=data.get('total_locations', 0),
            unique_locations=data.get('unique_locations', 0),
            most_visited_location=data.get('most_visited_location'),
            time_at_most_visited=data.get('time_at_most_visited', 0.0),
            total_distance_traveled=data.get('total_distance_traveled', 0.0),
            total_travel_time=data.get('total_travel_time', 0.0),
            average_speed=data.get('average_speed', 0.0),
            fuel_consumption=data.get('fuel_consumption', 0.0),
            location_heatmap=data.get('location_heatmap'),
            location_timeline=data.get('location_timeline'),
            movement_patterns=data.get('movement_patterns'),
            company_id=data['company_id']
        )
        
        db.session.add(analytics)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('location_analytics_created', analytics.to_dict(), data['company_id'])
        
        return jsonify(analytics.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Performance Metrics
@analytics_reporting_bp.route('/performance-metrics', methods=['GET'])
@jwt_required()
def get_performance_metrics():
    """Get performance metrics"""
    try:
        company_id = request.args.get('company_id', type=int)
        user_id = request.args.get('user_id', type=int)
        department_id = request.args.get('department_id', type=int)
        metric_type = request.args.get('metric_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = PerformanceMetric.query.filter(PerformanceMetric.company_id == company_id)
        
        if user_id:
            query = query.filter(PerformanceMetric.user_id == user_id)
        
        if department_id:
            query = query.filter(PerformanceMetric.department_id == department_id)
        
        if metric_type:
            query = query.filter(PerformanceMetric.metric_type == MetricType(metric_type))
        
        if start_date:
            query = query.filter(PerformanceMetric.period_start >= date.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(PerformanceMetric.period_end <= date.fromisoformat(end_date))
        
        metrics = query.order_by(PerformanceMetric.period_start.desc()).limit(100).all()
        
        return jsonify([metric.to_dict() for metric in metrics])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_reporting_bp.route('/performance-metrics', methods=['POST'])
@jwt_required()
def create_performance_metric():
    """Create performance metric"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['metric_name', 'metric_type', 'metric_value', 'period_start', 'period_end', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create metric
        metric = PerformanceMetric(
            metric_name=data['metric_name'],
            metric_description=data.get('metric_description'),
            metric_type=MetricType(data['metric_type']),
            metric_value=data['metric_value'],
            target_value=data.get('target_value', 0.0),
            unit=data.get('unit', ''),
            period_start=date.fromisoformat(data['period_start']),
            period_end=date.fromisoformat(data['period_end']),
            user_id=data.get('user_id', user_id),
            department_id=data.get('department_id'),
            company_id=data['company_id']
        )
        
        db.session.add(metric)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('performance_metric_created', metric.to_dict(), data['company_id'])
        
        return jsonify(metric.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Reports
@analytics_reporting_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """Get reports"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        report_type = request.args.get('report_type')
        is_public = request.args.get('is_public', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = Report.query.filter(Report.company_id == company_id)
        
        if report_type:
            query = query.filter(Report.report_type == ReportType(report_type))
        
        if is_public is not None:
            query = query.filter(Report.is_public == is_public)
        
        reports = query.order_by(Report.created_at.desc()).limit(50).all()
        
        return jsonify([report.to_dict() for report in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_reporting_bp.route('/reports', methods=['POST'])
@jwt_required()
def create_report():
    """Create report"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['report_name', 'report_type', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create report
        report = Report(
            report_name=data['report_name'],
            report_description=data.get('report_description'),
            report_type=ReportType(data['report_type']),
            report_frequency=ReportFrequency(data.get('report_frequency', 'ON_DEMAND')),
            report_config=data.get('report_config'),
            filters=data.get('filters'),
            columns=data.get('columns'),
            sorting=data.get('sorting'),
            report_data=data.get('report_data'),
            is_public=data.get('is_public', False),
            allowed_users=data.get('allowed_users'),
            allowed_roles=data.get('allowed_roles'),
            company_id=data['company_id']
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('report_created', report.to_dict(), data['company_id'])
        
        return jsonify(report.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@analytics_reporting_bp.route('/reports/<int:report_id>/generate', methods=['POST'])
@jwt_required()
def generate_report(report_id):
    """Generate report"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        report = Report.query.filter(
            Report.id == report_id,
            Report.company_id == data.get('company_id')
        ).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Update report generation status
        report.generation_status = 'Generating'
        report.last_generated = datetime.utcnow()
        
        # Simulate report generation
        # In a real implementation, this would generate the actual report data
        report.report_data = {
            'generated_at': datetime.utcnow().isoformat(),
            'data': 'Report data would be generated here'
        }
        report.generation_status = 'Completed'
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('report_generated', report.to_dict(), report.company_id)
        
        return jsonify(report.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Dashboards
@analytics_reporting_bp.route('/dashboards', methods=['GET'])
@jwt_required()
def get_dashboards():
    """Get dashboards"""
    try:
        user_id = get_jwt_identity()
        company_id = request.args.get('company_id', type=int)
        dashboard_type = request.args.get('dashboard_type')
        is_public = request.args.get('is_public', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = Dashboard.query.filter(Dashboard.company_id == company_id)
        
        if dashboard_type:
            query = query.filter(Dashboard.dashboard_type == DashboardType(dashboard_type))
        
        if is_public is not None:
            query = query.filter(Dashboard.is_public == is_public)
        
        dashboards = query.order_by(Dashboard.created_at.desc()).limit(50).all()
        
        return jsonify([dashboard.to_dict() for dashboard in dashboards])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_reporting_bp.route('/dashboards', methods=['POST'])
@jwt_required()
def create_dashboard():
    """Create dashboard"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['dashboard_name', 'dashboard_type', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create dashboard
        dashboard = Dashboard(
            dashboard_name=data['dashboard_name'],
            dashboard_description=data.get('dashboard_description'),
            dashboard_type=DashboardType(data['dashboard_type']),
            is_default=data.get('is_default', False),
            dashboard_config=data.get('dashboard_config'),
            widgets=data.get('widgets'),
            layout=data.get('layout'),
            is_public=data.get('is_public', False),
            allowed_users=data.get('allowed_users'),
            allowed_roles=data.get('allowed_roles'),
            company_id=data['company_id']
        )
        
        db.session.add(dashboard)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('dashboard_created', dashboard.to_dict(), data['company_id'])
        
        return jsonify(dashboard.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# KPIs
@analytics_reporting_bp.route('/kpis', methods=['GET'])
@jwt_required()
def get_kpis():
    """Get KPIs"""
    try:
        company_id = request.args.get('company_id', type=int)
        kpi_category = request.args.get('kpi_category')
        kpi_type = request.args.get('kpi_type')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = KPI.query.filter(KPI.company_id == company_id)
        
        if kpi_category:
            query = query.filter(KPI.kpi_category == kpi_category)
        
        if kpi_type:
            query = query.filter(KPI.kpi_type == MetricType(kpi_type))
        
        kpis = query.order_by(KPI.created_at.desc()).limit(100).all()
        
        return jsonify([kpi.to_dict() for kpi in kpis])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_reporting_bp.route('/kpis', methods=['POST'])
@jwt_required()
def create_kpi():
    """Create KPI"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['kpi_name', 'kpi_category', 'kpi_type', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create KPI
        kpi = KPI(
            kpi_name=data['kpi_name'],
            kpi_description=data.get('kpi_description'),
            kpi_category=data['kpi_category'],
            kpi_type=MetricType(data['kpi_type']),
            calculation_formula=data.get('calculation_formula'),
            data_sources=data.get('data_sources'),
            update_frequency=ReportFrequency(data.get('update_frequency', 'DAILY')),
            current_value=data.get('current_value', 0.0),
            target_value=data.get('target_value', 0.0),
            previous_value=data.get('previous_value', 0.0),
            trend=data.get('trend', 'Stable'),
            company_id=data['company_id']
        )
        
        db.session.add(kpi)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('kpi_created', kpi.to_dict(), data['company_id'])
        
        return jsonify(kpi.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Data Visualizations
@analytics_reporting_bp.route('/visualizations', methods=['GET'])
@jwt_required()
def get_data_visualizations():
    """Get data visualizations"""
    try:
        company_id = request.args.get('company_id', type=int)
        visualization_type = request.args.get('visualization_type')
        is_public = request.args.get('is_public', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = DataVisualization.query.filter(DataVisualization.company_id == company_id)
        
        if visualization_type:
            query = query.filter(DataVisualization.visualization_type == visualization_type)
        
        if is_public is not None:
            query = query.filter(DataVisualization.is_public == is_public)
        
        visualizations = query.order_by(DataVisualization.last_updated.desc()).limit(100).all()
        
        return jsonify([visualization.to_dict() for visualization in visualizations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_reporting_bp.route('/visualizations', methods=['POST'])
@jwt_required()
def create_data_visualization():
    """Create data visualization"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['visualization_name', 'visualization_type', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create visualization
        visualization = DataVisualization(
            visualization_name=data['visualization_name'],
            visualization_description=data.get('visualization_description'),
            visualization_type=data['visualization_type'],
            chart_config=data.get('chart_config'),
            data_query=data.get('data_query'),
            filters=data.get('filters'),
            visualization_data=data.get('visualization_data'),
            is_public=data.get('is_public', False),
            allowed_users=data.get('allowed_users'),
            allowed_roles=data.get('allowed_roles'),
            company_id=data['company_id']
        )
        
        db.session.add(visualization)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('data_visualization_created', visualization.to_dict(), data['company_id'])
        
        return jsonify(visualization.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
