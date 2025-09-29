# Advanced Supply Chain Models
# Intelligent supply chain management with demand forecasting, supplier management, and logistics optimization

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

class DemandForecastMethod(enum.Enum):
    MOVING_AVERAGE = "Moving Average"
    EXPONENTIAL_SMOOTHING = "Exponential Smoothing"
    LINEAR_REGRESSION = "Linear Regression"
    SEASONAL_DECOMPOSITION = "Seasonal Decomposition"
    MACHINE_LEARNING = "Machine Learning"

class SupplierRating(enum.Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    AVERAGE = "Average"
    POOR = "Poor"
    CRITICAL = "Critical"

class OrderStatus(enum.Enum):
    DRAFT = "Draft"
    PENDING = "Pending"
    APPROVED = "Approved"
    ORDERED = "Ordered"
    PARTIALLY_RECEIVED = "Partially Received"
    RECEIVED = "Received"
    CANCELLED = "Cancelled"

class ShipmentStatus(enum.Enum):
    PENDING = "Pending"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"
    DELAYED = "Delayed"
    LOST = "Lost"
    DAMAGED = "Damaged"

class InventoryABC(enum.Enum):
    A = "A"  # High value, low quantity
    B = "B"  # Medium value, medium quantity
    C = "C"  # Low value, high quantity

# Demand Forecasting Models
class DemandForecast(BaseModel):
    """Demand forecast model"""
    __tablename__ = 'demand_forecasts'
    
    # Forecast Information
    forecast_name = db.Column(db.String(200), nullable=False)
    forecast_period_start = db.Column(db.Date, nullable=False)
    forecast_period_end = db.Column(db.Date, nullable=False)
    forecast_method = db.Column(db.Enum(DemandForecastMethod), nullable=False)
    
    # Item Information
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item = relationship("Item")
    
    # Forecast Data
    forecasted_quantity = db.Column(db.Float, default=0.0)
    actual_quantity = db.Column(db.Float, default=0.0)
    forecast_accuracy = db.Column(db.Float, default=0.0)
    confidence_level = db.Column(db.Float, default=0.0)
    
    # Forecast Parameters
    forecast_parameters = db.Column(db.JSON)  # Method-specific parameters
    seasonal_factors = db.Column(db.JSON)  # Seasonal adjustment factors
    trend_factors = db.Column(db.JSON)  # Trend analysis factors
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'forecast_name': self.forecast_name,
            'forecast_period_start': self.forecast_period_start.isoformat() if self.forecast_period_start else None,
            'forecast_period_end': self.forecast_period_end.isoformat() if self.forecast_period_end else None,
            'forecast_method': self.forecast_method.value if self.forecast_method else None,
            'item_id': self.item_id,
            'forecasted_quantity': self.forecasted_quantity,
            'actual_quantity': self.actual_quantity,
            'forecast_accuracy': self.forecast_accuracy,
            'confidence_level': self.confidence_level,
            'forecast_parameters': self.forecast_parameters,
            'seasonal_factors': self.seasonal_factors,
            'trend_factors': self.trend_factors,
            'company_id': self.company_id
        })
        return data

class SafetyStock(BaseModel):
    """Safety stock model"""
    __tablename__ = 'safety_stocks'
    
    # Item Information
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item = relationship("Item")
    
    # Safety Stock Calculation
    current_stock = db.Column(db.Float, default=0.0)
    safety_stock_level = db.Column(db.Float, default=0.0)
    reorder_point = db.Column(db.Float, default=0.0)
    reorder_quantity = db.Column(db.Float, default=0.0)
    
    # Calculation Parameters
    lead_time_days = db.Column(db.Integer, default=0)
    demand_variability = db.Column(db.Float, default=0.0)
    lead_time_variability = db.Column(db.Float, default=0.0)
    service_level = db.Column(db.Float, default=95.0)  # Percentage
    
    # ABC Classification
    abc_classification = db.Column(db.Enum(InventoryABC))
    item_value = db.Column(db.Float, default=0.0)
    annual_usage_value = db.Column(db.Float, default=0.0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'item_id': self.item_id,
            'current_stock': self.current_stock,
            'safety_stock_level': self.safety_stock_level,
            'reorder_point': self.reorder_point,
            'reorder_quantity': self.reorder_quantity,
            'lead_time_days': self.lead_time_days,
            'demand_variability': self.demand_variability,
            'lead_time_variability': self.lead_time_variability,
            'service_level': self.service_level,
            'abc_classification': self.abc_classification.value if self.abc_classification else None,
            'item_value': self.item_value,
            'annual_usage_value': self.annual_usage_value,
            'company_id': self.company_id
        })
        return data

