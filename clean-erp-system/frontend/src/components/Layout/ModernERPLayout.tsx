// Modern ERP Layout Component
// Three-part layout with top navigation, collapsible sidebar, and main content

import React, { useState, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon as ListIcon,
  ListItemText as ListText,
  Collapse,
  TextField,
  InputAdornment,
  Switch,
  FormControlLabel,
  useMediaQuery,
  useTheme,
  Tooltip,
  Chip
} from '@mui/material';
import {
  Menu as MenuIcon,
  Search,
  Notifications,
  AccountCircle,
  Settings,
  Logout,
  Dashboard,
  People,
  Business,
  Assignment,
  Inventory,
  Store,
  Event,
  Share,
  Timeline,
  Assessment,
  ExpandLess,
  ExpandMore,
  ChevronLeft,
  ChevronRight,
  Brightness4,
  Brightness7,
  MoreVert,
  Home,
  TrendingUp,
  Analytics,
  Support,
  Schedule,
  Description,
  CloudSync,
  CloudDone,
  CloudOff
} from '@mui/icons-material';

interface ModernERPLayoutProps {
  children: React.ReactNode;
  currentModule?: string;
  onModuleChange?: (module: string) => void;
  userRole?: 'user' | 'admin' | 'super_admin';
  darkMode?: boolean;
  onDarkModeToggle?: () => void;
}

