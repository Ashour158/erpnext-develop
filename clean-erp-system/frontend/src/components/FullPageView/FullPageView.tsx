# Full-Page View Component
# Comprehensive full-page views for all modules and submodules

import React, { useState, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Tabs,
  Tab,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Breadcrumbs,
  Link
} from '@mui/material';
import {
  Close as CloseIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Fullscreen as FullscreenIcon,
  ExitFullscreen as ExitFullscreenIcon
} from '@mui/icons-material';

interface FullPageViewProps {
  module: string;
  submodule?: string;
  entityId?: string;
  onClose: () => void;
  onRefresh?: () => void;
  onSettings?: () => void;
}

const FullPageView: React.FC<FullPageViewProps> = ({
  module,
  submodule,
  entityId,
  onClose,
  onRefresh,
  onSettings
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [module, submodule, entityId]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load data based on module and submodule
      const response = await fetch(`/api/${module}/${submodule || ''}${entityId ? `/${entityId}` : ''}`);
      const result = await response.json();
      setData(result.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const renderModuleContent = () => {
    switch (module) {
      case 'crm':
        return <CRMFullPageView submodule={submodule} data={data} />;
      case 'finance':
        return <FinanceFullPageView submodule={submodule} data={data} />;
      case 'people':
        return <PeopleFullPageView submodule={submodule} data={data} />;
      case 'supply_chain':
        return <SupplyChainFullPageView submodule={submodule} data={data} />;
      case 'maintenance':
        return <MaintenanceFullPageView submodule={submodule} data={data} />;
      case 'booking':
        return <BookingFullPageView submodule={submodule} data={data} />;
      case 'moments':
        return <MomentsFullPageView submodule={submodule} data={data} />;
      case 'ai':
        return <AIFullPageView submodule={submodule} data={data} />;
      case 'workflow':
        return <WorkflowFullPageView submodule={submodule} data={data} />;
      default:
        return <div>Module not found</div>;
    }
  };

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 1300,
        backgroundColor: 'background.default',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* Header */}
      <AppBar position="static" color="primary">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {module.toUpperCase()} {submodule && `- ${submodule.toUpperCase()}`}
          </Typography>
          
          <IconButton color="inherit" onClick={onRefresh}>
            <RefreshIcon />
          </IconButton>
          
          <IconButton color="inherit" onClick={onSettings}>
            <SettingsIcon />
          </IconButton>
          
          <IconButton color="inherit" onClick={toggleFullscreen}>
            {isFullscreen ? <ExitFullscreenIcon /> : <FullscreenIcon />}
          </IconButton>
          
          <IconButton color="inherit" onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Breadcrumbs */}
      <Box sx={{ px: 2, py: 1, backgroundColor: 'grey.100' }}>
        <Breadcrumbs>
          <Link color="inherit" href="/">
            Home
          </Link>
          <Link color="inherit" href={`/${module}`}>
            {module.toUpperCase()}
          </Link>
          {submodule && (
            <Typography color="text.primary">
              {submodule.toUpperCase()}
            </Typography>
          )}
        </Breadcrumbs>
      </Box>

      {/* Content */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <Typography>Loading...</Typography>
          </Box>
        ) : (
          renderModuleContent()
        )}
      </Box>
    </Box>
  );
};

// CRM Full Page View
const CRMFullPageView: React.FC<{ submodule?: string; data: any }> = ({ submodule, data }) => {
  const [activeTab, setActiveTab] = useState(0);

  const tabs = [
    { label: 'Overview', value: 0 },
    { label: 'Customers', value: 1 },
    { label: 'Contacts', value: 2 },
    { label: 'Opportunities', value: 3 },
    { label: 'Leads', value: 4 },
    { label: 'Reports', value: 5 }
  ];

  return (
    <Box sx={{ p: 2 }}>
      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
        {tabs.map(tab => (
          <Tab key={tab.value} label={tab.label} value={tab.value} />
        ))}
      </Tabs>

      <Box sx={{ mt: 2 }}>
        {activeTab === 0 && <CRMOverview />}
        {activeTab === 1 && <CRMCustomers />}
        {activeTab === 2 && <CRMContacts />}
        {activeTab === 3 && <CRMOpportunities />}
        {activeTab === 4 && <CRMLeads />}
        {activeTab === 5 && <CRMReports />}
      </Box>
    </Box>
  );
};

