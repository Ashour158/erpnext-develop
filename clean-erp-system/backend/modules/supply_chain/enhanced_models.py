# Enhanced Supply Chain Models
# Comprehensive supply chain management with advanced features

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Date, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class ProductType(enum.Enum):
    KIT = "kit"
    MACHINE = "machine"
    SOFTWARE = "software"
    CONSUMABLE = "consumable"
    EQUIPMENT = "equipment"
    RAW_MATERIAL = "raw_material"
    FINISHED_GOOD = "finished_good"
    SEMI_FINISHED = "semi_finished"
    SPARE_PART = "spare_part"
    SERVICE = "service"

class TemperatureControl(enum.Enum):
    ROOM_TEMPERATURE = "room_temperature"
    REFRIGERATED_4_8 = "refrigerated_4_8"
    FROZEN_MINUS_20 = "frozen_minus_20"
    ULTRA_FROZEN_MINUS_70 = "ultra_frozen_minus_70"
    CONTROLLED_ROOM = "controlled_room"
    AMBIENT = "ambient"

class ItemStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    OBSOLETE = "obsolete"

class BatchStatus(enum.Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    QUARANTINE = "quarantine"
    EXPIRED = "expired"
    CONSUMED = "consumed"

class DeliveryStatus(enum.Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    PARTIALLY_DELIVERED = "partially_delivered"
    CANCELLED = "cancelled"

class VigilanceLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Enhanced Item model with comprehensive product data
class EnhancedItem(Base):
    __tablename__ = 'enhanced_items'
    
    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(100), unique=True, nullable=False, index=True)
    item_name = Column(String(255), nullable=False)
    description = Column(Text)
    sku = Column(String(100), unique=True, index=True)
    part_number = Column(String(100), index=True)
    vendor_id = Column(Integer, ForeignKey('suppliers.id'))
    manufacturer = Column(String(255))
    cost_price = Column(Float, default=0.0)
    sales_price = Column(Float, default=0.0)
    isbn = Column(String(20))
    gs1_code = Column(String(50))
    product_type = Column(Enum(ProductType), nullable=False)
    temperature_control = Column(Enum(TemperatureControl), default=TemperatureControl.ROOM_TEMPERATURE)
    status = Column(Enum(ItemStatus), default=ItemStatus.ACTIVE)
    
    # Additional parameters
    weight = Column(Float)
    dimensions = Column(JSON)  # {"length": 10, "width": 5, "height": 3, "unit": "cm"}
    color = Column(String(50))
    material = Column(String(100))
    specifications = Column(JSON)  # Additional technical specifications
    
    # Inventory tracking
    current_stock = Column(Float, default=0.0)
    minimum_stock = Column(Float, default=0.0)
    maximum_stock = Column(Float, default=0.0)
    reorder_point = Column(Float, default=0.0)
    
    # Tracking requirements
    requires_batch_tracking = Column(Boolean, default=False)
    requires_lot_tracking = Column(Boolean, default=False)
    requires_expiry_tracking = Column(Boolean, default=False)
    shelf_life_days = Column(Integer)
    
    # Compliance and certifications
    certifications = Column(JSON)  # List of certifications
    compliance_requirements = Column(JSON)  # Regulatory compliance data
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    vendor = relationship("Supplier", back_populates="items")
    batches = relationship("ItemBatch", back_populates="item", cascade="all, delete-orphan")
    lots = relationship("ItemLot", back_populates="item", cascade="all, delete-orphan")
    stock_movements = relationship("StockMovement", back_populates="item")
    sales_order_items = relationship("SalesOrderItem", back_populates="item")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="item")
    delivery_note_items = relationship("DeliveryNoteItem", back_populates="item")
    vigilance_records = relationship("VigilanceRecord", back_populates="item")

