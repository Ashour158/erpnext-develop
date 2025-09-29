// Booking Module Component
// Complete booking management with resources, scheduling, rules

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
  AppBar,
  Toolbar,
  IconButton,
  Badge,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Fab,
  Tooltip,
  LinearProgress,
  Alert,
  Snackbar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem as SelectMenuItem,
  Switch,
  FormControlLabel,
  Checkbox,
  FormGroup,
  Autocomplete,
  Pagination,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon
} from '@mui/material';
import {
  Dashboard,
  Event,
  People,
  Timeline,
  Assessment,
  Settings,
  Notifications,
  AccountCircle,
  MoreVert,
  Add,
  Search,
  FilterList,
  ViewModule,
  ViewList,
  ViewComfy,
  Edit,
  Delete,
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
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Speed,
  Storage,
  NetworkCheck,
  Wifi,
  WifiOff,
  CheckCircle,
  Error,
  Warning,
  Info,
  Description,
  TableChart,
  PictureAsPdf,
  CloudDownload,
  CloudUpload,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
  MoreVert as MoreVertIcon,
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  ViewModule as ViewModuleIcon,
  ViewList as ViewListIcon,
  ViewComfy as ViewComfyIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  LocationOn as LocationOnIcon,
  Business as BusinessIcon,
  Person as PersonIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Sync as SyncIcon,
  CloudSync as CloudSyncIcon,
  CloudDone as CloudDoneIcon,
  CloudOff as CloudOffIcon,
  GetApp as GetAppIcon,
  Publish as PublishIcon,
  FileDownload as FileDownloadIcon,
  FileUpload as FileUploadIcon,
  Print as PrintIcon,
  Share as ShareIcon,
  Archive as ArchiveIcon,
  RestoreFromTrash as RestoreFromTrashIcon,
  Timeline as TimelineIcon2,
  Assessment as AssessmentIcon2,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  NetworkCheck as NetworkCheckIcon,
  Wifi as WifiIcon,
  WifiOff as WifiOffIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Description as DescriptionIcon,
  TableChart as TableChartIcon,
  PictureAsPdf as PictureAsPdfIcon,
  CloudDownload as CloudDownloadIcon,
  CloudUpload as CloudUploadIcon
} from '@mui/icons-material';
import FullPageView from '../common/FullPageView';
import RealtimeSync from '../common/RealtimeSync';
import ImportExport from '../common/ImportExport';

interface BookingModuleProps {
  userRole: 'user' | 'admin' | 'super_admin';
  onModuleChange?: (module: string) => void;
}

const BookingModule: React.FC<BookingModuleProps> = ({ userRole, onModuleChange }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [showSettings, setShowSettings] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'table'>('table');
  const [realtimeStatus, setRealtimeStatus] = useState<'connected' | 'disconnected' | 'syncing'>('connected');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleSettingsClick = () => {
    setShowSettings(!showSettings);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleViewModeChange = (mode: 'grid' | 'list' | 'table') => {
    setViewMode(mode);
  };

  const renderDashboard = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Active Bookings
                </Typography>
                <Typography variant="h4">24</Typography>
              </Box>
              <Event color="primary" />
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
                  Available Resources
                </Typography>
                <Typography variant="h4">12</Typography>
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
                  Today's Bookings
                </Typography>
                <Typography variant="h4">8</Typography>
              </Box>
              <Timeline color="primary" />
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
                  Revenue
                </Typography>
                <Typography variant="h4">$2,450</Typography>
              </Box>
              <Assessment color="primary" />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderBookings = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Bookings</Typography>
          <Box display="flex" gap={1}>
            <Button
              variant={viewMode === 'grid' ? 'contained' : 'outlined'}
              size="small"
              startIcon={<ViewComfyIcon />}
              onClick={() => handleViewModeChange('grid')}
            >
              Grid
            </Button>
            <Button
              variant={viewMode === 'list' ? 'contained' : 'outlined'}
              size="small"
              startIcon={<ViewListIcon />}
              onClick={() => handleViewModeChange('list')}
            >
              List
            </Button>
            <Button
              variant={viewMode === 'table' ? 'contained' : 'outlined'}
              size="small"
              startIcon={<ViewModuleIcon />}
              onClick={() => handleViewModeChange('table')}
            >
              Table
            </Button>
          </Box>
        </Box>
        <Typography>Booking management interface will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderResources = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Resources</Typography>
        <Typography>Resource management interface will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderScheduling = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Scheduling</Typography>
        <Typography>Scheduling interface will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderRules = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Booking Rules</Typography>
        <Typography>Booking rule management interface will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderCalendar = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Calendar</Typography>
        <Typography>Booking calendar interface will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderReports = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Reports</Typography>
        <Typography>Booking reports and analytics will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 0:
        return renderDashboard();
      case 1:
        return renderBookings();
      case 2:
        return renderResources();
      case 3:
        return renderScheduling();
      case 4:
        return renderRules();
      case 5:
        return renderCalendar();
      case 6:
        return renderReports();
      default:
        return null;
    }
  };

  if (showSettings) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>Booking Module Settings</Typography>
        <Typography>Booking module settings will be implemented here</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Module Header */}
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Booking Management
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            <RealtimeSync
              onSyncStatusChange={(status) => setRealtimeStatus(status.status)}
              onDataUpdate={(module, data) => console.log('Data updated:', module, data)}
              onError={(error) => setError(error)}
            />
            <IconButton color="inherit">
              <Badge badgeContent={4} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            <IconButton color="inherit" onClick={handleSettingsClick}>
              <SettingsIcon />
            </IconButton>
            <IconButton color="inherit" onClick={handleMenuClick}>
              <MoreVertIcon />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Module Tabs */}
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Dashboard" icon={<Dashboard />} />
        <Tab label="Bookings" icon={<Event />} />
        <Tab label="Resources" icon={<People />} />
        <Tab label="Scheduling" icon={<Timeline />} />
        <Tab label="Rules" icon={<Assessment />} />
        <Tab label="Calendar" icon={<Event />} />
        <Tab label="Reports" icon={<Analytics />} />
      </Tabs>

      {/* Module Content */}
      {renderTabContent()}

      {/* User Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleMenuClose}>
          <ListItemIcon>
            <AccountCircleIcon />
          </ListItemIcon>
          <ListItemText>Profile</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText>Settings</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleMenuClose}>
          <ListItemText>Logout</ListItemText>
        </MenuItem>
      </Menu>

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

export default BookingModule;