# Advanced Supplier Management
class Supplier(BaseModel):
    """Enhanced supplier model"""
    __tablename__ = 'suppliers'
    
    # Supplier Information
    supplier_name = db.Column(db.String(200), nullable=False)
    supplier_code = db.Column(db.String(50), unique=True, nullable=False)
    contact_person = db.Column(db.String(200))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    
    # Address Information
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Business Information
    tax_id = db.Column(db.String(50))
    business_type = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    years_in_business = db.Column(db.Integer, default=0)
    
    # Supplier Rating
    overall_rating = db.Column(db.Enum(SupplierRating), default=SupplierRating.AVERAGE)
    quality_rating = db.Column(db.Float, default=0.0)
    delivery_rating = db.Column(db.Float, default=0.0)
    price_rating = db.Column(db.Float, default=0.0)
    service_rating = db.Column(db.Float, default=0.0)
    
    # Financial Information
    credit_limit = db.Column(db.Float, default=0.0)
    payment_terms = db.Column(db.String(100))
    currency = db.Column(db.String(3), default='USD')
    
    # Supplier Settings
    is_active = db.Column(db.Boolean, default=True)
    is_preferred = db.Column(db.Boolean, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    supplier_products = relationship("SupplierProduct", back_populates="supplier")
    supplier_evaluations = relationship("SupplierEvaluation", back_populates="supplier")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'supplier_name': self.supplier_name,
            'supplier_code': self.supplier_code,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'tax_id': self.tax_id,
            'business_type': self.business_type,
            'industry': self.industry,
            'years_in_business': self.years_in_business,
            'overall_rating': self.overall_rating.value if self.overall_rating else None,
            'quality_rating': self.quality_rating,
            'delivery_rating': self.delivery_rating,
            'price_rating': self.price_rating,
            'service_rating': self.service_rating,
            'credit_limit': self.credit_limit,
            'payment_terms': self.payment_terms,
            'currency': self.currency,
            'is_active': self.is_active,
            'is_preferred': self.is_preferred,
            'is_blacklisted': self.is_blacklisted,
            'company_id': self.company_id
        })
        return data

class SupplierProduct(BaseModel):
    """Supplier product model"""
    __tablename__ = 'supplier_products'
    
    # Product Information
    product_code = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_description = db.Column(db.Text)
    
    # Supplier Association
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    supplier = relationship("Supplier", back_populates="supplier_products")
    
    # Item Association
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    item = relationship("Item")
    
    # Pricing Information
    unit_price = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    minimum_order_quantity = db.Column(db.Float, default=1.0)
    lead_time_days = db.Column(db.Integer, default=0)
    
    # Product Specifications
    specifications = db.Column(db.JSON)  # Technical specifications
    certifications = db.Column(db.JSON)  # Quality certifications
    compliance_info = db.Column(db.JSON)  # Regulatory compliance
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'product_code': self.product_code,
            'product_name': self.product_name,
            'product_description': self.product_description,
            'supplier_id': self.supplier_id,
            'item_id': self.item_id,
            'unit_price': self.unit_price,
            'currency': self.currency,
            'minimum_order_quantity': self.minimum_order_quantity,
            'lead_time_days': self.lead_time_days,
            'specifications': self.specifications,
            'certifications': self.certifications,
            'compliance_info': self.compliance_info,
            'company_id': self.company_id
        })
        return data

