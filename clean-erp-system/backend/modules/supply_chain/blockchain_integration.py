# Blockchain Integration for Supply Chain Transparency
# Immutable record keeping and traceability

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum
import hashlib
import json

class BlockchainType(enum.Enum):
    ETHEREUM = "ethereum"
    HYPERLEDGER = "hyperledger"
    CORDRA = "cordra"
    PRIVATE = "private"
    CONSORTIUM = "consortium"

class TransactionType(enum.Enum):
    ITEM_CREATION = "item_creation"
    ITEM_TRANSFER = "item_transfer"
    QUALITY_CHECK = "quality_check"
    BATCH_CREATION = "batch_creation"
    BATCH_TRANSFER = "batch_transfer"
    CERTIFICATION = "certification"
    COMPLIANCE = "compliance"
    OWNERSHIP_CHANGE = "ownership_change"
    LOCATION_UPDATE = "location_update"
    TEMPERATURE_LOG = "temperature_log"

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REJECTED = "rejected"

class SmartContractType(enum.Enum):
    QUALITY_ASSURANCE = "quality_assurance"
    TEMPERATURE_MONITORING = "temperature_monitoring"
    COMPLIANCE_TRACKING = "compliance_tracking"
    OWNERSHIP_TRANSFER = "ownership_transfer"
    PAYMENT_ESCROW = "payment_escrow"

# Blockchain Network Configuration
class BlockchainNetwork(Base):
    __tablename__ = 'blockchain_networks'
    
    id = Column(Integer, primary_key=True, index=True)
    network_name = Column(String(255), nullable=False)
    network_type = Column(Enum(BlockchainType), nullable=False)
    network_url = Column(String(500), nullable=False)
    chain_id = Column(Integer)
    
    # Network configuration
    network_config = Column(JSON)  # Network-specific configuration
    gas_price = Column(Float)  # Gas price for transactions
    gas_limit = Column(Integer)  # Gas limit for transactions
    
    # Authentication
    private_key = Column(String(500))  # Encrypted private key
    public_key = Column(String(500))
    wallet_address = Column(String(100))
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    sync_status = Column(String(20), default='unknown')
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    creator = relationship("User")
    transactions = relationship("BlockchainTransaction", back_populates="network")
    smart_contracts = relationship("SmartContract", back_populates="network")

# Smart Contracts
class SmartContract(Base):
    __tablename__ = 'smart_contracts'
    
    id = Column(Integer, primary_key=True, index=True)
    contract_name = Column(String(255), nullable=False)
    contract_type = Column(Enum(SmartContractType), nullable=False)
    contract_address = Column(String(100), unique=True, nullable=False)
    network_id = Column(Integer, ForeignKey('blockchain_networks.id'), nullable=False)
    
    # Contract details
    contract_abi = Column(JSON)  # Contract ABI
    contract_bytecode = Column(Text)  # Contract bytecode
    contract_source = Column(Text)  # Contract source code
    
    # Contract configuration
    contract_config = Column(JSON)  # Contract-specific configuration
    deployment_params = Column(JSON)  # Deployment parameters
    
    # Status
    is_deployed = Column(Boolean, default=False)
    deployment_tx_hash = Column(String(100))
    deployment_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    network = relationship("BlockchainNetwork", back_populates="smart_contracts")
    creator = relationship("User")
    transactions = relationship("BlockchainTransaction", back_populates="contract")

# Blockchain Transactions
class BlockchainTransaction(Base):
    __tablename__ = 'blockchain_transactions'
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_hash = Column(String(100), unique=True, nullable=False, index=True)
    network_id = Column(Integer, ForeignKey('blockchain_networks.id'), nullable=False)
    contract_id = Column(Integer, ForeignKey('smart_contracts.id'))
    
    # Transaction details
    transaction_type = Column(Enum(TransactionType), nullable=False)
    from_address = Column(String(100))
    to_address = Column(String(100))
    value = Column(Float, default=0.0)
    gas_used = Column(Integer)
    gas_price = Column(Float)
    
    # Transaction data
    transaction_data = Column(JSON)  # Transaction-specific data
    metadata = Column(JSON)  # Additional metadata
    
    # Status and confirmation
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    block_number = Column(Integer)
    block_hash = Column(String(100))
    confirmation_count = Column(Integer, default=0)
    confirmed_at = Column(DateTime)
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    lot_id = Column(Integer, ForeignKey('item_lots.id'))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    network = relationship("BlockchainNetwork", back_populates="transactions")
    contract = relationship("SmartContract", back_populates="transactions")
    item = relationship("EnhancedItem")
    batch = relationship("ItemBatch")
    lot = relationship("ItemLot")

# Supply Chain Events (for blockchain recording)
class SupplyChainEvent(Base):
    __tablename__ = 'supply_chain_events'
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    event_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Event data
    event_data = Column(JSON, nullable=False)
    event_hash = Column(String(100), nullable=False, index=True)  # Hash of event data
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    lot_id = Column(Integer, ForeignKey('item_lots.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Blockchain integration
    blockchain_tx_id = Column(Integer, ForeignKey('blockchain_transactions.id'))
    is_recorded = Column(Boolean, default=False)
    recorded_at = Column(DateTime)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey('users.id'))
    verified_at = Column(DateTime)
    verification_hash = Column(String(100))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem")
    batch = relationship("ItemBatch")
    lot = relationship("ItemLot")
    user = relationship("User", foreign_keys=[user_id])
    blockchain_tx = relationship("BlockchainTransaction")
    verifier = relationship("User", foreign_keys=[verified_by])

# Blockchain Certificates
class BlockchainCertificate(Base):
    __tablename__ = 'blockchain_certificates'
    
    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(String(100), unique=True, nullable=False, index=True)
    certificate_type = Column(String(50), nullable=False)  # quality, compliance, origin, sustainability
    certificate_data = Column(JSON, nullable=False)
    certificate_hash = Column(String(100), nullable=False, index=True)
    
    # Certificate details
    issuer = Column(String(255), nullable=False)
    issuer_signature = Column(String(500))
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime)
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    lot_id = Column(Integer, ForeignKey('item_lots.id'))
    
    # Blockchain integration
    blockchain_tx_id = Column(Integer, ForeignKey('blockchain_transactions.id'))
    is_recorded = Column(Boolean, default=False)
    recorded_at = Column(DateTime)
    
    # Status
    is_valid = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime)
    revoked_by = Column(Integer, ForeignKey('users.id'))
    revocation_reason = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem")
    batch = relationship("ItemBatch")
    lot = relationship("ItemLot")
    blockchain_tx = relationship("BlockchainTransaction")
    creator = relationship("User", foreign_keys=[created_by])
    revoker = relationship("User", foreign_keys=[revoked_by])

