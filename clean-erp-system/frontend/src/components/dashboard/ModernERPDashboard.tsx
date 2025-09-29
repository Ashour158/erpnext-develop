// Modern ERP Dashboard Component
// Widget-based grid with KPI cards, charts, and data tables

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Chip,
  LinearProgress,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText as ListText,
  Divider,
  Button,
  Tooltip,
  Skeleton
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  People,
  Business,
  Assignment,
  Inventory,
  MoreVert,
  ArrowUpward,
  ArrowDownward,
  Refresh,
  Fullscreen,
  Download,
  Share,
  Star,
  StarBorder,
  CheckCircle,
  Warning,
  Error,
  Info,
  Schedule,
  LocalShipping,
  Store,
  Assessment,
  Timeline,
  Analytics
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts';

interface ModernERPDashboardProps {
  userRole?: 'user' | 'admin' | 'super_admin';
}

const ModernERPDashboard: React.FC<ModernERPDashboardProps> = ({ userRole = 'user' }) => {
  const [loading, setLoading] = useState(true);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedWidget, setSelectedWidget] = useState<string | null>(null);

  // Sample data for charts
  const salesData = [
    { name: 'Jan', value: 4000, target: 3500 },
    { name: 'Feb', value: 3000, target: 3500 },
    { name: 'Mar', value: 5000, target: 4000 },
    { name: 'Apr', value: 4500, target: 4000 },
    { name: 'May', value: 6000, target: 5000 },
    { name: 'Jun', value: 5500, target: 5000 }
  ];

  const revenueData = [
    { name: 'Q1', revenue: 120000, profit: 30000 },
    { name: 'Q2', revenue: 150000, profit: 45000 },
    { name: 'Q3', revenue: 180000, profit: 60000 },
    { name: 'Q4', revenue: 200000, profit: 75000 }
  ];

  const customerData = [
    { name: 'New', value: 45, color: '#4A90E2' },
    { name: 'Returning', value: 35, color: '#50E3C2' },
    { name: 'VIP', value: 20, color: '#E95E5E' }
  ];

  const recentOrders = [
    { id: 'ORD-001', customer: 'John Doe', amount: 1250, status: 'completed', date: '2024-01-15' },
    { id: 'ORD-002', customer: 'Jane Smith', amount: 850, status: 'processing', date: '2024-01-14' },
    { id: 'ORD-003', customer: 'Bob Johnson', amount: 2100, status: 'pending', date: '2024-01-13' },
    { id: 'ORD-004', customer: 'Alice Brown', amount: 675, status: 'completed', date: '2024-01-12' },
    { id: 'ORD-005', customer: 'Charlie Wilson', amount: 1425, status: 'shipped', date: '2024-01-11' }
  ];

  const recentActivities = [
    { id: 1, type: 'sale', message: 'New sale created', user: 'John Doe', time: '2 min ago', icon: <TrendingUp /> },
    { id: 2, type: 'customer', message: 'Customer updated profile', user: 'Jane Smith', time: '5 min ago', icon: <People /> },
    { id: 3, type: 'inventory', message: 'Stock level updated', user: 'System', time: '10 min ago', icon: <Inventory /> },
    { id: 4, type: 'order', message: 'Order shipped', user: 'Bob Johnson', time: '15 min ago', icon: <LocalShipping /> }
  ];

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => setLoading(false), 1500);
    return () => clearTimeout(timer);
  }, []);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, widgetId: string) => {
    setAnchorEl(event.currentTarget);
    setSelectedWidget(widgetId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedWidget(null);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#50E3C2';
      case 'processing':
        return '#4A90E2';
      case 'pending':
        return '#E95E5E';
      case 'shipped':
        return '#50E3C2';
      default:
        return '#555555';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle sx={{ color: '#50E3C2' }} />;
      case 'processing':
        return <Schedule sx={{ color: '#4A90E2' }} />;
      case 'pending':
        return <Warning sx={{ color: '#E95E5E' }} />;
      case 'shipped':
        return <LocalShipping sx={{ color: '#50E3C2' }} />;
      default:
        return <Info sx={{ color: '#555555' }} />;
    }
  };

  const KPICard = ({ title, value, change, trend, icon, color }: any) => (
    <Card
      sx={{
        background: 'linear-gradient(135deg, #FFFFFF 0%, #F9F9F9 100%)',
        border: '1px solid #E0E0E0',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
        transition: 'all 250ms ease-in-out',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 4px 16px rgba(0,0,0,0.1)'
        }
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="body2" sx={{ color: '#555555', fontWeight: 500 }}>
            {title}
          </Typography>
          <IconButton size="small" sx={{ color: color }}>
            {icon}
          </IconButton>
        </Box>
        <Typography variant="h4" sx={{ color: '#333333', fontWeight: 700, mb: 1 }}>
          {value}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {trend === 'up' ? (
            <ArrowUpward sx={{ color: '#50E3C2', fontSize: 16 }} />
          ) : (
            <ArrowDownward sx={{ color: '#E95E5E', fontSize: 16 }} />
          )}
          <Typography
            variant="body2"
            sx={{
              color: trend === 'up' ? '#50E3C2' : '#E95E5E',
              fontWeight: 600
            }}
          >
            {change}
          </Typography>
          <Typography variant="body2" sx={{ color: '#555555' }}>
            vs last month
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );

  const ChartCard = ({ title, children, actions }: any) => (
    <Card
      sx={{
        background: '#FFFFFF',
        border: '1px solid #E0E0E0',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
        transition: 'all 250ms ease-in-out',
        '&:hover': {
          boxShadow: '0 4px 16px rgba(0,0,0,0.1)'
        }
      }}
    >
      <CardContent sx={{ p: 0 }}>
        <Box
          sx={{
            p: 3,
            borderBottom: '1px solid #E0E0E0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <Typography variant="h6" sx={{ color: '#333333', fontWeight: 600 }}>
            {title}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {actions}
          </Box>
        </Box>
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      </CardContent>
    </Card>
  );

  const DataTableCard = ({ title, data, columns, actions }: any) => (
    <Card
      sx={{
        background: '#FFFFFF',
        border: '1px solid #E0E0E0',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
        transition: 'all 250ms ease-in-out',
        '&:hover': {
          boxShadow: '0 4px 16px rgba(0,0,0,0.1)'
        }
      }}
    >
      <CardContent sx={{ p: 0 }}>
        <Box
          sx={{
            p: 3,
            borderBottom: '1px solid #E0E0E0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <Typography variant="h6" sx={{ color: '#333333', fontWeight: 600 }}>
            {title}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {actions}
          </Box>
        </Box>
        <Box sx={{ p: 0 }}>
          {data.map((item: any, index: number) => (
            <Box
              key={index}
              sx={{
                p: 3,
                borderBottom: index < data.length - 1 ? '1px solid #E0E0E0' : 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                transition: 'all 150ms ease-in-out',
                '&:hover': {
                  backgroundColor: 'rgba(74, 144, 226, 0.05)'
                }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: '#4A90E2', width: 32, height: 32 }}>
                  {item.customer.charAt(0)}
                </Avatar>
                <Box>
                  <Typography variant="body1" sx={{ color: '#333333', fontWeight: 500 }}>
                    {item.customer}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#555555' }}>
                    {item.id} • {item.date}
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="h6" sx={{ color: '#333333', fontWeight: 600 }}>
                  ${item.amount.toLocaleString()}
                </Typography>
                <Chip
                  label={item.status}
                  size="small"
                  sx={{
                    backgroundColor: getStatusColor(item.status),
                    color: 'white',
                    fontWeight: 500
                  }}
                />
              </Box>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box>
        <Grid container spacing={3}>
          {[...Array(8)].map((_, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card sx={{ p: 3 }}>
                <Skeleton variant="text" width="60%" height={20} />
                <Skeleton variant="text" width="40%" height={40} />
                <Skeleton variant="text" width="80%" height={20} />
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box>
      {/* Welcome Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ color: '#333333', fontWeight: 700, mb: 1 }}>
          Welcome back! 👋
        </Typography>
        <Typography variant="body1" sx={{ color: '#555555' }}>
          Here's what's happening with your business today.
        </Typography>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Total Revenue"
            value="$125,430"
            change="+12.5%"
            trend="up"
            icon={<TrendingUp />}
            color="#4A90E2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="New Customers"
            value="1,234"
            change="+8.2%"
            trend="up"
            icon={<People />}
            color="#50E3C2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Active Orders"
            value="89"
            change="-2.1%"
            trend="down"
            icon={<Assignment />}
            color="#E95E5E"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Inventory Value"
            value="$45,670"
            change="+5.3%"
            trend="up"
            icon={<Inventory />}
            color="#4A90E2"
          />
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={8}>
          <ChartCard
            title="Sales Trend"
            actions={[
              <IconButton key="refresh" size="small">
                <Refresh />
              </IconButton>,
              <IconButton key="fullscreen" size="small">
                <Fullscreen />
              </IconButton>,
              <IconButton key="more" size="small">
                <MoreVert />
              </IconButton>
            ]}
          >
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={salesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E0E0E0" />
                <XAxis dataKey="name" stroke="#555555" />
                <YAxis stroke="#555555" />
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    border: '1px solid #E0E0E0',
                    borderRadius: '8px',
                    boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#4A90E2"
                  fill="rgba(74, 144, 226, 0.1)"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="target"
                  stroke="#50E3C2"
                  fill="rgba(80, 227, 194, 0.1)"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                />
              </AreaChart>
            </ResponsiveContainer>
          </ChartCard>
        </Grid>
        <Grid item xs={12} lg={4}>
          <ChartCard
            title="Customer Distribution"
            actions={[
              <IconButton key="refresh" size="small">
                <Refresh />
              </IconButton>
            ]}
          >
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={customerData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  dataKey="value"
                >
                  {customerData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    border: '1px solid #E0E0E0',
                    borderRadius: '8px',
                    boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        </Grid>
      </Grid>

      {/* Data Tables Row */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <DataTableCard
            title="Recent Orders"
            data={recentOrders}
            actions={[
              <Button key="view-all" size="small" sx={{ color: '#4A90E2' }}>
                View All
              </Button>
            ]}
          />
        </Grid>
        <Grid item xs={12} lg={4}>
          <Card
            sx={{
              background: '#FFFFFF',
              border: '1px solid #E0E0E0',
              borderRadius: '12px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
              height: '100%'
            }}
          >
            <CardContent sx={{ p: 0 }}>
              <Box
                sx={{
                  p: 3,
                  borderBottom: '1px solid #E0E0E0',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}
              >
                <Typography variant="h6" sx={{ color: '#333333', fontWeight: 600 }}>
                  Recent Activity
                </Typography>
                <IconButton size="small">
                  <Refresh />
                </IconButton>
              </Box>
              <List sx={{ p: 0 }}>
                {recentActivities.map((activity, index) => (
                  <ListItem
                    key={activity.id}
                    sx={{
                      py: 2,
                      borderBottom: index < recentActivities.length - 1 ? '1px solid #E0E0E0' : 'none'
                    }}
                  >
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'rgba(74, 144, 226, 0.1)', color: '#4A90E2' }}>
                        {activity.icon}
                      </Avatar>
                    </ListItemAvatar>
                    <ListText
                      primary={activity.message}
                      secondary={`${activity.user} • ${activity.time}`}
                      primaryTypographyProps={{
                        fontSize: '14px',
                        fontWeight: 500,
                        color: '#333333'
                      }}
                      secondaryTypographyProps={{
                        fontSize: '12px',
                        color: '#555555'
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ModernERPDashboard;