class SupplierEvaluation(BaseModel):
    """Supplier evaluation model"""
    __tablename__ = 'supplier_evaluations'
    
    # Evaluation Information
    evaluation_date = db.Column(db.Date, default=date.today)
    evaluation_period_start = db.Column(db.Date, nullable=False)
    evaluation_period_end = db.Column(db.Date, nullable=False)
    
    # Supplier Association
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    supplier = relationship("Supplier", back_populates="supplier_evaluations")
    
    # Evaluation Criteria
    quality_score = db.Column(db.Float, default=0.0)
    delivery_score = db.Column(db.Float, default=0.0)
    price_score = db.Column(db.Float, default=0.0)
    service_score = db.Column(db.Float, default=0.0)
    overall_score = db.Column(db.Float, default=0.0)
    
    # Performance Metrics
    on_time_delivery_rate = db.Column(db.Float, default=0.0)
    quality_acceptance_rate = db.Column(db.Float, default=0.0)
    average_lead_time = db.Column(db.Float, default=0.0)
    price_variance = db.Column(db.Float, default=0.0)
    
    # Evaluation Details
    strengths = db.Column(db.Text)
    weaknesses = db.Column(db.Text)
    improvement_recommendations = db.Column(db.Text)
    action_plan = db.Column(db.Text)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'evaluation_date': self.evaluation_date.isoformat() if self.evaluation_date else None,
            'evaluation_period_start': self.evaluation_period_start.isoformat() if self.evaluation_period_start else None,
            'evaluation_period_end': self.evaluation_period_end.isoformat() if self.evaluation_period_end else None,
            'supplier_id': self.supplier_id,
            'quality_score': self.quality_score,
            'delivery_score': self.delivery_score,
            'price_score': self.price_score,
            'service_score': self.service_score,
            'overall_score': self.overall_score,
            'on_time_delivery_rate': self.on_time_delivery_rate,
            'quality_acceptance_rate': self.quality_acceptance_rate,
            'average_lead_time': self.average_lead_time,
            'price_variance': self.price_variance,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'improvement_recommendations': self.improvement_recommendations,
            'action_plan': self.action_plan,
            'company_id': self.company_id
        })
        return data

# Advanced Purchase Order Management
class PurchaseOrder(BaseModel):
    """Enhanced purchase order model"""
    __tablename__ = 'purchase_orders'
    
    # Order Information
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    order_date = db.Column(db.Date, default=date.today)
    expected_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)
    
    # Supplier Information
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    supplier = relationship("Supplier")
    
    # Order Details
    total_amount = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.DRAFT)
    
    # Shipping Information
    shipping_address = db.Column(db.JSON)
    shipping_method = db.Column(db.String(100))
    shipping_cost = db.Column(db.Float, default=0.0)
    tracking_number = db.Column(db.String(100))
    
    # Terms and Conditions
    payment_terms = db.Column(db.String(200))
    delivery_terms = db.Column(db.String(200))
    special_instructions = db.Column(db.Text)
    
    # Approval Information
    approved_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    approved_by = relationship("Employee")
    approved_date = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    order_items = relationship("PurchaseOrderItem", back_populates="purchase_order")
    order_shipments = relationship("PurchaseOrderShipment", back_populates="purchase_order")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'order_number': self.order_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'supplier_id': self.supplier_id,
            'total_amount': self.total_amount,
            'currency': self.currency,
            'status': self.status.value if self.status else None,
            'shipping_address': self.shipping_address,
            'shipping_method': self.shipping_method,
            'shipping_cost': self.shipping_cost,
            'tracking_number': self.tracking_number,
            'payment_terms': self.payment_terms,
            'delivery_terms': self.delivery_terms,
            'special_instructions': self.special_instructions,
            'approved_by_id': self.approved_by_id,
            'approved_date': self.approved_date.isoformat() if self.approved_date else None,
            'company_id': self.company_id
        })
        return data

class PurchaseOrderItem(BaseModel):
    """Purchase order item model"""
    __tablename__ = 'purchase_order_items'
    
    # Item Information
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item = relationship("Item")
    
    # Order Association
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    purchase_order = relationship("PurchaseOrder", back_populates="order_items")
    
    # Item Details
    quantity_ordered = db.Column(db.Float, default=0.0)
    quantity_received = db.Column(db.Float, default=0.0)
    unit_price = db.Column(db.Float, default=0.0)
    line_total = db.Column(db.Float, default=0.0)
    
    # Delivery Information
    expected_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'item_id': self.item_id,
            'purchase_order_id': self.purchase_order_id,
            'quantity_ordered': self.quantity_ordered,
            'quantity_received': self.quantity_received,
            'unit_price': self.unit_price,
            'line_total': self.line_total,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'company_id': self.company_id
        })
        return data

