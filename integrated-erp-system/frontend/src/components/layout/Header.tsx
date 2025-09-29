import React, { useState } from 'react';
import { 
  Bars3Icon, 
  MagnifyingGlassIcon, 
  BellIcon, 
  UserIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  SunIcon,
  MoonIcon,
  ComputerDesktopIcon
} from '@heroicons/react/24/outline';

interface HeaderProps {
  onToggleSidebar: () => void;
  currentModule: string;
}

const Header: React.FC<HeaderProps> = ({ onToggleSidebar, currentModule }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    // Toggle dark mode class on document
    document.documentElement.classList.toggle('dark');
  };

  const notifications = [
    {
      id: 1,
      title: 'New customer registered',
      message: 'Acme Corporation has been added to CRM',
      time: '2 minutes ago',
      type: 'success'
    },
    {
      id: 2,
      title: 'Maintenance ticket created',
      message: 'Server maintenance scheduled for tonight',
      time: '1 hour ago',
      type: 'warning'
    },
    {
      id: 3,
      title: 'Payment received',
      message: 'Payment of $5,000 received from TechStart Inc',
      time: '3 hours ago',
      type: 'info'
    }
  ];

  const getModuleTitle = (module: string) => {
    const titles: { [key: string]: string } = {
      dashboard: 'Dashboard',
      crm: 'Customer Relationship Management',
      finance: 'Financial Management',
      people: 'Human Resources',
      moments: 'Social Collaboration',
      booking: 'Meeting & Resource Booking',
      maintenance: 'Asset & Maintenance',
      'supply-chain': 'Supply Chain Management'
    };
    return titles[module] || 'ERP System';
  };

  return (
    <header className="bg-white border-b border-neutral-200 px-6 py-4 flex items-center justify-between">
      {/* Left Section */}
      <div className="flex items-center gap-4">
        <button
          onClick={onToggleSidebar}
          className="p-2 text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 rounded-lg transition-all duration-200"
        >
          <Bars3Icon className="w-5 h-5" />
        </button>

        <div>
          <h1 className="text-xl font-semibold text-neutral-900">
            {getModuleTitle(currentModule)}
          </h1>
          <p className="text-sm text-neutral-500">
            Welcome back! Here's what's happening today.
          </p>
        </div>
      </div>

      {/* Center Section - Search */}
      <div className="flex-1 max-w-md mx-8">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400" />
          <input
            type="text"
            placeholder="Search across all modules..."
            className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg bg-neutral-50 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all duration-200"
          />
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-2">
        {/* Dark Mode Toggle */}
        <div className="flex items-center bg-neutral-100 rounded-lg p-1">
          <button
            onClick={toggleDarkMode}
            className={`p-1 rounded-md transition-all duration-200 ${
              isDarkMode ? 'bg-white shadow-sm' : 'text-neutral-500'
            }`}
          >
            <MoonIcon className="w-4 h-4" />
          </button>
          <button
            onClick={toggleDarkMode}
            className={`p-1 rounded-md transition-all duration-200 ${
              !isDarkMode ? 'bg-white shadow-sm' : 'text-neutral-500'
            }`}
          >
            <SunIcon className="w-4 h-4" />
          </button>
          <button
            onClick={toggleDarkMode}
            className="p-1 rounded-md transition-all duration-200 text-neutral-500"
          >
            <ComputerDesktopIcon className="w-4 h-4" />
          </button>
        </div>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 rounded-lg transition-all duration-200"
          >
            <BellIcon className="w-5 h-5" />
            {notifications.length > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {notifications.length}
              </span>
            )}
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 top-full mt-2 w-80 bg-white border border-neutral-200 rounded-lg shadow-lg z-50">
              <div className="p-4 border-b border-neutral-200">
                <h3 className="font-semibold text-neutral-900">Notifications</h3>
                <p className="text-sm text-neutral-500">{notifications.length} new notifications</p>
              </div>
              <div className="max-h-96 overflow-y-auto">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className="p-4 border-b border-neutral-100 hover:bg-neutral-50 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-2 h-2 rounded-full mt-2 ${
                        notification.type === 'success' ? 'bg-green-500' :
                        notification.type === 'warning' ? 'bg-yellow-500' :
                        notification.type === 'error' ? 'bg-red-500' :
                        'bg-blue-500'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-neutral-900 text-sm">
                          {notification.title}
                        </h4>
                        <p className="text-neutral-600 text-sm mt-1">
                          {notification.message}
                        </p>
                        <p className="text-neutral-400 text-xs mt-1">
                          {notification.time}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="p-4 border-t border-neutral-200">
                <button className="w-full text-center text-blue-600 hover:text-blue-700 font-medium text-sm">
                  View all notifications
                </button>
              </div>
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-3 p-2 text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 rounded-lg transition-all duration-200"
          >
            <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white font-medium text-sm">A</span>
            </div>
            <div className="text-left">
              <div className="font-medium text-sm text-neutral-900">Ahmed Ashour</div>
              <div className="text-xs text-neutral-500">System Administrator</div>
            </div>
          </button>

          {/* User Menu Dropdown */}
          {showUserMenu && (
            <div className="absolute right-0 top-full mt-2 w-56 bg-white border border-neutral-200 rounded-lg shadow-lg z-50">
              <div className="p-4 border-b border-neutral-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-medium">A</span>
                  </div>
                  <div>
                    <div className="font-medium text-neutral-900">Ahmed Ashour</div>
                    <div className="text-sm text-neutral-500">ahmed@company.com</div>
                  </div>
                </div>
              </div>
              <div className="py-2">
                <button className="w-full flex items-center gap-3 px-4 py-2 text-neutral-700 hover:bg-neutral-50 transition-colors">
                  <UserIcon className="w-4 h-4" />
                  Profile Settings
                </button>
                <button className="w-full flex items-center gap-3 px-4 py-2 text-neutral-700 hover:bg-neutral-50 transition-colors">
                  <Cog6ToothIcon className="w-4 h-4" />
                  System Settings
                </button>
                <div className="border-t border-neutral-200 my-2" />
                <button className="w-full flex items-center gap-3 px-4 py-2 text-red-600 hover:bg-red-50 transition-colors">
                  <ArrowRightOnRectangleIcon className="w-4 h-4" />
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Click outside to close dropdowns */}
      {(showUserMenu || showNotifications) && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setShowUserMenu(false);
            setShowNotifications(false);
          }}
        />
      )}
    </header>
  );
};

export default Header;
