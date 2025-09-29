# Internal Chat System
# Real-time chat system with private chats, group chats, and department channels

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
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import base64
import re
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    VOICE_MESSAGE = "voice_message"
    FILE = "file"
    SYSTEM = "system"
    CALL = "call"
    EVENT = "event"

class ChatType(Enum):
    PRIVATE = "private"
    GROUP = "group"
    CHANNEL = "channel"
    DEPARTMENT = "department"
    PROJECT = "project"

class MessageStatus(Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    PENDING = "pending"

class UserStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"
    BUSY = "busy"
    DO_NOT_DISTURB = "do_not_disturb"

@dataclass
class ChatUser:
    user_id: str
    username: str
    display_name: str
    email: str
    avatar_url: Optional[str] = None
    status: UserStatus = UserStatus.OFFLINE
    last_seen: Optional[datetime] = None
    is_typing: bool = False
    typing_in: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)

@dataclass
class ChatMessage:
    message_id: str
    chat_id: str
    sender_id: str
    content: str
    message_type: MessageType
    timestamp: datetime
    status: MessageStatus = MessageStatus.SENT
    reply_to: Optional[str] = None
    edited: bool = False
    edited_at: Optional[datetime] = None
    reactions: Dict[str, List[str]] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_encrypted: bool = False
    encryption_key: Optional[str] = None

@dataclass
class ChatRoom:
    room_id: str
    name: str
    description: Optional[str] = None
    chat_type: ChatType = ChatType.PRIVATE
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    participants: List[str] = field(default_factory=list)
    admins: List[str] = field(default_factory=list)
    moderators: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    is_archived: bool = False
    is_private: bool = False
    department_id: Optional[str] = None
    project_id: Optional[str] = None
    last_message: Optional[ChatMessage] = None
    unread_count: Dict[str, int] = field(default_factory=dict)
    message_count: int = 0

@dataclass
class ChatChannel:
    channel_id: str
    name: str
    description: Optional[str] = None
    department_id: str
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    members: List[str] = field(default_factory=list)
    admins: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    is_archived: bool = False
    is_public: bool = True
    topic: Optional[str] = None
    last_message: Optional[ChatMessage] = None
    unread_count: Dict[str, int] = field(default_factory=dict)
    message_count: int = 0

