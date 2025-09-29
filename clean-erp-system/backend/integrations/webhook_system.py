# Webhook System
# Real-time webhook delivery and management system

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import uuid
import hashlib
import hmac
from urllib.parse import urlparse
import ssl
from concurrent.futures import ThreadPoolExecutor
import queue
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookStatus(Enum):
    PENDING = "pending"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"

class WebhookPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class WebhookEvent:
    event_id: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    source: str
    priority: WebhookPriority = WebhookPriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = None

@dataclass
class WebhookDelivery:
    delivery_id: str
    webhook_url: str
    event: WebhookEvent
    status: WebhookStatus
    created_at: datetime
    delivered_at: Optional[datetime] = None
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    next_retry_at: Optional[datetime] = None
    headers: Dict[str, str] = None
    timeout: int = 30

@dataclass
class WebhookSubscription:
    subscription_id: str
    client_id: str
    event_types: List[str]
    webhook_url: str
    secret_key: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    failure_count: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    retry_policy: Dict[str, Any] = None
    headers: Dict[str, str] = None
    timeout: int = 30

class WebhookSystem:
    """
    Advanced Webhook System for Real-time Integration
    Provides reliable webhook delivery with retry mechanisms and monitoring
    """
    
    def __init__(self):
        self.subscriptions: Dict[str, WebhookSubscription] = {}
        self.deliveries: Dict[str, WebhookDelivery] = {}
        self.event_queue = queue.PriorityQueue()
        self.delivery_queue = queue.PriorityQueue()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = False
        self.worker_threads = []
        self.retry_intervals = [1, 5, 15, 60, 300]  # seconds
        self.max_retries = 5
        
        # Start background workers
        self._start_workers()
    
    def _start_workers(self):
        """Start background worker threads"""
        self.running = True
        
        # Event processor worker
        event_worker = threading.Thread(target=self._process_events, daemon=True)
        event_worker.start()
        self.worker_threads.append(event_worker)
        
        # Delivery worker
        delivery_worker = threading.Thread(target=self._process_deliveries, daemon=True)
        delivery_worker.start()
        self.worker_threads.append(delivery_worker)
        
        # Retry worker
        retry_worker = threading.Thread(target=self._process_retries, daemon=True)
        retry_worker.start()
        self.worker_threads.append(retry_worker)
        
        logger.info("Webhook system workers started")
    
    def stop(self):
        """Stop the webhook system"""
        self.running = False
        for thread in self.worker_threads:
            thread.join(timeout=5)
        logger.info("Webhook system stopped")
    
    def create_subscription(self,
                           client_id: str,
                           event_types: List[str],
                           webhook_url: str,
                           secret_key: str,
                           retry_policy: Optional[Dict[str, Any]] = None,
                           headers: Optional[Dict[str, str]] = None,
                           timeout: int = 30) -> WebhookSubscription:
        """Create a new webhook subscription"""
        try:
            subscription_id = str(uuid.uuid4())
            
            # Validate webhook URL
            parsed_url = urlparse(webhook_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid webhook URL")
            
            subscription = WebhookSubscription(
                subscription_id=subscription_id,
                client_id=client_id,
                event_types=event_types,
                webhook_url=webhook_url,
                secret_key=secret_key,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                retry_policy=retry_policy or {
                    'max_retries': 5,
                    'retry_intervals': [1, 5, 15, 60, 300],
                    'exponential_backoff': True
                },
                headers=headers or {},
                timeout=timeout
            )
            
            self.subscriptions[subscription_id] = subscription
            logger.info(f"Created webhook subscription: {subscription_id} for {client_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error creating webhook subscription: {str(e)}")
            raise
    
    def update_subscription(self, subscription_id: str, updates: Dict[str, Any]) -> bool:
        """Update webhook subscription"""
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Webhook subscription {subscription_id} not found")
            
            subscription = self.subscriptions[subscription_id]
            
            # Update allowed fields
            allowed_fields = ['event_types', 'webhook_url', 'secret_key', 'is_active', 
                             'retry_policy', 'headers', 'timeout']
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(subscription, field, value)
            
            subscription.updated_at = datetime.now()
            self.subscriptions[subscription_id] = subscription
            
            logger.info(f"Updated webhook subscription: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating webhook subscription: {str(e)}")
            return False
    
    def delete_subscription(self, subscription_id: str) -> bool:
        """Delete webhook subscription"""
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Webhook subscription {subscription_id} not found")
            
            del self.subscriptions[subscription_id]
            logger.info(f"Deleted webhook subscription: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting webhook subscription: {str(e)}")
            return False
    
    def trigger_webhook(self, event_type: str, payload: Dict[str, Any], 
                       source: str = "system", priority: WebhookPriority = WebhookPriority.NORMAL) -> str:
        """Trigger webhook for an event"""
        try:
            event_id = str(uuid.uuid4())
            
            event = WebhookEvent(
                event_id=event_id,
                event_type=event_type,
                payload=payload,
                timestamp=datetime.now(),
                source=source,
                priority=priority,
                metadata={}
            )
            
            # Add to event queue with priority
            priority_value = {
                WebhookPriority.URGENT: 1,
                WebhookPriority.HIGH: 2,
                WebhookPriority.NORMAL: 3,
                WebhookPriority.LOW: 4
            }[priority]
            
            self.event_queue.put((priority_value, event))
            
            logger.info(f"Triggered webhook event: {event_type} (ID: {event_id})")
            return event_id
            
        except Exception as e:
            logger.error(f"Error triggering webhook: {str(e)}")
            raise
    
    def _process_events(self):
        """Process webhook events from queue"""
        while self.running:
            try:
                # Get event from queue (blocking with timeout)
                priority, event = self.event_queue.get(timeout=1)
                
                # Find matching subscriptions
                matching_subscriptions = [
                    sub for sub in self.subscriptions.values()
                    if sub.is_active and event.event_type in sub.event_types
                ]
                
                # Create deliveries for each subscription
                for subscription in matching_subscriptions:
                    delivery_id = str(uuid.uuid4())
                    
                    delivery = WebhookDelivery(
                        delivery_id=delivery_id,
                        webhook_url=subscription.webhook_url,
                        event=event,
                        status=WebhookStatus.PENDING,
                        created_at=datetime.now(),
                        headers=subscription.headers.copy(),
                        timeout=subscription.timeout
                    )
                    
                    # Add webhook signature
                    signature = self._create_webhook_signature(event, subscription.secret_key)
                    delivery.headers['X-Webhook-Signature'] = signature
                    delivery.headers['X-Webhook-Event'] = event.event_type
                    delivery.headers['X-Webhook-Delivery'] = delivery_id
                    
                    self.deliveries[delivery_id] = delivery
                    
                    # Add to delivery queue
                    self.delivery_queue.put((priority, delivery))
                
                self.event_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing webhook event: {str(e)}")
    
    def _process_deliveries(self):
        """Process webhook deliveries"""
        while self.running:
            try:
                # Get delivery from queue (blocking with timeout)
                priority, delivery = self.delivery_queue.get(timeout=1)
                
                # Update status to delivering
                delivery.status = WebhookStatus.DELIVERING
                self.deliveries[delivery.delivery_id] = delivery
                
                # Send webhook asynchronously
                asyncio.run(self._send_webhook(delivery))
                
                self.delivery_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing webhook delivery: {str(e)}")
    
    async def _send_webhook(self, delivery: WebhookDelivery):
        """Send webhook asynchronously"""
        try:
            # Prepare payload
            payload = {
                'event_id': delivery.event.event_id,
                'event_type': delivery.event.event_type,
                'timestamp': delivery.event.timestamp.isoformat(),
                'source': delivery.event.source,
                'data': delivery.event.payload
            }
            
            # Create HTTP request
            timeout = aiohttp.ClientTimeout(total=delivery.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    delivery.webhook_url,
                    json=payload,
                    headers=delivery.headers
                ) as response:
                    
                    delivery.response_code = response.status
                    delivery.response_body = await response.text()
                    
                    if response.status >= 200 and response.status < 300:
                        # Success
                        delivery.status = WebhookStatus.DELIVERED
                        delivery.delivered_at = datetime.now()
                        
                        # Update subscription success
                        subscription = self._get_subscription_by_url(delivery.webhook_url)
                        if subscription:
                            subscription.last_success = datetime.now()
                            subscription.failure_count = 0
                        
                        logger.info(f"Webhook delivered successfully: {delivery.delivery_id}")
                    else:
                        # Failed
                        delivery.status = WebhookStatus.FAILED
                        delivery.error_message = f"HTTP {response.status}: {delivery.response_body}"
                        
                        # Update subscription failure
                        subscription = self._get_subscription_by_url(delivery.webhook_url)
                        if subscription:
                            subscription.last_failure = datetime.now()
                            subscription.failure_count += 1
                        
                        # Schedule retry if not exceeded max retries
                        if delivery.retry_count < delivery.event.max_retries:
                            self._schedule_retry(delivery)
                        
                        logger.warning(f"Webhook delivery failed: {delivery.delivery_id} - {delivery.error_message}")
            
        except asyncio.TimeoutError:
            delivery.status = WebhookStatus.FAILED
            delivery.error_message = "Request timeout"
            self._schedule_retry(delivery)
            logger.warning(f"Webhook delivery timeout: {delivery.delivery_id}")
            
        except Exception as e:
            delivery.status = WebhookStatus.FAILED
            delivery.error_message = str(e)
            self._schedule_retry(delivery)
            logger.error(f"Webhook delivery error: {delivery.delivery_id} - {str(e)}")
        
        finally:
            # Update delivery in storage
            self.deliveries[delivery.delivery_id] = delivery
    
    def _schedule_retry(self, delivery: WebhookDelivery):
        """Schedule webhook retry"""
        if delivery.retry_count >= delivery.event.max_retries:
            delivery.status = WebhookStatus.EXPIRED
            logger.error(f"Webhook delivery expired after {delivery.retry_count} retries: {delivery.delivery_id}")
            return
        
        delivery.retry_count += 1
        delivery.status = WebhookStatus.RETRYING
        
        # Calculate retry delay with exponential backoff
        retry_delay = min(self.retry_intervals[delivery.retry_count - 1], 300)  # Max 5 minutes
        delivery.next_retry_at = datetime.now() + timedelta(seconds=retry_delay)
        
        # Add to retry queue
        self.delivery_queue.put((1, delivery))  # High priority for retries
        
        logger.info(f"Scheduled webhook retry {delivery.retry_count} for {delivery.delivery_id} in {retry_delay}s")
    
    def _process_retries(self):
        """Process webhook retries"""
        while self.running:
            try:
                # Check for deliveries that need retry
                current_time = datetime.now()
                retry_deliveries = [
                    delivery for delivery in self.deliveries.values()
                    if delivery.status == WebhookStatus.RETRYING and 
                       delivery.next_retry_at and 
                       delivery.next_retry_at <= current_time
                ]
                
                for delivery in retry_deliveries:
                    # Reset status and retry
                    delivery.status = WebhookStatus.PENDING
                    delivery.next_retry_at = None
                    self.delivery_queue.put((1, delivery))  # High priority
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error processing webhook retries: {str(e)}")
                time.sleep(5)
    
    def _get_subscription_by_url(self, webhook_url: str) -> Optional[WebhookSubscription]:
        """Get subscription by webhook URL"""
        for subscription in self.subscriptions.values():
            if subscription.webhook_url == webhook_url:
                return subscription
        return None
    
    def _create_webhook_signature(self, event: WebhookEvent, secret: str) -> str:
        """Create webhook signature"""
        payload = json.dumps({
            'event_id': event.event_id,
            'event_type': event.event_type,
            'timestamp': event.timestamp.isoformat(),
            'data': event.payload
        }, sort_keys=True)
        
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def get_webhook_statistics(self) -> Dict[str, Any]:
        """Get webhook system statistics"""
        total_subscriptions = len(self.subscriptions)
        active_subscriptions = len([s for s in self.subscriptions.values() if s.is_active])
        total_deliveries = len(self.deliveries)
        
        delivery_stats = {
            'pending': len([d for d in self.deliveries.values() if d.status == WebhookStatus.PENDING]),
            'delivering': len([d for d in self.deliveries.values() if d.status == WebhookStatus.DELIVERING]),
            'delivered': len([d for d in self.deliveries.values() if d.status == WebhookStatus.DELIVERED]),
            'failed': len([d for d in self.deliveries.values() if d.status == WebhookStatus.FAILED]),
            'retrying': len([d for d in self.deliveries.values() if d.status == WebhookStatus.RETRYING]),
            'expired': len([d for d in self.deliveries.values() if d.status == WebhookStatus.EXPIRED])
        }
        
        success_rate = 0
        if total_deliveries > 0:
            success_rate = (delivery_stats['delivered'] / total_deliveries) * 100
        
        return {
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'total_deliveries': total_deliveries,
            'delivery_stats': delivery_stats,
            'success_rate': success_rate,
            'queue_sizes': {
                'events': self.event_queue.qsize(),
                'deliveries': self.delivery_queue.qsize()
            }
        }
    
    def get_delivery_status(self, delivery_id: str) -> Optional[WebhookDelivery]:
        """Get webhook delivery status"""
        return self.deliveries.get(delivery_id)
    
    def get_subscription_deliveries(self, subscription_id: str, 
                                   limit: int = 100, offset: int = 0) -> List[WebhookDelivery]:
        """Get deliveries for a subscription"""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return []
        
        deliveries = [
            delivery for delivery in self.deliveries.values()
            if delivery.webhook_url == subscription.webhook_url
        ]
        
        # Sort by created_at descending
        deliveries.sort(key=lambda x: x.created_at, reverse=True)
        
        return deliveries[offset:offset + limit]

# Global Webhook System instance
webhook_system = WebhookSystem()
