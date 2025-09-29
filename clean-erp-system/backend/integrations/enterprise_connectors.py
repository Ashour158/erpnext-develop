# Enterprise Connectors
# Advanced integration with major ERP systems (SAP, Oracle, Microsoft Dynamics, NetSuite)

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import uuid
import base64
import hashlib
import hmac
from urllib.parse import urlencode, parse_qs
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectorType(Enum):
    SAP = "sap"
    ORACLE = "oracle"
    MICROSOFT_DYNAMICS = "microsoft_dynamics"
    NETSUITE = "netsuite"

class SyncStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ConnectorConfig:
    connector_id: str
    connector_type: ConnectorType
    name: str
    base_url: str
    api_key: str
    secret_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    oauth_token: Optional[str] = None
    refresh_token: Optional[str] = None
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None

@dataclass
class SyncJob:
    job_id: str
    connector_id: str
    sync_type: str
    status: SyncStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_synced: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None
    sync_data: Dict[str, Any] = None

class SAPConnector:
    """
    SAP ERP Integration Connector
    Supports SAP ECC, S/4HANA, and SAP Business One
    """
    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup SAP authentication"""
        if self.config.username and self.config.password:
            # Basic authentication
            auth_string = f"{self.config.username}:{self.config.password}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            self.session.headers.update({
                'Authorization': f'Basic {encoded_auth}',
                'Content-Type': 'application/json'
            })
        elif self.config.oauth_token:
            # OAuth authentication
            self.session.headers.update({
                'Authorization': f'Bearer {self.config.oauth_token}',
                'Content-Type': 'application/json'
            })
    
    def get_customers(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch customers from SAP"""
        try:
            url = f"{self.base_url}/api/customers"
            params = {
                'limit': limit,
                'offset': offset,
                'format': 'json'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('customers', []),
                'total': data.get('total', 0),
                'connector': 'SAP'
            }
            
        except Exception as e:
            logger.error(f"SAP customer fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'SAP'
            }
    
    def get_products(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch products from SAP"""
        try:
            url = f"{self.base_url}/api/products"
            params = {
                'limit': limit,
                'offset': offset,
                'format': 'json'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('products', []),
                'total': data.get('total', 0),
                'connector': 'SAP'
            }
            
        except Exception as e:
            logger.error(f"SAP product fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'SAP'
            }
    
    def get_sales_orders(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch sales orders from SAP"""
        try:
            url = f"{self.base_url}/api/sales_orders"
            params = {
                'limit': limit,
                'offset': offset,
                'format': 'json'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('sales_orders', []),
                'total': data.get('total', 0),
                'connector': 'SAP'
            }
            
        except Exception as e:
            logger.error(f"SAP sales order fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'SAP'
            }
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create customer in SAP"""
        try:
            url = f"{self.base_url}/api/customers"
            
            response = self.session.post(url, json=customer_data)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data,
                'connector': 'SAP'
            }
            
        except Exception as e:
            logger.error(f"SAP customer creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'SAP'
            }

class OracleConnector:
    """
    Oracle ERP Integration Connector
    Supports Oracle EBS, Oracle Cloud ERP, and Oracle NetSuite
    """
    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup Oracle authentication"""
        if self.config.api_key:
            self.session.headers.update({
                'X-API-Key': self.config.api_key,
                'Content-Type': 'application/json'
            })
        elif self.config.oauth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.config.oauth_token}',
                'Content-Type': 'application/json'
            })
    
    def get_customers(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch customers from Oracle"""
        try:
            url = f"{self.base_url}/api/customers"
            params = {
                'limit': limit,
                'offset': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('customers', []),
                'total': data.get('total', 0),
                'connector': 'Oracle'
            }
            
        except Exception as e:
            logger.error(f"Oracle customer fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Oracle'
            }
    
    def get_products(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch products from Oracle"""
        try:
            url = f"{self.base_url}/api/products"
            params = {
                'limit': limit,
                'offset': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('products', []),
                'total': data.get('total', 0),
                'connector': 'Oracle'
            }
            
        except Exception as e:
            logger.error(f"Oracle product fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Oracle'
            }

class MicrosoftDynamicsConnector:
    """
    Microsoft Dynamics 365 Integration Connector
    Supports Dynamics 365 Finance, Sales, and Supply Chain Management
    """
    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup Microsoft Dynamics authentication"""
        if self.config.oauth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.config.oauth_token}',
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0'
            })
    
    def get_customers(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch customers from Microsoft Dynamics"""
        try:
            url = f"{self.base_url}/api/data/v9.0/accounts"
            params = {
                '$top': limit,
                '$skip': offset,
                '$select': 'accountid,name,emailaddress1,telephone1,address1_city,address1_stateorprovince'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('value', []),
                'total': len(data.get('value', [])),
                'connector': 'Microsoft Dynamics'
            }
            
        except Exception as e:
            logger.error(f"Microsoft Dynamics customer fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Microsoft Dynamics'
            }
    
    def get_products(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch products from Microsoft Dynamics"""
        try:
            url = f"{self.base_url}/api/data/v9.0/products"
            params = {
                '$top': limit,
                '$skip': offset,
                '$select': 'productid,name,productnumber,price,description'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('value', []),
                'total': len(data.get('value', [])),
                'connector': 'Microsoft Dynamics'
            }
            
        except Exception as e:
            logger.error(f"Microsoft Dynamics product fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Microsoft Dynamics'
            }

class NetSuiteConnector:
    """
    NetSuite ERP Integration Connector
    Supports NetSuite SuiteCloud Platform and RESTlets
    """
    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup NetSuite authentication"""
        if self.config.oauth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.config.oauth_token}',
                'Content-Type': 'application/json',
                'X-NetSuite-Application-Id': self.config.api_key
            })
    
    def get_customers(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch customers from NetSuite"""
        try:
            url = f"{self.base_url}/services/rest/record/v1/customer"
            params = {
                'limit': limit,
                'offset': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('items', []),
                'total': data.get('count', 0),
                'connector': 'NetSuite'
            }
            
        except Exception as e:
            logger.error(f"NetSuite customer fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'NetSuite'
            }
    
    def get_products(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch products from NetSuite"""
        try:
            url = f"{self.base_url}/services/rest/record/v1/inventoryitem"
            params = {
                'limit': limit,
                'offset': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('items', []),
                'total': data.get('count', 0),
                'connector': 'NetSuite'
            }
            
        except Exception as e:
            logger.error(f"NetSuite product fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'NetSuite'
            }

class EnterpriseConnectorManager:
    """
    Enterprise Connector Management System
    Manages integrations with major ERP systems
    """
    
    def __init__(self):
        self.connectors: Dict[str, Union[SAPConnector, OracleConnector, MicrosoftDynamicsConnector, NetSuiteConnector]] = {}
        self.sync_jobs: List[SyncJob] = []
    
    def create_connector(self, config: ConnectorConfig) -> bool:
        """Create a new enterprise connector"""
        try:
            if config.connector_type == ConnectorType.SAP:
                connector = SAPConnector(config)
            elif config.connector_type == ConnectorType.ORACLE:
                connector = OracleConnector(config)
            elif config.connector_type == ConnectorType.MICROSOFT_DYNAMICS:
                connector = MicrosoftDynamicsConnector(config)
            elif config.connector_type == ConnectorType.NETSUITE:
                connector = NetSuiteConnector(config)
            else:
                raise ValueError(f"Unsupported connector type: {config.connector_type}")
            
            self.connectors[config.connector_id] = connector
            logger.info(f"Created {config.connector_type.value} connector: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating connector: {str(e)}")
            return False
    
    def get_connector(self, connector_id: str) -> Optional[Union[SAPConnector, OracleConnector, MicrosoftDynamicsConnector, NetSuiteConnector]]:
        """Get a connector by ID"""
        return self.connectors.get(connector_id)
    
    def sync_data(self, connector_id: str, sync_type: str, data: Dict[str, Any]) -> SyncJob:
        """Sync data with enterprise system"""
        try:
            connector = self.get_connector(connector_id)
            if not connector:
                raise ValueError(f"Connector {connector_id} not found")
            
            job_id = str(uuid.uuid4())
            sync_job = SyncJob(
                job_id=job_id,
                connector_id=connector_id,
                sync_type=sync_type,
                status=SyncStatus.IN_PROGRESS,
                started_at=datetime.now(),
                sync_data=data
            )
            
            self.sync_jobs.append(sync_job)
            
            # Perform sync based on type
            if sync_type == 'customers':
                result = connector.get_customers()
            elif sync_type == 'products':
                result = connector.get_products()
            elif sync_type == 'sales_orders':
                result = connector.get_sales_orders()
            else:
                raise ValueError(f"Unsupported sync type: {sync_type}")
            
            # Update sync job
            if result.get('success'):
                sync_job.status = SyncStatus.COMPLETED
                sync_job.records_synced = len(result.get('data', []))
            else:
                sync_job.status = SyncStatus.FAILED
                sync_job.error_message = result.get('error', 'Unknown error')
                sync_job.records_failed = 1
            
            sync_job.completed_at = datetime.now()
            
            logger.info(f"Sync job {job_id} completed with status: {sync_job.status.value}")
            return sync_job
            
        except Exception as e:
            logger.error(f"Error syncing data: {str(e)}")
            sync_job.status = SyncStatus.FAILED
            sync_job.error_message = str(e)
            sync_job.completed_at = datetime.now()
            return sync_job
    
    def get_sync_status(self, job_id: str) -> Optional[SyncJob]:
        """Get sync job status"""
        for job in self.sync_jobs:
            if job.job_id == job_id:
                return job
        return None
    
    def get_connector_statistics(self) -> Dict[str, Any]:
        """Get connector statistics"""
        total_connectors = len(self.connectors)
        active_connectors = len([c for c in self.connectors.values() if hasattr(c, 'config') and c.config.is_active])
        total_sync_jobs = len(self.sync_jobs)
        successful_syncs = len([j for j in self.sync_jobs if j.status == SyncStatus.COMPLETED])
        failed_syncs = len([j for j in self.sync_jobs if j.status == SyncStatus.FAILED])
        
        return {
            'total_connectors': total_connectors,
            'active_connectors': active_connectors,
            'total_sync_jobs': total_sync_jobs,
            'successful_syncs': successful_syncs,
            'failed_syncs': failed_syncs,
            'success_rate': (successful_syncs / total_sync_jobs * 100) if total_sync_jobs > 0 else 0
        }

# Global Enterprise Connector Manager
enterprise_connector_manager = EnterpriseConnectorManager()