class ChatSystem:
    """
    Internal Chat System
    Handles real-time messaging, private chats, group chats, and department channels
    """
    
    def __init__(self):
        self.users: Dict[str, ChatUser] = {}
        self.rooms: Dict[str, ChatRoom] = {}
        self.channels: Dict[str, ChatChannel] = {}
        self.messages: Dict[str, List[ChatMessage]] = {}
        self.typing_users: Dict[str, Set[str]] = {}
        self.online_users: Set[str] = set()
        
        # Real-time communication
        self.websocket_connections: Dict[str, Any] = {}
        self.message_queue = queue.Queue()
        self.is_processing = True
        
        # Start background processing
        self._start_message_processing()
        
        # Initialize default channels
        self._initialize_default_channels()
    
    def _start_message_processing(self):
        """Start background message processing"""
        self.is_processing = True
        
        # Start processing thread
        thread = threading.Thread(target=self._process_messages, daemon=True)
        thread.start()
        
        logger.info("Chat system message processing started")
    
    def _process_messages(self):
        """Process messages in background"""
        while self.is_processing:
            try:
                message = self.message_queue.get(timeout=1)
                self._handle_message(message)
                self.message_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
    
    def _initialize_default_channels(self):
        """Initialize default department channels"""
        default_channels = [
            {
                'name': 'General',
                'description': 'General company discussions',
                'department_id': 'all',
                'is_public': True
            },
            {
                'name': 'Announcements',
                'description': 'Company announcements and updates',
                'department_id': 'all',
                'is_public': True
            },
            {
                'name': 'IT Support',
                'description': 'IT support and technical discussions',
                'department_id': 'it',
                'is_public': True
            },
            {
                'name': 'HR',
                'description': 'Human resources discussions',
                'department_id': 'hr',
                'is_public': True
            },
            {
                'name': 'Sales',
                'description': 'Sales team discussions',
                'department_id': 'sales',
                'is_public': True
            },
            {
                'name': 'Marketing',
                'description': 'Marketing team discussions',
                'department_id': 'marketing',
                'is_public': True
            }
        ]
        
        for channel_data in default_channels:
            self.create_channel(
                name=channel_data['name'],
                description=channel_data['description'],
                department_id=channel_data['department_id'],
                created_by='system',
                is_public=channel_data['is_public']
            )
    
    def register_user(self, user_id: str, username: str, display_name: str, email: str, 
                     avatar_url: str = None, permissions: List[str] = None) -> ChatUser:
        """Register a new user in the chat system"""
        try:
            user = ChatUser(
                user_id=user_id,
                username=username,
                display_name=display_name,
                email=email,
                avatar_url=avatar_url,
                permissions=permissions or []
            )
            
            self.users[user_id] = user
            logger.info(f"User registered: {username} ({user_id})")
            
            return user
            
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            raise
    
    def set_user_online(self, user_id: str) -> bool:
        """Set user as online"""
        try:
            if user_id in self.users:
                self.users[user_id].status = UserStatus.ONLINE
                self.users[user_id].last_seen = datetime.now()
                self.online_users.add(user_id)
                
                # Notify other users
                self._broadcast_user_status(user_id, UserStatus.ONLINE)
                
                logger.info(f"User set online: {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error setting user online: {str(e)}")
            return False
    
    def set_user_offline(self, user_id: str) -> bool:
        """Set user as offline"""
        try:
            if user_id in self.users:
                self.users[user_id].status = UserStatus.OFFLINE
                self.users[user_id].last_seen = datetime.now()
                self.online_users.discard(user_id)
                
                # Notify other users
                self._broadcast_user_status(user_id, UserStatus.OFFLINE)
                
                logger.info(f"User set offline: {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error setting user offline: {str(e)}")
            return False
    
    def set_user_typing(self, user_id: str, chat_id: str, is_typing: bool) -> bool:
        """Set user typing status"""
        try:
            if user_id in self.users:
                self.users[user_id].is_typing = is_typing
                self.users[user_id].typing_in = chat_id if is_typing else None
                
                if is_typing:
                    if chat_id not in self.typing_users:
                        self.typing_users[chat_id] = set()
                    self.typing_users[chat_id].add(user_id)
                else:
                    if chat_id in self.typing_users:
                        self.typing_users[chat_id].discard(user_id)
                
                # Broadcast typing status
                self._broadcast_typing_status(user_id, chat_id, is_typing)
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error setting user typing: {str(e)}")
            return False
    
    def create_private_chat(self, user1_id: str, user2_id: str) -> Optional[ChatRoom]:
        """Create a private chat between two users"""
        try:
            # Check if private chat already exists
            existing_chat = self._find_private_chat(user1_id, user2_id)
            if existing_chat:
                return existing_chat
            
            # Create new private chat
            room_id = str(uuid.uuid4())
            room = ChatRoom(
                room_id=room_id,
                name=f"Private Chat",
                chat_type=ChatType.PRIVATE,
                created_by=user1_id,
                participants=[user1_id, user2_id],
                is_private=True
            )
            
            self.rooms[room_id] = room
            self.messages[room_id] = []
            
            logger.info(f"Private chat created: {room_id} between {user1_id} and {user2_id}")
            return room
            
        except Exception as e:
            logger.error(f"Error creating private chat: {str(e)}")
            return None
    
    def create_group_chat(self, name: str, description: str, created_by: str, 
                         participants: List[str], is_private: bool = False) -> Optional[ChatRoom]:
        """Create a group chat"""
        try:
            room_id = str(uuid.uuid4())
            room = ChatRoom(
                room_id=room_id,
                name=name,
                description=description,
                chat_type=ChatType.GROUP,
                created_by=created_by,
                participants=participants,
                admins=[created_by],
                is_private=is_private
            )
            
            self.rooms[room_id] = room
            self.messages[room_id] = []
            
            logger.info(f"Group chat created: {room_id} by {created_by}")
            return room
            
        except Exception as e:
            logger.error(f"Error creating group chat: {str(e)}")
            return None
    
    def create_channel(self, name: str, description: str, department_id: str, 
                      created_by: str, is_public: bool = True) -> Optional[ChatChannel]:
        """Create a department channel"""
        try:
            channel_id = str(uuid.uuid4())
            channel = ChatChannel(
                channel_id=channel_id,
                name=name,
                description=description,
                department_id=department_id,
                created_by=created_by,
                is_public=is_public,
                admins=[created_by]
            )
            
            self.channels[channel_id] = channel
            self.messages[channel_id] = []
            
            logger.info(f"Channel created: {channel_id} in department {department_id}")
            return channel
            
        except Exception as e:
            logger.error(f"Error creating channel: {str(e)}")
            return None
    
    def send_message(self, chat_id: str, sender_id: str, content: str, 
                    message_type: MessageType = MessageType.TEXT, 
                    reply_to: str = None, attachments: List[Dict[str, Any]] = None) -> Optional[ChatMessage]:
        """Send a message to a chat"""
        try:
            # Validate chat exists
            if chat_id not in self.rooms and chat_id not in self.channels:
                logger.error(f"Chat not found: {chat_id}")
                return None
            
            # Validate sender is participant
            if not self._is_participant(chat_id, sender_id):
                logger.error(f"User {sender_id} is not a participant in chat {chat_id}")
                return None
            
            # Create message
            message = ChatMessage(
                message_id=str(uuid.uuid4()),
                chat_id=chat_id,
                sender_id=sender_id,
                content=content,
                message_type=message_type,
                timestamp=datetime.now(),
                reply_to=reply_to,
                attachments=attachments or []
            )
            
            # Store message
            if chat_id not in self.messages:
                self.messages[chat_id] = []
            self.messages[chat_id].append(message)
            
            # Update chat metadata
            self._update_chat_metadata(chat_id, message)
            
            # Queue for processing
            self.message_queue.put(message)
            
            logger.info(f"Message sent: {message.message_id} in chat {chat_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return None
    
    def send_voice_message(self, chat_id: str, sender_id: str, audio_data: bytes, 
                          duration: float) -> Optional[ChatMessage]:
        """Send a voice message"""
        try:
            # Save audio file
            audio_id = str(uuid.uuid4())
            audio_path = self._save_audio_file(audio_id, audio_data)
            
            # Create message with audio attachment
            message = self.send_message(
                chat_id=chat_id,
                sender_id=sender_id,
                content="Voice message",
                message_type=MessageType.VOICE_MESSAGE,
                attachments=[{
                    'type': 'audio',
                    'id': audio_id,
                    'path': audio_path,
                    'duration': duration,
                    'size': len(audio_data)
                }]
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Error sending voice message: {str(e)}")
            return None
    
    def edit_message(self, message_id: str, new_content: str, editor_id: str) -> bool:
        """Edit a message"""
        try:
            # Find message
            message = self._find_message(message_id)
            if not message:
                return False
            
            # Check permissions
            if message.sender_id != editor_id and not self._is_admin(message.chat_id, editor_id):
                return False
            
            # Update message
            message.content = new_content
            message.edited = True
            message.edited_at = datetime.now()
            
            # Broadcast edit
            self._broadcast_message_edit(message)
            
            logger.info(f"Message edited: {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error editing message: {str(e)}")
            return False
    
    def delete_message(self, message_id: str, deleter_id: str) -> bool:
        """Delete a message"""
        try:
            # Find message
            message = self._find_message(message_id)
            if not message:
                return False
            
            # Check permissions
            if message.sender_id != deleter_id and not self._is_admin(message.chat_id, deleter_id):
                return False
            
            # Remove message
            chat_id = message.chat_id
            if chat_id in self.messages:
                self.messages[chat_id] = [m for m in self.messages[chat_id] if m.message_id != message_id]
            
            # Broadcast deletion
            self._broadcast_message_deletion(message_id, chat_id)
            
            logger.info(f"Message deleted: {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting message: {str(e)}")
            return False
    
    def add_reaction(self, message_id: str, user_id: str, emoji: str) -> bool:
        """Add reaction to a message"""
        try:
            message = self._find_message(message_id)
            if not message:
                return False
            
            if emoji not in message.reactions:
                message.reactions[emoji] = []
            
            if user_id not in message.reactions[emoji]:
                message.reactions[emoji].append(user_id)
                
                # Broadcast reaction
                self._broadcast_reaction(message_id, user_id, emoji, 'add')
                
                logger.info(f"Reaction added: {emoji} to message {message_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding reaction: {str(e)}")
            return False
    
    def remove_reaction(self, message_id: str, user_id: str, emoji: str) -> bool:
        """Remove reaction from a message"""
        try:
            message = self._find_message(message_id)
            if not message:
                return False
            
            if emoji in message.reactions and user_id in message.reactions[emoji]:
                message.reactions[emoji].remove(user_id)
                
                # Clean up empty reactions
                if not message.reactions[emoji]:
                    del message.reactions[emoji]
                
                # Broadcast reaction removal
                self._broadcast_reaction(message_id, user_id, emoji, 'remove')
                
                logger.info(f"Reaction removed: {emoji} from message {message_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing reaction: {str(e)}")
            return False
    
    def mark_message_read(self, message_id: str, user_id: str) -> bool:
        """Mark a message as read"""
        try:
            message = self._find_message(message_id)
            if not message:
                return False
            
            # Update message status
            if message.status != MessageStatus.READ:
                message.status = MessageStatus.READ
                
                # Broadcast read status
                self._broadcast_read_status(message_id, user_id)
                
                logger.info(f"Message marked as read: {message_id} by {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking message as read: {str(e)}")
            return False
    
    def get_chat_messages(self, chat_id: str, user_id: str, limit: int = 50, 
                         offset: int = 0) -> List[ChatMessage]:
        """Get messages from a chat"""
        try:
            # Check permissions
            if not self._is_participant(chat_id, user_id):
                return []
            
            if chat_id not in self.messages:
                return []
            
            messages = self.messages[chat_id]
            start_idx = max(0, len(messages) - offset - limit)
            end_idx = len(messages) - offset
            
            return messages[start_idx:end_idx]
            
        except Exception as e:
            logger.error(f"Error getting chat messages: {str(e)}")
            return []
    
    def get_user_chats(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all chats for a user"""
        try:
            user_chats = []
            
            # Get rooms where user is participant
            for room_id, room in self.rooms.items():
                if user_id in room.participants:
                    user_chats.append({
                        'id': room_id,
                        'name': room.name,
                        'type': room.chat_type.value,
                        'last_message': room.last_message,
                        'unread_count': room.unread_count.get(user_id, 0),
                        'participants': len(room.participants)
                    })
            
            # Get channels where user is member
            for channel_id, channel in self.channels.items():
                if user_id in channel.members or channel.is_public:
                    user_chats.append({
                        'id': channel_id,
                        'name': channel.name,
                        'type': 'channel',
                        'department': channel.department_id,
                        'last_message': channel.last_message,
                        'unread_count': channel.unread_count.get(user_id, 0),
                        'members': len(channel.members)
                    })
            
            return user_chats
            
        except Exception as e:
            logger.error(f"Error getting user chats: {str(e)}")
            return []
    
    def search_messages(self, user_id: str, query: str, chat_id: str = None) -> List[ChatMessage]:
        """Search messages"""
        try:
            results = []
            query_lower = query.lower()
            
            # Search in specific chat or all user chats
            if chat_id:
                chats_to_search = [chat_id] if self._is_participant(chat_id, user_id) else []
            else:
                chats_to_search = self._get_user_chats(user_id)
            
            for chat in chats_to_search:
                if chat in self.messages:
                    for message in self.messages[chat]:
                        if query_lower in message.content.lower():
                            results.append(message)
            
            # Sort by timestamp (newest first)
            results.sort(key=lambda x: x.timestamp, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching messages: {str(e)}")
            return []
    
    def _find_private_chat(self, user1_id: str, user2_id: str) -> Optional[ChatRoom]:
        """Find existing private chat between two users"""
        for room in self.rooms.values():
            if (room.chat_type == ChatType.PRIVATE and 
                user1_id in room.participants and 
                user2_id in room.participants and 
                len(room.participants) == 2):
                return room
        return None
    
    def _is_participant(self, chat_id: str, user_id: str) -> bool:
        """Check if user is participant in chat"""
        if chat_id in self.rooms:
            return user_id in self.rooms[chat_id].participants
        elif chat_id in self.channels:
            return user_id in self.channels[chat_id].members or self.channels[chat_id].is_public
        return False
    
    def _is_admin(self, chat_id: str, user_id: str) -> bool:
        """Check if user is admin in chat"""
        if chat_id in self.rooms:
            return user_id in self.rooms[chat_id].admins
        elif chat_id in self.channels:
            return user_id in self.channels[chat_id].admins
        return False
    
    def _find_message(self, message_id: str) -> Optional[ChatMessage]:
        """Find message by ID"""
        for messages in self.messages.values():
            for message in messages:
                if message.message_id == message_id:
                    return message
        return None
    
    def _get_user_chats(self, user_id: str) -> List[str]:
        """Get all chat IDs where user is participant"""
        chats = []
        
        # Add rooms
        for room_id, room in self.rooms.items():
            if user_id in room.participants:
                chats.append(room_id)
        
        # Add channels
        for channel_id, channel in self.channels.items():
            if user_id in channel.members or channel.is_public:
                chats.append(channel_id)
        
        return chats
    
    def _update_chat_metadata(self, chat_id: str, message: ChatMessage):
        """Update chat metadata with new message"""
        if chat_id in self.rooms:
            room = self.rooms[chat_id]
            room.last_message = message
            room.message_count += 1
            room.updated_at = datetime.now()
        elif chat_id in self.channels:
            channel = self.channels[chat_id]
            channel.last_message = message
            channel.message_count += 1
            channel.updated_at = datetime.now()
    
    def _save_audio_file(self, audio_id: str, audio_data: bytes) -> str:
        """Save audio file and return path"""
        try:
            # Create audio directory
            audio_dir = Path("uploads/audio")
            audio_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file
            audio_path = audio_dir / f"{audio_id}.wav"
            with open(audio_path, 'wb') as f:
                f.write(audio_data)
            
            return str(audio_path)
            
        except Exception as e:
            logger.error(f"Error saving audio file: {str(e)}")
            return ""
    
    def _handle_message(self, message: ChatMessage):
        """Handle message processing"""
        try:
            # Broadcast message to participants
            self._broadcast_message(message)
            
            # Update unread counts
            self._update_unread_counts(message)
            
            # Process message content
            self._process_message_content(message)
            
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
    
    def _broadcast_message(self, message: ChatMessage):
        """Broadcast message to all participants"""
        try:
            # Get participants
            participants = self._get_chat_participants(message.chat_id)
            
            # Broadcast to each participant
            for participant_id in participants:
                if participant_id in self.websocket_connections:
                    # Send via WebSocket
                    self._send_websocket_message(participant_id, {
                        'type': 'new_message',
                        'message': self._serialize_message(message)
                    })
            
        except Exception as e:
            logger.error(f"Error broadcasting message: {str(e)}")
    
    def _broadcast_user_status(self, user_id: str, status: UserStatus):
        """Broadcast user status change"""
        try:
            # Get all user's chats
            user_chats = self._get_user_chats(user_id)
            
            for chat_id in user_chats:
                participants = self._get_chat_participants(chat_id)
                
                for participant_id in participants:
                    if participant_id != user_id and participant_id in self.websocket_connections:
                        self._send_websocket_message(participant_id, {
                            'type': 'user_status',
                            'user_id': user_id,
                            'status': status.value
                        })
            
        except Exception as e:
            logger.error(f"Error broadcasting user status: {str(e)}")
    
    def _broadcast_typing_status(self, user_id: str, chat_id: str, is_typing: bool):
        """Broadcast typing status"""
        try:
            participants = self._get_chat_participants(chat_id)
            
            for participant_id in participants:
                if participant_id != user_id and participant_id in self.websocket_connections:
                    self._send_websocket_message(participant_id, {
                        'type': 'typing',
                        'user_id': user_id,
                        'chat_id': chat_id,
                        'is_typing': is_typing
                    })
            
        except Exception as e:
            logger.error(f"Error broadcasting typing status: {str(e)}")
    
    def _broadcast_message_edit(self, message: ChatMessage):
        """Broadcast message edit"""
        try:
            participants = self._get_chat_participants(message.chat_id)
            
            for participant_id in participants:
                if participant_id in self.websocket_connections:
                    self._send_websocket_message(participant_id, {
                        'type': 'message_edit',
                        'message': self._serialize_message(message)
                    })
            
        except Exception as e:
            logger.error(f"Error broadcasting message edit: {str(e)}")
    
    def _broadcast_message_deletion(self, message_id: str, chat_id: str):
        """Broadcast message deletion"""
        try:
            participants = self._get_chat_participants(chat_id)
            
            for participant_id in participants:
                if participant_id in self.websocket_connections:
                    self._send_websocket_message(participant_id, {
                        'type': 'message_delete',
                        'message_id': message_id,
                        'chat_id': chat_id
                    })
            
        except Exception as e:
            logger.error(f"Error broadcasting message deletion: {str(e)}")
    
    def _broadcast_reaction(self, message_id: str, user_id: str, emoji: str, action: str):
        """Broadcast reaction change"""
        try:
            message = self._find_message(message_id)
            if not message:
                return
            
            participants = self._get_chat_participants(message.chat_id)
            
            for participant_id in participants:
                if participant_id in self.websocket_connections:
                    self._send_websocket_message(participant_id, {
                        'type': 'reaction',
                        'message_id': message_id,
                        'user_id': user_id,
                        'emoji': emoji,
                        'action': action
                    })
            
        except Exception as e:
            logger.error(f"Error broadcasting reaction: {str(e)}")
    
    def _broadcast_read_status(self, message_id: str, user_id: str):
        """Broadcast read status"""
        try:
            message = self._find_message(message_id)
            if not message:
                return
            
            participants = self._get_chat_participants(message.chat_id)
            
            for participant_id in participants:
                if participant_id in self.websocket_connections:
                    self._send_websocket_message(participant_id, {
                        'type': 'message_read',
                        'message_id': message_id,
                        'user_id': user_id
                    })
            
        except Exception as e:
            logger.error(f"Error broadcasting read status: {str(e)}")
    
    def _get_chat_participants(self, chat_id: str) -> List[str]:
        """Get all participants in a chat"""
        if chat_id in self.rooms:
            return self.rooms[chat_id].participants
        elif chat_id in self.channels:
            return self.channels[chat_id].members
        return []
    
    def _update_unread_counts(self, message: ChatMessage):
        """Update unread counts for participants"""
        try:
            participants = self._get_chat_participants(message.chat_id)
            
            for participant_id in participants:
                if participant_id != message.sender_id:
                    if message.chat_id in self.rooms:
                        if participant_id not in self.rooms[message.chat_id].unread_count:
                            self.rooms[message.chat_id].unread_count[participant_id] = 0
                        self.rooms[message.chat_id].unread_count[participant_id] += 1
                    elif message.chat_id in self.channels:
                        if participant_id not in self.channels[message.chat_id].unread_count:
                            self.channels[message.chat_id].unread_count[participant_id] = 0
                        self.channels[message.chat_id].unread_count[participant_id] += 1
            
        except Exception as e:
            logger.error(f"Error updating unread counts: {str(e)}")
    
    def _process_message_content(self, message: ChatMessage):
        """Process message content for special features"""
        try:
            # Process mentions
            self._process_mentions(message)
            
            # Process hashtags
            self._process_hashtags(message)
            
            # Process links
            self._process_links(message)
            
        except Exception as e:
            logger.error(f"Error processing message content: {str(e)}")
    
    def _process_mentions(self, message: ChatMessage):
        """Process @mentions in message"""
        try:
            mention_pattern = r'@(\w+)'
            mentions = re.findall(mention_pattern, message.content)
            
            for mention in mentions:
                # Find user by username
                for user_id, user in self.users.items():
                    if user.username == mention:
                        # Notify mentioned user
                        self._notify_mention(user_id, message)
                        break
            
        except Exception as e:
            logger.error(f"Error processing mentions: {str(e)}")
    
    def _process_hashtags(self, message: ChatMessage):
        """Process #hashtags in message"""
        try:
            hashtag_pattern = r'#(\w+)'
            hashtags = re.findall(hashtag_pattern, message.content)
            
            for hashtag in hashtags:
                # Store hashtag for search
                self._store_hashtag(hashtag, message)
            
        except Exception as e:
            logger.error(f"Error processing hashtags: {str(e)}")
    
    def _process_links(self, message: ChatMessage):
        """Process links in message"""
        try:
            link_pattern = r'https?://[^\s]+'
            links = re.findall(link_pattern, message.content)
            
            for link in links:
                # Generate link preview
                self._generate_link_preview(link, message)
            
        except Exception as e:
            logger.error(f"Error processing links: {str(e)}")
    
    def _notify_mention(self, user_id: str, message: ChatMessage):
        """Notify user of mention"""
        try:
            if user_id in self.websocket_connections:
                self._send_websocket_message(user_id, {
                    'type': 'mention',
                    'message': self._serialize_message(message)
                })
            
        except Exception as e:
            logger.error(f"Error notifying mention: {str(e)}")
    
    def _store_hashtag(self, hashtag: str, message: ChatMessage):
        """Store hashtag for search"""
        try:
            # This would store in database for hashtag search
            pass
            
        except Exception as e:
            logger.error(f"Error storing hashtag: {str(e)}")
    
    def _generate_link_preview(self, link: str, message: ChatMessage):
        """Generate link preview"""
        try:
            # This would generate link preview metadata
            pass
            
        except Exception as e:
            logger.error(f"Error generating link preview: {str(e)}")
    
    def _send_websocket_message(self, user_id: str, data: Dict[str, Any]):
        """Send WebSocket message to user"""
        try:
            if user_id in self.websocket_connections:
                connection = self.websocket_connections[user_id]
                # Send via WebSocket connection
                # This would be implemented with actual WebSocket library
                pass
            
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {str(e)}")
    
    def _serialize_message(self, message: ChatMessage) -> Dict[str, Any]:
        """Serialize message for transmission"""
        try:
            return {
                'message_id': message.message_id,
                'chat_id': message.chat_id,
                'sender_id': message.sender_id,
                'content': message.content,
                'message_type': message.message_type.value,
                'timestamp': message.timestamp.isoformat(),
                'status': message.status.value,
                'reply_to': message.reply_to,
                'edited': message.edited,
                'edited_at': message.edited_at.isoformat() if message.edited_at else None,
                'reactions': message.reactions,
                'attachments': message.attachments,
                'metadata': message.metadata
            }
            
        except Exception as e:
            logger.error(f"Error serializing message: {str(e)}")
            return {}
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get chat system analytics"""
        try:
            return {
                'total_users': len(self.users),
                'online_users': len(self.online_users),
                'total_rooms': len(self.rooms),
                'total_channels': len(self.channels),
                'total_messages': sum(len(messages) for messages in self.messages.values()),
                'active_chats': len([room for room in self.rooms.values() if room.last_message and (datetime.now() - room.last_message.timestamp).days < 7]),
                'typing_users': sum(len(users) for users in self.typing_users.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}

# Global chat system instance
chat_system = ChatSystem()
