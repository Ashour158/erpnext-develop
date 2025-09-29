# Supply Chain Models - Complete Supply Chain Management
# Advanced inventory and procurement models without Frappe dependencies

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

# Enums
class ItemType(enum.Enum):
    PRODUCT = "Product"
    SERVICE = "Service"
    RAW_MATERIAL = "Raw Material"
    CONSUMABLE = "Consumable"

class StockStatus(enum.Enum):
    IN_STOCK = "In Stock"
    OUT_OF_STOCK = "Out of Stock"
    LOW_STOCK = "Low Stock"
    DISCONTINUED = "Discontinued"

class OrderStatus(enum.Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class MovementType(enum.Enum):
    RECEIPT = "Receipt"
    ISSUE = "Issue"
    TRANSFER = "Transfer"
    ADJUSTMENT = "Adjustment"

# Supplier Model
class Supplier(BaseModel):
    """Supplier model"""
    __tablename__ = 'suppliers'
    
    supplier_name = db.Column(db.String(200), nullable=False)
    supplier_code = db.Column(db.String(50), unique=True, nullable=False)
    
    # Contact Information
    contact_person = db.Column(db.String(200))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    
    # Address
    address_line_1 = db.Column(db.String(200))
    address_line_2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Business Information
    tax_id = db.Column(db.String(50))
    registration_number = db.Column(db.String(50))
    credit_limit = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_preferred = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    items = relationship("Item", back_populates="supplier")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'supplier_name': self.supplier_name,
            'supplier_code': self.supplier_code,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'tax_id': self.tax_id,
            'registration_number': self.registration_number,
            'credit_limit': self.credit_limit,
            'currency': self.currency,
            'is_active': self.is_active,
            'is_preferred': self.is_preferred,
            'company_id': self.company_id
        })
        return data

# Item Group Model
class ItemGroup(BaseModel):
    """Item Group model"""
    __tablename__ = 'item_groups'
    
    group_name = db.Column(db.String(200), nullable=False)
    group_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Hierarchy
    parent_group_id = db.Column(db.Integer, db.ForeignKey('item_groups.id'))
    parent_group = relationship("ItemGroup", remote_side=[id])
    child_groups = relationship("ItemGroup", back_populates="parent_group")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    items = relationship("Item", back_populates="item_group")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'group_name': self.group_name,
            'group_code': self.group_code,
            'description': self.description,
            'parent_group_id': self.parent_group_id,
            'company_id': self.company_id
        })
        return data

# Item Model
class Item(BaseModel):
    """Item model"""
    __tablename__ = 'items'
    
    item_name = db.Column(db.String(200), nullable=False)
    item_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Item Details
    item_type = db.Column(db.Enum(ItemType), nullable=False)
    item_group_id = db.Column(db.Integer, db.ForeignKey('item_groups.id'), nullable=False)
    item_group = relationship("ItemGroup", back_populates="items")
    
    # Supplier Information
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    supplier = relationship("Supplier", back_populates="items")
    
    # Pricing
    standard_rate = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Inventory Settings
    is_stock_item = db.Column(db.Boolean, default=True)
    has_variants = db.Column(db.Boolean, default=False)
    is_sales_item = db.Column(db.Boolean, default=True)
    is_purchase_item = db.Column(db.Boolean, default=True)
    
    # Stock Information
    stock_status = db.Column(db.Enum(StockStatus), default=StockStatus.IN_STOCK)
    minimum_stock_level = db.Column(db.Float, default=0.0)
    maximum_stock_level = db.Column(db.Float, default=0.0)
    reorder_level = db.Column(db.Float, default=0.0)
    
    # Unit of Measure
    stock_uom = db.Column(db.String(50), default='Nos')
    purchase_uom = db.Column(db.String(50))
    sales_uom = db.Column(db.String(50))
    
    # Additional Information
    weight = db.Column(db.Float, default=0.0)
    weight_uom = db.Column(db.String(10), default='kg')
    dimensions = db.Column(db.JSON)  # Length, Width, Height
    image = db.Column(db.String(255))
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    stock_entries = relationship("StockEntry", back_populates="item")
    purchase_orders = relationship("PurchaseOrder", back_populates="item")
    sales_orders = relationship("SalesOrder", back_populates="item")
    stock_movements = relationship("StockMovement", back_populates="item")
    item_prices = relationship("ItemPrice", back_populates="item")
    item_variants = relationship("ItemVariant", back_populates="item")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'item_name': self.item_name,
            'item_code': self.item_code,
            'description': self.description,
            'item_type': self.item_type.value if self.item_type else None,
            'item_group_id': self.item_group_id,
            'supplier_id': self.supplier_id,
            'standard_rate': self.standard_rate,
            'currency': self.currency,
            'is_stock_item': self.is_stock_item,
            'has_variants': self.has_variants,
            'is_sales_item': self.is_sales_item,
            'is_purchase_item': self.is_purchase_item,
            'stock_status': self.stock_status.value if self.stock_status else None,
            'minimum_stock_level': self.minimum_stock_level,
            'maximum_stock_level': self.maximum_stock_level,
            'reorder_level': self.reorder_level,
            'stock_uom': self.stock_uom,
            'purchase_uom': self.purchase_uom,
            'sales_uom': self.sales_uom,
            'weight': self.weight,
            'weight_uom': self.weight_uom,
            'dimensions': self.dimensions,
            'image': self.image,
            'company_id': self.company_id
        })
        return data

