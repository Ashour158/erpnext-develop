# Global Trade and International Compliance
# International trade compliance and regulatory management

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum, Date
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class TradeType(enum.Enum):
    IMPORT = "import"
    EXPORT = "export"
    RE_EXPORT = "re_export"
    TRANSIT = "transit"
    BONDED_WAREHOUSE = "bonded_warehouse"

class TradeStatus(enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class ComplianceStatus(enum.Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    PENDING = "pending"
    EXEMPT = "exempt"

class DocumentType(enum.Enum):
    COMMERCIAL_INVOICE = "commercial_invoice"
    PACKING_LIST = "packing_list"
    BILL_OF_LADING = "bill_of_lading"
    CERTIFICATE_OF_ORIGIN = "certificate_of_origin"
    EXPORT_LICENSE = "export_license"
    IMPORT_PERMIT = "import_permit"
    PHYTOSANITARY_CERTIFICATE = "phytosanitary_certificate"
    HEALTH_CERTIFICATE = "health_certificate"
    QUALITY_CERTIFICATE = "quality_certificate"
    INSURANCE_CERTIFICATE = "insurance_certificate"
    CUSTOMS_DECLARATION = "customs_declaration"

# International Trade Transactions
class TradeTransaction(Base):
    __tablename__ = 'trade_transactions'
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Transaction details
    trade_type = Column(Enum(TradeType), nullable=False)
    transaction_date = Column(Date, default=date.today)
    status = Column(Enum(TradeStatus), default=TradeStatus.DRAFT)
    
    # Parties involved
    exporter_id = Column(Integer, ForeignKey('companies.id'))
    importer_id = Column(Integer, ForeignKey('companies.id'))
    freight_forwarder_id = Column(Integer, ForeignKey('suppliers.id'))
    customs_broker_id = Column(Integer, ForeignKey('suppliers.id'))
    
    # Trade route
    origin_country = Column(String(100), nullable=False)
    origin_port = Column(String(100))
    destination_country = Column(String(100), nullable=False)
    destination_port = Column(String(100))
    transit_countries = Column(JSON)  # List of transit countries
    
    # Financial details
    total_value = Column(Float, nullable=False)
    currency = Column(String(3), default='USD')
    incoterms = Column(String(10))  # FOB, CIF, EXW, etc.
    payment_terms = Column(String(50))
    payment_method = Column(String(50))
    
    # Shipping details
    shipping_method = Column(String(50))  # sea, air, road, rail
    vessel_name = Column(String(255))
    voyage_number = Column(String(100))
    container_numbers = Column(JSON)  # List of container numbers
    seal_numbers = Column(JSON)  # List of seal numbers
    
    # Compliance
    compliance_status = Column(Enum(ComplianceStatus), default=ComplianceStatus.PENDING)
    regulatory_requirements = Column(JSON)  # List of regulatory requirements
    compliance_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    exporter = relationship("Company", foreign_keys=[exporter_id])
    importer = relationship("Company", foreign_keys=[importer_id])
    freight_forwarder = relationship("Supplier", foreign_keys=[freight_forwarder_id])
    customs_broker = relationship("Supplier", foreign_keys=[customs_broker_id])
    creator = relationship("User")
    items = relationship("TradeItem", back_populates="transaction", cascade="all, delete-orphan")
    documents = relationship("TradeDocument", back_populates="transaction", cascade="all, delete-orphan")
    compliance_checks = relationship("ComplianceCheck", back_populates="transaction", cascade="all, delete-orphan")

# Trade Items
class TradeItem(Base):
    __tablename__ = 'trade_items'
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey('trade_transactions.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('enhanced_items.id'), nullable=False)
    
    # Item details
    item_description = Column(Text, nullable=False)
    quantity = Column(Float, nullable=False)
    unit_of_measure = Column(String(20), nullable=False)
    unit_price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    
    # Classification
    hs_code = Column(String(20))  # Harmonized System code
    country_of_origin = Column(String(100), nullable=False)
    preferential_origin = Column(Boolean, default=False)
    
    # Regulatory information
    regulatory_classification = Column(String(100))
    license_requirements = Column(JSON)  # List of license requirements
    restrictions = Column(JSON)  # List of restrictions
    prohibitions = Column(JSON)  # List of prohibitions
    
    # Compliance
    compliance_requirements = Column(JSON)  # Item-specific compliance requirements
    certification_requirements = Column(JSON)  # Required certifications
    testing_requirements = Column(JSON)  # Required testing
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transaction = relationship("TradeTransaction", back_populates="items")
    item = relationship("EnhancedItem")

# Trade Documents
class TradeDocument(Base):
    __tablename__ = 'trade_documents'
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey('trade_transactions.id'), nullable=False)
    
    # Document details
    document_type = Column(Enum(DocumentType), nullable=False)
    document_number = Column(String(100), nullable=False)
    document_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    
    # Document content
    document_title = Column(String(255), nullable=False)
    document_description = Column(Text)
    document_content = Column(JSON)  # Document-specific content
    document_template = Column(String(100))  # Template used
    
    # Document files
    document_file_path = Column(String(500))
    document_file_type = Column(String(20))  # pdf, docx, xlsx, etc.
    document_size = Column(Integer)
    
    # Status
    is_required = Column(Boolean, default=True)
    is_submitted = Column(Boolean, default=False)
    submitted_date = Column(DateTime)
    is_approved = Column(Boolean, default=False)
    approved_date = Column(DateTime)
    approved_by = Column(Integer, ForeignKey('users.id'))
    
    # Validation
    is_validated = Column(Boolean, default=False)
    validated_date = Column(DateTime)
    validated_by = Column(Integer, ForeignKey('users.id'))
    validation_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    transaction = relationship("TradeTransaction", back_populates="documents")
    approver = relationship("User", foreign_keys=[approved_by])
    validator = relationship("User", foreign_keys=[validated_by])
    creator = relationship("User", foreign_keys=[created_by])

# Compliance Checks
class ComplianceCheck(Base):
    __tablename__ = 'compliance_checks'
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey('trade_transactions.id'), nullable=False)
    
    # Check details
    check_type = Column(String(50), nullable=False)  # regulatory, customs, security, quality
    check_name = Column(String(255), nullable=False)
    check_description = Column(Text)
    regulatory_authority = Column(String(255))
    
    # Check requirements
    requirements = Column(JSON)  # List of requirements
    applicable_regulations = Column(JSON)  # Applicable regulations
    check_criteria = Column(JSON)  # Check criteria
    
    # Check results
    status = Column(Enum(ComplianceStatus), default=ComplianceStatus.PENDING)
    check_date = Column(DateTime, default=datetime.utcnow)
    check_result = Column(Text)
    compliance_score = Column(Float)  # 0-100 compliance score
    findings = Column(JSON)  # Detailed findings
    
    # Actions
    corrective_actions = Column(JSON)  # Required corrective actions
    preventive_actions = Column(JSON)  # Preventive actions
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_date = Column(DateTime)
    verified_by = Column(Integer, ForeignKey('users.id'))
    verification_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    checked_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    transaction = relationship("TradeTransaction", back_populates="compliance_checks")
    checker = relationship("User", foreign_keys=[checked_by])
    verifier = relationship("User", foreign_keys=[verified_by])

# Regulatory Requirements
class RegulatoryRequirement(Base):
    __tablename__ = 'regulatory_requirements'
    
    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Requirement details
    requirement_name = Column(String(255), nullable=False)
    requirement_type = Column(String(50), nullable=False)  # import, export, transit, general
    regulatory_authority = Column(String(255), nullable=False)
    applicable_countries = Column(JSON)  # List of applicable countries
    applicable_products = Column(JSON)  # List of applicable products
    
    # Requirement content
    requirement_description = Column(Text, nullable=False)
    requirement_criteria = Column(JSON)  # Requirement criteria
    compliance_standards = Column(JSON)  # Compliance standards
    documentation_requirements = Column(JSON)  # Required documentation
    
    # Validity
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    is_active = Column(Boolean, default=True)
    
    # Compliance
    compliance_frequency = Column(String(20), default='per_transaction')  # per_transaction, annual, quarterly
    compliance_deadline = Column(Integer)  # Days before transaction
    penalty_amount = Column(Float)  # Penalty for non-compliance
    penalty_currency = Column(String(3), default='USD')
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")

# Country Regulations
class CountryRegulation(Base):
    __tablename__ = 'country_regulations'
    
    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String(3), nullable=False, index=True)
    country_name = Column(String(100), nullable=False)
    
    # Trade regulations
    import_regulations = Column(JSON)  # Import regulations
    export_regulations = Column(JSON)  # Export regulations
    transit_regulations = Column(JSON)  # Transit regulations
    customs_procedures = Column(JSON)  # Customs procedures
    
    # Tariffs and duties
    tariff_schedules = Column(JSON)  # Tariff schedules
    duty_rates = Column(JSON)  # Duty rates
    preferential_rates = Column(JSON)  # Preferential rates
    anti_dumping_duties = Column(JSON)  # Anti-dumping duties
    
    # Trade agreements
    trade_agreements = Column(JSON)  # Trade agreements
    preferential_treatment = Column(JSON)  # Preferential treatment
    rules_of_origin = Column(JSON)  # Rules of origin
    
    # Documentation requirements
    required_documents = Column(JSON)  # Required documents
    document_templates = Column(JSON)  # Document templates
    certification_requirements = Column(JSON)  # Certification requirements
    
    # Compliance
    compliance_deadlines = Column(JSON)  # Compliance deadlines
    penalty_structures = Column(JSON)  # Penalty structures
    appeal_procedures = Column(JSON)  # Appeal procedures
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    trade_transactions = relationship("TradeTransaction")

