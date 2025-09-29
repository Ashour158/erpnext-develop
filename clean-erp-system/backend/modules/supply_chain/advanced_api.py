# Advanced Supply Chain API Endpoints
# Intelligent supply chain management with demand forecasting, supplier management, and logistics optimization

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import require_auth, get_current_user
from .advanced_models import (
    DemandForecast, SafetyStock, Supplier, SupplierProduct, SupplierEvaluation,
    PurchaseOrder, PurchaseOrderItem, PurchaseOrderShipment, Warehouse, WarehouseLocation
)
from datetime import datetime, date
import json

# Create blueprint
advanced_supply_chain_bp = Blueprint('advanced_supply_chain', __name__, url_prefix='/advanced-supply-chain')

# Demand Forecasting Endpoints
@advanced_supply_chain_bp.route('/demand-forecasts', methods=['GET'])
@require_auth
def get_demand_forecasts():
    """Get all demand forecasts"""
    try:
        query = DemandForecast.query.filter_by(company_id=get_current_user().company_id)
        
        # Apply filters
        if request.args.get('item_id'):
            query = query.filter_by(item_id=request.args.get('item_id'))
        if request.args.get('forecast_method'):
            query = query.filter_by(forecast_method=request.args.get('forecast_method'))
        
        forecasts = query.all()
        return jsonify({
            'success': True,
            'data': [forecast.to_dict() for forecast in forecasts]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_supply_chain_bp.route('/demand-forecasts', methods=['POST'])
@require_auth
def create_demand_forecast():
    """Create a new demand forecast"""
    try:
        data = request.get_json()
        forecast = DemandForecast(
            forecast_name=data['forecast_name'],
            forecast_period_start=datetime.strptime(data['forecast_period_start'], '%Y-%m-%d').date(),
            forecast_period_end=datetime.strptime(data['forecast_period_end'], '%Y-%m-%d').date(),
            forecast_method=data['forecast_method'],
            item_id=data['item_id'],
            forecasted_quantity=data.get('forecasted_quantity', 0.0),
            actual_quantity=data.get('actual_quantity', 0.0),
            forecast_accuracy=data.get('forecast_accuracy', 0.0),
            confidence_level=data.get('confidence_level', 0.0),
            forecast_parameters=data.get('forecast_parameters', {}),
            seasonal_factors=data.get('seasonal_factors', {}),
            trend_factors=data.get('trend_factors', {}),
            company_id=get_current_user().company_id
        )
        db.session.add(forecast)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': forecast.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_supply_chain_bp.route('/demand-forecasts/<int:forecast_id>/calculate', methods=['POST'])
@require_auth
def calculate_demand_forecast(forecast_id):
    """Calculate demand forecast using specified method"""
    try:
        forecast = DemandForecast.query.get_or_404(forecast_id)
        data = request.get_json()
        
        # This would integrate with actual forecasting algorithms
        # For now, we'll simulate the calculation
        historical_data = data.get('historical_data', [])
        method = forecast.forecast_method.value
        
        # Simulate forecast calculation based on method
        if method == 'Moving Average':
            # Simple moving average calculation
            if len(historical_data) >= 3:
                forecast.forecasted_quantity = sum(historical_data[-3:]) / 3
        elif method == 'Exponential Smoothing':
            # Exponential smoothing calculation
            alpha = forecast.forecast_parameters.get('alpha', 0.3)
            if historical_data:
                forecast.forecasted_quantity = historical_data[-1] * alpha + (1 - alpha) * forecast.forecasted_quantity
        elif method == 'Machine Learning':
            # ML-based forecasting (would integrate with ML models)
            forecast.forecasted_quantity = sum(historical_data) / len(historical_data) if historical_data else 0
        
        # Calculate confidence level based on historical accuracy
        if historical_data:
            forecast.confidence_level = min(95.0, max(50.0, 100 - (len(historical_data) * 5)))
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': forecast.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Safety Stock Management Endpoints
@advanced_supply_chain_bp.route('/safety-stocks', methods=['GET'])
@require_auth
def get_safety_stocks():
    """Get all safety stock levels"""
    try:
        safety_stocks = SafetyStock.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [stock.to_dict() for stock in safety_stocks]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_supply_chain_bp.route('/safety-stocks', methods=['POST'])
@require_auth
def create_safety_stock():
    """Create a new safety stock entry"""
    try:
        data = request.get_json()
        safety_stock = SafetyStock(
            item_id=data['item_id'],
            current_stock=data.get('current_stock', 0.0),
            safety_stock_level=data.get('safety_stock_level', 0.0),
            reorder_point=data.get('reorder_point', 0.0),
            reorder_quantity=data.get('reorder_quantity', 0.0),
            lead_time_days=data.get('lead_time_days', 0),
            demand_variability=data.get('demand_variability', 0.0),
            lead_time_variability=data.get('lead_time_variability', 0.0),
            service_level=data.get('service_level', 95.0),
            abc_classification=data.get('abc_classification'),
            item_value=data.get('item_value', 0.0),
            annual_usage_value=data.get('annual_usage_value', 0.0),
            company_id=get_current_user().company_id
        )
        db.session.add(safety_stock)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': safety_stock.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_supply_chain_bp.route('/safety-stocks/<int:stock_id>/calculate', methods=['POST'])
@require_auth
def calculate_safety_stock(stock_id):
    """Calculate optimal safety stock level"""
    try:
        safety_stock = SafetyStock.query.get_or_404(stock_id)
        
        # Calculate safety stock using statistical methods
        # Formula: Safety Stock = Z * sqrt(Lead Time * Demand Variance + Demand^2 * Lead Time Variance)
        # Where Z is the service level factor
        
        service_level = safety_stock.service_level / 100
        z_factor = 1.96 if service_level >= 0.95 else 1.65 if service_level >= 0.90 else 1.28
        
        lead_time_variance = safety_stock.lead_time_variability ** 2
        demand_variance = safety_stock.demand_variability ** 2
        
        safety_stock.safety_stock_level = z_factor * (safety_stock.lead_time_days * demand_variance + 
                                                     safety_stock.demand_variability ** 2 * lead_time_variance) ** 0.5
        
        # Calculate reorder point
        safety_stock.reorder_point = safety_stock.safety_stock_level + (safety_stock.demand_variability * safety_stock.lead_time_days)
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': safety_stock.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Advanced Supplier Management Endpoints
@advanced_supply_chain_bp.route('/suppliers', methods=['GET'])
@require_auth
def get_suppliers():
    """Get all suppliers with advanced filtering"""
    try:
        query = Supplier.query.filter_by(company_id=get_current_user().company_id)
        
        # Apply filters
        if request.args.get('rating'):
            query = query.filter_by(overall_rating=request.args.get('rating'))
        if request.args.get('is_preferred'):
            query = query.filter_by(is_preferred=request.args.get('is_preferred') == 'true')
        if request.args.get('is_active'):
            query = query.filter_by(is_active=request.args.get('is_active') == 'true')
        
        suppliers = query.all()
        return jsonify({
            'success': True,
            'data': [supplier.to_dict() for supplier in suppliers]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_supply_chain_bp.route('/suppliers', methods=['POST'])
@require_auth
def create_supplier():
    """Create a new supplier"""
    try:
        data = request.get_json()
        supplier = Supplier(
            supplier_name=data['supplier_name'],
            supplier_code=data['supplier_code'],
            contact_person=data.get('contact_person'),
            email=data.get('email'),
            phone=data.get('phone'),
            website=data.get('website'),
            address_line1=data.get('address_line1'),
            address_line2=data.get('address_line2'),
            city=data.get('city'),
            state=data.get('state'),
            postal_code=data.get('postal_code'),
            country=data.get('country'),
            tax_id=data.get('tax_id'),
            business_type=data.get('business_type'),
            industry=data.get('industry'),
            years_in_business=data.get('years_in_business', 0),
            overall_rating=data.get('overall_rating', 'Average'),
            quality_rating=data.get('quality_rating', 0.0),
            delivery_rating=data.get('delivery_rating', 0.0),
            price_rating=data.get('price_rating', 0.0),
            service_rating=data.get('service_rating', 0.0),
            credit_limit=data.get('credit_limit', 0.0),
            payment_terms=data.get('payment_terms'),
            currency=data.get('currency', 'USD'),
            is_active=data.get('is_active', True),
            is_preferred=data.get('is_preferred', False),
            is_blacklisted=data.get('is_blacklisted', False),
            company_id=get_current_user().company_id
        )
        db.session.add(supplier)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': supplier.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_supply_chain_bp.route('/suppliers/<int:supplier_id>/products', methods=['POST'])
@require_auth
def add_supplier_product(supplier_id):
    """Add a product to a supplier"""
    try:
        data = request.get_json()
        product = SupplierProduct(
            product_code=data['product_code'],
            product_name=data['product_name'],
            product_description=data.get('product_description'),
            supplier_id=supplier_id,
            item_id=data.get('item_id'),
            unit_price=data.get('unit_price', 0.0),
            currency=data.get('currency', 'USD'),
            minimum_order_quantity=data.get('minimum_order_quantity', 1.0),
            lead_time_days=data.get('lead_time_days', 0),
            specifications=data.get('specifications', {}),
            certifications=data.get('certifications', {}),
            compliance_info=data.get('compliance_info', {}),
            company_id=get_current_user().company_id
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': product.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_supply_chain_bp.route('/suppliers/<int:supplier_id>/evaluate', methods=['POST'])
@require_auth
def evaluate_supplier(supplier_id):
    """Evaluate a supplier"""
    try:
        data = request.get_json()
        evaluation = SupplierEvaluation(
            evaluation_date=datetime.strptime(data['evaluation_date'], '%Y-%m-%d').date() if data.get('evaluation_date') else date.today(),
            evaluation_period_start=datetime.strptime(data['evaluation_period_start'], '%Y-%m-%d').date(),
            evaluation_period_end=datetime.strptime(data['evaluation_period_end'], '%Y-%m-%d').date(),
            supplier_id=supplier_id,
            quality_score=data.get('quality_score', 0.0),
            delivery_score=data.get('delivery_score', 0.0),
            price_score=data.get('price_score', 0.0),
            service_score=data.get('service_score', 0.0),
            overall_score=data.get('overall_score', 0.0),
            on_time_delivery_rate=data.get('on_time_delivery_rate', 0.0),
            quality_acceptance_rate=data.get('quality_acceptance_rate', 0.0),
            average_lead_time=data.get('average_lead_time', 0.0),
            price_variance=data.get('price_variance', 0.0),
            strengths=data.get('strengths'),
            weaknesses=data.get('weaknesses'),
            improvement_recommendations=data.get('improvement_recommendations'),
            action_plan=data.get('action_plan'),
            company_id=get_current_user().company_id
        )
        db.session.add(evaluation)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': evaluation.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Advanced Purchase Order Management
@advanced_supply_chain_bp.route('/purchase-orders', methods=['GET'])
@require_auth
def get_purchase_orders():
    """Get all purchase orders with advanced filtering"""
    try:
        query = PurchaseOrder.query.filter_by(company_id=get_current_user().company_id)
        
        # Apply filters
        if request.args.get('supplier_id'):
            query = query.filter_by(supplier_id=request.args.get('supplier_id'))
        if request.args.get('status'):
            query = query.filter_by(status=request.args.get('status'))
        if request.args.get('date_from'):
            query = query.filter(PurchaseOrder.order_date >= datetime.strptime(request.args.get('date_from'), '%Y-%m-%d').date())
        if request.args.get('date_to'):
            query = query.filter(PurchaseOrder.order_date <= datetime.strptime(request.args.get('date_to'), '%Y-%m-%d').date())
        
        orders = query.all()
        return jsonify({
            'success': True,
            'data': [order.to_dict() for order in orders]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_supply_chain_bp.route('/purchase-orders', methods=['POST'])
@require_auth
def create_purchase_order():
    """Create a new purchase order"""
    try:
        data = request.get_json()
        
        # Generate order number
        order_number = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        order = PurchaseOrder(
            order_number=order_number,
            order_date=datetime.strptime(data['order_date'], '%Y-%m-%d').date() if data.get('order_date') else date.today(),
            expected_delivery_date=datetime.strptime(data['expected_delivery_date'], '%Y-%m-%d').date() if data.get('expected_delivery_date') else None,
            supplier_id=data['supplier_id'],
            total_amount=data.get('total_amount', 0.0),
            currency=data.get('currency', 'USD'),
            status=data.get('status', 'Draft'),
            shipping_address=data.get('shipping_address', {}),
            shipping_method=data.get('shipping_method'),
            shipping_cost=data.get('shipping_cost', 0.0),
            tracking_number=data.get('tracking_number'),
            payment_terms=data.get('payment_terms'),
            delivery_terms=data.get('delivery_terms'),
            special_instructions=data.get('special_instructions'),
            approved_by_id=data.get('approved_by_id'),
            company_id=get_current_user().company_id
        )
        
        # Add order items
        for item_data in data.get('order_items', []):
            item = PurchaseOrderItem(
                item_id=item_data['item_id'],
                quantity_ordered=item_data.get('quantity_ordered', 0.0),
                unit_price=item_data.get('unit_price', 0.0),
                line_total=item_data.get('line_total', 0.0),
                expected_delivery_date=datetime.strptime(item_data['expected_delivery_date'], '%Y-%m-%d').date() if item_data.get('expected_delivery_date') else None,
                company_id=get_current_user().company_id
            )
            order.order_items.append(item)
        
        db.session.add(order)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': order.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_supply_chain_bp.route('/purchase-orders/<int:order_id>/approve', methods=['POST'])
@require_auth
def approve_purchase_order(order_id):
    """Approve a purchase order"""
    try:
        order = PurchaseOrder.query.get_or_404(order_id)
        data = request.get_json()
        
        order.status = 'Approved'
        order.approved_by_id = data.get('approved_by_id', get_current_user().id)
        order.approved_date = datetime.utcnow()
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': order.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Warehouse Management Endpoints
@advanced_supply_chain_bp.route('/warehouses', methods=['GET'])
@require_auth
def get_warehouses():
    """Get all warehouses"""
    try:
        warehouses = Warehouse.query.filter_by(company_id=get_current_user().company_id).all()
        return jsonify({
            'success': True,
            'data': [warehouse.to_dict() for warehouse in warehouses]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_supply_chain_bp.route('/warehouses', methods=['POST'])
@require_auth
def create_warehouse():
    """Create a new warehouse"""
    try:
        data = request.get_json()
        warehouse = Warehouse(
            warehouse_name=data['warehouse_name'],
            warehouse_code=data['warehouse_code'],
            warehouse_type=data.get('warehouse_type', 'Main'),
            address_line1=data.get('address_line1'),
            address_line2=data.get('address_line2'),
            city=data.get('city'),
            state=data.get('state'),
            postal_code=data.get('postal_code'),
            country=data.get('country'),
            total_capacity=data.get('total_capacity', 0.0),
            used_capacity=data.get('used_capacity', 0.0),
            capacity_unit=data.get('capacity_unit', 'sqft'),
            manager_id=data.get('manager_id'),
            is_active=data.get('is_active', True),
            is_automated=data.get('is_automated', False),
            company_id=get_current_user().company_id
        )
        db.session.add(warehouse)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': warehouse.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_supply_chain_bp.route('/warehouses/<int:warehouse_id>/locations', methods=['POST'])
@require_auth
def add_warehouse_location(warehouse_id):
    """Add a location to a warehouse"""
    try:
        data = request.get_json()
        location = WarehouseLocation(
            location_code=data['location_code'],
            location_name=data['location_name'],
            location_type=data.get('location_type', 'Shelf'),
            warehouse_id=warehouse_id,
            capacity=data.get('capacity', 0.0),
            used_capacity=data.get('used_capacity', 0.0),
            location_path=data.get('location_path'),
            is_active=data.get('is_active', True),
            is_restricted=data.get('is_restricted', False),
            company_id=get_current_user().company_id
        )
        db.session.add(location)
        db.session.commit()
        return jsonify({
            'success': True,
            'data': location.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Analytics Endpoints
@advanced_supply_chain_bp.route('/analytics/inventory-abc', methods=['GET'])
@require_auth
def get_inventory_abc_analysis():
    """Get ABC analysis of inventory"""
    try:
        safety_stocks = SafetyStock.query.filter_by(company_id=get_current_user().company_id).all()
        
        # Calculate ABC classification
        abc_data = {'A': [], 'B': [], 'C': []}
        for stock in safety_stocks:
            classification = stock.abc_classification.value if stock.abc_classification else 'C'
            abc_data[classification].append({
                'item_id': stock.item_id,
                'item_name': stock.item.item_name if stock.item else 'Unknown',
                'annual_usage_value': stock.annual_usage_value,
                'current_stock': stock.current_stock,
                'safety_stock_level': stock.safety_stock_level
            })
        
        return jsonify({
            'success': True,
            'data': abc_data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_supply_chain_bp.route('/analytics/supplier-performance', methods=['GET'])
@require_auth
def get_supplier_performance():
    """Get supplier performance analytics"""
    try:
        suppliers = Supplier.query.filter_by(company_id=get_current_user().company_id).all()
        
        performance_data = []
        for supplier in suppliers:
            # Get latest evaluation
            latest_evaluation = SupplierEvaluation.query.filter_by(
                supplier_id=supplier.id
            ).order_by(SupplierEvaluation.evaluation_date.desc()).first()
            
            performance_data.append({
                'supplier_id': supplier.id,
                'supplier_name': supplier.supplier_name,
                'overall_rating': supplier.overall_rating.value if supplier.overall_rating else None,
                'quality_rating': supplier.quality_rating,
                'delivery_rating': supplier.delivery_rating,
                'price_rating': supplier.price_rating,
                'service_rating': supplier.service_rating,
                'on_time_delivery_rate': latest_evaluation.on_time_delivery_rate if latest_evaluation else 0.0,
                'quality_acceptance_rate': latest_evaluation.quality_acceptance_rate if latest_evaluation else 0.0,
                'average_lead_time': latest_evaluation.average_lead_time if latest_evaluation else 0.0
            })
        
        return jsonify({
            'success': True,
            'data': performance_data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@advanced_supply_chain_bp.route('/analytics/demand-forecast-accuracy', methods=['GET'])
@require_auth
def get_forecast_accuracy():
    """Get demand forecast accuracy analytics"""
    try:
        forecasts = DemandForecast.query.filter_by(company_id=get_current_user().company_id).all()
        
        accuracy_data = []
        total_accuracy = 0.0
        count = 0
        
        for forecast in forecasts:
            if forecast.actual_quantity > 0:
                accuracy = abs(forecast.forecasted_quantity - forecast.actual_quantity) / forecast.actual_quantity * 100
                accuracy_data.append({
                    'forecast_id': forecast.id,
                    'forecast_name': forecast.forecast_name,
                    'item_name': forecast.item.item_name if forecast.item else 'Unknown',
                    'forecasted_quantity': forecast.forecasted_quantity,
                    'actual_quantity': forecast.actual_quantity,
                    'accuracy_percentage': 100 - accuracy,
                    'forecast_method': forecast.forecast_method.value if forecast.forecast_method else None
                })
                total_accuracy += (100 - accuracy)
                count += 1
        
        average_accuracy = total_accuracy / count if count > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'forecast_accuracy': accuracy_data,
                'average_accuracy': average_accuracy,
                'total_forecasts': len(forecasts),
                'forecasts_with_actuals': count
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