# Item Group model for categorization
class ItemGroup(Base):
    __tablename__ = 'item_groups'
    
    id = Column(Integer, primary_key=True, index=True)
    group_code = Column(String(50), unique=True, nullable=False)
    group_name = Column(String(255), nullable=False)
    description = Column(Text)
    parent_group_id = Column(Integer, ForeignKey('item_groups.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    parent_group = relationship("ItemGroup", remote_side=[id])
    child_groups = relationship("ItemGroup", back_populates="parent_group")
    items = relationship("EnhancedItem", back_populates="item_group")

# Batch tracking for items
class ItemBatch(Base):
    __tablename__ = 'item_batches'
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey('enhanced_items.id'), nullable=False)
    batch_number = Column(String(100), nullable=False, index=True)
    lot_number = Column(String(100), index=True)
    expiry_date = Column(Date)
    manufacturing_date = Column(Date)
    received_date = Column(Date, default=date.today)
    status = Column(Enum(BatchStatus), default=BatchStatus.AVAILABLE)
    
    # Quantity tracking
    initial_quantity = Column(Float, nullable=False)
    current_quantity = Column(Float, nullable=False)
    reserved_quantity = Column(Float, default=0.0)
    consumed_quantity = Column(Float, default=0.0)
    
    # Quality and compliance
    quality_certificate = Column(String(255))
    test_results = Column(JSON)
    compliance_status = Column(String(50))
    
    # Location tracking
    warehouse_location = Column(String(100))
    storage_conditions = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem", back_populates="batches")
    movements = relationship("BatchMovement", back_populates="batch")

# Lot tracking for items
class ItemLot(Base):
    __tablename__ = 'item_lots'
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey('enhanced_items.id'), nullable=False)
    lot_number = Column(String(100), nullable=False, index=True)
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    expiry_date = Column(Date)
    manufacturing_date = Column(Date)
    received_date = Column(Date, default=date.today)
    status = Column(Enum(BatchStatus), default=BatchStatus.AVAILABLE)
    
    # Quantity tracking
    initial_quantity = Column(Float, nullable=False)
    current_quantity = Column(Float, nullable=False)
    reserved_quantity = Column(Float, default=0.0)
    consumed_quantity = Column(Float, default=0.0)
    
    # Quality and compliance
    quality_certificate = Column(String(255))
    test_results = Column(JSON)
    compliance_status = Column(String(50))
    
    # Location tracking
    warehouse_location = Column(String(100))
    storage_conditions = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem", back_populates="lots")
    batch = relationship("ItemBatch")

