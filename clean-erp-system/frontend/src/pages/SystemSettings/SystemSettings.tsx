// System Settings Page
// Comprehensive system settings management

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Paper,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Button,
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
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Business as BusinessIcon,
  People as PeopleIcon,
  Workflow as WorkflowIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Api as ApiIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';

interface SystemSettingsProps {}

const SystemSettings: React.FC<SystemSettingsProps> = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogType, setDialogType] = useState('');
  const [formData, setFormData] = useState({});
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleOpenDialog = (type: string, data?: any) => {
    setDialogType(type);
    setFormData(data || {});
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setFormData({});
  };

  const handleSave = () => {
    // Handle save logic here
    setSnackbar({ open: true, message: 'Settings saved successfully', severity: 'success' });
    handleCloseDialog();
  };

  const handleDelete = (id: string) => {
    // Handle delete logic here
    setSnackbar({ open: true, message: 'Item deleted successfully', severity: 'success' });
  };

  const tabs = [
    { label: 'General Settings', icon: <SettingsIcon />, value: 0 },
    { label: 'Departments', icon: <BusinessIcon />, value: 1 },
    { label: 'User Profiles', icon: <PeopleIcon />, value: 2 },
    { label: 'Workflows', icon: <WorkflowIcon />, value: 3 },
    { label: 'Security', icon: <SecurityIcon />, value: 4 },
    { label: 'Data Management', icon: <StorageIcon />, value: 5 },
    { label: 'API Marketplace', icon: <ApiIcon />, value: 6 }
  ];

  const renderGeneralSettings = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        General System Settings
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Company Information" />
            <CardContent>
              <TextField
                fullWidth
                label="Company Name"
                variant="outlined"
                margin="normal"
              />
              <TextField
                fullWidth
                label="Company Code"
                variant="outlined"
                margin="normal"
              />
              <TextField
                fullWidth
                label="Company Description"
                variant="outlined"
                margin="normal"
                multiline
                rows={3}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="System Preferences" />
            <CardContent>
              <FormControl fullWidth margin="normal">
                <InputLabel>Default Language</InputLabel>
                <Select value="en">
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="es">Spanish</MenuItem>
                  <MenuItem value="fr">French</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth margin="normal">
                <InputLabel>Default Currency</InputLabel>
                <Select value="USD">
                  <MenuItem value="USD">USD</MenuItem>
                  <MenuItem value="EUR">EUR</MenuItem>
                  <MenuItem value="GBP">GBP</MenuItem>
                </Select>
              </FormControl>
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Enable Real-time Sync"
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderDepartments = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Departments</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog('department')}
        >
          Add Department
        </Button>
      </Box>
      <Grid container spacing={3}>
        {[1, 2, 3].map((dept) => (
          <Grid item xs={12} md={4} key={dept}>
            <Card>
              <CardHeader
                title={`Department ${dept}`}
                action={
                  <Box>
                    <IconButton onClick={() => handleOpenDialog('department', { id: dept })}>
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(dept.toString())}>
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                }
              />
              <CardContent>
                <Typography variant="body2" color="textSecondary">
                  Department description and details
                </Typography>
                <Box mt={2}>
                  <Chip label="Active" color="success" size="small" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderUserProfiles = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">User Profiles</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog('userProfile')}
        >
          Add User Profile
        </Button>
      </Box>
      <List>
        {[1, 2, 3].map((profile) => (
          <ListItem key={profile}>
            <ListItemText
              primary={`User Profile ${profile}`}
              secondary="Profile description and details"
            />
            <ListItemSecondaryAction>
              <IconButton onClick={() => handleOpenDialog('userProfile', { id: profile })}>
                <EditIcon />
              </IconButton>
              <IconButton onClick={() => handleDelete(profile.toString())}>
                <DeleteIcon />
              </IconButton>
            </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  const renderWorkflows = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Workflow Templates</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog('workflow')}
        >
          Add Workflow Template
        </Button>
      </Box>
      <Grid container spacing={3}>
        {[1, 2, 3].map((workflow) => (
          <Grid item xs={12} md={4} key={workflow}>
            <Card>
              <CardHeader
                title={`Workflow Template ${workflow}`}
                action={
                  <Box>
                    <IconButton onClick={() => handleOpenDialog('workflow', { id: workflow })}>
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(workflow.toString())}>
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                }
              />
              <CardContent>
                <Typography variant="body2" color="textSecondary">
                  Workflow description and details
                </Typography>
                <Box mt={2}>
                  <Chip label="Active" color="success" size="small" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderSecurity = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Security Settings
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="User Roles" />
            <CardContent>
              <List>
                {['Admin', 'Manager', 'User'].map((role) => (
                  <ListItem key={role}>
                    <ListItemText primary={role} />
                    <ListItemSecondaryAction>
                      <IconButton>
                        <EditIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Permissions" />
            <CardContent>
              <List>
                {['Read', 'Write', 'Delete', 'Admin'].map((permission) => (
                  <ListItem key={permission}>
                    <ListItemText primary={permission} />
                    <ListItemSecondaryAction>
                      <IconButton>
                        <EditIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderDataManagement = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Data Management
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Data Archives" />
            <CardContent>
              <Typography variant="body2" color="textSecondary">
                Manage data archiving and retention policies
              </Typography>
              <Button variant="outlined" sx={{ mt: 2 }}>
                Configure Archives
              </Button>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Backup Settings" />
            <CardContent>
              <Typography variant="body2" color="textSecondary">
                Configure automated backups and data protection
              </Typography>
              <Button variant="outlined" sx={{ mt: 2 }}>
                Configure Backups
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderAPIMarketplace = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">API Marketplace</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog('api')}
        >
          Add API
        </Button>
      </Box>
      <Grid container spacing={3}>
        {[1, 2, 3].map((api) => (
          <Grid item xs={12} md={4} key={api}>
            <Card>
              <CardHeader
                title={`API ${api}`}
                action={
                  <Box>
                    <IconButton onClick={() => handleOpenDialog('api', { id: api })}>
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(api.toString())}>
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                }
              />
              <CardContent>
                <Typography variant="body2" color="textSecondary">
                  API description and details
                </Typography>
                <Box mt={2}>
                  <Chip label="Active" color="success" size="small" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 0:
        return renderGeneralSettings();
      case 1:
        return renderDepartments();
      case 2:
        return renderUserProfiles();
      case 3:
        return renderWorkflows();
      case 4:
        return renderSecurity();
      case 5:
        return renderDataManagement();
      case 6:
        return renderAPIMarketplace();
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        System Settings
      </Typography>
      
      <Paper sx={{ mt: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          {tabs.map((tab) => (
            <Tab
              key={tab.value}
              label={tab.label}
              icon={tab.icon}
              iconPosition="start"
            />
          ))}
        </Tabs>
        
        <Box sx={{ p: 3 }}>
          {renderTabContent()}
        </Box>
      </Paper>

      {/* Dialog for creating/editing items */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogType === 'department' ? 'Department' :
           dialogType === 'userProfile' ? 'User Profile' :
           dialogType === 'workflow' ? 'Workflow Template' :
           dialogType === 'api' ? 'API' : 'Item'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Name"
            variant="outlined"
            margin="normal"
          />
          <TextField
            fullWidth
            label="Description"
            variant="outlined"
            margin="normal"
            multiline
            rows={3}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Status</InputLabel>
            <Select value="active">
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="inactive">Inactive</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} startIcon={<CancelIcon />}>
            Cancel
          </Button>
          <Button onClick={handleSave} startIcon={<SaveIcon />} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity as any}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default SystemSettings;
