// Modern ERP Widget Component
// Reusable widget component with drag, resize, and customization

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Switch,
  FormControlLabel,
  Chip,
  Avatar,
  LinearProgress,
  Skeleton
} from '@mui/material';
import {
  MoreVert,
  Refresh,
  Fullscreen,
  Download,
  Share,
  Settings,
  Star,
  StarBorder,
  Close,
  DragIndicator,
  Resize,
  Visibility,
  VisibilityOff
} from '@mui/icons-material';

interface ModernERPWidgetProps {
  id: string;
  title: string;
  children: React.ReactNode;
  loading?: boolean;
  error?: string;
  onRefresh?: () => void;
  onFullscreen?: () => void;
  onDownload?: () => void;
  onShare?: () => void;
  onSettings?: () => void;
  onClose?: () => void;
  draggable?: boolean;
  resizable?: boolean;
  customizable?: boolean;
  starred?: boolean;
  onStarToggle?: () => void;
  size?: 'small' | 'medium' | 'large';
  type?: 'kpi' | 'chart' | 'table' | 'list' | 'custom';
  className?: string;
}

const ModernERPWidget: React.FC<ModernERPWidgetProps> = ({
  id,
  title,
  children,
  loading = false,
  error,
  onRefresh,
  onFullscreen,
  onDownload,
  onShare,
  onSettings,
  onClose,
  draggable = false,
  resizable = false,
  customizable = false,
  starred = false,
  onStarToggle,
  size = 'medium',
  type = 'custom',
  className
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return { minHeight: 200 };
      case 'medium':
        return { minHeight: 300 };
      case 'large':
        return { minHeight: 400 };
      default:
        return { minHeight: 300 };
    }
  };

  const getTypeStyles = () => {
    switch (type) {
      case 'kpi':
        return {
          background: 'linear-gradient(135deg, #FFFFFF 0%, #F9F9F9 100%)',
          border: '1px solid #E0E0E0'
        };
      case 'chart':
        return {
          background: '#FFFFFF',
          border: '1px solid #E0E0E0'
        };
      case 'table':
        return {
          background: '#FFFFFF',
          border: '1px solid #E0E0E0'
        };
      case 'list':
        return {
          background: '#FFFFFF',
          border: '1px solid #E0E0E0'
        };
      default:
        return {
          background: '#FFFFFF',
          border: '1px solid #E0E0E0'
        };
    }
  };

  return (
    <Card
      className={className}
      sx={{
        ...getTypeStyles(),
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
        transition: 'all 250ms ease-in-out',
        cursor: draggable ? 'move' : 'default',
        position: 'relative',
        overflow: 'hidden',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
          '& .widget-actions': {
            opacity: 1
          }
        },
        ...getSizeStyles()
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Widget Header */}
      <Box
        sx={{
          p: 2,
          borderBottom: '1px solid #E0E0E0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'rgba(249, 249, 249, 0.5)'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {draggable && (
            <DragIndicator sx={{ color: '#555555', fontSize: 16 }} />
          )}
          <Typography
            variant="h6"
            sx={{
              color: '#333333',
              fontWeight: 600,
              fontSize: '16px'
            }}
          >
            {title}
          </Typography>
          {starred && (
            <Star sx={{ color: '#FFD700', fontSize: 16 }} />
          )}
        </Box>

        {/* Widget Actions */}
        <Box
          className="widget-actions"
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.5,
            opacity: isHovered ? 1 : 0,
            transition: 'opacity 150ms ease-in-out'
          }}
        >
          {onStarToggle && (
            <Tooltip title={starred ? 'Remove from favorites' : 'Add to favorites'}>
              <IconButton
                size="small"
                onClick={onStarToggle}
                sx={{
                  color: starred ? '#FFD700' : '#555555',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 215, 0, 0.1)'
                  }
                }}
              >
                {starred ? <Star /> : <StarBorder />}
              </IconButton>
            </Tooltip>
          )}

          {onRefresh && (
            <Tooltip title="Refresh">
              <IconButton
                size="small"
                onClick={onRefresh}
                sx={{
                  color: '#555555',
                  '&:hover': {
                    backgroundColor: 'rgba(74, 144, 226, 0.1)',
                    color: '#4A90E2'
                  }
                }}
              >
                <Refresh />
              </IconButton>
            </Tooltip>
          )}

          {onFullscreen && (
            <Tooltip title="Fullscreen">
              <IconButton
                size="small"
                onClick={onFullscreen}
                sx={{
                  color: '#555555',
                  '&:hover': {
                    backgroundColor: 'rgba(74, 144, 226, 0.1)',
                    color: '#4A90E2'
                  }
                }}
              >
                <Fullscreen />
              </IconButton>
            </Tooltip>
          )}

          {onDownload && (
            <Tooltip title="Download">
              <IconButton
                size="small"
                onClick={onDownload}
                sx={{
                  color: '#555555',
                  '&:hover': {
                    backgroundColor: 'rgba(74, 144, 226, 0.1)',
                    color: '#4A90E2'
                  }
                }}
              >
                <Download />
              </IconButton>
            </Tooltip>
          )}

          {onShare && (
            <Tooltip title="Share">
              <IconButton
                size="small"
                onClick={onShare}
                sx={{
                  color: '#555555',
                  '&:hover': {
                    backgroundColor: 'rgba(74, 144, 226, 0.1)',
                    color: '#4A90E2'
                  }
                }}
              >
                <Share />
              </IconButton>
            </Tooltip>
          )}

          {customizable && (
            <Tooltip title="Settings">
              <IconButton
                size="small"
                onClick={onSettings}
                sx={{
                  color: '#555555',
                  '&:hover': {
                    backgroundColor: 'rgba(74, 144, 226, 0.1)',
                    color: '#4A90E2'
                  }
                }}
              >
                <Settings />
              </IconButton>
            </Tooltip>
          )}

          <Tooltip title="More options">
            <IconButton
              size="small"
              onClick={handleMenuClick}
              sx={{
                color: '#555555',
                '&:hover': {
                  backgroundColor: 'rgba(74, 144, 226, 0.1)',
                  color: '#4A90E2'
                }
              }}
            >
              <MoreVert />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Widget Content */}
      <CardContent sx={{ p: 0, height: 'calc(100% - 60px)' }}>
        {loading ? (
          <Box sx={{ p: 3 }}>
            <Skeleton variant="text" width="60%" height={20} sx={{ mb: 2 }} />
            <Skeleton variant="text" width="40%" height={40} sx={{ mb: 2 }} />
            <Skeleton variant="text" width="80%" height={20} />
          </Box>
        ) : error ? (
          <Box
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              textAlign: 'center'
            }}
          >
            <Error sx={{ color: '#E95E5E', fontSize: 48, mb: 2 }} />
            <Typography variant="body1" sx={{ color: '#E95E5E', mb: 1 }}>
              Something went wrong
            </Typography>
            <Typography variant="body2" sx={{ color: '#555555' }}>
              {error}
            </Typography>
            {onRefresh && (
              <IconButton
                onClick={onRefresh}
                sx={{
                  mt: 2,
                  color: '#4A90E2',
                  '&:hover': {
                    backgroundColor: 'rgba(74, 144, 226, 0.1)'
                  }
                }}
              >
                <Refresh />
              </IconButton>
            )}
          </Box>
        ) : (
          <Box sx={{ height: '100%', overflow: 'auto' }}>
            {children}
          </Box>
        )}
      </CardContent>

      {/* Resize Handle */}
      {resizable && (
        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            right: 0,
            width: 20,
            height: 20,
            cursor: 'nw-resize',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            opacity: isHovered ? 1 : 0,
            transition: 'opacity 150ms ease-in-out'
          }}
        >
          <Resize sx={{ color: '#555555', fontSize: 16 }} />
        </Box>
      )}

      {/* More Options Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        PaperProps={{
          sx: {
            mt: 1,
            minWidth: 200,
            borderRadius: '8px',
            boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
            border: '1px solid #E0E0E0'
          }
        }}
      >
        {onRefresh && (
          <MenuItem onClick={() => { onRefresh(); handleMenuClose(); }}>
            <ListItemIcon>
              <Refresh />
            </ListItemIcon>
            <ListItemText>Refresh</ListItemText>
          </MenuItem>
        )}
        {onFullscreen && (
          <MenuItem onClick={() => { onFullscreen(); handleMenuClose(); }}>
            <ListItemIcon>
              <Fullscreen />
            </ListItemIcon>
            <ListItemText>Fullscreen</ListItemText>
          </MenuItem>
        )}
        {onDownload && (
          <MenuItem onClick={() => { onDownload(); handleMenuClose(); }}>
            <ListItemIcon>
              <Download />
            </ListItemIcon>
            <ListItemText>Download</ListItemText>
          </MenuItem>
        )}
        {onShare && (
          <MenuItem onClick={() => { onShare(); handleMenuClose(); }}>
            <ListItemIcon>
              <Share />
            </ListItemIcon>
            <ListItemText>Share</ListItemText>
          </MenuItem>
        )}
        {customizable && onSettings && (
          <MenuItem onClick={() => { onSettings(); handleMenuClose(); }}>
            <ListItemIcon>
              <Settings />
            </ListItemIcon>
            <ListItemText>Settings</ListItemText>
          </MenuItem>
        )}
        {onClose && (
          <MenuItem
            onClick={() => { onClose(); handleMenuClose(); }}
            sx={{ color: '#E95E5E' }}
          >
            <ListItemIcon>
              <Close />
            </ListItemIcon>
            <ListItemText>Remove Widget</ListItemText>
          </MenuItem>
        )}
      </Menu>
    </Card>
  );
};

export default ModernERPWidget;
