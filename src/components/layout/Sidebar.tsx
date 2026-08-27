import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Calendar,
  FileText,
  Receipt,
  User,
  Users,
  Building2,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Shield,
  RefreshCw,
} from 'lucide-react';

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
  isAdmin?: boolean;
}

interface NavItem {
  path: string;
  label: string;
  icon: React.ElementType;
  adminOnly?: boolean;
  requiredPermission?: string;
}

const employeeNavItems: NavItem[] = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/attendance', label: 'Attendance', icon: Calendar },
  { path: '/leave', label: 'Leave Management', icon: FileText },
  { path: '/payslip', label: 'Payslip', icon: Receipt },
  { path: '/reimbursements', label: 'Reimbursements & Claims', icon: Receipt },
  { path: '/profile', label: 'Profile', icon: User },
];

const adminNavItems: NavItem[] = [
  { path: '/admin', label: 'Admin Dashboard', icon: Shield }, // Always visible if they can access admin
  { path: '/admin/employees', label: 'Employees', icon: Users, adminOnly: true, requiredPermission: 'employee.read' },
  { path: '/admin/payroll/control', label: 'Payroll Control', icon: Receipt, adminOnly: true, requiredPermission: 'payroll.read' },
  { path: '/admin/payroll/cycles', label: 'Payroll Cycles', icon: RefreshCw, adminOnly: true, requiredPermission: 'payroll.cycle.read' },
  { path: '/admin/settings/payroll', label: 'Payroll Settings', icon: Settings, adminOnly: true, requiredPermission: 'organization.manage' },
  { path: '/admin/organization', label: 'Organization', icon: Building2, adminOnly: true, requiredPermission: 'organization.manage' },
  { path: '/admin/holidays', label: 'Holidays', icon: Calendar, adminOnly: true, requiredPermission: 'organization.manage' },
  { path: '/admin/attendance', label: 'Attendance Monitor', icon: Calendar, adminOnly: true, requiredPermission: 'attendance.read' },
  { path: '/admin/attendance/sync', label: 'Attendance Sync Settings', icon: RefreshCw, adminOnly: true, requiredPermission: 'attendance.sync' },
  { path: '/admin/attendance/historical-corrections', label: 'Historical Corrections', icon: FileText, adminOnly: true, requiredPermission: 'attendance.sync' },
  { path: '/admin/attendance-policy', label: 'Policy Engine', icon: Settings, adminOnly: true, requiredPermission: 'policy.attendance.manage' },
  { path: '/admin/leave-policy', label: 'Leave Policy', icon: Settings, adminOnly: true, requiredPermission: 'policy.leave.manage' },
  { path: '/admin/reimbursement-policy', label: 'Reimb. Policy', icon: Settings, adminOnly: true, requiredPermission: 'policy.reimbursement.manage' },
  { path: '/admin/weekly-off-policy', label: 'Weekly Off', icon: Settings, adminOnly: true, requiredPermission: 'policy.weekly_off.manage' },
  { path: '/admin/approvals', label: 'Leave Approvals', icon: FileText, adminOnly: true, requiredPermission: 'leave.approve' },
  { path: '/admin/reimbursement-approvals', label: 'Reimbursement Approvals', icon: Receipt, adminOnly: true, requiredPermission: 'reimbursement.approve' },
  { path: '/admin/settings', label: 'Settings', icon: Settings, adminOnly: true, requiredPermission: 'organization.manage' },
];

import { useAuth } from '../../context/AuthContext';

export const Sidebar: React.FC<SidebarProps> = ({
  isCollapsed,
  onToggle,
  isAdmin = false,
}) => {
  const location = useLocation();
  const { user, logout, hasPermission } = useAuth();
  
  const navItems = (isAdmin ? adminNavItems : employeeNavItems).filter(item => {
    if (item.requiredPermission) {
      return hasPermission(item.requiredPermission);
    }
    return true;
  });

  return (
    <motion.aside
      className="fixed left-0 top-0 h-screen bg-white border-r border-neutral-200 z-40 flex flex-col shadow-sm"
      animate={{ width: isCollapsed ? 80 : 260 }}
      transition={{ duration: 0.2, ease: 'easeInOut' }}
    >
      {/* Logo Area */}
      <div className="relative h-16 flex items-center justify-center border-b border-neutral-200">
        <motion.div
          className="flex items-center gap-3"
          initial={false}
          animate={{ opacity: 1 }}
        >
          <div className="w-10 h-10 rounded-xl bg-primary-500 flex items-center justify-center shadow-md">
            <span className="text-white font-bold text-sm">IDS</span>
          </div>
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                className="overflow-hidden whitespace-nowrap"
              >
                <h1 className="text-lg font-bold text-neutral-900">IDS Pvt Ltd</h1>
                <p className="text-xs text-neutral-500">Enterprise HRMS</p>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Toggle Button */}
        <motion.button
          onClick={onToggle}
          className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-primary-500 border-2 border-white text-white flex items-center justify-center shadow-md"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          {isCollapsed ? (
            <ChevronRight className="w-3 h-3" />
          ) : (
            <ChevronLeft className="w-3 h-3" />
          )}
        </motion.button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 overflow-y-auto">
        <div className="space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <NavLink key={item.path} to={item.path}>
                <motion.div
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-primary-50 text-primary-600 border-l-3 border-primary-500'
                      : 'text-neutral-500 hover:bg-neutral-100 hover:text-neutral-800'
                  }`}
                  whileHover={{ x: 4 }}
                >
                  <item.icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-primary-500' : ''}`} />
                  <AnimatePresence>
                    {!isCollapsed && (
                      <motion.span
                        initial={{ opacity: 0, width: 0 }}
                        animate={{ opacity: 1, width: 'auto' }}
                        exit={{ opacity: 0, width: 0 }}
                        className="text-sm font-medium overflow-hidden whitespace-nowrap"
                      >
                        {item.label}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </motion.div>
              </NavLink>
            );
          })}
        </div>
      </nav>

      {/* User Profile */}
      <div className="p-3 border-t border-neutral-200">
        <motion.div
          className="flex items-center gap-3 p-2 rounded-lg hover:bg-neutral-100 cursor-pointer transition-colors"
          whileHover={{ scale: 1.02 }}
        >
          <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 border-2 border-primary-500">
            <span className="text-primary-600 font-medium text-sm">
              {user?.name ? user.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() : 'U'}
            </span>
          </div>
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                className="flex-1 overflow-hidden"
              >
                <p className="text-sm font-medium text-neutral-900 truncate">{user?.name || 'User'}</p>
                <p className="text-xs text-neutral-500 truncate">{user?.empId || 'EMP-000'}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        <AnimatePresence>
          {!isCollapsed && (
            <motion.button
              onClick={() => logout()}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-2 w-full px-3 py-2 mt-2 rounded-lg text-neutral-500 hover:bg-red-50 hover:text-red-600 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm">Logout</span>
            </motion.button>
          )}
        </AnimatePresence>
      </div>
    </motion.aside>
  );
};

export default Sidebar;
