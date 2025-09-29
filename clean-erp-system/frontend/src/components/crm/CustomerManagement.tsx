// Customer Management Component
// Full-featured customer management with CRUD operations, import/export, real-time sync

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
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
  Fab,
  Tooltip,
  Menu,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar,
  Badge,
  LinearProgress,
  Autocomplete,
  Pagination,
  Checkbox,
  FormGroup
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  FilterList,
  Download,
  Upload,
  Refresh,
  MoreVert,
  Visibility,
  Phone,
  Email,
  LocationOn,
  Business,
  Person,
  Star,
  StarBorder,
  Sync,
  CloudSync,
  CloudDone,
  CloudOff,
  GetApp,
  Publish,
  FileDownload,
  FileUpload,
  Print,
  Share,
  Archive,
  RestoreFromTrash,
  Settings,
  Analytics,
  Timeline,
  Assessment
} from '@mui/icons-material';

interface Customer {
  id: number;
  name: string;
  email: string;
  phone: string;
  company: string;
  status: 'active' | 'inactive' | 'prospect' | 'customer';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  source: string;
  lastContact: string;
  totalValue: number;
  avatar?: string;
  address?: string;
  notes?: string;
  tags?: string[];
  assignedTo?: string;
  createdAt: string;
  updatedAt: string;
}

interface CustomerManagementProps {
  onCustomerSelect?: (customer: Customer) => void;
  onFullPageView?: (view: string, data?: any) => void;
}

