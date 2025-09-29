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
  Divider
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Analytics,
  AutoGraph,
  Insights,
  Warning,
  CheckCircle,
  Error,
  Refresh,
  Download,
  Share,
  Settings,
  PlayArrow,
  Stop,
  Pause
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

interface PredictionResult {
  value: number;
  confidence: number;
  model_accuracy: number;
  features_importance: Record<string, number>;
  timestamp: string;
}

interface AnalyticsInsight {
  insight_type: string;
  title: string;
  description: string;
  confidence: number;
  impact: string;
  recommendations: string[];
  data_points: Record<string, any>;
  timestamp: string;
}

interface AutomationRule {
  id: string;
  name: string;
  description: string;
  trigger: string;
  status: string;
  execution_count: number;
  success_count: number;
  failure_count: number;
  last_executed: string;
  created_at: string;
}

const AIAnalyticsDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Analytics State
  const [predictions, setPredictions] = useState<PredictionResult[]>([]);
  const [insights, setInsights] = useState<AnalyticsInsight[]>([]);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  
  // Automation State
  const [automationRules, setAutomationRules] = useState<AutomationRule[]>([]);
  const [automationStats, setAutomationStats] = useState<any>(null);
  
  // NLP State
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  
  // Dialog States
  const [createRuleDialog, setCreateRuleDialog] = useState(false);
  const [newRule, setNewRule] = useState({
    name: '',
    description: '',
    trigger: 'event_based',
    conditions: [],
    actions: []
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load analytics insights
      const insightsResponse = await fetch('/api/ai/analytics/insights', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': 'current-user'
        },
        body: JSON.stringify({
          sales_data: generateMockSalesData(),
          customer_data: generateMockCustomerData(),
          inventory_data: generateMockInventoryData()
        })
      });
      
      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setInsights(insightsData.insights || []);
      }

      // Load automation statistics
      const statsResponse = await fetch('/api/ai/automation/statistics', {
        headers: {
          'X-User-ID': 'current-user'
        }
      });
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setAutomationStats(statsData.statistics);
      }

      // Load automation rules
      const rulesResponse = await fetch('/api/ai/automation/rules', {
        headers: {
          'X-User-ID': 'current-user'
        }
      });
      
      if (rulesResponse.ok) {
        const rulesData = await rulesResponse.json();
        setAutomationRules(rulesData.rules || []);
      }

    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateMockSalesData = () => {
    const data = [];
    const today = new Date();
    for (let i = 0; i < 30; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      data.push({
        date: date.toISOString().split('T')[0],
        sales_amount: Math.random() * 10000 + 5000
      });
    }
    return data;
  };

  const generateMockCustomerData = () => {
    return [
      { customer_id: 1, total_orders: 15, total_spent: 2500, days_since_last_purchase: 5, churned: 0 },
      { customer_id: 2, total_orders: 8, total_spent: 1200, days_since_last_purchase: 45, churned: 0 },
      { customer_id: 3, total_orders: 3, total_spent: 300, days_since_last_purchase: 120, churned: 1 }
    ];
  };

  const generateMockInventoryData = () => {
    return [
      { item_name: 'Product A', current_stock: 50, min_stock_level: 100 },
      { item_name: 'Product B', current_stock: 25, min_stock_level: 30 },
      { item_name: 'Product C', current_stock: 200, min_stock_level: 150 }
    ];
  };

  const handlePredictSales = async () => {
    try {
      const response = await fetch('/api/ai/analytics/predict-sales', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': 'current-user'
        },
        body: JSON.stringify({
          features: {
            year: new Date().getFullYear(),
            month: new Date().getMonth() + 1,
            quarter: Math.floor(new Date().getMonth() / 3) + 1,
            day_of_week: new Date().getDay(),
            is_weekend: new Date().getDay() >= 5 ? 1 : 0,
            sales_lag_1: 8500,
            sales_lag_7: 8200,
            sales_lag_30: 7800,
            sales_ma_7: 8300,
            sales_ma_30: 8000
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        setPredictions(prev => [data.prediction, ...prev.slice(0, 9)]);
      }
    } catch (err) {
      console.error('Error predicting sales:', err);
    }
  };

  const handleChatSubmit = async () => {
    if (!currentMessage.trim()) return;

    const userMessage = {
      type: 'user',
      message: currentMessage,
      timestamp: new Date().toISOString()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');

    try {
      const response = await fetch('/api/ai/nlp/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': 'current-user'
        },
        body: JSON.stringify({
          message: currentMessage,
          context: {}
        })
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage = {
          type: 'ai',
          message: data.response.response,
          timestamp: new Date().toISOString()
        };
        setChatMessages(prev => [...prev, aiMessage]);
      }
    } catch (err) {
      console.error('Error in chat:', err);
    }
  };

  const handleCreateRule = async () => {
    try {
      const response = await fetch('/api/ai/automation/rules', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': 'current-user'
        },
        body: JSON.stringify(newRule)
      });

      if (response.ok) {
        setCreateRuleDialog(false);
        setNewRule({ name: '', description: '', trigger: 'event_based', conditions: [], actions: [] });
        loadDashboardData();
      }
    } catch (err) {
      console.error('Error creating rule:', err);
    }
  };

  const renderAnalyticsTab = () => (
    <Grid container spacing={3}>
      {/* AI Insights */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Insights sx={{ mr: 1, verticalAlign: 'middle' }} />
              AI-Powered Insights
            </Typography>
            {insights.map((insight, index) => (
              <Alert
                key={index}
                severity={insight.impact === 'high' ? 'warning' : 'info'}
                sx={{ mb: 2 }}
              >
                <Typography variant="subtitle2">{insight.title}</Typography>
                <Typography variant="body2">{insight.description}</Typography>
                {insight.recommendations.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Recommendations:
                    </Typography>
                    <List dense>
                      {insight.recommendations.map((rec, idx) => (
                        <ListItem key={idx} sx={{ py: 0 }}>
                          <ListItemIcon sx={{ minWidth: 20 }}>
                            <CheckCircle fontSize="small" color="success" />
                          </ListItemIcon>
                          <ListItemText primary={rec} />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
              </Alert>
            ))}
          </CardContent>
        </Card>
      </Grid>

      {/* Sales Predictions */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                <AutoGraph sx={{ mr: 1, verticalAlign: 'middle' }} />
                Sales Predictions
              </Typography>
              <Button
                variant="contained"
                size="small"
                onClick={handlePredictSales}
                startIcon={<PlayArrow />}
              >
                Predict
              </Button>
            </Box>
            {predictions.map((prediction, index) => (
              <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="h6" color="primary">
                  ${prediction.value.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Confidence: {(prediction.confidence * 100).toFixed(1)}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={prediction.confidence * 100}
                  sx={{ mt: 1 }}
                />
              </Box>
            ))}
          </CardContent>
        </Card>
      </Grid>

      {/* Model Performance */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Analytics sx={{ mr: 1, verticalAlign: 'middle' }} />
              Model Performance
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Sales Forecasting Model
              </Typography>
              <LinearProgress
                variant="determinate"
                value={85}
                sx={{ mt: 1 }}
              />
              <Typography variant="caption" color="text.secondary">
                85% Accuracy
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Customer Churn Model
              </Typography>
              <LinearProgress
                variant="determinate"
                value={92}
                sx={{ mt: 1 }}
              />
              <Typography variant="caption" color="text.secondary">
                92% Accuracy
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderAutomationTab = () => (
    <Grid container spacing={3}>
      {/* Automation Statistics */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Settings sx={{ mr: 1, verticalAlign: 'middle' }} />
              Automation Statistics
            </Typography>
            {automationStats && (
              <Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Total Rules</Typography>
                  <Typography variant="h6">{automationStats.total_rules}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Active Rules</Typography>
                  <Typography variant="h6" color="success.main">
                    {automationStats.active_rules}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Success Rate</Typography>
                  <Typography variant="h6" color="primary">
                    {automationStats.success_rate?.toFixed(1)}%
                  </Typography>
                </Box>
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Automation Rules */}
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                <AutoGraph sx={{ mr: 1, verticalAlign: 'middle' }} />
                Automation Rules
              </Typography>
              <Button
                variant="contained"
                onClick={() => setCreateRuleDialog(true)}
                startIcon={<Settings />}
              >
                Create Rule
              </Button>
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Trigger</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Executions</TableCell>
                    <TableCell>Success Rate</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {automationRules.map((rule) => (
                    <TableRow key={rule.id}>
                      <TableCell>{rule.name}</TableCell>
                      <TableCell>
                        <Chip label={rule.trigger} size="small" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={rule.status}
                          size="small"
                          color={rule.status === 'active' ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell>{rule.execution_count}</TableCell>
                      <TableCell>
                        {rule.execution_count > 0
                          ? ((rule.success_count / rule.execution_count) * 100).toFixed(1)
                          : 0}%
                      </TableCell>
                      <TableCell>
                        <IconButton size="small">
                          <PlayArrow />
                        </IconButton>
                        <IconButton size="small">
                          <Pause />
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
    </Grid>
  );

  const renderNLPTab = () => (
    <Grid container spacing={3}>
      {/* Chat Interface */}
      <Grid item xs={12} md={8}>
        <Card sx={{ height: 500 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Insights sx={{ mr: 1, verticalAlign: 'middle' }} />
              Chat with Your Data
            </Typography>
            <Box sx={{ height: 350, overflow: 'auto', mb: 2, p: 1, bgcolor: 'grey.50' }}>
              {chatMessages.map((message, index) => (
                <Box
                  key={index}
                  sx={{
                    mb: 2,
                    p: 2,
                    bgcolor: message.type === 'user' ? 'primary.light' : 'grey.200',
                    borderRadius: 1,
                    ml: message.type === 'user' ? 'auto' : 0,
                    mr: message.type === 'user' ? 0 : 'auto',
                    maxWidth: '80%'
                  }}
                >
                  <Typography variant="body2">{message.message}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </Typography>
                </Box>
              ))}
            </Box>
            <Box display="flex" gap={1}>
              <TextField
                fullWidth
                placeholder="Ask me anything about your data..."
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleChatSubmit()}
              />
              <Button
                variant="contained"
                onClick={handleChatSubmit}
                disabled={!currentMessage.trim()}
              >
                Send
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Voice Commands Help */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Insights sx={{ mr: 1, verticalAlign: 'middle' }} />
              Voice Commands
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Try these voice commands:
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText
                  primary="Show me sales data"
                  secondary="Query data"
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Create new customer"
                  secondary="Commands"
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Generate monthly report"
                  secondary="Reports"
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Analyze customer trends"
                  secondary="Analysis"
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
        AI-Powered Analytics Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Advanced AI analytics, intelligent automation, and natural language interface for your ERP system.
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Analytics" icon={<Analytics />} />
          <Tab label="Automation" icon={<Settings />} />
          <Tab label="Natural Language" icon={<Insights />} />
        </Tabs>
      </Box>

      {activeTab === 0 && renderAnalyticsTab()}
      {activeTab === 1 && renderAutomationTab()}
      {activeTab === 2 && renderNLPTab()}

      {/* Create Rule Dialog */}
      <Dialog open={createRuleDialog} onClose={() => setCreateRuleDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Automation Rule</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Rule Name"
            value={newRule.name}
            onChange={(e) => setNewRule(prev => ({ ...prev, name: e.target.value }))}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Description"
            value={newRule.description}
            onChange={(e) => setNewRule(prev => ({ ...prev, description: e.target.value }))}
            multiline
            rows={3}
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Trigger Type</InputLabel>
            <Select
              value={newRule.trigger}
              onChange={(e) => setNewRule(prev => ({ ...prev, trigger: e.target.value }))}
            >
              <MenuItem value="event_based">Event Based</MenuItem>
              <MenuItem value="scheduled">Scheduled</MenuItem>
              <MenuItem value="condition_based">Condition Based</MenuItem>
              <MenuItem value="manual">Manual</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateRuleDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateRule} variant="contained">Create Rule</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AIAnalyticsDashboard;
