import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface DashboardLayoutProps {
  children: React.ReactNode;
  isAdmin?: boolean;
}

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  '/dashboard': { title: 'Dashboard', subtitle: 'Welcome back, John!' },
  '/attendance': { title: 'Attendance', subtitle: 'Track your attendance records' },
  '/leave': { title: 'Leave Management', subtitle: 'Manage your leaves & OD' },
  '/payslip': { title: 'Payslip', subtitle: 'View your salary details' },
  '/profile': { title: 'Profile', subtitle: 'Manage your personal information' },
  '/reports': { title: 'Reports', subtitle: 'Analytics & insights' },
  '/admin': { title: 'Admin Dashboard', subtitle: 'System overview' },
  '/admin/employees': { title: 'Employee Management', subtitle: 'Manage all employees' },
  '/admin/payroll': { title: 'Payroll', subtitle: 'Process payroll' },
  '/admin/branches': { title: 'Branch Management', subtitle: 'Manage branches' },
  '/admin/attendance': { title: 'Attendance Monitor', subtitle: 'Monitor all attendance' },
  '/admin/approvals': { title: 'Approvals', subtitle: 'Pending approvals' },
  '/admin/settings': { title: 'Settings', subtitle: 'System configuration' },
};

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  isAdmin = false,
}) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 1024;
      setIsMobile(mobile);
      if (mobile) setSidebarCollapsed(true);
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const pageConfig = pageTitles[location.pathname] || { title: 'Dashboard', subtitle: '' };

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Subtle Background Pattern */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-primary-100/30 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-primary-50/50 rounded-full blur-3xl" />
      </div>

      <Sidebar
        isCollapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        isAdmin={isAdmin}
      />

      <motion.main
        className="relative min-h-screen transition-all duration-200"
        animate={{
          marginLeft: isMobile ? 0 : sidebarCollapsed ? 80 : 260,
        }}
      >
        <Header
          title={pageConfig.title}
          subtitle={pageConfig.subtitle}
          onMenuClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        <motion.div
          className="p-4 lg:p-6"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {children}
        </motion.div>
      </motion.main>
    </div>
  );
};

export default DashboardLayout;