// Finance Full Page View
const FinanceFullPageView: React.FC<{ submodule?: string; data: any }> = ({ submodule, data }) => {
  const [activeTab, setActiveTab] = useState(0);

  const tabs = [
    { label: 'Dashboard', value: 0 },
    { label: 'Invoices', value: 1 },
    { label: 'Payments', value: 2 },
    { label: 'Journal Entries', value: 3 },
    { label: 'Reports', value: 4 },
    { label: 'Settings', value: 5 }
  ];

  return (
    <Box sx={{ p: 2 }}>
      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
        {tabs.map(tab => (
          <Tab key={tab.value} label={tab.label} value={tab.value} />
        ))}
      </Tabs>

      <Box sx={{ mt: 2 }}>
        {activeTab === 0 && <FinanceDashboard />}
        {activeTab === 1 && <FinanceInvoices />}
        {activeTab === 2 && <FinancePayments />}
        {activeTab === 3 && <FinanceJournalEntries />}
        {activeTab === 4 && <FinanceReports />}
        {activeTab === 5 && <FinanceSettings />}
      </Box>
    </Box>
  );
};

// People Full Page View
const PeopleFullPageView: React.FC<{ submodule?: string; data: any }> = ({ submodule, data }) => {
  const [activeTab, setActiveTab] = useState(0);

  const tabs = [
    { label: 'Dashboard', value: 0 },
    { label: 'Employees', value: 1 },
    { label: 'Departments', value: 2 },
    { label: 'Leave Management', value: 3 },
    { label: 'Attendance', value: 4 },
    { label: 'Payroll', value: 5 },
    { label: 'Performance', value: 6 }
  ];

  return (
    <Box sx={{ p: 2 }}>
      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
        {tabs.map(tab => (
          <Tab key={tab.value} label={tab.label} value={tab.value} />
        ))}
      </Tabs>

      <Box sx={{ mt: 2 }}>
        {activeTab === 0 && <PeopleDashboard />}
        {activeTab === 1 && <PeopleEmployees />}
        {activeTab === 2 && <PeopleDepartments />}
        {activeTab === 3 && <PeopleLeaveManagement />}
        {activeTab === 4 && <PeopleAttendance />}
        {activeTab === 5 && <PeoplePayroll />}
        {activeTab === 6 && <PeoplePerformance />}
      </Box>
    </Box>
  );
};

// Supply Chain Full Page View
const SupplyChainFullPageView: React.FC<{ submodule?: string; data: any }> = ({ submodule, data }) => {
  const [activeTab, setActiveTab] = useState(0);

  const tabs = [
    { label: 'Dashboard', value: 0 },
    { label: 'Inventory', value: 1 },
    { label: 'Suppliers', value: 2 },
    { label: 'Purchase Orders', value: 3 },
    { label: 'Sales Orders', value: 4 },
    { label: 'Reports', value: 5 }
  ];

  return (
    <Box sx={{ p: 2 }}>
      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
        {tabs.map(tab => (
          <Tab key={tab.value} label={tab.label} value={tab.value} />
        ))}
      </Tabs>

      <Box sx={{ mt: 2 }}>
        {activeTab === 0 && <SupplyChainDashboard />}
        {activeTab === 1 && <SupplyChainInventory />}
        {activeTab === 2 && <SupplyChainSuppliers />}
        {activeTab === 3 && <SupplyChainPurchaseOrders />}
        {activeTab === 4 && <SupplyChainSalesOrders />}
        {activeTab === 5 && <SupplyChainReports />}
      </Box>
    </Box>
  );
};

// Maintenance Full Page View
const MaintenanceFullPageView: React.FC<{ submodule?: string; data: any }> = ({ submodule, data }) => {
  const [activeTab, setActiveTab] = useState(0);

  const tabs = [
    { label: 'Dashboard', value: 0 },
    { label: 'Assets', value: 1 },
    { label: 'Work Orders', value: 2 },
    { label: 'Schedules', value: 3 },
    { label: 'Teams', value: 4 },
    { label: 'Reports', value: 5 }
  ];

  return (
    <Box sx={{ p: 2 }}>
      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
        {tabs.map(tab => (
          <Tab key={tab.value} label={tab.label} value={tab.value} />
        ))}
      </Tabs>

      <Box sx={{ mt: 2 }}>
        {activeTab === 0 && <MaintenanceDashboard />}
        {activeTab === 1 && <MaintenanceAssets />}
        {activeTab === 2 && <MaintenanceWorkOrders />}
        {activeTab === 3 && <MaintenanceSchedules />}
        {activeTab === 4 && <MaintenanceTeams />}
        {activeTab === 5 && <MaintenanceReports />}
      </Box>
    </Box>
  );
};

