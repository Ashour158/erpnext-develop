// Internal Communication Dashboard
// Complete dashboard for internal communication system with chat, VOIP, and file sharing

import React, { useState, useEffect } from 'react';
import {
  ChatBubbleLeftRightIcon,
  PhoneIcon,
  VideoCameraIcon,
  DocumentIcon,
  CalendarIcon,
  UserGroupIcon,
  PaperClipIcon,
  MicrophoneIcon,
  SpeakerWaveIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  BellIcon,
  CogIcon,
  ShareIcon,
  HeartIcon,
  ChatBubbleOvalLeftIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface ChatMessage {
  message_id: string;
  chat_id: string;
  sender_id: string;
  content: string;
  message_type: string;
  timestamp: string;
  status: string;
  reactions: Record<string, string[]>;
  attachments: any[];
}

interface ChatRoom {
  id: string;
  name: string;
  type: string;
  last_message: ChatMessage | null;
  unread_count: number;
  participants: number;
}

interface CallSession {
  call_id: string;
  caller_id: string;
  call_type: string;
  status: string;
  created_at: string;
  duration: number;
  participants: any[];
}

interface SharedFile {
  file_id: string;
  filename: string;
  file_type: string;
  size: number;
  upload_date: string;
  description: string;
  tags: string[];
  download_count: number;
}

interface ChatEvent {
  event_id: string;
  title: string;
  description: string;
  event_type: string;
  status: string;
  priority: string;
  scheduled_at: string;
  duration: number;
  attendees: string[];
}

const CommunicationDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('chat');
  const [activeChat, setActiveChat] = useState<string | null>(null);
  const [activeCall, setActiveCall] = useState<string | null>(null);
  
  // Data states
  const [chats, setChats] = useState<ChatRoom[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [calls, setCalls] = useState<CallSession[]>([]);
  const [files, setFiles] = useState<SharedFile[]>([]);
  const [events, setEvents] = useState<ChatEvent[]>([]);
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
  
  // UI states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [showEventCreate, setShowEventCreate] = useState(false);
  const [showCallModal, setShowCallModal] = useState(false);
  
  // Form states
  const [newMessage, setNewMessage] = useState('');
  const [typingUsers, setTypingUsers] = useState<string[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [callForm, setCallForm] = useState({
    callee_id: '',
    call_type: 'audio'
  });
  const [eventForm, setEventForm] = useState({
    title: '',
    description: '',
    event_type: 'meeting',
    scheduled_at: '',
    duration: 60,
    attendees: []
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadChats(),
        loadCalls(),
        loadFiles(),
        loadEvents(),
        loadOnlineUsers()
      ]);
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadChats = async () => {
    try {
      const response = await fetch('/api/communication/chat/users/user123/chats', {
        headers: { 'X-API-Key': 'your-api-key' }
      });
      const data = await response.json();
      setChats(data.chats || []);
    } catch (err) {
      console.error('Error loading chats:', err);
    }
  };

  const loadMessages = async (chatId: string) => {
    try {
      const response = await fetch(`/api/communication/chat/rooms/${chatId}/messages?user_id=user123`, {
        headers: { 'X-API-Key': 'your-api-key' }
      });
      const data = await response.json();
      setMessages(data.messages || []);
    } catch (err) {
      console.error('Error loading messages:', err);
    }
  };

  const loadCalls = async () => {
    try {
      const response = await fetch('/api/communication/voip/users/user123/calls', {
        headers: { 'X-API-Key': 'your-api-key' }
      });
      const data = await response.json();
      setCalls(data.calls || []);
    } catch (err) {
      console.error('Error loading calls:', err);
    }
  };

  const loadFiles = async () => {
    try {
      const response = await fetch('/api/communication/files/users/user123/files', {
        headers: { 'X-API-Key': 'your-api-key' }
      });
      const data = await response.json();
      setFiles(data.files || []);
    } catch (err) {
      console.error('Error loading files:', err);
    }
  };

  const loadEvents = async () => {
    try {
      const response = await fetch('/api/communication/events/users/user123/events', {
        headers: { 'X-API-Key': 'your-api-key' }
      });
      const data = await response.json();
      setEvents(data.events || []);
    } catch (err) {
      console.error('Error loading events:', err);
    }
  };

  const loadOnlineUsers = async () => {
    try {
      // This would load online users
      setOnlineUsers(['user1', 'user2', 'user3']);
    } catch (err) {
      console.error('Error loading online users:', err);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !activeChat) return;

    try {
      const response = await fetch('/api/communication/chat/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'your-api-key'
        },
        body: JSON.stringify({
          chat_id: activeChat,
          sender_id: 'user123',
          content: newMessage,
          message_type: 'text'
        })
      });

      if (response.ok) {
        setNewMessage('');
        loadMessages(activeChat);
      }
    } catch (err) {
      setError('Failed to send message');
    }
  };

  const initiateCall = async () => {
    try {
      const response = await fetch('/api/communication/voip/calls', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'your-api-key'
        },
        body: JSON.stringify({
          caller_id: 'user123',
          callee_id: callForm.callee_id,
          call_type: callForm.call_type
        })
      });

      if (response.ok) {
        setShowCallModal(false);
        setCallForm({ callee_id: '', call_type: 'audio' });
        loadCalls();
      }
    } catch (err) {
      setError('Failed to initiate call');
    }
  };

  const uploadFile = async (file: File) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('uploader_id', 'user123');
      formData.append('description', '');
      formData.append('share_type', 'private');

      const response = await fetch('/api/communication/files/upload', {
        method: 'POST',
        headers: { 'X-API-Key': 'your-api-key' },
        body: formData
      });

      if (response.ok) {
        setShowFileUpload(false);
        loadFiles();
      }
    } catch (err) {
      setError('Failed to upload file');
    }
  };

  const createEvent = async () => {
    try {
      const response = await fetch('/api/communication/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'your-api-key'
        },
        body: JSON.stringify({
          title: eventForm.title,
          description: eventForm.description,
          event_type: eventForm.event_type,
          scheduled_at: eventForm.scheduled_at,
          duration: eventForm.duration,
          created_by: 'user123',
          attendees: eventForm.attendees
        })
      });

      if (response.ok) {
        setShowEventCreate(false);
        setEventForm({
          title: '',
          description: '',
          event_type: 'meeting',
          scheduled_at: '',
          duration: 60,
          attendees: []
        });
        loadEvents();
      }
    } catch (err) {
      setError('Failed to create event');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-600 bg-green-100';
      case 'offline': return 'text-gray-600 bg-gray-100';
      case 'away': return 'text-yellow-600 bg-yellow-100';
      case 'busy': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getFileTypeIcon = (fileType: string) => {
    switch (fileType) {
      case 'image': return '🖼️';
      case 'video': return '🎥';
      case 'audio': return '🎵';
      case 'document': return '📄';
      case 'pdf': return '📕';
      case 'spreadsheet': return '📊';
      case 'presentation': return '📽️';
      case 'archive': return '📦';
      case 'code': return '💻';
      default: return '📁';
    }
  };

  const tabs = [
    { id: 'chat', name: 'Chat', icon: ChatBubbleLeftRightIcon },
    { id: 'voip', name: 'Calls', icon: PhoneIcon },
    { id: 'files', name: 'Files', icon: DocumentIcon },
    { id: 'events', name: 'Events', icon: CalendarIcon },
    { id: 'analytics', name: 'Analytics', icon: ChartBarIcon }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Internal Communication</h1>
              <p className="text-gray-600">Chat, calls, file sharing, and event management</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600">{onlineUsers.length} online</span>
              </div>
              <button
                onClick={() => setShowCallModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <PhoneIcon className="h-5 w-5 mr-2" />
                Start Call
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center`}
              >
                <tab.icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        )}

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Chat List */}
            <div className="lg:col-span-1">
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Chats</h3>
                    <button className="text-blue-600 hover:text-blue-900">
                      <PlusIcon className="h-5 w-5" />
                    </button>
                  </div>
                  
                  <div className="space-y-2">
                    {chats.map((chat) => (
                      <div
                        key={chat.id}
                        onClick={() => {
                          setActiveChat(chat.id);
                          loadMessages(chat.id);
                        }}
                        className={`p-3 rounded-lg cursor-pointer hover:bg-gray-50 ${
                          activeChat === chat.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{chat.name}</p>
                            <p className="text-xs text-gray-500">{chat.type}</p>
                          </div>
                          {chat.unread_count > 0 && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {chat.unread_count}
                            </span>
                          )}
                        </div>
                        {chat.last_message && (
                          <p className="text-xs text-gray-500 mt-1 truncate">
                            {chat.last_message.content}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Chat Messages */}
            <div className="lg:col-span-2">
              <div className="bg-white shadow rounded-lg h-96 flex flex-col">
                {activeChat ? (
                  <>
                    {/* Chat Header */}
                    <div className="px-4 py-3 border-b border-gray-200">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-medium text-gray-900">
                          {chats.find(c => c.id === activeChat)?.name}
                        </h3>
                        <div className="flex items-center space-x-2">
                          <button className="text-gray-400 hover:text-gray-600">
                            <PhoneIcon className="h-5 w-5" />
                          </button>
                          <button className="text-gray-400 hover:text-gray-600">
                            <VideoCameraIcon className="h-5 w-5" />
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                      {messages.map((message) => (
                        <div key={message.message_id} className="flex items-start space-x-3">
                          <div className="flex-shrink-0">
                            <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                              <span className="text-sm font-medium text-gray-700">
                                {message.sender_id.charAt(0).toUpperCase()}
                              </span>
                            </div>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <span className="text-sm font-medium text-gray-900">
                                {message.sender_id}
                              </span>
                              <span className="text-xs text-gray-500">
                                {new Date(message.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                            <p className="text-sm text-gray-700 mt-1">{message.content}</p>
                            {Object.keys(message.reactions).length > 0 && (
                              <div className="flex items-center space-x-1 mt-2">
                                {Object.entries(message.reactions).map(([emoji, users]) => (
                                  <span key={emoji} className="text-xs bg-gray-100 px-2 py-1 rounded">
                                    {emoji} {users.length}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Message Input */}
                    <div className="px-4 py-3 border-t border-gray-200">
                      <div className="flex items-center space-x-2">
                        <input
                          type="text"
                          value={newMessage}
                          onChange={(e) => setNewMessage(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                          placeholder="Type a message..."
                          className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                        />
                        <button
                          onClick={sendMessage}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                        >
                          <PaperClipIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={sendMessage}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                        >
                          Send
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-center">
                    <p className="text-gray-500">Select a chat to start messaging</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* VOIP Tab */}
        {activeTab === 'voip' && (
          <div className="space-y-6">
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Calls</h3>
                  <button
                    onClick={() => setShowCallModal(true)}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  >
                    <PlusIcon className="h-4 w-4 mr-2" />
                    New Call
                  </button>
                </div>

                <div className="space-y-4">
                  {calls.map((call) => (
                    <div key={call.call_id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="flex-shrink-0">
                            {call.call_type === 'video' ? (
                              <VideoCameraIcon className="h-6 w-6 text-blue-600" />
                            ) : (
                              <PhoneIcon className="h-6 w-6 text-green-600" />
                            )}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              Call to {call.caller_id}
                            </p>
                            <p className="text-xs text-gray-500">
                              {new Date(call.created_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            call.status === 'ended' ? 'bg-green-100 text-green-800' :
                            call.status === 'failed' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {call.status}
                          </span>
                          <span className="text-sm text-gray-500">
                            {formatDuration(call.duration)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Files Tab */}
        {activeTab === 'files' && (
          <div className="space-y-6">
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Shared Files</h3>
                  <button
                    onClick={() => setShowFileUpload(true)}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  >
                    <PlusIcon className="h-4 w-4 mr-2" />
                    Upload File
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {files.map((file) => (
                    <div key={file.file_id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0">
                          <span className="text-2xl">{getFileTypeIcon(file.file_type)}</span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {file.filename}
                          </p>
                          <p className="text-xs text-gray-500">
                            {formatFileSize(file.size)} • {file.download_count} downloads
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {new Date(file.upload_date).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      {file.description && (
                        <p className="text-xs text-gray-600 mt-2">{file.description}</p>
                      )}
                      {file.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {file.tags.map((tag, index) => (
                            <span key={index} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              #{tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Events Tab */}
        {activeTab === 'events' && (
          <div className="space-y-6">
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Events</h3>
                  <button
                    onClick={() => setShowEventCreate(true)}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  >
                    <PlusIcon className="h-4 w-4 mr-2" />
                    Create Event
                  </button>
                </div>

                <div className="space-y-4">
                  {events.map((event) => (
                    <div key={event.event_id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="flex-shrink-0">
                            <CalendarIcon className="h-6 w-6 text-blue-600" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">{event.title}</p>
                            <p className="text-xs text-gray-500">{event.description}</p>
                            <p className="text-xs text-gray-400">
                              {new Date(event.scheduled_at).toLocaleString()} • {event.duration} min
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(event.priority)}`}>
                            {event.priority}
                          </span>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            event.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                            event.status === 'completed' ? 'bg-green-100 text-green-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {event.status}
                          </span>
                        </div>
                      </div>
                      {event.attendees.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs text-gray-500">
                            Attendees: {event.attendees.join(', ')}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <ChatBubbleLeftRightIcon className="h-6 w-6 text-blue-600" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Messages</dt>
                        <dd className="text-lg font-medium text-gray-900">1,234</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <PhoneIcon className="h-6 w-6 text-green-600" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Calls</dt>
                        <dd className="text-lg font-medium text-gray-900">89</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <DocumentIcon className="h-6 w-6 text-purple-600" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Files Shared</dt>
                        <dd className="text-lg font-medium text-gray-900">456</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <CalendarIcon className="h-6 w-6 text-orange-600" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Events Created</dt>
                        <dd className="text-lg font-medium text-gray-900">23</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Call Modal */}
      {showCallModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Start a Call</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">User ID</label>
                  <input
                    type="text"
                    value={callForm.callee_id}
                    onChange={(e) => setCallForm({ ...callForm, callee_id: e.target.value })}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter user ID"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Call Type</label>
                  <select
                    value={callForm.call_type}
                    onChange={(e) => setCallForm({ ...callForm, call_type: e.target.value })}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="audio">Audio Call</option>
                    <option value="video">Video Call</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowCallModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={initiateCall}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                >
                  Start Call
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* File Upload Modal */}
      {showFileUpload && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Upload File</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Select File</label>
                  <input
                    type="file"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) uploadFile(file);
                    }}
                    className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowFileUpload(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Event Create Modal */}
      {showEventCreate && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Create Event</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Title</label>
                  <input
                    type="text"
                    value={eventForm.title}
                    onChange={(e) => setEventForm({ ...eventForm, title: e.target.value })}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter event title"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    value={eventForm.description}
                    onChange={(e) => setEventForm({ ...eventForm, description: e.target.value })}
                    rows={3}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter event description"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Event Type</label>
                  <select
                    value={eventForm.event_type}
                    onChange={(e) => setEventForm({ ...eventForm, event_type: e.target.value })}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="meeting">Meeting</option>
                    <option value="call">Call</option>
                    <option value="deadline">Deadline</option>
                    <option value="reminder">Reminder</option>
                    <option value="task">Task</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Scheduled At</label>
                  <input
                    type="datetime-local"
                    value={eventForm.scheduled_at}
                    onChange={(e) => setEventForm({ ...eventForm, scheduled_at: e.target.value })}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Duration (minutes)</label>
                  <input
                    type="number"
                    value={eventForm.duration}
                    onChange={(e) => setEventForm({ ...eventForm, duration: parseInt(e.target.value) })}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowEventCreate(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={createEvent}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                >
                  Create Event
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CommunicationDashboard;
