import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import Footer from './Footer';
import LoadingSpinner from '../common/LoadingSpinner';
import ToastContainer from '../common/ToastContainer';

// Import all module components
import Dashboard from '../dashboard/Dashboard';
import CRM from '../crm/CRM';
import Finance from '../finance/Finance';
import People from '../people/People';
import Moments from '../moments/Moments';
import Booking from '../booking/Booking';
import Maintenance from '../maintenance/Maintenance';
import SupplyChain from '../supply-chain/SupplyChain';

// Import module-specific pages
import Customer360 from '../crm/pages/Customer360';
import OpportunityManagement from '../crm/pages/OpportunityManagement';
import LeadManagement from '../crm/pages/LeadManagement';
import ContactManagement from '../crm/pages/ContactManagement';
import QuotationManagement from '../crm/pages/QuotationManagement';
import Forecasting from '../crm/pages/Forecasting';

import FinancialStatements from '../finance/pages/FinancialStatements';
import MultiCurrency from '../finance/pages/MultiCurrency';
import Invoicing from '../finance/pages/Invoicing';
import JournalEntries from '../finance/pages/JournalEntries';

import EmployeeManagement from '../people/pages/EmployeeManagement';
import LeaveManagement from '../people/pages/LeaveManagement';
import KPIManagement from '../people/pages/KPIManagement';
import AttendanceManagement from '../people/pages/AttendanceManagement';

import MomentsFeed from '../moments/pages/MomentsFeed';
import SocialPosts from '../moments/pages/SocialPosts';
import MediaGallery from '../moments/pages/MediaGallery';

import BookingCalendar from '../booking/pages/BookingCalendar';
import MeetingRequests from '../booking/pages/MeetingRequests';
import ResourceBooking from '../booking/pages/ResourceBooking';

import MaintenanceTickets from '../maintenance/pages/MaintenanceTickets';
import AssetManagement from '../maintenance/pages/AssetManagement';
import PreventiveMaintenance from '../maintenance/pages/PreventiveMaintenance';

import InventoryManagement from '../supply-chain/pages/InventoryManagement';
import PurchaseOrders from '../supply-chain/pages/PurchaseOrders';
import SupplierManagement from '../supply-chain/pages/SupplierManagement';

const MainLayout: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [currentModule, setCurrentModule] = useState<string>('dashboard');

  useEffect(() => {
    // Simulate loading time
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const handleModuleChange = (module: string) => {
    setCurrentModule(module);
    // Store current module in localStorage for persistence
    localStorage.setItem('currentModule', module);
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <Router>
      <div className="min-h-screen bg-neutral-50 flex">
        {/* Sidebar */}
        <Sidebar 
          collapsed={sidebarCollapsed}
          currentModule={currentModule}
          onModuleChange={handleModuleChange}
        />

        {/* Main Content Area */}
        <div className={`flex-1 flex flex-col transition-all duration-300 ${
          sidebarCollapsed ? 'ml-16' : 'ml-64'
        }`}>
          {/* Header */}
          <Header 
            onToggleSidebar={toggleSidebar}
            currentModule={currentModule}
          />

          {/* Main Content */}
          <main className="flex-1 p-6 overflow-auto">
            <Routes>
              {/* Dashboard Routes */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />

              {/* CRM Routes */}
              <Route path="/crm" element={<CRM />} />
              <Route path="/crm/customer-360/:id" element={<Customer360 />} />
              <Route path="/crm/opportunities" element={<OpportunityManagement />} />
              <Route path="/crm/leads" element={<LeadManagement />} />
              <Route path="/crm/contacts" element={<ContactManagement />} />
              <Route path="/crm/quotations" element={<QuotationManagement />} />
              <Route path="/crm/forecasting" element={<Forecasting />} />

              {/* Finance Routes */}
              <Route path="/finance" element={<Finance />} />
              <Route path="/finance/statements" element={<FinancialStatements />} />
              <Route path="/finance/multi-currency" element={<MultiCurrency />} />
              <Route path="/finance/invoicing" element={<Invoicing />} />
              <Route path="/finance/journals" element={<JournalEntries />} />

              {/* People Routes */}
              <Route path="/people" element={<People />} />
              <Route path="/people/employees" element={<EmployeeManagement />} />
              <Route path="/people/leave" element={<LeaveManagement />} />
              <Route path="/people/kpi" element={<KPIManagement />} />
              <Route path="/people/attendance" element={<AttendanceManagement />} />

              {/* Moments Routes */}
              <Route path="/moments" element={<Moments />} />
              <Route path="/moments/feed" element={<MomentsFeed />} />
              <Route path="/moments/posts" element={<SocialPosts />} />
              <Route path="/moments/gallery" element={<MediaGallery />} />

              {/* Booking Routes */}
              <Route path="/booking" element={<Booking />} />
              <Route path="/booking/calendar" element={<BookingCalendar />} />
              <Route path="/booking/meetings" element={<MeetingRequests />} />
              <Route path="/booking/resources" element={<ResourceBooking />} />

              {/* Maintenance Routes */}
              <Route path="/maintenance" element={<Maintenance />} />
              <Route path="/maintenance/tickets" element={<MaintenanceTickets />} />
              <Route path="/maintenance/assets" element={<AssetManagement />} />
              <Route path="/maintenance/preventive" element={<PreventiveMaintenance />} />

              {/* Supply Chain Routes */}
              <Route path="/supply-chain" element={<SupplyChain />} />
              <Route path="/supply-chain/inventory" element={<InventoryManagement />} />
              <Route path="/supply-chain/purchase-orders" element={<PurchaseOrders />} />
              <Route path="/supply-chain/suppliers" element={<SupplierManagement />} />

              {/* 404 Route */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </main>

          {/* Footer */}
          <Footer />
        </div>

        {/* Toast Container */}
        <ToastContainer />
      </div>
    </Router>
  );
};

export default MainLayout;
