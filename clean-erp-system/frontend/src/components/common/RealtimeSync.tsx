// Real-time Synchronization Component
// Handles real-time data synchronization across all modules

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Chip,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Alert,
  Snackbar,
  LinearProgress,
  Typography,
  Card,
  CardContent,
  Grid,
  Badge
} from '@mui/material';
import {
  CloudSync,
  CloudDone,
  CloudOff,
  Sync,
  Refresh,
  Settings,
  Notifications,
  CheckCircle,
  Error,
  Warning,
  Info,
  Timeline,
  Assessment,
  Speed,
  Storage,
  NetworkCheck,
  Wifi,
  WifiOff
} from '@mui/icons-material';

interface SyncStatus {
  status: 'connected' | 'disconnected' | 'syncing' | 'error';
  lastSync: Date | null;
  syncCount: number;
  errorCount: number;
  latency: number;
  throughput: number;
  modules: Array<{
    name: string;
    status: 'synced' | 'pending' | 'error';
    lastSync: Date | null;
    recordCount: number;
  }>;
}

interface RealtimeSyncProps {
  onSyncStatusChange?: (status: SyncStatus) => void;
  onDataUpdate?: (module: string, data: any) => void;
  onError?: (error: string) => void;
}

const RealtimeSync: React.FC<RealtimeSyncProps> = ({
  onSyncStatusChange,
  onDataUpdate,
  onError
}) => {
  const [syncStatus, setSyncStatus] = useState<SyncStatus>({
    status: 'disconnected',
    lastSync: null,
    syncCount: 0,
    errorCount: 0,
    latency: 0,
    throughput: 0,
    modules: []
  });
  
  const [notifications, setNotifications] = useState<Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    timestamp: Date;
    module?: string;
  }>>([]);
  
  const [showDetails, setShowDetails] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  useEffect(() => {
    initializeRealtimeSync();
    return () => {
      cleanupRealtimeSync();
    };
  }, []);

  const initializeRealtimeSync = () => {
    // Initialize WebSocket connection for real-time sync
    const ws = new WebSocket('ws://localhost:5000/realtime');
    
    ws.onopen = () => {
      setSyncStatus(prev => ({ ...prev, status: 'connected' }));
      addNotification('success', 'Real-time sync connected');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleRealtimeUpdate(data);
      } catch (error) {
        console.error('Error parsing real-time update:', error);
      }
    };
    
    ws.onclose = () => {
      setSyncStatus(prev => ({ ...prev, status: 'disconnected' }));
      addNotification('warning', 'Real-time sync disconnected');
    };
    
    ws.onerror = (error) => {
      setSyncStatus(prev => ({ ...prev, status: 'error', errorCount: prev.errorCount + 1 }));
      addNotification('error', 'Real-time sync error');
    };
    
    // Store WebSocket reference for cleanup
    (window as any).realtimeWS = ws;
  };

  const cleanupRealtimeSync = () => {
    if ((window as any).realtimeWS) {
      (window as any).realtimeWS.close();
    }
  };

  const handleRealtimeUpdate = (data: any) => {
    const { type, module, payload, timestamp } = data;
    
    switch (type) {
      case 'data_update':
        handleDataUpdate(module, payload);
        break;
      case 'sync_status':
        handleSyncStatusUpdate(payload);
        break;
      case 'error':
        handleSyncError(payload);
        break;
      case 'notification':
        handleSyncNotification(payload);
        break;
    }
    
    // Update sync status
    setSyncStatus(prev => ({
      ...prev,
      lastSync: new Date(timestamp),
      syncCount: prev.syncCount + 1
    }));
  };

  const handleDataUpdate = (module: string, data: any) => {
    // Update module data
    setSyncStatus(prev => ({
      ...prev,
      modules: prev.modules.map(m => 
        m.name === module 
          ? { ...m, status: 'synced', lastSync: new Date(), recordCount: data.recordCount || m.recordCount }
          : m
      )
    }));
    
    // Notify parent component
    onDataUpdate?.(module, data);
    
    // Add notification
    addNotification('info', `Data updated in ${module}`, module);
  };

  const handleSyncStatusUpdate = (status: any) => {
    setSyncStatus(prev => ({
      ...prev,
      ...status,
      lastSync: new Date()
    }));
    
    onSyncStatusChange?.(syncStatus);
  };

  const handleSyncError = (error: any) => {
    setSyncStatus(prev => ({
      ...prev,
      status: 'error',
      errorCount: prev.errorCount + 1
    }));
    
    addNotification('error', error.message || 'Sync error occurred');
    onError?.(error.message || 'Sync error occurred');
  };

  const handleSyncNotification = (notification: any) => {
    addNotification(
      notification.type || 'info',
      notification.message,
      notification.module
    );
  };

  const addNotification = (type: 'success' | 'error' | 'warning' | 'info', message: string, module?: string) => {
    const notification = {
      id: Date.now().toString(),
      type,
      message,
      timestamp: new Date(),
      module
    };
    
    setNotifications(prev => [notification, ...prev.slice(0, 9)]); // Keep last 10 notifications
  };

  const handleManualSync = () => {
    setSyncStatus(prev => ({ ...prev, status: 'syncing' }));
    
    // Trigger manual sync
    fetch('/api/realtime/sync', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        setSyncStatus(prev => ({ ...prev, status: 'connected' }));
        addNotification('success', 'Manual sync completed');
      } else {
        throw new Error(data.error || 'Sync failed');
      }
    })
    .catch(error => {
      setSyncStatus(prev => ({ ...prev, status: 'error' }));
      addNotification('error', error.message);
    });
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const getStatusIcon = () => {
    switch (syncStatus.status) {
      case 'connected':
        return <CloudDone color="success" />;
      case 'syncing':
        return <CloudSync color="warning" />;
      case 'disconnected':
        return <CloudOff color="error" />;
      case 'error':
        return <Error color="error" />;
      default:
        return <CloudOff color="error" />;
    }
  };

  const getStatusColor = () => {
    switch (syncStatus.status) {
      case 'connected':
        return 'success';
      case 'syncing':
        return 'warning';
      case 'disconnected':
        return 'error';
      case 'error':
        return 'error';
      default:
        return 'error';
    }
  };

  const getStatusText = () => {
    switch (syncStatus.status) {
      case 'connected':
        return 'Connected';
      case 'syncing':
        return 'Syncing...';
      case 'disconnected':
        return 'Disconnected';
      case 'error':
        return 'Error';
      default:
        return 'Unknown';
    }
  };

  const renderSyncDetails = () => (
    <Card sx={{ mt: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Sync Details
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <Timeline color="primary" />
              <Typography variant="body2">
                Last Sync: {syncStatus.lastSync ? syncStatus.lastSync.toLocaleString() : 'Never'}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <Speed color="primary" />
              <Typography variant="body2">
                Latency: {syncStatus.latency}ms
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <Assessment color="primary" />
              <Typography variant="body2">
                Sync Count: {syncStatus.syncCount}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <Error color="error" />
              <Typography variant="body2">
                Error Count: {syncStatus.errorCount}
              </Typography>
            </Box>
          </Grid>
        </Grid>
        
        <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
          Module Status
        </Typography>
        {syncStatus.modules.map((module, index) => (
          <Box key={index} display="flex" justifyContent="space-between" alignItems="center" py={1}>
            <Typography variant="body2">{module.name}</Typography>
            <Box display="flex" alignItems="center" gap={1}>
              <Chip
                label={module.status}
                color={module.status === 'synced' ? 'success' : 
                       module.status === 'pending' ? 'warning' : 'error'}
                size="small"
              />
              <Typography variant="caption">
                {module.recordCount} records
              </Typography>
            </Box>
          </Box>
        ))}
      </CardContent>
    </Card>
  );

  const renderNotifications = () => (
    <Box sx={{ mt: 2 }}>
      <Typography variant="subtitle2" gutterBottom>
        Recent Notifications
      </Typography>
      {notifications.map((notification) => (
        <Box key={notification.id} display="flex" alignItems="center" gap={1} py={0.5}>
          {notification.type === 'success' && <CheckCircle color="success" fontSize="small" />}
          {notification.type === 'error' && <Error color="error" fontSize="small" />}
          {notification.type === 'warning' && <Warning color="warning" fontSize="small" />}
          {notification.type === 'info' && <Info color="info" fontSize="small" />}
          <Typography variant="body2" sx={{ flexGrow: 1 }}>
            {notification.message}
          </Typography>
          <Typography variant="caption" color="textSecondary">
            {notification.timestamp.toLocaleTimeString()}
          </Typography>
        </Box>
      ))}
    </Box>
  );

  return (
    <Box>
      {/* Sync Status Indicator */}
      <Box display="flex" alignItems="center" gap={1}>
        <Tooltip title={`Real-time sync: ${getStatusText()}`}>
          <IconButton onClick={() => setShowDetails(!showDetails)}>
            {getStatusIcon()}
          </IconButton>
        </Tooltip>
        
        <Chip
          label={getStatusText()}
          color={getStatusColor()}
          size="small"
        />
        
        {syncStatus.status === 'syncing' && (
          <LinearProgress sx={{ width: 100, height: 4 }} />
        )}
        
        <IconButton onClick={handleManualSync} disabled={syncStatus.status === 'syncing'}>
          <Sync />
        </IconButton>
        
        <IconButton onClick={handleMenuClick}>
          <MoreVert />
        </IconButton>
      </Box>

      {/* Sync Details */}
      {showDetails && (
        <Box>
          {renderSyncDetails()}
          {renderNotifications()}
        </Box>
      )}

      {/* More Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => { handleManualSync(); handleMenuClose(); }}>
          <ListItemIcon>
            <Sync />
          </ListItemIcon>
          <ListItemText>Manual Sync</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={() => { setShowDetails(!showDetails); handleMenuClose(); }}>
          <ListItemIcon>
            <Assessment />
          </ListItemIcon>
          <ListItemText>Sync Details</ListItemText>
        </MenuItem>
        
        <Divider />
        
        <MenuItem onClick={() => { /* Settings */ handleMenuClose(); }}>
          <ListItemIcon>
            <Settings />
          </ListItemIcon>
          <ListItemText>Sync Settings</ListItemText>
        </MenuItem>
      </Menu>

      {/* Notifications Snackbar */}
      {notifications.map((notification) => (
        <Snackbar
          key={notification.id}
          open={true}
          autoHideDuration={6000}
          onClose={() => {
            setNotifications(prev => prev.filter(n => n.id !== notification.id));
          }}
        >
          <Alert severity={notification.type}>
            {notification.message}
          </Alert>
        </Snackbar>
      ))}
    </Box>
  );
};

export default RealtimeSync;
