# E-commerce Connectors
# Advanced integration with major e-commerce platforms (Shopify, WooCommerce, Magento, Amazon)

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EcommerceConnectorType(Enum):
    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"
    MAGENTO = "magento"
    AMAZON = "amazon"

class SyncStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class EcommerceConnectorConfig:
    connector_id: str
    connector_type: EcommerceConnectorType
    name: str
    base_url: str
    api_key: str
    secret_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None

@dataclass
class EcommerceSyncJob:
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

class ShopifyConnector:
    """
    Shopify E-commerce Integration Connector
    Supports Shopify Admin API v2023-10 with OAuth 2.0 authentication
    """
    
    def __init__(self, config: EcommerceConnectorConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup Shopify OAuth authentication"""
        if self.config.access_token:
            self.session.headers.update({
                'X-Shopify-Access-Token': self.config.access_token,
                'Content-Type': 'application/json'
            })
        elif self.config.api_key:
            self.session.headers.update({
                'X-Shopify-Access-Token': self.config.api_key,
                'Content-Type': 'application/json'
            })
    
    def get_products(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch products from Shopify"""
        try:
            url = f"{self.base_url}/admin/api/2023-10/products.json"
            params = {
                'limit': limit,
                'page_info': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('products', []),
                'total': len(data.get('products', [])),
                'connector': 'Shopify'
            }
            
        except Exception as e:
            logger.error(f"Shopify products fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Shopify'
            }
    
    def get_orders(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch orders from Shopify"""
        try:
            url = f"{self.base_url}/admin/api/2023-10/orders.json"
            params = {
                'limit': limit,
                'page_info': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('orders', []),
                'total': len(data.get('orders', [])),
                'connector': 'Shopify'
            }
            
        except Exception as e:
            logger.error(f"Shopify orders fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Shopify'
            }
    
    def get_customers(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch customers from Shopify"""
        try:
            url = f"{self.base_url}/admin/api/2023-10/customers.json"
            params = {
                'limit': limit,
                'page_info': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('customers', []),
                'total': len(data.get('customers', [])),
                'connector': 'Shopify'
            }
            
        except Exception as e:
            logger.error(f"Shopify customers fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Shopify'
            }
    
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create product in Shopify"""
        try:
            url = f"{self.base_url}/admin/api/2023-10/products.json"
            
            response = self.session.post(url, json=product_data)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data,
                'connector': 'Shopify'
            }
            
        except Exception as e:
            logger.error(f"Shopify product creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Shopify'
            }
    
    def update_inventory(self, inventory_item_id: str, quantity: int) -> Dict[str, Any]:
        """Update inventory in Shopify"""
        try:
            url = f"{self.base_url}/admin/api/2023-10/inventory_levels/set.json"
            
            payload = {
                'location_id': self.config.metadata.get('location_id'),
                'inventory_item_id': inventory_item_id,
                'available': quantity
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data,
                'connector': 'Shopify'
            }
            
        except Exception as e:
            logger.error(f"Shopify inventory update error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Shopify'
            }

class WooCommerceConnector:
    """
    WooCommerce E-commerce Integration Connector
    Supports WooCommerce REST API v3 with API key authentication
    """
    
    def __init__(self, config: EcommerceConnectorConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup WooCommerce API authentication"""
        if self.config.api_key and self.config.secret_key:
            auth_string = f"{self.config.api_key}:{self.config.secret_key}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            self.session.headers.update({
                'Authorization': f'Basic {encoded_auth}',
                'Content-Type': 'application/json'
            })
    
    def get_products(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch products from WooCommerce"""
        try:
            url = f"{self.base_url}/wp-json/wc/v3/products"
            params = {
                'per_page': limit,
                'page': (offset // limit) + 1
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data,
                'total': len(data),
                'connector': 'WooCommerce'
            }
            
        except Exception as e:
            logger.error(f"WooCommerce products fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'WooCommerce'
            }
    
    def get_orders(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch orders from WooCommerce"""
        try:
            url = f"{self.base_url}/wp-json/wc/v3/orders"
            params = {
                'per_page': limit,
                'page': (offset // limit) + 1
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data,
                'total': len(data),
                'connector': 'WooCommerce'
            }
            
        except Exception as e:
            logger.error(f"WooCommerce orders fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'WooCommerce'
            }
    
    def get_customers(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch customers from WooCommerce"""
        try:
            url = f"{self.base_url}/wp-json/wc/v3/customers"
            params = {
                'per_page': limit,
                'page': (offset // limit) + 1
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data,
                'total': len(data),
                'connector': 'WooCommerce'
            }
            
        except Exception as e:
            logger.error(f"WooCommerce customers fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'WooCommerce'
            }
    
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create product in WooCommerce"""
        try:
            url = f"{self.base_url}/wp-json/wc/v3/products"
            
            response = self.session.post(url, json=product_data)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data,
                'connector': 'WooCommerce'
            }
            
        except Exception as e:
            logger.error(f"WooCommerce product creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'WooCommerce'
            }

class MagentoConnector:
    """
    Magento E-commerce Integration Connector
    Supports Magento 2 REST API with OAuth 2.0 authentication
    """
    
    def __init__(self, config: EcommerceConnectorConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup Magento OAuth authentication"""
        if self.config.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.config.access_token}',
                'Content-Type': 'application/json'
            })
        elif self.config.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.config.api_key}',
                'Content-Type': 'application/json'
            })
    
    def get_products(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch products from Magento"""
        try:
            url = f"{self.base_url}/rest/V1/products"
            params = {
                'searchCriteria[pageSize]': limit,
                'searchCriteria[currentPage]': (offset // limit) + 1
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('items', []),
                'total': data.get('total_count', 0),
                'connector': 'Magento'
            }
            
        except Exception as e:
            logger.error(f"Magento products fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Magento'
            }
    
    def get_orders(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch orders from Magento"""
        try:
            url = f"{self.base_url}/rest/V1/orders"
            params = {
                'searchCriteria[pageSize]': limit,
                'searchCriteria[currentPage]': (offset // limit) + 1
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('items', []),
                'total': data.get('total_count', 0),
                'connector': 'Magento'
            }
            
        except Exception as e:
            logger.error(f"Magento orders fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Magento'
            }
    
    def get_customers(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch customers from Magento"""
        try:
            url = f"{self.base_url}/rest/V1/customers"
            params = {
                'searchCriteria[pageSize]': limit,
                'searchCriteria[currentPage]': (offset // limit) + 1
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('items', []),
                'total': data.get('total_count', 0),
                'connector': 'Magento'
            }
            
        except Exception as e:
            logger.error(f"Magento customers fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Magento'
            }

class AmazonConnector:
    """
    Amazon Marketplace Integration Connector
    Supports Amazon Selling Partner API with AWS authentication
    """
    
    def __init__(self, config: EcommerceConnectorConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup Amazon AWS authentication"""
        if self.config.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.config.access_token}',
                'Content-Type': 'application/json',
                'x-amz-access-token': self.config.access_token
            })
        elif self.config.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.config.api_key}',
                'Content-Type': 'application/json',
                'x-amz-access-token': self.config.api_key
            })
    
    def get_products(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch products from Amazon"""
        try:
            url = f"{self.base_url}/catalog/2022-04-01/items"
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
                'total': data.get('pagination', {}).get('total', 0),
                'connector': 'Amazon'
            }
            
        except Exception as e:
            logger.error(f"Amazon products fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Amazon'
            }
    
    def get_orders(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch orders from Amazon"""
        try:
            url = f"{self.base_url}/orders/v0/orders"
            params = {
                'MaxResultsPerPage': limit,
                'NextToken': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('payload', {}).get('Orders', []),
                'total': len(data.get('payload', {}).get('Orders', [])),
                'connector': 'Amazon'
            }
            
        except Exception as e:
            logger.error(f"Amazon orders fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Amazon'
            }
    
    def update_inventory(self, sku: str, quantity: int) -> Dict[str, Any]:
        """Update inventory in Amazon"""
        try:
            url = f"{self.base_url}/feeds/2021-06-30/documents"
            
            # Create inventory feed document
            feed_data = {
                'contentType': 'text/xml',
                'content': f'<?xml version="1.0" encoding="UTF-8"?><Inventory><SKU>{sku}</SKU><Quantity>{quantity}</Quantity></Inventory>'
            }
            
            response = self.session.post(url, json=feed_data)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data,
                'connector': 'Amazon'
            }
            
        except Exception as e:
            logger.error(f"Amazon inventory update error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Amazon'
            }

class EcommerceConnectorManager:
    """
    E-commerce Connector Management System
    Manages integrations with major e-commerce platforms
    """
    
    def __init__(self):
        self.connectors: Dict[str, Union[ShopifyConnector, WooCommerceConnector, MagentoConnector, AmazonConnector]] = {}
        self.sync_jobs: List[EcommerceSyncJob] = []
    
    def create_connector(self, config: EcommerceConnectorConfig) -> bool:
        """Create a new e-commerce connector"""
        try:
            if config.connector_type == EcommerceConnectorType.SHOPIFY:
                connector = ShopifyConnector(config)
            elif config.connector_type == EcommerceConnectorType.WOOCOMMERCE:
                connector = WooCommerceConnector(config)
            elif config.connector_type == EcommerceConnectorType.MAGENTO:
                connector = MagentoConnector(config)
            elif config.connector_type == EcommerceConnectorType.AMAZON:
                connector = AmazonConnector(config)
            else:
                raise ValueError(f"Unsupported e-commerce connector type: {config.connector_type}")
            
            self.connectors[config.connector_id] = connector
            logger.info(f"Created {config.connector_type.value} connector: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating e-commerce connector: {str(e)}")
            return False
    
    def get_connector(self, connector_id: str) -> Optional[Union[ShopifyConnector, WooCommerceConnector, MagentoConnector, AmazonConnector]]:
        """Get an e-commerce connector by ID"""
        return self.connectors.get(connector_id)
    
    def sync_ecommerce_data(self, connector_id: str, sync_type: str, data: Dict[str, Any]) -> EcommerceSyncJob:
        """Sync data with e-commerce platform"""
        try:
            connector = self.get_connector(connector_id)
            if not connector:
                raise ValueError(f"E-commerce Connector {connector_id} not found")
            
            job_id = str(uuid.uuid4())
            sync_job = EcommerceSyncJob(
                job_id=job_id,
                connector_id=connector_id,
                sync_type=sync_type,
                status=SyncStatus.IN_PROGRESS,
                started_at=datetime.now(),
                sync_data=data
            )
            
            self.sync_jobs.append(sync_job)
            
            # Perform sync based on type
            if sync_type == 'products':
                result = connector.get_products()
            elif sync_type == 'orders':
                result = connector.get_orders()
            elif sync_type == 'customers':
                result = connector.get_customers()
            else:
                raise ValueError(f"Unsupported e-commerce sync type: {sync_type}")
            
            # Update sync job
            if result.get('success'):
                sync_job.status = SyncStatus.COMPLETED
                sync_job.records_synced = len(result.get('data', []))
            else:
                sync_job.status = SyncStatus.FAILED
                sync_job.error_message = result.get('error', 'Unknown error')
                sync_job.records_failed = 1
            
            sync_job.completed_at = datetime.now()
            
            logger.info(f"E-commerce sync job {job_id} completed with status: {sync_job.status.value}")
            return sync_job
            
        except Exception as e:
            logger.error(f"Error syncing e-commerce data: {str(e)}")
            sync_job.status = SyncStatus.FAILED
            sync_job.error_message = str(e)
            sync_job.completed_at = datetime.now()
            return sync_job
    
    def get_ecommerce_sync_status(self, job_id: str) -> Optional[EcommerceSyncJob]:
        """Get e-commerce sync job status"""
        for job in self.sync_jobs:
            if job.job_id == job_id:
                return job
        return None
    
    def get_ecommerce_connector_statistics(self) -> Dict[str, Any]:
        """Get e-commerce connector statistics"""
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

# Global E-commerce Connector Manager
ecommerce_connector_manager = EcommerceConnectorManager()
