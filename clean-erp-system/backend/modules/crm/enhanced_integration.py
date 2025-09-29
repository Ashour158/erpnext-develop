# CRM Integration with Supply Chain
# Enhanced CRM integration for quote creation with supply chain items

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from ..supply_chain.enhanced_models import EnhancedItem, ProductType, TemperatureControl, ItemStatus
from .models import Customer, Opportunity, Quote, QuoteItem
from datetime import datetime, date
import json

crm_integration_bp = Blueprint('crm_integration', __name__)

# Get items for quote creation
@crm_integration_bp.route('/items-for-quote', methods=['GET'])
@jwt_required()
def get_items_for_quote():
    """Get items available for quote creation"""
    try:
        company_id = request.args.get('company_id', type=int)
        customer_id = request.args.get('customer_id', type=int)
        product_type = request.args.get('product_type')
        temperature_control = request.args.get('temperature_control')
        search_term = request.args.get('search_term')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = EnhancedItem.query.filter(
            EnhancedItem.company_id == company_id,
            EnhancedItem.status == ItemStatus.ACTIVE
        )
        
        if product_type:
            query = query.filter(EnhancedItem.product_type == ProductType(product_type))
        
        if temperature_control:
            query = query.filter(EnhancedItem.temperature_control == TemperatureControl(temperature_control))
        
        if search_term:
            query = query.filter(
                db.or_(
                    EnhancedItem.item_name.ilike(f'%{search_term}%'),
                    EnhancedItem.item_code.ilike(f'%{search_term}%'),
                    EnhancedItem.sku.ilike(f'%{search_term}%'),
                    EnhancedItem.description.ilike(f'%{search_term}%')
                )
            )
        
        items = query.order_by(EnhancedItem.item_name).limit(100).all()
        
        # Format items for quote creation
        formatted_items = []
        for item in items:
            formatted_items.append({
                'id': item.id,
                'item_code': item.item_code,
                'item_name': item.item_name,
                'description': item.description,
                'sku': item.sku,
                'part_number': item.part_number,
                'manufacturer': item.manufacturer,
                'sales_price': item.sales_price,
                'cost_price': item.cost_price,
                'product_type': item.product_type.value,
                'temperature_control': item.temperature_control.value,
                'current_stock': item.current_stock,
                'requires_batch_tracking': item.requires_batch_tracking,
                'requires_lot_tracking': item.requires_lot_tracking,
                'requires_expiry_tracking': item.requires_expiry_tracking,
                'specifications': item.specifications,
                'certifications': item.certifications,
                'vendor': {
                    'id': item.vendor.id if item.vendor else None,
                    'name': item.vendor.supplier_name if item.vendor else None
                } if item.vendor else None
            })
        
        return jsonify(formatted_items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create quote with items
@crm_integration_bp.route('/quotes', methods=['POST'])
@jwt_required()
def create_quote_with_items():
    """Create quote with supply chain items"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['customer_id', 'opportunity_id', 'company_id', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create quote
        quote = Quote(
            quote_number=f"Q-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            customer_id=data['customer_id'],
            opportunity_id=data['opportunity_id'],
            quote_date=date.today(),
            valid_until=datetime.fromisoformat(data['valid_until']).date() if data.get('valid_until') else None,
            status=data.get('status', 'draft'),
            subtotal=data.get('subtotal', 0.0),
            tax_amount=data.get('tax_amount', 0.0),
            discount_amount=data.get('discount_amount', 0.0),
            total_amount=data.get('total_amount', 0.0),
            terms_and_conditions=data.get('terms_and_conditions'),
            notes=data.get('notes'),
            created_by=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(quote)
        db.session.flush()  # Get the ID
        
        # Add quote items
        total_amount = 0.0
        for item_data in data['items']:
            # Get item details
            item = EnhancedItem.query.filter_by(id=item_data['item_id']).first()
            if not item:
                continue
            
            quantity = item_data['quantity']
            unit_price = item_data.get('unit_price', item.sales_price)
            discount_percentage = item_data.get('discount_percentage', 0.0)
            tax_percentage = item_data.get('tax_percentage', 0.0)
            
            # Calculate line total
            line_subtotal = quantity * unit_price
            discount_amount = line_subtotal * (discount_percentage / 100)
            line_after_discount = line_subtotal - discount_amount
            tax_amount = line_after_discount * (tax_percentage / 100)
            line_total = line_after_discount + tax_amount
            
            quote_item = QuoteItem(
                quote_id=quote.id,
                item_id=item_data['item_id'],
                item_code=item.item_code,
                item_name=item.item_name,
                description=item.description,
                quantity=quantity,
                unit_price=unit_price,
                discount_percentage=discount_percentage,
                tax_percentage=tax_percentage,
                line_total=line_total,
                batch_number=item_data.get('batch_number'),
                lot_number=item_data.get('lot_number'),
                expiry_date=datetime.fromisoformat(item_data['expiry_date']).date() if item_data.get('expiry_date') else None,
                specifications=item_data.get('specifications'),
                delivery_requirements=item_data.get('delivery_requirements')
            )
            
            db.session.add(quote_item)
            total_amount += line_total
        
        # Update quote total
        quote.total_amount = total_amount
        quote.subtotal = total_amount - quote.tax_amount
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('quote_created_with_items', quote.to_dict(), data['company_id'])
        
        return jsonify(quote.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Auto-create Sales Order when deal is closed won
@crm_integration_bp.route('/deals/<int:deal_id>/close-won', methods=['POST'])
@jwt_required()
def close_deal_won(deal_id):
    """Close deal as won and auto-create sales order"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get the opportunity/deal
        opportunity = Opportunity.query.filter_by(id=deal_id).first()
        if not opportunity:
            return jsonify({'error': 'Deal not found'}), 404
        
        # Update opportunity status
        opportunity.status = 'closed_won'
        opportunity.closed_date = date.today()
        opportunity.closed_by = user_id
        
        # Get the quote associated with this opportunity
        quote = Quote.query.filter_by(
            opportunity_id=deal_id,
            status='accepted'
        ).first()
        
        if not quote:
            return jsonify({'error': 'No accepted quote found for this deal'}), 400
        
        # Create sales order from quote
        from ..supply_chain.enhanced_models import EnhancedSalesOrder, SalesOrderItem
        
        sales_order = EnhancedSalesOrder(
            so_number=f"SO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            customer_id=opportunity.customer_id,
            crm_deal_id=deal_id,
            order_date=date.today(),
            delivery_date=datetime.fromisoformat(data['delivery_date']).date() if data.get('delivery_date') else None,
            status='confirmed',
            subtotal=quote.subtotal,
            tax_amount=quote.tax_amount,
            discount_amount=quote.discount_amount,
            total_amount=quote.total_amount,
            shipping_address=data.get('shipping_address'),
            billing_address=data.get('billing_address'),
            shipping_method=data.get('shipping_method'),
            delivery_instructions=data.get('delivery_instructions'),
            created_by=user_id,
            company_id=opportunity.company_id
        )
        
        db.session.add(sales_order)
        db.session.flush()  # Get the ID
        
        # Create sales order items from quote items
        for quote_item in quote.items:
            sales_order_item = SalesOrderItem(
                sales_order_id=sales_order.id,
                item_id=quote_item.item_id,
                quantity=quote_item.quantity,
                unit_price=quote_item.unit_price,
                discount_percentage=quote_item.discount_percentage,
                tax_percentage=quote_item.tax_percentage,
                line_total=quote_item.line_total,
                pending_quantity=quote_item.quantity
            )
            db.session.add(sales_order_item)
        
        # Update quote status
        quote.status = 'converted_to_sales_order'
        quote.sales_order_id = sales_order.id
        
        db.session.commit()
        
        # Emit real-time updates
        emit_realtime_update('deal_closed_won', opportunity.to_dict(), opportunity.company_id)
        emit_realtime_update('sales_order_auto_created', sales_order.to_dict(), opportunity.company_id)
        
        return jsonify({
            'message': 'Deal closed as won and sales order created',
            'sales_order': sales_order.to_dict(),
            'opportunity': opportunity.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get items by vendor for PO creation
@crm_integration_bp.route('/items/by-vendor', methods=['GET'])
@jwt_required()
def get_items_by_vendor():
    """Get items grouped by vendor for PO creation"""
    try:
        company_id = request.args.get('company_id', type=int)
        sales_order_id = request.args.get('sales_order_id', type=int)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        if not sales_order_id:
            return jsonify({'error': 'Sales Order ID is required'}), 400
        
        # Get sales order items
        from ..supply_chain.enhanced_models import SalesOrderItem
        sales_order_items = SalesOrderItem.query.filter_by(sales_order_id=sales_order_id).all()
        
        # Group items by vendor
        vendor_items = {}
        for so_item in sales_order_items:
            item = EnhancedItem.query.filter_by(id=so_item.item_id).first()
            if not item or not item.vendor:
                continue
            
            vendor_id = item.vendor_id
            vendor_name = item.vendor.supplier_name
            
            if vendor_id not in vendor_items:
                vendor_items[vendor_id] = {
                    'vendor_id': vendor_id,
                    'vendor_name': vendor_name,
                    'vendor_contact': item.vendor.contact_person if item.vendor else None,
                    'vendor_email': item.vendor.email if item.vendor else None,
                    'vendor_phone': item.vendor.phone if item.vendor else None,
                    'items': []
                }
            
            vendor_items[vendor_id]['items'].append({
                'id': item.id,
                'item_code': item.item_code,
                'item_name': item.item_name,
                'description': item.description,
                'sku': item.sku,
                'part_number': item.part_number,
                'manufacturer': item.manufacturer,
                'cost_price': item.cost_price,
                'sales_price': item.sales_price,
                'product_type': item.product_type.value,
                'temperature_control': item.temperature_control.value,
                'quantity': so_item.quantity,
                'unit_price': so_item.unit_price,
                'line_total': so_item.line_total,
                'requires_batch_tracking': item.requires_batch_tracking,
                'requires_lot_tracking': item.requires_lot_tracking,
                'requires_expiry_tracking': item.requires_expiry_tracking,
                'specifications': item.specifications,
                'certifications': item.certifications
            })
        
        return jsonify(list(vendor_items.values()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create PO from sales order items
@crm_integration_bp.route('/purchase-orders/auto-create', methods=['POST'])
@jwt_required()
def auto_create_purchase_orders():
    """Auto-create purchase orders from sales order items grouped by vendor"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['sales_order_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        sales_order_id = data['sales_order_id']
        company_id = data['company_id']
        
        # Get sales order
        from ..supply_chain.enhanced_models import EnhancedSalesOrder
        sales_order = EnhancedSalesOrder.query.filter_by(id=sales_order_id).first()
        if not sales_order:
            return jsonify({'error': 'Sales order not found'}), 404
        
        # Get items grouped by vendor
        vendor_items_response = get_items_by_vendor()
        if vendor_items_response[1] != 200:  # Check if there was an error
            return vendor_items_response
        
        vendor_items = vendor_items_response[0].get_json()
        
        created_pos = []
        
        # Create PO for each vendor
        for vendor_data in vendor_items:
            from ..supply_chain.enhanced_models import EnhancedPurchaseOrder, PurchaseOrderItem
            
            # Create purchase order
            po = EnhancedPurchaseOrder(
                po_number=f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{vendor_data['vendor_id']}",
                supplier_id=vendor_data['vendor_id'],
                sales_order_id=sales_order_id,
                order_date=date.today(),
                expected_delivery_date=datetime.fromisoformat(data['expected_delivery_date']).date() if data.get('expected_delivery_date') else None,
                status='draft',
                created_by=user_id,
                company_id=company_id
            )
            
            db.session.add(po)
            db.session.flush()  # Get the ID
            
            # Add purchase order items
            po_subtotal = 0.0
            for item_data in vendor_data['items']:
                po_item = PurchaseOrderItem(
                    purchase_order_id=po.id,
                    item_id=item_data['id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['cost_price'],  # Use cost price for PO
                    line_total=item_data['quantity'] * item_data['cost_price'],
                    pending_quantity=item_data['quantity']
                )
                db.session.add(po_item)
                po_subtotal += po_item.line_total
            
            # Update PO totals
            po.subtotal = po_subtotal
            po.total_amount = po_subtotal
            
            created_pos.append(po.to_dict())
        
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('purchase_orders_auto_created', created_pos, company_id)
        
        return jsonify({
            'message': f'Created {len(created_pos)} purchase orders',
            'purchase_orders': created_pos
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get quote with item details
@crm_integration_bp.route('/quotes/<int:quote_id>/with-items', methods=['GET'])
@jwt_required()
def get_quote_with_items(quote_id):
    """Get quote with detailed item information"""
    try:
        quote = Quote.query.filter_by(id=quote_id).first()
        if not quote:
            return jsonify({'error': 'Quote not found'}), 404
        
        # Get quote items with item details
        quote_items = []
        for quote_item in quote.items:
            item = EnhancedItem.query.filter_by(id=quote_item.item_id).first()
            if item:
                quote_items.append({
                    'id': quote_item.id,
                    'item_id': quote_item.item_id,
                    'item_code': quote_item.item_code,
                    'item_name': quote_item.item_name,
                    'description': quote_item.description,
                    'quantity': quote_item.quantity,
                    'unit_price': quote_item.unit_price,
                    'discount_percentage': quote_item.discount_percentage,
                    'tax_percentage': quote_item.tax_percentage,
                    'line_total': quote_item.line_total,
                    'batch_number': quote_item.batch_number,
                    'lot_number': quote_item.lot_number,
                    'expiry_date': quote_item.expiry_date.isoformat() if quote_item.expiry_date else None,
                    'specifications': quote_item.specifications,
                    'delivery_requirements': quote_item.delivery_requirements,
                    'item_details': {
                        'sku': item.sku,
                        'part_number': item.part_number,
                        'manufacturer': item.manufacturer,
                        'product_type': item.product_type.value,
                        'temperature_control': item.temperature_control.value,
                        'requires_batch_tracking': item.requires_batch_tracking,
                        'requires_lot_tracking': item.requires_lot_tracking,
                        'requires_expiry_tracking': item.requires_expiry_tracking,
                        'specifications': item.specifications,
                        'certifications': item.certifications,
                        'vendor': {
                            'id': item.vendor.id if item.vendor else None,
                            'name': item.vendor.supplier_name if item.vendor else None
                        } if item.vendor else None
                    }
                })
        
        return jsonify({
            'quote': quote.to_dict(),
            'items': quote_items
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