const CustomerManagement: React.FC<CustomerManagementProps> = ({ 
  onCustomerSelect, 
  onFullPageView 
}) => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [filteredCustomers, setFilteredCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [selectedCustomers, setSelectedCustomers] = useState<number[]>([]);
  const [page, setPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'table'>('table');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [realtimeStatus, setRealtimeStatus] = useState<'connected' | 'disconnected' | 'syncing'>('connected');
  
  // Dialog states
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState<'create' | 'edit' | 'view'>('create');
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  
  // Form states
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    status: 'prospect',
    priority: 'medium',
    source: '',
    address: '',
    notes: '',
    tags: [] as string[],
    assignedTo: ''
  });

  useEffect(() => {
    fetchCustomers();
    // Set up real-time sync
    setupRealtimeSync();
  }, []);

  useEffect(() => {
    filterCustomers();
  }, [customers, searchTerm, statusFilter, priorityFilter]);

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/crm/customers');
      const data = await response.json();
      if (data.success) {
        setCustomers(data.data);
      } else {
        setError('Failed to fetch customers');
      }
    } catch (err) {
      setError('Failed to fetch customers');
    } finally {
      setLoading(false);
    }
  };

  const setupRealtimeSync = () => {
    // Simulate real-time sync status
    setRealtimeStatus('connected');
    
    // In a real implementation, this would set up WebSocket connection
    // for real-time updates
  };

  const filterCustomers = () => {
    let filtered = customers.filter(customer => {
      const matchesSearch = customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          customer.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          customer.company.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === 'all' || customer.status === statusFilter;
      const matchesPriority = priorityFilter === 'all' || customer.priority === priorityFilter;
      
      return matchesSearch && matchesStatus && matchesPriority;
    });

    // Sort customers
    filtered.sort((a, b) => {
      const aValue = a[sortBy as keyof Customer];
      const bValue = b[sortBy as keyof Customer];
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredCustomers(filtered);
  };

  const handleCreateCustomer = async () => {
    try {
      const response = await fetch('/api/crm/customers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Customer created successfully');
        setDialogOpen(false);
        fetchCustomers();
        resetForm();
      } else {
        setError(data.error || 'Failed to create customer');
      }
    } catch (err) {
      setError('Failed to create customer');
    }
  };

  const handleUpdateCustomer = async () => {
    if (!selectedCustomer) return;
    
    try {
      const response = await fetch(`/api/crm/customers/${selectedCustomer.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Customer updated successfully');
        setDialogOpen(false);
        fetchCustomers();
        resetForm();
      } else {
        setError(data.error || 'Failed to update customer');
      }
    } catch (err) {
      setError('Failed to update customer');
    }
  };

  const handleDeleteCustomer = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this customer?')) {
      try {
        const response = await fetch(`/api/crm/customers/${id}`, {
          method: 'DELETE'
        });
        const data = await response.json();
        if (data.success) {
          setSuccess('Customer deleted successfully');
          fetchCustomers();
        } else {
          setError(data.error || 'Failed to delete customer');
        }
      } catch (err) {
        setError('Failed to delete customer');
      }
    }
  };

  const handleImportCustomers = async (file: File) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('/api/crm/customers/import', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      if (data.success) {
        setSuccess(`Successfully imported ${data.importedCount} customers`);
        setImportDialogOpen(false);
        fetchCustomers();
      } else {
        setError(data.error || 'Failed to import customers');
      }
    } catch (err) {
      setError('Failed to import customers');
    } finally {
      setLoading(false);
    }
  };

  const handleExportCustomers = async (format: 'csv' | 'excel' | 'pdf') => {
    try {
      const response = await fetch(`/api/crm/customers/export?format=${format}`, {
        method: 'GET'
      });
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `customers.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
      setSuccess('Customers exported successfully');
      setExportDialogOpen(false);
    } catch (err) {
      setError('Failed to export customers');
    }
  };

  const handleBulkAction = async (action: string) => {
    if (selectedCustomers.length === 0) return;
    
    try {
      const response = await fetch('/api/crm/customers/bulk-action', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action,
          customerIds: selectedCustomers
        })
      });
      const data = await response.json();
      if (data.success) {
        setSuccess(`Bulk action completed successfully`);
        setSelectedCustomers([]);
        fetchCustomers();
      } else {
        setError(data.error || 'Failed to perform bulk action');
      }
    } catch (err) {
      setError('Failed to perform bulk action');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      phone: '',
      company: '',
      status: 'prospect',
      priority: 'medium',
      source: '',
      address: '',
      notes: '',
      tags: [],
      assignedTo: ''
    });
  };

  const openDialog = (type: 'create' | 'edit' | 'view', customer?: Customer) => {
    setDialogType(type);
    setSelectedCustomer(customer || null);
    
    if (customer && (type === 'edit' || type === 'view')) {
      setFormData({
        name: customer.name,
        email: customer.email,
        phone: customer.phone,
        company: customer.company,
        status: customer.status,
        priority: customer.priority,
        source: customer.source,
        address: customer.address || '',
        notes: customer.notes || '',
        tags: customer.tags || [],
        assignedTo: customer.assignedTo || ''
      });
    } else if (type === 'create') {
      resetForm();
    }
    
    setDialogOpen(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'error';
      case 'prospect': return 'warning';
      case 'customer': return 'info';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'default';
      default: return 'default';
    }
  };

  const renderCustomerTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">
              <Checkbox
                indeterminate={selectedCustomers.length > 0 && selectedCustomers.length < filteredCustomers.length}
                checked={selectedCustomers.length === filteredCustomers.length && filteredCustomers.length > 0}
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedCustomers(filteredCustomers.map(c => c.id));
                  } else {
                    setSelectedCustomers([]);
                  }
                }}
              />
            </TableCell>
            <TableCell>Customer</TableCell>
            <TableCell>Company</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Priority</TableCell>
            <TableCell>Last Contact</TableCell>
            <TableCell>Total Value</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {filteredCustomers
            .slice((page - 1) * rowsPerPage, page * rowsPerPage)
            .map((customer) => (
            <TableRow key={customer.id} hover>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={selectedCustomers.includes(customer.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedCustomers([...selectedCustomers, customer.id]);
                    } else {
                      setSelectedCustomers(selectedCustomers.filter(id => id !== customer.id));
                    }
                  }}
                />
              </TableCell>
              <TableCell>
                <Box display="flex" alignItems="center">
                  <Avatar sx={{ mr: 2, width: 32, height: 32 }}>
                    {customer.name.charAt(0)}
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle2">{customer.name}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {customer.email}
                    </Typography>
                  </Box>
                </Box>
              </TableCell>
              <TableCell>{customer.company}</TableCell>
              <TableCell>
                <Chip
                  label={customer.status}
                  color={getStatusColor(customer.status)}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Chip
                  label={customer.priority}
                  color={getPriorityColor(customer.priority)}
                  size="small"
                />
              </TableCell>
              <TableCell>{customer.lastContact}</TableCell>
              <TableCell>${customer.totalValue.toLocaleString()}</TableCell>
              <TableCell>
                <IconButton
                  size="small"
                  onClick={() => openDialog('view', customer)}
                >
                  <Visibility />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => openDialog('edit', customer)}
                >
                  <Edit />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => handleDeleteCustomer(customer.id)}
                >
                  <Delete />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const renderCustomerDialog = () => (
    <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        {dialogType === 'create' ? 'Create Customer' : 
         dialogType === 'edit' ? 'Edit Customer' : 'View Customer'}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Customer Name"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              disabled={dialogType === 'view'}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              disabled={dialogType === 'view'}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Phone"
              value={formData.phone}
              onChange={(e) => setFormData({...formData, phone: e.target.value})}
              disabled={dialogType === 'view'}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Company"
              value={formData.company}
              onChange={(e) => setFormData({...formData, company: e.target.value})}
              disabled={dialogType === 'view'}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={formData.status}
                onChange={(e) => setFormData({...formData, status: e.target.value})}
                disabled={dialogType === 'view'}
              >
                <MenuItem value="prospect">Prospect</MenuItem>
                <MenuItem value="customer">Customer</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={formData.priority}
                onChange={(e) => setFormData({...formData, priority: e.target.value})}
                disabled={dialogType === 'view'}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="urgent">Urgent</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Address"
              multiline
              rows={2}
              value={formData.address}
              onChange={(e) => setFormData({...formData, address: e.target.value})}
              disabled={dialogType === 'view'}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Notes"
              multiline
              rows={3}
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
              disabled={dialogType === 'view'}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
        {dialogType !== 'view' && (
          <Button
            variant="contained"
            onClick={dialogType === 'create' ? handleCreateCustomer : handleUpdateCustomer}
          >
            {dialogType === 'create' ? 'Create' : 'Update'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );

  const renderImportDialog = () => (
    <Dialog open={importDialogOpen} onClose={() => setImportDialogOpen(false)} maxWidth="sm" fullWidth>
      <DialogTitle>Import Customers</DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Upload a CSV or Excel file with customer data. The file should include columns for:
            name, email, phone, company, status, priority, source, address, notes.
          </Typography>
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                handleImportCustomers(file);
              }
            }}
            style={{ marginTop: 16 }}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setImportDialogOpen(false)}>Cancel</Button>
      </DialogActions>
    </Dialog>
  );

  const renderExportDialog = () => (
    <Dialog open={exportDialogOpen} onClose={() => setExportDialogOpen(false)} maxWidth="sm" fullWidth>
      <DialogTitle>Export Customers</DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Choose the format for exporting customer data:
          </Typography>
          <Box display="flex" gap={2} sx={{ mt: 2 }}>
            <Button
              variant="outlined"
              startIcon={<FileDownload />}
              onClick={() => handleExportCustomers('csv')}
            >
              CSV
            </Button>
            <Button
              variant="outlined"
              startIcon={<FileDownload />}
              onClick={() => handleExportCustomers('excel')}
            >
              Excel
            </Button>
            <Button
              variant="outlined"
              startIcon={<FileDownload />}
              onClick={() => handleExportCustomers('pdf')}
            >
              PDF
            </Button>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setExportDialogOpen(false)}>Cancel</Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Box>
      {/* Header with Actions */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Customer Management</Typography>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Upload />}
            onClick={() => setImportDialogOpen(true)}
          >
            Import
          </Button>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={() => setExportDialogOpen(true)}
          >
            Export
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => openDialog('create')}
          >
            Add Customer
          </Button>
        </Box>
      </Box>

      {/* Filters and Search */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search customers..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="prospect">Prospect</MenuItem>
                  <MenuItem value="customer">Customer</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={priorityFilter}
                  onChange={(e) => setPriorityFilter(e.target.value)}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                variant="outlined"
                startIcon={<FilterList />}
                onClick={() => {/* Filter logic */}}
              >
                More Filters
              </Button>
            </Grid>
            <Grid item xs={12} md={2}>
              <Box display="flex" gap={1}>
                <Tooltip title="Refresh">
                  <IconButton onClick={fetchCustomers}>
                    <Refresh />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Real-time Sync">
                  <IconButton>
                    {realtimeStatus === 'connected' ? <CloudDone /> : 
                     realtimeStatus === 'syncing' ? <CloudSync /> : <CloudOff />}
                  </IconButton>
                </Tooltip>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Bulk Actions */}
      {selectedCustomers.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <Typography variant="body2">
                {selectedCustomers.length} customers selected
              </Typography>
              <Button
                size="small"
                onClick={() => handleBulkAction('activate')}
              >
                Activate
              </Button>
              <Button
                size="small"
                onClick={() => handleBulkAction('deactivate')}
              >
                Deactivate
              </Button>
              <Button
                size="small"
                onClick={() => handleBulkAction('delete')}
                color="error"
              >
                Delete
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Customer Table */}
      {loading ? (
        <LinearProgress />
      ) : (
        renderCustomerTable()
      )}

      {/* Pagination */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mt={3}>
        <Typography variant="body2" color="textSecondary">
          Showing {((page - 1) * rowsPerPage) + 1} to {Math.min(page * rowsPerPage, filteredCustomers.length)} of {filteredCustomers.length} customers
        </Typography>
        <Pagination
          count={Math.ceil(filteredCustomers.length / rowsPerPage)}
          page={page}
          onChange={(e, newPage) => setPage(newPage)}
        />
      </Box>

      {/* Dialogs */}
      {renderCustomerDialog()}
      {renderImportDialog()}
      {renderExportDialog()}

      {/* Snackbars */}
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

export default CustomerManagement;