# Enhanced Sales Order model
class EnhancedSalesOrder(Base):
    __tablename__ = 'enhanced_sales_orders'
    
    id = Column(Integer, primary_key=True, index=True)
    so_number = Column(String(100), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    crm_deal_id = Column(Integer, ForeignKey('opportunities.id'))  # Link to CRM deal
    order_date = Column(Date, default=date.today)
    delivery_date = Column(Date)
    status = Column(String(50), default='draft')
    
    # Pricing
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    
    # Shipping and delivery
    shipping_address = Column(JSON)
    billing_address = Column(JSON)
    shipping_method = Column(String(100))
    delivery_instructions = Column(Text)
    
    # Template customization
    template_id = Column(Integer, ForeignKey('document_templates.id'))
    custom_template_data = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    customer = relationship("Customer")
    crm_deal = relationship("Opportunity")
    items = relationship("SalesOrderItem", back_populates="sales_order", cascade="all, delete-orphan")
    template = relationship("DocumentTemplate")
    purchase_orders = relationship("PurchaseOrder", back_populates="sales_order")

# Enhanced Purchase Order model
class EnhancedPurchaseOrder(Base):
    __tablename__ = 'enhanced_purchase_orders'
    
    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(100), unique=True, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    sales_order_id = Column(Integer, ForeignKey('enhanced_sales_orders.id'))
    order_date = Column(Date, default=date.today)
    expected_delivery_date = Column(Date)
    actual_delivery_date = Column(Date)
    status = Column(String(50), default='draft')
    
    # Pricing
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    shipping_cost = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    
    # Consolidation
    is_consolidated = Column(Boolean, default=False)
    consolidated_po_id = Column(Integer, ForeignKey('enhanced_purchase_orders.id'))
    consolidation_date = Column(DateTime)
    
    # Template customization
    template_id = Column(Integer, ForeignKey('document_templates.id'))
    custom_template_data = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    supplier = relationship("Supplier")
    sales_order = relationship("EnhancedSalesOrder", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    template = relationship("DocumentTemplate")
    consolidated_po = relationship("EnhancedPurchaseOrder", remote_side=[id])
    delivery_notes = relationship("DeliveryNote", back_populates="purchase_order")

# Enhanced Sales Order Item
class SalesOrderItem(Base):
    __tablename__ = 'sales_order_items'
    
    id = Column(Integer, primary_key=True, index=True)
    sales_order_id = Column(Integer, ForeignKey('enhanced_sales_orders.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('enhanced_items.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0)
    tax_percentage = Column(Float, default=0.0)
    line_total = Column(Float, nullable=False)
    
    # Delivery tracking
    delivered_quantity = Column(Float, default=0.0)
    pending_quantity = Column(Float, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sales_order = relationship("EnhancedSalesOrder", back_populates="items")
    item = relationship("EnhancedItem", back_populates="sales_order_items")

# Enhanced Purchase Order Item
class PurchaseOrderItem(Base):
    __tablename__ = 'purchase_order_items'
    
    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey('enhanced_purchase_orders.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('enhanced_items.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0)
    tax_percentage = Column(Float, default=0.0)
    line_total = Column(Float, nullable=False)
    
    # Receipt tracking
    received_quantity = Column(Float, default=0.0)
    pending_quantity = Column(Float, nullable=False)
    
    # Batch/Lot tracking
    batch_number = Column(String(100))
    lot_number = Column(String(100))
    expiry_date = Column(Date)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    purchase_order = relationship("EnhancedPurchaseOrder", back_populates="items")
    item = relationship("EnhancedItem", back_populates="purchase_order_items")

# Delivery Note model
class DeliveryNote(Base):
    __tablename__ = 'delivery_notes'
    
    id = Column(Integer, primary_key=True, index=True)
    dn_number = Column(String(100), unique=True, nullable=False, index=True)
    purchase_order_id = Column(Integer, ForeignKey('enhanced_purchase_orders.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    delivery_date = Column(Date, default=date.today)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING)
    
    # Delivery details
    delivery_address = Column(JSON)
    delivery_method = Column(String(100))
    tracking_number = Column(String(100))
    delivery_instructions = Column(Text)
    
    # Template customization
    template_id = Column(Integer, ForeignKey('document_templates.id'))
    custom_template_data = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    purchase_order = relationship("EnhancedPurchaseOrder", back_populates="delivery_notes")
    customer = relationship("Customer")
    items = relationship("DeliveryNoteItem", back_populates="delivery_note", cascade="all, delete-orphan")
    template = relationship("DocumentTemplate")

# Delivery Note Item
class DeliveryNoteItem(Base):
    __tablename__ = 'delivery_note_items'
    
    id = Column(Integer, primary_key=True, index=True)
    delivery_note_id = Column(Integer, ForeignKey('delivery_notes.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('enhanced_items.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    delivered_quantity = Column(Float, default=0.0)
    pending_quantity = Column(Float, nullable=False)
    
    # Batch/Lot tracking
    batch_number = Column(String(100))
    lot_number = Column(String(100))
    expiry_date = Column(Date)
    
    # Quality check
    quality_status = Column(String(50))
    quality_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    delivery_note = relationship("DeliveryNote", back_populates="items")
    item = relationship("EnhancedItem", back_populates="delivery_note_items")

# Stock Movement tracking
class StockMovement(Base):
    __tablename__ = 'stock_movements'
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey('enhanced_items.id'), nullable=False)
    movement_type = Column(String(50), nullable=False)  # in, out, transfer, adjustment
    quantity = Column(Float, nullable=False)
    reference_type = Column(String(50))  # purchase_order, sales_order, delivery_note, etc.
    reference_id = Column(Integer)
    batch_number = Column(String(100))
    lot_number = Column(String(100))
    
    # Location tracking
    from_location = Column(String(100))
    to_location = Column(String(100))
    
    # Metadata
    movement_date = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem", back_populates="stock_movements")

# Batch Movement tracking
class BatchMovement(Base):
    __tablename__ = 'batch_movements'
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey('item_batches.id'), nullable=False)
    movement_type = Column(String(50), nullable=False)
    quantity = Column(Float, nullable=False)
    reference_type = Column(String(50))
    reference_id = Column(Integer)
    
    # Location tracking
    from_location = Column(String(100))
    to_location = Column(String(100))
    
    # Metadata
    movement_date = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    batch = relationship("ItemBatch", back_populates="movements")

# Vigilance System for Supply Chain
class VigilanceRecord(Base):
    __tablename__ = 'vigilance_records'
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    lot_id = Column(Integer, ForeignKey('item_lots.id'))
    vigilance_type = Column(String(100), nullable=False)  # quality, compliance, expiry, etc.
    vigilance_level = Column(Enum(VigilanceLevel), nullable=False)
    description = Column(Text, nullable=False)
    corrective_action = Column(Text)
    preventive_action = Column(Text)
    status = Column(String(50), default='open')  # open, in_progress, resolved, closed
    
    # Tracking
    detected_date = Column(DateTime, default=datetime.utcnow)
    resolution_date = Column(DateTime)
    assigned_to = Column(Integer, ForeignKey('users.id'))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem", back_populates="vigilance_records")
    batch = relationship("ItemBatch")
    lot = relationship("ItemLot")
    assigned_user = relationship("User", foreign_keys=[assigned_to])

# Document Templates for customization
class DocumentTemplate(Base):
    __tablename__ = 'document_templates'
    
    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(255), nullable=False)
    template_type = Column(String(50), nullable=False)  # sales_order, purchase_order, delivery_note
    template_file_path = Column(String(500))  # Path to uploaded template file
    template_file_type = Column(String(10))  # docx, pdf
    is_active = Column(Boolean, default=True)
    
    # Template configuration
    template_config = Column(JSON)  # Configuration for template fields
    default_template = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    sales_orders = relationship("EnhancedSalesOrder", back_populates="template")
    purchase_orders = relationship("EnhancedPurchaseOrder", back_populates="template")
    delivery_notes = relationship("DeliveryNote", back_populates="template")

# Supply Chain Reports
class SupplyChainReport(Base):
    __tablename__ = 'supply_chain_reports'
    
    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # vendor_po, items_amount, consumption, delivery
    report_period = Column(String(20), nullable=False)  # weekly, monthly, quarterly, annual
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Report data
    report_data = Column(JSON)
    report_summary = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Add relationships to existing models
EnhancedItem.item_group_id = Column(Integer, ForeignKey('item_groups.id'))
EnhancedItem.item_group = relationship("ItemGroup", back_populates="items")
