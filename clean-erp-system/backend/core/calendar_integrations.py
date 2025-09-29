# External Calendar Integrations
# Integration with Google Calendar, Microsoft Outlook, and other calendar providers

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
import requests
import json
from typing import Dict, List, Optional, Tuple

class IntegrationProvider(enum.Enum):
    GOOGLE = "Google"
    MICROSOFT = "Microsoft"
    APPLE = "Apple"
    OUTLOOK = "Outlook"
    YAHOO = "Yahoo"
    CUSTOM = "Custom"

class SyncDirection(enum.Enum):
    INBOUND = "Inbound"
    OUTBOUND = "Outbound"
    BIDIRECTIONAL = "Bidirectional"

class IntegrationStatus(enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ERROR = "Error"
    SYNCING = "Syncing"

class CalendarIntegration(BaseModel):
    """External calendar integration model"""
    __tablename__ = 'calendar_integrations'
    
    # Integration Information
    integration_name = db.Column(db.String(200), nullable=False)
    provider = db.Column(db.Enum(IntegrationProvider), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Authentication
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expires = db.Column(db.DateTime)
    client_id = db.Column(db.String(255))
    client_secret = db.Column(db.String(255))
    
    # Integration Settings
    sync_direction = db.Column(db.Enum(SyncDirection), default=SyncDirection.BIDIRECTIONAL)
    sync_frequency = db.Column(db.Integer, default=15)  # minutes
    auto_sync = db.Column(db.Boolean, default=True)
    
    # Calendar Mapping
    external_calendar_id = db.Column(db.String(255))
    internal_calendar_id = db.Column(db.Integer, db.ForeignKey('calendars.id'))
    internal_calendar = relationship("Calendar")
    
    # Sync Status
    last_sync = db.Column(db.DateTime)
    sync_status = db.Column(db.Enum(IntegrationStatus), default=IntegrationStatus.ACTIVE)
    sync_errors = db.Column(db.JSON)
    sync_count = db.Column(db.Integer, default=0)
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'integration_name': self.integration_name,
            'provider': self.provider.value if self.provider else None,
            'is_active': self.is_active,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_expires': self.token_expires.isoformat() if self.token_expires else None,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'sync_direction': self.sync_direction.value if self.sync_direction else None,
            'sync_frequency': self.sync_frequency,
            'auto_sync': self.auto_sync,
            'external_calendar_id': self.external_calendar_id,
            'internal_calendar_id': self.internal_calendar_id,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'sync_status': self.sync_status.value if self.sync_status else None,
            'sync_errors': self.sync_errors,
            'sync_count': self.sync_count,
            'user_id': self.user_id,
            'company_id': self.company_id
        })
        return data

class SyncLog(BaseModel):
    """Sync log model"""
    __tablename__ = 'sync_logs'
    
    # Sync Information
    sync_type = db.Column(db.String(50), nullable=False)  # Inbound, Outbound, Bidirectional
    sync_status = db.Column(db.String(50), nullable=False)  # Success, Error, Partial
    sync_start = db.Column(db.DateTime, default=datetime.utcnow)
    sync_end = db.Column(db.DateTime)
    sync_duration = db.Column(db.Float, default=0.0)  # seconds
    
    # Sync Results
    events_synced = db.Column(db.Integer, default=0)
    events_created = db.Column(db.Integer, default=0)
    events_updated = db.Column(db.Integer, default=0)
    events_deleted = db.Column(db.Integer, default=0)
    events_skipped = db.Column(db.Integer, default=0)
    
    # Error Information
    error_message = db.Column(db.Text)
    error_details = db.Column(db.JSON)
    
    # Integration Association
    integration_id = db.Column(db.Integer, db.ForeignKey('calendar_integrations.id'), nullable=False)
    integration = relationship("CalendarIntegration")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'sync_type': self.sync_type,
            'sync_status': self.sync_status,
            'sync_start': self.sync_start.isoformat() if self.sync_start else None,
            'sync_end': self.sync_end.isoformat() if self.sync_end else None,
            'sync_duration': self.sync_duration,
            'events_synced': self.events_synced,
            'events_created': self.events_created,
            'events_updated': self.events_updated,
            'events_deleted': self.events_deleted,
            'events_skipped': self.events_skipped,
            'error_message': self.error_message,
            'error_details': self.error_details,
            'integration_id': self.integration_id,
            'company_id': self.company_id
        })
        return data