# Warehouse Model
class Warehouse(BaseModel):
    """Warehouse model"""
    __tablename__ = 'warehouses'
    
    warehouse_name = db.Column(db.String(200), nullable=False)
    warehouse_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Location
    address_line_1 = db.Column(db.String(200))
    address_line_2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Warehouse Details
    warehouse_type = db.Column(db.String(50))  # Main, Transit, Storage, etc.
    is_group = db.Column(db.Boolean, default=False)
    parent_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))
    parent_warehouse = relationship("Warehouse", remote_side=[id])
    
    # Manager
    warehouse_manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    warehouse_manager = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    stock_entries = relationship("StockEntry", back_populates="warehouse")
    stock_movements = relationship("StockMovement", back_populates="warehouse")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'warehouse_name': self.warehouse_name,
            'warehouse_code': self.warehouse_code,
            'description': self.description,
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'warehouse_type': self.warehouse_type,
            'is_group': self.is_group,
            'parent_warehouse_id': self.parent_warehouse_id,
            'warehouse_manager_id': self.warehouse_manager_id,
            'company_id': self.company_id
        })
        return data

# Stock Entry Model
class StockEntry(BaseModel):
    """Stock Entry model"""
    __tablename__ = 'stock_entries'
    
    entry_number = db.Column(db.String(50), unique=True, nullable=False)
    entry_date = db.Column(db.DateTime, nullable=False)
    entry_type = db.Column(db.Enum(MovementType), nullable=False)
    
    # References
    reference_doctype = db.Column(db.String(50))
    reference_docname = db.Column(db.String(100))
    
    # Warehouse
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    warehouse = relationship("Warehouse", back_populates="stock_entries")
    
    # Item
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item = relationship("Item", back_populates="stock_entries")
    
    # Quantities
    quantity = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, default=0.0)
    amount = db.Column(db.Float, default=0.0)
    
    # Additional Information
    batch_number = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'entry_number': self.entry_number,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'entry_type': self.entry_type.value if self.entry_type else None,
            'reference_doctype': self.reference_doctype,
            'reference_docname': self.reference_docname,
            'warehouse_id': self.warehouse_id,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'rate': self.rate,
            'amount': self.amount,
            'batch_number': self.batch_number,
            'serial_number': self.serial_number,
            'remarks': self.remarks,
            'company_id': self.company_id
        })
        return data

# Purchase Order Model
class PurchaseOrder(BaseModel):
    """Purchase Order model"""
    __tablename__ = 'purchase_orders'
    
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    expected_delivery_date = db.Column(db.DateTime)
    
    # Supplier
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    supplier = relationship("Supplier", back_populates="purchase_orders")
    
    # Item
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item = relationship("Item", back_populates="purchase_orders")
    
    # Quantities and Pricing
    quantity = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    # Status
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.DRAFT)
    
    # Additional Information
    terms_and_conditions = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'order_number': self.order_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'supplier_id': self.supplier_id,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'rate': self.rate,
            'amount': self.amount,
            'status': self.status.value if self.status else None,
            'terms_and_conditions': self.terms_and_conditions,
            'notes': self.notes,
            'company_id': self.company_id
        })
        return data

# Sales Order Model
class SalesOrder(BaseModel):
    """Sales Order model"""
    __tablename__ = 'sales_orders'
    
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    delivery_date = db.Column(db.DateTime)
    
    # Customer
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer_name = db.Column(db.String(200))
    customer_email = db.Column(db.String(120))
    
    # Item
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item = relationship("Item", back_populates="sales_orders")
    
    # Quantities and Pricing
    quantity = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    # Status
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.DRAFT)
    
    # Additional Information
    terms_and_conditions = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'order_number': self.order_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'rate': self.rate,
            'amount': self.amount,
            'status': self.status.value if self.status else None,
            'terms_and_conditions': self.terms_and_conditions,
            'notes': self.notes,
            'company_id': self.company_id
        })
        return data