# Trade Agreements
class TradeAgreement(Base):
    __tablename__ = 'trade_agreements'
    
    id = Column(Integer, primary_key=True, index=True)
    agreement_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Agreement details
    agreement_name = Column(String(255), nullable=False)
    agreement_type = Column(String(50), nullable=False)  # fta, cptpp, wto, bilateral
    participating_countries = Column(JSON, nullable=False)  # List of participating countries
    
    # Agreement terms
    agreement_description = Column(Text)
    key_provisions = Column(JSON)  # Key provisions
    tariff_reductions = Column(JSON)  # Tariff reductions
    rules_of_origin = Column(JSON)  # Rules of origin
    
    # Validity
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    is_active = Column(Boolean, default=True)
    
    # Benefits
    preferential_treatment = Column(JSON)  # Preferential treatment
    duty_reductions = Column(JSON)  # Duty reductions
    quota_benefits = Column(JSON)  # Quota benefits
    
    # Compliance
    compliance_requirements = Column(JSON)  # Compliance requirements
    documentation_requirements = Column(JSON)  # Documentation requirements
    certification_requirements = Column(JSON)  # Certification requirements
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    trade_transactions = relationship("TradeTransaction")

# Customs Declarations
class CustomsDeclaration(Base):
    __tablename__ = 'customs_declarations'
    
    id = Column(Integer, primary_key=True, index=True)
    declaration_id = Column(String(100), unique=True, nullable=False, index=True)
    transaction_id = Column(Integer, ForeignKey('trade_transactions.id'), nullable=False)
    
    # Declaration details
    declaration_type = Column(String(50), nullable=False)  # import, export, transit
    customs_office = Column(String(255), nullable=False)
    customs_officer = Column(String(255))
    declaration_date = Column(DateTime, default=datetime.utcnow)
    
    # Declaration content
    declaration_data = Column(JSON, nullable=False)  # Declaration data
    total_duty_amount = Column(Float, default=0.0)
    total_tax_amount = Column(Float, default=0.0)
    total_fees = Column(Float, default=0.0)
    currency = Column(String(3), default='USD')
    
    # Status
    status = Column(String(20), default='draft')  # draft, submitted, under_review, approved, rejected
    submission_date = Column(DateTime)
    approval_date = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Processing
    processing_time = Column(Integer)  # Processing time in hours
    customs_clearance_date = Column(DateTime)
    release_date = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    transaction = relationship("TradeTransaction")
    creator = relationship("User")