// Booking Full Page View
const BookingFullPageView: React.FC<{ submodule?: string; data: any }> = ({ submodule, data }) => {
  const [activeTab, setActiveTab] = useState(0);

  const tabs = [
    { label: 'Dashboard', value: 0 },
    { label: 'Resources', value: 1 },
    { label: 'Bookings', value: 2 },
    { label: 'Calendar', value: 3 },
    { label: 'Reports', value: 4 }
  ];

  return (
    <Box sx={{ p: 2 }}>
      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
        {tabs.map(tab => (
          <Tab key={tab.value} label={tab.label} value={tab.value} />
        ))}
      </Tabs>

      <Box sx={{ mt: 2 }}>
        {activeTab === 0 && <BookingDashboard />}
        {activeTab === 1 && <BookingResources />}
        {activeTab === 2 && <BookingBookings />}
        {activeTab === 3 && <BookingCalendar />}
        {activeTab === 4 && <BookingReports />}
      </Box>
    </Box>
  );
};

// Moments Full Page View
const MomentsFullPageView: React.FC<{ submodule?: string; data: any }> = ({ submodule, data }) => {
  const [activeTab, setActiveTab] = useState(0);

  const tabs = [
    { label: 'Feed', value: 0 },
    { label: 'Moments', value: 1 },
    { label: 'Profiles', value: 2 },
    { label: 'Notifications', value: 3 },
    { label: 'Analytics', value: 4 }
  ];

  return (
    <Box sx={{ p: 2 }}>
      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
        {tabs.map(tab => (
          <Tab key={tab.value} label={tab.label} value={tab.value} />
        ))}
      </Tabs>

      <Box sx={{ mt: 2 }}>
        {activeTab === 0 && <MomentsFeed />}
        {activeTab === 1 && <MomentsMoments />}
        {activeTab === 2 && <MomentsProfiles />}
        {activeTab === 3 && <MomentsNotifications />}
        {activeTab === 4 && <MomentsAnalytics />}
      </Box>
    </Box>
  );
};

// AI Full Page View
const AIFullPageView: React.FC<{ submodule?: string; data: any }> = ({ submodule, data }) => {
  const [activeTab, setActiveTab] = useState(0);

  const tabs = [
    { label: 'Dashboard', value: 0 },
    { label: 'Models', value: 1 },
    { label: 'Predictions', value: 2 },
    { label: 'Insights', value: 3 },
    { label: 'Analytics', value: 4 }
  ];

  return (
    <Box sx={{ p: 2 }}>
      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
        {tabs.map(tab => (
          <Tab key={tab.value} label={tab.label} value={tab.value} />
        ))}
      </Tabs>

      <Box sx={{ mt: 2 }}>
        {activeTab === 0 && <AIDashboard />}
        {activeTab === 1 && <AIModels />}
        {activeTab === 2 && <AIPredictions />}
        {activeTab === 3 && <AIInsights />}
        {activeTab === 4 && <AIAnalytics />}
      </Box>
    </Box>
  );
};

// Workflow Full Page View
const WorkflowFullPageView: React.FC<{ submodule?: string; data: any }> = ({ submodule, data }) => {
  const [activeTab, setActiveTab] = useState(0);

  const tabs = [
    { label: 'Dashboard', value: 0 },
    { label: 'Workflows', value: 1 },
    { label: 'Executions', value: 2 },
    { label: 'Templates', value: 3 },
    { label: 'Analytics', value: 4 }
  ];

  return (
    <Box sx={{ p: 2 }}>
      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
        {tabs.map(tab => (
          <Tab key={tab.value} label={tab.label} value={tab.value} />
        ))}
      </Tabs>

      <Box sx={{ mt: 2 }}>
        {activeTab === 0 && <WorkflowDashboard />}
        {activeTab === 1 && <WorkflowWorkflows />}
        {activeTab === 2 && <WorkflowExecutions />}
        {activeTab === 3 && <WorkflowTemplates />}
        {activeTab === 4 && <WorkflowAnalytics />}
      </Box>
    </Box>
  );
};

export default FullPageView;
