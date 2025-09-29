# CRM Connectors
# Advanced integration with major CRM systems (Salesforce, HubSpot, Pipedrive, Zoho)

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

class CRMConnectorType(Enum):
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    PIPEDRIVE = "pipedrive"
    ZOHO = "zoho"

class SyncDirection(Enum):
    IMPORT = "import"
    EXPORT = "export"
    BIDIRECTIONAL = "bidirectional"

@dataclass
class CRMConnectorConfig:
    connector_id: str
    connector_type: CRMConnectorType
    name: str
    base_url: str
    api_key: str
    secret_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    is_active: bool = True
    sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None

@dataclass
class CRMSyncJob:
    job_id: str
    connector_id: str
    sync_type: str
    direction: SyncDirection
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_synced: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None
    sync_data: Dict[str, Any] = None

class SalesforceConnector:
    """
    Salesforce CRM Integration Connector
    Supports Salesforce API v52.0+ with OAuth 2.0 authentication
    """
    
    def __init__(self, config: CRMConnectorConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup Salesforce OAuth authentication"""
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
    
    def get_leads(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch leads from Salesforce"""
        try:
            url = f"{self.base_url}/services/data/v52.0/sobjects/Lead"
            params = {
                'limit': limit,
                'offset': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('records', []),
                'total': data.get('totalSize', 0),
                'connector': 'Salesforce'
            }
            
        except Exception as e:
            logger.error(f"Salesforce leads fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Salesforce'
            }
    
    def get_contacts(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch contacts from Salesforce"""
        try:
            url = f"{self.base_url}/services/data/v52.0/sobjects/Contact"
            params = {
                'limit': limit,
                'offset': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('records', []),
                'total': data.get('totalSize', 0),
                'connector': 'Salesforce'
            }
            
        except Exception as e:
            logger.error(f"Salesforce contacts fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Salesforce'
            }
    
    def get_opportunities(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch opportunities from Salesforce"""
        try:
            url = f"{self.base_url}/services/data/v52.0/sobjects/Opportunity"
            params = {
                'limit': limit,
                'offset': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('records', []),
                'total': data.get('totalSize', 0),
                'connector': 'Salesforce'
            }
            
        except Exception as e:
            logger.error(f"Salesforce opportunities fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Salesforce'
            }
    
    def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create lead in Salesforce"""
        try:
            url = f"{self.base_url}/services/data/v52.0/sobjects/Lead"
            
            response = self.session.post(url, json=lead_data)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data,
                'connector': 'Salesforce'
            }
            
        except Exception as e:
            logger.error(f"Salesforce lead creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Salesforce'
            }
    
    def update_opportunity(self, opportunity_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update opportunity in Salesforce"""
        try:
            url = f"{self.base_url}/services/data/v52.0/sobjects/Opportunity/{opportunity_id}"
            
            response = self.session.patch(url, json=update_data)
            response.raise_for_status()
            
            return {
                'success': True,
                'message': 'Opportunity updated successfully',
                'connector': 'Salesforce'
            }
            
        except Exception as e:
            logger.error(f"Salesforce opportunity update error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Salesforce'
            }

class HubSpotConnector:
    """
    HubSpot CRM Integration Connector
    Supports HubSpot API v3 with OAuth 2.0 authentication
    """
    
    def __init__(self, config: CRMConnectorConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup HubSpot OAuth authentication"""
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
    
    def get_contacts(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch contacts from HubSpot"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts"
            params = {
                'limit': limit,
                'after': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('results', []),
                'total': data.get('total', 0),
                'connector': 'HubSpot'
            }
            
        except Exception as e:
            logger.error(f"HubSpot contacts fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'HubSpot'
            }
    
    def get_deals(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch deals from HubSpot"""
        try:
            url = f"{self.base_url}/crm/v3/objects/deals"
            params = {
                'limit': limit,
                'after': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('results', []),
                'total': data.get('total', 0),
                'connector': 'HubSpot'
            }
            
        except Exception as e:
            logger.error(f"HubSpot deals fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'HubSpot'
            }
    
    def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in HubSpot"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts"
            
            response = self.session.post(url, json=contact_data)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data,
                'connector': 'HubSpot'
            }
            
        except Exception as e:
            logger.error(f"HubSpot contact creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'HubSpot'
            }

class PipedriveConnector:
    """
    Pipedrive CRM Integration Connector
    Supports Pipedrive API v1 with API token authentication
    """
    
    def __init__(self, config: CRMConnectorConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup Pipedrive API token authentication"""
        if self.config.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.config.api_key}',
                'Content-Type': 'application/json'
            })
    
    def get_persons(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch persons from Pipedrive"""
        try:
            url = f"{self.base_url}/v1/persons"
            params = {
                'limit': limit,
                'start': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('data', {}).get('items', []),
                'total': data.get('additional_data', {}).get('pagination', {}).get('total_count', 0),
                'connector': 'Pipedrive'
            }
            
        except Exception as e:
            logger.error(f"Pipedrive persons fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Pipedrive'
            }
    
    def get_deals(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch deals from Pipedrive"""
        try:
            url = f"{self.base_url}/v1/deals"
            params = {
                'limit': limit,
                'start': offset
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('data', {}).get('items', []),
                'total': data.get('additional_data', {}).get('pagination', {}).get('total_count', 0),
                'connector': 'Pipedrive'
            }
            
        except Exception as e:
            logger.error(f"Pipedrive deals fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Pipedrive'
            }
    
    def create_person(self, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create person in Pipedrive"""
        try:
            url = f"{self.base_url}/v1/persons"
            
            response = self.session.post(url, json=person_data)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data,
                'connector': 'Pipedrive'
            }
            
        except Exception as e:
            logger.error(f"Pipedrive person creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Pipedrive'
            }

class ZohoConnector:
    """
    Zoho CRM Integration Connector
    Supports Zoho CRM API v2 with OAuth 2.0 authentication
    """
    
    def __init__(self, config: CRMConnectorConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup Zoho OAuth authentication"""
        if self.config.access_token:
            self.session.headers.update({
                'Authorization': f'Zoho-oauthtoken {self.config.access_token}',
                'Content-Type': 'application/json'
            })
        elif self.config.api_key:
            self.session.headers.update({
                'Authorization': f'Zoho-oauthtoken {self.config.api_key}',
                'Content-Type': 'application/json'
            })
    
    def get_leads(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch leads from Zoho"""
        try:
            url = f"{self.base_url}/crm/v2/Leads"
            params = {
                'per_page': limit,
                'page': (offset // limit) + 1
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('data', []),
                'total': data.get('info', {}).get('count', 0),
                'connector': 'Zoho'
            }
            
        except Exception as e:
            logger.error(f"Zoho leads fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Zoho'
            }
    
    def get_contacts(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch contacts from Zoho"""
        try:
            url = f"{self.base_url}/crm/v2/Contacts"
            params = {
                'per_page': limit,
                'page': (offset // limit) + 1
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('data', []),
                'total': data.get('info', {}).get('count', 0),
                'connector': 'Zoho'
            }
            
        except Exception as e:
            logger.error(f"Zoho contacts fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Zoho'
            }
    
    def get_deals(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch deals from Zoho"""
        try:
            url = f"{self.base_url}/crm/v2/Deals"
            params = {
                'per_page': limit,
                'page': (offset // limit) + 1
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'data': data.get('data', []),
                'total': data.get('info', {}).get('count', 0),
                'connector': 'Zoho'
            }
            
        except Exception as e:
            logger.error(f"Zoho deals fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'connector': 'Zoho'
            }

class CRMConnectorManager:
    """
    CRM Connector Management System
    Manages integrations with major CRM systems
    """
    
    def __init__(self):
        self.connectors: Dict[str, Union[SalesforceConnector, HubSpotConnector, PipedriveConnector, ZohoConnector]] = {}
        self.sync_jobs: List[CRMSyncJob] = []
    
    def create_connector(self, config: CRMConnectorConfig) -> bool:
        """Create a new CRM connector"""
        try:
            if config.connector_type == CRMConnectorType.SALESFORCE:
                connector = SalesforceConnector(config)
            elif config.connector_type == CRMConnectorType.HUBSPOT:
                connector = HubSpotConnector(config)
            elif config.connector_type == CRMConnectorType.PIPEDRIVE:
                connector = PipedriveConnector(config)
            elif config.connector_type == CRMConnectorType.ZOHO:
                connector = ZohoConnector(config)
            else:
                raise ValueError(f"Unsupported CRM connector type: {config.connector_type}")
            
            self.connectors[config.connector_id] = connector
            logger.info(f"Created {config.connector_type.value} connector: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating CRM connector: {str(e)}")
            return False
    
    def get_connector(self, connector_id: str) -> Optional[Union[SalesforceConnector, HubSpotConnector, PipedriveConnector, ZohoConnector]]:
        """Get a CRM connector by ID"""
        return self.connectors.get(connector_id)
    
    def sync_crm_data(self, connector_id: str, sync_type: str, direction: SyncDirection, data: Dict[str, Any]) -> CRMSyncJob:
        """Sync data with CRM system"""
        try:
            connector = self.get_connector(connector_id)
            if not connector:
                raise ValueError(f"CRM Connector {connector_id} not found")
            
            job_id = str(uuid.uuid4())
            sync_job = CRMSyncJob(
                job_id=job_id,
                connector_id=connector_id,
                sync_type=sync_type,
                direction=direction,
                status='in_progress',
                started_at=datetime.now(),
                sync_data=data
            )
            
            self.sync_jobs.append(sync_job)
            
            # Perform sync based on type and direction
            if sync_type == 'leads':
                if direction in [SyncDirection.IMPORT, SyncDirection.BIDIRECTIONAL]:
                    result = connector.get_leads()
                else:
                    result = {'success': True, 'data': [], 'connector': connector.__class__.__name__}
            elif sync_type == 'contacts':
                if direction in [SyncDirection.IMPORT, SyncDirection.BIDIRECTIONAL]:
                    result = connector.get_contacts()
                else:
                    result = {'success': True, 'data': [], 'connector': connector.__class__.__name__}
            elif sync_type == 'deals':
                if direction in [SyncDirection.IMPORT, SyncDirection.BIDIRECTIONAL]:
                    result = connector.get_deals()
                else:
                    result = {'success': True, 'data': [], 'connector': connector.__class__.__name__}
            else:
                raise ValueError(f"Unsupported CRM sync type: {sync_type}")
            
            # Update sync job
            if result.get('success'):
                sync_job.status = 'completed'
                sync_job.records_synced = len(result.get('data', []))
            else:
                sync_job.status = 'failed'
                sync_job.error_message = result.get('error', 'Unknown error')
                sync_job.records_failed = 1
            
            sync_job.completed_at = datetime.now()
            
            logger.info(f"CRM sync job {job_id} completed with status: {sync_job.status}")
            return sync_job
            
        except Exception as e:
            logger.error(f"Error syncing CRM data: {str(e)}")
            sync_job.status = 'failed'
            sync_job.error_message = str(e)
            sync_job.completed_at = datetime.now()
            return sync_job
    
    def get_crm_sync_status(self, job_id: str) -> Optional[CRMSyncJob]:
        """Get CRM sync job status"""
        for job in self.sync_jobs:
            if job.job_id == job_id:
                return job
        return None
    
    def get_crm_connector_statistics(self) -> Dict[str, Any]:
        """Get CRM connector statistics"""
        total_connectors = len(self.connectors)
        active_connectors = len([c for c in self.connectors.values() if hasattr(c, 'config') and c.config.is_active])
        total_sync_jobs = len(self.sync_jobs)
        successful_syncs = len([j for j in self.sync_jobs if j.status == 'completed'])
        failed_syncs = len([j for j in self.sync_jobs if j.status == 'failed'])
        
        return {
            'total_connectors': total_connectors,
            'active_connectors': active_connectors,
            'total_sync_jobs': total_sync_jobs,
            'successful_syncs': successful_syncs,
            'failed_syncs': failed_syncs,
            'success_rate': (successful_syncs / total_sync_jobs * 100) if total_sync_jobs > 0 else 0
        }

# Global CRM Connector Manager
crm_connector_manager = CRMConnectorManager()
