# Maintenance API - Complete Asset and Maintenance Management API
# Advanced maintenance operations without Frappe dependencies

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import token_required, get_current_user
from .models import (
    Asset, AssetCategory, AssetLocation, MaintenanceSchedule, MaintenanceTask,
    WorkOrder, SparePart, MaintenanceTeam
)
from datetime import datetime, date, timedelta
import json

maintenance_api = Blueprint('maintenance_api', __name__)

# Asset Category Management
@maintenance_api.route('/asset-categories', methods=['GET'])
@token_required
def get_asset_categories():
    """Get all asset categories"""
    try:
        company_id = request.args.get('company_id')
        categories = AssetCategory.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [category.to_dict() for category in categories]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@maintenance_api.route('/asset-categories', methods=['POST'])
@token_required
def create_asset_category():
    """Create new asset category"""
    try:
        data = request.get_json()
        category = AssetCategory(
            category_name=data['category_name'],
            category_code=data['category_code'],
            description=data.get('description'),
            depreciation_method=data.get('depreciation_method'),
            useful_life_years=data.get('useful_life_years', 0),
            residual_value=data.get('residual_value', 0),
            company_id=data['company_id']
        )
        db.session.add(category)
        db.session.commit()
        return jsonify({'success': True, 'data': category.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Asset Location Management
@maintenance_api.route('/asset-locations', methods=['GET'])
@token_required
def get_asset_locations():
    """Get all asset locations"""
    try:
        company_id = request.args.get('company_id')
        locations = AssetLocation.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [location.to_dict() for location in locations]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@maintenance_api.route('/asset-locations', methods=['POST'])
@token_required
def create_asset_location():
    """Create new asset location"""
    try:
        data = request.get_json()
        location = AssetLocation(
            location_name=data['location_name'],
            location_code=data['location_code'],
            description=data.get('description'),
            address_line_1=data.get('address_line_1'),
            city=data.get('city'),
            state=data.get('state'),
            postal_code=data.get('postal_code'),
            country=data.get('country'),
            location_manager_id=data.get('location_manager_id'),
            company_id=data['company_id']
        )
        db.session.add(location)
        db.session.commit()
        return jsonify({'success': True, 'data': location.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Asset Management
@maintenance_api.route('/assets', methods=['GET'])
@token_required
def get_assets():
    """Get all assets"""
    try:
        company_id = request.args.get('company_id')
        category_id = request.args.get('category_id')
        location_id = request.args.get('location_id')
        status = request.args.get('status')
        
        query = Asset.query.filter_by(company_id=company_id)
        if category_id:
            query = query.filter_by(asset_category_id=category_id)
        if location_id:
            query = query.filter_by(asset_location_id=location_id)
        if status:
            query = query.filter_by(status=status)
        
        assets = query.all()
        return jsonify({
            'success': True,
            'data': [asset.to_dict() for asset in assets]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@maintenance_api.route('/assets', methods=['POST'])
@token_required
def create_asset():
    """Create new asset"""
    try:
        data = request.get_json()
        asset = Asset(
            asset_name=data['asset_name'],
            asset_code=data['asset_code'],
            description=data.get('description'),
            asset_category_id=data['asset_category_id'],
            asset_location_id=data.get('asset_location_id'),
            manufacturer=data.get('manufacturer'),
            model_number=data.get('model_number'),
            serial_number=data.get('serial_number'),
            purchase_date=datetime.fromisoformat(data['purchase_date']).date() if data.get('purchase_date') else None,
            warranty_expiry_date=datetime.fromisoformat(data['warranty_expiry_date']).date() if data.get('warranty_expiry_date') else None,
            purchase_cost=data.get('purchase_cost', 0),
            current_value=data.get('current_value', 0),
            currency=data.get('currency', 'USD'),
            status=data.get('status', 'Active'),
            is_critical=data.get('is_critical', False),
            maintenance_frequency_days=data.get('maintenance_frequency_days', 0),
            custodian_id=data.get('custodian_id'),
            company_id=data['company_id']
        )
        db.session.add(asset)
        db.session.commit()
        return jsonify({'success': True, 'data': asset.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@maintenance_api.route('/assets/<int:asset_id>', methods=['GET'])
@token_required
def get_asset(asset_id):
    """Get specific asset"""
    try:
        asset = Asset.query.get_or_404(asset_id)
        return jsonify({'success': True, 'data': asset.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Maintenance Team Management
@maintenance_api.route('/maintenance-teams', methods=['GET'])
@token_required
def get_maintenance_teams():
    """Get all maintenance teams"""
    try:
        company_id = request.args.get('company_id')
        teams = MaintenanceTeam.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [team.to_dict() for team in teams]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@maintenance_api.route('/maintenance-teams', methods=['POST'])
@token_required
def create_maintenance_team():
    """Create new maintenance team"""
    try:
        data = request.get_json()
        team = MaintenanceTeam(
            team_name=data['team_name'],
            team_code=data['team_code'],
            description=data.get('description'),
            team_lead_id=data.get('team_lead_id'),
            team_members=data.get('team_members', []),
            specialization=data.get('specialization'),
            skills=data.get('skills', []),
            company_id=data['company_id']
        )
        db.session.add(team)
        db.session.commit()
        return jsonify({'success': True, 'data': team.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Maintenance Schedule Management
@maintenance_api.route('/maintenance-schedules', methods=['GET'])
@token_required
def get_maintenance_schedules():
    """Get maintenance schedules"""
    try:
        company_id = request.args.get('company_id')
        asset_id = request.args.get('asset_id')
        maintenance_type = request.args.get('maintenance_type')
        
        query = MaintenanceSchedule.query.filter_by(company_id=company_id)
        if asset_id:
            query = query.filter_by(asset_id=asset_id)
        if maintenance_type:
            query = query.filter_by(maintenance_type=maintenance_type)
        
        schedules = query.all()
        return jsonify({
            'success': True,
            'data': [schedule.to_dict() for schedule in schedules]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@maintenance_api.route('/maintenance-schedules', methods=['POST'])
@token_required
def create_maintenance_schedule():
    """Create maintenance schedule"""
    try:
        data = request.get_json()
        schedule = MaintenanceSchedule(
            asset_id=data['asset_id'],
            schedule_name=data['schedule_name'],
            maintenance_type=data['maintenance_type'],
            start_date=datetime.fromisoformat(data['start_date']).date(),
            end_date=datetime.fromisoformat(data['end_date']).date(),
            frequency_days=data.get('frequency_days', 0),
            description=data.get('description'),
            instructions=data.get('instructions'),
            estimated_duration_hours=data.get('estimated_duration_hours', 0),
            is_recurring=data.get('is_recurring', True),
            company_id=data['company_id']
        )
        db.session.add(schedule)
        db.session.commit()
        return jsonify({'success': True, 'data': schedule.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Maintenance Task Management
@maintenance_api.route('/maintenance-tasks', methods=['GET'])
@token_required
def get_maintenance_tasks():
    """Get maintenance tasks"""
    try:
        company_id = request.args.get('company_id')
        schedule_id = request.args.get('schedule_id')
        assigned_to_id = request.args.get('assigned_to_id')
        status = request.args.get('status')
        
        query = MaintenanceTask.query.filter_by(company_id=company_id)
        if schedule_id:
            query = query.filter_by(schedule_id=schedule_id)
        if assigned_to_id:
            query = query.filter_by(assigned_to_id=assigned_to_id)
        if status:
            query = query.filter_by(status=status)
        
        tasks = query.all()
        return jsonify({
            'success': True,
            'data': [task.to_dict() for task in tasks]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@maintenance_api.route('/maintenance-tasks', methods=['POST'])
@token_required
def create_maintenance_task():
    """Create maintenance task"""
    try:
        data = request.get_json()
        task = MaintenanceTask(
            schedule_id=data['schedule_id'],
            task_name=data['task_name'],
            task_description=data.get('task_description'),
            instructions=data.get('instructions'),
            estimated_duration_hours=data.get('estimated_duration_hours', 0),
            priority=data.get('priority', 'Medium'),
            assigned_to_id=data.get('assigned_to_id'),
            company_id=data['company_id']
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({'success': True, 'data': task.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Work Order Management
@maintenance_api.route('/work-orders', methods=['GET'])
@token_required
def get_work_orders():
    """Get work orders"""
    try:
        company_id = request.args.get('company_id')
        asset_id = request.args.get('asset_id')
        assigned_team_id = request.args.get('assigned_team_id')
        status = request.args.get('status')
        priority = request.args.get('priority')
        
        query = WorkOrder.query.filter_by(company_id=company_id)
        if asset_id:
            query = query.filter_by(asset_id=asset_id)
        if assigned_team_id:
            query = query.filter_by(assigned_team_id=assigned_team_id)
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=priority)
        
        work_orders = query.all()
        return jsonify({
            'success': True,
            'data': [order.to_dict() for order in work_orders]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@maintenance_api.route('/work-orders', methods=['POST'])
@token_required
def create_work_order():
    """Create work order"""
    try:
        data = request.get_json()
        work_order = WorkOrder(
            work_order_number=data['work_order_number'],
            work_order_date=datetime.fromisoformat(data['work_order_date']),
            asset_id=data['asset_id'],
            assigned_team_id=data.get('assigned_team_id'),
            title=data['title'],
            description=data.get('description'),
            instructions=data.get('instructions'),
            priority=data.get('priority', 'Medium'),
            scheduled_start_date=datetime.fromisoformat(data['scheduled_start_date']) if data.get('scheduled_start_date') else None,
            scheduled_end_date=datetime.fromisoformat(data['scheduled_end_date']) if data.get('scheduled_end_date') else None,
            estimated_cost=data.get('estimated_cost', 0),
            currency=data.get('currency', 'USD'),
            notes=data.get('notes'),
            company_id=data['company_id']
        )
        db.session.add(work_order)
        db.session.commit()
        return jsonify({'success': True, 'data': work_order.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@maintenance_api.route('/work-orders/<int:work_order_id>/update-status', methods=['POST'])
@token_required
def update_work_order_status(work_order_id):
    """Update work order status"""
    try:
        data = request.get_json()
        work_order = WorkOrder.query.get_or_404(work_order_id)
        work_order.status = data['status']
        
        if data['status'] == 'In Progress' and not work_order.actual_start_date:
            work_order.actual_start_date = datetime.now()
        elif data['status'] == 'Completed' and not work_order.actual_end_date:
            work_order.actual_end_date = datetime.now()
            work_order.completion_notes = data.get('completion_notes')
        
        db.session.commit()
        return jsonify({'success': True, 'data': work_order.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Spare Part Management
@maintenance_api.route('/spare-parts', methods=['GET'])
@token_required
def get_spare_parts():
    """Get spare parts"""
    try:
        company_id = request.args.get('company_id')
        category = request.args.get('category')
        is_critical = request.args.get('is_critical')
        
        query = SparePart.query.filter_by(company_id=company_id)
        if category:
            query = query.filter_by(category=category)
        if is_critical:
            query = query.filter_by(is_critical=is_critical.lower() == 'true')
        
        spare_parts = query.all()
        return jsonify({
            'success': True,
            'data': [part.to_dict() for part in spare_parts]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@maintenance_api.route('/spare-parts', methods=['POST'])
@token_required
def create_spare_part():
    """Create spare part"""
    try:
        data = request.get_json()
        spare_part = SparePart(
            part_name=data['part_name'],
            part_number=data['part_number'],
            description=data.get('description'),
            manufacturer=data.get('manufacturer'),
            model_number=data.get('model_number'),
            category=data.get('category'),
            current_stock=data.get('current_stock', 0),
            minimum_stock_level=data.get('minimum_stock_level', 0),
            maximum_stock_level=data.get('maximum_stock_level', 0),
            reorder_level=data.get('reorder_level', 0),
            unit_cost=data.get('unit_cost', 0),
            currency=data.get('currency', 'USD'),
            supplier_id=data.get('supplier_id'),
            is_critical=data.get('is_critical', False),
            company_id=data['company_id']
        )
        db.session.add(spare_part)
        db.session.commit()
        return jsonify({'success': True, 'data': spare_part.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Analytics and Reporting
@maintenance_api.route('/maintenance-analytics', methods=['GET'])
@token_required
def get_maintenance_analytics():
    """Get maintenance analytics"""
    try:
        company_id = request.args.get('company_id')
        
        # Calculate analytics
        total_assets = Asset.query.filter_by(company_id=company_id).count()
        active_assets = Asset.query.filter_by(company_id=company_id, status='Active').count()
        under_maintenance = Asset.query.filter_by(company_id=company_id, status='Under Maintenance').count()
        
        total_work_orders = WorkOrder.query.filter_by(company_id=company_id).count()
        completed_work_orders = WorkOrder.query.filter_by(company_id=company_id, status='Completed').count()
        pending_work_orders = WorkOrder.query.filter_by(company_id=company_id, status='Draft').count()
        
        analytics = {
            'total_assets': total_assets,
            'active_assets': active_assets,
            'under_maintenance': under_maintenance,
            'total_work_orders': total_work_orders,
            'completed_work_orders': completed_work_orders,
            'pending_work_orders': pending_work_orders,
            'completion_rate': (completed_work_orders / total_work_orders * 100) if total_work_orders > 0 else 0
        }
        
        return jsonify({'success': True, 'data': analytics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
