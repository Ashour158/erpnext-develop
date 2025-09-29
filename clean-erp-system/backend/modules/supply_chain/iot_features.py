# IoT Features for Supply Chain Module
# IoT device management and smart manufacturing integrated into Supply Chain

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
    RFID_READER = "rfid_reader"
    BARCODE_SCANNER = "barcode_scanner"
    WEIGHT_SCALE = "weight_scale"
    TEMPERATURE_SENSOR = "temperature_sensor"

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
    warehouse_id: Optional[str] = None
    status: DeviceStatus = DeviceStatus.UNKNOWN
    last_seen: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class IoTDeviceManagement:
    """
    IoT Device Management for Supply Chain
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
                       mac_address: str, location: str, warehouse_id: str = None,
                       firmware_version: str = "1.0.0", metadata: Dict[str, Any] = None) -> IoTDevice:
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
                warehouse_id=warehouse_id,
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
    
    def get_devices_by_warehouse(self, warehouse_id: str) -> List[IoTDevice]:
        """Get devices by warehouse"""
        return [
            device for device in self.devices.values()
            if device.warehouse_id == warehouse_id
        ]
    
    def get_devices_by_type(self, device_type: DeviceType) -> List[IoTDevice]:
        """Get devices by type"""
        return [
            device for device in self.devices.values()
            if device.device_type == device_type
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

class SmartManufacturing:
    """
    Smart Manufacturing for Supply Chain
    Production line monitoring and automation
    """
    
    def __init__(self):
        self.production_lines: Dict[str, Dict[str, Any]] = {}
        self.sensors: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[Dict[str, Any]] = []
    
    def create_production_line(self, name: str, location: str, 
                              capacity: int, metadata: Dict[str, Any] = None) -> str:
        """Create a production line"""
        try:
            line_id = str(uuid.uuid4())
            
            production_line = {
                'line_id': line_id,
                'name': name,
                'location': location,
                'capacity': capacity,
                'status': 'active',
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'metadata': metadata or {}
            }
            
            self.production_lines[line_id] = production_line
            
            logger.info(f"Production line created: {line_id}")
            return line_id
            
        except Exception as e:
            logger.error(f"Error creating production line: {str(e)}")
            return ""
    
    def add_sensor_to_line(self, line_id: str, sensor_id: str, sensor_type: str,
                          position: str, metadata: Dict[str, Any] = None) -> bool:
        """Add sensor to production line"""
        try:
            if line_id not in self.production_lines:
                return False
            
            sensor = {
                'sensor_id': sensor_id,
                'line_id': line_id,
                'sensor_type': sensor_type,
                'position': position,
                'status': 'active',
                'created_at': datetime.now(),
                'metadata': metadata or {}
            }
            
            self.sensors[sensor_id] = sensor
            
            logger.info(f"Sensor added to line: {sensor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding sensor to line: {str(e)}")
            return False
    
    def get_production_line_status(self, line_id: str) -> Dict[str, Any]:
        """Get production line status"""
        try:
            if line_id not in self.production_lines:
                return {'status': 'error', 'message': 'Production line not found'}
            
            line = self.production_lines[line_id]
            
            # Get sensors for this line
            line_sensors = [
                sensor for sensor in self.sensors.values()
                if sensor['line_id'] == line_id
            ]
            
            return {
                'line_id': line_id,
                'name': line['name'],
                'status': line['status'],
                'capacity': line['capacity'],
                'sensors_count': len(line_sensors),
                'active_sensors': len([s for s in line_sensors if s['status'] == 'active']),
                'last_updated': line['updated_at'].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting production line status: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def create_alert(self, line_id: str, alert_type: str, message: str,
                    severity: str = 'medium', metadata: Dict[str, Any] = None) -> str:
        """Create production alert"""
        try:
            alert_id = str(uuid.uuid4())
            
            alert = {
                'alert_id': alert_id,
                'line_id': line_id,
                'alert_type': alert_type,
                'message': message,
                'severity': severity,
                'status': 'active',
                'created_at': datetime.now(),
                'metadata': metadata or {}
            }
            
            self.alerts.append(alert)
            
            logger.info(f"Production alert created: {alert_id}")
            return alert_id
            
        except Exception as e:
            logger.error(f"Error creating production alert: {str(e)}")
            return ""

class SupplyChainIoT:
    """
    Supply Chain IoT Integration
    IoT data processing and analytics for supply chain
    """
    
    def __init__(self):
        self.iot_data: Dict[str, List[Dict[str, Any]]] = {}
        self.analytics: Dict[str, Dict[str, Any]] = {}
    
    def store_iot_data(self, device_id: str, data: Dict[str, Any]) -> bool:
        """Store IoT data"""
        try:
            if device_id not in self.iot_data:
                self.iot_data[device_id] = []
            
            data_point = {
                'timestamp': datetime.now(),
                'data': data,
                'processed': False
            }
            
            self.iot_data[device_id].append(data_point)
            
            # Keep only last 1000 data points per device
            if len(self.iot_data[device_id]) > 1000:
                self.iot_data[device_id] = self.iot_data[device_id][-1000:]
            
            logger.info(f"IoT data stored for device: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing IoT data: {str(e)}")
            return False
    
    def get_iot_data(self, device_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get IoT data for device"""
        try:
            if device_id not in self.iot_data:
                return []
            
            return self.iot_data[device_id][-limit:]
            
        except Exception as e:
            logger.error(f"Error getting IoT data: {str(e)}")
            return []
    
    def analyze_iot_data(self, device_id: str) -> Dict[str, Any]:
        """Analyze IoT data for device"""
        try:
            if device_id not in self.iot_data:
                return {'status': 'error', 'message': 'No data found for device'}
            
            data_points = self.iot_data[device_id]
            
            if not data_points:
                return {'status': 'error', 'message': 'No data points available'}
            
            # Calculate basic analytics
            timestamps = [dp['timestamp'] for dp in data_points]
            data_values = [dp['data'] for dp in data_points]
            
            # Calculate statistics
            analytics = {
                'device_id': device_id,
                'total_data_points': len(data_points),
                'first_timestamp': min(timestamps).isoformat(),
                'last_timestamp': max(timestamps).isoformat(),
                'data_frequency': len(data_points) / max(1, (max(timestamps) - min(timestamps)).total_seconds() / 3600),  # points per hour
                'status': 'success'
            }
            
            # Store analytics
            self.analytics[device_id] = analytics
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error analyzing IoT data: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_analytics(self, device_id: str) -> Dict[str, Any]:
        """Get analytics for device"""
        return self.analytics.get(device_id, {})

# Global IoT features instances
iot_device_management = IoTDeviceManagement()
smart_manufacturing = SmartManufacturing()
supply_chain_iot = SupplyChainIoT()
