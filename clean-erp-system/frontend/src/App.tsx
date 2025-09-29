// Modern ERP System - Main App Component
// Complete ERP system with modern UI/UX design

import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import ModernERPLayout from './components/layout/ModernERPLayout';
import ModernERPDashboard from './components/dashboard/ModernERPDashboard';
import ModernERPWidget from './components/common/ModernERPWidget';

// Import all modules
import CRMModule from './components/crm/CRMModule';
import FinanceModule from './components/finance/FinanceModule';
import DeskModule from './components/desk/DeskModule';
import PeopleModule from './components/people/PeopleModule';
import SupplyChainModule from './components/supply_chain/SupplyChainModule';
import ProjectManagementModule from './components/project_management/ProjectManagementModule';
import QualityManagementModule from './components/quality_management/QualityManagementModule';
import BusinessIntelligenceModule from './components/business_intelligence/BusinessIntelligenceModule';
import MarketingAutomationModule from './components/marketing_automation/MarketingAutomationModule';
import BookingModule from './components/booking/BookingModule';
import MomentsModule from './components/moments/MomentsModule';
import WorkflowEngine from './components/workflow/WorkflowEngine';
import CalendarSystem from './components/calendar/CalendarSystem';

// Import design system
import './styles/design-system.css';

interface AppProps {}

