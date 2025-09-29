# VOIP System
# Internal VOIP calling system with audio/video support

import asyncio
import json
import logging
import uuid
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import queue
import base64
import hashlib
import hmac
import os
from pathlib import Path
import wave
import struct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallType(Enum):
    AUDIO = "audio"
    VIDEO = "video"
    SCREEN_SHARE = "screen_share"
    GROUP = "group"

class CallStatus(Enum):
    INITIATING = "initiating"
    RINGING = "ringing"
    CONNECTED = "connected"
    ON_HOLD = "on_hold"
    ENDED = "ended"
    FAILED = "failed"
    BUSY = "busy"
    REJECTED = "rejected"

class CallQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class CallParticipant:
    user_id: str
    username: str
    display_name: str
    joined_at: datetime
    left_at: Optional[datetime] = None
    is_muted: bool = False
    is_video_enabled: bool = True
    is_speaking: bool = False
    audio_level: float = 0.0
    connection_quality: CallQuality = CallQuality.GOOD
    network_latency: float = 0.0
    packet_loss: float = 0.0

@dataclass
class CallSession:
    call_id: str
    caller_id: str
    call_type: CallType
    status: CallStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration: float = 0.0
    participants: List[CallParticipant] = field(default_factory=list)
    recording_enabled: bool = False
    recording_path: Optional[str] = None
    quality: CallQuality = CallQuality.GOOD
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CallSettings:
    user_id: str
    auto_answer: bool = False
    do_not_disturb: bool = False
    ringtone: str = "default"
    video_enabled: bool = True
    audio_enabled: bool = True
    max_participants: int = 10
    recording_enabled: bool = False
    quality_preference: CallQuality = CallQuality.GOOD

