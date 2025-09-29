# Enhanced Supply Chain API
# Comprehensive supply chain management with advanced features

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from .enhanced_models import (
    EnhancedItem, ItemGroup, ItemBatch, ItemLot, EnhancedSalesOrder, EnhancedPurchaseOrder,
    SalesOrderItem, PurchaseOrderItem, DeliveryNote, DeliveryNoteItem, StockMovement,
    BatchMovement, VigilanceRecord, DocumentTemplate, SupplyChainReport,
    ProductType, TemperatureControl, ItemStatus, BatchStatus, DeliveryStatus, VigilanceLevel
)
from datetime import datetime, date, timedelta
import json
import os
from werkzeug.utils import secure_filename

enhanced_supply_chain_bp = Blueprint('enhanced_supply_chain', __name__)

# Enhanced Items Management
@enhanced_supply_chain_bp.route('/items', methods=['GET'])
@jwt_required()
def get_enhanced_items():
    """Get enhanced items with comprehensive filtering"""
    try:
        company_id = request.args.get('company_id', type=int)
        item_code = request.args.get('item_code')
        sku = request.args.get('sku')
        product_type = request.args.get('product_type')
        temperature_control = request.args.get('temperature_control')
        status = request.args.get('status')
        vendor_id = request.args.get('vendor_id', type=int)
        requires_batch_tracking = request.args.get('requires_batch_tracking', type=bool)
        requires_lot_tracking = request.args.get('requires_lot_tracking', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = EnhancedItem.query.filter(EnhancedItem.company_id == company_id)
        
        if item_code:
            query = query.filter(EnhancedItem.item_code.ilike(f'%{item_code}%'))
        
        if sku:
            query = query.filter(EnhancedItem.sku.ilike(f'%{sku}%'))
        
        if product_type:
            query = query.filter(EnhancedItem.product_type == ProductType(product_type))
        
        if temperature_control:
            query = query.filter(EnhancedItem.temperature_control == TemperatureControl(temperature_control))
        
        if status:
            query = query.filter(EnhancedItem.status == ItemStatus(status))
        
        if vendor_id:
            query = query.filter(EnhancedItem.vendor_id == vendor_id)
        
        if requires_batch_tracking is not None:
            query = query.filter(EnhancedItem.requires_batch_tracking == requires_batch_tracking)
        
        if requires_lot_tracking is not None:
            query = query.filter(EnhancedItem.requires_lot_tracking == requires_lot_tracking)
        
        items = query.order_by(EnhancedItem.item_name).all()
        
        return jsonify([item.to_dict() for item in items])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_supply_chain_bp.route('/items', methods=['POST'])
@jwt_required()
def create_enhanced_item():
    """Create enhanced item with comprehensive data"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['item_code', 'item_name', 'product_type', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create enhanced item
        item = EnhancedItem(
            item_code=data['item_code'],
            item_name=data['item_name'],
            description=data.get('description'),
            sku=data.get('sku'),
            part_number=data.get('part_number'),
            vendor_id=data.get('vendor_id'),
            manufacturer=data.get('manufacturer'),
            cost_price=data.get('cost_price', 0.0),
            sales_price=data.get('sales_price', 0.0),
            isbn=data.get('isbn'),
            gs1_code=data.get('gs1_code'),
            product_type=ProductType(data['product_type']),
            temperature_control=TemperatureControl(data.get('temperature_control', 'room_temperature')),
            status=ItemStatus(data.get('status', 'active')),
            
            # Additional parameters
            weight=data.get('weight'),
            dimensions=data.get('dimensions'),
            color=data.get('color'),
            material=data.get('material'),
            specifications=data.get('specifications'),
            
            # Inventory tracking
            current_stock=data.get('current_stock', 0.0),
            minimum_stock=data.get('minimum_stock', 0.0),
            maximum_stock=data.get('maximum_stock', 0.0),
            reorder_point=data.get('reorder_point', 0.0),
            
            # Tracking requirements
            requires_batch_tracking=data.get('requires_batch_tracking', False),
            requires_lot_tracking=data.get('requires_lot_tracking', False),
            requires_expiry_tracking=data.get('requires_expiry_tracking', False),
            shelf_life_days=data.get('shelf_life_days'),
            
            # Compliance and certifications
            certifications=data.get('certifications'),
            compliance_requirements=data.get('compliance_requirements'),
            
            created_by=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(item)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('enhanced_item_created', item.to_dict(), data['company_id'])
        
        return jsonify(item.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@enhanced_supply_chain_bp.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_enhanced_item(item_id):
    """Update enhanced item"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        item = EnhancedItem.query.filter_by(id=item_id).first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        # Update item fields
        for key, value in data.items():
            if hasattr(item, key) and key not in ['id', 'created_at', 'created_by']:
                if key in ['product_type', 'temperature_control', 'status']:
                    setattr(item, key, getattr(ProductType if key == 'product_type' else 
                                             TemperatureControl if key == 'temperature_control' else 
                                             ItemStatus, value))
                else:
                    setattr(item, key, value)
        
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('enhanced_item_updated', item.to_dict(), item.company_id)
        
        return jsonify(item.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Item Groups Management
@enhanced_supply_chain_bp.route('/item-groups', methods=['GET'])
@jwt_required()
def get_item_groups():
    """Get item groups"""
    try:
        company_id = request.args.get('company_id', type=int)
        group_code = request.args.get('group_code')
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = ItemGroup.query.filter(ItemGroup.company_id == company_id)
        
        if group_code:
            query = query.filter(ItemGroup.group_code.ilike(f'%{group_code}%'))
        
        if is_active is not None:
            query = query.filter(ItemGroup.is_active == is_active)
        
        groups = query.order_by(ItemGroup.group_name).all()
        
        return jsonify([group.to_dict() for group in groups])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_supply_chain_bp.route('/item-groups', methods=['POST'])
@jwt_required()
def create_item_group():
    """Create item group"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['group_code', 'group_name', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create item group
        group = ItemGroup(
            group_code=data['group_code'],
            group_name=data['group_name'],
            description=data.get('description'),
            parent_group_id=data.get('parent_group_id'),
            is_active=data.get('is_active', True),
            company_id=data['company_id']
        )
        
        db.session.add(group)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('item_group_created', group.to_dict(), data['company_id'])
        
        return jsonify(group.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Batch and Lot Tracking
@enhanced_supply_chain_bp.route('/items/<int:item_id>/batches', methods=['POST'])
@jwt_required()
def create_item_batch(item_id):
    """Create item batch"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['batch_number', 'initial_quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create batch
        batch = ItemBatch(
            item_id=item_id,
            batch_number=data['batch_number'],
            lot_number=data.get('lot_number'),
            expiry_date=datetime.fromisoformat(data['expiry_date']).date() if data.get('expiry_date') else None,
            manufacturing_date=datetime.fromisoformat(data['manufacturing_date']).date() if data.get('manufacturing_date') else None,
            initial_quantity=data['initial_quantity'],
            current_quantity=data['initial_quantity'],
            warehouse_location=data.get('warehouse_location'),
            storage_conditions=data.get('storage_conditions'),
            quality_certificate=data.get('quality_certificate'),
            test_results=data.get('test_results'),
            compliance_status=data.get('compliance_status'),
            created_by=user_id,
            company_id=data.get('company_id')
        )
        
        db.session.add(batch)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('item_batch_created', batch.to_dict(), data.get('company_id'))
        
        return jsonify(batch.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@enhanced_supply_chain_bp.route('/items/<int:item_id>/lots', methods=['POST'])
@jwt_required()
def create_item_lot(item_id):
    """Create item lot"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['lot_number', 'initial_quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create lot
        lot = ItemLot(
            item_id=item_id,
            lot_number=data['lot_number'],
            batch_id=data.get('batch_id'),
            expiry_date=datetime.fromisoformat(data['expiry_date']).date() if data.get('expiry_date') else None,
            manufacturing_date=datetime.fromisoformat(data['manufacturing_date']).date() if data.get('manufacturing_date') else None,
            initial_quantity=data['initial_quantity'],
            current_quantity=data['initial_quantity'],
            warehouse_location=data.get('warehouse_location'),
            storage_conditions=data.get('storage_conditions'),
            quality_certificate=data.get('quality_certificate'),
            test_results=data.get('test_results'),
            compliance_status=data.get('compliance_status'),
            created_by=user_id,
            company_id=data.get('company_id')
        )
        
        db.session.add(lot)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('item_lot_created', lot.to_dict(), data.get('company_id'))
        
        return jsonify(lot.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Auto-create Sales Order from CRM deal
@enhanced_supply_chain_bp.route('/sales-orders/auto-create', methods=['POST'])
@jwt_required()
def auto_create_sales_order():
    """Auto-create sales order from CRM deal"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['crm_deal_id', 'customer_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create sales order
        sales_order = EnhancedSalesOrder(
            so_number=f"SO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            customer_id=data['customer_id'],
            crm_deal_id=data['crm_deal_id'],
            order_date=date.today(),
            delivery_date=datetime.fromisoformat(data['delivery_date']).date() if data.get('delivery_date') else None,
            status='confirmed',
            subtotal=data.get('subtotal', 0.0),
            tax_amount=data.get('tax_amount', 0.0),
            discount_amount=data.get('discount_amount', 0.0),
            total_amount=data.get('total_amount', 0.0),
            shipping_address=data.get('shipping_address'),
            billing_address=data.get('billing_address'),
            shipping_method=data.get('shipping_method'),
            delivery_instructions=data.get('delivery_instructions'),
            created_by=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(sales_order)
        db.session.flush()  # Get the ID
        
        # Add sales order items
        for item_data in data.get('items', []):
            sales_order_item = SalesOrderItem(
                sales_order_id=sales_order.id,
                item_id=item_data['item_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                discount_percentage=item_data.get('discount_percentage', 0.0),
                tax_percentage=item_data.get('tax_percentage', 0.0),
                line_total=item_data['quantity'] * item_data['unit_price'],
                pending_quantity=item_data['quantity']
            )
            db.session.add(sales_order_item)
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('sales_order_auto_created', sales_order.to_dict(), data['company_id'])
        
        return jsonify(sales_order.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Enhanced Purchase Order Management
@enhanced_supply_chain_bp.route('/purchase-orders', methods=['GET'])
@jwt_required()
def get_enhanced_purchase_orders():
    """Get enhanced purchase orders"""
    try:
        company_id = request.args.get('company_id', type=int)
        po_number = request.args.get('po_number')
        supplier_id = request.args.get('supplier_id', type=int)
        status = request.args.get('status')
        is_consolidated = request.args.get('is_consolidated', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = EnhancedPurchaseOrder.query.filter(EnhancedPurchaseOrder.company_id == company_id)
        
        if po_number:
            query = query.filter(EnhancedPurchaseOrder.po_number.ilike(f'%{po_number}%'))
        
        if supplier_id:
            query = query.filter(EnhancedPurchaseOrder.supplier_id == supplier_id)
        
        if status:
            query = query.filter(EnhancedPurchaseOrder.status == status)
        
        if is_consolidated is not None:
            query = query.filter(EnhancedPurchaseOrder.is_consolidated == is_consolidated)
        
        purchase_orders = query.order_by(EnhancedPurchaseOrder.order_date.desc()).all()
        
        return jsonify([po.to_dict() for po in purchase_orders])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_supply_chain_bp.route('/purchase-orders', methods=['POST'])
@jwt_required()
def create_enhanced_purchase_order():
    """Create enhanced purchase order"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['supplier_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create purchase order
        purchase_order = EnhancedPurchaseOrder(
            po_number=f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            supplier_id=data['supplier_id'],
            sales_order_id=data.get('sales_order_id'),
            order_date=date.today(),
            expected_delivery_date=datetime.fromisoformat(data['expected_delivery_date']).date() if data.get('expected_delivery_date') else None,
            status=data.get('status', 'draft'),
            subtotal=data.get('subtotal', 0.0),
            tax_amount=data.get('tax_amount', 0.0),
            discount_amount=data.get('discount_amount', 0.0),
            shipping_cost=data.get('shipping_cost', 0.0),
            total_amount=data.get('total_amount', 0.0),
            is_consolidated=data.get('is_consolidated', False),
            consolidated_po_id=data.get('consolidated_po_id'),
            template_id=data.get('template_id'),
            custom_template_data=data.get('custom_template_data'),
            created_by=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(purchase_order)
        db.session.flush()  # Get the ID
        
        # Add purchase order items
        for item_data in data.get('items', []):
            purchase_order_item = PurchaseOrderItem(
                purchase_order_id=purchase_order.id,
                item_id=item_data['item_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                discount_percentage=item_data.get('discount_percentage', 0.0),
                tax_percentage=item_data.get('tax_percentage', 0.0),
                line_total=item_data['quantity'] * item_data['unit_price'],
                pending_quantity=item_data['quantity'],
                batch_number=item_data.get('batch_number'),
                lot_number=item_data.get('lot_number'),
                expiry_date=datetime.fromisoformat(item_data['expiry_date']).date() if item_data.get('expiry_date') else None
            )
            db.session.add(purchase_order_item)
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('purchase_order_created', purchase_order.to_dict(), data['company_id'])
        
        return jsonify(purchase_order.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# PO Consolidation
@enhanced_supply_chain_bp.route('/purchase-orders/consolidate', methods=['POST'])
@jwt_required()
def consolidate_purchase_orders():
    """Consolidate multiple purchase orders"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['po_ids', 'supplier_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        po_ids = data['po_ids']
        if len(po_ids) < 2:
            return jsonify({'error': 'At least 2 purchase orders are required for consolidation'}), 400
        
        # Create consolidated PO
        consolidated_po = EnhancedPurchaseOrder(
            po_number=f"CONS-PO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            supplier_id=data['supplier_id'],
            order_date=date.today(),
            expected_delivery_date=datetime.fromisoformat(data['expected_delivery_date']).date() if data.get('expected_delivery_date') else None,
            status='consolidated',
            is_consolidated=True,
            consolidation_date=datetime.utcnow(),
            created_by=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(consolidated_po)
        db.session.flush()  # Get the ID
        
        # Update original POs to link to consolidated PO
        for po_id in po_ids:
            po = EnhancedPurchaseOrder.query.filter_by(id=po_id).first()
            if po:
                po.consolidated_po_id = consolidated_po.id
                po.is_consolidated = True
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('purchase_orders_consolidated', consolidated_po.to_dict(), data['company_id'])
        
        return jsonify(consolidated_po.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delivery Notes Management
@enhanced_supply_chain_bp.route('/delivery-notes', methods=['GET'])
@jwt_required()
def get_delivery_notes():
    """Get delivery notes"""
    try:
        company_id = request.args.get('company_id', type=int)
        dn_number = request.args.get('dn_number')
        customer_id = request.args.get('customer_id', type=int)
        status = request.args.get('status')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = DeliveryNote.query.filter(DeliveryNote.company_id == company_id)
        
        if dn_number:
            query = query.filter(DeliveryNote.dn_number.ilike(f'%{dn_number}%'))
        
        if customer_id:
            query = query.filter(DeliveryNote.customer_id == customer_id)
        
        if status:
            query = query.filter(DeliveryNote.status == DeliveryStatus(status))
        
        delivery_notes = query.order_by(DeliveryNote.delivery_date.desc()).all()
        
        return jsonify([dn.to_dict() for dn in delivery_notes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_supply_chain_bp.route('/delivery-notes', methods=['POST'])
@jwt_required()
def create_delivery_note():
    """Create delivery note"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['customer_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create delivery note
        delivery_note = DeliveryNote(
            dn_number=f"DN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            purchase_order_id=data.get('purchase_order_id'),
            customer_id=data['customer_id'],
            delivery_date=date.today(),
            status=DeliveryStatus(data.get('status', 'pending')),
            delivery_address=data.get('delivery_address'),
            delivery_method=data.get('delivery_method'),
            tracking_number=data.get('tracking_number'),
            delivery_instructions=data.get('delivery_instructions'),
            template_id=data.get('template_id'),
            custom_template_data=data.get('custom_template_data'),
            created_by=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(delivery_note)
        db.session.flush()  # Get the ID
        
        # Add delivery note items
        for item_data in data.get('items', []):
            delivery_note_item = DeliveryNoteItem(
                delivery_note_id=delivery_note.id,
                item_id=item_data['item_id'],
                quantity=item_data['quantity'],
                delivered_quantity=item_data.get('delivered_quantity', 0.0),
                pending_quantity=item_data['quantity'] - item_data.get('delivered_quantity', 0.0),
                batch_number=item_data.get('batch_number'),
                lot_number=item_data.get('lot_number'),
                expiry_date=datetime.fromisoformat(item_data['expiry_date']).date() if item_data.get('expiry_date') else None,
                quality_status=item_data.get('quality_status'),
                quality_notes=item_data.get('quality_notes')
            )
            db.session.add(delivery_note_item)
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('delivery_note_created', delivery_note.to_dict(), data['company_id'])
        
        return jsonify(delivery_note.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Vigilance System
@enhanced_supply_chain_bp.route('/vigilance', methods=['GET'])
@jwt_required()
def get_vigilance_records():
    """Get vigilance records"""
    try:
        company_id = request.args.get('company_id', type=int)
        item_id = request.args.get('item_id', type=int)
        vigilance_type = request.args.get('vigilance_type')
        vigilance_level = request.args.get('vigilance_level')
        status = request.args.get('status')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = VigilanceRecord.query.filter(VigilanceRecord.company_id == company_id)
        
        if item_id:
            query = query.filter(VigilanceRecord.item_id == item_id)
        
        if vigilance_type:
            query = query.filter(VigilanceRecord.vigilance_type == vigilance_type)
        
        if vigilance_level:
            query = query.filter(VigilanceRecord.vigilance_level == VigilanceLevel(vigilance_level))
        
        if status:
            query = query.filter(VigilanceRecord.status == status)
        
        records = query.order_by(VigilanceRecord.detected_date.desc()).all()
        
        return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_supply_chain_bp.route('/vigilance', methods=['POST'])
@jwt_required()
def create_vigilance_record():
    """Create vigilance record"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['vigilance_type', 'vigilance_level', 'description', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create vigilance record
        record = VigilanceRecord(
            item_id=data.get('item_id'),
            batch_id=data.get('batch_id'),
            lot_id=data.get('lot_id'),
            vigilance_type=data['vigilance_type'],
            vigilance_level=VigilanceLevel(data['vigilance_level']),
            description=data['description'],
            corrective_action=data.get('corrective_action'),
            preventive_action=data.get('preventive_action'),
            status=data.get('status', 'open'),
            assigned_to=data.get('assigned_to'),
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

# Supply Chain Reports
@enhanced_supply_chain_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_supply_chain_reports():
    """Get supply chain reports"""
    try:
        company_id = request.args.get('company_id', type=int)
        report_type = request.args.get('report_type')
        report_period = request.args.get('report_period')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = SupplyChainReport.query.filter(SupplyChainReport.company_id == company_id)
        
        if report_type:
            query = query.filter(SupplyChainReport.report_type == report_type)
        
        if report_period:
            query = query.filter(SupplyChainReport.report_period == report_period)
        
        reports = query.order_by(SupplyChainReport.generated_at.desc()).all()
        
        return jsonify([report.to_dict() for report in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_supply_chain_bp.route('/reports/generate', methods=['POST'])
@jwt_required()
def generate_supply_chain_report():
    """Generate supply chain report"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['report_name', 'report_type', 'report_period', 'start_date', 'end_date', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate report data based on type
        report_data = {}
        start_date = datetime.fromisoformat(data['start_date']).date()
        end_date = datetime.fromisoformat(data['end_date']).date()
        
        if data['report_type'] == 'vendor_po':
            # Generate vendor PO report
            pos = EnhancedPurchaseOrder.query.filter(
                EnhancedPurchaseOrder.company_id == data['company_id'],
                EnhancedPurchaseOrder.order_date >= start_date,
                EnhancedPurchaseOrder.order_date <= end_date
            ).all()
            
            report_data = {
                'total_pos': len(pos),
                'total_value': sum(po.total_amount for po in pos),
                'by_supplier': {},
                'by_status': {}
            }
            
            for po in pos:
                supplier_name = po.supplier.supplier_name if po.supplier else 'Unknown'
                if supplier_name not in report_data['by_supplier']:
                    report_data['by_supplier'][supplier_name] = {'count': 0, 'value': 0}
                report_data['by_supplier'][supplier_name]['count'] += 1
                report_data['by_supplier'][supplier_name]['value'] += po.total_amount
                
                if po.status not in report_data['by_status']:
                    report_data['by_status'][po.status] = 0
                report_data['by_status'][po.status] += 1
        
        elif data['report_type'] == 'items_amount':
            # Generate items amount report
            items = EnhancedItem.query.filter(
                EnhancedItem.company_id == data['company_id']
            ).all()
            
            report_data = {
                'total_items': len(items),
                'total_stock_value': sum(item.current_stock * item.cost_price for item in items),
                'by_product_type': {},
                'by_temperature_control': {}
            }
            
            for item in items:
                product_type = item.product_type.value
                if product_type not in report_data['by_product_type']:
                    report_data['by_product_type'][product_type] = {'count': 0, 'value': 0}
                report_data['by_product_type'][product_type]['count'] += 1
                report_data['by_product_type'][product_type]['value'] += item.current_stock * item.cost_price
                
                temp_control = item.temperature_control.value
                if temp_control not in report_data['by_temperature_control']:
                    report_data['by_temperature_control'][temp_control] = {'count': 0, 'value': 0}
                report_data['by_temperature_control'][temp_control]['count'] += 1
                report_data['by_temperature_control'][temp_control]['value'] += item.current_stock * item.cost_price
        
        # Create report record
        report = SupplyChainReport(
            report_name=data['report_name'],
            report_type=data['report_type'],
            report_period=data['report_period'],
            start_date=start_date,
            end_date=end_date,
            report_data=report_data,
            report_summary=data.get('report_summary'),
            created_by=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('supply_chain_report_generated', report.to_dict(), data['company_id'])
        
        return jsonify(report.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Document Templates Management
@enhanced_supply_chain_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_document_templates():
    """Get document templates"""
    try:
        company_id = request.args.get('company_id', type=int)
        template_type = request.args.get('template_type')
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = DocumentTemplate.query.filter(DocumentTemplate.company_id == company_id)
        
        if template_type:
            query = query.filter(DocumentTemplate.template_type == template_type)
        
        if is_active is not None:
            query = query.filter(DocumentTemplate.is_active == is_active)
        
        templates = query.order_by(DocumentTemplate.template_name).all()
        
        return jsonify([template.to_dict() for template in templates])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_supply_chain_bp.route('/templates', methods=['POST'])
@jwt_required()
def create_document_template():
    """Create document template"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['template_name', 'template_type', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create template
        template = DocumentTemplate(
            template_name=data['template_name'],
            template_type=data['template_type'],
            template_file_path=data.get('template_file_path'),
            template_file_type=data.get('template_file_type'),
            is_active=data.get('is_active', True),
            template_config=data.get('template_config'),
            default_template=data.get('default_template', False),
            created_by=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(template)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('document_template_created', template.to_dict(), data['company_id'])
        
        return jsonify(template.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Template file upload
@enhanced_supply_chain_bp.route('/templates/upload', methods=['POST'])
@jwt_required()
def upload_template_file():
    """Upload template file"""
    try:
        user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        template_id = request.form.get('template_id', type=int)
        
        if not template_id:
            return jsonify({'error': 'Template ID is required'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'docx', 'pdf'}
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        if file_extension not in allowed_extensions:
            return jsonify({'error': 'Only DOCX and PDF files are allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        upload_folder = 'uploads/templates'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, f"{template_id}_{filename}")
        file.save(file_path)
        
        # Update template with file path
        template = DocumentTemplate.query.filter_by(id=template_id).first()
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        template.template_file_path = file_path
        template.template_file_type = file_extension
        db.session.commit()
        
        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Batch and Lot Tracking
@enhanced_supply_chain_bp.route('/tracking/batch/<string:batch_number>', methods=['GET'])
@jwt_required()
def track_batch(batch_number):
    """Track batch by batch number"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        batch = ItemBatch.query.filter(
            ItemBatch.batch_number == batch_number,
            ItemBatch.company_id == company_id
        ).first()
        
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404
        
        # Get batch movements
        movements = BatchMovement.query.filter(
            BatchMovement.batch_id == batch.id
        ).order_by(BatchMovement.movement_date.desc()).all()
        
        return jsonify({
            'batch': batch.to_dict(),
            'movements': [movement.to_dict() for movement in movements]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_supply_chain_bp.route('/tracking/lot/<string:lot_number>', methods=['GET'])
@jwt_required()
def track_lot(lot_number):
    """Track lot by lot number"""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        lot = ItemLot.query.filter(
            ItemLot.lot_number == lot_number,
            ItemLot.company_id == company_id
        ).first()
        
        if not lot:
            return jsonify({'error': 'Lot not found'}), 404
        
        return jsonify(lot.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
