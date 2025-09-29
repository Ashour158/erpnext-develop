// System Admin Panel Component
// Comprehensive system administration interface

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
  Snackbar
} from '@mui/material';
import {
  AdminPanelSettings,
  People,
  Business,
  Settings,
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
  Error
} from '@mui/icons-material';

interface SystemAdminPanelProps {
  onModuleSelect?: (module: string) => void;
}

const SystemAdminPanel: React.FC<SystemAdminPanelProps> = ({ onModuleSelect }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [systemStats, setSystemStats] = useState({
    totalUsers: 0,
    totalDepartments: 0,
    totalModules: 0,
    totalRoles: 0,
    totalPermissions: 0,
    activeModules: 0,
    inactiveModules: 0,
    adminUsers: 0,
    regularUsers: 0
  });
  const [systemHealth, setSystemHealth] = useState({
    overallHealth: 100,
    totalChecks: 0,
    healthyChecks: 0,
    warningChecks: 0,
    criticalChecks: 0
  });
  const [modules, setModules] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState('');
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    fetchSystemData();
  }, []);

  const fetchSystemData = async () => {
    setLoading(true);
    try {
      // Fetch system dashboard data
      const dashboardResponse = await fetch('/api/system-admin/dashboard');
      const dashboardData = await dashboardResponse.json();
      if (dashboardData.success) {
        setSystemStats(dashboardData.data);
      }

      // Fetch system health
      const healthResponse = await fetch('/api/system-admin/health');
      const healthData = await healthResponse.json();
      if (healthData.success) {
        setSystemHealth(healthData.data);
      }

      // Fetch modules
      const modulesResponse = await fetch('/api/system-admin/modules');
      const modulesData = await modulesResponse.json();
      if (modulesData.success) {
        setModules(modulesData.data);
      }

      // Fetch departments
      const departmentsResponse = await fetch('/api/system-admin/departments');
      const departmentsData = await departmentsResponse.json();
      if (departmentsData.success) {
        setDepartments(departmentsData.data);
      }

      // Fetch users
      const usersResponse = await fetch('/api/system-admin/users');
      const usersData = await usersResponse.json();
      if (usersData.success) {
        setUsers(usersData.data);
      }

      // Fetch roles
      const rolesResponse = await fetch('/api/system-admin/roles');
      const rolesData = await rolesResponse.json();
      if (rolesData.success) {
        setRoles(rolesData.data);
      }

      // Fetch permissions
      const permissionsResponse = await fetch('/api/system-admin/permissions');
      const permissionsData = await permissionsResponse.json();
      if (permissionsData.success) {
        setPermissions(permissionsData.data);
      }

      // Fetch audit logs
      const auditResponse = await fetch('/api/system-admin/audit-logs');
      const auditData = await auditResponse.json();
      if (auditData.success) {
        setAuditLogs(auditData.data);
      }
    } catch (err) {
      setError('Failed to fetch system data');
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
        const response = await fetch(`/api/system-admin/${type}/${id}`, {
          method: 'DELETE'
        });
        const data = await response.json();
        if (data.success) {
          setSuccess('Item deleted successfully');
          fetchSystemData();
        } else {
          setError(data.error || 'Failed to delete item');
        }
      } catch (err) {
        setError('Failed to delete item');
      }
    }
  };

  const handleModuleStatusChange = async (moduleId: number, status: string) => {
    try {
      const response = await fetch(`/api/system-admin/modules/${moduleId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ module_status: status })
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Module status updated successfully');
        fetchSystemData();
      } else {
        setError(data.error || 'Failed to update module status');
      }
    } catch (err) {
      setError('Failed to update module status');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'error';
      case 'maintenance': return 'warning';
      case 'deprecated': return 'default';
      default: return 'default';
    }
  };

  const getHealthColor = (health: number) => {
    if (health >= 90) return 'success';
    if (health >= 70) return 'warning';
    return 'error';
  };

  const renderOverview = () => (
    <Grid container spacing={3}>
      {/* System Overview Cards */}
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Users
                </Typography>
                <Typography variant="h4">
                  {systemStats.totalUsers}
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
                  Total Modules
                </Typography>
                <Typography variant="h4">
                  {systemStats.totalModules}
                </Typography>
              </Box>
              <AdminPanelSettings color="primary" />
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
                  Total Departments
                </Typography>
                <Typography variant="h4">
                  {systemStats.totalDepartments}
                </Typography>
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
                  System Health
                </Typography>
                <Typography variant="h4" color={getHealthColor(systemHealth.overallHealth)}>
                  {systemHealth.overallHealth}%
                </Typography>
              </Box>
              <CheckCircle color={getHealthColor(systemHealth.overallHealth)} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* System Health Details */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              System Health Details
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success.main">
                    {systemHealth.healthyChecks}
                  </Typography>
                  <Typography color="textSecondary">Healthy</Typography>
                </Box>
              </Grid>
              <Grid item xs={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="warning.main">
                    {systemHealth.warningChecks}
                  </Typography>
                  <Typography color="textSecondary">Warning</Typography>
                </Box>
              </Grid>
              <Grid item xs={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="error.main">
                    {systemHealth.criticalChecks}
                  </Typography>
                  <Typography color="textSecondary">Critical</Typography>
                </Box>
              </Grid>
              <Grid item xs={3}>
                <Box textAlign="center">
                  <Typography variant="h4">
                    {systemHealth.totalChecks}
                  </Typography>
                  <Typography color="textSecondary">Total Checks</Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderModules = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">System Modules</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleCreateItem('module')}
          >
            Add Module
          </Button>
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Module Name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Performance</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {modules.map((module: any) => (
                <TableRow key={module.id}>
                  <TableCell>
                    <Typography variant="subtitle2">{module.module_display_name}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {module.module_name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={module.module_status}
                      color={getStatusColor(module.module_status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{module.module_version}</TableCell>
                  <TableCell>{module.module_category}</TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {module.module_performance_score}%
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleEditItem(module, 'module')}
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleModuleStatusChange(module.id, 
                        module.module_status === 'active' ? 'inactive' : 'active'
                      )}
                    >
                      {module.module_status === 'active' ? <Block /> : <CheckCircle />}
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

  const renderDepartments = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Departments</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleCreateItem('department')}
          >
            Add Department
          </Button>
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Department Name</TableCell>
                <TableCell>Code</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Head</TableCell>
                <TableCell>Budget</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {departments.map((dept: any) => (
                <TableRow key={dept.id}>
                  <TableCell>
                    <Typography variant="subtitle2">{dept.department_name}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {dept.department_description}
                    </Typography>
                  </TableCell>
                  <TableCell>{dept.department_code}</TableCell>
                  <TableCell>
                    <Chip
                      label={dept.department_status}
                      color={getStatusColor(dept.department_status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{dept.head?.name || 'N/A'}</TableCell>
                  <TableCell>${dept.department_budget?.toLocaleString() || '0'}</TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleEditItem(dept, 'department')}
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteItem(dept.id, 'departments')}
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

  const renderUsers = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Users</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleCreateItem('user')}
          >
            Add User
          </Button>
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user: any) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <Typography variant="subtitle2">{user.name}</Typography>
                  </TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <Chip label={user.role || 'User'} size="small" />
                  </TableCell>
                  <TableCell>{user.department?.department_name || 'N/A'}</TableCell>
                  <TableCell>
                    <Chip
                      label={user.is_active ? 'Active' : 'Inactive'}
                      color={user.is_active ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleEditItem(user, 'user')}
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteItem(user.id, 'users')}
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

  const renderAuditLogs = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          System Audit Logs
        </Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Module</TableCell>
                <TableCell>Result</TableCell>
                <TableCell>IP Address</TableCell>
                <TableCell>Timestamp</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {auditLogs.map((log: any) => (
                <TableRow key={log.id}>
                  <TableCell>{log.user?.name || 'System'}</TableCell>
                  <TableCell>
                    <Chip
                      label={log.action_type}
                      size="small"
                      color={log.action_result === 'success' ? 'success' : 'error'}
                    />
                  </TableCell>
                  <TableCell>{log.action_module || 'N/A'}</TableCell>
                  <TableCell>
                    <Chip
                      label={log.action_result}
                      size="small"
                      color={log.action_result === 'success' ? 'success' : 'error'}
                    />
                  </TableCell>
                  <TableCell>{log.request_ip}</TableCell>
                  <TableCell>
                    {new Date(log.action_timestamp).toLocaleString()}
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
      <Typography variant="h4" gutterBottom>
        System Administration
      </Typography>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Overview" />
        <Tab label="Modules" />
        <Tab label="Departments" />
        <Tab label="Users" />
        <Tab label="Roles & Permissions" />
        <Tab label="Audit Logs" />
        <Tab label="System Health" />
      </Tabs>

      {activeTab === 0 && renderOverview()}
      {activeTab === 1 && renderModules()}
      {activeTab === 2 && renderDepartments()}
      {activeTab === 3 && renderUsers()}
      {activeTab === 4 && (
        <Card>
          <CardContent>
            <Typography variant="h6">Roles & Permissions</Typography>
            <Typography>Roles and permissions management will be implemented here</Typography>
          </CardContent>
        </Card>
      )}
      {activeTab === 5 && renderAuditLogs()}
      {activeTab === 6 && (
        <Card>
          <CardContent>
            <Typography variant="h6">System Health</Typography>
            <Typography>System health monitoring will be implemented here</Typography>
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

export default SystemAdminPanel;
