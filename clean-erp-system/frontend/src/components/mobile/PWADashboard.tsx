// Progressive Web App Dashboard
// Mobile-optimized dashboard with offline functionality

import React, { useState, useEffect, useCallback } from 'react';
import {
  DevicePhoneMobileIcon,
  WifiIcon,
  WifiSlashIcon,
  CloudIcon,
  CloudSlashIcon,
  BellIcon,
  CogIcon,
  HomeIcon,
  ChartBarIcon,
  UserGroupIcon,
  DocumentTextIcon,
  CalendarIcon,
  ChatBubbleLeftRightIcon,
  CameraIcon,
  MicrophoneIcon,
  MapPinIcon,
  QrCodeIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  BellSlashIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

interface PWADashboardProps {
  className?: string;
}

const PWADashboard: React.FC<PWADashboardProps> = ({ className = '' }) => {
  // State
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isInstalled, setIsInstalled] = useState(false);
  const [activeTab, setActiveTab] = useState<'home' | 'analytics' | 'team' | 'documents' | 'calendar' | 'chat'>('home');
  const [notifications, setNotifications] = useState<any[]>([]);
  const [showCamera, setShowCamera] = useState(false);
  const [showVoice, setShowVoice] = useState(false);
  const [location, setLocation] = useState<{lat: number, lng: number} | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // PWA Installation
  useEffect(() => {
    // Check if app is installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
    }

    // Listen for online/offline events
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Get user location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
        },
        (error) => {
          console.error('Error getting location:', error);
        }
      );
    }
  }, []);

  // Handlers
  const handleInstall = useCallback(async () => {
    try {
      // Check if PWA is installable
      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registered:', registration);
      }
    } catch (error) {
      console.error('Error installing PWA:', error);
    }
  }, []);

  const handleCamera = useCallback(() => {
    setShowCamera(true);
    // Implement camera functionality
  }, []);

  const handleVoice = useCallback(() => {
    setShowVoice(true);
    // Implement voice functionality
  }, []);

  const handleQRScan = useCallback(() => {
    // Implement QR code scanning
    console.log('QR Code scanning initiated');
  }, []);

  const handleTabChange = useCallback((tab: typeof activeTab) => {
    setActiveTab(tab);
  }, []);

  // Render functions
  const renderHomeTab = () => (
    <div className="space-y-4">
      {/* Status Cards */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="flex items-center space-x-2">
            {isOnline ? (
              <WifiIcon className="w-5 h-5 text-green-500" />
            ) : (
              <WifiSlashIcon className="w-5 h-5 text-red-500" />
            )}
            <span className="text-sm font-medium">
              {isOnline ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
        
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="flex items-center space-x-2">
            {isInstalled ? (
              <CheckCircleIcon className="w-5 h-5 text-green-500" />
            ) : (
              <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />
            )}
            <span className="text-sm font-medium">
              {isInstalled ? 'Installed' : 'Install Available'}
            </span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg p-4 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={handleCamera}
            className="flex flex-col items-center space-y-2 p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <CameraIcon className="w-8 h-8 text-blue-600" />
            <span className="text-sm font-medium">Camera</span>
          </button>
          
          <button
            onClick={handleVoice}
            className="flex flex-col items-center space-y-2 p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
          >
            <MicrophoneIcon className="w-8 h-8 text-green-600" />
            <span className="text-sm font-medium">Voice</span>
          </button>
          
          <button
            onClick={handleQRScan}
            className="flex flex-col items-center space-y-2 p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
          >
            <QrCodeIcon className="w-8 h-8 text-purple-600" />
            <span className="text-sm font-medium">QR Scan</span>
          </button>
          
          <button
            onClick={() => setLocation(null)}
            className="flex flex-col items-center space-y-2 p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors"
          >
            <MapPinIcon className="w-8 h-8 text-orange-600" />
            <span className="text-sm font-medium">Location</span>
          </button>
        </div>
      </div>

      {/* Location Info */}
      {location && (
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <h3 className="text-lg font-semibold mb-2">Current Location</h3>
          <p className="text-sm text-gray-600">
            Lat: {location.lat.toFixed(6)}, Lng: {location.lng.toFixed(6)}
          </p>
        </div>
      )}
    </div>
  );

  const renderAnalyticsTab = () => (
    <div className="space-y-4">
      <div className="bg-white rounded-lg p-4 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Mobile Analytics</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">App Usage</span>
            <span className="text-sm font-medium">2h 34m</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Data Synced</span>
            <span className="text-sm font-medium">1.2 GB</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Offline Time</span>
            <span className="text-sm font-medium">45m</span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTeamTab = () => (
    <div className="space-y-4">
      <div className="bg-white rounded-lg p-4 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Team Members</h3>
        <div className="space-y-3">
          {['John Doe', 'Jane Smith', 'Mike Johnson'].map((member, index) => (
            <div key={index} className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">
                  {member.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
              <span className="text-sm font-medium">{member}</span>
              <div className="w-2 h-2 bg-green-500 rounded-full ml-auto"></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderDocumentsTab = () => (
    <div className="space-y-4">
      <div className="bg-white rounded-lg p-4 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Recent Documents</h3>
        <div className="space-y-3">
          {['Project Report.pdf', 'Meeting Notes.docx', 'Budget.xlsx'].map((doc, index) => (
            <div key={index} className="flex items-center space-x-3">
              <DocumentTextIcon className="w-5 h-5 text-gray-400" />
              <span className="text-sm font-medium">{doc}</span>
              <span className="text-xs text-gray-500 ml-auto">2h ago</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderCalendarTab = () => (
    <div className="space-y-4">
      <div className="bg-white rounded-lg p-4 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Today's Schedule</h3>
        <div className="space-y-3">
          {[
            { time: '9:00 AM', event: 'Team Meeting', type: 'meeting' },
            { time: '2:00 PM', event: 'Client Call', type: 'call' },
            { time: '4:00 PM', event: 'Project Review', type: 'review' }
          ].map((item, index) => (
            <div key={index} className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-sm font-medium">{item.time}</span>
              <span className="text-sm text-gray-600">{item.event}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderChatTab = () => (
    <div className="space-y-4">
      <div className="bg-white rounded-lg p-4 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Recent Chats</h3>
        <div className="space-y-3">
          {[
            { name: 'Team Chat', lastMessage: 'Great work on the project!', time: '2m ago' },
            { name: 'John Doe', lastMessage: 'Can we schedule a call?', time: '1h ago' },
            { name: 'Jane Smith', lastMessage: 'The report is ready', time: '3h ago' }
          ].map((chat, index) => (
            <div key={index} className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">
                  {chat.name.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">{chat.name}</span>
                  <span className="text-xs text-gray-500">{chat.time}</span>
                </div>
                <p className="text-xs text-gray-600">{chat.lastMessage}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'home':
        return renderHomeTab();
      case 'analytics':
        return renderAnalyticsTab();
      case 'team':
        return renderTeamTab();
      case 'documents':
        return renderDocumentsTab();
      case 'calendar':
        return renderCalendarTab();
      case 'chat':
        return renderChatTab();
      default:
        return renderHomeTab();
    }
  };

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <DevicePhoneMobileIcon className="w-6 h-6 text-blue-600" />
            <h1 className="text-lg font-semibold text-gray-900">Mobile ERP</h1>
          </div>
          
          <div className="flex items-center space-x-2">
            {isOnline ? (
              <WifiIcon className="w-5 h-5 text-green-500" />
            ) : (
              <WifiSlashIcon className="w-5 h-5 text-red-500" />
            )}
            
            <button className="p-2 text-gray-400 hover:text-gray-600">
              <BellIcon className="w-5 h-5" />
            </button>
            
            <button className="p-2 text-gray-400 hover:text-gray-600">
              <CogIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="px-4 py-4">
        {renderTabContent()}
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200">
        <div className="grid grid-cols-6 gap-1">
          {[
            { id: 'home', label: 'Home', icon: HomeIcon },
            { id: 'analytics', label: 'Analytics', icon: ChartBarIcon },
            { id: 'team', label: 'Team', icon: UserGroupIcon },
            { id: 'documents', label: 'Docs', icon: DocumentTextIcon },
            { id: 'calendar', label: 'Calendar', icon: CalendarIcon },
            { id: 'chat', label: 'Chat', icon: ChatBubbleLeftRightIcon }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id as typeof activeTab)}
              className={`flex flex-col items-center space-y-1 py-2 px-1 ${
                activeTab === tab.id
                  ? 'text-blue-600'
                  : 'text-gray-400'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              <span className="text-xs font-medium">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Install Prompt */}
      {!isInstalled && (
        <div className="fixed top-16 left-4 right-4 bg-blue-600 text-white rounded-lg p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">Install ERP Mobile App</h3>
              <p className="text-sm text-blue-100">Get the full mobile experience</p>
            </div>
            <button
              onClick={handleInstall}
              className="bg-white text-blue-600 px-4 py-2 rounded-lg text-sm font-medium"
            >
              Install
            </button>
          </div>
        </div>
      )}

      {/* Camera Modal */}
      {showCamera && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-sm mx-4">
            <h3 className="text-lg font-semibold mb-4">Camera</h3>
            <div className="bg-gray-100 rounded-lg h-48 flex items-center justify-center mb-4">
              <CameraIcon className="w-12 h-12 text-gray-400" />
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowCamera(false)}
                className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowCamera(false)}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg"
              >
                Capture
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Voice Modal */}
      {showVoice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-sm mx-4">
            <h3 className="text-lg font-semibold mb-4">Voice Input</h3>
            <div className="bg-gray-100 rounded-lg h-48 flex items-center justify-center mb-4">
              <MicrophoneIcon className="w-12 h-12 text-gray-400" />
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowVoice(false)}
                className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowVoice(false)}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg"
              >
                Record
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PWADashboard;
