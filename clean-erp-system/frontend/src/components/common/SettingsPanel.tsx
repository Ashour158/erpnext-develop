// Settings Panel Component
// Integrated settings within each module based on user privileges

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
  Switch,
  FormControlLabel,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Snackbar,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Settings,
  Person,
  Security,
  Palette,
  Notifications,
  Language,
  Storage,
  Integration,
  AdminPanelSettings,
  SupervisedUserCircle,
  ExpandMore,
  Add,
  Edit,
  Delete,
  Save,
  Cancel
} from '@mui/icons-material';

interface SettingsPanelProps {
  moduleName: string;
  userRole: 'user' | 'admin' | 'super_admin';
  onSettingsChange?: (settings: any) => void;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({ 
  moduleName, 
  userRole, 
  onSettingsChange 
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [settings, setSettings] = useState({
    // User Settings (Basic)
    theme: 'light',
    language: 'en',
    notifications: true,
    emailNotifications: true,
    pushNotifications: true,
    autoSave: true,
    showTutorials: true,
    defaultView: 'grid',
    itemsPerPage: 25,
    
    // Admin Settings (Module-specific)
    moduleFeatures: {},
    integrations: {},
    workflows: {},
    permissions: {},
    dataRetention: {},
    performance: {},
    
    // Super Admin Settings (System-wide)
    systemModules: {},
    systemSecurity: {},
    systemIntegrations: {},
    systemPerformance: {},
    systemBackup: {},
    systemMonitoring: {}
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState('');

  useEffect(() => {
    fetchSettings();
  }, [moduleName, userRole]);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/settings/${moduleName}?role=${userRole}`);
      const data = await response.json();
      if (data.success) {
        setSettings(data.settings);
      }
    } catch (err) {
      setError('Failed to fetch settings');
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async (updatedSettings: any) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/settings/${moduleName}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ settings: updatedSettings, role: userRole })
      });
      const data = await response.json();
      if (data.success) {
        setSettings(updatedSettings);
        setSuccess('Settings saved successfully');
        onSettingsChange?.(updatedSettings);
      } else {
        setError(data.error || 'Failed to save settings');
      }
    } catch (err) {
      setError('Failed to save settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSettingChange = (key: string, value: any) => {
    const updatedSettings = { ...settings, [key]: value };
    setSettings(updatedSettings);
    saveSettings(updatedSettings);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const renderUserSettings = () => (
    <Grid container spacing={3}>
      {/* Personal Preferences */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Personal Preferences
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Theme</InputLabel>
                  <Select
                    value={settings.theme}
                    onChange={(e) => handleSettingChange('theme', e.target.value)}
                  >
                    <MenuItem value="light">Light</MenuItem>
                    <MenuItem value="dark">Dark</MenuItem>
                    <MenuItem value="auto">Auto</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Language</InputLabel>
                  <Select
                    value={settings.language}
                    onChange={(e) => handleSettingChange('language', e.target.value)}
                  >
                    <MenuItem value="en">English</MenuItem>
                    <MenuItem value="es">Spanish</MenuItem>
                    <MenuItem value="fr">French</MenuItem>
                    <MenuItem value="de">German</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Default View</InputLabel>
                  <Select
                    value={settings.defaultView}
                    onChange={(e) => handleSettingChange('defaultView', e.target.value)}
                  >
                    <MenuItem value="grid">Grid</MenuItem>
                    <MenuItem value="list">List</MenuItem>
                    <MenuItem value="table">Table</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Items Per Page</InputLabel>
                  <Select
                    value={settings.itemsPerPage}
                    onChange={(e) => handleSettingChange('itemsPerPage', e.target.value)}
                  >
                    <MenuItem value={10}>10</MenuItem>
                    <MenuItem value={25}>25</MenuItem>
                    <MenuItem value={50}>50</MenuItem>
                    <MenuItem value={100}>100</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Notifications */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Notifications
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications}
                      onChange={(e) => handleSettingChange('notifications', e.target.checked)}
                    />
                  }
                  label="Enable Notifications"
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.emailNotifications}
                      onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
                    />
                  }
                  label="Email Notifications"
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.pushNotifications}
                      onChange={(e) => handleSettingChange('pushNotifications', e.target.checked)}
                    />
                  }
                  label="Push Notifications"
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Application Settings */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Application Settings
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.autoSave}
                      onChange={(e) => handleSettingChange('autoSave', e.target.checked)}
                    />
                  }
                  label="Auto Save"
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.showTutorials}
                      onChange={(e) => handleSettingChange('showTutorials', e.target.checked)}
                    />
                  }
                  label="Show Tutorials"
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderAdminSettings = () => (
    <Grid container spacing={3}>
      {/* Module Features */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Module Features
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Enable or disable features for this module
            </Typography>
            <List>
              <ListItem>
                <ListItemText 
                  primary="Advanced Analytics" 
                  secondary="Enable advanced analytics and reporting"
                />
                <ListItemSecondaryAction>
                  <Switch
                    checked={settings.moduleFeatures?.advancedAnalytics || false}
                    onChange={(e) => handleSettingChange('moduleFeatures', {
                      ...settings.moduleFeatures,
                      advancedAnalytics: e.target.checked
                    })}
                  />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="AI Integration" 
                  secondary="Enable AI-powered features"
                />
                <ListItemSecondaryAction>
                  <Switch
                    checked={settings.moduleFeatures?.aiIntegration || false}
                    onChange={(e) => handleSettingChange('moduleFeatures', {
                      ...settings.moduleFeatures,
                      aiIntegration: e.target.checked
                    })}
                  />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Mobile Support" 
                  secondary="Enable mobile application features"
                />
                <ListItemSecondaryAction>
                  <Switch
                    checked={settings.moduleFeatures?.mobileSupport || false}
                    onChange={(e) => handleSettingChange('moduleFeatures', {
                      ...settings.moduleFeatures,
                      mobileSupport: e.target.checked
                    })}
                  />
                </ListItemSecondaryAction>
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Grid>

      {/* Integrations */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Integrations
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Manage third-party integrations
            </Typography>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="subtitle1">Available Integrations</Typography>
              <Button
                variant="outlined"
                startIcon={<Add />}
                onClick={() => setDialogOpen(true)}
              >
                Add Integration
              </Button>
            </Box>
            <List>
              <ListItem>
                <ListItemText 
                  primary="Google Workspace" 
                  secondary="Connect with Google Workspace"
                />
                <ListItemSecondaryAction>
                  <Chip label="Connected" color="success" size="small" />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Microsoft 365" 
                  secondary="Connect with Microsoft 365"
                />
                <ListItemSecondaryAction>
                  <Chip label="Available" color="default" size="small" />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Salesforce" 
                  secondary="Connect with Salesforce CRM"
                />
                <ListItemSecondaryAction>
                  <Chip label="Available" color="default" size="small" />
                </ListItemSecondaryAction>
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Grid>

      {/* Workflows */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Workflows
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Configure automated workflows
            </Typography>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>Email Notifications</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Send email when new record is created"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="Send email when record is updated"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="Send email when record is deleted"
                />
              </AccordionDetails>
            </Accordion>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>Data Validation</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Validate email addresses"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Validate phone numbers"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="Validate postal codes"
                />
              </AccordionDetails>
            </Accordion>
          </CardContent>
        </Card>
      </Grid>

      {/* Performance */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Performance Settings
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Cache Duration (minutes)"
                  type="number"
                  value={settings.performance?.cacheDuration || 60}
                  onChange={(e) => handleSettingChange('performance', {
                    ...settings.performance,
                    cacheDuration: parseInt(e.target.value)
                  })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="API Rate Limit (requests/minute)"
                  type="number"
                  value={settings.performance?.rateLimit || 1000}
                  onChange={(e) => handleSettingChange('performance', {
                    ...settings.performance,
                    rateLimit: parseInt(e.target.value)
                  })}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderSuperAdminSettings = () => (
    <Grid container spacing={3}>
      {/* System Modules */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              System Modules
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Enable or disable system modules
            </Typography>
            <List>
              <ListItem>
                <ListItemText 
                  primary="CRM Module" 
                  secondary="Customer Relationship Management"
                />
                <ListItemSecondaryAction>
                  <Switch defaultChecked />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Finance Module" 
                  secondary="Financial Management"
                />
                <ListItemSecondaryAction>
                  <Switch defaultChecked />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="HR Module" 
                  secondary="Human Resources Management"
                />
                <ListItemSecondaryAction>
                  <Switch defaultChecked />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Marketing Module" 
                  secondary="Marketing Automation"
                />
                <ListItemSecondaryAction>
                  <Switch defaultChecked />
                </ListItemSecondaryAction>
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Grid>

      {/* System Security */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              System Security
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Multi-Factor Authentication"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Password Complexity"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={<Switch />}
                  label="Biometric Authentication"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Session Encryption"
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* System Integrations */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              System Integrations
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Manage system-wide integrations
            </Typography>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="subtitle1">Available Integrations</Typography>
              <Button
                variant="outlined"
                startIcon={<Add />}
                onClick={() => setDialogOpen(true)}
              >
                Request Integration
              </Button>
            </Box>
            <List>
              <ListItem>
                <ListItemText 
                  primary="Single Sign-On (SSO)" 
                  secondary="Enterprise SSO integration"
                />
                <ListItemSecondaryAction>
                  <Chip label="Active" color="success" size="small" />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Email Service" 
                  secondary="SMTP and email service integration"
                />
                <ListItemSecondaryAction>
                  <Chip label="Active" color="success" size="small" />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Cloud Storage" 
                  secondary="AWS S3, Google Drive, Dropbox"
                />
                <ListItemSecondaryAction>
                  <Chip label="Available" color="default" size="small" />
                </ListItemSecondaryAction>
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Grid>

      {/* System Performance */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              System Performance
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Database Connection Pool"
                  type="number"
                  defaultValue={20}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Cache Size (MB)"
                  type="number"
                  defaultValue={512}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Session Timeout (minutes)"
                  type="number"
                  defaultValue={480}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="API Timeout (seconds)"
                  type="number"
                  defaultValue={30}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* System Backup */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              System Backup
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Backup Frequency</InputLabel>
                  <Select defaultValue="daily">
                    <MenuItem value="hourly">Hourly</MenuItem>
                    <MenuItem value="daily">Daily</MenuItem>
                    <MenuItem value="weekly">Weekly</MenuItem>
                    <MenuItem value="monthly">Monthly</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Retention Period</InputLabel>
                  <Select defaultValue="30">
                    <MenuItem value="7">7 days</MenuItem>
                    <MenuItem value="30">30 days</MenuItem>
                    <MenuItem value="90">90 days</MenuItem>
                    <MenuItem value="365">1 year</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const getTabsForRole = () => {
    switch (userRole) {
      case 'user':
        return [
          { label: 'Personal', icon: <Person /> },
          { label: 'Notifications', icon: <Notifications /> },
          { label: 'Appearance', icon: <Palette /> }
        ];
      case 'admin':
        return [
          { label: 'Personal', icon: <Person /> },
          { label: 'Module Features', icon: <Settings /> },
          { label: 'Integrations', icon: <Integration /> },
          { label: 'Workflows', icon: <AdminPanelSettings /> },
          { label: 'Performance', icon: <Storage /> }
        ];
      case 'super_admin':
        return [
          { label: 'Personal', icon: <Person /> },
          { label: 'System Modules', icon: <AdminPanelSettings /> },
          { label: 'Security', icon: <Security /> },
          { label: 'Integrations', icon: <Integration /> },
          { label: 'Performance', icon: <Storage /> },
          { label: 'Backup', icon: <Storage /> }
        ];
      default:
        return [];
    }
  };

  const renderTabContent = () => {
    switch (userRole) {
      case 'user':
        return renderUserSettings();
      case 'admin':
        return renderAdminSettings();
      case 'super_admin':
        return renderSuperAdminSettings();
      default:
        return null;
    }
  };

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={3}>
        <Settings sx={{ mr: 1 }} />
        <Typography variant="h5">
          {moduleName} Settings
        </Typography>
        <Chip 
          label={userRole.replace('_', ' ').toUpperCase()} 
          color={userRole === 'super_admin' ? 'error' : userRole === 'admin' ? 'warning' : 'default'}
          sx={{ ml: 2 }}
        />
      </Box>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        {getTabsForRole().map((tab, index) => (
          <Tab key={index} label={tab.label} icon={tab.icon} />
        ))}
      </Tabs>

      {renderTabContent()}

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

export default SettingsPanel;