const ModernERPLayout: React.FC<ModernERPLayoutProps> = ({
  children,
  currentModule = 'dashboard',
  onModuleChange,
  userRole = 'user',
  darkMode = false,
  onDarkModeToggle
}) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [realtimeStatus, setRealtimeStatus] = useState<'connected' | 'disconnected' | 'syncing'>('connected');
  const [notifications, setNotifications] = useState(4);
  const [searchQuery, setSearchQuery] = useState('');

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const drawerWidth = sidebarCollapsed ? 70 : 240;

  const modules = [
    { id: 'dashboard', label: 'Dashboard', icon: <Dashboard />, color: '#4A90E2' },
    { id: 'crm', label: 'CRM', icon: <People />, color: '#50E3C2' },
    { id: 'finance', label: 'Finance', icon: <Business />, color: '#4A90E2' },
    { id: 'desk', label: 'Desk', icon: <Assignment />, color: '#E95E5E' },
    { id: 'people', label: 'People', icon: <People />, color: '#50E3C2' },
    { id: 'supply_chain', label: 'Supply Chain', icon: <Inventory />, color: '#4A90E2' },
    { id: 'project_management', label: 'Projects', icon: <Assignment />, color: '#50E3C2' },
    { id: 'quality_management', label: 'Quality', icon: <Assessment />, color: '#E95E5E' },
    { id: 'business_intelligence', label: 'Analytics', icon: <Analytics />, color: '#4A90E2' },
    { id: 'marketing_automation', label: 'Marketing', icon: <Share />, color: '#50E3C2' },
    { id: 'booking', label: 'Booking', icon: <Event />, color: '#4A90E2' },
    { id: 'moments', label: 'Moments', icon: <Share />, color: '#50E3C2' },
    { id: 'workflow', label: 'Workflow', icon: <Timeline />, color: '#4A90E2' },
    { id: 'calendar', label: 'Calendar', icon: <Event />, color: '#50E3C2' }
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleSidebarToggle = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleModuleClick = (moduleId: string) => {
    onModuleChange?.(moduleId);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const getRealtimeIcon = () => {
    switch (realtimeStatus) {
      case 'connected':
        return <CloudDone color="success" />;
      case 'syncing':
        return <CloudSync color="warning" />;
      case 'disconnected':
        return <CloudOff color="error" />;
      default:
        return <CloudOff color="error" />;
    }
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Sidebar Header */}
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid #E0E0E0',
          minHeight: 64
        }}
      >
        {!sidebarCollapsed && (
          <Typography variant="h6" sx={{ color: '#333333', fontWeight: 600 }}>
            ERP System
          </Typography>
        )}
        <IconButton
          onClick={handleSidebarToggle}
          sx={{
            color: '#555555',
            '&:hover': { backgroundColor: 'rgba(74, 144, 226, 0.1)' }
          }}
        >
          {sidebarCollapsed ? <ChevronRight /> : <ChevronLeft />}
        </IconButton>
      </Box>

      {/* Navigation List */}
      <List sx={{ flexGrow: 1, px: 1, py: 2 }}>
        {modules.map((module) => (
          <ListItem key={module.id} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              onClick={() => handleModuleClick(module.id)}
              sx={{
                borderRadius: '8px',
                mb: 0.5,
                backgroundColor: currentModule === module.id ? 'rgba(74, 144, 226, 0.1)' : 'transparent',
                border: currentModule === module.id ? '1px solid rgba(74, 144, 226, 0.2)' : '1px solid transparent',
                '&:hover': {
                  backgroundColor: 'rgba(74, 144, 226, 0.05)',
                  transform: 'translateY(-1px)',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                },
                transition: 'all 150ms ease-in-out'
              }}
            >
              <ListIcon
                sx={{
                  color: currentModule === module.id ? module.color : '#555555',
                  minWidth: sidebarCollapsed ? 'auto' : 40,
                  mr: sidebarCollapsed ? 0 : 2
                }}
              >
                {module.icon}
              </ListIcon>
              {!sidebarCollapsed && (
                <ListText
                  primary={module.label}
                  sx={{
                    color: currentModule === module.id ? '#333333' : '#555555',
                    fontWeight: currentModule === module.id ? 600 : 400,
                    fontSize: '14px'
                  }}
                />
              )}
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      {/* Sidebar Footer */}
      <Box sx={{ p: 2, borderTop: '1px solid #E0E0E0' }}>
        <FormControlLabel
          control={
            <Switch
              checked={darkMode}
              onChange={onDarkModeToggle}
              size="small"
            />
          }
          label={!sidebarCollapsed ? "Dark Mode" : ""}
          sx={{
            '& .MuiFormControlLabel-label': {
              fontSize: '12px',
              color: '#555555'
            }
          }}
        />
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* Top Navigation Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          backgroundColor: '#FFFFFF',
          color: '#333333',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          borderBottom: '1px solid #E0E0E0',
          zIndex: theme.zIndex.drawer + 1
        }}
      >
        <Toolbar sx={{ minHeight: '64px !important' }}>
          {/* Mobile Menu Button */}
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          {/* Company Logo */}
          <Box sx={{ display: 'flex', alignItems: 'center', mr: 4 }}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                color: '#4A90E2',
                fontSize: '20px'
              }}
            >
              ERP System
            </Typography>
          </Box>

          {/* Global Search Bar */}
          <Box sx={{ flexGrow: 1, maxWidth: 600, mx: 'auto' }}>
            <TextField
              fullWidth
              placeholder="Search across all modules..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              size="small"
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: '#F9F9F9',
                  borderRadius: '8px',
                  '& fieldset': {
                    borderColor: '#E0E0E0',
                    borderWidth: '1px'
                  },
                  '&:hover fieldset': {
                    borderColor: '#4A90E2'
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#4A90E2',
                    boxShadow: '0 0 0 3px rgba(74, 144, 226, 0.1)'
                  }
                }
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search sx={{ color: '#555555', fontSize: 20 }} />
                  </InputAdornment>
                )
              }}
            />
          </Box>

          {/* Right Side Actions */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Real-time Status */}
            <Tooltip title={`Real-time sync: ${realtimeStatus}`}>
              <IconButton size="small">
                {getRealtimeIcon()}
              </IconButton>
            </Tooltip>

            {/* Notifications */}
            <IconButton color="inherit">
              <Badge badgeContent={notifications} color="error">
                <Notifications />
              </Badge>
            </IconButton>

            {/* User Profile Menu */}
            <IconButton
              color="inherit"
              onClick={handleMenuClick}
              sx={{
                '&:hover': {
                  backgroundColor: 'rgba(74, 144, 226, 0.1)'
                }
              }}
            >
              <Avatar sx={{ width: 32, height: 32, bgcolor: '#4A90E2' }}>
                <AccountCircle />
              </Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Side Navigation Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        {/* Mobile Drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              backgroundColor: '#FFFFFF',
              borderRight: '1px solid #E0E0E0'
            }
          }}
        >
          {drawer}
        </Drawer>

        {/* Desktop Drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              backgroundColor: '#FFFFFF',
              borderRight: '1px solid #E0E0E0',
              transition: 'width 250ms ease-in-out'
            }
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          backgroundColor: '#F9F9F9',
          minHeight: '100vh',
          transition: 'margin 250ms ease-in-out'
        }}
      >
        <Toolbar sx={{ minHeight: '64px !important' }} />
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      </Box>

      {/* User Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        PaperProps={{
          sx: {
            mt: 1,
            minWidth: 200,
            borderRadius: '8px',
            boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
            border: '1px solid #E0E0E0'
          }
        }}
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
          <ListItemIcon>
            <Logout />
          </ListItemIcon>
          <ListItemText>Logout</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default ModernERPLayout;