const App: React.FC<AppProps> = () => {
  const [currentModule, setCurrentModule] = useState('dashboard');
  const [userRole, setUserRole] = useState<'user' | 'admin' | 'super_admin'>('user');
  const [darkMode, setDarkMode] = useState(false);

  // Create theme based on design system
  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#4A90E2',
        light: '#7BB3F0',
        dark: '#3A7BC8',
        contrastText: '#FFFFFF'
      },
      secondary: {
        main: '#50E3C2',
        light: '#7BEDD1',
        dark: '#3BC4A8',
        contrastText: '#FFFFFF'
      },
      error: {
        main: '#E95E5E',
        light: '#F07A7A',
        dark: '#D44A4A',
        contrastText: '#FFFFFF'
      },
      warning: {
        main: '#FFB74D',
        light: '#FFC971',
        dark: '#FF9800',
        contrastText: '#FFFFFF'
      },
      info: {
        main: '#4A90E2',
        light: '#7BB3F0',
        dark: '#3A7BC8',
        contrastText: '#FFFFFF'
      },
      success: {
        main: '#50E3C2',
        light: '#7BEDD1',
        dark: '#3BC4A8',
        contrastText: '#FFFFFF'
      },
      background: {
        default: darkMode ? '#121212' : '#F9F9F9',
        paper: darkMode ? '#1E1E1E' : '#FFFFFF'
      },
      text: {
        primary: darkMode ? '#FFFFFF' : '#333333',
        secondary: darkMode ? '#B0B0B0' : '#555555'
      }
    },
    typography: {
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
      h1: {
        fontSize: '32px',
        fontWeight: 700,
        lineHeight: 1.2
      },
      h2: {
        fontSize: '24px',
        fontWeight: 600,
        lineHeight: 1.3
      },
      h3: {
        fontSize: '20px',
        fontWeight: 600,
        lineHeight: 1.4
      },
      h4: {
        fontSize: '18px',
        fontWeight: 600,
        lineHeight: 1.4
      },
      h5: {
        fontSize: '16px',
        fontWeight: 600,
        lineHeight: 1.4
      },
      h6: {
        fontSize: '14px',
        fontWeight: 600,
        lineHeight: 1.4
      },
      body1: {
        fontSize: '16px',
        lineHeight: 1.6
      },
      body2: {
        fontSize: '14px',
        lineHeight: 1.6
      },
      button: {
        fontSize: '14px',
        fontWeight: 500,
        textTransform: 'none'
      }
    },
    shape: {
      borderRadius: 8
    },
    shadows: [
      'none',
      '0 1px 2px rgba(0,0,0,0.05)',
      '0 2px 4px rgba(0,0,0,0.05)',
      '0 4px 8px rgba(0,0,0,0.1)',
      '0 8px 16px rgba(0,0,0,0.1)',
      '0 16px 32px rgba(0,0,0,0.1)',
      '0 32px 64px rgba(0,0,0,0.1)',
      '0 64px 128px rgba(0,0,0,0.1)',
      '0 128px 256px rgba(0,0,0,0.1)',
      '0 256px 512px rgba(0,0,0,0.1)',
      '0 512px 1024px rgba(0,0,0,0.1)',
      '0 1024px 2048px rgba(0,0,0,0.1)',
      '0 2048px 4096px rgba(0,0,0,0.1)',
      '0 4096px 8192px rgba(0,0,0,0.1)',
      '0 8192px 16384px rgba(0,0,0,0.1)',
      '0 16384px 32768px rgba(0,0,0,0.1)',
      '0 32768px 65536px rgba(0,0,0,0.1)',
      '0 65536px 131072px rgba(0,0,0,0.1)',
      '0 131072px 262144px rgba(0,0,0,0.1)',
      '0 262144px 524288px rgba(0,0,0,0.1)',
      '0 524288px 1048576px rgba(0,0,0,0.1)',
      '0 1048576px 2097152px rgba(0,0,0,0.1)',
      '0 2097152px 4194304px rgba(0,0,0,0.1)',
      '0 4194304px 8388608px rgba(0,0,0,0.1)',
      '0 8388608px 16777216px rgba(0,0,0,0.1)'
    ],
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: '8px',
            textTransform: 'none',
            fontWeight: 500,
            boxShadow: 'none',
            '&:hover': {
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              transform: 'translateY(-1px)'
            }
          }
        }
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
            border: '1px solid #E0E0E0',
            transition: 'all 250ms ease-in-out',
            '&:hover': {
              boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
              transform: 'translateY(-2px)'
            }
          }
        }
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              borderRadius: '8px',
              '& fieldset': {
                borderColor: '#E0E0E0'
              },
              '&:hover fieldset': {
                borderColor: '#4A90E2'
              },
              '&.Mui-focused fieldset': {
                borderColor: '#4A90E2',
                boxShadow: '0 0 0 3px rgba(74, 144, 226, 0.1)'
              }
            }
          }
        }
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: '6px',
            fontWeight: 500
          }
        }
      }
    }
  });

  const handleModuleChange = (module: string) => {
    setCurrentModule(module);
  };

  const handleDarkModeToggle = () => {
    setDarkMode(!darkMode);
  };

  const renderModule = () => {
    switch (currentModule) {
      case 'dashboard':
        return <ModernERPDashboard userRole={userRole} />;
      case 'crm':
        return <CRMModule userRole={userRole} onModuleChange={handleModuleChange} />;
      case 'finance':
        return <FinanceModule userRole={userRole} onModuleChange={handleModuleChange} />;
      case 'desk':
        return <DeskModule userRole={userRole} onModuleChange={handleModuleChange} />;
      case 'people':
        return <PeopleModule userRole={userRole} onModuleChange={handleModuleChange} />;
      case 'supply_chain':
        return <SupplyChainModule userRole={userRole} onModuleChange={handleModuleChange} />;
      case 'project_management':
        return <ProjectManagementModule userRole={userRole} onModuleChange={handleModuleChange} />;
      case 'quality_management':
        return <QualityManagementModule userRole={userRole} onModuleChange={handleModuleChange} />;
      case 'business_intelligence':
        return <BusinessIntelligenceModule userRole={userRole} onModuleChange={handleModuleChange} />;
      case 'marketing_automation':
        return <MarketingAutomationModule userRole={userRole} onModuleChange={handleModuleChange} />;
      case 'booking':
        return <BookingModule userRole={userRole} onModuleChange={handleModuleChange} />;
      case 'moments':
        return <MomentsModule userRole={userRole} onModuleChange={handleModuleChange} />;
      case 'workflow':
        return <WorkflowEngine userRole={userRole} onModuleChange={handleModuleChange} />;
      case 'calendar':
        return <CalendarSystem userRole={userRole} onModuleChange={handleModuleChange} />;
      default:
        return <ModernERPDashboard userRole={userRole} />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ModernERPLayout
        currentModule={currentModule}
        onModuleChange={handleModuleChange}
        userRole={userRole}
        darkMode={darkMode}
        onDarkModeToggle={handleDarkModeToggle}
      >
        {renderModule()}
      </ModernERPLayout>
    </ThemeProvider>
  );
};

export default App;