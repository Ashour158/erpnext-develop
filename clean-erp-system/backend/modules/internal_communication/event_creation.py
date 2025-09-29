# Event Creation System
# Create events from chat system with calendar integration

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
import time
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    MEETING = "meeting"
    CALL = "call"
    DEADLINE = "deadline"
    REMINDER = "reminder"
    TASK = "task"
    APPOINTMENT = "appointment"
    CONFERENCE = "conference"
    WORKSHOP = "workshop"
    TRAINING = "training"
    SOCIAL = "social"

class EventStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"

class EventPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class ChatEvent:
    event_id: str
    title: str
    description: str
    event_type: EventType
    status: EventStatus
    priority: EventPriority
    created_by: str
    created_at: datetime
    scheduled_at: datetime
    duration: int  # minutes
    location: Optional[str] = None
    attendees: List[str] = field(default_factory=list)
    chat_id: Optional[str] = None
    message_id: Optional[str] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    reminder_minutes: List[int] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class EventReminder:
    reminder_id: str
    event_id: str
    user_id: str
    reminder_time: datetime
    message: str
    sent: bool = False
    sent_at: Optional[datetime] = None

class EventCreationSystem:
    """
    Event Creation System
    Creates events from chat messages and manages calendar integration
    """
    
    def __init__(self):
        self.events: Dict[str, ChatEvent] = {}
        self.reminders: Dict[str, EventReminder] = {}
        self.event_queue = queue.Queue()
        self.is_processing = True
        
        # Start background processing
        self._start_event_processing()
        
        # Initialize event patterns
        self._initialize_event_patterns()
    
    def _start_event_processing(self):
        """Start background event processing"""
        self.is_processing = True
        
        # Start processing thread
        thread = threading.Thread(target=self._process_events, daemon=True)
        thread.start()
        
        logger.info("Event creation system processing started")
    
    def _process_events(self):
        """Process events in background"""
        while self.is_processing:
            try:
                event_data = self.event_queue.get(timeout=1)
                self._handle_event_processing(event_data)
                self.event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {str(e)}")
    
    def _initialize_event_patterns(self):
        """Initialize event detection patterns"""
        self.event_patterns = {
            EventType.MEETING: [
                r'\b(meeting|discuss|talk about|review|planning)\b',
                r'\b(team meeting|standup|sync|catch up)\b',
                r'\b(weekly|daily|monthly) meeting\b'
            ],
            EventType.CALL: [
                r'\b(call|phone|video call|zoom|teams)\b',
                r'\b(conference call|teleconference)\b',
                r'\b(speak with|talk to|contact)\b'
            ],
            EventType.DEADLINE: [
                r'\b(deadline|due|submit|deliver|complete)\b',
                r'\b(finish by|end of|before)\b',
                r'\b(urgent|asap|immediately)\b'
            ],
            EventType.REMINDER: [
                r'\b(remind|remember|don\'t forget)\b',
                r'\b(follow up|check back|revisit)\b',
                r'\b(important|note|mark)\b'
            ],
            EventType.TASK: [
                r'\b(task|todo|work on|implement)\b',
                r'\b(need to|should|must)\b',
                r'\b(assignment|project|work)\b'
            ],
            EventType.APPOINTMENT: [
                r'\b(appointment|schedule|book|reserve)\b',
                r'\b(visit|see|meet with)\b',
                r'\b(available|free time|slot)\b'
            ],
            EventType.CONFERENCE: [
                r'\b(conference|convention|summit)\b',
                r'\b(presentation|speak|present)\b',
                r'\b(attend|participate|join)\b'
            ],
            EventType.WORKSHOP: [
                r'\b(workshop|training|session)\b',
                r'\b(learn|teach|instruct)\b',
                r'\b(skill|development|course)\b'
            ],
            EventType.TRAINING: [
                r'\b(training|course|lesson)\b',
                r'\b(education|learning|study)\b',
                r'\b(certification|certificate)\b'
            ],
            EventType.SOCIAL: [
                r'\b(party|celebration|event)\b',
                r'\b(social|gathering|get together)\b',
                r'\b(fun|entertainment|leisure)\b'
            ]
        }
        
        # Time patterns
        self.time_patterns = [
            r'\b(today|tomorrow|yesterday)\b',
            r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'\b(\d{1,2}:\d{2})\b',  # Time like 14:30
            r'\b(\d{1,2}am|\d{1,2}pm)\b',  # Time like 2pm
            r'\b(\d{1,2}/\d{1,2}/\d{4})\b',  # Date like 12/25/2024
            r'\b(\d{1,2}-\d{1,2}-\d{4})\b',  # Date like 25-12-2024
            r'\b(\d{4}-\d{1,2}-\d{1,2})\b',  # Date like 2024-12-25
        ]
        
        # Duration patterns
        self.duration_patterns = [
            r'\b(\d+)\s*(minute|min|hour|hr|day|week|month)\b',
            r'\b(half hour|30 min|1 hour|2 hours)\b',
            r'\b(all day|full day|morning|afternoon|evening)\b'
        ]
    
    def create_event_from_message(self, message_content: str, created_by: str, 
                                 chat_id: str = None, message_id: str = None) -> Optional[ChatEvent]:
        """Create event from chat message"""
        try:
            # Analyze message for event information
            event_info = self._analyze_message_for_event(message_content)
            
            if not event_info:
                return None
            
            # Create event
            event_id = str(uuid.uuid4())
            event = ChatEvent(
                event_id=event_id,
                title=event_info['title'],
                description=event_info['description'],
                event_type=event_info['event_type'],
                status=EventStatus.DRAFT,
                priority=event_info['priority'],
                created_by=created_by,
                created_at=datetime.now(),
                scheduled_at=event_info['scheduled_at'],
                duration=event_info['duration'],
                location=event_info.get('location'),
                attendees=event_info.get('attendees', []),
                chat_id=chat_id,
                message_id=message_id,
                tags=event_info.get('tags', [])
            )
            
            # Store event
            self.events[event_id] = event
            
            # Queue for processing
            self.event_queue.put({
                'action': 'create',
                'event': event
            })
            
            logger.info(f"Event created from message: {event_id}")
            return event
            
        except Exception as e:
            logger.error(f"Error creating event from message: {str(e)}")
            return None
    
    def create_manual_event(self, title: str, description: str, event_type: EventType,
                          scheduled_at: datetime, duration: int, created_by: str,
                          attendees: List[str] = None, location: str = None,
                          priority: EventPriority = EventPriority.MEDIUM) -> Optional[ChatEvent]:
        """Create event manually"""
        try:
            event_id = str(uuid.uuid4())
            event = ChatEvent(
                event_id=event_id,
                title=title,
                description=description,
                event_type=event_type,
                status=EventStatus.SCHEDULED,
                priority=priority,
                created_by=created_by,
                created_at=datetime.now(),
                scheduled_at=scheduled_at,
                duration=duration,
                location=location,
                attendees=attendees or [],
                tags=[]
            )
            
            # Store event
            self.events[event_id] = event
            
            # Queue for processing
            self.event_queue.put({
                'action': 'create',
                'event': event
            })
            
            logger.info(f"Manual event created: {event_id}")
            return event
            
        except Exception as e:
            logger.error(f"Error creating manual event: {str(e)}")
            return None
    
    def update_event(self, event_id: str, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update an event"""
        try:
            if event_id not in self.events:
                return False
            
            event = self.events[event_id]
            
            # Check permissions
            if event.created_by != user_id and user_id not in event.attendees:
                return False
            
            # Update fields
            for field, value in updates.items():
                if hasattr(event, field):
                    setattr(event, field, value)
            
            event.updated_at = datetime.now()
            
            # Queue for processing
            self.event_queue.put({
                'action': 'update',
                'event': event
            })
            
            logger.info(f"Event updated: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating event: {str(e)}")
            return False
    
    def delete_event(self, event_id: str, user_id: str) -> bool:
        """Delete an event"""
        try:
            if event_id not in self.events:
                return False
            
            event = self.events[event_id]
            
            # Check permissions
            if event.created_by != user_id:
                return False
            
            # Update status
            event.status = EventStatus.CANCELLED
            
            # Queue for processing
            self.event_queue.put({
                'action': 'delete',
                'event': event
            })
            
            logger.info(f"Event deleted: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting event: {str(e)}")
            return False
    
    def get_user_events(self, user_id: str, start_date: datetime = None, 
                       end_date: datetime = None) -> List[ChatEvent]:
        """Get events for a user"""
        try:
            user_events = []
            
            for event in self.events.values():
                # Check if user is involved in event
                if (event.created_by == user_id or 
                    user_id in event.attendees):
                    
                    # Filter by date range if provided
                    if start_date and event.scheduled_at < start_date:
                        continue
                    if end_date and event.scheduled_at > end_date:
                        continue
                    
                    user_events.append(event)
            
            # Sort by scheduled time
            user_events.sort(key=lambda x: x.scheduled_at)
            
            return user_events
            
        except Exception as e:
            logger.error(f"Error getting user events: {str(e)}")
            return []
    
    def get_event(self, event_id: str, user_id: str) -> Optional[ChatEvent]:
        """Get specific event"""
        try:
            if event_id not in self.events:
                return None
            
            event = self.events[event_id]
            
            # Check permissions
            if (event.created_by != user_id and 
                user_id not in event.attendees):
                return None
            
            return event
            
        except Exception as e:
            logger.error(f"Error getting event: {str(e)}")
            return None
    
    def search_events(self, user_id: str, query: str) -> List[ChatEvent]:
        """Search events"""
        try:
            results = []
            query_lower = query.lower()
            
            for event in self.events.values():
                # Check if user is involved in event
                if (event.created_by == user_id or 
                    user_id in event.attendees):
                    
                    # Search in title, description, and tags
                    if (query_lower in event.title.lower() or 
                        query_lower in event.description.lower() or
                        any(query_lower in tag.lower() for tag in event.tags)):
                        results.append(event)
            
            # Sort by scheduled time
            results.sort(key=lambda x: x.scheduled_at)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching events: {str(e)}")
            return []
    
    def add_event_reminder(self, event_id: str, user_id: str, 
                          reminder_minutes: List[int]) -> bool:
        """Add reminders to an event"""
        try:
            if event_id not in self.events:
                return False
            
            event = self.events[event_id]
            
            # Check permissions
            if (event.created_by != user_id and 
                user_id not in event.attendees):
                return False
            
            # Add reminders
            for minutes in reminder_minutes:
                reminder_time = event.scheduled_at - timedelta(minutes=minutes)
                
                reminder_id = str(uuid.uuid4())
                reminder = EventReminder(
                    reminder_id=reminder_id,
                    event_id=event_id,
                    user_id=user_id,
                    reminder_time=reminder_time,
                    message=f"Reminder: {event.title} in {minutes} minutes"
                )
                
                self.reminders[reminder_id] = reminder
            
            # Update event
            event.reminder_minutes.extend(reminder_minutes)
            
            logger.info(f"Reminders added to event: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding event reminders: {str(e)}")
            return False
    
    def get_upcoming_events(self, user_id: str, days: int = 7) -> List[ChatEvent]:
        """Get upcoming events for a user"""
        try:
            upcoming_events = []
            end_date = datetime.now() + timedelta(days=days)
            
            for event in self.events.values():
                # Check if user is involved in event
                if (event.created_by == user_id or 
                    user_id in event.attendees):
                    
                    # Check if event is upcoming
                    if (event.scheduled_at > datetime.now() and 
                        event.scheduled_at <= end_date and
                        event.status in [EventStatus.SCHEDULED, EventStatus.IN_PROGRESS]):
                        upcoming_events.append(event)
            
            # Sort by scheduled time
            upcoming_events.sort(key=lambda x: x.scheduled_at)
            
            return upcoming_events
            
        except Exception as e:
            logger.error(f"Error getting upcoming events: {str(e)}")
            return []
    
    def _analyze_message_for_event(self, message_content: str) -> Optional[Dict[str, Any]]:
        """Analyze message content for event information"""
        try:
            content_lower = message_content.lower()
            
            # Detect event type
            event_type = self._detect_event_type(content_lower)
            if not event_type:
                return None
            
            # Extract title
            title = self._extract_title(message_content, event_type)
            
            # Extract description
            description = self._extract_description(message_content)
            
            # Extract scheduled time
            scheduled_at = self._extract_scheduled_time(message_content)
            if not scheduled_at:
                scheduled_at = datetime.now() + timedelta(hours=1)  # Default to 1 hour from now
            
            # Extract duration
            duration = self._extract_duration(message_content)
            if not duration:
                duration = 60  # Default to 1 hour
            
            # Extract location
            location = self._extract_location(message_content)
            
            # Extract attendees
            attendees = self._extract_attendees(message_content)
            
            # Determine priority
            priority = self._determine_priority(content_lower)
            
            # Extract tags
            tags = self._extract_tags(message_content)
            
            return {
                'title': title,
                'description': description,
                'event_type': event_type,
                'scheduled_at': scheduled_at,
                'duration': duration,
                'location': location,
                'attendees': attendees,
                'priority': priority,
                'tags': tags
            }
            
        except Exception as e:
            logger.error(f"Error analyzing message for event: {str(e)}")
            return None
    
    def _detect_event_type(self, content: str) -> Optional[EventType]:
        """Detect event type from content"""
        try:
            for event_type, patterns in self.event_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return event_type
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting event type: {str(e)}")
            return None
    
    def _extract_title(self, content: str, event_type: EventType) -> str:
        """Extract event title from content"""
        try:
            # Simple title extraction
            if event_type == EventType.MEETING:
                return "Meeting"
            elif event_type == EventType.CALL:
                return "Call"
            elif event_type == EventType.DEADLINE:
                return "Deadline"
            elif event_type == EventType.REMINDER:
                return "Reminder"
            elif event_type == EventType.TASK:
                return "Task"
            elif event_type == EventType.APPOINTMENT:
                return "Appointment"
            elif event_type == EventType.CONFERENCE:
                return "Conference"
            elif event_type == EventType.WORKSHOP:
                return "Workshop"
            elif event_type == EventType.TRAINING:
                return "Training"
            elif event_type == EventType.SOCIAL:
                return "Social Event"
            else:
                return "Event"
            
        except Exception as e:
            logger.error(f"Error extracting title: {str(e)}")
            return "Event"
    
    def _extract_description(self, content: str) -> str:
        """Extract event description from content"""
        try:
            # Use the original content as description
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error extracting description: {str(e)}")
            return ""
    
    def _extract_scheduled_time(self, content: str) -> Optional[datetime]:
        """Extract scheduled time from content"""
        try:
            # Look for time patterns
            for pattern in self.time_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    # Parse the matched time
                    time_str = match.group(1)
                    return self._parse_time_string(time_str)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting scheduled time: {str(e)}")
            return None
    
    def _parse_time_string(self, time_str: str) -> Optional[datetime]:
        """Parse time string to datetime"""
        try:
            # This would implement time parsing logic
            # For now, return a default time
            return datetime.now() + timedelta(hours=1)
            
        except Exception as e:
            logger.error(f"Error parsing time string: {str(e)}")
            return None
    
    def _extract_duration(self, content: str) -> Optional[int]:
        """Extract duration from content"""
        try:
            # Look for duration patterns
            for pattern in self.duration_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    # Parse duration
                    duration_str = match.group(1)
                    return self._parse_duration_string(duration_str)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting duration: {str(e)}")
            return None
    
    def _parse_duration_string(self, duration_str: str) -> Optional[int]:
        """Parse duration string to minutes"""
        try:
            # This would implement duration parsing logic
            # For now, return default duration
            return 60  # 1 hour
            
        except Exception as e:
            logger.error(f"Error parsing duration string: {str(e)}")
            return None
    
    def _extract_location(self, content: str) -> Optional[str]:
        """Extract location from content"""
        try:
            # Look for location patterns
            location_patterns = [
                r'\b(at|in|room|office|building)\s+([A-Za-z0-9\s]+)',
                r'\b(conference room|meeting room|boardroom)\b',
                r'\b(zoom|teams|google meet|skype)\b'
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return match.group(0).strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting location: {str(e)}")
            return None
    
    def _extract_attendees(self, content: str) -> List[str]:
        """Extract attendees from content"""
        try:
            attendees = []
            
            # Look for @mentions
            mention_pattern = r'@(\w+)'
            mentions = re.findall(mention_pattern, content)
            attendees.extend(mentions)
            
            # Look for "with" patterns
            with_pattern = r'\bwith\s+([A-Za-z\s,]+)'
            match = re.search(with_pattern, content, re.IGNORECASE)
            if match:
                with_attendees = [name.strip() for name in match.group(1).split(',')]
                attendees.extend(with_attendees)
            
            return attendees
            
        except Exception as e:
            logger.error(f"Error extracting attendees: {str(e)}")
            return []
    
    def _determine_priority(self, content: str) -> EventPriority:
        """Determine event priority from content"""
        try:
            if any(word in content for word in ['urgent', 'asap', 'immediately', 'critical']):
                return EventPriority.URGENT
            elif any(word in content for word in ['important', 'high', 'priority']):
                return EventPriority.HIGH
            elif any(word in content for word in ['low', 'when possible', 'sometime']):
                return EventPriority.LOW
            else:
                return EventPriority.MEDIUM
            
        except Exception as e:
            logger.error(f"Error determining priority: {str(e)}")
            return EventPriority.MEDIUM
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content"""
        try:
            tags = []
            
            # Look for hashtags
            hashtag_pattern = r'#(\w+)'
            hashtags = re.findall(hashtag_pattern, content)
            tags.extend(hashtags)
            
            return tags
            
        except Exception as e:
            logger.error(f"Error extracting tags: {str(e)}")
            return []
    
    def _handle_event_processing(self, event_data: Dict[str, Any]):
        """Handle event processing"""
        try:
            action = event_data.get('action')
            event = event_data.get('event')
            
            if action == 'create':
                self._process_event_creation(event)
            elif action == 'update':
                self._process_event_update(event)
            elif action == 'delete':
                self._process_event_deletion(event)
            elif action == 'reminder':
                self._process_event_reminder(event)
            
        except Exception as e:
            logger.error(f"Error handling event processing: {str(e)}")
    
    def _process_event_creation(self, event: ChatEvent):
        """Process event creation"""
        try:
            # Set status to scheduled
            event.status = EventStatus.SCHEDULED
            
            # Create default reminders
            self._create_default_reminders(event)
            
            # Notify attendees
            self._notify_event_created(event)
            
            logger.info(f"Event creation processed: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Error processing event creation: {str(e)}")
    
    def _process_event_update(self, event: ChatEvent):
        """Process event update"""
        try:
            # Notify attendees of changes
            self._notify_event_updated(event)
            
            logger.info(f"Event update processed: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Error processing event update: {str(e)}")
    
    def _process_event_deletion(self, event: ChatEvent):
        """Process event deletion"""
        try:
            # Cancel all reminders
            self._cancel_event_reminders(event)
            
            # Notify attendees
            self._notify_event_cancelled(event)
            
            logger.info(f"Event deletion processed: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Error processing event deletion: {str(e)}")
    
    def _process_event_reminder(self, event: ChatEvent):
        """Process event reminder"""
        try:
            # Send reminder notifications
            self._send_reminder_notifications(event)
            
            logger.info(f"Event reminder processed: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Error processing event reminder: {str(e)}")
    
    def _create_default_reminders(self, event: ChatEvent):
        """Create default reminders for event"""
        try:
            # Default reminders: 15 minutes, 1 hour, 1 day
            default_reminders = [15, 60, 1440]  # minutes
            
            for minutes in default_reminders:
                reminder_time = event.scheduled_at - timedelta(minutes=minutes)
                
                reminder_id = str(uuid.uuid4())
                reminder = EventReminder(
                    reminder_id=reminder_id,
                    event_id=event.event_id,
                    user_id=event.created_by,
                    reminder_time=reminder_time,
                    message=f"Reminder: {event.title} in {minutes} minutes"
                )
                
                self.reminders[reminder_id] = reminder
            
        except Exception as e:
            logger.error(f"Error creating default reminders: {str(e)}")
    
    def _cancel_event_reminders(self, event: ChatEvent):
        """Cancel all reminders for event"""
        try:
            # Remove all reminders for this event
            reminders_to_remove = [
                reminder_id for reminder_id, reminder in self.reminders.items()
                if reminder.event_id == event.event_id
            ]
            
            for reminder_id in reminders_to_remove:
                del self.reminders[reminder_id]
            
        except Exception as e:
            logger.error(f"Error cancelling event reminders: {str(e)}")
    
    def _notify_event_created(self, event: ChatEvent):
        """Notify attendees that event was created"""
        try:
            # This would send notifications to attendees
            logger.info(f"Event created notification sent for {event.event_id}")
            
        except Exception as e:
            logger.error(f"Error notifying event created: {str(e)}")
    
    def _notify_event_updated(self, event: ChatEvent):
        """Notify attendees that event was updated"""
        try:
            # This would send notifications to attendees
            logger.info(f"Event updated notification sent for {event.event_id}")
            
        except Exception as e:
            logger.error(f"Error notifying event updated: {str(e)}")
    
    def _notify_event_cancelled(self, event: ChatEvent):
        """Notify attendees that event was cancelled"""
        try:
            # This would send notifications to attendees
            logger.info(f"Event cancelled notification sent for {event.event_id}")
            
        except Exception as e:
            logger.error(f"Error notifying event cancelled: {str(e)}")
    
    def _send_reminder_notifications(self, event: ChatEvent):
        """Send reminder notifications for event"""
        try:
            # This would send reminder notifications
            logger.info(f"Reminder notifications sent for {event.event_id}")
            
        except Exception as e:
            logger.error(f"Error sending reminder notifications: {str(e)}")
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get event creation analytics"""
        try:
            return {
                'total_events': len(self.events),
                'events_by_type': {
                    event_type.value: len([e for e in self.events.values() if e.event_type == event_type])
                    for event_type in EventType
                },
                'events_by_status': {
                    status.value: len([e for e in self.events.values() if e.status == status])
                    for status in EventStatus
                },
                'total_reminders': len(self.reminders),
                'upcoming_events': len([e for e in self.events.values() if e.scheduled_at > datetime.now()])
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}

# Global event creation system instance
event_creation_system = EventCreationSystem()
