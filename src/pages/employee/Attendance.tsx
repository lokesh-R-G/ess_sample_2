import React, { useEffect, useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Clock, CheckCircle2, XCircle, Coffee, Calendar as CalendarIcon, Briefcase } from 'lucide-react';
import { GlassCard, StatusBadge } from '../../components/ui';
import { DashboardLayout } from '../../components/layout';
import { format, addMonths, subMonths, startOfMonth, endOfMonth, eachDayOfInterval, getDay, isToday } from 'date-fns';
import { AttendanceRecord, getMyAttendance } from '../../services/attendanceService';

const statusConfig: Record<string, { bg: string; text: string; icon: React.ElementType; label: string }> = {
  present: { bg: 'bg-emerald-100', text: 'text-emerald-700', icon: CheckCircle2, label: 'Present' },
  absent: { bg: 'bg-red-100', text: 'text-red-700', icon: XCircle, label: 'Absent' },
  leave: { bg: 'bg-amber-100', text: 'text-amber-700', icon: CalendarIcon, label: 'Leave' },
  weekoff: { bg: 'bg-blue-100', text: 'text-blue-700', icon: Coffee, label: 'Week Off' },
  od: { bg: 'bg-purple-100', text: 'text-purple-700', icon: Briefcase, label: 'OD' },
  partial: { bg: 'bg-yellow-100', text: 'text-yellow-700', icon: Clock, label: 'Partial' },
};

