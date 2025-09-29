# Supply Chain Transparency System
# Blockchain-based supply chain tracking and verification

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import hmac
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionType(Enum):
    PRODUCT_CREATION = "product_creation"
    PRODUCT_TRANSFER = "product_transfer"
    QUALITY_CHECK = "quality_check"
    CERTIFICATION = "certification"
    SHIPMENT = "shipment"
    DELIVERY = "delivery"

class VerificationStatus(Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class BlockchainTransaction:
    transaction_id: str
    transaction_type: TransactionType
    product_id: str
    from_entity: str
    to_entity: str
    timestamp: datetime
    data: Dict[str, Any]
    hash: str
    previous_hash: str
    nonce: int
    verified: bool = False
    verification_status: VerificationStatus = VerificationStatus.PENDING

@dataclass
class Product:
    product_id: str
    name: str
    description: str
    manufacturer: str
    batch_number: str
    serial_number: str
    created_at: datetime
    current_owner: str
    location: str
    status: str
    blockchain_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class SupplyChainTransparency:
    """
    Supply Chain Transparency System
    Blockchain-based supply chain tracking and verification
    """
    
    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.transactions: Dict[str, BlockchainTransaction] = {}
        self.verification_queue: List[str] = []
        
    def create_product(self, name: str, description: str, manufacturer: str,
                      batch_number: str, serial_number: str, location: str,
                      metadata: Dict[str, Any] = None) -> Product:
        """Create a new product in the blockchain"""
        try:
            product = Product(
                product_id=str(uuid.uuid4()),
                name=name,
                description=description,
                manufacturer=manufacturer,
                batch_number=batch_number,
                serial_number=serial_number,
                created_at=datetime.now(),
                current_owner=manufacturer,
                location=location,
                status="created",
                blockchain_hash="",
                metadata=metadata or {}
            )
            
            # Create initial transaction
            transaction = self._create_transaction(
                TransactionType.PRODUCT_CREATION,
                product.product_id,
                manufacturer,
                manufacturer,
                {
                    'product_name': name,
                    'description': description,
                    'batch_number': batch_number,
                    'serial_number': serial_number,
                    'location': location
                }
            )
            
            product.blockchain_hash = transaction.hash
            self.products[product.product_id] = product
            self.transactions[transaction.transaction_id] = transaction
            
            logger.info(f"Product created: {product.product_id}")
            return product
            
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise
    
    def transfer_product(self, product_id: str, from_entity: str, to_entity: str,
                        new_location: str, transfer_data: Dict[str, Any] = None) -> bool:
        """Transfer product ownership"""
        try:
            if product_id not in self.products:
                return False
            
            product = self.products[product_id]
            
            # Create transfer transaction
            transaction = self._create_transaction(
                TransactionType.PRODUCT_TRANSFER,
                product_id,
                from_entity,
                to_entity,
                {
                    'from_location': product.location,
                    'to_location': new_location,
                    'transfer_data': transfer_data or {}
                }
            )
            
            # Update product
            product.current_owner = to_entity
            product.location = new_location
            product.blockchain_hash = transaction.hash
            product.updated_at = datetime.now()
            
            self.transactions[transaction.transaction_id] = transaction
            
            logger.info(f"Product transferred: {product_id} from {from_entity} to {to_entity}")
            return True
            
        except Exception as e:
            logger.error(f"Error transferring product: {str(e)}")
            return False
    
    def add_quality_check(self, product_id: str, checker: str, quality_data: Dict[str, Any]) -> bool:
        """Add quality check to product"""
        try:
            if product_id not in self.products:
                return False
            
            product = self.products[product_id]
            
            # Create quality check transaction
            transaction = self._create_transaction(
                TransactionType.QUALITY_CHECK,
                product_id,
                checker,
                product.current_owner,
                quality_data
            )
            
            self.transactions[transaction.transaction_id] = transaction
            
            logger.info(f"Quality check added: {product_id} by {checker}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding quality check: {str(e)}")
            return False
    
    def add_certification(self, product_id: str, certifier: str, certification_data: Dict[str, Any]) -> bool:
        """Add certification to product"""
        try:
            if product_id not in self.products:
                return False
            
            product = self.products[product_id]
            
            # Create certification transaction
            transaction = self._create_transaction(
                TransactionType.CERTIFICATION,
                product_id,
                certifier,
                product.current_owner,
                certification_data
            )
            
            self.transactions[transaction.transaction_id] = transaction
            
            logger.info(f"Certification added: {product_id} by {certifier}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding certification: {str(e)}")
            return False
    
    def _create_transaction(self, transaction_type: TransactionType, product_id: str,
                           from_entity: str, to_entity: str, data: Dict[str, Any]) -> BlockchainTransaction:
        """Create a blockchain transaction"""
        try:
            transaction_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            # Get previous hash
            previous_hash = self._get_previous_hash(product_id)
            
            # Create transaction data
            transaction_data = {
                'transaction_id': transaction_id,
                'transaction_type': transaction_type.value,
                'product_id': product_id,
                'from_entity': from_entity,
                'to_entity': to_entity,
                'timestamp': timestamp.isoformat(),
                'data': data,
                'previous_hash': previous_hash
            }
            
            # Calculate hash
            transaction_hash = self._calculate_hash(transaction_data)
            
            # Create transaction
            transaction = BlockchainTransaction(
                transaction_id=transaction_id,
                transaction_type=transaction_type,
                product_id=product_id,
                from_entity=from_entity,
                to_entity=to_entity,
                timestamp=timestamp,
                data=data,
                hash=transaction_hash,
                previous_hash=previous_hash,
                nonce=0
            )
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error creating transaction: {str(e)}")
            raise
    
    def _get_previous_hash(self, product_id: str) -> str:
        """Get previous hash for product"""
        try:
            # Find the last transaction for this product
            product_transactions = [
                t for t in self.transactions.values()
                if t.product_id == product_id
            ]
            
            if not product_transactions:
                return "0"
            
            # Get the most recent transaction
            latest_transaction = max(product_transactions, key=lambda t: t.timestamp)
            return latest_transaction.hash
            
        except Exception as e:
            logger.error(f"Error getting previous hash: {str(e)}")
            return "0"
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash for transaction data"""
        try:
            # Convert data to JSON string
            data_string = json.dumps(data, sort_keys=True)
            
            # Calculate SHA-256 hash
            hash_object = hashlib.sha256(data_string.encode())
            return hash_object.hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating hash: {str(e)}")
            return ""
    
    def get_product_history(self, product_id: str) -> List[BlockchainTransaction]:
        """Get complete history of a product"""
        try:
            product_transactions = [
                t for t in self.transactions.values()
                if t.product_id == product_id
            ]
            
            # Sort by timestamp
            product_transactions.sort(key=lambda t: t.timestamp)
            
            return product_transactions
            
        except Exception as e:
            logger.error(f"Error getting product history: {str(e)}")
            return []
    
    def verify_product(self, product_id: str) -> bool:
        """Verify product authenticity"""
        try:
            if product_id not in self.products:
                return False
            
            product = self.products[product_id]
            history = self.get_product_history(product_id)
            
            # Verify blockchain integrity
            for i, transaction in enumerate(history):
                if i == 0:
                    # First transaction
                    if transaction.previous_hash != "0":
                        return False
                else:
                    # Check previous hash
                    if transaction.previous_hash != history[i-1].hash:
                        return False
                
                # Verify transaction hash
                transaction_data = {
                    'transaction_id': transaction.transaction_id,
                    'transaction_type': transaction.transaction_type.value,
                    'product_id': transaction.product_id,
                    'from_entity': transaction.from_entity,
                    'to_entity': transaction.to_entity,
                    'timestamp': transaction.timestamp.isoformat(),
                    'data': transaction.data,
                    'previous_hash': transaction.previous_hash
                }
                
                calculated_hash = self._calculate_hash(transaction_data)
                if calculated_hash != transaction.hash:
                    return False
            
            logger.info(f"Product verified: {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying product: {str(e)}")
            return False
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        return self.products.get(product_id)
    
    def get_transaction(self, transaction_id: str) -> Optional[BlockchainTransaction]:
        """Get transaction by ID"""
        return self.transactions.get(transaction_id)
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get supply chain analytics"""
        try:
            total_products = len(self.products)
            total_transactions = len(self.transactions)
            
            # Transaction type distribution
            transaction_types = {}
            for transaction in self.transactions.values():
                transaction_type = transaction.transaction_type.value
                transaction_types[transaction_type] = transaction_types.get(transaction_type, 0) + 1
            
            # Product status distribution
            product_statuses = {}
            for product in self.products.values():
                status = product.status
                product_statuses[status] = product_statuses.get(status, 0) + 1
            
            return {
                'total_products': total_products,
                'total_transactions': total_transactions,
                'transaction_types': transaction_types,
                'product_statuses': product_statuses
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}

# Global supply chain transparency instance
supply_chain_transparency = SupplyChainTransparency()