# Trade Analytics
class TradeAnalytics(Base):
    __tablename__ = 'trade_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    analytics_type = Column(String(50), nullable=False)  # volume, value, compliance, performance
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Analytics data
    analytics_data = Column(JSON, nullable=False)
    key_metrics = Column(JSON)  # Key metrics
    trends = Column(JSON)  # Trend analysis
    insights = Column(JSON)  # Key insights
    
    # Performance metrics
    total_transactions = Column(Integer, default=0)
    total_value = Column(Float, default=0.0)
    compliance_rate = Column(Float, default=0.0)
    average_processing_time = Column(Float, default=0.0)
    
    # Country analysis
    top_export_countries = Column(JSON)  # Top export countries
    top_import_countries = Column(JSON)  # Top import countries
    trade_balance = Column(JSON)  # Trade balance by country
    
    # Product analysis
    top_export_products = Column(JSON)  # Top export products
    top_import_products = Column(JSON)  # Top import products
    product_performance = Column(JSON)  # Product performance
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    calculated_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    calculator = relationship("User")

# Trade Risk Assessment
class TradeRiskAssessment(Base):
    __tablename__ = 'trade_risk_assessments'
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String(100), unique=True, nullable=False, index=True)
    transaction_id = Column(Integer, ForeignKey('trade_transactions.id'), nullable=False)
    
    # Risk assessment
    risk_level = Column(String(20), nullable=False)  # low, medium, high, critical
    risk_score = Column(Float, nullable=False)  # 0-100 risk score
    risk_factors = Column(JSON)  # Risk factors identified
    risk_mitigation = Column(JSON)  # Risk mitigation measures
    
    # Risk categories
    regulatory_risk = Column(Float, default=0.0)  # Regulatory risk score
    compliance_risk = Column(Float, default=0.0)  # Compliance risk score
    financial_risk = Column(Float, default=0.0)  # Financial risk score
    operational_risk = Column(Float, default=0.0)  # Operational risk score
    reputational_risk = Column(Float, default=0.0)  # Reputational risk score
    
    # Assessment details
    assessment_date = Column(DateTime, default=datetime.utcnow)
    assessed_by = Column(Integer, ForeignKey('users.id'))
    assessment_notes = Column(Text)
    
    # Recommendations
    recommendations = Column(JSON)  # Risk mitigation recommendations
    monitoring_requirements = Column(JSON)  # Monitoring requirements
    review_frequency = Column(String(20), default='monthly')  # Review frequency
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    transaction = relationship("TradeTransaction")
    assessor = relationship("User")
