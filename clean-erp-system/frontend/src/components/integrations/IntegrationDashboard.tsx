import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  CloudSync,
  Api,
  Webhook,
  Store,
  Business,
  People,
  TrendingUp,
  CheckCircle,
  Error,
  Refresh,
  Add,
  Settings,
  PlayArrow,
  Stop,
  Pause,
  Download,
  Share,
  ExpandMore,
  Link,
  Security,
  Speed,
  Analytics
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

interface Connector {
  id: string;
  name: string;
  type: string;
  status: string;
  last_sync: string;
  records_synced: number;
  success_rate: number;
  created_at: string;
}

interface SyncJob {
  id: string;
  connector_id: string;
  sync_type: string;
  status: string;
  started_at: string;
  completed_at?: string;
  records_synced: number;
  records_failed: number;
  error_message?: string;
}

interface APIClient {
  id: string;
  name: string;
  tier: string;
  status: string;
  rate_limit: number;
  created_at: string;
  api_key: string;
}

interface WebhookSubscription {
  id: string;
  client_id: string;
  event_types: string[];
  webhook_url: string;
  is_active: boolean;
  created_at: string;
  last_triggered?: string;
  failure_count: number;
}

const IntegrationDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Data State
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [syncJobs, setSyncJobs] = useState<SyncJob[]>([]);
  const [apiClients, setApiClients] = useState<APIClient[]>([]);
  const [webhookSubscriptions, setWebhookSubscriptions] = useState<WebhookSubscription[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  
  // Dialog States
  const [createConnectorDialog, setCreateConnectorDialog] = useState(false);
  const [createAPIClientDialog, setCreateAPIClientDialog] = useState(false);
  const [createWebhookDialog, setCreateWebhookDialog] = useState(false);
  const [syncDialog, setSyncDialog] = useState(false);
  
  // Form States
  const [newConnector, setNewConnector] = useState({
    type: 'enterprise',
    connector_type: 'sap',
    name: '',
    base_url: '',
    api_key: '',
    secret_key: '',
    username: '',
    password: ''
  });
  
  const [newAPIClient, setNewAPIClient] = useState({
    name: '',
    tier: 'basic',
    webhook_url: '',
    allowed_ips: ''
  });
  
  const [newWebhook, setNewWebhook] = useState({
    client_id: '',
    event_types: [] as string[],
    webhook_url: '',
    secret_key: ''
  });
  
  const [selectedConnector, setSelectedConnector] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load statistics
      const statsResponse = await fetch('/api/integration/status', {
        headers: {
          'X-User-ID': 'current-user'
        }
      });
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStatistics(statsData.status);
      }

      // Load connectors (mock data for now)
      setConnectors([
        {
          id: '1',
          name: 'SAP ERP System',
          type: 'Enterprise',
          status: 'active',
          last_sync: '2024-01-15T10:30:00Z',
          records_synced: 1250,
          success_rate: 98.5,
          created_at: '2024-01-01T00:00:00Z'
        },
        {
          id: '2',
          name: 'Salesforce CRM',
          type: 'CRM',
          status: 'active',
          last_sync: '2024-01-15T09:15:00Z',
          records_synced: 850,
          success_rate: 99.2,
          created_at: '2024-01-02T00:00:00Z'
        },
        {
          id: '3',
          name: 'Shopify Store',
          type: 'E-commerce',
          status: 'active',
          last_sync: '2024-01-15T08:45:00Z',
          records_synced: 2100,
          success_rate: 97.8,
          created_at: '2024-01-03T00:00:00Z'
        }
      ]);

      // Load API clients
      setApiClients([
        {
          id: '1',
          name: 'Mobile App Client',
          tier: 'professional',
          status: 'active',
          rate_limit: 100000,
          created_at: '2024-01-01T00:00:00Z',
          api_key: 'erp_abc123def456'
        },
        {
          id: '2',
          name: 'Partner Integration',
          tier: 'enterprise',
          status: 'active',
          rate_limit: 1000000,
          created_at: '2024-01-02T00:00:00Z',
          api_key: 'erp_xyz789uvw012'
        }
      ]);

      // Load webhook subscriptions
      setWebhookSubscriptions([
        {
          id: '1',
          client_id: '1',
          event_types: ['data_created', 'data_updated'],
          webhook_url: 'https://partner.com/webhooks/erp',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          last_triggered: '2024-01-15T10:30:00Z',
          failure_count: 0
        }
      ]);

    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateConnector = async () => {
    try {
      const response = await fetch('/api/integration/enterprise/connectors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': 'current-user'
        },
        body: JSON.stringify(newConnector)
      });

      if (response.ok) {
        setCreateConnectorDialog(false);
        setNewConnector({
          type: 'enterprise',
          connector_type: 'sap',
          name: '',
          base_url: '',
          api_key: '',
          secret_key: '',
          username: '',
          password: ''
        });
        loadDashboardData();
      }
    } catch (err) {
      console.error('Error creating connector:', err);
    }
  };

  const handleCreateAPIClient = async () => {
    try {
      const response = await fetch('/api/integration/api-marketplace/clients', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': 'current-user'
        },
        body: JSON.stringify(newAPIClient)
      });

      if (response.ok) {
        setCreateAPIClientDialog(false);
        setNewAPIClient({
          name: '',
          tier: 'basic',
          webhook_url: '',
          allowed_ips: ''
        });
        loadDashboardData();
      }
    } catch (err) {
      console.error('Error creating API client:', err);
    }
  };

  const handleCreateWebhook = async () => {
    try {
      const response = await fetch('/api/integration/webhooks/subscriptions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': 'current-user'
        },
        body: JSON.stringify(newWebhook)
      });

      if (response.ok) {
        setCreateWebhookDialog(false);
        setNewWebhook({
          client_id: '',
          event_types: [],
          webhook_url: '',
          secret_key: ''
        });
        loadDashboardData();
      }
    } catch (err) {
      console.error('Error creating webhook:', err);
    }
  };

  const handleSyncConnector = async (connectorId: string, syncType: string) => {
    try {
      const response = await fetch(`/api/integration/enterprise/connectors/${connectorId}/sync`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': 'current-user'
        },
        body: JSON.stringify({
          sync_type: syncType,
          sync_data: {}
        })
      });

      if (response.ok) {
        loadDashboardData();
      }
    } catch (err) {
      console.error('Error syncing connector:', err);
    }
  };

  const renderOverviewTab = () => (
    <Grid container spacing={3}>
      {/* System Status */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <CloudSync sx={{ mr: 1, verticalAlign: 'middle' }} />
              Integration System Status
            </Typography>
            {statistics && (
              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary">
                      {statistics.enterprise_connectors?.total_connectors || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Enterprise Connectors
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary">
                      {statistics.crm_connectors?.total_connectors || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      CRM Connectors
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary">
                      {statistics.ecommerce_connectors?.total_connectors || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      E-commerce Connectors
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary">
                      {statistics.api_marketplace?.total_clients || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      API Clients
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Connectors Overview */}
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                <Link sx={{ mr: 1, verticalAlign: 'middle' }} />
                Active Connectors
              </Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setCreateConnectorDialog(true)}
              >
                Add Connector
              </Button>
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Last Sync</TableCell>
                    <TableCell>Success Rate</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {connectors.map((connector) => (
                    <TableRow key={connector.id}>
                      <TableCell>{connector.name}</TableCell>
                      <TableCell>
                        <Chip 
                          label={connector.type} 
                          size="small" 
                          color={connector.type === 'Enterprise' ? 'primary' : 
                                connector.type === 'CRM' ? 'secondary' : 'success'}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={connector.status}
                          size="small"
                          color={connector.status === 'active' ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(connector.last_sync).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <Typography variant="body2" sx={{ mr: 1 }}>
                            {connector.success_rate}%
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={connector.success_rate}
                            sx={{ width: 60, height: 8 }}
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => handleSyncConnector(connector.id, 'customers')}
                        >
                          <PlayArrow />
                        </IconButton>
                        <IconButton size="small">
                          <Settings />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* Quick Actions */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Speed sx={{ mr: 1, verticalAlign: 'middle' }} />
              Quick Actions
            </Typography>
            <List>
              <ListItem button onClick={() => setCreateConnectorDialog(true)}>
                <ListItemIcon>
                  <Add />
                </ListItemIcon>
                <ListItemText primary="Add New Connector" />
              </ListItem>
              <ListItem button onClick={() => setCreateAPIClientDialog(true)}>
                <ListItemIcon>
                  <Api />
                </ListItemIcon>
                <ListItemText primary="Create API Client" />
              </ListItem>
              <ListItem button onClick={() => setCreateWebhookDialog(true)}>
                <ListItemIcon>
                  <Webhook />
                </ListItemIcon>
                <ListItemText primary="Setup Webhook" />
              </ListItem>
              <ListItem button onClick={loadDashboardData}>
                <ListItemIcon>
                  <Refresh />
                </ListItemIcon>
                <ListItemText primary="Refresh All Data" />
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderConnectorsTab = () => (
    <Grid container spacing={3}>
      {/* Enterprise Connectors */}
      <Grid item xs={12}>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h6">
              <Business sx={{ mr: 1, verticalAlign: 'middle' }} />
              Enterprise Connectors
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {['SAP', 'Oracle', 'Microsoft Dynamics', 'NetSuite'].map((system) => (
                <Grid item xs={12} md={3} key={system}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">{system}</Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        Connect with {system} ERP system for seamless data synchronization
                      </Typography>
                      <Button variant="outlined" size="small" fullWidth>
                        Configure
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </AccordionDetails>
        </Accordion>
      </Grid>

      {/* CRM Connectors */}
      <Grid item xs={12}>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h6">
              <People sx={{ mr: 1, verticalAlign: 'middle' }} />
              CRM Connectors
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {['Salesforce', 'HubSpot', 'Pipedrive', 'Zoho'].map((crm) => (
                <Grid item xs={12} md={3} key={crm}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">{crm}</Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        Integrate with {crm} CRM for customer data management
                      </Typography>
                      <Button variant="outlined" size="small" fullWidth>
                        Configure
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </AccordionDetails>
        </Accordion>
      </Grid>

      {/* E-commerce Connectors */}
      <Grid item xs={12}>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h6">
              <Store sx={{ mr: 1, verticalAlign: 'middle' }} />
              E-commerce Connectors
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {['Shopify', 'WooCommerce', 'Magento', 'Amazon'].map((platform) => (
                <Grid item xs={12} md={3} key={platform}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">{platform}</Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        Connect with {platform} for order and inventory management
                      </Typography>
                      <Button variant="outlined" size="small" fullWidth>
                        Configure
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </AccordionDetails>
        </Accordion>
      </Grid>
    </Grid>
  );

  const renderAPITab = () => (
    <Grid container spacing={3}>
      {/* API Clients */}
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                <Api sx={{ mr: 1, verticalAlign: 'middle' }} />
                API Clients
              </Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setCreateAPIClientDialog(true)}
              >
                Create Client
              </Button>
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Tier</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Rate Limit</TableCell>
                    <TableCell>API Key</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {apiClients.map((client) => (
                    <TableRow key={client.id}>
                      <TableCell>{client.name}</TableCell>
                      <TableCell>
                        <Chip 
                          label={client.tier} 
                          size="small" 
                          color={client.tier === 'enterprise' ? 'primary' : 
                                client.tier === 'professional' ? 'secondary' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={client.status}
                          size="small"
                          color={client.status === 'active' ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell>{client.rate_limit.toLocaleString()}/hour</TableCell>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {client.api_key}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <IconButton size="small">
                          <Settings />
                        </IconButton>
                        <IconButton size="small">
                          <Download />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* API Documentation */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Security sx={{ mr: 1, verticalAlign: 'middle' }} />
              API Documentation
            </Typography>
            <List>
              <ListItem button>
                <ListItemText primary="Authentication Guide" />
              </ListItem>
              <ListItem button>
                <ListItemText primary="Rate Limits" />
              </ListItem>
              <ListItem button>
                <ListItemText primary="SDK Downloads" />
              </ListItem>
              <ListItem button>
                <ListItemText primary="Webhook Setup" />
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderWebhooksTab = () => (
    <Grid container spacing={3}>
      {/* Webhook Subscriptions */}
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                <Webhook sx={{ mr: 1, verticalAlign: 'middle' }} />
                Webhook Subscriptions
              </Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setCreateWebhookDialog(true)}
              >
                Create Subscription
              </Button>
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Client</TableCell>
                    <TableCell>Event Types</TableCell>
                    <TableCell>Webhook URL</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Last Triggered</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {webhookSubscriptions.map((webhook) => (
                    <TableRow key={webhook.id}>
                      <TableCell>Client {webhook.client_id}</TableCell>
                      <TableCell>
                        {webhook.event_types.map((event) => (
                          <Chip key={event} label={event} size="small" sx={{ mr: 0.5 }} />
                        ))}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {webhook.webhook_url}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={webhook.is_active ? 'Active' : 'Inactive'}
                          size="small"
                          color={webhook.is_active ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        {webhook.last_triggered ? 
                          new Date(webhook.last_triggered).toLocaleString() : 
                          'Never'
                        }
                      </TableCell>
                      <TableCell>
                        <IconButton size="small">
                          <Settings />
                        </IconButton>
                        <IconButton size="small">
                          <PlayArrow />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* Webhook Events */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Analytics sx={{ mr: 1, verticalAlign: 'middle' }} />
              Webhook Events
            </Typography>
            <List>
              <ListItem>
                <ListItemText 
                  primary="Data Created" 
                  secondary="Triggered when new data is created"
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Data Updated" 
                  secondary="Triggered when data is modified"
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Order Created" 
                  secondary="Triggered when new orders are placed"
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Payment Processed" 
                  secondary="Triggered when payments are completed"
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <LinearProgress sx={{ width: '50%' }} />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Integration Ecosystem Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Manage enterprise connectors, CRM integrations, e-commerce platforms, API clients, and webhook subscriptions.
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Overview" icon={<CloudSync />} />
          <Tab label="Connectors" icon={<Link />} />
          <Tab label="API Marketplace" icon={<Api />} />
          <Tab label="Webhooks" icon={<Webhook />} />
        </Tabs>
      </Box>

      {activeTab === 0 && renderOverviewTab()}
      {activeTab === 1 && renderConnectorsTab()}
      {activeTab === 2 && renderAPITab()}
      {activeTab === 3 && renderWebhooksTab()}

      {/* Create Connector Dialog */}
      <Dialog open={createConnectorDialog} onClose={() => setCreateConnectorDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Connector</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Connector Type</InputLabel>
                <Select
                  value={newConnector.type}
                  onChange={(e) => setNewConnector(prev => ({ ...prev, type: e.target.value }))}
                >
                  <MenuItem value="enterprise">Enterprise</MenuItem>
                  <MenuItem value="crm">CRM</MenuItem>
                  <MenuItem value="ecommerce">E-commerce</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>System</InputLabel>
                <Select
                  value={newConnector.connector_type}
                  onChange={(e) => setNewConnector(prev => ({ ...prev, connector_type: e.target.value }))}
                >
                  <MenuItem value="sap">SAP</MenuItem>
                  <MenuItem value="oracle">Oracle</MenuItem>
                  <MenuItem value="microsoft_dynamics">Microsoft Dynamics</MenuItem>
                  <MenuItem value="netsuite">NetSuite</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Connector Name"
                value={newConnector.name}
                onChange={(e) => setNewConnector(prev => ({ ...prev, name: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Base URL"
                value={newConnector.base_url}
                onChange={(e) => setNewConnector(prev => ({ ...prev, base_url: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="API Key"
                value={newConnector.api_key}
                onChange={(e) => setNewConnector(prev => ({ ...prev, api_key: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Secret Key"
                type="password"
                value={newConnector.secret_key}
                onChange={(e) => setNewConnector(prev => ({ ...prev, secret_key: e.target.value }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateConnectorDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateConnector} variant="contained">Create Connector</Button>
        </DialogActions>
      </Dialog>

      {/* Create API Client Dialog */}
      <Dialog open={createAPIClientDialog} onClose={() => setCreateAPIClientDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create API Client</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Client Name"
                value={newAPIClient.name}
                onChange={(e) => setNewAPIClient(prev => ({ ...prev, name: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>API Tier</InputLabel>
                <Select
                  value={newAPIClient.tier}
                  onChange={(e) => setNewAPIClient(prev => ({ ...prev, tier: e.target.value }))}
                >
                  <MenuItem value="free">Free (1,000 requests/hour)</MenuItem>
                  <MenuItem value="basic">Basic (10,000 requests/hour)</MenuItem>
                  <MenuItem value="professional">Professional (100,000 requests/hour)</MenuItem>
                  <MenuItem value="enterprise">Enterprise (1,000,000 requests/hour)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Webhook URL (Optional)"
                value={newAPIClient.webhook_url}
                onChange={(e) => setNewAPIClient(prev => ({ ...prev, webhook_url: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Allowed IPs (Optional)"
                value={newAPIClient.allowed_ips}
                onChange={(e) => setNewAPIClient(prev => ({ ...prev, allowed_ips: e.target.value }))}
                placeholder="192.168.1.1, 10.0.0.1"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateAPIClientDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateAPIClient} variant="contained">Create Client</Button>
        </DialogActions>
      </Dialog>

      {/* Create Webhook Dialog */}
      <Dialog open={createWebhookDialog} onClose={() => setCreateWebhookDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Webhook Subscription</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>API Client</InputLabel>
                <Select
                  value={newWebhook.client_id}
                  onChange={(e) => setNewWebhook(prev => ({ ...prev, client_id: e.target.value }))}
                >
                  {apiClients.map((client) => (
                    <MenuItem key={client.id} value={client.id}>
                      {client.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Webhook URL"
                value={newWebhook.webhook_url}
                onChange={(e) => setNewWebhook(prev => ({ ...prev, webhook_url: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Secret Key"
                value={newWebhook.secret_key}
                onChange={(e) => setNewWebhook(prev => ({ ...prev, secret_key: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Event Types</InputLabel>
                <Select
                  multiple
                  value={newWebhook.event_types}
                  onChange={(e) => setNewWebhook(prev => ({ ...prev, event_types: e.target.value as string[] }))}
                >
                  <MenuItem value="data_created">Data Created</MenuItem>
                  <MenuItem value="data_updated">Data Updated</MenuItem>
                  <MenuItem value="data_deleted">Data Deleted</MenuItem>
                  <MenuItem value="order_created">Order Created</MenuItem>
                  <MenuItem value="payment_processed">Payment Processed</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateWebhookDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateWebhook} variant="contained">Create Webhook</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default IntegrationDashboard;
