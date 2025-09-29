// Full Page View Component
// Generic full-page view for all modules with complete functionality

import React, { useState, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Button,
  Breadcrumbs,
  Link,
  Chip,
  Badge,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Fab,
  Tooltip,
  LinearProgress,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Close,
  Edit,
  Delete,
  Share,
  Print,
  Download,
  Upload,
  Refresh,
  Sync,
  CloudSync,
  CloudDone,
  CloudOff,
  Settings,
  MoreVert,
  Home,
  ArrowBack,
  Save,
  Cancel,
  Add,
  Search,
  FilterList,
  ViewList,
  ViewModule,
  ViewComfy,
  Analytics,
  Timeline,
  Assessment,
  GetApp,
  Publish,
  Archive,
  RestoreFromTrash
} from '@mui/icons-material';

interface FullPageViewProps {
  title: string;
  subtitle?: string;
  module: string;
  entity: string;
  entityId?: number;
  onClose: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  onRefresh?: () => void;
  onExport?: () => void;
  onImport?: () => void;
  onPrint?: () => void;
  onShare?: () => void;
  onArchive?: () => void;
  onRestore?: () => void;
  children: React.ReactNode;
  loading?: boolean;
  error?: string;
  success?: string;
  realtimeStatus?: 'connected' | 'disconnected' | 'syncing';
  breadcrumbs?: Array<{ label: string; href?: string }>;
  actions?: Array<{
    label: string;
    icon: React.ReactNode;
    onClick: () => void;
    color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
    variant?: 'text' | 'outlined' | 'contained';
  }>;
  status?: string;
  priority?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

const FullPageView: React.FC<FullPageViewProps> = ({
  title,
  subtitle,
  module,
  entity,
  entityId,
  onClose,
  onEdit,
  onDelete,
  onSave,
  onCancel,
  onRefresh,
  onExport,
  onImport,
  onPrint,
  onShare,
  onArchive,
  onRestore,
  children,
  loading = false,
  error,
  success,
  realtimeStatus = 'connected',
  breadcrumbs = [],
  actions = [],
  status,
  priority,
  tags = [],
  metadata = {}
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'table'>('table');
  const [isEditing, setIsEditing] = useState(false);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleEdit = () => {
    setIsEditing(true);
    onEdit?.();
  };

  const handleSave = () => {
    setIsEditing(false);
    onSave?.();
  };

  const handleCancel = () => {
    setIsEditing(false);
    onCancel?.();
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active':
      case 'completed':
      case 'success':
        return 'success';
      case 'inactive':
      case 'cancelled':
      case 'error':
        return 'error';
      case 'pending':
      case 'warning':
        return 'warning';
      case 'draft':
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'urgent':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'default';
      default:
        return 'default';
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

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={onClose}
            sx={{ mr: 2 }}
          >
            <Close />
          </IconButton>
          
          <Box sx={{ flexGrow: 1 }}>
            <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 1 }}>
              <Link
                underline="hover"
                color="inherit"
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  // Navigate to home
                }}
              >
                <Home sx={{ mr: 0.5 }} fontSize="inherit" />
                Home
              </Link>
              <Link
                underline="hover"
                color="inherit"
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  // Navigate to module
                }}
              >
                {module}
              </Link>
              <Typography color="text.primary">
                {entity}
              </Typography>
            </Breadcrumbs>
            
            <Typography variant="h6" component="div">
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="textSecondary">
                {subtitle}
              </Typography>
            )}
          </Box>

          {/* Status and Priority */}
          <Box display="flex" gap={1} sx={{ mr: 2 }}>
            {status && (
              <Chip
                label={status}
                color={getStatusColor(status)}
                size="small"
              />
            )}
            {priority && (
              <Chip
                label={priority}
                color={getPriorityColor(priority)}
                size="small"
                variant="outlined"
              />
            )}
            {tags.map((tag, index) => (
              <Chip
                key={index}
                label={tag}
                size="small"
                variant="outlined"
              />
            ))}
          </Box>

          {/* Real-time Status */}
          <Tooltip title={`Real-time sync: ${realtimeStatus}`}>
            <IconButton color="inherit">
              {getRealtimeIcon()}
            </IconButton>
          </Tooltip>

          {/* Actions */}
          <Box display="flex" gap={1}>
            {onRefresh && (
              <Tooltip title="Refresh">
                <IconButton color="inherit" onClick={onRefresh}>
                  <Refresh />
                </IconButton>
              </Tooltip>
            )}
            
            {onExport && (
              <Tooltip title="Export">
                <IconButton color="inherit" onClick={onExport}>
                  <Download />
                </IconButton>
              </Tooltip>
            )}
            
            {onImport && (
              <Tooltip title="Import">
                <IconButton color="inherit" onClick={onImport}>
                  <Upload />
                </IconButton>
              </Tooltip>
            )}
            
            {onPrint && (
              <Tooltip title="Print">
                <IconButton color="inherit" onClick={onPrint}>
                  <Print />
                </IconButton>
              </Tooltip>
            )}
            
            {onShare && (
              <Tooltip title="Share">
                <IconButton color="inherit" onClick={onShare}>
                  <Share />
                </IconButton>
              </Tooltip>
            )}

            {/* Edit/Save/Cancel */}
            {!isEditing ? (
              onEdit && (
                <Button
                  variant="outlined"
                  startIcon={<Edit />}
                  onClick={handleEdit}
                >
                  Edit
                </Button>
              )
            ) : (
              <Box display="flex" gap={1}>
                <Button
                  variant="contained"
                  startIcon={<Save />}
                  onClick={handleSave}
                >
                  Save
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Cancel />}
                  onClick={handleCancel}
                >
                  Cancel
                </Button>
              </Box>
            )}

            {/* More Actions Menu */}
            <IconButton color="inherit" onClick={handleMenuClick}>
              <MoreVert />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Loading Indicator */}
      {loading && <LinearProgress />}

      {/* Content */}
      <Box sx={{ flexGrow: 1, overflow: 'auto', p: 3 }}>
        {children}
      </Box>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
        }}
        onClick={() => {
          // Quick action
        }}
      >
        <Add />
      </Fab>

      {/* More Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        {onEdit && (
          <MenuItem onClick={() => { handleEdit(); handleMenuClose(); }}>
            <ListItemIcon>
              <Edit />
            </ListItemIcon>
            <ListItemText>Edit</ListItemText>
          </MenuItem>
        )}
        
        {onDelete && (
          <MenuItem onClick={() => { onDelete(); handleMenuClose(); }}>
            <ListItemIcon>
              <Delete />
            </ListItemIcon>
            <ListItemText>Delete</ListItemText>
          </MenuItem>
        )}
        
        <Divider />
        
        {onArchive && (
          <MenuItem onClick={() => { onArchive(); handleMenuClose(); }}>
            <ListItemIcon>
              <Archive />
            </ListItemIcon>
            <ListItemText>Archive</ListItemText>
          </MenuItem>
        )}
        
        {onRestore && (
          <MenuItem onClick={() => { onRestore(); handleMenuClose(); }}>
            <ListItemIcon>
              <RestoreFromTrash />
            </ListItemIcon>
            <ListItemText>Restore</ListItemText>
          </MenuItem>
        )}
        
        <Divider />
        
        <MenuItem onClick={() => { /* Settings */ handleMenuClose(); }}>
          <ListItemIcon>
            <Settings />
          </ListItemIcon>
          <ListItemText>Settings</ListItemText>
        </MenuItem>
      </Menu>

      {/* Snackbars */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => {/* Clear error */}}
      >
        <Alert severity="error">
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => {/* Clear success */}}
      >
        <Alert severity="success">
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default FullPageView;
