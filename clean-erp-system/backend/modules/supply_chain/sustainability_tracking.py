# Sustainability Tracking for Supply Chain
# Environmental impact monitoring and carbon footprint tracking

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum, Date
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class SustainabilityMetric(enum.Enum):
    CARBON_FOOTPRINT = "carbon_footprint"
    WATER_USAGE = "water_usage"
    ENERGY_CONSUMPTION = "energy_consumption"
    WASTE_GENERATION = "waste_generation"
    RECYCLING_RATE = "recycling_rate"
    RENEWABLE_ENERGY = "renewable_energy"
    SUSTAINABLE_MATERIALS = "sustainable_materials"
    BIODIVERSITY_IMPACT = "biodiversity_impact"
    AIR_QUALITY = "air_quality"
    SOIL_HEALTH = "soil_health"

class ImpactLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CertificationType(enum.Enum):
    ISO_14001 = "iso_14001"
    LEED = "leed"
    BREEAM = "breeam"
    ENERGY_STAR = "energy_star"
    FAIR_TRADE = "fair_trade"
    ORGANIC = "organic"
    SUSTAINABLE_FORESTRY = "sustainable_forestry"
    CARBON_NEUTRAL = "carbon_neutral"
    CUSTOM = "custom"

class SustainabilityStatus(enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

# Carbon Footprint Tracking
class CarbonFootprint(Base):
    __tablename__ = 'carbon_footprints'
    
    id = Column(Integer, primary_key=True, index=True)
    footprint_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    lot_id = Column(Integer, ForeignKey('item_lots.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    transport_id = Column(Integer, ForeignKey('transport_legs.id'))
    
    # Carbon footprint data
    scope_1_emissions = Column(Float, default=0.0)  # Direct emissions
    scope_2_emissions = Column(Float, default=0.0)  # Indirect emissions from energy
    scope_3_emissions = Column(Float, default=0.0)  # Other indirect emissions
    total_emissions = Column(Float, default=0.0)  # Total CO2 equivalent
    emissions_unit = Column(String(20), default='kg_co2e')  # Unit of measurement
    
    # Emission sources
    manufacturing_emissions = Column(Float, default=0.0)
    transport_emissions = Column(Float, default=0.0)
    packaging_emissions = Column(Float, default=0.0)
    disposal_emissions = Column(Float, default=0.0)
    energy_emissions = Column(Float, default=0.0)
    
    # Calculation details
    calculation_method = Column(String(50))  # Method used for calculation
    calculation_date = Column(DateTime, default=datetime.utcnow)
    calculation_notes = Column(Text)
    data_sources = Column(JSON)  # Sources of emission data
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey('users.id'))
    verified_at = Column(DateTime)
    verification_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem")
    batch = relationship("ItemBatch")
    lot = relationship("ItemLot")
    supplier = relationship("Supplier")
    transport = relationship("TransportLeg")
    verifier = relationship("User", foreign_keys=[verified_by])
    creator = relationship("User", foreign_keys=[created_by])

# Water Usage Tracking
class WaterUsage(Base):
    __tablename__ = 'water_usage'
    
    id = Column(Integer, primary_key=True, index=True)
    usage_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    lot_id = Column(Integer, ForeignKey('item_lots.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    
    # Water usage data
    total_water_usage = Column(Float, nullable=False)  # Total water usage
    usage_unit = Column(String(20), default='liters')  # Unit of measurement
    usage_period_start = Column(DateTime, nullable=False)
    usage_period_end = Column(DateTime, nullable=False)
    
    # Usage breakdown
    direct_water_usage = Column(Float, default=0.0)  # Direct water consumption
    indirect_water_usage = Column(Float, default=0.0)  # Indirect water consumption
    recycled_water = Column(Float, default=0.0)  # Recycled water usage
    wastewater_generated = Column(Float, default=0.0)  # Wastewater generated
    
    # Water quality
    water_quality_score = Column(Float)  # Water quality score (0-100)
    contamination_level = Column(Float)  # Contamination level
    treatment_required = Column(Boolean, default=False)
    treatment_method = Column(String(100))
    
    # Efficiency metrics
    water_efficiency_ratio = Column(Float)  # Water efficiency ratio
    water_recycling_rate = Column(Float)  # Water recycling rate
    water_waste_rate = Column(Float)  # Water waste rate
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem")
    batch = relationship("ItemBatch")
    lot = relationship("ItemLot")
    supplier = relationship("Supplier")
    facility = relationship("Facility")
    creator = relationship("User")

# Energy Consumption Tracking
class EnergyConsumption(Base):
    __tablename__ = 'energy_consumption'
    
    id = Column(Integer, primary_key=True, index=True)
    consumption_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    lot_id = Column(Integer, ForeignKey('item_lots.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    
    # Energy consumption data
    total_energy_consumption = Column(Float, nullable=False)  # Total energy consumption
    energy_unit = Column(String(20), default='kwh')  # Unit of measurement
    consumption_period_start = Column(DateTime, nullable=False)
    consumption_period_end = Column(DateTime, nullable=False)
    
    # Energy sources
    renewable_energy = Column(Float, default=0.0)  # Renewable energy consumption
    non_renewable_energy = Column(Float, default=0.0)  # Non-renewable energy consumption
    solar_energy = Column(Float, default=0.0)  # Solar energy
    wind_energy = Column(Float, default=0.0)  # Wind energy
    hydro_energy = Column(Float, default=0.0)  # Hydroelectric energy
    nuclear_energy = Column(Float, default=0.0)  # Nuclear energy
    fossil_fuel_energy = Column(Float, default=0.0)  # Fossil fuel energy
    
    # Energy efficiency
    energy_efficiency_ratio = Column(Float)  # Energy efficiency ratio
    renewable_energy_percentage = Column(Float)  # Percentage of renewable energy
    energy_intensity = Column(Float)  # Energy intensity per unit of output
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem")
    batch = relationship("ItemBatch")
    lot = relationship("ItemLot")
    supplier = relationship("Supplier")
    facility = relationship("Facility")
    creator = relationship("User")

# Waste Generation Tracking
class WasteGeneration(Base):
    __tablename__ = 'waste_generation'
    
    id = Column(Integer, primary_key=True, index=True)
    waste_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    lot_id = Column(Integer, ForeignKey('item_lots.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    
    # Waste generation data
    total_waste_generated = Column(Float, nullable=False)  # Total waste generated
    waste_unit = Column(String(20), default='kg')  # Unit of measurement
    generation_period_start = Column(DateTime, nullable=False)
    generation_period_end = Column(DateTime, nullable=False)
    
    # Waste types
    hazardous_waste = Column(Float, default=0.0)  # Hazardous waste
    non_hazardous_waste = Column(Float, default=0.0)  # Non-hazardous waste
    recyclable_waste = Column(Float, default=0.0)  # Recyclable waste
    organic_waste = Column(Float, default=0.0)  # Organic waste
    electronic_waste = Column(Float, default=0.0)  # Electronic waste
    packaging_waste = Column(Float, default=0.0)  # Packaging waste
    
    # Waste management
    waste_recycled = Column(Float, default=0.0)  # Waste recycled
    waste_reused = Column(Float, default=0.0)  # Waste reused
    waste_composted = Column(Float, default=0.0)  # Waste composted
    waste_landfilled = Column(Float, default=0.0)  # Waste landfilled
    waste_incinerated = Column(Float, default=0.0)  # Waste incinerated
    
    # Waste efficiency
    recycling_rate = Column(Float)  # Recycling rate
    waste_reduction_rate = Column(Float)  # Waste reduction rate
    circular_economy_score = Column(Float)  # Circular economy score
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem")
    batch = relationship("ItemBatch")
    lot = relationship("ItemLot")
    supplier = relationship("Supplier")
    facility = relationship("Facility")
    creator = relationship("User")

# Sustainable Materials Tracking
class SustainableMaterials(Base):
    __tablename__ = 'sustainable_materials'
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    lot_id = Column(Integer, ForeignKey('item_lots.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    
    # Material data
    material_name = Column(String(255), nullable=False)
    material_type = Column(String(100), nullable=False)  # raw_material, component, packaging
    material_weight = Column(Float, nullable=False)
    weight_unit = Column(String(20), default='kg')
    
    # Sustainability attributes
    is_recycled = Column(Boolean, default=False)  # Is recycled material
    is_renewable = Column(Boolean, default=False)  # Is renewable material
    is_biodegradable = Column(Boolean, default=False)  # Is biodegradable
    is_compostable = Column(Boolean, default=False)  # Is compostable
    is_certified_sustainable = Column(Boolean, default=False)  # Is certified sustainable
    
    # Material composition
    recycled_content_percentage = Column(Float, default=0.0)  # Percentage of recycled content
    renewable_content_percentage = Column(Float, default=0.0)  # Percentage of renewable content
    bio_based_percentage = Column(Float, default=0.0)  # Percentage of bio-based content
    
    # Certifications
    sustainability_certifications = Column(JSON)  # List of sustainability certifications
    certification_bodies = Column(JSON)  # Certification bodies
    certification_dates = Column(JSON)  # Certification dates
    certification_valid_until = Column(Date)  # Certification validity
    
    # Life cycle assessment
    lca_score = Column(Float)  # Life cycle assessment score
    environmental_impact_score = Column(Float)  # Environmental impact score
    carbon_footprint_per_kg = Column(Float)  # Carbon footprint per kg
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem")
    batch = relationship("ItemBatch")
    lot = relationship("ItemLot")
    supplier = relationship("Supplier")
    creator = relationship("User")

# Sustainability Certifications
class SustainabilityCertification(Base):
    __tablename__ = 'sustainability_certifications'
    
    id = Column(Integer, primary_key=True, index=True)
    certification_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Certification details
    certification_name = Column(String(255), nullable=False)
    certification_type = Column(Enum(CertificationType), nullable=False)
    certification_body = Column(String(255), nullable=False)
    certification_standard = Column(String(255), nullable=False)
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    lot_id = Column(Integer, ForeignKey('item_lots.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    
    # Certification status
    certification_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    is_valid = Column(Boolean, default=True)
    is_renewable = Column(Boolean, default=True)
    
    # Certification details
    certification_score = Column(Float)  # Certification score (0-100)
    certification_level = Column(String(50))  # Certification level
    certification_scope = Column(JSON)  # Certification scope
    certification_requirements = Column(JSON)  # Certification requirements
    
    # Audit information
    last_audit_date = Column(Date)
    next_audit_date = Column(Date)
    audit_frequency = Column(String(20), default='annual')  # annual, biennial, triennial
    audit_results = Column(JSON)  # Audit results
    
    # Documentation
    certificate_document = Column(String(500))  # Path to certificate document
    audit_reports = Column(JSON)  # List of audit reports
    compliance_evidence = Column(JSON)  # Compliance evidence
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem")
    batch = relationship("ItemBatch")
    lot = relationship("ItemLot")
    supplier = relationship("Supplier")
    facility = relationship("Facility")
    creator = relationship("User")

# Sustainability Goals and Targets
class SustainabilityGoal(Base):
    __tablename__ = 'sustainability_goals'
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Goal details
    goal_name = Column(String(255), nullable=False)
    goal_description = Column(Text)
    goal_type = Column(Enum(SustainabilityMetric), nullable=False)
    goal_category = Column(String(50))  # environmental, social, economic
    
    # Goal targets
    target_value = Column(Float, nullable=False)
    target_unit = Column(String(20), nullable=False)
    baseline_value = Column(Float, default=0.0)
    baseline_date = Column(Date)
    
    # Goal timeline
    start_date = Column(Date, nullable=False)
    target_date = Column(Date, nullable=False)
    is_achieved = Column(Boolean, default=False)
    achieved_date = Column(Date)
    
    # Goal progress
    current_value = Column(Float, default=0.0)
    progress_percentage = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Goal scope
    scope_items = Column(JSON)  # Items included in goal
    scope_suppliers = Column(JSON)  # Suppliers included in goal
    scope_facilities = Column(JSON)  # Facilities included in goal
    
    # Goal status
    status = Column(Enum(SustainabilityStatus), default=SustainabilityStatus.GOOD)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")
    progress_updates = relationship("SustainabilityProgress", back_populates="goal")

# Sustainability Progress Tracking
class SustainabilityProgress(Base):
    __tablename__ = 'sustainability_progress'
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey('sustainability_goals.id'), nullable=False)
    progress_date = Column(Date, nullable=False)
    
    # Progress data
    current_value = Column(Float, nullable=False)
    progress_percentage = Column(Float, nullable=False)
    improvement_rate = Column(Float)  # Rate of improvement
    
    # Progress details
    progress_notes = Column(Text)
    achievements = Column(JSON)  # Key achievements
    challenges = Column(JSON)  # Challenges faced
    actions_taken = Column(JSON)  # Actions taken
    
    # Data sources
    data_sources = Column(JSON)  # Sources of progress data
    data_quality = Column(String(20), default='good')  # good, fair, poor
    verification_status = Column(String(20), default='pending')  # pending, verified, rejected
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    goal = relationship("SustainabilityGoal", back_populates="progress_updates")
    creator = relationship("User")

# Sustainability Reporting
class SustainabilityReport(Base):
    __tablename__ = 'sustainability_reports'
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Report details
    report_name = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # annual, quarterly, monthly, ad_hoc
    report_period_start = Column(Date, nullable=False)
    report_period_end = Column(Date, nullable=False)
    
    # Report content
    executive_summary = Column(Text)
    key_metrics = Column(JSON)  # Key sustainability metrics
    goal_progress = Column(JSON)  # Progress towards goals
    achievements = Column(JSON)  # Key achievements
    challenges = Column(JSON)  # Challenges faced
    recommendations = Column(JSON)  # Recommendations
    
    # Report data
    report_data = Column(JSON)  # Detailed report data
    charts_data = Column(JSON)  # Charts and visualizations
    appendices = Column(JSON)  # Report appendices
    
    # Report status
    status = Column(String(20), default='draft')  # draft, review, approved, published
    is_public = Column(Boolean, default=False)
    published_date = Column(DateTime)
    
    # Compliance
    compliance_standards = Column(JSON)  # Compliance standards
    audit_trail = Column(JSON)  # Audit trail
    approval_chain = Column(JSON)  # Approval chain
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Additional supporting models
class Facility(Base):
    __tablename__ = 'facilities'
    
    id = Column(Integer, primary_key=True, index=True)
    facility_name = Column(String(255), nullable=False)
    facility_type = Column(String(50))  # manufacturing, warehouse, office, retail
    location = Column(String(255))
    coordinates = Column(JSON)  # GPS coordinates
    
    # Sustainability attributes
    is_green_building = Column(Boolean, default=False)
    leed_certification = Column(String(50))
    energy_rating = Column(String(20))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))

class TransportLeg(Base):
    __tablename__ = 'transport_legs'
    
    id = Column(Integer, primary_key=True, index=True)
    transport_type = Column(String(50))  # road, rail, air, sea
    distance_km = Column(Float)
    fuel_type = Column(String(50))
    fuel_consumption = Column(Float)
    
    # Environmental impact
    carbon_emissions = Column(Float)
    emissions_factor = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
