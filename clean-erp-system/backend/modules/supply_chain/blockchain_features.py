# Blockchain Features for Supply Chain Module
# Blockchain transparency and smart contracts integrated into Supply Chain

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
    SUPPLIER_VERIFICATION = "supplier_verification"
    WAREHOUSE_ENTRY = "warehouse_entry"
    WAREHOUSE_EXIT = "warehouse_exit"

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
    warehouse_id: Optional[str] = None
    status: str = "created"
    blockchain_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

class SupplyChainTransparency:
    """
    Supply Chain Transparency for Supply Chain Module
    Blockchain-based supply chain tracking and verification
    """
    
    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.transactions: Dict[str, BlockchainTransaction] = {}
        self.verification_queue: List[str] = []
        
    def create_product(self, name: str, description: str, manufacturer: str,
                      batch_number: str, serial_number: str, location: str,
                      warehouse_id: str = None, metadata: Dict[str, Any] = None) -> Product:
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
                warehouse_id=warehouse_id,
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
                    'location': location,
                    'warehouse_id': warehouse_id
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
                        new_location: str, warehouse_id: str = None, transfer_data: Dict[str, Any] = None) -> bool:
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
                    'warehouse_id': warehouse_id,
                    'transfer_data': transfer_data or {}
                }
            )
            
            # Update product
            product.current_owner = to_entity
            product.location = new_location
            product.warehouse_id = warehouse_id
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

class SmartContracts:
    """
    Smart Contracts for Supply Chain
    Automated contract execution
    """
    
    def __init__(self):
        self.contracts: Dict[str, Dict[str, Any]] = {}
        self.executions: Dict[str, Dict[str, Any]] = {}
    
    def create_contract(self, name: str, contract_type: str, conditions: List[Dict[str, Any]],
                       actions: List[Dict[str, Any]], parties: List[str]) -> str:
        """Create a smart contract"""
        try:
            contract_id = str(uuid.uuid4())
            
            contract = {
                'contract_id': contract_id,
                'name': name,
                'contract_type': contract_type,
                'conditions': conditions,
                'actions': actions,
                'parties': parties,
                'status': 'active',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            self.contracts[contract_id] = contract
            
            logger.info(f"Smart contract created: {contract_id}")
            return contract_id
            
        except Exception as e:
            logger.error(f"Error creating smart contract: {str(e)}")
            return ""
    
    def execute_contract(self, contract_id: str, trigger_data: Dict[str, Any]) -> bool:
        """Execute smart contract"""
        try:
            if contract_id not in self.contracts:
                return False
            
            contract = self.contracts[contract_id]
            
            # Check conditions
            if not self._check_conditions(contract['conditions'], trigger_data):
                return False
            
            # Execute actions
            execution_id = str(uuid.uuid4())
            execution = {
                'execution_id': execution_id,
                'contract_id': contract_id,
                'trigger_data': trigger_data,
                'status': 'executed',
                'executed_at': datetime.now()
            }
            
            self.executions[execution_id] = execution
            
            logger.info(f"Smart contract executed: {contract_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error executing smart contract: {str(e)}")
            return False
    
    def _check_conditions(self, conditions: List[Dict[str, Any]], trigger_data: Dict[str, Any]) -> bool:
        """Check contract conditions"""
        try:
            for condition in conditions:
                field = condition.get('field')
                operator = condition.get('operator')
                value = condition.get('value')
                
                if not all([field, operator]):
                    continue
                
                trigger_value = trigger_data.get(field)
                
                if not self._evaluate_condition(trigger_value, operator, value):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking conditions: {str(e)}")
            return False
    
    def _evaluate_condition(self, trigger_value: Any, operator: str, value: Any) -> bool:
        """Evaluate a single condition"""
        try:
            if operator == 'equals':
                return trigger_value == value
            elif operator == 'not_equals':
                return trigger_value != value
            elif operator == 'greater_than':
                return isinstance(trigger_value, (int, float)) and trigger_value > value
            elif operator == 'less_than':
                return isinstance(trigger_value, (int, float)) and trigger_value < value
            elif operator == 'contains':
                return isinstance(trigger_value, str) and value in trigger_value
            else:
                return True
                
        except Exception as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            return False

class AuditTrails:
    """
    Audit Trails for Supply Chain
    Immutable audit logging
    """
    
    def __init__(self):
        self.audit_logs: List[Dict[str, Any]] = []
    
    def log_audit_event(self, event_type: str, entity_type: str, entity_id: str,
                        user_id: str, action: str, details: Dict[str, Any] = None) -> str:
        """Log audit event"""
        try:
            log_id = str(uuid.uuid4())
            
            audit_log = {
                'log_id': log_id,
                'event_type': event_type,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'user_id': user_id,
                'action': action,
                'details': details or {},
                'timestamp': datetime.now(),
                'ip_address': '127.0.0.1',  # Would get from request
                'user_agent': 'ERP System'  # Would get from request
            }
            
            self.audit_logs.append(audit_log)
            
            logger.info(f"Audit event logged: {log_id}")
            return log_id
            
        except Exception as e:
            logger.error(f"Error logging audit event: {str(e)}")
            return ""
    
    def get_audit_logs(self, entity_type: str = None, entity_id: str = None,
                      user_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs"""
        try:
            logs = self.audit_logs.copy()
            
            # Filter by entity type
            if entity_type:
                logs = [log for log in logs if log['entity_type'] == entity_type]
            
            # Filter by entity ID
            if entity_id:
                logs = [log for log in logs if log['entity_id'] == entity_id]
            
            # Filter by user ID
            if user_id:
                logs = [log for log in logs if log['user_id'] == user_id]
            
            # Sort by timestamp (newest first)
            logs.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Limit results
            return logs[:limit]
            
        except Exception as e:
            logger.error(f"Error getting audit logs: {str(e)}")
            return []
    
    def get_audit_summary(self, entity_type: str = None, entity_id: str = None) -> Dict[str, Any]:
        """Get audit summary"""
        try:
            logs = self.get_audit_logs(entity_type, entity_id, limit=1000)
            
            if not logs:
                return {'total_events': 0, 'events_by_type': {}, 'events_by_user': {}}
            
            # Count events by type
            events_by_type = {}
            for log in logs:
                event_type = log['event_type']
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
            
            # Count events by user
            events_by_user = {}
            for log in logs:
                user_id = log['user_id']
                events_by_user[user_id] = events_by_user.get(user_id, 0) + 1
            
            return {
                'total_events': len(logs),
                'events_by_type': events_by_type,
                'events_by_user': events_by_user,
                'first_event': logs[-1]['timestamp'].isoformat(),
                'last_event': logs[0]['timestamp'].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting audit summary: {str(e)}")
            return {}

# Global blockchain features instances
supply_chain_transparency = SupplyChainTransparency()
smart_contracts = SmartContracts()
audit_trails = AuditTrails()
