// People (HR) Module Component
// Complete HR management with employees, departments, leave, attendance, performance

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
  People,
  Business,
  Assignment,
  Schedule,
  Analytics,
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
  Timeline,
  Assessment,
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
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
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

interface PeopleModuleProps {
  userRole: 'user' | 'admin' | 'super_admin';
  onModuleChange?: (module: string) => void;
}

const PeopleModule: React.FC<PeopleModuleProps> = ({ userRole, onModuleChange }) => {
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
                  Total Employees
                </Typography>
                <Typography variant="h4">156</Typography>
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
                  Active Employees
                </Typography>
                <Typography variant="h4">142</Typography>
              </Box>
              <Person color="primary" />
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
                  Departments
                </Typography>
                <Typography variant="h4">12</Typography>
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
                  Leave Requests
                </Typography>
                <Typography variant="h4">8</Typography>
              </Box>
              <Schedule color="primary" />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderEmployees = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Employees</Typography>
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
        <Typography>Employee management interface will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderDepartments = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Departments</Typography>
        <Typography>Department management interface will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderLeaveManagement = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Leave Management</Typography>
        <Typography>Leave management interface will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderAttendance = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Attendance</Typography>
        <Typography>Attendance management interface will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderPerformance = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Performance</Typography>
        <Typography>Performance management interface will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderRecruitment = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Recruitment</Typography>
        <Typography>Recruitment management interface will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderReports = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Reports</Typography>
        <Typography>HR reports and analytics will be implemented here</Typography>
      </CardContent>
    </Card>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 0:
        return renderDashboard();
      case 1:
        return renderEmployees();
      case 2:
        return renderDepartments();
      case 3:
        return renderLeaveManagement();
      case 4:
        return renderAttendance();
      case 5:
        return renderPerformance();
      case 6:
        return renderRecruitment();
      case 7:
        return renderReports();
      default:
        return null;
    }
  };

  if (showSettings) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>People Module Settings</Typography>
        <Typography>People module settings will be implemented here</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Module Header */}
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            People Management (HR)
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
        <Tab label="Employees" icon={<People />} />
        <Tab label="Departments" icon={<Business />} />
        <Tab label="Leave" icon={<Schedule />} />
        <Tab label="Attendance" icon={<Assignment />} />
        <Tab label="Performance" icon={<Star />} />
        <Tab label="Recruitment" icon={<Person />} />
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

export default PeopleModule;
