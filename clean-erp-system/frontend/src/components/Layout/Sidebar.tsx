// Sidebar Navigation Component
// Updated to include System Settings

import React, { useState } from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  Box,
  Typography,
  Divider,
  IconButton,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Business as BusinessIcon,
  AccountBalance as FinanceIcon,
  Inventory as InventoryIcon,
  Build as MaintenanceIcon,
  Event as BookingIcon,
  Chat as MomentsIcon,
  Psychology as AiIcon,
  AccountTree as WorkflowIcon,
  Settings as SettingsIcon,
  ExpandLess,
  ExpandMore,
  Menu as MenuIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const handleItemClick = (path: string) => {
    navigate(path);
    if (isMobile) {
      onClose();
    }
  };

  const handleExpandClick = (item: string) => {
    setExpandedItems(prev => 
      prev.includes(item) 
        ? prev.filter(i => i !== item)
        : [...prev, item]
    );
  };

  const menuItems = [
    {
      label: 'Dashboard',
      icon: <DashboardIcon />,
      path: '/',
      type: 'single'
    },
    {
      label: 'CRM',
      icon: <BusinessIcon />,
      type: 'group',
      items: [
        { label: 'Customers', path: '/crm/customers' },
        { label: 'Contacts', path: '/crm/contacts' },
        { label: 'Leads', path: '/crm/leads' },
        { label: 'Opportunities', path: '/crm/opportunities' }
      ]
    },
    {
      label: 'Finance',
      icon: <FinanceIcon />,
      type: 'group',
      items: [
        { label: 'Invoices', path: '/finance/invoices' },
        { label: 'Accounts', path: '/finance/accounts' }
      ]
    },
    {
      label: 'People',
      icon: <PeopleIcon />,
      type: 'group',
      items: [
        { label: 'Employees', path: '/people/employees' },
        { label: 'Attendance', path: '/people/attendance' },
        { label: 'Leave Requests', path: '/people/leave-requests' }
      ]
    },
    {
      label: 'Supply Chain',
      icon: <InventoryIcon />,
      type: 'group',
      items: [
        { label: 'Inventory', path: '/supply-chain/inventory' },
        { label: 'Purchase Orders', path: '/supply-chain/purchase-orders' },
        { label: 'Suppliers', path: '/supply-chain/suppliers' }
      ]
    },
    {
      label: 'Maintenance',
      icon: <MaintenanceIcon />,
      type: 'group',
      items: [
        { label: 'Assets', path: '/maintenance/assets' },
        { label: 'Work Orders', path: '/maintenance/work-orders' }
      ]
    },
    {
      label: 'Booking',
      icon: <BookingIcon />,
      type: 'group',
      items: [
        { label: 'Meetings', path: '/booking/meetings' },
        { label: 'Resources', path: '/booking/resources' }
      ]
    },
    {
      label: 'Moments',
      icon: <MomentsIcon />,
      type: 'group',
      items: [
        { label: 'Social Feed', path: '/moments/feed' }
      ]
    },
    {
      label: 'AI Analytics',
      icon: <AiIcon />,
      path: '/ai',
      type: 'single'
    },
    {
      label: 'Workflow',
      icon: <WorkflowIcon />,
      path: '/workflow',
      type: 'single'
    },
    {
      label: 'System Settings',
      icon: <SettingsIcon />,
      path: '/system-settings',
      type: 'single'
    }
  ];

  const renderMenuItem = (item: any, level: number = 0) => {
    const isExpanded = expandedItems.includes(item.label);
    const isActive = location.pathname === item.path;
    
    if (item.type === 'single') {
      return (
        <ListItem key={item.label} disablePadding>
          <ListItemButton
            onClick={() => handleItemClick(item.path)}
            sx={{
              pl: 2 + level * 2,
              backgroundColor: isActive ? theme.palette.primary.main : 'transparent',
              color: isActive ? theme.palette.primary.contrastText : 'inherit',
              '&:hover': {
                backgroundColor: isActive 
                  ? theme.palette.primary.dark 
                  : theme.palette.action.hover
              }
            }}
          >
            <ListItemIcon sx={{ color: isActive ? theme.palette.primary.contrastText : 'inherit' }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        </ListItem>
      );
    }

    if (item.type === 'group') {
      return (
        <React.Fragment key={item.label}>
          <ListItem disablePadding>
            <ListItemButton
              onClick={() => handleExpandClick(item.label)}
              sx={{ pl: 2 + level * 2 }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
              {isExpanded ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>
          </ListItem>
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.items.map((subItem: any) => (
                <ListItem key={subItem.label} disablePadding>
                  <ListItemButton
                    onClick={() => handleItemClick(subItem.path)}
                    sx={{
                      pl: 4 + level * 2,
                      backgroundColor: location.pathname === subItem.path ? theme.palette.primary.main : 'transparent',
                      color: location.pathname === subItem.path ? theme.palette.primary.contrastText : 'inherit',
                      '&:hover': {
                        backgroundColor: location.pathname === subItem.path 
                          ? theme.palette.primary.dark 
                          : theme.palette.action.hover
                      }
                    }}
                  >
                    <ListItemText primary={subItem.label} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Collapse>
        </React.Fragment>
      );
    }

    return null;
  };

  return (
    <Drawer
      variant={isMobile ? 'temporary' : 'persistent'}
      open={open}
      onClose={onClose}
      sx={{
        width: 280,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: 280,
          boxSizing: 'border-box',
          backgroundColor: theme.palette.background.paper,
          borderRight: `1px solid ${theme.palette.divider}`
        }
      }}
    >
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
          Clean ERP
        </Typography>
        {isMobile && (
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        )}
      </Box>
      
      <Divider />
      
      <List sx={{ flexGrow: 1, pt: 1 }}>
        {menuItems.map((item) => renderMenuItem(item))}
      </List>
      
      <Divider />
      
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="textSecondary">
          Clean ERP System v1.0.0
        </Typography>
      </Box>
    </Drawer>
  );
};

export default Sidebar;
