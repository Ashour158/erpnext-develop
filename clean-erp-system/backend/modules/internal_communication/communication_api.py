# Communication API
# REST API endpoints for internal communication system

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import json
import uuid
from functools import wraps

# Import communication modules
from .chat_system import ChatSystem, ChatMessage, ChatRoom, ChatChannel, MessageType, ChatType, UserStatus
from .voip_system import VOIPSystem, CallSession, CallType, CallStatus
from .file_sharing import FileSharingSystem, SharedFile, FileType, ShareType
from .event_creation import EventCreationSystem, ChatEvent, EventType, EventStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
communication_bp = Blueprint('communication', __name__, url_prefix='/api/communication')

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in headers
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != current_app.config.get('COMMUNICATION_API_KEY'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Chat System Endpoints
@communication_bp.route('/chat/users', methods=['POST'])
@require_auth
def register_user():
    """Register a new user in the chat system"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'username', 'display_name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Register user
        user = chat_system.register_user(
            user_id=data['user_id'],
            username=data['username'],
            display_name=data['display_name'],
            email=data['email'],
            avatar_url=data.get('avatar_url'),
            permissions=data.get('permissions', [])
        )
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'display_name': user.display_name,
                'email': user.email,
                'status': user.status.value
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/chat/users/<user_id>/status', methods=['PUT'])
@require_auth
def update_user_status(user_id: str):
    """Update user status"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if status == 'online':
            success = chat_system.set_user_online(user_id)
        elif status == 'offline':
            success = chat_system.set_user_offline(user_id)
        else:
            return jsonify({'error': 'Invalid status'}), 400
        
        if success:
            return jsonify({'success': True, 'message': 'Status updated'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
            
    except Exception as e:
        logger.error(f"Error updating user status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/chat/rooms', methods=['POST'])
@require_auth
def create_chat_room():
    """Create a new chat room"""
    try:
        data = request.get_json()
        
        if data.get('chat_type') == 'private':
            # Create private chat
            room = chat_system.create_private_chat(
                user1_id=data['user1_id'],
                user2_id=data['user2_id']
            )
        elif data.get('chat_type') == 'group':
            # Create group chat
            room = chat_system.create_group_chat(
                name=data['name'],
                description=data.get('description', ''),
                created_by=data['created_by'],
                participants=data['participants'],
                is_private=data.get('is_private', False)
            )
        else:
            return jsonify({'error': 'Invalid chat type'}), 400
        
        if room:
            return jsonify({
                'success': True,
                'room': {
                    'room_id': room.room_id,
                    'name': room.name,
                    'chat_type': room.chat_type.value,
                    'participants': room.participants
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to create room'}), 500
            
    except Exception as e:
        logger.error(f"Error creating chat room: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/chat/channels', methods=['POST'])
@require_auth
def create_channel():
    """Create a new channel"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'department_id', 'created_by']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        channel = chat_system.create_channel(
            name=data['name'],
            description=data.get('description', ''),
            department_id=data['department_id'],
            created_by=data['created_by'],
            is_public=data.get('is_public', True)
        )
        
        if channel:
            return jsonify({
                'success': True,
                'channel': {
                    'channel_id': channel.channel_id,
                    'name': channel.name,
                    'department_id': channel.department_id,
                    'is_public': channel.is_public
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to create channel'}), 500
            
    except Exception as e:
        logger.error(f"Error creating channel: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/chat/messages', methods=['POST'])
@require_auth
def send_message():
    """Send a message"""
    try:
        data = request.get_json()
        
        required_fields = ['chat_id', 'sender_id', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        message = chat_system.send_message(
            chat_id=data['chat_id'],
            sender_id=data['sender_id'],
            content=data['content'],
            message_type=MessageType(data.get('message_type', 'text')),
            reply_to=data.get('reply_to'),
            attachments=data.get('attachments', [])
        )
        
        if message:
            return jsonify({
                'success': True,
                'message': {
                    'message_id': message.message_id,
                    'chat_id': message.chat_id,
                    'sender_id': message.sender_id,
                    'content': message.content,
                    'message_type': message.message_type.value,
                    'timestamp': message.timestamp.isoformat()
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to send message'}), 500
            
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/chat/messages/<message_id>', methods=['PUT'])
@require_auth
def edit_message(message_id: str):
    """Edit a message"""
    try:
        data = request.get_json()
        
        success = chat_system.edit_message(
            message_id=message_id,
            new_content=data['content'],
            editor_id=data['editor_id']
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Message edited'}), 200
        else:
            return jsonify({'error': 'Failed to edit message'}), 500
            
    except Exception as e:
        logger.error(f"Error editing message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/chat/messages/<message_id>', methods=['DELETE'])
@require_auth
def delete_message(message_id: str):
    """Delete a message"""
    try:
        data = request.get_json()
        
        success = chat_system.delete_message(
            message_id=message_id,
            deleter_id=data['deleter_id']
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Message deleted'}), 200
        else:
            return jsonify({'error': 'Failed to delete message'}), 500
            
    except Exception as e:
        logger.error(f"Error deleting message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/chat/messages/<message_id>/reactions', methods=['POST'])
@require_auth
def add_reaction(message_id: str):
    """Add reaction to a message"""
    try:
        data = request.get_json()
        
        success = chat_system.add_reaction(
            message_id=message_id,
            user_id=data['user_id'],
            emoji=data['emoji']
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Reaction added'}), 200
        else:
            return jsonify({'error': 'Failed to add reaction'}), 500
            
    except Exception as e:
        logger.error(f"Error adding reaction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/chat/messages/<message_id>/reactions', methods=['DELETE'])
@require_auth
def remove_reaction(message_id: str):
    """Remove reaction from a message"""
    try:
        data = request.get_json()
        
        success = chat_system.remove_reaction(
            message_id=message_id,
            user_id=data['user_id'],
            emoji=data['emoji']
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Reaction removed'}), 200
        else:
            return jsonify({'error': 'Failed to remove reaction'}), 500
            
    except Exception as e:
        logger.error(f"Error removing reaction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/chat/rooms/<room_id>/messages', methods=['GET'])
@require_auth
def get_room_messages(room_id: str):
    """Get messages from a room"""
    try:
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        messages = chat_system.get_chat_messages(room_id, user_id, limit, offset)
        
        return jsonify({
            'messages': [
                {
                    'message_id': msg.message_id,
                    'sender_id': msg.sender_id,
                    'content': msg.content,
                    'message_type': msg.message_type.value,
                    'timestamp': msg.timestamp.isoformat(),
                    'status': msg.status.value,
                    'reactions': msg.reactions,
                    'attachments': msg.attachments
                }
                for msg in messages
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting room messages: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/chat/users/<user_id>/chats', methods=['GET'])
@require_auth
def get_user_chats(user_id: str):
    """Get all chats for a user"""
    try:
        chats = chat_system.get_user_chats(user_id)
        
        return jsonify({'chats': chats}), 200
        
    except Exception as e:
        logger.error(f"Error getting user chats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/chat/search', methods=['GET'])
@require_auth
def search_messages():
    """Search messages"""
    try:
        user_id = request.args.get('user_id')
        query = request.args.get('query')
        chat_id = request.args.get('chat_id')
        
        if not user_id or not query:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        messages = chat_system.search_messages(user_id, query, chat_id)
        
        return jsonify({
            'messages': [
                {
                    'message_id': msg.message_id,
                    'chat_id': msg.chat_id,
                    'sender_id': msg.sender_id,
                    'content': msg.content,
                    'message_type': msg.message_type.value,
                    'timestamp': msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching messages: {str(e)}")
        return jsonify({'error': str(e)}), 500

# VOIP System Endpoints
@communication_bp.route('/voip/calls', methods=['POST'])
@require_auth
def initiate_call():
    """Initiate a new call"""
    try:
        data = request.get_json()
        
        required_fields = ['caller_id', 'callee_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        call_session = voip_system.initiate_call(
            caller_id=data['caller_id'],
            callee_id=data['callee_id'],
            call_type=CallType(data.get('call_type', 'audio'))
        )
        
        if call_session:
            return jsonify({
                'success': True,
                'call': {
                    'call_id': call_session.call_id,
                    'caller_id': call_session.caller_id,
                    'call_type': call_session.call_type.value,
                    'status': call_session.status.value,
                    'created_at': call_session.created_at.isoformat()
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to initiate call'}), 500
            
    except Exception as e:
        logger.error(f"Error initiating call: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/voip/calls/<call_id>/answer', methods=['POST'])
@require_auth
def answer_call(call_id: str):
    """Answer a call"""
    try:
        data = request.get_json()
        
        success = voip_system.answer_call(call_id, data['user_id'])
        
        if success:
            return jsonify({'success': True, 'message': 'Call answered'}), 200
        else:
            return jsonify({'error': 'Failed to answer call'}), 500
            
    except Exception as e:
        logger.error(f"Error answering call: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/voip/calls/<call_id>/reject', methods=['POST'])
@require_auth
def reject_call(call_id: str):
    """Reject a call"""
    try:
        data = request.get_json()
        
        success = voip_system.reject_call(call_id, data['user_id'])
        
        if success:
            return jsonify({'success': True, 'message': 'Call rejected'}), 200
        else:
            return jsonify({'error': 'Failed to reject call'}), 500
            
    except Exception as e:
        logger.error(f"Error rejecting call: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/voip/calls/<call_id>/end', methods=['POST'])
@require_auth
def end_call(call_id: str):
    """End a call"""
    try:
        data = request.get_json()
        
        success = voip_system.end_call(call_id, data['user_id'])
        
        if success:
            return jsonify({'success': True, 'message': 'Call ended'}), 200
        else:
            return jsonify({'error': 'Failed to end call'}), 500
            
    except Exception as e:
        logger.error(f"Error ending call: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/voip/calls/<call_id>/join', methods=['POST'])
@require_auth
def join_call(call_id: str):
    """Join a call"""
    try:
        data = request.get_json()
        
        success = voip_system.join_call(call_id, data['user_id'])
        
        if success:
            return jsonify({'success': True, 'message': 'Joined call'}), 200
        else:
            return jsonify({'error': 'Failed to join call'}), 500
            
    except Exception as e:
        logger.error(f"Error joining call: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/voip/calls/<call_id>/leave', methods=['POST'])
@require_auth
def leave_call(call_id: str):
    """Leave a call"""
    try:
        data = request.get_json()
        
        success = voip_system.leave_call(call_id, data['user_id'])
        
        if success:
            return jsonify({'success': True, 'message': 'Left call'}), 200
        else:
            return jsonify({'error': 'Failed to leave call'}), 500
            
    except Exception as e:
        logger.error(f"Error leaving call: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/voip/calls/<call_id>/mute', methods=['POST'])
@require_auth
def mute_participant(call_id: str):
    """Mute/unmute a participant"""
    try:
        data = request.get_json()
        
        success = voip_system.mute_participant(
            call_id=call_id,
            user_id=data['user_id'],
            muted=data['muted']
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Participant muted/unmuted'}), 200
        else:
            return jsonify({'error': 'Failed to mute/unmute participant'}), 500
            
    except Exception as e:
        logger.error(f"Error muting participant: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/voip/calls/<call_id>/video', methods=['POST'])
@require_auth
def toggle_video(call_id: str):
    """Enable/disable video"""
    try:
        data = request.get_json()
        
        success = voip_system.enable_video(
            call_id=call_id,
            user_id=data['user_id'],
            enabled=data['enabled']
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Video toggled'}), 200
        else:
            return jsonify({'error': 'Failed to toggle video'}), 500
            
    except Exception as e:
        logger.error(f"Error toggling video: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/voip/calls/<call_id>/recording', methods=['POST'])
@require_auth
def start_recording(call_id: str):
    """Start recording a call"""
    try:
        data = request.get_json()
        
        success = voip_system.start_recording(call_id, data['user_id'])
        
        if success:
            return jsonify({'success': True, 'message': 'Recording started'}), 200
        else:
            return jsonify({'error': 'Failed to start recording'}), 500
            
    except Exception as e:
        logger.error(f"Error starting recording: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/voip/calls/<call_id>/recording', methods=['DELETE'])
@require_auth
def stop_recording(call_id: str):
    """Stop recording a call"""
    try:
        data = request.get_json()
        
        success = voip_system.stop_recording(call_id, data['user_id'])
        
        if success:
            return jsonify({'success': True, 'message': 'Recording stopped'}), 200
        else:
            return jsonify({'error': 'Failed to stop recording'}), 500
            
    except Exception as e:
        logger.error(f"Error stopping recording: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/voip/calls/<call_id>', methods=['GET'])
@require_auth
def get_call_status(call_id: str):
    """Get call status"""
    try:
        call_session = voip_system.get_call_status(call_id)
        
        if call_session:
            return jsonify({
                'call': {
                    'call_id': call_session.call_id,
                    'caller_id': call_session.caller_id,
                    'call_type': call_session.call_type.value,
                    'status': call_session.status.value,
                    'created_at': call_session.created_at.isoformat(),
                    'started_at': call_session.started_at.isoformat() if call_session.started_at else None,
                    'duration': call_session.duration,
                    'participants': [
                        {
                            'user_id': p.user_id,
                            'username': p.username,
                            'display_name': p.display_name,
                            'is_muted': p.is_muted,
                            'is_video_enabled': p.is_video_enabled
                        }
                        for p in call_session.participants
                    ]
                }
            }), 200
        else:
            return jsonify({'error': 'Call not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting call status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/voip/users/<user_id>/calls', methods=['GET'])
@require_auth
def get_user_calls(user_id: str):
    """Get calls for a user"""
    try:
        calls = voip_system.get_user_calls(user_id)
        
        return jsonify({
            'calls': [
                {
                    'call_id': call.call_id,
                    'caller_id': call.caller_id,
                    'call_type': call.call_type.value,
                    'status': call.status.value,
                    'created_at': call.created_at.isoformat(),
                    'duration': call.duration
                }
                for call in calls
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user calls: {str(e)}")
        return jsonify({'error': str(e)}), 500

# File Sharing Endpoints
@communication_bp.route('/files/upload', methods=['POST'])
@require_auth
def upload_file():
    """Upload a file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get file data
        file_data = file.read()
        filename = file.filename
        
        # Get additional data
        uploader_id = request.form.get('uploader_id')
        description = request.form.get('description', '')
        tags = request.form.get('tags', '').split(',') if request.form.get('tags') else []
        share_type = ShareType(request.form.get('share_type', 'private'))
        
        if not uploader_id:
            return jsonify({'error': 'Missing uploader_id'}), 400
        
        # Upload file
        shared_file = file_sharing_system.upload_file(
            filename=filename,
            file_data=file_data,
            uploader_id=uploader_id,
            description=description,
            tags=tags,
            share_type=share_type
        )
        
        if shared_file:
            return jsonify({
                'success': True,
                'file': {
                    'file_id': shared_file.file_id,
                    'filename': shared_file.filename,
                    'file_type': shared_file.file_type.value,
                    'size': shared_file.size,
                    'upload_date': shared_file.upload_date.isoformat()
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to upload file'}), 500
            
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/files/<file_id>/download', methods=['GET'])
@require_auth
def download_file(file_id: str):
    """Download a file"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        file_data = file_sharing_system.download_file(file_id, user_id)
        
        if file_data:
            return jsonify({
                'success': True,
                'file_data': file_data.hex()  # Convert to hex string for JSON
            }), 200
        else:
            return jsonify({'error': 'File not found or access denied'}), 404
            
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/files/<file_id>', methods=['GET'])
@require_auth
def get_file_info(file_id: str):
    """Get file information"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        file_info = file_sharing_system.get_file_info(file_id, user_id)
        
        if file_info:
            return jsonify({
                'file': {
                    'file_id': file_info.file_id,
                    'filename': file_info.filename,
                    'file_type': file_info.file_type.value,
                    'size': file_info.size,
                    'upload_date': file_info.upload_date.isoformat(),
                    'description': file_info.description,
                    'tags': file_info.tags,
                    'download_count': file_info.download_count
                }
            }), 200
        else:
            return jsonify({'error': 'File not found or access denied'}), 404
            
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/files/share', methods=['POST'])
@require_auth
def share_file():
    """Share a file"""
    try:
        data = request.get_json()
        
        required_fields = ['file_id', 'shared_by', 'shared_with']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        file_share = file_sharing_system.share_file(
            file_id=data['file_id'],
            shared_by=data['shared_by'],
            shared_with=data['shared_with'],
            share_type=ShareType(data.get('share_type', 'private')),
            permissions=data.get('permissions', ['read']),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        )
        
        if file_share:
            return jsonify({
                'success': True,
                'share': {
                    'share_id': file_share.share_id,
                    'file_id': file_share.file_id,
                    'shared_by': file_share.shared_by,
                    'shared_with': file_share.shared_with,
                    'share_type': file_share.share_type.value
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to share file'}), 500
            
    except Exception as e:
        logger.error(f"Error sharing file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/files/users/<user_id>/files', methods=['GET'])
@require_auth
def get_user_files(user_id: str):
    """Get files for a user"""
    try:
        file_type = request.args.get('file_type')
        files = file_sharing_system.get_user_files(
            user_id=user_id,
            file_type=FileType(file_type) if file_type else None
        )
        
        return jsonify({
            'files': [
                {
                    'file_id': file.file_id,
                    'filename': file.filename,
                    'file_type': file.file_type.value,
                    'size': file.size,
                    'upload_date': file.upload_date.isoformat(),
                    'description': file.description,
                    'tags': file.tags
                }
                for file in files
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/files/search', methods=['GET'])
@require_auth
def search_files():
    """Search files"""
    try:
        user_id = request.args.get('user_id')
        query = request.args.get('query')
        file_type = request.args.get('file_type')
        
        if not user_id or not query:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        files = file_sharing_system.search_files(
            user_id=user_id,
            query=query,
            file_type=FileType(file_type) if file_type else None
        )
        
        return jsonify({
            'files': [
                {
                    'file_id': file.file_id,
                    'filename': file.filename,
                    'file_type': file.file_type.value,
                    'size': file.size,
                    'upload_date': file.upload_date.isoformat(),
                    'description': file.description,
                    'tags': file.tags
                }
                for file in files
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/files/<file_id>/comments', methods=['POST'])
@require_auth
def add_file_comment():
    """Add a comment to a file"""
    try:
        data = request.get_json()
        
        comment = file_sharing_system.add_file_comment(
            file_id=data['file_id'],
            user_id=data['user_id'],
            content=data['content']
        )
        
        if comment:
            return jsonify({
                'success': True,
                'comment': {
                    'comment_id': comment.comment_id,
                    'file_id': comment.file_id,
                    'user_id': comment.user_id,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat()
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to add comment'}), 500
            
    except Exception as e:
        logger.error(f"Error adding file comment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/files/<file_id>/comments', methods=['GET'])
@require_auth
def get_file_comments(file_id: str):
    """Get comments for a file"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        comments = file_sharing_system.get_file_comments(file_id, user_id)
        
        return jsonify({
            'comments': [
                {
                    'comment_id': comment.comment_id,
                    'user_id': comment.user_id,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat(),
                    'is_edited': comment.is_edited
                }
                for comment in comments
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting file comments: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Event Creation Endpoints
@communication_bp.route('/events', methods=['POST'])
@require_auth
def create_event():
    """Create an event"""
    try:
        data = request.get_json()
        
        if data.get('from_message'):
            # Create event from message
            event = event_creation_system.create_event_from_message(
                message_content=data['message_content'],
                created_by=data['created_by'],
                chat_id=data.get('chat_id'),
                message_id=data.get('message_id')
            )
        else:
            # Create manual event
            event = event_creation_system.create_manual_event(
                title=data['title'],
                description=data['description'],
                event_type=EventType(data['event_type']),
                scheduled_at=datetime.fromisoformat(data['scheduled_at']),
                duration=data['duration'],
                created_by=data['created_by'],
                attendees=data.get('attendees', []),
                location=data.get('location'),
                priority=EventPriority(data.get('priority', 'medium'))
            )
        
        if event:
            return jsonify({
                'success': True,
                'event': {
                    'event_id': event.event_id,
                    'title': event.title,
                    'description': event.description,
                    'event_type': event.event_type.value,
                    'status': event.status.value,
                    'priority': event.priority.value,
                    'scheduled_at': event.scheduled_at.isoformat(),
                    'duration': event.duration,
                    'attendees': event.attendees
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to create event'}), 500
            
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/events/<event_id>', methods=['PUT'])
@require_auth
def update_event(event_id: str):
    """Update an event"""
    try:
        data = request.get_json()
        
        success = event_creation_system.update_event(
            event_id=event_id,
            user_id=data['user_id'],
            updates=data['updates']
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Event updated'}), 200
        else:
            return jsonify({'error': 'Failed to update event'}), 500
            
    except Exception as e:
        logger.error(f"Error updating event: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/events/<event_id>', methods=['DELETE'])
@require_auth
def delete_event(event_id: str):
    """Delete an event"""
    try:
        data = request.get_json()
        
        success = event_creation_system.delete_event(
            event_id=event_id,
            user_id=data['user_id']
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Event deleted'}), 200
        else:
            return jsonify({'error': 'Failed to delete event'}), 500
            
    except Exception as e:
        logger.error(f"Error deleting event: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/events/<event_id>', methods=['GET'])
@require_auth
def get_event(event_id: str):
    """Get an event"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        event = event_creation_system.get_event(event_id, user_id)
        
        if event:
            return jsonify({
                'event': {
                    'event_id': event.event_id,
                    'title': event.title,
                    'description': event.description,
                    'event_type': event.event_type.value,
                    'status': event.status.value,
                    'priority': event.priority.value,
                    'scheduled_at': event.scheduled_at.isoformat(),
                    'duration': event.duration,
                    'attendees': event.attendees,
                    'location': event.location,
                    'tags': event.tags
                }
            }), 200
        else:
            return jsonify({'error': 'Event not found or access denied'}), 404
            
    except Exception as e:
        logger.error(f"Error getting event: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/events/users/<user_id>/events', methods=['GET'])
@require_auth
def get_user_events(user_id: str):
    """Get events for a user"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        events = event_creation_system.get_user_events(
            user_id=user_id,
            start_date=datetime.fromisoformat(start_date) if start_date else None,
            end_date=datetime.fromisoformat(end_date) if end_date else None
        )
        
        return jsonify({
            'events': [
                {
                    'event_id': event.event_id,
                    'title': event.title,
                    'description': event.description,
                    'event_type': event.event_type.value,
                    'status': event.status.value,
                    'priority': event.priority.value,
                    'scheduled_at': event.scheduled_at.isoformat(),
                    'duration': event.duration,
                    'attendees': event.attendees
                }
                for event in events
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user events: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/events/search', methods=['GET'])
@require_auth
def search_events():
    """Search events"""
    try:
        user_id = request.args.get('user_id')
        query = request.args.get('query')
        
        if not user_id or not query:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        events = event_creation_system.search_events(user_id, query)
        
        return jsonify({
            'events': [
                {
                    'event_id': event.event_id,
                    'title': event.title,
                    'description': event.description,
                    'event_type': event.event_type.value,
                    'status': event.status.value,
                    'priority': event.priority.value,
                    'scheduled_at': event.scheduled_at.isoformat(),
                    'duration': event.duration
                }
                for event in events
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching events: {str(e)}")
        return jsonify({'error': str(e)}), 500

@communication_bp.route('/events/<event_id>/reminders', methods=['POST'])
@require_auth
def add_event_reminders():
    """Add reminders to an event"""
    try:
        data = request.get_json()
        
        success = event_creation_system.add_event_reminder(
            event_id=data['event_id'],
            user_id=data['user_id'],
            reminder_minutes=data['reminder_minutes']
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Reminders added'}), 200
        else:
            return jsonify({'error': 'Failed to add reminders'}), 500
            
    except Exception as e:
        logger.error(f"Error adding event reminders: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Analytics Endpoints
@communication_bp.route('/analytics', methods=['GET'])
@require_auth
def get_analytics():
    """Get communication analytics"""
    try:
        chat_analytics = chat_system.get_analytics()
        voip_analytics = voip_system.get_analytics()
        file_analytics = file_sharing_system.get_analytics()
        event_analytics = event_creation_system.get_analytics()
        
        return jsonify({
            'chat': chat_analytics,
            'voip': voip_analytics,
            'files': file_analytics,
            'events': event_analytics
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Health Check
@communication_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'chat': 'active',
                'voip': 'active',
                'file_sharing': 'active',
                'event_creation': 'active'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