class VOIPSystem:
    """
    VOIP System
    Handles audio/video calls, screen sharing, and group calls
    """
    
    def __init__(self):
        self.active_calls: Dict[str, CallSession] = {}
        self.call_history: List[CallSession] = []
        self.user_settings: Dict[str, CallSettings] = {}
        self.webrtc_connections: Dict[str, Any] = {}
        self.audio_streams: Dict[str, Any] = {}
        self.video_streams: Dict[str, Any] = {}
        
        # Call processing
        self.call_queue = queue.Queue()
        self.is_processing = True
        
        # Start background processing
        self._start_call_processing()
        
        # Initialize audio/video processing
        self._initialize_media_processing()
    
    def _start_call_processing(self):
        """Start background call processing"""
        self.is_processing = True
        
        # Start processing thread
        thread = threading.Thread(target=self._process_calls, daemon=True)
        thread.start()
        
        logger.info("VOIP system call processing started")
    
    def _process_calls(self):
        """Process calls in background"""
        while self.is_processing:
            try:
                call_data = self.call_queue.get(timeout=1)
                self._handle_call(call_data)
                self.call_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing call: {str(e)}")
    
    def _initialize_media_processing(self):
        """Initialize audio/video processing"""
        try:
            # Create media directories
            media_dir = Path("uploads/media")
            media_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize WebRTC
            self._initialize_webrtc()
            
            logger.info("Media processing initialized")
            
        except Exception as e:
            logger.error(f"Error initializing media processing: {str(e)}")
    
    def _initialize_webrtc(self):
        """Initialize WebRTC for peer-to-peer connections"""
        try:
            # This would initialize WebRTC libraries
            # For now, we'll simulate the functionality
            logger.info("WebRTC initialized")
            
        except Exception as e:
            logger.error(f"Error initializing WebRTC: {str(e)}")
    
    def initiate_call(self, caller_id: str, callee_id: str, call_type: CallType = CallType.AUDIO) -> Optional[CallSession]:
        """Initiate a new call"""
        try:
            # Check if callee is available
            if not self._is_user_available(callee_id):
                return None
            
            # Create call session
            call_id = str(uuid.uuid4())
            call_session = CallSession(
                call_id=call_id,
                caller_id=caller_id,
                call_type=call_type,
                status=CallStatus.INITIATING,
                created_at=datetime.now()
            )
            
            # Add caller as participant
            caller_participant = CallParticipant(
                user_id=caller_id,
                username=self._get_username(caller_id),
                display_name=self._get_display_name(caller_id),
                joined_at=datetime.now()
            )
            call_session.participants.append(caller_participant)
            
            # Store call session
            self.active_calls[call_id] = call_session
            
            # Queue for processing
            self.call_queue.put({
                'action': 'initiate',
                'call_session': call_session,
                'callee_id': callee_id
            })
            
            logger.info(f"Call initiated: {call_id} from {caller_id} to {callee_id}")
            return call_session
            
        except Exception as e:
            logger.error(f"Error initiating call: {str(e)}")
            return None
    
    def answer_call(self, call_id: str, user_id: str) -> bool:
        """Answer an incoming call"""
        try:
            if call_id not in self.active_calls:
                return False
            
            call_session = self.active_calls[call_id]
            
            # Check if user is the callee
            if user_id == call_session.caller_id:
                return False
            
            # Update call status
            call_session.status = CallStatus.CONNECTED
            call_session.started_at = datetime.now()
            
            # Add callee as participant
            callee_participant = CallParticipant(
                user_id=user_id,
                username=self._get_username(user_id),
                display_name=self._get_display_name(user_id),
                joined_at=datetime.now()
            )
            call_session.participants.append(callee_participant)
            
            # Start call processing
            self._start_call_processing(call_session)
            
            # Notify participants
            self._notify_call_answered(call_session)
            
            logger.info(f"Call answered: {call_id} by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error answering call: {str(e)}")
            return False
    
    def reject_call(self, call_id: str, user_id: str) -> bool:
        """Reject an incoming call"""
        try:
            if call_id not in self.active_calls:
                return False
            
            call_session = self.active_calls[call_id]
            
            # Update call status
            call_session.status = CallStatus.REJECTED
            call_session.ended_at = datetime.now()
            
            # Calculate duration
            if call_session.started_at:
                call_session.duration = (call_session.ended_at - call_session.started_at).total_seconds()
            
            # Move to history
            self.call_history.append(call_session)
            del self.active_calls[call_id]
            
            # Notify caller
            self._notify_call_rejected(call_session, user_id)
            
            logger.info(f"Call rejected: {call_id} by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error rejecting call: {str(e)}")
            return False
    
    def end_call(self, call_id: str, user_id: str) -> bool:
        """End an active call"""
        try:
            if call_id not in self.active_calls:
                return False
            
            call_session = self.active_calls[call_id]
            
            # Check if user is participant
            if not self._is_participant(call_session, user_id):
                return False
            
            # Update call status
            call_session.status = CallStatus.ENDED
            call_session.ended_at = datetime.now()
            
            # Calculate duration
            if call_session.started_at:
                call_session.duration = (call_session.ended_at - call_session.started_at).total_seconds()
            
            # Stop recording if enabled
            if call_session.recording_enabled:
                self._stop_call_recording(call_session)
            
            # Move to history
            self.call_history.append(call_session)
            del self.active_calls[call_id]
            
            # Notify participants
            self._notify_call_ended(call_session, user_id)
            
            logger.info(f"Call ended: {call_id} by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ending call: {str(e)}")
            return False
    
    def join_call(self, call_id: str, user_id: str) -> bool:
        """Join an active call (for group calls)"""
        try:
            if call_id not in self.active_calls:
                return False
            
            call_session = self.active_calls[call_id]
            
            # Check if call is active
            if call_session.status != CallStatus.CONNECTED:
                return False
            
            # Check if user is already participant
            if self._is_participant(call_session, user_id):
                return True
            
            # Add user as participant
            participant = CallParticipant(
                user_id=user_id,
                username=self._get_username(user_id),
                display_name=self._get_display_name(user_id),
                joined_at=datetime.now()
            )
            call_session.participants.append(participant)
            
            # Notify other participants
            self._notify_participant_joined(call_session, user_id)
            
            logger.info(f"User joined call: {user_id} in {call_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error joining call: {str(e)}")
            return False
    
    def leave_call(self, call_id: str, user_id: str) -> bool:
        """Leave an active call"""
        try:
            if call_id not in self.active_calls:
                return False
            
            call_session = self.active_calls[call_id]
            
            # Remove participant
            call_session.participants = [p for p in call_session.participants if p.user_id != user_id]
            
            # Update participant's left time
            for participant in call_session.participants:
                if participant.user_id == user_id:
                    participant.left_at = datetime.now()
                    break
            
            # Notify other participants
            self._notify_participant_left(call_session, user_id)
            
            # End call if no participants left
            if not call_session.participants:
                self.end_call(call_id, user_id)
            
            logger.info(f"User left call: {user_id} from {call_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error leaving call: {str(e)}")
            return False
    
    def mute_participant(self, call_id: str, user_id: str, muted: bool) -> bool:
        """Mute/unmute a participant"""
        try:
            if call_id not in self.active_calls:
                return False
            
            call_session = self.active_calls[call_id]
            
            # Find participant
            for participant in call_session.participants:
                if participant.user_id == user_id:
                    participant.is_muted = muted
                    
                    # Notify other participants
                    self._notify_participant_muted(call_session, user_id, muted)
                    
                    logger.info(f"Participant muted: {user_id} in {call_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error muting participant: {str(e)}")
            return False
    
    def enable_video(self, call_id: str, user_id: str, enabled: bool) -> bool:
        """Enable/disable video for a participant"""
        try:
            if call_id not in self.active_calls:
                return False
            
            call_session = self.active_calls[call_id]
            
            # Find participant
            for participant in call_session.participants:
                if participant.user_id == user_id:
                    participant.is_video_enabled = enabled
                    
                    # Notify other participants
                    self._notify_video_toggled(call_session, user_id, enabled)
                    
                    logger.info(f"Video toggled: {user_id} in {call_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error toggling video: {str(e)}")
            return False
    
    def start_recording(self, call_id: str, user_id: str) -> bool:
        """Start recording a call"""
        try:
            if call_id not in self.active_calls:
                return False
            
            call_session = self.active_calls[call_id]
            
            # Check if user is participant
            if not self._is_participant(call_session, user_id):
                return False
            
            # Enable recording
            call_session.recording_enabled = True
            call_session.recording_path = self._create_recording_path(call_id)
            
            # Start recording process
            self._start_call_recording(call_session)
            
            # Notify participants
            self._notify_recording_started(call_session)
            
            logger.info(f"Recording started: {call_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting recording: {str(e)}")
            return False
    
    def stop_recording(self, call_id: str, user_id: str) -> bool:
        """Stop recording a call"""
        try:
            if call_id not in self.active_calls:
                return False
            
            call_session = self.active_calls[call_id]
            
            # Check if user is participant
            if not self._is_participant(call_session, user_id):
                return False
            
            # Stop recording
            call_session.recording_enabled = False
            self._stop_call_recording(call_session)
            
            # Notify participants
            self._notify_recording_stopped(call_session)
            
            logger.info(f"Recording stopped: {call_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping recording: {str(e)}")
            return False
    
    def get_call_status(self, call_id: str) -> Optional[CallSession]:
        """Get call status"""
        try:
            return self.active_calls.get(call_id)
        except Exception as e:
            logger.error(f"Error getting call status: {str(e)}")
            return None
    
    def get_user_calls(self, user_id: str) -> List[CallSession]:
        """Get all calls for a user"""
        try:
            user_calls = []
            
            # Get active calls
            for call_session in self.active_calls.values():
                if self._is_participant(call_session, user_id):
                    user_calls.append(call_session)
            
            # Get recent call history
            recent_calls = [call for call in self.call_history if self._is_participant(call, user_id)]
            recent_calls.sort(key=lambda x: x.created_at, reverse=True)
            
            return user_calls + recent_calls[:10]  # Last 10 calls
            
        except Exception as e:
            logger.error(f"Error getting user calls: {str(e)}")
            return []
    
    def get_call_history(self, user_id: str, limit: int = 50) -> List[CallSession]:
        """Get call history for a user"""
        try:
            user_calls = [call for call in self.call_history if self._is_participant(call, user_id)]
            user_calls.sort(key=lambda x: x.created_at, reverse=True)
            
            return user_calls[:limit]
            
        except Exception as e:
            logger.error(f"Error getting call history: {str(e)}")
            return []
    
    def search_calls(self, user_id: str, query: str) -> List[CallSession]:
        """Search calls by participant name or call ID"""
        try:
            results = []
            query_lower = query.lower()
            
            for call in self.call_history:
                if self._is_participant(call, user_id):
                    # Search by call ID
                    if query_lower in call.call_id.lower():
                        results.append(call)
                        continue
                    
                    # Search by participant names
                    for participant in call.participants:
                        if (query_lower in participant.username.lower() or 
                            query_lower in participant.display_name.lower()):
                            results.append(call)
                            break
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching calls: {str(e)}")
            return []
    
    def _is_user_available(self, user_id: str) -> bool:
        """Check if user is available for calls"""
        try:
            # Check if user has do not disturb enabled
            if user_id in self.user_settings:
                if self.user_settings[user_id].do_not_disturb:
                    return False
            
            # Check if user is in another call
            for call_session in self.active_calls.values():
                if self._is_participant(call_session, user_id):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking user availability: {str(e)}")
            return False
    
    def _is_participant(self, call_session: CallSession, user_id: str) -> bool:
        """Check if user is participant in call"""
        return any(p.user_id == user_id for p in call_session.participants)
    
    def _get_username(self, user_id: str) -> str:
        """Get username for user ID"""
        # This would query the user database
        return f"user_{user_id}"
    
    def _get_display_name(self, user_id: str) -> str:
        """Get display name for user ID"""
        # This would query the user database
        return f"User {user_id}"
    
    def _handle_call(self, call_data: Dict[str, Any]):
        """Handle call processing"""
        try:
            action = call_data.get('action')
            call_session = call_data.get('call_session')
            
            if action == 'initiate':
                self._process_call_initiation(call_session, call_data.get('callee_id'))
            elif action == 'ring':
                self._process_call_ringing(call_session)
            elif action == 'connect':
                self._process_call_connection(call_session)
            elif action == 'end':
                self._process_call_ending(call_session)
            
        except Exception as e:
            logger.error(f"Error handling call: {str(e)}")
    
    def _process_call_initiation(self, call_session: CallSession, callee_id: str):
        """Process call initiation"""
        try:
            # Update call status
            call_session.status = CallStatus.RINGING
            
            # Notify callee
            self._notify_incoming_call(call_session, callee_id)
            
            # Set timeout for call
            self._set_call_timeout(call_session)
            
        except Exception as e:
            logger.error(f"Error processing call initiation: {str(e)}")
    
    def _process_call_ringing(self, call_session: CallSession):
        """Process call ringing"""
        try:
            # Update call status
            call_session.status = CallStatus.RINGING
            
            # Notify caller
            self._notify_call_ringing(call_session)
            
        except Exception as e:
            logger.error(f"Error processing call ringing: {str(e)}")
    
    def _process_call_connection(self, call_session: CallSession):
        """Process call connection"""
        try:
            # Update call status
            call_session.status = CallStatus.CONNECTED
            call_session.started_at = datetime.now()
            
            # Start media streams
            self._start_media_streams(call_session)
            
            # Notify participants
            self._notify_call_connected(call_session)
            
        except Exception as e:
            logger.error(f"Error processing call connection: {str(e)}")
    
    def _process_call_ending(self, call_session: CallSession):
        """Process call ending"""
        try:
            # Update call status
            call_session.status = CallStatus.ENDED
            call_session.ended_at = datetime.now()
            
            # Stop media streams
            self._stop_media_streams(call_session)
            
            # Notify participants
            self._notify_call_ended(call_session, call_session.caller_id)
            
        except Exception as e:
            logger.error(f"Error processing call ending: {str(e)}")
    
    def _start_call_processing(self, call_session: CallSession):
        """Start call processing"""
        try:
            # Start audio/video processing
            self._start_media_processing(call_session)
            
            # Start quality monitoring
            self._start_quality_monitoring(call_session)
            
        except Exception as e:
            logger.error(f"Error starting call processing: {str(e)}")
    
    def _start_media_processing(self, call_session: CallSession):
        """Start media processing for call"""
        try:
            # Initialize audio streams
            for participant in call_session.participants:
                self._initialize_audio_stream(call_session.call_id, participant.user_id)
                
                if call_session.call_type == CallType.VIDEO:
                    self._initialize_video_stream(call_session.call_id, participant.user_id)
            
        except Exception as e:
            logger.error(f"Error starting media processing: {str(e)}")
    
    def _initialize_audio_stream(self, call_id: str, user_id: str):
        """Initialize audio stream for participant"""
        try:
            # This would initialize audio stream
            stream_id = f"{call_id}_{user_id}_audio"
            self.audio_streams[stream_id] = {
                'call_id': call_id,
                'user_id': user_id,
                'enabled': True,
                'quality': CallQuality.GOOD
            }
            
        except Exception as e:
            logger.error(f"Error initializing audio stream: {str(e)}")
    
    def _initialize_video_stream(self, call_id: str, user_id: str):
        """Initialize video stream for participant"""
        try:
            # This would initialize video stream
            stream_id = f"{call_id}_{user_id}_video"
            self.video_streams[stream_id] = {
                'call_id': call_id,
                'user_id': user_id,
                'enabled': True,
                'quality': CallQuality.GOOD
            }
            
        except Exception as e:
            logger.error(f"Error initializing video stream: {str(e)}")
    
    def _start_quality_monitoring(self, call_session: CallSession):
        """Start quality monitoring for call"""
        try:
            # Monitor call quality
            for participant in call_session.participants:
                self._monitor_participant_quality(call_session, participant)
            
        except Exception as e:
            logger.error(f"Error starting quality monitoring: {str(e)}")
    
    def _monitor_participant_quality(self, call_session: CallSession, participant: CallParticipant):
        """Monitor quality for a participant"""
        try:
            # Monitor audio quality
            self._monitor_audio_quality(call_session, participant)
            
            # Monitor video quality
            if call_session.call_type == CallType.VIDEO:
                self._monitor_video_quality(call_session, participant)
            
        except Exception as e:
            logger.error(f"Error monitoring participant quality: {str(e)}")
    
    def _monitor_audio_quality(self, call_session: CallSession, participant: CallParticipant):
        """Monitor audio quality for participant"""
        try:
            # This would monitor audio quality metrics
            # For now, we'll simulate quality monitoring
            participant.connection_quality = CallQuality.GOOD
            participant.network_latency = 50.0  # ms
            participant.packet_loss = 0.01  # 1%
            
        except Exception as e:
            logger.error(f"Error monitoring audio quality: {str(e)}")
    
    def _monitor_video_quality(self, call_session: CallSession, participant: CallParticipant):
        """Monitor video quality for participant"""
        try:
            # This would monitor video quality metrics
            # For now, we'll simulate quality monitoring
            participant.connection_quality = CallQuality.GOOD
            
        except Exception as e:
            logger.error(f"Error monitoring video quality: {str(e)}")
    
    def _start_call_recording(self, call_session: CallSession):
        """Start recording a call"""
        try:
            # Create recording file
            recording_path = call_session.recording_path
            if recording_path:
                # Initialize recording
                self._initialize_recording(recording_path, call_session)
            
        except Exception as e:
            logger.error(f"Error starting call recording: {str(e)}")
    
    def _stop_call_recording(self, call_session: CallSession):
        """Stop recording a call"""
        try:
            # Finalize recording
            if call_session.recording_path:
                self._finalize_recording(call_session.recording_path, call_session)
            
        except Exception as e:
            logger.error(f"Error stopping call recording: {str(e)}")
    
    def _initialize_recording(self, recording_path: str, call_session: CallSession):
        """Initialize call recording"""
        try:
            # Create recording file
            Path(recording_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Initialize audio recording
            self._initialize_audio_recording(recording_path, call_session)
            
        except Exception as e:
            logger.error(f"Error initializing recording: {str(e)}")
    
    def _finalize_recording(self, recording_path: str, call_session: CallSession):
        """Finalize call recording"""
        try:
            # Finalize audio recording
            self._finalize_audio_recording(recording_path, call_session)
            
        except Exception as e:
            logger.error(f"Error finalizing recording: {str(e)}")
    
    def _initialize_audio_recording(self, recording_path: str, call_session: CallSession):
        """Initialize audio recording"""
        try:
            # This would initialize audio recording
            # For now, we'll create a placeholder
            with open(recording_path, 'w') as f:
                f.write(f"Call recording: {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error initializing audio recording: {str(e)}")
    
    def _finalize_audio_recording(self, recording_path: str, call_session: CallSession):
        """Finalize audio recording"""
        try:
            # This would finalize audio recording
            # For now, we'll just log the completion
            logger.info(f"Audio recording finalized: {recording_path}")
            
        except Exception as e:
            logger.error(f"Error finalizing audio recording: {str(e)}")
    
    def _create_recording_path(self, call_id: str) -> str:
        """Create recording file path"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"call_{call_id}_{timestamp}.wav"
            return f"uploads/recordings/{filename}"
            
        except Exception as e:
            logger.error(f"Error creating recording path: {str(e)}")
            return ""
    
    def _set_call_timeout(self, call_session: CallSession):
        """Set timeout for call"""
        try:
            # Set timeout (e.g., 30 seconds)
            timeout = 30
            
            # This would set a timer to end the call if not answered
            def timeout_callback():
                if call_session.status == CallStatus.RINGING:
                    call_session.status = CallStatus.FAILED
                    call_session.ended_at = datetime.now()
                    self._notify_call_timeout(call_session)
            
            # In a real implementation, this would use a timer
            # For now, we'll just log the timeout
            logger.info(f"Call timeout set for {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error setting call timeout: {str(e)}")
    
    def _start_media_streams(self, call_session: CallSession):
        """Start media streams for call"""
        try:
            # Start audio streams
            for participant in call_session.participants:
                self._start_audio_stream(call_session.call_id, participant.user_id)
                
                if call_session.call_type == CallType.VIDEO:
                    self._start_video_stream(call_session.call_id, participant.user_id)
            
        except Exception as e:
            logger.error(f"Error starting media streams: {str(e)}")
    
    def _stop_media_streams(self, call_session: CallSession):
        """Stop media streams for call"""
        try:
            # Stop audio streams
            for participant in call_session.participants:
                self._stop_audio_stream(call_session.call_id, participant.user_id)
                
                if call_session.call_type == CallType.VIDEO:
                    self._stop_video_stream(call_session.call_id, participant.user_id)
            
        except Exception as e:
            logger.error(f"Error stopping media streams: {str(e)}")
    
    def _start_audio_stream(self, call_id: str, user_id: str):
        """Start audio stream for participant"""
        try:
            stream_id = f"{call_id}_{user_id}_audio"
            if stream_id in self.audio_streams:
                self.audio_streams[stream_id]['enabled'] = True
            
        except Exception as e:
            logger.error(f"Error starting audio stream: {str(e)}")
    
    def _stop_audio_stream(self, call_id: str, user_id: str):
        """Stop audio stream for participant"""
        try:
            stream_id = f"{call_id}_{user_id}_audio"
            if stream_id in self.audio_streams:
                self.audio_streams[stream_id]['enabled'] = False
            
        except Exception as e:
            logger.error(f"Error stopping audio stream: {str(e)}")
    
    def _start_video_stream(self, call_id: str, user_id: str):
        """Start video stream for participant"""
        try:
            stream_id = f"{call_id}_{user_id}_video"
            if stream_id in self.video_streams:
                self.video_streams[stream_id]['enabled'] = True
            
        except Exception as e:
            logger.error(f"Error starting video stream: {str(e)}")
    
    def _stop_video_stream(self, call_id: str, user_id: str):
        """Stop video stream for participant"""
        try:
            stream_id = f"{call_id}_{user_id}_video"
            if stream_id in self.video_streams:
                self.video_streams[stream_id]['enabled'] = False
            
        except Exception as e:
            logger.error(f"Error stopping video stream: {str(e)}")
    
    # Notification methods
    def _notify_incoming_call(self, call_session: CallSession, callee_id: str):
        """Notify callee of incoming call"""
        try:
            # This would send notification to callee
            logger.info(f"Incoming call notification sent to {callee_id}")
            
        except Exception as e:
            logger.error(f"Error notifying incoming call: {str(e)}")
    
    def _notify_call_answered(self, call_session: CallSession):
        """Notify participants that call was answered"""
        try:
            # This would notify all participants
            logger.info(f"Call answered notification sent for {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error notifying call answered: {str(e)}")
    
    def _notify_call_rejected(self, call_session: CallSession, rejector_id: str):
        """Notify caller that call was rejected"""
        try:
            # This would notify caller
            logger.info(f"Call rejected notification sent for {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error notifying call rejected: {str(e)}")
    
    def _notify_call_ended(self, call_session: CallSession, ender_id: str):
        """Notify participants that call ended"""
        try:
            # This would notify all participants
            logger.info(f"Call ended notification sent for {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error notifying call ended: {str(e)}")
    
    def _notify_call_timeout(self, call_session: CallSession):
        """Notify caller that call timed out"""
        try:
            # This would notify caller
            logger.info(f"Call timeout notification sent for {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error notifying call timeout: {str(e)}")
    
    def _notify_call_ringing(self, call_session: CallSession):
        """Notify caller that call is ringing"""
        try:
            # This would notify caller
            logger.info(f"Call ringing notification sent for {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error notifying call ringing: {str(e)}")
    
    def _notify_call_connected(self, call_session: CallSession):
        """Notify participants that call is connected"""
        try:
            # This would notify all participants
            logger.info(f"Call connected notification sent for {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error notifying call connected: {str(e)}")
    
    def _notify_participant_joined(self, call_session: CallSession, user_id: str):
        """Notify participants that someone joined"""
        try:
            # This would notify all participants
            logger.info(f"Participant joined notification sent for {user_id} in {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error notifying participant joined: {str(e)}")
    
    def _notify_participant_left(self, call_session: CallSession, user_id: str):
        """Notify participants that someone left"""
        try:
            # This would notify all participants
            logger.info(f"Participant left notification sent for {user_id} in {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error notifying participant left: {str(e)}")
    
    def _notify_participant_muted(self, call_session: CallSession, user_id: str, muted: bool):
        """Notify participants that someone was muted/unmuted"""
        try:
            # This would notify all participants
            logger.info(f"Participant muted notification sent for {user_id} in {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error notifying participant muted: {str(e)}")
    
    def _notify_video_toggled(self, call_session: CallSession, user_id: str, enabled: bool):
        """Notify participants that video was toggled"""
        try:
            # This would notify all participants
            logger.info(f"Video toggled notification sent for {user_id} in {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error notifying video toggled: {str(e)}")
    
    def _notify_recording_started(self, call_session: CallSession):
        """Notify participants that recording started"""
        try:
            # This would notify all participants
            logger.info(f"Recording started notification sent for {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error notifying recording started: {str(e)}")
    
    def _notify_recording_stopped(self, call_session: CallSession):
        """Notify participants that recording stopped"""
        try:
            # This would notify all participants
            logger.info(f"Recording stopped notification sent for {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error notifying recording stopped: {str(e)}")
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get VOIP system analytics"""
        try:
            return {
                'active_calls': len(self.active_calls),
                'total_calls': len(self.call_history),
                'calls_today': len([call for call in self.call_history if call.created_at.date() == datetime.now().date()]),
                'total_duration': sum(call.duration for call in self.call_history),
                'avg_duration': sum(call.duration for call in self.call_history) / max(len(self.call_history), 1),
                'failed_calls': len([call for call in self.call_history if call.status == CallStatus.FAILED]),
                'success_rate': len([call for call in self.call_history if call.status == CallStatus.ENDED]) / max(len(self.call_history), 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}

# Global VOIP system instance
voip_system = VOIPSystem()
