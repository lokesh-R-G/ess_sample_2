import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Users, Building2, CheckCircle, DollarSign, TrendingUp, AlertCircle, Clock, BarChart3 } from 'lucide-react';
import { GlassCard, KPICard, AnimatedButton, StatusBadge } from '../../components/ui';
import { AreaChart, DonutChart } from '../../components/charts';
import { AdminSummary, getAdminSummary, AttendanceSummary, getAttendanceSummary } from '../../services/adminService';

export const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<AdminSummary | null>(null);
  const [attSummary, setAttSummary] = useState<AttendanceSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadSummary = async () => {
      try {
        setIsLoading(true);
        const [sum, att] = await Promise.all([
          getAdminSummary(),
          getAttendanceSummary()
        ]);
        setSummary(sum);
        setAttSummary(att);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : 'Unable to load admin dashboard');
      } finally {
        setIsLoading(false);
      }
    };

    loadSummary();
  }, []);

  const attendanceChartData = useMemo(() => ([{ name: 'Present', data: summary?.attendanceTrend.present ?? [] }, { name: 'Absent', data: summary?.attendanceTrend.absent ?? [] }]), [summary]);
  const recentEmployees = summary?.employeeList ?? [];
  const branchData = summary?.branchData ?? [];


  return (
    <>
      <div className="space-y-6">

        {error ? <GlassCard className="p-4 border border-red-200 bg-red-50 text-red-700">{error}</GlassCard> : null}
        {isLoading ? <GlassCard className="p-4 text-sm text-neutral-500">Loading admin dashboard...</GlassCard> : null}
        {/* Welcome Section */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <GlassCard className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-neutral-900 mb-1">Admin Dashboard</h2>
                <p className="text-sm text-neutral-600">Monitor and manage your organization efficiently</p>
              </div>
              <AnimatedButton variant="secondary" size="sm" icon={Clock}>Pending Approvals (8)</AnimatedButton>
            </div>
          </GlassCard>
        </motion.div>

        {/* Admin KPIs */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <KPICard title="Total Employees" value={summary?.stats.totalEmployees ?? 0} icon={Users} color="green" />
          <KPICard title="Active Employees" value={summary?.stats.activeEmployees ?? 0} icon={CheckCircle} color="blue" />
          <KPICard title="New Joinees" value={summary?.stats.newJoinees ?? 0} icon={TrendingUp} color="purple" />
          <KPICard title="Attrition" value={summary?.stats.attrition ?? 0} icon={TrendingUp} color="red" />
          <KPICard title="Attendance Rate" value={summary?.stats.attendanceRate ?? 0} suffix="%" icon={BarChart3} color="yellow" />
          <KPICard title="Branches" value={summary?.stats.branches ?? 0} icon={Building2} color="orange" />
        </div>

        {/* Daily Attendance Monitor */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <GlassCard className="p-6">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4">Today's Attendance Monitor</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <KPICard title="Present Today" value={attSummary?.present ?? 0} icon={CheckCircle} color="green" />
              <KPICard title="Absent Today" value={attSummary?.absent ?? 0} icon={AlertCircle} color="red" />
              <KPICard title="On Duty / Leave" value={attSummary?.od ?? 0} icon={Clock} color="purple" />
            </div>
          </GlassCard>
        </motion.div>

        {/* Quick Actions */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <GlassCard className="p-6">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
              {[
                { label: 'Add Employee', icon: Users, colorScheme: { bg: 'bg-primary-100', icon: 'text-primary-600' }, path: '/admin/employees' },
                { label: 'Process Payroll', icon: DollarSign, colorScheme: { bg: 'bg-purple-100', icon: 'text-purple-600' }, path: '/admin/payroll' },
                { label: 'Approve Leaves', icon: CheckCircle, colorScheme: { bg: 'bg-blue-100', icon: 'text-blue-600' }, path: '/admin/leave-approvals' },
                { label: 'Add Branch', icon: Building2, colorScheme: { bg: 'bg-amber-100', icon: 'text-amber-600' }, path: '/admin/branches' },
                { label: 'Run Reports', icon: BarChart3, colorScheme: { bg: 'bg-orange-100', icon: 'text-orange-600' }, path: '/admin' },
                { label: 'View Alerts', icon: AlertCircle, colorScheme: { bg: 'bg-red-100', icon: 'text-red-600' }, path: '/admin' },
              ].map((action, index) => (
                <motion.button key={action.label} onClick={() => navigate(action.path)} className="p-4 rounded-xl bg-neutral-50 hover:bg-primary-50 border border-neutral-200 hover:border-primary-300 transition-all text-center" whileHover={{ y: -2 }} whileTap={{ scale: 0.98 }} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.05 }}>
                  <div className={`w-10 h-10 rounded-lg ${action.colorScheme.bg} flex items-center justify-center mx-auto mb-2`}>
                    <action.icon className={`w-5 h-5 ${action.colorScheme.icon}`} />
                  </div>
                  <p className="text-xs font-medium text-neutral-700">{action.label}</p>
                </motion.button>
              ))}
            </div>
          </GlassCard>
        </motion.div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <motion.div className="lg:col-span-2" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <GlassCard className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-neutral-900">Attendance Trend</h3>
                <div className="flex items-center gap-3 text-xs text-neutral-500">
                  <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-emerald-500" />Present</div>
                  <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-red-500" />Absent</div>
                </div>
              </div>
              <AreaChart data={attendanceChartData} categories={summary?.attendanceTrend.months ?? []} height={280} />

            </GlassCard>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <GlassCard className="p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4">Department Distribution</h3>
              <DonutChart labels={branchData.map((branch) => branch.name)} series={branchData.map((branch) => branch.employees)} height={250} />

            </GlassCard>
          </motion.div>
        </div>

        {/* Branches & Recent Employees */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <GlassCard className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-neutral-900">Branches</h3>
                <AnimatedButton variant="secondary" size="sm" icon={Building2} onClick={() => navigate('/admin/branches')}>Manage</AnimatedButton>
              </div>
              <div className="space-y-3">
                {branchData.map((branch, index) => (
                  <motion.div key={branch.id} className="flex items-center justify-between p-3 rounded-lg bg-neutral-50 border border-neutral-200 hover:border-primary-300 transition-colors" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.05 }}>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center"><Building2 className="w-5 h-5 text-primary-600" /></div>
                      <div><p className="text-sm font-medium text-neutral-900">{branch.name}</p><p className="text-xs text-neutral-500">{branch.city}</p></div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-neutral-900">{branch.employees} Employees</p>
                      <StatusBadge status={branch.status === 'active' ? 'success' : 'error'} label={branch.status} size="sm" />
                    </div>
                  </motion.div>
                ))}
              </div>
            </GlassCard>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <GlassCard className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-neutral-900">Recent Employees</h3>
                <AnimatedButton variant="secondary" size="sm" icon={Users} onClick={() => navigate('/admin/employees')}>View All</AnimatedButton>
              </div>
              <div className="space-y-3">
                {recentEmployees.map((emp, index) => (
                  <motion.div key={emp.id} className="flex items-center justify-between p-3 rounded-lg bg-neutral-50 border border-neutral-200 hover:border-primary-300 transition-colors" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.05 }}>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-primary-100 border border-primary-300 flex items-center justify-center">
                        <span className="text-primary-600 text-xs font-semibold">{emp.name.split(' ').map((n) => n[0]).join('')}</span>
                      </div>
                      <div><p className="text-sm font-medium text-neutral-900">{emp.name}</p><p className="text-xs text-neutral-500">{emp.designation}</p></div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-neutral-500">{emp.id}</p>
                      <StatusBadge status={emp.status === 'active' ? 'success' : 'error'} label={emp.status} size="sm" />
                    </div>
                  </motion.div>
                ))}
              </div>
            </GlassCard>
          </motion.div>
        </div>

        {/* Payroll Status */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <GlassCard className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center"><DollarSign className="w-6 h-6 text-emerald-600" /></div>
                <div><h3 className="text-lg font-semibold text-neutral-900">Payroll Overview</h3><p className="text-sm text-neutral-600">Backend-driven summary</p></div>
              </div>
              <div className="flex items-center gap-3">
                <StatusBadge status="success" label="Connected" />
                <span className="text-sm text-neutral-500">Total: {summary?.stats.totalEmployees ?? 0} employees</span>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </>
  );
};

export default AdminDashboard;