export const Attendance: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadAttendance = async () => {
      try {
        setError('');
        setIsLoading(true);
        const fromDate = format(startOfMonth(currentDate), 'yyyy-MM-dd');
        const toDate = format(endOfMonth(currentDate), 'yyyy-MM-dd');
        const response = await getMyAttendance(fromDate, toDate);
        setRecords(response.records);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : 'Unable to load attendance');
      } finally {
        setIsLoading(false);
      }
    };

    loadAttendance();
  }, [currentDate]);

  const attendanceMap = useMemo(
    () => new Map(records.map((record) => [record.date, record])),
    [records],
  );

  const getAttendanceForDate = (date: Date) => attendanceMap.get(format(date, 'yyyy-MM-dd'));

  const prevMonth = () => setCurrentDate(subMonths(currentDate, 1));
  const nextMonth = () => setCurrentDate(addMonths(currentDate, 1));
  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const daysInMonth = eachDayOfInterval({ start: monthStart, end: monthEnd });
  const startDay = getDay(monthStart);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {error ? <GlassCard className="p-4 border border-red-200 bg-red-50 text-red-700">{error}</GlassCard> : null}

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {Object.entries(statusConfig).map(([key, config]) => {
            const count = records.filter((a) => (a.status?.toLowerCase() ?? 'absent') === key).length;
            return (
              <motion.div
                key={key}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: Object.keys(statusConfig).indexOf(key) * 0.05 }}
              >
                <GlassCard className="p-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${config.bg}`}>
                      <config.icon className={`w-5 h-5 ${config.text}`} />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-neutral-900">{count}</p>
                      <p className="text-xs text-neutral-500">{config.label}</p>
                    </div>
                  </div>
                </GlassCard>
              </motion.div>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <motion.div className="lg:col-span-2" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <GlassCard className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-semibold text-neutral-900">Attendance Calendar</h2>
                  <p className="text-sm text-neutral-500">Click on a day to view details</p>
                </div>
                <div className="flex items-center gap-3">
                  <motion.button onClick={prevMonth} className="p-2 rounded-lg bg-neutral-100 hover:bg-neutral-200 border border-neutral-200 transition-colors" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <ChevronLeft className="w-5 h-5 text-neutral-600" />
                  </motion.button>
                  <span className="text-lg font-medium text-neutral-900 min-w-[140px] text-center">{format(currentDate, 'MMMM yyyy')}</span>
                  <motion.button onClick={nextMonth} className="p-2 rounded-lg bg-neutral-100 hover:bg-neutral-200 border border-neutral-200 transition-colors" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <ChevronRight className="w-5 h-5 text-neutral-600" />
                  </motion.button>
                </div>
              </div>

              <div className="grid grid-cols-7 gap-2 mb-2">
                {weekDays.map((day) => (
                  <div key={day} className="text-center text-xs font-semibold text-primary-600 uppercase py-2">{day}</div>
                ))}
              </div>

              <div className="grid grid-cols-7 gap-2">
                {[...Array(startDay)].map((_, i) => <div key={`empty-${i}`} className="aspect-square" />)}
                {daysInMonth.map((day, index) => {
                  const attendance = getAttendanceForDate(day);
                  const status = attendance?.status?.toLowerCase() ?? 'absent';
                  const isSelected = selectedDate && format(day, 'yyyy-MM-dd') === format(selectedDate, 'yyyy-MM-dd');

                  return (
                    <motion.button
                      key={day.toISOString()}
                      className={`aspect-square rounded-lg flex flex-col items-center justify-center relative transition-all ${isSelected ? 'ring-2 ring-primary-500 bg-primary-50' : isToday(day) ? 'bg-primary-50 border border-primary-300' : 'hover:bg-neutral-100'} bg-white border border-neutral-200`}
                      onClick={() => setSelectedDate(day)}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.01 }}
                      whileHover={{ scale: 1.05 }}
                    >
                      <span className={`text-sm font-medium ${isToday(day) ? 'text-primary-600' : 'text-neutral-900'}`}>{format(day, 'd')}</span>
                      {attendance && <div className={`w-1.5 h-1.5 rounded-full mt-1 ${status.includes('present') ? 'bg-emerald-500' : status === 'absent' ? 'bg-red-500' : status === 'leave' ? 'bg-amber-500' : status === 'od' ? 'bg-purple-500' : 'bg-blue-500'}`} />}
                    </motion.button>
                  );
                })}
              </div>

              <div className="flex flex-wrap items-center gap-4 mt-6 pt-4 border-t border-neutral-200">
                {Object.entries(statusConfig).map(([key, config]) => (
                  <div key={key} className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${config.bg}`} />
                    <span className="text-xs text-neutral-600">{config.label}</span>
                  </div>
                ))}
              </div>
            </GlassCard>
          </motion.div>

          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
            <GlassCard className="p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4">Day Details</h3>
              <AnimatePresence mode="wait">
                {isLoading ? (
                  <div className="text-sm text-neutral-500">Loading attendance...</div>
                ) : selectedDate ? (
                  (() => {
                    const attendance = getAttendanceForDate(selectedDate);
                    if (!attendance) {
                      return <div className="text-sm text-neutral-500">No attendance found for this date.</div>;
                    }
                    const status = attendance.status?.toLowerCase() ?? 'absent';
                    
                    const inTimeStr = attendance.inTime || attendance.firstIn;
                    const outTimeStr = attendance.outTime || attendance.lastOut;
                    const inDate = inTimeStr ? new Date(inTimeStr) : null;
                    const outDate = outTimeStr ? new Date(outTimeStr) : null;
                    
                    let computedHours = attendance.workHours;
                    if (computedHours === undefined && inDate && outDate) {
                      computedHours = (outDate.getTime() - inDate.getTime()) / (1000 * 60 * 60);
                    }

                    return (
                      <motion.div key={selectedDate.toISOString()} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="space-y-4">
                        <div className="text-center p-4 rounded-xl bg-primary-50 border border-primary-200">
                          <p className="text-2xl font-bold text-neutral-900">{format(selectedDate, 'd')}</p>
                          <p className="text-sm text-neutral-600">{format(selectedDate, 'EEEE, MMMM yyyy')}</p>
                        </div>
                        <div className="flex justify-center">
                          <StatusBadge
                            status={status.includes('present') ? 'success' : status === 'absent' ? 'error' : status === 'leave' ? 'warning' : status === 'od' ? 'purple' : 'info'}
                            label={attendance.status || 'ABSENT'}
                          />
                        </div>
                        <div className="text-sm text-neutral-600 space-y-2">
                          <div className="flex items-center justify-between">
                            <span>Status</span>
                            <span className="font-medium text-neutral-900 capitalize">{attendance.status || 'Absent'}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span>In Time</span>
                            <span className="font-medium text-neutral-900">{inDate ? format(inDate, 'hh:mm a') : '--:--'}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span>Out Time</span>
                            <span className="font-medium text-neutral-900">{outDate ? format(outDate, 'hh:mm a') : '--:--'}</span>
                          </div>
                        </div>
                        {(status.includes('present') || status === 'od' || status === 'partial') && (
                          <div className="space-y-3">
                            <div className="flex items-center justify-between p-3 rounded-lg bg-neutral-50 border border-neutral-200">
                              <div className="flex items-center gap-2"><Clock className="w-4 h-4 text-emerald-600" /><span className="text-sm text-neutral-600">Check In</span></div>
                              <span className="text-sm font-medium text-neutral-900">{inDate ? format(inDate, 'hh:mm a') : '--:--'}</span>
                            </div>
                            <div className="flex items-center justify-between p-3 rounded-lg bg-neutral-50 border border-neutral-200">
                              <div className="flex items-center gap-2"><Clock className="w-4 h-4 text-red-600" /><span className="text-sm text-neutral-600">Check Out</span></div>
                              <span className="text-sm font-medium text-neutral-900">{outDate ? format(outDate, 'hh:mm a') : '--:--'}</span>
                            </div>
                            {computedHours !== undefined && computedHours > 0 && (
                              <div className="flex items-center justify-between p-3 rounded-lg bg-primary-50 border border-primary-200">
                                <div className="flex items-center gap-2"><Clock className="w-4 h-4 text-primary-600" /><span className="text-sm text-neutral-600">Working Hours</span></div>
                                <span className="text-sm font-semibold text-primary-600">{computedHours.toFixed(2)} hrs</span>
                              </div>
                            )}
                          </div>
                        )}
                      </motion.div>
                    );
                  })()
                ) : (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-8">
                    <CalendarIcon className="w-12 h-12 text-neutral-300 mx-auto mb-3" />
                    <p className="text-sm text-neutral-500">Select a day to view details</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </GlassCard>
          </motion.div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Attendance;
