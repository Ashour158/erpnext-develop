// Module Admin Panel Component
// Module-specific administration interface

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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar,
  LinearProgress,
  Tooltip
} from '@mui/material';
import {
  Settings,
  People,
  Business,
  Security,
  Analytics,
  Notifications,
  Add,
  Edit,
  Delete,
  Visibility,
  Block,
  CheckCircle,
  Warning,
  Error,
  Speed,
  Integration,
  Report,
  Alert as AlertIcon
} from '@mui/icons-material';

interface ModuleAdminPanelProps {
  moduleId: string;
  moduleName: string;
  onBack?: () => void;
}

const ModuleAdminPanel: React.FC<ModuleAdminPanelProps> = ({ 
  moduleId, 
  moduleName, 
  onBack 
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [moduleStats, setModuleStats] = useState({
    totalUsers: 0,
    activeUsers: 0,
    totalFeatures: 0,
    enabledFeatures: 0,
    totalIntegrations: 0,
    activeIntegrations: 0,
    totalAlerts: 0,
    activeAlerts: 0
  });
  const [moduleConfig, setModuleConfig] = useState([]);
  const [moduleFeatures, setModuleFeatures] = useState([]);
  const [userAccess, setUserAccess] = useState([]);
  const [departmentAccess, setDepartmentAccess] = useState([]);
  const [integrations, setIntegrations] = useState([]);
  const [analytics, setAnalytics] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState('');
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    fetchModuleData();
  }, [moduleId]);

  const fetchModuleData = async () => {
    setLoading(true);
    try {
      // Fetch module dashboard data
      const dashboardResponse = await fetch(`/api/module-admin/analytics/dashboard?module_id=${moduleId}`);
      const dashboardData = await dashboardResponse.json();
      if (dashboardData.success) {
        setModuleStats(dashboardData.data);
      }

      // Fetch module configuration
      const configResponse = await fetch(`/api/module-admin/configurations?module_id=${moduleId}`);
      const configData = await configResponse.json();
      if (configData.success) {
        setModuleConfig(configData.data);
      }

      // Fetch module features
      const featuresResponse = await fetch(`/api/module-admin/features?module_id=${moduleId}`);
      const featuresData = await featuresResponse.json();
      if (featuresData.success) {
        setModuleFeatures(featuresData.data);
      }

      // Fetch user access
      const userAccessResponse = await fetch(`/api/module-admin/user-access?module_id=${moduleId}`);
      const userAccessData = await userAccessResponse.json();
      if (userAccessData.success) {
        setUserAccess(userAccessData.data);
      }

      // Fetch department access
      const deptAccessResponse = await fetch(`/api/module-admin/department-access?module_id=${moduleId}`);
      const deptAccessData = await deptAccessResponse.json();
      if (deptAccessData.success) {
        setDepartmentAccess(deptAccessData.data);
      }

      // Fetch integrations
      const integrationsResponse = await fetch(`/api/module-admin/integrations?module_id=${moduleId}`);
      const integrationsData = await integrationsResponse.json();
      if (integrationsData.success) {
        setIntegrations(integrationsData.data);
      }

      // Fetch analytics
      const analyticsResponse = await fetch(`/api/module-admin/analytics?module_id=${moduleId}`);
      const analyticsData = await analyticsResponse.json();
      if (analyticsData.success) {
        setAnalytics(analyticsData.data);
      }

      // Fetch alerts
      const alertsResponse = await fetch(`/api/module-admin/alerts?module_id=${moduleId}`);
      const alertsData = await alertsResponse.json();
      if (alertsData.success) {
        setAlerts(alertsData.data);
      }

      // Fetch reports
      const reportsResponse = await fetch(`/api/module-admin/reports?module_id=${moduleId}`);
      const reportsData = await reportsResponse.json();
      if (reportsData.success) {
        setReports(reportsData.data);
      }
    } catch (err) {
      setError('Failed to fetch module data');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleCreateItem = (type: string) => {
    setDialogType(type);
    setSelectedItem(null);
    setDialogOpen(true);
  };

  const handleEditItem = (item: any, type: string) => {
    setDialogType(type);
    setSelectedItem(item);
    setDialogOpen(true);
  };

  const handleDeleteItem = async (id: number, type: string) => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      try {
        const response = await fetch(`/api/module-admin/${type}/${id}`, {
          method: 'DELETE'
        });
        const data = await response.json();
        if (data.success) {
          setSuccess('Item deleted successfully');
          fetchModuleData();
        } else {
          setError(data.error || 'Failed to delete item');
        }
      } catch (err) {
        setError('Failed to delete item');
      }
    }
  };

  const handleFeatureStatusChange = async (featureId: number, status: string) => {
    try {
      const response = await fetch(`/api/module-admin/features/${featureId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ feature_status: status })
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Feature status updated successfully');
        fetchModuleData();
      } else {
        setError(data.error || 'Failed to update feature status');
      }
    } catch (err) {
      setError('Failed to update feature status');
    }
  };

  const handleIntegrationTest = async (integrationId: number) => {
    try {
      const response = await fetch(`/api/module-admin/integrations/${integrationId}/test`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Integration test completed successfully');
      } else {
        setError(data.error || 'Integration test failed');
      }
    } catch (err) {
      setError('Integration test failed');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'enabled':
      case 'success':
        return 'success';
      case 'inactive':
      case 'disabled':
      case 'error':
        return 'error';
      case 'maintenance':
      case 'warning':
        return 'warning';
      case 'pending':
        return 'default';
      default:
        return 'default';
    }
  };

  const renderOverview = () => (
    <Grid container spacing={3}>
      {/* Module Overview Cards */}
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Users
                </Typography>
                <Typography variant="h4">
                  {moduleStats.totalUsers}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {moduleStats.activeUsers} active
                </Typography>
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
                  Features
                </Typography>
                <Typography variant="h4">
                  {moduleStats.totalFeatures}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {moduleStats.enabledFeatures} enabled
                </Typography>
              </Box>
              <Settings color="primary" />
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
                  Integrations
                </Typography>
                <Typography variant="h4">
                  {moduleStats.totalIntegrations}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {moduleStats.activeIntegrations} active
                </Typography>
              </Box>
              <Integration color="primary" />
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
                  Alerts
                </Typography>
                <Typography variant="h4">
                  {moduleStats.totalAlerts}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {moduleStats.activeAlerts} active
                </Typography>
              </Box>
              <AlertIcon color="primary" />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Module Performance */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Module Performance
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box>
                  <Typography variant="body2" color="textSecondary">
                    Response Time
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={75} 
                    sx={{ mt: 1, mb: 1 }}
                  />
                  <Typography variant="caption">75ms</Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box>
                  <Typography variant="body2" color="textSecondary">
                    Success Rate
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={95} 
                    color="success"
                    sx={{ mt: 1, mb: 1 }}
                  />
                  <Typography variant="caption">95%</Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderConfiguration = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Module Configuration</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleCreateItem('configuration')}
          >
            Add Configuration
          </Button>
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Configuration Key</TableCell>
                <TableCell>Value</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {moduleConfig.map((config: any) => (
                <TableRow key={config.id}>
                  <TableCell>
                    <Typography variant="subtitle2">{config.config_key}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {config.config_description}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap>
                      {config.config_value}
                    </Typography>
                  </TableCell>
                  <TableCell>{config.config_type}</TableCell>
                  <TableCell>{config.config_category}</TableCell>
                  <TableCell>
                    <Chip
                      label={config.is_active ? 'Active' : 'Inactive'}
                      color={config.is_active ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleEditItem(config, 'configuration')}
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteItem(config.id, 'configurations')}
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );

  const renderFeatures = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Module Features</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleCreateItem('feature')}
          >
            Add Feature
          </Button>
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Feature Name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Usage</TableCell>
                <TableCell>Performance</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {moduleFeatures.map((feature: any) => (
                <TableRow key={feature.id}>
                  <TableCell>
                    <Typography variant="subtitle2">{feature.feature_display_name}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {feature.feature_description}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={feature.feature_status}
                      color={getStatusColor(feature.feature_status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{feature.feature_version}</TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {feature.feature_usage_count} times
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center">
                      <LinearProgress 
                        variant="determinate" 
                        value={feature.feature_performance_score} 
                        sx={{ width: 60, mr: 1 }}
                      />
                      <Typography variant="caption">
                        {feature.feature_performance_score}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleEditItem(feature, 'feature')}
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleFeatureStatusChange(feature.id, 
                        feature.feature_status === 'enabled' ? 'disabled' : 'enabled'
                      )}
                    >
                      {feature.feature_status === 'enabled' ? <Block /> : <CheckCircle />}
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );

  const renderIntegrations = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Module Integrations</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleCreateItem('integration')}
          >
            Add Integration
          </Button>
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Integration Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Health</TableCell>
                <TableCell>Last Sync</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {integrations.map((integration: any) => (
                <TableRow key={integration.id}>
                  <TableCell>
                    <Typography variant="subtitle2">{integration.integration_name}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {integration.integration_provider}
                    </Typography>
                  </TableCell>
                  <TableCell>{integration.integration_type}</TableCell>
                  <TableCell>
                    <Chip
                      label={integration.integration_status}
                      color={getStatusColor(integration.integration_status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={integration.integration_health}
                      color={getStatusColor(integration.integration_health)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {integration.integration_last_sync 
                      ? new Date(integration.integration_last_sync).toLocaleString()
                      : 'Never'
                    }
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Test Integration">
                      <IconButton
                        size="small"
                        onClick={() => handleIntegrationTest(integration.id)}
                      >
                        <Speed />
                      </IconButton>
                    </Tooltip>
                    <IconButton
                      size="small"
                      onClick={() => handleEditItem(integration, 'integration')}
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteItem(integration.id, 'integrations')}
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );

  const renderAlerts = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Module Alerts</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleCreateItem('alert')}
          >
            Add Alert
          </Button>
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Alert Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Last Triggered</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {alerts.map((alert: any) => (
                <TableRow key={alert.id}>
                  <TableCell>
                    <Typography variant="subtitle2">{alert.alert_name}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {alert.alert_message}
                    </Typography>
                  </TableCell>
                  <TableCell>{alert.alert_type}</TableCell>
                  <TableCell>
                    <Chip
                      label={alert.alert_severity}
                      color={getStatusColor(alert.alert_severity)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={alert.alert_status}
                      color={getStatusColor(alert.alert_status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {alert.last_triggered 
                      ? new Date(alert.last_triggered).toLocaleString()
                      : 'Never'
                    }
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleEditItem(alert, 'alert')}
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteItem(alert.id, 'alerts')}
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );

  const renderDialog = () => (
    <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        {selectedItem ? 'Edit' : 'Create'} {dialogType}
      </DialogTitle>
      <DialogContent>
        {/* Dialog content based on type */}
        <Typography>Dialog content will be implemented based on the specific type</Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
        <Button variant="contained" onClick={() => setDialogOpen(false)}>
          {selectedItem ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={3}>
        {onBack && (
          <Button onClick={onBack} sx={{ mr: 2 }}>
            ← Back
          </Button>
        )}
        <Typography variant="h4">
          {moduleName} Administration
        </Typography>
      </Box>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Overview" />
        <Tab label="Configuration" />
        <Tab label="Features" />
        <Tab label="User Access" />
        <Tab label="Department Access" />
        <Tab label="Integrations" />
        <Tab label="Analytics" />
        <Tab label="Alerts" />
        <Tab label="Reports" />
      </Tabs>

      {activeTab === 0 && renderOverview()}
      {activeTab === 1 && renderConfiguration()}
      {activeTab === 2 && renderFeatures()}
      {activeTab === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6">User Access</Typography>
            <Typography>User access management will be implemented here</Typography>
          </CardContent>
        </Card>
      )}
      {activeTab === 4 && (
        <Card>
          <CardContent>
            <Typography variant="h6">Department Access</Typography>
            <Typography>Department access management will be implemented here</Typography>
          </CardContent>
        </Card>
      )}
      {activeTab === 5 && renderIntegrations()}
      {activeTab === 6 && (
        <Card>
          <CardContent>
            <Typography variant="h6">Analytics</Typography>
            <Typography>Module analytics will be implemented here</Typography>
          </CardContent>
        </Card>
      )}
      {activeTab === 7 && renderAlerts()}
      {activeTab === 8 && (
        <Card>
          <CardContent>
            <Typography variant="h6">Reports</Typography>
            <Typography>Module reports will be implemented here</Typography>
          </CardContent>
        </Card>
      )}

      {renderDialog()}

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError('')}
      >
        <Alert severity="error" onClose={() => setError('')}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => setSuccess('')}
      >
        <Alert severity="success" onClose={() => setSuccess('')}>
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ModuleAdminPanel;