# Google Calendar Integration
class GoogleCalendarIntegration:
    """Google Calendar integration class"""
    
    def __init__(self, integration: CalendarIntegration):
        self.integration = integration
        self.base_url = "https://www.googleapis.com/calendar/v3"
        self.headers = {
            'Authorization': f'Bearer {integration.access_token}',
            'Content-Type': 'application/json'
        }
    
    def refresh_token(self) -> bool:
        """Refresh access token"""
        try:
            url = "https://oauth2.googleapis.com/token"
            data = {
                'client_id': self.integration.client_id,
                'client_secret': self.integration.client_secret,
                'refresh_token': self.integration.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.integration.access_token = token_data['access_token']
                self.integration.token_expires = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False
    
    def get_calendars(self) -> List[Dict]:
        """Get user's calendars"""
        try:
            url = f"{self.base_url}/users/me/calendarList"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 401:
                if self.refresh_token():
                    self.headers['Authorization'] = f'Bearer {self.integration.access_token}'
                    response = requests.get(url, headers=self.headers)
                else:
                    return []
            
            if response.status_code == 200:
                return response.json().get('items', [])
            return []
        except Exception as e:
            print(f"Error getting calendars: {e}")
            return []
    
    def get_events(self, calendar_id: str, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Get events from calendar"""
        try:
            url = f"{self.base_url}/calendars/{calendar_id}/events"
            params = {}
            
            if start_date:
                params['timeMin'] = start_date.isoformat() + 'Z'
            if end_date:
                params['timeMax'] = end_date.isoformat() + 'Z'
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 401:
                if self.refresh_token():
                    self.headers['Authorization'] = f'Bearer {self.integration.access_token}'
                    response = requests.get(url, headers=self.headers, params=params)
                else:
                    return []
            
            if response.status_code == 200:
                return response.json().get('items', [])
            return []
        except Exception as e:
            print(f"Error getting events: {e}")
            return []
    
    def create_event(self, calendar_id: str, event_data: Dict) -> Optional[Dict]:
        """Create event in calendar"""
        try:
            url = f"{self.base_url}/calendars/{calendar_id}/events"
            response = requests.post(url, headers=self.headers, json=event_data)
            
            if response.status_code == 401:
                if self.refresh_token():
                    self.headers['Authorization'] = f'Bearer {self.integration.access_token}'
                    response = requests.post(url, headers=self.headers, json=event_data)
                else:
                    return None
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error creating event: {e}")
            return None
    
    def update_event(self, calendar_id: str, event_id: str, event_data: Dict) -> Optional[Dict]:
        """Update event in calendar"""
        try:
            url = f"{self.base_url}/calendars/{calendar_id}/events/{event_id}"
            response = requests.put(url, headers=self.headers, json=event_data)
            
            if response.status_code == 401:
                if self.refresh_token():
                    self.headers['Authorization'] = f'Bearer {self.integration.access_token}'
                    response = requests.put(url, headers=self.headers, json=event_data)
                else:
                    return None
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error updating event: {e}")
            return None
    
    def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """Delete event from calendar"""
        try:
            url = f"{self.base_url}/calendars/{calendar_id}/events/{event_id}"
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code == 401:
                if self.refresh_token():
                    self.headers['Authorization'] = f'Bearer {self.integration.access_token}'
                    response = requests.delete(url, headers=self.headers)
                else:
                    return False
            
            return response.status_code == 204
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False

# Microsoft Outlook Integration
class MicrosoftOutlookIntegration:
    """Microsoft Outlook integration class"""
    
    def __init__(self, integration: CalendarIntegration):
        self.integration = integration
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            'Authorization': f'Bearer {integration.access_token}',
            'Content-Type': 'application/json'
        }
    
    def refresh_token(self) -> bool:
        """Refresh access token"""
        try:
            url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            data = {
                'client_id': self.integration.client_id,
                'client_secret': self.integration.client_secret,
                'refresh_token': self.integration.refresh_token,
                'grant_type': 'refresh_token',
                'scope': 'https://graph.microsoft.com/calendars.readwrite'
            }
            
            response = requests.post(url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.integration.access_token = token_data['access_token']
                self.integration.token_expires = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False
    
    def get_calendars(self) -> List[Dict]:
        """Get user's calendars"""
        try:
            url = f"{self.base_url}/me/calendars"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 401:
                if self.refresh_token():
                    self.headers['Authorization'] = f'Bearer {self.integration.access_token}'
                    response = requests.get(url, headers=self.headers)
                else:
                    return []
            
            if response.status_code == 200:
                return response.json().get('value', [])
            return []
        except Exception as e:
            print(f"Error getting calendars: {e}")
            return []
    
    def get_events(self, calendar_id: str, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Get events from calendar"""
        try:
            url = f"{self.base_url}/me/calendars/{calendar_id}/events"
            params = {}
            
            if start_date and end_date:
                params['$filter'] = f"start/dateTime ge '{start_date.isoformat()}' and end/dateTime le '{end_date.isoformat()}'"
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 401:
                if self.refresh_token():
                    self.headers['Authorization'] = f'Bearer {self.integration.access_token}'
                    response = requests.get(url, headers=self.headers, params=params)
                else:
                    return []
            
            if response.status_code == 200:
                return response.json().get('value', [])
            return []
        except Exception as e:
            print(f"Error getting events: {e}")
            return []
    
    def create_event(self, calendar_id: str, event_data: Dict) -> Optional[Dict]:
        """Create event in calendar"""
        try:
            url = f"{self.base_url}/me/calendars/{calendar_id}/events"
            response = requests.post(url, headers=self.headers, json=event_data)
            
            if response.status_code == 401:
                if self.refresh_token():
                    self.headers['Authorization'] = f'Bearer {self.integration.access_token}'
                    response = requests.post(url, headers=self.headers, json=event_data)
                else:
                    return None
            
            if response.status_code == 201:
                return response.json()
            return None
        except Exception as e:
            print(f"Error creating event: {e}")
            return None
    
    def update_event(self, calendar_id: str, event_id: str, event_data: Dict) -> Optional[Dict]:
        """Update event in calendar"""
        try:
            url = f"{self.base_url}/me/calendars/{calendar_id}/events/{event_id}"
            response = requests.patch(url, headers=self.headers, json=event_data)
            
            if response.status_code == 401:
                if self.refresh_token():
                    self.headers['Authorization'] = f'Bearer {self.integration.access_token}'
                    response = requests.patch(url, headers=self.headers, json=event_data)
                else:
                    return None
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error updating event: {e}")
            return None
    
    def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """Delete event from calendar"""
        try:
            url = f"{self.base_url}/me/calendars/{calendar_id}/events/{event_id}"
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code == 401:
                if self.refresh_token():
                    self.headers['Authorization'] = f'Bearer {self.integration.access_token}'
                    response = requests.delete(url, headers=self.headers)
                else:
                    return False
            
            return response.status_code == 204
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False

# Integration Factory
class IntegrationFactory:
    """Factory for creating integration instances"""
    
    @staticmethod
    def create_integration(integration: CalendarIntegration):
        """Create integration instance based on provider"""
        if integration.provider == IntegrationProvider.GOOGLE:
            return GoogleCalendarIntegration(integration)
        elif integration.provider == IntegrationProvider.MICROSOFT:
            return MicrosoftOutlookIntegration(integration)
        else:
            raise ValueError(f"Unsupported provider: {integration.provider}")

# Sync Service
class CalendarSyncService:
    """Calendar synchronization service"""
    
    def __init__(self, integration: CalendarIntegration):
        self.integration = integration
        self.external_integration = IntegrationFactory.create_integration(integration)
    
    def sync_calendars(self) -> SyncLog:
        """Sync calendars"""
        sync_log = SyncLog(
            sync_type='Calendar Sync',
            sync_status='Success',
            integration_id=self.integration.id,
            company_id=self.integration.company_id
        )
        
        try:
            # Get external calendars
            external_calendars = self.external_integration.get_calendars()
            
            # Process calendars
            for calendar in external_calendars:
                # Map external calendar to internal calendar
                # This would involve creating or updating internal calendar
                pass
            
            sync_log.sync_status = 'Success'
            sync_log.sync_end = datetime.utcnow()
            sync_log.sync_duration = (sync_log.sync_end - sync_log.sync_start).total_seconds()
            
        except Exception as e:
            sync_log.sync_status = 'Error'
            sync_log.error_message = str(e)
            sync_log.sync_end = datetime.utcnow()
            sync_log.sync_duration = (sync_log.sync_end - sync_log.sync_start).total_seconds()
        
        db.session.add(sync_log)
        db.session.commit()
        
        return sync_log
    
    def sync_events(self, start_date: datetime = None, end_date: datetime = None) -> SyncLog:
        """Sync events between external and internal calendars"""
        sync_log = SyncLog(
            sync_type='Event Sync',
            sync_status='Success',
            integration_id=self.integration.id,
            company_id=self.integration.company_id
        )
        
        try:
            # Get external events
            external_events = self.external_integration.get_events(
                self.integration.external_calendar_id,
                start_date,
                end_date
            )
            
            # Process events
            for event in external_events:
                # Map external event to internal event
                # This would involve creating or updating internal event
                sync_log.events_synced += 1
            
            sync_log.sync_status = 'Success'
            sync_log.sync_end = datetime.utcnow()
            sync_log.sync_duration = (sync_log.sync_end - sync_log.sync_start).total_seconds()
            
        except Exception as e:
            sync_log.sync_status = 'Error'
            sync_log.error_message = str(e)
            sync_log.sync_end = datetime.utcnow()
            sync_log.sync_duration = (sync_log.sync_end - sync_log.sync_start).total_seconds()
        
        db.session.add(sync_log)
        db.session.commit()
        
        return sync_log