# Stock Movement Model
class StockMovement(BaseModel):
    """Stock Movement model"""
    __tablename__ = 'stock_movements'
    
    movement_date = db.Column(db.DateTime, nullable=False)
    movement_type = db.Column(db.Enum(MovementType), nullable=False)
    
    # Item
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item = relationship("Item", back_populates="stock_movements")
    
    # Warehouse
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    warehouse = relationship("Warehouse", back_populates="stock_movements")
    
    # Quantities
    quantity = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, default=0.0)
    amount = db.Column(db.Float, default=0.0)
    
    # Reference
    reference_doctype = db.Column(db.String(50))
    reference_docname = db.Column(db.String(100))
    
    # Additional Information
    batch_number = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'movement_date': self.movement_date.isoformat() if self.movement_date else None,
            'movement_type': self.movement_type.value if self.movement_type else None,
            'item_id': self.item_id,
            'warehouse_id': self.warehouse_id,
            'quantity': self.quantity,
            'rate': self.rate,
            'amount': self.amount,
            'reference_doctype': self.reference_doctype,
            'reference_docname': self.reference_docname,
            'batch_number': self.batch_number,
            'serial_number': self.serial_number,
            'remarks': self.remarks,
            'company_id': self.company_id
        })
        return data

# Item Price Model
class ItemPrice(BaseModel):
    """Item Price model"""
    __tablename__ = 'item_prices'
    
    # Item
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item = relationship("Item", back_populates="item_prices")
    
    # Price Details
    price_list = db.Column(db.String(100), nullable=False)
    rate = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Validity
    valid_from = db.Column(db.DateTime)
    valid_upto = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'item_id': self.item_id,
            'price_list': self.price_list,
            'rate': self.rate,
            'currency': self.currency,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_upto': self.valid_upto.isoformat() if self.valid_upto else None,
            'company_id': self.company_id
        })
        return data

# Item Variant Model
class ItemVariant(BaseModel):
    """Item Variant model"""
    __tablename__ = 'item_variants'
    
    # Parent Item
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item = relationship("Item", back_populates="item_variants")
    
    # Variant Details
    variant_name = db.Column(db.String(200), nullable=False)
    variant_code = db.Column(db.String(50), unique=True, nullable=False)
    attributes = db.Column(db.JSON)  # Color, Size, etc.
    
    # Pricing
    rate = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Stock Information
    stock_status = db.Column(db.Enum(StockStatus), default=StockStatus.IN_STOCK)
    minimum_stock_level = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'item_id': self.item_id,
            'variant_name': self.variant_name,
            'variant_code': self.variant_code,
            'attributes': self.attributes,
            'rate': self.rate,
            'currency': self.currency,
            'stock_status': self.stock_status.value if self.stock_status else None,
            'minimum_stock_level': self.minimum_stock_level,
            'company_id': self.company_id
        })
        return data

# Bill of Materials Model
class BOM(BaseModel):
    """Bill of Materials model"""
    __tablename__ = 'bom'
    
    bom_name = db.Column(db.String(200), nullable=False)
    bom_code = db.Column(db.String(50), unique=True, nullable=False)
    
    # Parent Item
    parent_item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    parent_item = relationship("Item")
    
    # BOM Details
    quantity = db.Column(db.Float, default=1.0)
    unit_of_measure = db.Column(db.String(50), default='Nos')
    is_active = db.Column(db.Boolean, default=True)
    
    # BOM Items (stored as JSON for simplicity)
    bom_items = db.Column(db.JSON)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'bom_name': self.bom_name,
            'bom_code': self.bom_code,
            'parent_item_id': self.parent_item_id,
            'quantity': self.quantity,
            'unit_of_measure': self.unit_of_measure,
            'is_active': self.is_active,
            'bom_items': self.bom_items,
            'company_id': self.company_id
        })
        return data

# Production Order Model
class ProductionOrder(BaseModel):
    """Production Order model"""
    __tablename__ = 'production_orders'
    
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    planned_start_date = db.Column(db.DateTime)
    planned_end_date = db.Column(db.DateTime)
    
    # Item to be produced
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item = relationship("Item")
    
    # BOM
    bom_id = db.Column(db.Integer, db.ForeignKey('bom.id'))
    bom = relationship("BOM")
    
    # Quantities
    quantity_to_produce = db.Column(db.Float, nullable=False)
    quantity_produced = db.Column(db.Float, default=0.0)
    
    # Status
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.DRAFT)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'order_number': self.order_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'planned_start_date': self.planned_start_date.isoformat() if self.planned_start_date else None,
            'planned_end_date': self.planned_end_date.isoformat() if self.planned_end_date else None,
            'item_id': self.item_id,
            'bom_id': self.bom_id,
            'quantity_to_produce': self.quantity_to_produce,
            'quantity_produced': self.quantity_produced,
            'status': self.status.value if self.status else None,
            'company_id': self.company_id
        })
        return data
