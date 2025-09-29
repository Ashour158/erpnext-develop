# Performance Optimization API
# API endpoints for performance optimization features including caching strategy, load balancing, and performance monitoring

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from .models import (
    CacheEntry, LoadBalancer, BackendServer, PerformanceMetric, PerformanceAlert,
    DatabaseOptimization, APIOptimization, PerformanceReport,
    CacheType, CacheStrategy, LoadBalancerType, PerformanceMetricType
)
from datetime import datetime, timedelta, date
import json

performance_optimization_bp = Blueprint('performance_optimization', __name__)

# Cache Management
@performance_optimization_bp.route('/cache', methods=['GET'])
@jwt_required()
def get_cache_entries():
    """Get cache entries"""
    try:
        company_id = request.args.get('company_id', type=int)
        cache_type = request.args.get('cache_type')
        cache_strategy = request.args.get('cache_strategy')
        expired = request.args.get('expired', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = CacheEntry.query.filter(CacheEntry.company_id == company_id)
        
        if cache_type:
            query = query.filter(CacheEntry.cache_type == CacheType(cache_type))
        
        if cache_strategy:
            query = query.filter(CacheEntry.cache_strategy == CacheStrategy(cache_strategy))
        
        if expired is not None:
            if expired:
                query = query.filter(CacheEntry.expires_at < datetime.utcnow())
            else:
                query = query.filter(CacheEntry.expires_at > datetime.utcnow())
        
        entries = query.order_by(CacheEntry.last_accessed.desc()).limit(1000).all()
        
        return jsonify([entry.to_dict() for entry in entries])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_optimization_bp.route('/cache', methods=['POST'])
@jwt_required()
def create_cache_entry():
    """Create cache entry"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['cache_key', 'cache_value', 'cache_type', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create cache entry
        entry = CacheEntry(
            cache_key=data['cache_key'],
            cache_value=data['cache_value'],
            cache_type=CacheType(data['cache_type']),
            cache_strategy=CacheStrategy(data.get('cache_strategy', 'TTL')),
            cache_size=data.get('cache_size', 0),
            hit_count=data.get('hit_count', 0),
            miss_count=data.get('miss_count', 0),
            access_count=data.get('access_count', 0),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            ttl=data.get('ttl', 3600),
            cache_config=data.get('cache_config'),
            tags=data.get('tags'),
            company_id=data['company_id']
        )
        
        db.session.add(entry)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('cache_entry_created', entry.to_dict(), data['company_id'])
        
        return jsonify(entry.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@performance_optimization_bp.route('/cache/<string:cache_key>', methods=['GET'])
@jwt_required()
def get_cache_entry(cache_key):
    """Get specific cache entry"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        entry = CacheEntry.query.filter(
            CacheEntry.cache_key == cache_key,
            CacheEntry.company_id == company_id
        ).first()
        
        if not entry:
            return jsonify({'error': 'Cache entry not found'}), 404
        
        # Update access statistics
        entry.access_count += 1
        entry.last_accessed = datetime.utcnow()
        db.session.commit()
        
        return jsonify(entry.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_optimization_bp.route('/cache/<string:cache_key>', methods=['DELETE'])
@jwt_required()
def delete_cache_entry(cache_key):
    """Delete cache entry"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        entry = CacheEntry.query.filter(
            CacheEntry.cache_key == cache_key,
            CacheEntry.company_id == company_id
        ).first()
        
        if not entry:
            return jsonify({'error': 'Cache entry not found'}), 404
        
        db.session.delete(entry)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('cache_entry_deleted', {'cache_key': cache_key}, company_id)
        
        return jsonify({'message': 'Cache entry deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Load Balancers
@performance_optimization_bp.route('/load-balancers', methods=['GET'])
@jwt_required()
def get_load_balancers():
    """Get load balancers"""
    try:
        company_id = request.args.get('company_id', type=int)
        balancer_type = request.args.get('balancer_type')
        is_active = request.args.get('is_active', type=bool)
        status = request.args.get('status')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = LoadBalancer.query.filter(LoadBalancer.company_id == company_id)
        
        if balancer_type:
            query = query.filter(LoadBalancer.balancer_type == LoadBalancerType(balancer_type))
        
        if is_active is not None:
            query = query.filter(LoadBalancer.is_active == is_active)
        
        if status:
            query = query.filter(LoadBalancer.status == status)
        
        balancers = query.order_by(LoadBalancer.created_at.desc()).all()
        
        return jsonify([balancer.to_dict() for balancer in balancers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_optimization_bp.route('/load-balancers', methods=['POST'])
@jwt_required()
def create_load_balancer():
    """Create load balancer"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['balancer_name', 'balancer_type', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create load balancer
        balancer = LoadBalancer(
            balancer_name=data['balancer_name'],
            balancer_description=data.get('balancer_description'),
            balancer_type=LoadBalancerType(data['balancer_type']),
            is_active=data.get('is_active', True),
            balancer_config=data.get('balancer_config'),
            health_check_config=data.get('health_check_config'),
            ssl_config=data.get('ssl_config'),
            backend_servers=data.get('backend_servers'),
            server_weights=data.get('server_weights'),
            status=data.get('status', 'Active'),
            last_health_check=datetime.fromisoformat(data['last_health_check']) if data.get('last_health_check') else None,
            health_check_interval=data.get('health_check_interval', 30),
            total_requests=data.get('total_requests', 0),
            successful_requests=data.get('successful_requests', 0),
            failed_requests=data.get('failed_requests', 0),
            average_response_time=data.get('average_response_time', 0.0),
            company_id=data['company_id']
        )
        
        db.session.add(balancer)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('load_balancer_created', balancer.to_dict(), data['company_id'])
        
        return jsonify(balancer.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Backend Servers
@performance_optimization_bp.route('/backend-servers', methods=['GET'])
@jwt_required()
def get_backend_servers():
    """Get backend servers"""
    try:
        company_id = request.args.get('company_id', type=int)
        load_balancer_id = request.args.get('load_balancer_id', type=int)
        is_active = request.args.get('is_active', type=bool)
        is_healthy = request.args.get('is_healthy', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = BackendServer.query.filter(BackendServer.company_id == company_id)
        
        if load_balancer_id:
            query = query.filter(BackendServer.load_balancer_id == load_balancer_id)
        
        if is_active is not None:
            query = query.filter(BackendServer.is_active == is_active)
        
        if is_healthy is not None:
            query = query.filter(BackendServer.is_healthy == is_healthy)
        
        servers = query.order_by(BackendServer.server_name).all()
        
        return jsonify([server.to_dict() for server in servers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_optimization_bp.route('/backend-servers', methods=['POST'])
@jwt_required()
def create_backend_server():
    """Create backend server"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['server_name', 'server_url', 'load_balancer_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create backend server
        server = BackendServer(
            server_name=data['server_name'],
            server_description=data.get('server_description'),
            server_url=data['server_url'],
            server_port=data.get('server_port', 80),
            server_protocol=data.get('server_protocol', 'http'),
            load_balancer_id=data['load_balancer_id'],
            server_weight=data.get('server_weight', 1),
            max_connections=data.get('max_connections', 100),
            timeout=data.get('timeout', 30),
            is_active=data.get('is_active', True),
            is_healthy=data.get('is_healthy', True),
            last_health_check=datetime.fromisoformat(data['last_health_check']) if data.get('last_health_check') else None,
            health_check_url=data.get('health_check_url'),
            current_connections=data.get('current_connections', 0),
            total_requests=data.get('total_requests', 0),
            successful_requests=data.get('successful_requests', 0),
            failed_requests=data.get('failed_requests', 0),
            average_response_time=data.get('average_response_time', 0.0),
            company_id=data['company_id']
        )
        
        db.session.add(server)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('backend_server_created', server.to_dict(), data['company_id'])
        
        return jsonify(server.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Performance Metrics
@performance_optimization_bp.route('/metrics', methods=['GET'])
@jwt_required()
def get_performance_metrics():
    """Get performance metrics"""
    try:
        company_id = request.args.get('company_id', type=int)
        metric_type = request.args.get('metric_type')
        resource_name = request.args.get('resource_name')
        component = request.args.get('component')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = PerformanceMetric.query.filter(PerformanceMetric.company_id == company_id)
        
        if metric_type:
            query = query.filter(PerformanceMetric.metric_type == PerformanceMetricType(metric_type))
        
        if resource_name:
            query = query.filter(PerformanceMetric.resource_name == resource_name)
        
        if component:
            query = query.filter(PerformanceMetric.component == component)
        
        if start_date:
            query = query.filter(PerformanceMetric.metric_timestamp >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(PerformanceMetric.metric_timestamp <= datetime.fromisoformat(end_date))
        
        metrics = query.order_by(PerformanceMetric.metric_timestamp.desc()).limit(1000).all()
        
        return jsonify([metric.to_dict() for metric in metrics])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_optimization_bp.route('/metrics', methods=['POST'])
@jwt_required()
def create_performance_metric():
    """Create performance metric"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['metric_name', 'metric_type', 'metric_value', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create performance metric
        metric = PerformanceMetric(
            metric_name=data['metric_name'],
            metric_type=PerformanceMetricType(data['metric_type']),
            metric_value=data['metric_value'],
            metric_unit=data.get('metric_unit', ''),
            resource_name=data.get('resource_name'),
            resource_id=data.get('resource_id'),
            component=data.get('component'),
            metric_timestamp=datetime.fromisoformat(data['metric_timestamp']) if data.get('metric_timestamp') else datetime.utcnow(),
            collection_interval=data.get('collection_interval', 60),
            metric_metadata=data.get('metric_metadata'),
            tags=data.get('tags'),
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

# Performance Alerts
@performance_optimization_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_performance_alerts():
    """Get performance alerts"""
    try:
        company_id = request.args.get('company_id', type=int)
        alert_type = request.args.get('alert_type')
        severity = request.args.get('severity')
        is_active = request.args.get('is_active', type=bool)
        is_triggered = request.args.get('is_triggered', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = PerformanceAlert.query.filter(PerformanceAlert.company_id == company_id)
        
        if alert_type:
            query = query.filter(PerformanceAlert.alert_type == alert_type)
        
        if severity:
            query = query.filter(PerformanceAlert.severity == severity)
        
        if is_active is not None:
            query = query.filter(PerformanceAlert.is_active == is_active)
        
        if is_triggered is not None:
            query = query.filter(PerformanceAlert.is_triggered == is_triggered)
        
        alerts = query.order_by(PerformanceAlert.created_at.desc()).all()
        
        return jsonify([alert.to_dict() for alert in alerts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_optimization_bp.route('/alerts', methods=['POST'])
@jwt_required()
def create_performance_alert():
    """Create performance alert"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['alert_name', 'alert_type', 'metric_name', 'threshold_value', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create performance alert
        alert = PerformanceAlert(
            alert_name=data['alert_name'],
            alert_description=data.get('alert_description'),
            alert_type=data['alert_type'],
            severity=data.get('severity', 'Medium'),
            metric_name=data['metric_name'],
            threshold_value=data['threshold_value'],
            comparison_operator=data.get('comparison_operator', '>'),
            alert_condition=data.get('alert_condition'),
            is_active=data.get('is_active', True),
            is_triggered=data.get('is_triggered', False),
            last_triggered=datetime.fromisoformat(data['last_triggered']) if data.get('last_triggered') else None,
            trigger_count=data.get('trigger_count', 0),
            alert_actions=data.get('alert_actions'),
            notification_recipients=data.get('notification_recipients'),
            company_id=data['company_id']
        )
        
        db.session.add(alert)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('performance_alert_created', alert.to_dict(), data['company_id'])
        
        return jsonify(alert.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Database Optimizations
@performance_optimization_bp.route('/database-optimizations', methods=['GET'])
@jwt_required()
def get_database_optimizations():
    """Get database optimizations"""
    try:
        company_id = request.args.get('company_id', type=int)
        optimization_type = request.args.get('optimization_type')
        database_name = request.args.get('database_name')
        is_applied = request.args.get('is_applied', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = DatabaseOptimization.query.filter(DatabaseOptimization.company_id == company_id)
        
        if optimization_type:
            query = query.filter(DatabaseOptimization.optimization_type == optimization_type)
        
        if database_name:
            query = query.filter(DatabaseOptimization.database_name == database_name)
        
        if is_applied is not None:
            query = query.filter(DatabaseOptimization.is_applied == is_applied)
        
        optimizations = query.order_by(DatabaseOptimization.created_at.desc()).all()
        
        return jsonify([optimization.to_dict() for optimization in optimizations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_optimization_bp.route('/database-optimizations', methods=['POST'])
@jwt_required()
def create_database_optimization():
    """Create database optimization"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['optimization_name', 'optimization_type', 'database_name', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create database optimization
        optimization = DatabaseOptimization(
            optimization_name=data['optimization_name'],
            optimization_description=data.get('optimization_description'),
            optimization_type=data['optimization_type'],
            database_name=data['database_name'],
            table_name=data.get('table_name'),
            query_text=data.get('query_text'),
            optimization_config=data.get('optimization_config'),
            optimization_sql=data.get('optimization_sql'),
            is_applied=data.get('is_applied', False),
            applied_at=datetime.fromisoformat(data['applied_at']) if data.get('applied_at') else None,
            applied_by=data.get('applied_by'),
            before_performance=data.get('before_performance'),
            after_performance=data.get('after_performance'),
            improvement_percentage=data.get('improvement_percentage', 0.0),
            company_id=data['company_id']
        )
        
        db.session.add(optimization)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('database_optimization_created', optimization.to_dict(), data['company_id'])
        
        return jsonify(optimization.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API Optimizations
@performance_optimization_bp.route('/api-optimizations', methods=['GET'])
@jwt_required()
def get_api_optimizations():
    """Get API optimizations"""
    try:
        company_id = request.args.get('company_id', type=int)
        optimization_type = request.args.get('optimization_type')
        api_endpoint = request.args.get('api_endpoint')
        is_active = request.args.get('is_active', type=bool)
        is_applied = request.args.get('is_applied', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = APIOptimization.query.filter(APIOptimization.company_id == company_id)
        
        if optimization_type:
            query = query.filter(APIOptimization.optimization_type == optimization_type)
        
        if api_endpoint:
            query = query.filter(APIOptimization.api_endpoint == api_endpoint)
        
        if is_active is not None:
            query = query.filter(APIOptimization.is_active == is_active)
        
        if is_applied is not None:
            query = query.filter(APIOptimization.is_applied == is_applied)
        
        optimizations = query.order_by(APIOptimization.created_at.desc()).all()
        
        return jsonify([optimization.to_dict() for optimization in optimizations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_optimization_bp.route('/api-optimizations', methods=['POST'])
@jwt_required()
def create_api_optimization():
    """Create API optimization"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['optimization_name', 'optimization_type', 'api_endpoint', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create API optimization
        optimization = APIOptimization(
            optimization_name=data['optimization_name'],
            optimization_description=data.get('optimization_description'),
            optimization_type=data['optimization_type'],
            api_endpoint=data['api_endpoint'],
            api_method=data.get('api_method', 'GET'),
            api_version=data.get('api_version', 'v1'),
            optimization_config=data.get('optimization_config'),
            cache_strategy=data.get('cache_strategy'),
            rate_limit_config=data.get('rate_limit_config'),
            compression_config=data.get('compression_config'),
            is_active=data.get('is_active', True),
            is_applied=data.get('is_applied', False),
            applied_at=datetime.fromisoformat(data['applied_at']) if data.get('applied_at') else None,
            applied_by=data.get('applied_by'),
            before_performance=data.get('before_performance'),
            after_performance=data.get('after_performance'),
            improvement_percentage=data.get('improvement_percentage', 0.0),
            company_id=data['company_id']
        )
        
        db.session.add(optimization)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('api_optimization_created', optimization.to_dict(), data['company_id'])
        
        return jsonify(optimization.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Performance Reports
@performance_optimization_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_performance_reports():
    """Get performance reports"""
    try:
        company_id = request.args.get('company_id', type=int)
        report_type = request.args.get('report_type')
        status = request.args.get('status')
        generated_by = request.args.get('generated_by', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = PerformanceReport.query.filter(PerformanceReport.company_id == company_id)
        
        if report_type:
            query = query.filter(PerformanceReport.report_type == report_type)
        
        if status:
            query = query.filter(PerformanceReport.status == status)
        
        if generated_by:
            query = query.filter(PerformanceReport.generated_by == generated_by)
        
        if start_date:
            query = query.filter(PerformanceReport.report_period_start >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(PerformanceReport.report_period_end <= datetime.fromisoformat(end_date))
        
        reports = query.order_by(PerformanceReport.generated_at.desc()).all()
        
        return jsonify([report.to_dict() for report in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_optimization_bp.route('/reports', methods=['POST'])
@jwt_required()
def create_performance_report():
    """Create performance report"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['report_name', 'report_type', 'report_period_start', 'report_period_end', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create performance report
        report = PerformanceReport(
            report_name=data['report_name'],
            report_description=data.get('report_description'),
            report_type=data['report_type'],
            report_period_start=datetime.fromisoformat(data['report_period_start']),
            report_period_end=datetime.fromisoformat(data['report_period_end']),
            status=data.get('status', 'Draft'),
            generated_by=user_id,
            report_data=data.get('report_data'),
            performance_summary=data.get('performance_summary'),
            recommendations=data.get('recommendations'),
            charts_data=data.get('charts_data'),
            company_id=data['company_id']
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('performance_report_created', report.to_dict(), data['company_id'])
        
        return jsonify(report.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
