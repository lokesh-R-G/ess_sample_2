import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CalendarDays, Clock, Briefcase, IndianRupee, Users, PartyPopper, Bell } from 'lucide-react';
import { GlassCard, KPICard, StatusBadge, NotificationCard } from '../../components/ui';
import ErrorBoundary from '../../components/ui/ErrorBoundary';
import { AreaChart, DonutChart } from '../../components/charts';
import { DashboardLayout } from '../../components/layout';
import { DashboardSummary, getDashboardSummary } from '../../services/dashboardService';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadSummary = async () => {
      try {
        setError('');
        setIsLoading(true);
        const data = await getDashboardSummary();
        setSummary(data);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : 'Unable to load dashboard');
      } finally {
        setIsLoading(false);
      }
    };

    loadSummary();
  }, []);

  const attendanceChartData = useMemo(
    () => [{ name: 'Present Days', data: summary?.attendanceTrendData.present ?? [] }],
    [summary],
  );

  const leaveChartData = summary?.distribution ?? [0, 0, 0, 0, 0];

  return (
    <DashboardLayout>
      <div className="space-y-4">
        {error ? <GlassCard className="p-4 border border-red-200 bg-red-50 text-red-700">{error}</GlassCard> : null}
        {isLoading ? <GlassCard className="p-4 text-sm text-neutral-500">Loading dashboard...</GlassCard> : null}

        <motion.div className="space-y-6" variants={containerVariants} initial="hidden" animate="visible">
          <motion.div variants={itemVariants}>
            <GlassCard className="p-6 relative overflow-hidden">
              <div className="relative z-10">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-neutral-900 mb-2">Welcome back, {summary?.employee.name ?? 'Employee'}!</h2>
                    <p className="text-neutral-600 mb-4">Here's your attendance and payroll overview.</p>
                    <div className="flex items-center gap-3">
                      <StatusBadge status="success" label="Live Data" size="sm" />
                      <span className="text-sm text-neutral-500">Synced from backend</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="absolute -right-20 -bottom-20 w-48 h-48 bg-primary-100/50 rounded-full blur-2xl" />
            </GlassCard>
          </motion.div>

          {summary?.alerts && summary.alerts.length > 0 && (
            <motion.div variants={itemVariants}>
              <GlassCard className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-neutral-900">Enterprise Alert Center</h3>
                  <Bell className="w-5 h-5 text-primary-500" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {summary.alerts.map((alert, index) => {
                    const colors = {
                      success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
                      warning: 'bg-amber-50 text-amber-700 border-amber-200',
                      error: 'bg-red-50 text-red-700 border-red-200',
                      info: 'bg-blue-50 text-blue-700 border-blue-200'
                    };
                    return (
                      <div key={index} className={`p-4 rounded-xl border ${colors[alert.type]} flex items-start gap-3`}>
                        <div className="flex-1 font-medium">{alert.message}</div>
                      </div>
                    );
                  })}
                </div>
              </GlassCard>
            </motion.div>
          )}

          <motion.div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4" variants={itemVariants}>
            <KPICard title="Present Days" value={summary?.stats.presentDays ?? 0} icon={CalendarDays} color="green" delay={0} />
            <KPICard title="Absent Days" value={summary?.stats.absentDays ?? 0} icon={Users} color="red" delay={0.1} />
            <KPICard title="Leave Balance" value={summary?.stats.leaveBalance ?? 0} icon={Briefcase} color="blue" delay={0.2} />
            <KPICard title="Current Salary" value={summary?.stats.currentSalary ?? 0} prefix="₹" icon={IndianRupee} color="purple" delay={0.3} />
            <KPICard title="Working Hours" value={summary?.stats.workingHours ?? 0} suffix=" hrs" icon={Clock} color="yellow" delay={0.4} />
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <motion.div className="lg:col-span-2" variants={itemVariants}>
              <GlassCard className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-semibold text-neutral-900">Attendance Trend</h3>
                    <p className="text-sm text-neutral-500">Backend-driven attendance summary</p>
                  </div>
                </div>
                {summary && (
                  <ErrorBoundary fallback={<p className="text-sm text-neutral-500">Chart unavailable.</p>}>
                    <AreaChart data={attendanceChartData} categories={summary.attendanceTrendData.months ?? []} height={280} />
                  </ErrorBoundary>
                )}
              </GlassCard>
            </motion.div>

            <motion.div variants={itemVariants}>
              <GlassCard className="p-6">
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-neutral-900">Attendance Distribution</h3>
                  <p className="text-sm text-neutral-500">Current month snapshot</p>
                </div>
                {summary ? (
                  leaveChartData.reduce((a, b) => a + b, 0) > 0 ? (
                    <ErrorBoundary fallback={<p className="text-sm text-neutral-500">Chart unavailable.</p>}>
                      <DonutChart labels={[ 'Present', 'Leave', 'Absent', 'Week Off', 'OD' ]} series={leaveChartData} colors={[ '#00924C', '#f59e0b', '#ef4444', '#3b82f6', '#9333ea' ]} height={250} />
                    </ErrorBoundary>
                  ) : (
                    <p className="text-sm text-neutral-500">No distribution data available.</p>
                  )
                ) : null}
              </GlassCard>
            </motion.div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <motion.div variants={itemVariants}>
              <GlassCard className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Leave Balance</h3>
                <div className="space-y-4">
                  {Object.entries(summary?.leaveBalance ?? {}).length ? (
                    Object.entries(summary!.leaveBalance).map(([key, value]) => (
                      <div key={key} className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-neutral-600 capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                          <span className="text-neutral-800 font-medium">{value.balance} / {value.total}</span>
                        </div>
                        <div className="h-2 rounded-full bg-neutral-200 overflow-hidden">
                          <motion.div className="h-full bg-primary-500 rounded-full" initial={{ width: 0 }} animate={{ width: `${(value.balance / Math.max(value.total, 1)) * 100}%` }} transition={{ duration: 0.8, delay: 0.2 }} />
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-neutral-500">Leave balance data is not available yet.</p>
                  )}
                </div>
              </GlassCard>
            </motion.div>

            <motion.div variants={itemVariants}>
              <GlassCard className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-neutral-900">Upcoming Holidays</h3>
                  <PartyPopper className="w-5 h-5 text-amber-500" />
                </div>
                <div className="space-y-3">
                  {summary?.upcomingHolidays?.length ? summary.upcomingHolidays.slice(0, 4).map((holiday, index) => (
                    <motion.div key={holiday.date} className="flex items-center gap-3 p-3 rounded-lg bg-neutral-50 border border-neutral-200 hover:border-primary-300 transition-colors" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.1 }}>
                      <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center text-primary-600 font-semibold text-sm">{new Date(holiday.date).getDate()}</div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-neutral-900">{holiday.name}</p>
                        <p className="text-xs text-neutral-500">{holiday.type}</p>
                      </div>
                    </motion.div>
                  )) : <p className="text-sm text-neutral-500">No holidays loaded from backend.</p>}
                </div>
              </GlassCard>
            </motion.div>

            <motion.div variants={itemVariants}>
              <GlassCard className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-neutral-900">Recent Notifications</h3>
                  <Bell className="w-5 h-5 text-primary-500" />
                </div>
                <div className="space-y-3">
                  {summary?.notifications?.length ? summary.notifications.slice(0, 4).map((notification, index) => (
                    <NotificationCard
                      key={notification.id ?? index}
                      title={notification.title ?? 'Notification'}
                      message={notification.message ?? 'No details available.'}
                      type={(notification.type as 'success' | 'warning' | 'error' | 'info') ?? 'info'}
                      time={notification.time ?? ''}
                    />
                  )) : <p className="text-sm text-neutral-500">No notifications yet.</p>}
                </div>
              </GlassCard>
            </motion.div>
          </div>

          <motion.div variants={itemVariants}>
            <GlassCard className="p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {[
                  { label: 'Apply Leave', icon: CalendarDays, bgColor: 'bg-primary-100', iconColor: 'text-primary-600', path: '/leave' },
                  { label: 'View Payslip', icon: IndianRupee, bgColor: 'bg-purple-100', iconColor: 'text-purple-600', path: '/payslip' },
                  { label: 'Apply OD', icon: Briefcase, bgColor: 'bg-blue-100', iconColor: 'text-blue-600', path: '/leave?type=OD' },
                  { label: 'Update Profile', icon: Users, bgColor: 'bg-emerald-100', iconColor: 'text-emerald-600', path: '/profile' },
                ].map((action, index) => (
                  <motion.button
                    key={action.label}
                    onClick={() => navigate(action.path)}
                    className="p-4 rounded-xl bg-neutral-50 hover:bg-primary-50 border border-neutral-200 hover:border-primary-300 transition-all text-left"
                    whileHover={{ y: -2 }}
                    whileTap={{ scale: 0.98 }}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <div className={`w-10 h-10 rounded-lg ${action.bgColor} flex items-center justify-center mb-3`}>
                      <action.icon className={`w-5 h-5 ${action.iconColor}`} />
                    </div>
                    <p className="text-sm font-medium text-neutral-800">{action.label}</p>
                  </motion.button>
                ))}
              </div>
            </GlassCard>
          </motion.div>
        </motion.div>
      </div>
    </DashboardLayout>
  );
};

export default Dashboard;