# Logistics and Shipment Management
class PurchaseOrderShipment(BaseModel):
    """Purchase order shipment model"""
    __tablename__ = 'purchase_order_shipments'
    
    # Shipment Information
    shipment_number = db.Column(db.String(50), unique=True, nullable=False)
    shipment_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.Enum(ShipmentStatus), default=ShipmentStatus.PENDING)
    
    # Order Association
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    purchase_order = relationship("PurchaseOrder", back_populates="order_shipments")
    
    # Shipping Details
    carrier_name = db.Column(db.String(200))
    tracking_number = db.Column(db.String(100))
    shipping_cost = db.Column(db.Float, default=0.0)
    weight = db.Column(db.Float, default=0.0)
    dimensions = db.Column(db.JSON)  # Length, width, height
    
    # Delivery Information
    expected_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)
    delivery_address = db.Column(db.JSON)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'shipment_number': self.shipment_number,
            'shipment_date': self.shipment_date.isoformat() if self.shipment_date else None,
            'status': self.status.value if self.status else None,
            'purchase_order_id': self.purchase_order_id,
            'carrier_name': self.carrier_name,
            'tracking_number': self.tracking_number,
            'shipping_cost': self.shipping_cost,
            'weight': self.weight,
            'dimensions': self.dimensions,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'delivery_address': self.delivery_address,
            'company_id': self.company_id
        })
        return data

# Warehouse Management
class Warehouse(BaseModel):
    """Warehouse model"""
    __tablename__ = 'warehouses'
    
    # Warehouse Information
    warehouse_name = db.Column(db.String(200), nullable=False)
    warehouse_code = db.Column(db.String(50), unique=True, nullable=False)
    warehouse_type = db.Column(db.String(100), default='Main')  # Main, Distribution, Storage
    
    # Location Information
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Warehouse Details
    total_capacity = db.Column(db.Float, default=0.0)  # Total storage capacity
    used_capacity = db.Column(db.Float, default=0.0)  # Currently used capacity
    capacity_unit = db.Column(db.String(20), default='sqft')  # sqft, cubic meters, etc.
    
    # Warehouse Manager
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    manager = relationship("Employee")
    
    # Warehouse Settings
    is_active = db.Column(db.Boolean, default=True)
    is_automated = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    warehouse_locations = relationship("WarehouseLocation", back_populates="warehouse")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'warehouse_name': self.warehouse_name,
            'warehouse_code': self.warehouse_code,
            'warehouse_type': self.warehouse_type,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'total_capacity': self.total_capacity,
            'used_capacity': self.used_capacity,
            'capacity_unit': self.capacity_unit,
            'manager_id': self.manager_id,
            'is_active': self.is_active,
            'is_automated': self.is_automated,
            'company_id': self.company_id
        })
        return data

class WarehouseLocation(BaseModel):
    """Warehouse location model"""
    __tablename__ = 'warehouse_locations'
    
    # Location Information
    location_code = db.Column(db.String(50), nullable=False)
    location_name = db.Column(db.String(200), nullable=False)
    location_type = db.Column(db.String(100), default='Shelf')  # Shelf, Rack, Bin, Zone
    
    # Warehouse Association
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    warehouse = relationship("Warehouse", back_populates="warehouse_locations")
    
    # Location Details
    capacity = db.Column(db.Float, default=0.0)
    used_capacity = db.Column(db.Float, default=0.0)
    location_path = db.Column(db.String(200))  # A1-B2-C3 format
    
    # Location Settings
    is_active = db.Column(db.Boolean, default=True)
    is_restricted = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'location_code': self.location_code,
            'location_name': self.location_name,
            'location_type': self.location_type,
            'warehouse_id': self.warehouse_id,
            'capacity': self.capacity,
            'used_capacity': self.used_capacity,
            'location_path': self.location_path,
            'is_active': self.is_active,
            'is_restricted': self.is_restricted,
            'company_id': self.company_id
        })
        return data
