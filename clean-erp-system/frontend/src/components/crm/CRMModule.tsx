// CRM Module Component
// CRM module with integrated settings based on user role

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Tabs,
  Tab,
  AppBar,
  Toolbar,
  IconButton,
  Badge,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  Dashboard,
  People,
  Business,
  TrendingUp,
  Settings,
  Notifications,
  AccountCircle,
  MoreVert,
  Add,
  Search,
  FilterList,
  ViewModule,
  ViewList,
  ViewComfy
} from '@mui/icons-material';
import SettingsPanel from '../common/SettingsPanel';

interface CRMModuleProps {
  userRole: 'user' | 'admin' | 'super_admin';
  onModuleChange?: (module: string) => void;
}

const CRMModule: React.FC<CRMModuleProps> = ({ userRole, onModuleChange }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [showSettings, setShowSettings] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'table'>('grid');

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleSettingsClick = () => {
    setShowSettings(!showSettings);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleViewModeChange = (mode: 'grid' | 'list' | 'table') => {
    setViewMode(mode);
  };

  const renderDashboard = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Customers
                </Typography>
                <Typography variant="h4">1,234</Typography>
              </Box>
              <People color="primary" />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Active Opportunities
                </Typography>
                <Typography variant="h4">56</Typography>
              </Box>
              <TrendingUp color="primary" />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  This Month's Revenue
                </Typography>
                <Typography variant="h4">$45,678</Typography>
              </Box>
              <Business color="primary" />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Conversion Rate
                </Typography>
                <Typography variant="h4">23.5%</Typography>
              </Box>
              <TrendingUp color="primary" />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderCustomers = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Customers</Typography>
          <Box display="flex" gap={1}>
            <Button
              variant={viewMode === 'grid' ? 'contained' : 'outlined'}
              size="small"
              startIcon={<ViewComfy />}
              onClick={() => handleViewModeChange('grid')}
            >
              Grid
            </Button>
            <Button
              variant={viewMode === 'list' ? 'contained' : 'outlined'}
              size="small"
              startIcon={<ViewList />}
              onClick={() => handleViewModeChange('list')}
            >
              List
            </Button>
            <Button
              variant={viewMode === 'table' ? 'contained' : 'outlined'}
              size="small"
              startIcon={<ViewModule />}
              onClick={() => handleViewModeChange('table')}
            >
              Table
            </Button>
          </Box>
        </Box>
        <Typography>Customer management interface will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderOpportunities = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Opportunities</Typography>
        <Typography>Opportunity management interface will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderLeads = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Leads</Typography>
        <Typography>Lead management interface will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderReports = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Reports</Typography>
        <Typography>CRM reports and analytics will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 0:
        return renderDashboard();
      case 1:
        return renderCustomers();
      case 2:
        return renderOpportunities();
      case 3:
        return renderLeads();
      case 4:
        return renderReports();
      default:
        return null;
    }
  };

  if (showSettings) {
    return (
      <SettingsPanel
        moduleName="CRM"
        userRole={userRole}
        onSettingsChange={(settings) => {
          console.log('CRM Settings changed:', settings);
        }}
      />
    );
  }

  return (
    <Box>
      {/* Module Header */}
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Customer Relationship Management
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            <IconButton color="inherit">
              <Badge badgeContent={4} color="error">
                <Notifications />
              </Badge>
            </IconButton>
            <IconButton color="inherit" onClick={handleSettingsClick}>
              <Settings />
            </IconButton>
            <IconButton color="inherit" onClick={handleMenuClick}>
              <MoreVert />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Module Tabs */}
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Dashboard" icon={<Dashboard />} />
        <Tab label="Customers" icon={<People />} />
        <Tab label="Opportunities" icon={<TrendingUp />} />
        <Tab label="Leads" icon={<Business />} />
        <Tab label="Reports" icon={<TrendingUp />} />
      </Tabs>

      {/* Module Content */}
      {renderTabContent()}

      {/* User Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleMenuClose}>
          <ListItemIcon>
            <AccountCircle />
          </ListItemIcon>
          <ListItemText>Profile</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <ListItemIcon>
            <Settings />
          </ListItemIcon>
          <ListItemText>Settings</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleMenuClose}>
          <ListItemText>Logout</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default CRMModule;
