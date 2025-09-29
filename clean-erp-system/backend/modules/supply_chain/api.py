# Supply Chain API - Complete Supply Chain Management API
# Advanced inventory and procurement operations without Frappe dependencies

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import token_required, get_current_user
from .models import (
    Supplier, Item, ItemGroup, Warehouse, StockEntry, PurchaseOrder,
    SalesOrder, StockMovement, ItemPrice, ItemVariant, BOM, ProductionOrder
)
from datetime import datetime, date, timedelta
import json

supply_chain_api = Blueprint('supply_chain_api', __name__)

# Supplier Management
@supply_chain_api.route('/suppliers', methods=['GET'])
@token_required
def get_suppliers():
    """Get all suppliers"""
    try:
        company_id = request.args.get('company_id')
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        
        query = Supplier.query.filter_by(company_id=company_id)
        if is_active:
            query = query.filter_by(is_active=True)
        
        suppliers = query.all()
        return jsonify({
            'success': True,
            'data': [supplier.to_dict() for supplier in suppliers]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@supply_chain_api.route('/suppliers', methods=['POST'])
@token_required
def create_supplier():
    """Create new supplier"""
    try:
        data = request.get_json()
        supplier = Supplier(
            supplier_name=data['supplier_name'],
            supplier_code=data['supplier_code'],
            contact_person=data.get('contact_person'),
            email=data.get('email'),
            phone=data.get('phone'),
            website=data.get('website'),
            address_line_1=data.get('address_line_1'),
            city=data.get('city'),
            state=data.get('state'),
            postal_code=data.get('postal_code'),
            country=data.get('country'),
            tax_id=data.get('tax_id'),
            credit_limit=data.get('credit_limit', 0),
            currency=data.get('currency', 'USD'),
            company_id=data['company_id']
        )
        db.session.add(supplier)
        db.session.commit()
        return jsonify({'success': True, 'data': supplier.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Item Group Management
@supply_chain_api.route('/item-groups', methods=['GET'])
@token_required
def get_item_groups():
    """Get all item groups"""
    try:
        company_id = request.args.get('company_id')
        item_groups = ItemGroup.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [group.to_dict() for group in item_groups]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@supply_chain_api.route('/item-groups', methods=['POST'])
@token_required
def create_item_group():
    """Create new item group"""
    try:
        data = request.get_json()
        item_group = ItemGroup(
            group_name=data['group_name'],
            group_code=data['group_code'],
            description=data.get('description'),
            parent_group_id=data.get('parent_group_id'),
            company_id=data['company_id']
        )
        db.session.add(item_group)
        db.session.commit()
        return jsonify({'success': True, 'data': item_group.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Item Management
@supply_chain_api.route('/items', methods=['GET'])
@token_required
def get_items():
    """Get all items"""
    try:
        company_id = request.args.get('company_id')
        item_group_id = request.args.get('item_group_id')
        item_type = request.args.get('item_type')
        stock_status = request.args.get('stock_status')
        
        query = Item.query.filter_by(company_id=company_id)
        if item_group_id:
            query = query.filter_by(item_group_id=item_group_id)
        if item_type:
            query = query.filter_by(item_type=item_type)
        if stock_status:
            query = query.filter_by(stock_status=stock_status)
        
        items = query.all()
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in items]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@supply_chain_api.route('/items', methods=['POST'])
@token_required
def create_item():
    """Create new item"""
    try:
        data = request.get_json()
        item = Item(
            item_name=data['item_name'],
            item_code=data['item_code'],
            description=data.get('description'),
            item_type=data['item_type'],
            item_group_id=data['item_group_id'],
            supplier_id=data.get('supplier_id'),
            standard_rate=data.get('standard_rate', 0),
            currency=data.get('currency', 'USD'),
            is_stock_item=data.get('is_stock_item', True),
            has_variants=data.get('has_variants', False),
            is_sales_item=data.get('is_sales_item', True),
            is_purchase_item=data.get('is_purchase_item', True),
            minimum_stock_level=data.get('minimum_stock_level', 0),
            maximum_stock_level=data.get('maximum_stock_level', 0),
            reorder_level=data.get('reorder_level', 0),
            stock_uom=data.get('stock_uom', 'Nos'),
            weight=data.get('weight', 0),
            weight_uom=data.get('weight_uom', 'kg'),
            company_id=data['company_id']
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({'success': True, 'data': item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Warehouse Management
@supply_chain_api.route('/warehouses', methods=['GET'])
@token_required
def get_warehouses():
    """Get all warehouses"""
    try:
        company_id = request.args.get('company_id')
        warehouses = Warehouse.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [warehouse.to_dict() for warehouse in warehouses]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@supply_chain_api.route('/warehouses', methods=['POST'])
@token_required
def create_warehouse():
    """Create new warehouse"""
    try:
        data = request.get_json()
        warehouse = Warehouse(
            warehouse_name=data['warehouse_name'],
            warehouse_code=data['warehouse_code'],
            description=data.get('description'),
            address_line_1=data.get('address_line_1'),
            city=data.get('city'),
            state=data.get('state'),
            postal_code=data.get('postal_code'),
            country=data.get('country'),
            warehouse_type=data.get('warehouse_type'),
            warehouse_manager_id=data.get('warehouse_manager_id'),
            company_id=data['company_id']
        )
        db.session.add(warehouse)
        db.session.commit()
        return jsonify({'success': True, 'data': warehouse.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Stock Entry Management
@supply_chain_api.route('/stock-entries', methods=['GET'])
@token_required
def get_stock_entries():
    """Get stock entries"""
    try:
        company_id = request.args.get('company_id')
        warehouse_id = request.args.get('warehouse_id')
        item_id = request.args.get('item_id')
        entry_type = request.args.get('entry_type')
        
        query = StockEntry.query.filter_by(company_id=company_id)
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        if item_id:
            query = query.filter_by(item_id=item_id)
        if entry_type:
            query = query.filter_by(entry_type=entry_type)
        
        stock_entries = query.all()
        return jsonify({
            'success': True,
            'data': [entry.to_dict() for entry in stock_entries]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@supply_chain_api.route('/stock-entries', methods=['POST'])
@token_required
def create_stock_entry():
    """Create stock entry"""
    try:
        data = request.get_json()
        stock_entry = StockEntry(
            entry_number=data['entry_number'],
            entry_date=datetime.fromisoformat(data['entry_date']),
            entry_type=data['entry_type'],
            reference_doctype=data.get('reference_doctype'),
            reference_docname=data.get('reference_docname'),
            warehouse_id=data['warehouse_id'],
            item_id=data['item_id'],
            quantity=data['quantity'],
            rate=data.get('rate', 0),
            amount=data.get('amount', 0),
            batch_number=data.get('batch_number'),
            serial_number=data.get('serial_number'),
            remarks=data.get('remarks'),
            company_id=data['company_id']
        )
        db.session.add(stock_entry)
        db.session.commit()
        return jsonify({'success': True, 'data': stock_entry.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Purchase Order Management
@supply_chain_api.route('/purchase-orders', methods=['GET'])
@token_required
def get_purchase_orders():
    """Get purchase orders"""
    try:
        company_id = request.args.get('company_id')
        supplier_id = request.args.get('supplier_id')
        status = request.args.get('status')
        
        query = PurchaseOrder.query.filter_by(company_id=company_id)
        if supplier_id:
            query = query.filter_by(supplier_id=supplier_id)
        if status:
            query = query.filter_by(status=status)
        
        purchase_orders = query.all()
        return jsonify({
            'success': True,
            'data': [order.to_dict() for order in purchase_orders]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@supply_chain_api.route('/purchase-orders', methods=['POST'])
@token_required
def create_purchase_order():
    """Create purchase order"""
    try:
        data = request.get_json()
        purchase_order = PurchaseOrder(
            order_number=data['order_number'],
            order_date=datetime.fromisoformat(data['order_date']),
            expected_delivery_date=datetime.fromisoformat(data['expected_delivery_date']) if data.get('expected_delivery_date') else None,
            supplier_id=data['supplier_id'],
            item_id=data['item_id'],
            quantity=data['quantity'],
            rate=data['rate'],
            amount=data['amount'],
            terms_and_conditions=data.get('terms_and_conditions'),
            notes=data.get('notes'),
            company_id=data['company_id']
        )
        db.session.add(purchase_order)
        db.session.commit()
        return jsonify({'success': True, 'data': purchase_order.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Sales Order Management
@supply_chain_api.route('/sales-orders', methods=['GET'])
@token_required
def get_sales_orders():
    """Get sales orders"""
    try:
        company_id = request.args.get('company_id')
        customer_id = request.args.get('customer_id')
        status = request.args.get('status')
        
        query = SalesOrder.query.filter_by(company_id=company_id)
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        if status:
            query = query.filter_by(status=status)
        
        sales_orders = query.all()
        return jsonify({
            'success': True,
            'data': [order.to_dict() for order in sales_orders]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@supply_chain_api.route('/sales-orders', methods=['POST'])
@token_required
def create_sales_order():
    """Create sales order"""
    try:
        data = request.get_json()
        sales_order = SalesOrder(
            order_number=data['order_number'],
            order_date=datetime.fromisoformat(data['order_date']),
            delivery_date=datetime.fromisoformat(data['delivery_date']) if data.get('delivery_date') else None,
            customer_id=data.get('customer_id'),
            customer_name=data.get('customer_name'),
            customer_email=data.get('customer_email'),
            item_id=data['item_id'],
            quantity=data['quantity'],
            rate=data['rate'],
            amount=data['amount'],
            terms_and_conditions=data.get('terms_and_conditions'),
            notes=data.get('notes'),
            company_id=data['company_id']
        )
        db.session.add(sales_order)
        db.session.commit()
        return jsonify({'success': True, 'data': sales_order.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Stock Movement Management
@supply_chain_api.route('/stock-movements', methods=['GET'])
@token_required
def get_stock_movements():
    """Get stock movements"""
    try:
        company_id = request.args.get('company_id')
        warehouse_id = request.args.get('warehouse_id')
        item_id = request.args.get('item_id')
        movement_type = request.args.get('movement_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = StockMovement.query.filter_by(company_id=company_id)
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        if item_id:
            query = query.filter_by(item_id=item_id)
        if movement_type:
            query = query.filter_by(movement_type=movement_type)
        if start_date:
            query = query.filter(StockMovement.movement_date >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(StockMovement.movement_date <= datetime.fromisoformat(end_date))
        
        stock_movements = query.all()
        return jsonify({
            'success': True,
            'data': [movement.to_dict() for movement in stock_movements]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Item Price Management
@supply_chain_api.route('/item-prices', methods=['GET'])
@token_required
def get_item_prices():
    """Get item prices"""
    try:
        company_id = request.args.get('company_id')
        item_id = request.args.get('item_id')
        price_list = request.args.get('price_list')
        
        query = ItemPrice.query.filter_by(company_id=company_id)
        if item_id:
            query = query.filter_by(item_id=item_id)
        if price_list:
            query = query.filter_by(price_list=price_list)
        
        item_prices = query.all()
        return jsonify({
            'success': True,
            'data': [price.to_dict() for price in item_prices]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@supply_chain_api.route('/item-prices', methods=['POST'])
@token_required
def create_item_price():
    """Create item price"""
    try:
        data = request.get_json()
        item_price = ItemPrice(
            item_id=data['item_id'],
            price_list=data['price_list'],
            rate=data['rate'],
            currency=data.get('currency', 'USD'),
            valid_from=datetime.fromisoformat(data['valid_from']) if data.get('valid_from') else None,
            valid_upto=datetime.fromisoformat(data['valid_upto']) if data.get('valid_upto') else None,
            company_id=data['company_id']
        )
        db.session.add(item_price)
        db.session.commit()
        return jsonify({'success': True, 'data': item_price.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Item Variant Management
@supply_chain_api.route('/item-variants', methods=['GET'])
@token_required
def get_item_variants():
    """Get item variants"""
    try:
        company_id = request.args.get('company_id')
        item_id = request.args.get('item_id')
        
        query = ItemVariant.query.filter_by(company_id=company_id)
        if item_id:
            query = query.filter_by(item_id=item_id)
        
        item_variants = query.all()
        return jsonify({
            'success': True,
            'data': [variant.to_dict() for variant in item_variants]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@supply_chain_api.route('/item-variants', methods=['POST'])
@token_required
def create_item_variant():
    """Create item variant"""
    try:
        data = request.get_json()
        item_variant = ItemVariant(
            item_id=data['item_id'],
            variant_name=data['variant_name'],
            variant_code=data['variant_code'],
            attributes=data.get('attributes', {}),
            rate=data.get('rate', 0),
            currency=data.get('currency', 'USD'),
            minimum_stock_level=data.get('minimum_stock_level', 0),
            company_id=data['company_id']
        )
        db.session.add(item_variant)
        db.session.commit()
        return jsonify({'success': True, 'data': item_variant.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# BOM Management
@supply_chain_api.route('/bom', methods=['GET'])
@token_required
def get_bom():
    """Get BOM records"""
    try:
        company_id = request.args.get('company_id')
        parent_item_id = request.args.get('parent_item_id')
        
        query = BOM.query.filter_by(company_id=company_id)
        if parent_item_id:
            query = query.filter_by(parent_item_id=parent_item_id)
        
        bom_records = query.all()
        return jsonify({
            'success': True,
            'data': [bom.to_dict() for bom in bom_records]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@supply_chain_api.route('/bom', methods=['POST'])
@token_required
def create_bom():
    """Create BOM"""
    try:
        data = request.get_json()
        bom = BOM(
            bom_name=data['bom_name'],
            bom_code=data['bom_code'],
            parent_item_id=data['parent_item_id'],
            quantity=data.get('quantity', 1),
            unit_of_measure=data.get('unit_of_measure', 'Nos'),
            bom_items=data.get('bom_items', []),
            company_id=data['company_id']
        )
        db.session.add(bom)
        db.session.commit()
        return jsonify({'success': True, 'data': bom.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Production Order Management
@supply_chain_api.route('/production-orders', methods=['GET'])
@token_required
def get_production_orders():
    """Get production orders"""
    try:
        company_id = request.args.get('company_id')
        item_id = request.args.get('item_id')
        status = request.args.get('status')
        
        query = ProductionOrder.query.filter_by(company_id=company_id)
        if item_id:
            query = query.filter_by(item_id=item_id)
        if status:
            query = query.filter_by(status=status)
        
        production_orders = query.all()
        return jsonify({
            'success': True,
            'data': [order.to_dict() for order in production_orders]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@supply_chain_api.route('/production-orders', methods=['POST'])
@token_required
def create_production_order():
    """Create production order"""
    try:
        data = request.get_json()
        production_order = ProductionOrder(
            order_number=data['order_number'],
            order_date=datetime.fromisoformat(data['order_date']),
            planned_start_date=datetime.fromisoformat(data['planned_start_date']) if data.get('planned_start_date') else None,
            planned_end_date=datetime.fromisoformat(data['planned_end_date']) if data.get('planned_end_date') else None,
            item_id=data['item_id'],
            bom_id=data.get('bom_id'),
            quantity_to_produce=data['quantity_to_produce'],
            company_id=data['company_id']
        )
        db.session.add(production_order)
        db.session.commit()
        return jsonify({'success': True, 'data': production_order.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
