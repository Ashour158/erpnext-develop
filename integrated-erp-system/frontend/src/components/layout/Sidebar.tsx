import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  UsersIcon, 
  CurrencyDollarIcon, 
  UserGroupIcon,
  ChatBubbleLeftRightIcon,
  CalendarDaysIcon,
  WrenchScrewdriverIcon,
  TruckIcon,
  Cog6ToothIcon,
  ChartBarIcon,
  BellIcon,
  UserIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';

interface SidebarProps {
  collapsed: boolean;
  currentModule: string;
  onModuleChange: (module: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, currentModule, onModuleChange }) => {
  const location = useLocation();

  const modules = [
    {
      id: 'dashboard',
      name: 'Dashboard',
      icon: HomeIcon,
      path: '/dashboard',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      description: 'Overview and analytics'
    },
    {
      id: 'crm',
      name: 'CRM',
      icon: UsersIcon,
      path: '/crm',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      description: 'Customer relationship management',
      submodules: [
        { name: 'Customer 360°', path: '/crm/customer-360' },
        { name: 'Opportunities', path: '/crm/opportunities' },
        { name: 'Leads', path: '/crm/leads' },
        { name: 'Contacts', path: '/crm/contacts' },
        { name: 'Quotations', path: '/crm/quotations' },
        { name: 'Forecasting', path: '/crm/forecasting' }
      ]
    },
    {
      id: 'finance',
      name: 'Finance',
      icon: CurrencyDollarIcon,
      path: '/finance',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      description: 'Financial management',
      submodules: [
        { name: 'Financial Statements', path: '/finance/statements' },
        { name: 'Multi-Currency', path: '/finance/multi-currency' },
        { name: 'Invoicing', path: '/finance/invoicing' },
        { name: 'Journal Entries', path: '/finance/journals' }
      ]
    },
    {
      id: 'people',
      name: 'People',
      icon: UserGroupIcon,
      path: '/people',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      description: 'Human resources management',
      submodules: [
        { name: 'Employee Management', path: '/people/employees' },
        { name: 'Leave Management', path: '/people/leave' },
        { name: 'KPI Management', path: '/people/kpi' },
        { name: 'Attendance', path: '/people/attendance' }
      ]
    },
    {
      id: 'moments',
      name: 'Moments',
      icon: ChatBubbleLeftRightIcon,
      path: '/moments',
      color: 'text-pink-600',
      bgColor: 'bg-pink-50',
      description: 'Social collaboration platform',
      submodules: [
        { name: 'Feed', path: '/moments/feed' },
        { name: 'Posts', path: '/moments/posts' },
        { name: 'Gallery', path: '/moments/gallery' }
      ]
    },
    {
      id: 'booking',
      name: 'Booking',
      icon: CalendarDaysIcon,
      path: '/booking',
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      description: 'Meeting and resource booking',
      submodules: [
        { name: 'Calendar', path: '/booking/calendar' },
        { name: 'Meetings', path: '/booking/meetings' },
        { name: 'Resources', path: '/booking/resources' }
      ]
    },
    {
      id: 'maintenance',
      name: 'Maintenance',
      icon: WrenchScrewdriverIcon,
      path: '/maintenance',
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      description: 'Asset and maintenance management',
      submodules: [
        { name: 'Tickets', path: '/maintenance/tickets' },
        { name: 'Assets', path: '/maintenance/assets' },
        { name: 'Preventive', path: '/maintenance/preventive' }
      ]
    },
    {
      id: 'supply-chain',
      name: 'Supply Chain',
      icon: TruckIcon,
      path: '/supply-chain',
      color: 'text-teal-600',
      bgColor: 'bg-teal-50',
      description: 'Supply chain and inventory',
      submodules: [
        { name: 'Inventory', path: '/supply-chain/inventory' },
        { name: 'Purchase Orders', path: '/supply-chain/purchase-orders' },
        { name: 'Suppliers', path: '/supply-chain/suppliers' }
      ]
    }
  ];

  const isActive = (path: string) => {
    return location.pathname.startsWith(path);
  };

  const handleModuleClick = (moduleId: string) => {
    onModuleChange(moduleId);
  };

  return (
    <div className={`fixed left-0 top-0 h-full bg-white border-r border-neutral-200 transition-all duration-300 z-40 ${
      collapsed ? 'w-16' : 'w-64'
    }`}>
      {/* Logo and Brand */}
      <div className="p-4 border-b border-neutral-200">
        {collapsed ? (
          <div className="flex items-center justify-center">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">E</span>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">E</span>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-neutral-900">ERP System</h1>
              <p className="text-xs text-neutral-500">Independent Platform</p>
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        <div className="px-4 space-y-2">
          {modules.map((module) => {
            const Icon = module.icon;
            const isModuleActive = isActive(module.path);
            const isExpanded = currentModule === module.id;

            return (
              <div key={module.id}>
                {/* Main Module Link */}
                <Link
                  to={module.path}
                  onClick={() => handleModuleClick(module.id)}
                  className={`group flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200 ${
                    isModuleActive
                      ? `${module.bgColor} ${module.color} shadow-sm`
                      : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${isModuleActive ? module.color : 'text-neutral-500'}`} />
                  {!collapsed && (
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm">{module.name}</div>
                      <div className="text-xs text-neutral-500 truncate">{module.description}</div>
                    </div>
                  )}
                </Link>

                {/* Submodules */}
                {!collapsed && isExpanded && module.submodules && (
                  <div className="ml-8 mt-2 space-y-1">
                    {module.submodules.map((submodule) => (
                      <Link
                        key={submodule.path}
                        to={submodule.path}
                        className={`block px-3 py-2 text-sm rounded-md transition-all duration-200 ${
                          isActive(submodule.path)
                            ? 'bg-blue-50 text-blue-700 font-medium'
                            : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900'
                        }`}
                      >
                        {submodule.name}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </nav>

      {/* User Section */}
      <div className="border-t border-neutral-200 p-4">
        {collapsed ? (
          <div className="flex items-center justify-center">
            <div className="w-8 h-8 bg-neutral-200 rounded-full flex items-center justify-center">
              <UserIcon className="w-4 h-4 text-neutral-600" />
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white font-medium text-sm">A</span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-medium text-sm text-neutral-900">Ahmed Ashour</div>
              <div className="text-xs text-neutral-500">System Administrator</div>
            </div>
            <div className="flex items-center gap-1">
              <button className="p-1 text-neutral-400 hover:text-neutral-600 transition-colors">
                <BellIcon className="w-4 h-4" />
              </button>
              <button className="p-1 text-neutral-400 hover:text-neutral-600 transition-colors">
                <Cog6ToothIcon className="w-4 h-4" />
              </button>
              <button className="p-1 text-neutral-400 hover:text-neutral-600 transition-colors">
                <ArrowRightOnRectangleIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
