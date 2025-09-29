import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  UsersIcon, 
  UserPlusIcon,
  ChartBarIcon,
  DocumentTextIcon,
  CalendarDaysIcon,
  TrendingUpIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  FunnelIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';

const CRM: React.FC = () => {
  const location = useLocation();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  const [customers] = useState([
    {
      id: 1,
      name: 'Acme Corporation',
      email: 'contact@acme.com',
      phone: '+1 (555) 123-4567',
      status: 'Active',
      priority: 'High',
      healthScore: 85,
      lastActivity: '2 hours ago',
      totalSpent: 150000,
      opportunities: 3,
      avatar: 'AC'
    },
    {
      id: 2,
      name: 'TechStart Inc',
      email: 'info@techstart.com',
      phone: '+1 (555) 234-5678',
      status: 'Active',
      priority: 'Medium',
      healthScore: 92,
      lastActivity: '1 day ago',
      totalSpent: 45000,
      opportunities: 1,
      avatar: 'TI'
    },
    {
      id: 3,
      name: 'Global Solutions Ltd',
      email: 'sales@globalsolutions.com',
      phone: '+1 (555) 345-6789',
      status: 'At Risk',
      priority: 'High',
      healthScore: 45,
      lastActivity: '2 weeks ago',
      totalSpent: 200000,
      opportunities: 0,
      avatar: 'GS'
    }
  ]);

  const [opportunities] = useState([
    {
      id: 1,
      title: 'Enterprise Software License',
      customer: 'Acme Corporation',
      value: 50000,
      stage: 'Proposal',
      probability: 75,
      closeDate: '2024-02-15',
      owner: 'John Doe'
    },
    {
      id: 2,
      title: 'Cloud Migration Project',
      customer: 'TechStart Inc',
      value: 25000,
      stage: 'Negotiation',
      probability: 60,
      closeDate: '2024-01-30',
      owner: 'Jane Smith'
    },
    {
      id: 3,
      title: 'Consulting Services',
      customer: 'Global Solutions Ltd',
      value: 15000,
      stage: 'Qualification',
      probability: 40,
      closeDate: '2024-03-01',
      owner: 'Mike Johnson'
    }
  ]);

  const [leads] = useState([
    {
      id: 1,
      name: 'Sarah Wilson',
      company: 'Innovation Labs',
      email: 'sarah@innovationlabs.com',
      phone: '+1 (555) 456-7890',
      source: 'Website',
      status: 'New',
      score: 85,
      createdAt: '2024-01-15'
    },
    {
      id: 2,
      name: 'Michael Brown',
      company: 'Digital Dynamics',
      email: 'michael@digitaldynamics.com',
      phone: '+1 (555) 567-8901',
      source: 'Referral',
      status: 'Qualified',
      score: 72,
      createdAt: '2024-01-14'
    }
  ]);

  const crmModules = [
    {
      id: 'customers',
      name: 'Customer Management',
      description: 'Manage customer relationships and 360° views',
      icon: UsersIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      stats: { total: 1247, active: 1156, atRisk: 91 },
      link: '/crm/customers',
      features: ['Customer 360° View', 'Health Scoring', 'Activity Tracking', 'Communication History']
    },
    {
      id: 'opportunities',
      name: 'Opportunity Management',
      description: 'Track sales opportunities and pipeline',
      icon: TrendingUpIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      stats: { total: 156, open: 89, won: 45, lost: 22 },
      link: '/crm/opportunities',
      features: ['Sales Pipeline', 'Deal Tracking', 'Forecasting', 'Activity Management']
    },
    {
      id: 'leads',
      name: 'Lead Management',
      description: 'Capture and qualify leads',
      icon: UserPlusIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      stats: { total: 234, new: 45, qualified: 89, converted: 23 },
      link: '/crm/leads',
      features: ['Lead Capture', 'Scoring', 'Qualification', 'Nurturing']
    },
    {
      id: 'contacts',
      name: 'Contact Management',
      description: 'Manage contact information and relationships',
      icon: UsersIcon,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      borderColor: 'border-indigo-200',
      stats: { total: 3456, active: 2890, inactive: 566 },
      link: '/crm/contacts',
      features: ['Contact Profiles', 'Communication', 'Relationships', 'Analytics']
    },
    {
      id: 'quotations',
      name: 'Quotation Management',
      description: 'Create and manage quotations',
      icon: DocumentTextIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      stats: { total: 89, draft: 12, sent: 45, approved: 23 },
      link: '/crm/quotations',
      features: ['Quote Creation', 'Templates', 'Approval Workflow', 'Tracking']
    },
    {
      id: 'forecasting',
      name: 'Sales Forecasting',
      description: 'Predict and plan sales performance',
      icon: ChartBarIcon,
      color: 'text-teal-600',
      bgColor: 'bg-teal-50',
      borderColor: 'border-teal-200',
      stats: { target: 500000, achieved: 350000, forecast: 420000 },
      link: '/crm/forecasting',
      features: ['Revenue Forecasting', 'Target Tracking', 'AI Predictions', 'Dashboards']
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'at risk': return 'bg-red-100 text-red-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredCustomers = customers.filter(customer => {
    const matchesSearch = customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         customer.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || customer.status.toLowerCase() === filterStatus.toLowerCase();
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Customer Relationship Management</h1>
          <p className="text-neutral-600">Manage customers, opportunities, and sales pipeline</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn btn-primary">
            <PlusIcon className="w-4 h-4" />
            Add Customer
          </button>
          <button className="btn btn-outline">
            <FunnelIcon className="w-4 h-4" />
            Filters
          </button>
        </div>
      </div>

      {/* CRM Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {crmModules.map((module) => {
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
              
              <div className="space-y-2 mb-4">
                {Object.entries(module.stats).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-neutral-600 capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                    <span className="font-medium text-neutral-900">{value.toLocaleString()}</span>
                  </div>
                ))}
              </div>

              <div className="space-y-1">
                <p className="text-xs font-medium text-neutral-500 uppercase tracking-wide">Key Features</p>
                <div className="flex flex-wrap gap-1">
                  {module.features.slice(0, 2).map((feature) => (
                    <span key={feature} className="text-xs bg-neutral-100 text-neutral-600 px-2 py-1 rounded">
                      {feature}
                    </span>
                  ))}
                  {module.features.length > 2 && (
                    <span className="text-xs text-neutral-400">+{module.features.length - 2} more</span>
                  )}
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg p-6 border border-neutral-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-600">Total Customers</p>
              <p className="text-2xl font-bold text-neutral-900">1,247</p>
            </div>
            <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
              <UsersIcon className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <div className="flex items-center mt-2">
            <span className="text-sm text-green-600">+12% from last month</span>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 border border-neutral-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-600">Open Opportunities</p>
              <p className="text-2xl font-bold text-neutral-900">89</p>
            </div>
            <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
              <TrendingUpIcon className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="flex items-center mt-2">
            <span className="text-sm text-blue-600">$2.4M pipeline value</span>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 border border-neutral-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-600">New Leads</p>
              <p className="text-2xl font-bold text-neutral-900">45</p>
            </div>
            <div className="w-12 h-12 bg-purple-50 rounded-lg flex items-center justify-center">
              <UserPlusIcon className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <div className="flex items-center mt-2">
            <span className="text-sm text-purple-600">This week</span>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 border border-neutral-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-neutral-600">Conversion Rate</p>
              <p className="text-2xl font-bold text-neutral-900">23%</p>
            </div>
            <div className="w-12 h-12 bg-orange-50 rounded-lg flex items-center justify-center">
              <ChartBarIcon className="w-6 h-6 text-orange-600" />
            </div>
          </div>
          <div className="flex items-center mt-2">
            <span className="text-sm text-orange-600">+3% from last month</span>
          </div>
        </div>
      </div>

      {/* Recent Customers */}
      <div className="bg-white rounded-lg border border-neutral-200">
        <div className="p-6 border-b border-neutral-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-neutral-900">Recent Customers</h3>
            <div className="flex items-center gap-3">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400" />
                <input
                  type="text"
                  placeholder="Search customers..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="at risk">At Risk</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-neutral-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Customer</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Priority</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Health Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Total Spent</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Last Activity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-neutral-200">
              {filteredCustomers.map((customer) => (
                <tr key={customer.id} className="hover:bg-neutral-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-medium text-sm">
                        {customer.avatar}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-neutral-900">{customer.name}</div>
                        <div className="text-sm text-neutral-500">{customer.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(customer.status)}`}>
                      {customer.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(customer.priority)}`}>
                      {customer.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-neutral-200 rounded-full h-2 mr-2">
                        <div 
                          className={`h-2 rounded-full ${
                            customer.healthScore >= 80 ? 'bg-green-500' :
                            customer.healthScore >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${customer.healthScore}%` }}
                        />
                      </div>
                      <span className="text-sm text-neutral-900">{customer.healthScore}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-900">
                    ${customer.totalSpent.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
                    {customer.lastActivity}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center gap-2">
                      <Link
                        to={`/crm/customer-360/${customer.id}`}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        <EyeIcon className="w-4 h-4" />
                      </Link>
                      <button className="text-neutral-600 hover:text-neutral-900">
                        <PencilIcon className="w-4 h-4" />
                      </button>
                      <button className="text-red-600 hover:text-red-900">
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default CRM;
