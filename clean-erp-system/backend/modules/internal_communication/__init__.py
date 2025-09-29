# Internal Communication Module
# Comprehensive internal communication system with chat, VOIP, and file sharing

from .chat_system import ChatSystem, ChatMessage, ChatRoom, ChatChannel
from .voip_system import VOIPSystem, CallSession, CallParticipant
from .file_sharing import FileSharingSystem, SharedFile
from .event_creation import EventCreationSystem, ChatEvent
from .communication_api import CommunicationAPI
from .communication_dashboard import CommunicationDashboard

__all__ = [
    'ChatSystem',
    'ChatMessage', 
    'ChatRoom',
    'ChatChannel',
    'VOIPSystem',
    'CallSession',
    'CallParticipant',
    'FileSharingSystem',
    'SharedFile',
    'EventCreationSystem',
    'ChatEvent',
    'CommunicationAPI',
    'CommunicationDashboard'
]
