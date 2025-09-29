# IoT Device Management System
# Device registration, monitoring, and lifecycle management

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeviceType(Enum):
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    GATEWAY = "gateway"
    CAMERA = "camera"
    CONTROLLER = "controller"
    MONITOR = "monitor"

class DeviceStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    UNKNOWN = "unknown"

@dataclass
class IoTDevice:
    device_id: str
    name: str
    device_type: DeviceType
    manufacturer: str
    model: str
    serial_number: str
    firmware_version: str
    ip_address: str
    mac_address: str
    location: str
    status: DeviceStatus = DeviceStatus.UNKNOWN
    last_seen: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class DeviceManagement:
    """
    IoT Device Management System
    Device registration, monitoring, and lifecycle management
    """
    
    def __init__(self):
        self.devices: Dict[str, IoTDevice] = {}
        self.device_queue = queue.Queue()
        self.is_processing = True
        
        # Start background processing
        self._start_processing()
    
    def _start_processing(self):
        """Start background processing"""
        self.is_processing = True
        
        # Start processing thread
        thread = threading.Thread(target=self._process_devices, daemon=True)
        thread.start()
        
        logger.info("IoT device management processing started")
    
    def _process_devices(self):
        """Process device updates in background"""
        while self.is_processing:
            try:
                device_data = self.device_queue.get(timeout=1)
                self._handle_device_update(device_data)
                self.device_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing device: {str(e)}")
    
    def register_device(self, name: str, device_type: DeviceType, manufacturer: str,
                       model: str, serial_number: str, ip_address: str,
                       mac_address: str, location: str, firmware_version: str = "1.0.0",
                       metadata: Dict[str, Any] = None) -> IoTDevice:
        """Register a new IoT device"""
        try:
            device = IoTDevice(
                device_id=str(uuid.uuid4()),
                name=name,
                device_type=device_type,
                manufacturer=manufacturer,
                model=model,
                serial_number=serial_number,
                firmware_version=firmware_version,
                ip_address=ip_address,
                mac_address=mac_address,
                location=location,
                metadata=metadata or {}
            )
            
            self.devices[device.device_id] = device
            
            # Queue for processing
            self.device_queue.put({
                'action': 'register',
                'device': device
            })
            
            logger.info(f"Device registered: {device.device_id}")
            return device
            
        except Exception as e:
            logger.error(f"Error registering device: {str(e)}")
            raise
    
    def update_device_status(self, device_id: str, status: DeviceStatus) -> bool:
        """Update device status"""
        try:
            if device_id not in self.devices:
                return False
            
            device = self.devices[device_id]
            device.status = status
            device.last_seen = datetime.now()
            device.updated_at = datetime.now()
            
            # Queue for processing
            self.device_queue.put({
                'action': 'status_update',
                'device': device
            })
            
            logger.info(f"Device status updated: {device_id} -> {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating device status: {str(e)}")
            return False
    
    def get_device(self, device_id: str) -> Optional[IoTDevice]:
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def get_devices_by_type(self, device_type: DeviceType) -> List[IoTDevice]:
        """Get devices by type"""
        return [
            device for device in self.devices.values()
            if device.device_type == device_type
        ]
    
    def get_devices_by_status(self, status: DeviceStatus) -> List[IoTDevice]:
        """Get devices by status"""
        return [
            device for device in self.devices.values()
            if device.status == status
        ]
    
    def _handle_device_update(self, device_data: Dict[str, Any]):
        """Handle device update"""
        try:
            action = device_data.get('action')
            device = device_data.get('device')
            
            if action == 'register':
                self._process_device_registration(device)
            elif action == 'status_update':
                self._process_device_status_update(device)
            
        except Exception as e:
            logger.error(f"Error handling device update: {str(e)}")
    
    def _process_device_registration(self, device: IoTDevice):
        """Process device registration"""
        try:
            # This would implement device registration processing
            # For now, we'll just log the action
            logger.info(f"Device registration processed: {device.device_id}")
            
        except Exception as e:
            logger.error(f"Error processing device registration: {str(e)}")
    
    def _process_device_status_update(self, device: IoTDevice):
        """Process device status update"""
        try:
            # This would implement device status update processing
            # For now, we'll just log the action
            logger.info(f"Device status update processed: {device.device_id}")
            
        except Exception as e:
            logger.error(f"Error processing device status update: {str(e)}")
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get device analytics"""
        try:
            total_devices = len(self.devices)
            online_devices = len([d for d in self.devices.values() if d.status == DeviceStatus.ONLINE])
            offline_devices = len([d for d in self.devices.values() if d.status == DeviceStatus.OFFLINE])
            
            # Device type distribution
            device_types = {}
            for device in self.devices.values():
                device_type = device.device_type.value
                device_types[device_type] = device_types.get(device_type, 0) + 1
            
            return {
                'total_devices': total_devices,
                'online_devices': online_devices,
                'offline_devices': offline_devices,
                'device_types': device_types
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}

# Global device management instance
device_management = DeviceManagement()
