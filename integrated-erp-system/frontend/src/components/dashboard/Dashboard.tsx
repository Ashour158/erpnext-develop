import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  UsersIcon, 
  CurrencyDollarIcon, 
  UserGroupIcon,
  ChatBubbleLeftRightIcon,
  CalendarDaysIcon,
  WrenchScrewdriverIcon,
  TruckIcon,
  ChartBarIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({
    totalCustomers: 1247,
    totalRevenue: 2450000,
    totalEmployees: 156,
    activeTickets: 23,
    pendingApprovals: 8,
    systemHealth: 98.5
  });

  const [recentActivities, setRecentActivities] = useState([
    {
      id: 1,
      type: 'customer',
      title: 'New customer registered',
      description: 'Acme Corporation has been added to CRM',
      time: '2 minutes ago',
      icon: UsersIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      id: 2,
      type: 'maintenance',
      title: 'Maintenance ticket created',
      description: 'Server maintenance scheduled for tonight',
      time: '1 hour ago',
      icon: WrenchScrewdriverIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50'
    },
    {
      id: 3,
      type: 'finance',
      title: 'Payment received',
      description: 'Payment of $5,000 received from TechStart Inc',
      time: '3 hours ago',
      icon: CurrencyDollarIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      id: 4,
      type: 'people',
      title: 'Leave request submitted',
      description: 'John Doe submitted a leave request for next week',
      time: '5 hours ago',
      icon: UserGroupIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    }
  ]);

  const [quickActions] = useState([
    {
      title: 'Add New Customer',
      description: 'Register a new customer in CRM',
      icon: UsersIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      link: '/crm',
      action: 'create-customer'
    },
    {
      title: 'Create Invoice',
      description: 'Generate a new invoice',
      icon: CurrencyDollarIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      link: '/finance/invoicing',
      action: 'create-invoice'
    },
    {
      title: 'Schedule Meeting',
      description: 'Book a meeting with team members',
      icon: CalendarDaysIcon,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      link: '/booking/calendar',
      action: 'schedule-meeting'
    },
    {
      title: 'Create Ticket',
      description: 'Submit a maintenance ticket',
      icon: WrenchScrewdriverIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      link: '/maintenance/tickets',
      action: 'create-ticket'
    }
  ]);

  const [systemAlerts] = useState([
    {
      id: 1,
      type: 'warning',
      title: 'Database backup overdue',
      description: 'Last backup was 3 days ago. Schedule a backup soon.',
      icon: ExclamationTriangleIcon,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50'
    },
    {
      id: 2,
      type: 'info',
      title: 'System update available',
      description: 'Version 2.1.0 is available for download.',
      icon: InformationCircleIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      id: 3,
      type: 'success',
      title: 'All systems operational',
      description: 'All modules are running smoothly.',
      icon: CheckCircleIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    }
  ]);

  const modules = [
    {
      id: 'crm',
      name: 'CRM',
      description: 'Customer Relationship Management',
      icon: UsersIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      stats: { total: 1247, new: 23, active: 1156 },
      link: '/crm'
    },
    {
      id: 'finance',
      name: 'Finance',
      description: 'Financial Management',
      icon: CurrencyDollarIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      stats: { revenue: 2450000, invoices: 156, pending: 8 },
      link: '/finance'
    },
    {
      id: 'people',
      name: 'People',
      description: 'Human Resources',
      icon: UserGroupIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      stats: { employees: 156, onLeave: 12, active: 144 },
      link: '/people'
    },
    {
      id: 'moments',
      name: 'Moments',
      description: 'Social Collaboration',
      icon: ChatBubbleLeftRightIcon,
      color: 'text-pink-600',
      bgColor: 'bg-pink-50',
      borderColor: 'border-pink-200',
      stats: { posts: 89, likes: 1247, comments: 234 },
      link: '/moments'
    },
    {
      id: 'booking',
      name: 'Booking',
      description: 'Meeting & Resource Booking',
      icon: CalendarDaysIcon,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      borderColor: 'border-indigo-200',
      stats: { meetings: 23, resources: 8, pending: 3 },
      link: '/booking'
    },
    {
      id: 'maintenance',
      name: 'Maintenance',
      description: 'Asset & Maintenance',
      icon: WrenchScrewdriverIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      stats: { tickets: 23, assets: 156, scheduled: 8 },
      link: '/maintenance'
    },
    {
      id: 'supply-chain',
      name: 'Supply Chain',
      description: 'Supply Chain Management',
      icon: TruckIcon,
      color: 'text-teal-600',
      bgColor: 'bg-teal-50',
      borderColor: 'border-teal-200',
      stats: { orders: 45, suppliers: 23, inventory: 156 },
      link: '/supply-chain'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">Welcome back, Ahmed!</h1>
            <p className="text-blue-100">
              Here's what's happening in your ERP system today.
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{stats.systemHealth}%</div>
            <div className="text-blue-100 text-sm">System Health</div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg p-6 border border-neutral-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-600">Total Customers</p>
              <p className="text-2xl font-bold text-neutral-900">{stats.totalCustomers.toLocaleString()}</p>
            </div>
            <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
              <UsersIcon className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <div className="flex items-center mt-2">
            <TrendingUpIcon className="w-4 h-4 text-green-500 mr-1" />
            <span className="text-sm text-green-600">+12% from last month</span>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 border border-neutral-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-600">Total Revenue</p>
              <p className="text-2xl font-bold text-neutral-900">${(stats.totalRevenue / 1000000).toFixed(1)}M</p>
            </div>
            <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
              <CurrencyDollarIcon className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="flex items-center mt-2">
            <TrendingUpIcon className="w-4 h-4 text-green-500 mr-1" />
            <span className="text-sm text-green-600">+8% from last month</span>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 border border-neutral-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-600">Active Tickets</p>
              <p className="text-2xl font-bold text-neutral-900">{stats.activeTickets}</p>
            </div>
            <div className="w-12 h-12 bg-orange-50 rounded-lg flex items-center justify-center">
              <WrenchScrewdriverIcon className="w-6 h-6 text-orange-600" />
            </div>
          </div>
          <div className="flex items-center mt-2">
            <TrendingDownIcon className="w-4 h-4 text-green-500 mr-1" />
            <span className="text-sm text-green-600">-3 from yesterday</span>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 border border-neutral-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-600">Pending Approvals</p>
              <p className="text-2xl font-bold text-neutral-900">{stats.pendingApprovals}</p>
            </div>
            <div className="w-12 h-12 bg-yellow-50 rounded-lg flex items-center justify-center">
              <ClockIcon className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
          <div className="flex items-center mt-2">
            <span className="text-sm text-neutral-500">Requires attention</span>
          </div>
        </div>
      </div>

      {/* Modules Grid */}
      <div>
        <h2 className="text-xl font-semibold text-neutral-900 mb-4">Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {modules.map((module) => {
            const Icon = module.icon;
            return (
              <Link
                key={module.id}
                to={module.link}
                className="group bg-white rounded-lg p-6 border border-neutral-200 hover:border-neutral-300 hover:shadow-lg transition-all duration-200"
              >
                <div className="flex items-center gap-4 mb-4">
                  <div className={`w-12 h-12 ${module.bgColor} rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-200`}>
                    <Icon className={`w-6 h-6 ${module.color}`} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-neutral-900">{module.name}</h3>
                    <p className="text-sm text-neutral-500">{module.description}</p>
                  </div>
                </div>
                <div className="space-y-2">
                  {Object.entries(module.stats).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-neutral-600 capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                      <span className="font-medium text-neutral-900">{value.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-neutral-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.action}
                to={action.link}
                className="group bg-white rounded-lg p-4 border border-neutral-200 hover:border-neutral-300 hover:shadow-md transition-all duration-200"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 ${action.bgColor} rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-200`}>
                    <Icon className={`w-5 h-5 ${action.color}`} />
                  </div>
                  <div>
                    <h3 className="font-medium text-neutral-900 text-sm">{action.title}</h3>
                    <p className="text-xs text-neutral-500">{action.description}</p>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recent Activity & Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="bg-white rounded-lg border border-neutral-200">
          <div className="p-6 border-b border-neutral-200">
            <h3 className="text-lg font-semibold text-neutral-900">Recent Activity</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {recentActivities.map((activity) => {
                const Icon = activity.icon;
                return (
                  <div key={activity.id} className="flex items-start gap-3">
                    <div className={`w-8 h-8 ${activity.bgColor} rounded-lg flex items-center justify-center`}>
                      <Icon className={`w-4 h-4 ${activity.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-neutral-900 text-sm">{activity.title}</h4>
                      <p className="text-neutral-600 text-sm mt-1">{activity.description}</p>
                      <p className="text-neutral-400 text-xs mt-1">{activity.time}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* System Alerts */}
        <div className="bg-white rounded-lg border border-neutral-200">
          <div className="p-6 border-b border-neutral-200">
            <h3 className="text-lg font-semibold text-neutral-900">System Alerts</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {systemAlerts.map((alert) => {
                const Icon = alert.icon;
                return (
                  <div key={alert.id} className="flex items-start gap-3">
                    <div className={`w-8 h-8 ${alert.bgColor} rounded-lg flex items-center justify-center`}>
                      <Icon className={`w-4 h-4 ${alert.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-neutral-900 text-sm">{alert.title}</h4>
                      <p className="text-neutral-600 text-sm mt-1">{alert.description}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
