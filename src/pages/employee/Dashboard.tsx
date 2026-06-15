<<<<<<< HEAD
import React, { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { CalendarDays, Clock, Briefcase, IndianRupee, Users, PartyPopper, Bell } from 'lucide-react';
import { GlassCard, KPICard, StatusBadge, NotificationCard } from '../../components/ui';
import { AreaChart, DonutChart } from '../../components/charts';
import { DashboardLayout } from '../../components/layout';
import { DashboardSummary, getDashboardSummary } from '../../services/dashboardService';
=======
import React from 'react';
import { motion } from 'framer-motion';
import {
  CalendarDays,
  Clock,
  Briefcase,
  IndianRupee,
  Users,
  PartyPopper,
  Bell,
} from 'lucide-react';
import { GlassCard, KPICard, StatusBadge, NotificationCard } from '../../components/ui';
import { AreaChart, DonutChart } from '../../components/charts';
import { DashboardLayout } from '../../components/layout';
import {
  dashboardStats,
  attendanceTrendData,
  leaveBalance,
  upcomingHolidays,
  notifications,
  monthlyAttendance,
} from '../../data/mockData';
>>>>>>> d905dc76d127cb40376e7b8239e6f855343afc15

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export const Dashboard: React.FC = () => {
<<<<<<< HEAD
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadSummary = async () => {
      try {
        setIsLoading(true);
        setSummary(await getDashboardSummary());
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : 'Unable to load dashboard');
      } finally {
        setIsLoading(false);
      }
    };

    loadSummary();
  }, []);

  const attendanceChartData = useMemo(() => [{ name: 'Present Days', data: summary?.attendanceTrendData.present ?? [] }], [summary]);
  const leaveChartData = summary
    ? [summary.attendance.presentDays, summary.attendance.leaveBalance, summary.attendance.absentDays, 0, 0]
    : [0, 0, 0, 0, 0];

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

          <motion.div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4" variants={itemVariants}>
            <KPICard title="Present Days" value={summary?.attendance.presentDays ?? 0} icon={CalendarDays} color="green" delay={0} />
            <KPICard title="Absent Days" value={summary?.attendance.absentDays ?? 0} icon={Users} color="red" delay={0.1} />
            <KPICard title="Leave Balance" value={summary?.attendance.leaveBalance ?? 0} icon={Briefcase} color="blue" delay={0.2} />
            <KPICard title="Current Salary" value={summary?.attendance.currentSalary ?? 0} prefix="₹" icon={IndianRupee} color="purple" delay={0.3} />
            <KPICard title="Working Hours" value={summary?.attendance.workingHours ?? 0} suffix=" hrs" icon={Clock} color="yellow" delay={0.4} />
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
                <AreaChart data={attendanceChartData} categories={summary?.attendanceTrendData.months ?? []} height={280} />
              </GlassCard>
            </motion.div>

            <motion.div variants={itemVariants}>
              <GlassCard className="p-6">
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-neutral-900">Attendance Distribution</h3>
                  <p className="text-sm text-neutral-500">Current month snapshot</p>
                </div>
                <DonutChart labels={['Present', 'Leave', 'Absent', 'Week Off', 'OD']} series={leaveChartData} colors={['#00924C', '#f59e0b', '#ef4444', '#3b82f6', '#9333ea']} height={250} />
              </GlassCard>
            </motion.div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <motion.div variants={itemVariants}>
              <GlassCard className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Leave Balance</h3>
                <div className="space-y-4">
                  {Object.entries(summary?.leaveBalance ?? {}).map(([key, value]) => (
                    <div key={key} className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-neutral-600 capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                        <span className="text-neutral-800 font-medium">{value.balance} / {value.total}</span>
                      </div>
                      <div className="h-2 rounded-full bg-neutral-200 overflow-hidden">
                        <motion.div className="h-full bg-primary-500 rounded-full" initial={{ width: 0 }} animate={{ width: `${(value.balance / value.total) * 100}%` }} transition={{ duration: 0.8, delay: 0.2 }} />
                      </div>
                    </div>
                  ))}
                  {!Object.keys(summary?.leaveBalance ?? {}).length ? <p className="text-sm text-neutral-500">Leave balance data is not available yet.</p> : null}
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
                  {(summary?.upcomingHolidays ?? []).length ? summary!.upcomingHolidays.slice(0, 4).map((holiday, index) => (
                    <motion.div key={holiday.date} className="flex items-center gap-3 p-3 rounded-lg bg-neutral-50 border border-neutral-200 hover:border-primary-300 transition-colors" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.1 }}>
                      <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center text-primary-600 font-semibold text-sm">{new Date(holiday.date).getDate()}</div>
                      <div className="flex-1"><p className="text-sm font-medium text-neutral-900">{holiday.name}</p><p className="text-xs text-neutral-500">{holiday.type}</p></div>
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
                  {(summary?.notifications ?? []).length ? summary!.notifications.slice(0, 4).map((notification) => (
                    <NotificationCard key={notification.id} title={notification.title} message={notification.message} type={notification.type as 'success' | 'warning' | 'error' | 'info'} time={notification.time} />
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
                  { label: 'Apply Leave', icon: CalendarDays, bgColor: 'bg-primary-100', iconColor: 'text-primary-600' },
                  { label: 'View Payslip', icon: IndianRupee, bgColor: 'bg-purple-100', iconColor: 'text-purple-600' },
                  { label: 'Apply OD', icon: Briefcase, bgColor: 'bg-blue-100', iconColor: 'text-blue-600' },
                  { label: 'Update Profile', icon: Users, bgColor: 'bg-emerald-100', iconColor: 'text-emerald-600' },
                ].map((action, index) => (
                  <motion.button key={action.label} className="p-4 rounded-xl bg-neutral-50 hover:bg-primary-50 border border-neutral-200 hover:border-primary-300 transition-all text-left" whileHover={{ y: -2 }} whileTap={{ scale: 0.98 }} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }}>
                    <div className={`w-10 h-10 rounded-lg ${action.bgColor} flex items-center justify-center mb-3`}>
                      <action.icon className={`w-5 h-5 ${action.iconColor}`} />
                    </div>
                    <p className="text-sm font-medium text-neutral-800">{action.label}</p>
                  </motion.button>
=======
  const presentCount = monthlyAttendance.filter((a) => a.status === 'present').length;
  const leaveCount = monthlyAttendance.filter((a) => a.status === 'leave').length;
  const absentCount = monthlyAttendance.filter((a) => a.status === 'absent').length;
  const weekoffCount = monthlyAttendance.filter((a) => a.status === 'weekoff').length;

  const attendanceChartData = [{ name: 'Present Days', data: attendanceTrendData.present }];

  const leaveChartData = [
    presentCount,
    leaveCount,
    absentCount,
    weekoffCount,
    monthlyAttendance.filter((a) => a.status === 'od').length,
  ];

  return (
    <DashboardLayout>
      <motion.div className="space-y-6" variants={containerVariants} initial="hidden" animate="visible">
        {/* Welcome Banner */}
        <motion.div variants={itemVariants}>
          <GlassCard className="p-6 relative overflow-hidden">
            <div className="relative z-10">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-neutral-900 mb-2">Welcome back, John!</h2>
                  <p className="text-neutral-600 mb-4">Here's your attendance and payroll overview.</p>
                  <div className="flex items-center gap-3">
                    <StatusBadge status="success" label="Checked In" size="sm" />
                    <span className="text-sm text-neutral-500">09:15 AM</span>
                  </div>
                </div>
                <div className="hidden sm:block">
                  <img
                    src="https://images.pexels.com/photos/2379004/pexels-photo-2379004.jpeg?auto=compress&cs=tinysrgb&w=150"
                    alt="Profile"
                    className="w-20 h-20 rounded-xl object-cover border-2 border-primary-500"
                  />
                </div>
              </div>
            </div>
            <div className="absolute -right-20 -bottom-20 w-48 h-48 bg-primary-100/50 rounded-full blur-2xl" />
          </GlassCard>
        </motion.div>

        {/* KPI Cards */}
        <motion.div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4" variants={itemVariants}>
          <KPICard title="Present Days" value={dashboardStats.presentDays.value} icon={CalendarDays} trend={dashboardStats.presentDays.trend} trendLabel={dashboardStats.presentDays.label} color="green" delay={0} />
          <KPICard title="Absent Days" value={dashboardStats.absentDays.value} icon={Users} trend={dashboardStats.absentDays.trend} trendLabel={dashboardStats.absentDays.label} color="red" delay={0.1} />
          <KPICard title="Leave Balance" value={dashboardStats.leaveBalance.value} icon={Briefcase} trendLabel={dashboardStats.leaveBalance.label} color="blue" delay={0.2} />
          <KPICard title="Current Salary" value={dashboardStats.currentSalary.value} prefix="\u20B9" icon={IndianRupee} trend={dashboardStats.currentSalary.trend} trendLabel={dashboardStats.currentSalary.label} color="purple" delay={0.3} />
          <KPICard title="Working Hours" value={dashboardStats.workingHours.value} suffix=" hrs" icon={Clock} trend={dashboardStats.workingHours.trend} trendLabel={dashboardStats.workingHours.label} color="yellow" delay={0.4} />
        </motion.div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <motion.div className="lg:col-span-2" variants={itemVariants}>
            <GlassCard className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-neutral-900">Attendance Trend</h3>
                  <p className="text-sm text-neutral-500">Last 6 months overview</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1.5 text-xs text-neutral-500">
                    <div className="w-2 h-2 rounded-full bg-primary-500" />
                    Present Days
                  </div>
                </div>
              </div>
              <AreaChart data={attendanceChartData} categories={attendanceTrendData.months} height={280} />
            </GlassCard>
          </motion.div>

          <motion.div variants={itemVariants}>
            <GlassCard className="p-6">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-neutral-900">January Stats</h3>
                <p className="text-sm text-neutral-500">Attendance distribution</p>
              </div>
              <DonutChart labels={['Present', 'Leave', 'Absent', 'Week Off', 'OD']} series={leaveChartData} colors={['#00924C', '#f59e0b', '#ef4444', '#3b82f6', '#9333ea']} height={250} />
            </GlassCard>
          </motion.div>
        </div>

        {/* Widgets Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Leave Balance */}
          <motion.div variants={itemVariants}>
            <GlassCard className="p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4">Leave Balance</h3>
              <div className="space-y-4">
                {Object.entries(leaveBalance).map(([key, value]) => (
                  <div key={key} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-neutral-600 capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                      <span className="text-neutral-800 font-medium">{value.balance} / {value.total}</span>
                    </div>
                    <div className="h-2 rounded-full bg-neutral-200 overflow-hidden">
                      <motion.div className="h-full bg-primary-500 rounded-full" initial={{ width: 0 }} animate={{ width: `${(value.balance / value.total) * 100}%` }} transition={{ duration: 0.8, delay: 0.2 }} />
                    </div>
                  </div>
>>>>>>> d905dc76d127cb40376e7b8239e6f855343afc15
                ))}
              </div>
            </GlassCard>
          </motion.div>
<<<<<<< HEAD
        </motion.div>
      </div>
=======

          {/* Upcoming Holidays */}
          <motion.div variants={itemVariants}>
            <GlassCard className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-neutral-900">Upcoming Holidays</h3>
                <PartyPopper className="w-5 h-5 text-amber-500" />
              </div>
              <div className="space-y-3">
                {upcomingHolidays.slice(0, 4).map((holiday, index) => (
                  <motion.div key={holiday.date} className="flex items-center gap-3 p-3 rounded-lg bg-neutral-50 border border-neutral-200 hover:border-primary-300 transition-colors" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.1 }}>
                    <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center text-primary-600 font-semibold text-sm">
                      {new Date(holiday.date).getDate()}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-neutral-900">{holiday.name}</p>
                      <p className="text-xs text-neutral-500">{holiday.type}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </GlassCard>
          </motion.div>

          {/* Notifications */}
          <motion.div variants={itemVariants}>
            <GlassCard className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-neutral-900">Recent Notifications</h3>
                <Bell className="w-5 h-5 text-primary-500" />
              </div>
              <div className="space-y-3">
                {notifications.slice(0, 4).map((notification) => (
                  <NotificationCard key={notification.id} title={notification.title} message={notification.message} type={notification.type as 'success' | 'warning' | 'error' | 'info'} time={notification.time} />
                ))}
              </div>
            </GlassCard>
          </motion.div>
        </div>

        {/* Quick Actions */}
        <motion.div variants={itemVariants}>
          <GlassCard className="p-6">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: 'Apply Leave', icon: CalendarDays, bgColor: 'bg-primary-100', iconColor: 'text-primary-600' },
                { label: 'View Payslip', icon: IndianRupee, bgColor: 'bg-purple-100', iconColor: 'text-purple-600' },
                { label: 'Apply OD', icon: Briefcase, bgColor: 'bg-blue-100', iconColor: 'text-blue-600' },
                { label: 'Update Profile', icon: Users, bgColor: 'bg-emerald-100', iconColor: 'text-emerald-600' },
              ].map((action, index) => (
                <motion.button key={action.label} className="p-4 rounded-xl bg-neutral-50 hover:bg-primary-50 border border-neutral-200 hover:border-primary-300 transition-all text-left" whileHover={{ y: -2 }} whileTap={{ scale: 0.98 }} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }}>
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
>>>>>>> d905dc76d127cb40376e7b8239e6f855343afc15
    </DashboardLayout>
  );
};

<<<<<<< HEAD
export default Dashboard;
=======
export default Dashboard;
>>>>>>> d905dc76d127cb40376e7b8239e6f855343afc15