# Supply Chain Traceability
class SupplyChainTrace(Base):
    __tablename__ = 'supply_chain_traces'
    
    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String(100), unique=True, nullable=False, index=True)
    item_id = Column(Integer, ForeignKey('enhanced_items.id'), nullable=False)
    
    # Trace data
    trace_data = Column(JSON, nullable=False)
    trace_hash = Column(String(100), nullable=False, index=True)
    
    # Trace path
    origin_location = Column(String(255))
    current_location = Column(String(255))
    destination_location = Column(String(255))
    
    # Participants
    participants = Column(JSON)  # List of participants in the supply chain
    current_owner = Column(String(255))
    previous_owners = Column(JSON)  # List of previous owners
    
    # Blockchain integration
    blockchain_tx_id = Column(Integer, ForeignKey('blockchain_transactions.id'))
    is_recorded = Column(Boolean, default=False)
    recorded_at = Column(DateTime)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey('users.id'))
    verified_at = Column(DateTime)
    verification_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem")
    blockchain_tx = relationship("BlockchainTransaction")
    verifier = relationship("User")

# Blockchain Compliance
class BlockchainCompliance(Base):
    __tablename__ = 'blockchain_compliance'
    
    id = Column(Integer, primary_key=True, index=True)
    compliance_id = Column(String(100), unique=True, nullable=False, index=True)
    compliance_type = Column(String(50), nullable=False)  # regulatory, industry, internal
    compliance_standard = Column(String(100), nullable=False)
    
    # Compliance data
    compliance_data = Column(JSON, nullable=False)
    compliance_hash = Column(String(100), nullable=False, index=True)
    
    # Related entities
    item_id = Column(Integer, ForeignKey('enhanced_items.id'))
    batch_id = Column(Integer, ForeignKey('item_batches.id'))
    lot_id = Column(Integer, ForeignKey('item_lots.id'))
    
    # Compliance status
    compliance_status = Column(String(20), default='pending')  # pending, compliant, non_compliant, under_review
    compliance_score = Column(Float)  # 0-100 compliance score
    compliance_notes = Column(Text)
    
    # Blockchain integration
    blockchain_tx_id = Column(Integer, ForeignKey('blockchain_transactions.id'))
    is_recorded = Column(Boolean, default=False)
    recorded_at = Column(DateTime)
    
    # Audit
    audited_by = Column(Integer, ForeignKey('users.id'))
    audited_at = Column(DateTime)
    audit_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    item = relationship("EnhancedItem")
    batch = relationship("ItemBatch")
    lot = relationship("ItemLot")
    blockchain_tx = relationship("BlockchainTransaction")
    auditor = relationship("User")

# Blockchain Analytics
class BlockchainAnalytics(Base):
    __tablename__ = 'blockchain_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    analytics_type = Column(String(50), nullable=False)  # transaction_volume, network_health, compliance_rate
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Analytics data
    analytics_data = Column(JSON, nullable=False)
    insights = Column(JSON)
    recommendations = Column(JSON)
    
    # Performance metrics
    transaction_count = Column(Integer, default=0)
    total_gas_used = Column(Integer, default=0)
    average_gas_price = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    calculated_by = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    calculator = relationship("User")

# Blockchain Integration Status
class BlockchainIntegrationStatus(Base):
    __tablename__ = 'blockchain_integration_status'
    
    id = Column(Integer, primary_key=True, index=True)
    integration_name = Column(String(255), nullable=False)
    network_id = Column(Integer, ForeignKey('blockchain_networks.id'), nullable=False)
    status = Column(String(20), nullable=False)  # active, inactive, error, maintenance
    
    # Integration details
    last_sync = Column(DateTime)
    sync_status = Column(String(20), default='unknown')
    last_transaction = Column(DateTime)
    transaction_count = Column(Integer, default=0)
    
    # Error handling
    last_error = Column(Text)
    error_count = Column(Integer, default=0)
    error_rate = Column(Float, default=0.0)
    
    # Performance metrics
    average_response_time = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    throughput = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Relationships
    network = relationship("BlockchainNetwork")

# Utility functions for blockchain operations
def calculate_hash(data):
    """Calculate SHA-256 hash of data"""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(str(data).encode()).hexdigest()

def verify_hash(data, hash_value):
    """Verify data against hash"""
    calculated_hash = calculate_hash(data)
    return calculated_hash == hash_value

def create_event_hash(event_data):
    """Create hash for supply chain event"""
    return calculate_hash({
        'event_type': event_data.get('event_type'),
        'event_timestamp': event_data.get('event_timestamp'),
        'event_data': event_data.get('event_data'),
        'item_id': event_data.get('item_id'),
        'batch_id': event_data.get('batch_id'),
        'lot_id': event_data.get('lot_id')
    })
