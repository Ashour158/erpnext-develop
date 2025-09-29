# API Marketplace and Developer Platform
# Comprehensive API management, marketplace, and developer tools

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
import jwt
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APITier(Enum):
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class APIStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"

class WebhookEvent(Enum):
    DATA_CREATED = "data_created"
    DATA_UPDATED = "data_updated"
    DATA_DELETED = "data_deleted"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    ORDER_CREATED = "order_created"
    ORDER_UPDATED = "order_updated"
    PAYMENT_PROCESSED = "payment_processed"

@dataclass
class APIClient:
    client_id: str
    client_name: str
    client_secret: str
    api_key: str
    tier: APITier
    status: APIStatus
    rate_limit: int
    rate_limit_window: int  # seconds
    created_at: datetime
    updated_at: datetime
    created_by: str
    webhook_url: Optional[str] = None
    allowed_ips: List[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class APIEndpoint:
    endpoint_id: str
    name: str
    path: str
    method: str
    description: str
    parameters: List[Dict[str, Any]]
    response_schema: Dict[str, Any]
    rate_limit: int
    authentication_required: bool
    is_public: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class WebhookSubscription:
    subscription_id: str
    client_id: str
    event_type: WebhookEvent
    webhook_url: str
    secret_key: str
    is_active: bool
    created_at: datetime
    last_triggered: Optional[datetime] = None
    failure_count: int = 0
    metadata: Dict[str, Any] = None

@dataclass
class APIAnalytics:
    client_id: str
    endpoint: str
    method: str
    request_count: int
    success_count: int
    error_count: int
    average_response_time: float
    total_bandwidth: int
    date: datetime

class APIMarketplace:
    """
    API Marketplace and Developer Platform
    Comprehensive API management, marketplace, and developer tools
    """
    
    def __init__(self):
        self.api_clients: Dict[str, APIClient] = {}
        self.api_endpoints: Dict[str, APIEndpoint] = {}
        self.webhook_subscriptions: Dict[str, WebhookSubscription] = {}
        self.api_analytics: List[APIAnalytics] = []
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def create_api_client(self, 
                         client_name: str,
                         tier: APITier,
                         created_by: str,
                         webhook_url: Optional[str] = None,
                         allowed_ips: Optional[List[str]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> APIClient:
        """Create a new API client"""
        try:
            client_id = str(uuid.uuid4())
            client_secret = self._generate_secret()
            api_key = self._generate_api_key()
            
            # Set rate limits based on tier
            rate_limits = {
                APITier.FREE: 1000,
                APITier.BASIC: 10000,
                APITier.PROFESSIONAL: 100000,
                APITier.ENTERPRISE: 1000000
            }
            
            client = APIClient(
                client_id=client_id,
                client_name=client_name,
                client_secret=client_secret,
                api_key=api_key,
                tier=tier,
                status=APIStatus.ACTIVE,
                rate_limit=rate_limits[tier],
                rate_limit_window=3600,  # 1 hour
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=created_by,
                webhook_url=webhook_url,
                allowed_ips=allowed_ips or [],
                metadata=metadata or {}
            )
            
            self.api_clients[client_id] = client
            logger.info(f"Created API client: {client_name} (Tier: {tier.value})")
            return client
            
        except Exception as e:
            logger.error(f"Error creating API client: {str(e)}")
            raise
    
    def get_api_client(self, client_id: str) -> Optional[APIClient]:
        """Get API client by ID"""
        return self.api_clients.get(client_id)
    
    def get_api_client_by_key(self, api_key: str) -> Optional[APIClient]:
        """Get API client by API key"""
        for client in self.api_clients.values():
            if client.api_key == api_key:
                return client
        return None
    
    def update_api_client(self, client_id: str, updates: Dict[str, Any]) -> bool:
        """Update API client"""
        try:
            if client_id not in self.api_clients:
                raise ValueError(f"API client {client_id} not found")
            
            client = self.api_clients[client_id]
            
            # Update allowed fields
            allowed_fields = ['client_name', 'tier', 'status', 'rate_limit', 'webhook_url', 'allowed_ips', 'metadata']
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(client, field, value)
            
            client.updated_at = datetime.now()
            self.api_clients[client_id] = client
            
            logger.info(f"Updated API client: {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating API client: {str(e)}")
            return False
    
    def delete_api_client(self, client_id: str) -> bool:
        """Delete API client"""
        try:
            if client_id not in self.api_clients:
                raise ValueError(f"API client {client_id} not found")
            
            del self.api_clients[client_id]
            
            # Remove associated webhook subscriptions
            subscriptions_to_remove = [
                sub_id for sub_id, sub in self.webhook_subscriptions.items()
                if sub.client_id == client_id
            ]
            for sub_id in subscriptions_to_remove:
                del self.webhook_subscriptions[sub_id]
            
            logger.info(f"Deleted API client: {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting API client: {str(e)}")
            return False
    
    def create_api_endpoint(self,
                           name: str,
                           path: str,
                           method: str,
                           description: str,
                           parameters: List[Dict[str, Any]],
                           response_schema: Dict[str, Any],
                           rate_limit: int = 1000,
                           authentication_required: bool = True,
                           is_public: bool = False) -> APIEndpoint:
        """Create a new API endpoint"""
        try:
            endpoint_id = str(uuid.uuid4())
            
            endpoint = APIEndpoint(
                endpoint_id=endpoint_id,
                name=name,
                path=path,
                method=method,
                description=description,
                parameters=parameters,
                response_schema=response_schema,
                rate_limit=rate_limit,
                authentication_required=authentication_required,
                is_public=is_public,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.api_endpoints[endpoint_id] = endpoint
            logger.info(f"Created API endpoint: {name} ({method} {path})")
            return endpoint
            
        except Exception as e:
            logger.error(f"Error creating API endpoint: {str(e)}")
            raise
    
    def get_api_endpoints(self, is_public: Optional[bool] = None) -> List[APIEndpoint]:
        """Get API endpoints"""
        endpoints = list(self.api_endpoints.values())
        
        if is_public is not None:
            endpoints = [ep for ep in endpoints if ep.is_public == is_public]
        
        return endpoints
    
    def create_webhook_subscription(self,
                                  client_id: str,
                                  event_type: WebhookEvent,
                                  webhook_url: str,
                                  secret_key: Optional[str] = None) -> WebhookSubscription:
        """Create a webhook subscription"""
        try:
            if client_id not in self.api_clients:
                raise ValueError(f"API client {client_id} not found")
            
            subscription_id = str(uuid.uuid4())
            secret_key = secret_key or self._generate_secret()
            
            subscription = WebhookSubscription(
                subscription_id=subscription_id,
                client_id=client_id,
                event_type=event_type,
                webhook_url=webhook_url,
                secret_key=secret_key,
                is_active=True,
                created_at=datetime.now(),
                metadata={}
            )
            
            self.webhook_subscriptions[subscription_id] = subscription
            logger.info(f"Created webhook subscription: {event_type.value} for client {client_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error creating webhook subscription: {str(e)}")
            raise
    
    def trigger_webhook(self, event_type: WebhookEvent, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Trigger webhooks for an event"""
        results = []
        
        try:
            # Find all active subscriptions for this event
            subscriptions = [
                sub for sub in self.webhook_subscriptions.values()
                if sub.event_type == event_type and sub.is_active
            ]
            
            for subscription in subscriptions:
                try:
                    # Prepare webhook payload
                    payload = {
                        'event_type': event_type.value,
                        'timestamp': datetime.now().isoformat(),
                        'data': data,
                        'subscription_id': subscription.subscription_id
                    }
                    
                    # Create signature
                    signature = self._create_webhook_signature(payload, subscription.secret_key)
                    
                    # Send webhook
                    headers = {
                        'Content-Type': 'application/json',
                        'X-Webhook-Signature': signature,
                        'X-Webhook-Event': event_type.value
                    }
                    
                    response = requests.post(
                        subscription.webhook_url,
                        json=payload,
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        subscription.last_triggered = datetime.now()
                        subscription.failure_count = 0
                        results.append({
                            'subscription_id': subscription.subscription_id,
                            'status': 'success',
                            'response_code': response.status_code
                        })
                    else:
                        subscription.failure_count += 1
                        results.append({
                            'subscription_id': subscription.subscription_id,
                            'status': 'failed',
                            'response_code': response.status_code,
                            'error': response.text
                        })
                        
                except Exception as e:
                    subscription.failure_count += 1
                    results.append({
                        'subscription_id': subscription.subscription_id,
                        'status': 'error',
                        'error': str(e)
                    })
            
            logger.info(f"Triggered {len(subscriptions)} webhooks for event: {event_type.value}")
            return results
            
        except Exception as e:
            logger.error(f"Error triggering webhooks: {str(e)}")
            return []
    
    def validate_api_request(self, api_key: str, endpoint: str, method: str, ip_address: str) -> Dict[str, Any]:
        """Validate API request"""
        try:
            # Get client by API key
            client = self.get_api_client_by_key(api_key)
            if not client:
                return {
                    'valid': False,
                    'error': 'Invalid API key',
                    'status_code': 401
                }
            
            # Check if client is active
            if client.status != APIStatus.ACTIVE:
                return {
                    'valid': False,
                    'error': 'API client is not active',
                    'status_code': 403
                }
            
            # Check IP restrictions
            if client.allowed_ips and ip_address not in client.allowed_ips:
                return {
                    'valid': False,
                    'error': 'IP address not allowed',
                    'status_code': 403
                }
            
            # Check rate limits (simplified)
            # In a real implementation, this would use Redis or similar for distributed rate limiting
            
            return {
                'valid': True,
                'client_id': client.client_id,
                'tier': client.tier.value,
                'rate_limit': client.rate_limit
            }
            
        except Exception as e:
            logger.error(f"Error validating API request: {str(e)}")
            return {
                'valid': False,
                'error': 'Validation error',
                'status_code': 500
            }
    
    def record_api_analytics(self, client_id: str, endpoint: str, method: str, 
                           response_time: float, success: bool, bandwidth: int) -> None:
        """Record API analytics"""
        try:
            analytics = APIAnalytics(
                client_id=client_id,
                endpoint=endpoint,
                method=method,
                request_count=1,
                success_count=1 if success else 0,
                error_count=0 if success else 1,
                average_response_time=response_time,
                total_bandwidth=bandwidth,
                date=datetime.now()
            )
            
            self.api_analytics.append(analytics)
            
        except Exception as e:
            logger.error(f"Error recording API analytics: {str(e)}")
    
    def get_api_analytics(self, client_id: Optional[str] = None, 
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List[APIAnalytics]:
        """Get API analytics"""
        analytics = self.api_analytics.copy()
        
        if client_id:
            analytics = [a for a in analytics if a.client_id == client_id]
        
        if start_date:
            analytics = [a for a in analytics if a.date >= start_date]
        
        if end_date:
            analytics = [a for a in analytics if a.date <= end_date]
        
        return analytics
    
    def generate_sdk(self, language: str, client_id: str) -> Dict[str, Any]:
        """Generate SDK for a specific language"""
        try:
            client = self.get_api_client(client_id)
            if not client:
                raise ValueError(f"API client {client_id} not found")
            
            endpoints = self.get_api_endpoints()
            
            if language.lower() == 'python':
                return self._generate_python_sdk(client, endpoints)
            elif language.lower() == 'javascript':
                return self._generate_javascript_sdk(client, endpoints)
            elif language.lower() == 'java':
                return self._generate_java_sdk(client, endpoints)
            elif language.lower() == 'php':
                return self._generate_php_sdk(client, endpoints)
            else:
                raise ValueError(f"Unsupported language: {language}")
                
        except Exception as e:
            logger.error(f"Error generating SDK: {str(e)}")
            raise
    
    def _generate_python_sdk(self, client: APIClient, endpoints: List[APIEndpoint]) -> Dict[str, Any]:
        """Generate Python SDK"""
        sdk_code = f'''
import requests
import json
from typing import Dict, Any, Optional

class ERPAPIClient:
    def __init__(self, api_key: str, base_url: str = "https://api.erpsystem.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({{
            'Authorization': f'Bearer {{api_key}}',
            'Content-Type': 'application/json'
        }})
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{{self.base_url}}{{endpoint}}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
'''
        
        for endpoint in endpoints:
            method_name = endpoint.name.lower().replace(' ', '_').replace('-', '_')
            sdk_code += f'''
    def {method_name}(self, **kwargs) -> Dict[str, Any]:
        """{endpoint.description}"""
        return self._make_request('{endpoint.method}', '{endpoint.path}', **kwargs)
'''
        
        return {
            'language': 'python',
            'code': sdk_code,
            'filename': 'erp_api_client.py',
            'requirements': ['requests>=2.25.0']
        }
    
    def _generate_javascript_sdk(self, client: APIClient, endpoints: List[APIEndpoint]) -> Dict[str, Any]:
        """Generate JavaScript SDK"""
        sdk_code = f'''
class ERPAPIClient {{
    constructor(apiKey, baseUrl = 'https://api.erpsystem.com') {{
        this.apiKey = apiKey;
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.headers = {{
            'Authorization': `Bearer ${{apiKey}}`,
            'Content-Type': 'application/json'
        }};
    }}
    
    async _makeRequest(method, endpoint, options = {{}}) {{
        const url = `${{this.baseUrl}}${{endpoint}}`;
        const response = await fetch(url, {{
            method,
            headers: this.headers,
            ...options
        }});
        
        if (!response.ok) {{
            throw new Error(`HTTP error! status: ${{response.status}}`);
        }}
        
        return await response.json();
    }}
'''
        
        for endpoint in endpoints:
            method_name = endpoint.name.toLowerCase().replace(/\s+/g, '_').replace(/-/g, '_');
            sdk_code += f'''
    async {method_name}(options = {{}}) {{
        return this._makeRequest('{endpoint.method}', '{endpoint.path}', options);
    }}
'''
        
        sdk_code += '}'
        
        return {
            'language': 'javascript',
            'code': sdk_code,
            'filename': 'erp-api-client.js',
            'type': 'module'
        }
    
    def _generate_java_sdk(self, client: APIClient, endpoints: List[APIEndpoint]) -> Dict[str, Any]:
        """Generate Java SDK"""
        sdk_code = f'''
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import com.fasterxml.jackson.databind.ObjectMapper;

public class ERPAPIClient {{
    private final String apiKey;
    private final String baseUrl;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    
    public ERPAPIClient(String apiKey, String baseUrl) {{
        this.apiKey = apiKey;
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.httpClient = HttpClient.newHttpClient();
        this.objectMapper = new ObjectMapper();
    }}
    
    private String makeRequest(String method, String endpoint, String body) throws Exception {{
        String url = baseUrl + endpoint;
        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .header("Authorization", "Bearer " + apiKey)
            .header("Content-Type", "application/json");
        
        if (body != null) {{
            requestBuilder.method(method, HttpRequest.BodyPublishers.ofString(body));
        }} else {{
            requestBuilder.method(method, HttpRequest.BodyPublishers.noBody());
        }}
        
        HttpResponse<String> response = httpClient.send(
            requestBuilder.build(),
            HttpResponse.BodyHandlers.ofString()
        );
        
        if (response.statusCode() >= 400) {{
            throw new RuntimeException("HTTP error: " + response.statusCode());
        }}
        
        return response.body();
    }}
'''
        
        for endpoint in endpoints:
            method_name = endpoint.name.replace(' ', '').replace('-', '');
            sdk_code += f'''
    public String {method_name}() throws Exception {{
        return makeRequest("{endpoint.method}", "{endpoint.path}", null);
    }}
'''
        
        sdk_code += '}'
        
        return {
            'language': 'java',
            'code': sdk_code,
            'filename': 'ERPAPIClient.java',
            'dependencies': ['jackson-databind', 'java.net.http']
        }
    
    def _generate_php_sdk(self, client: APIClient, endpoints: List[APIEndpoint]) -> Dict[str, Any]:
        """Generate PHP SDK"""
        sdk_code = f'''
<?php

class ERPAPIClient {{
    private $apiKey;
    private $baseUrl;
    
    public function __construct($apiKey, $baseUrl = 'https://api.erpsystem.com') {{
        $this->apiKey = $apiKey;
        $this->baseUrl = rtrim($baseUrl, '/');
    }}
    
    private function makeRequest($method, $endpoint, $data = null) {{
        $url = $this->baseUrl . $endpoint;
        
        $headers = [
            'Authorization: Bearer ' . $this->apiKey,
            'Content-Type: application/json'
        ];}
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
        
        if ($data !== null) {{
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }}
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode >= 400) {{
            throw new Exception("HTTP error: " . $httpCode);
        }}
        
        return json_decode($response, true);
    }}
'''
        
        for endpoint in endpoints:
            method_name = strtolower(str_replace([' ', '-'], '_', $endpoint->name));
            sdk_code += f'''
    public function {method_name}($data = null) {{
        return $this->makeRequest('{endpoint.method}', '{endpoint.path}', $data);
    }}
'''
        
        sdk_code += '}'
        
        return {
            'language': 'php',
            'code': sdk_code,
            'filename': 'ERPAPIClient.php',
            'requirements': ['php>=7.4', 'curl']
        }
    
    def _generate_secret(self) -> str:
        """Generate a secure secret"""
        return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode()[:32]
    
    def _generate_api_key(self) -> str:
        """Generate an API key"""
        return f"erp_{uuid.uuid4().hex[:16]}"
    
    def _create_webhook_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """Create webhook signature"""
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

# Global API Marketplace instance
api_marketplace = APIMarketplace()
