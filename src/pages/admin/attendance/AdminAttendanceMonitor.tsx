import React, { useState, useEffect } from 'react';
import { GlassCard } from '../../../components/ui';
import { api } from '../../../lib/api';
import { format, startOfMonth, endOfMonth, addMonths, subMonths } from 'date-fns';
import { ChevronLeft, ChevronRight, AlertCircle, Clock } from 'lucide-react';

export const AdminAttendanceMonitor: React.FC = () => {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [data, setData] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [selectedCell, setSelectedCell] = useState<{employeeId: string, date: string, details: any, empDetails: any} | null>(null);

  useEffect(() => {
    fetchData();
  }, [currentMonth]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const from = format(startOfMonth(currentMonth), 'yyyy-MM-dd');
      const to = format(endOfMonth(currentMonth), 'yyyy-MM-dd');
      // Using the new API endpoint
      const response = await api.get<any>(`/v2/attendance/monitor?from=${from}&to=${to}`);
      setData(response.monthSummary || {});
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to fetch attendance data');
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = () => {
    const start = startOfMonth(currentMonth);
    const end = endOfMonth(currentMonth);
    const days = [];
    for (let d = start; d <= end; d.setDate(d.getDate() + 1)) {
      days.push(new Date(d));
    }
    return days;
  };
  
  const days = getDaysInMonth();

  const getStatusColor = (status: string, isLate: boolean) => {
    if (isLate) return 'bg-orange-100 text-orange-800 border border-orange-300';
    switch (status) {
      case 'Present': return 'bg-green-100 text-green-800';
      case 'Absent': return 'bg-red-100 text-red-800';
      case 'Leave': return 'bg-purple-100 text-purple-800';
      case 'Holiday': return 'bg-blue-100 text-blue-800';
      case 'Week Off': return 'bg-gray-100 text-gray-800';
      case 'LOP': return 'bg-rose-100 text-rose-800';
      default: return 'bg-gray-50 text-gray-400';
    }
  };

  const getStatusAbbr = (status: string) => {
    switch (status) {
      case 'Present': return 'P';
      case 'Absent': return 'A';
      case 'Leave': return 'L';
      case 'Holiday': return 'H';
      case 'Week Off': return 'WO';
      case 'LOP': return 'LOP';
      default: return '-';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Attendance Monitor</h1>
          <p className="text-neutral-500 mt-1">Review finalized attendance and leave balances</p>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
            className="p-2 hover:bg-neutral-100 rounded-full transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-neutral-600" />
          </button>
          <span className="text-lg font-semibold text-neutral-800 w-32 text-center">
            {format(currentMonth, 'MMMM yyyy')}
          </span>
          <button 
            onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
            className="p-2 hover:bg-neutral-100 rounded-full transition-colors"
          >
            <ChevronRight className="w-5 h-5 text-neutral-600" />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-xl flex items-center gap-3">
          <AlertCircle className="w-5 h-5" />
          <p>{error}</p>
        </div>
      )}

      <GlassCard className="overflow-hidden p-0 relative">
        {loading && (
          <div className="absolute inset-0 bg-white/50 backdrop-blur-sm z-10 flex items-center justify-center">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          </div>
        )}
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left whitespace-nowrap">
            <thead className="text-xs text-neutral-500 uppercase bg-neutral-50 sticky top-0 z-20">
              <tr>
                <th className="px-4 py-3 font-medium sticky left-0 bg-neutral-50 z-30 shadow-[1px_0_0_0_#e5e7eb]">Employee</th>
                <th className="px-4 py-3 font-medium border-l border-neutral-200">Summary (P/A/L/Late)</th>
                {days.map(day => (
                  <th key={day.toISOString()} className="px-2 py-3 font-medium text-center border-l border-neutral-200 min-w-[40px]">
                    {format(day, 'dd')}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.values(data).map((emp: any) => (
                <tr key={emp.employeeId} className="border-b border-neutral-100 hover:bg-neutral-50/50 transition-colors">
                  <td className="px-4 py-3 sticky left-0 bg-white shadow-[1px_0_0_0_#e5e7eb] z-10 group-hover:bg-neutral-50">
                    <div className="font-medium text-neutral-900">{emp.name}</div>
                    <div className="text-xs text-neutral-500">{emp.employeeCode || emp.employeeId}</div>
                  </td>
                  <td className="px-4 py-3 border-l border-neutral-100 text-neutral-600">
                    <span className="text-green-600 font-medium">{emp.summary.present}</span> / 
                    <span className="text-red-600 font-medium mx-1">{emp.summary.absent}</span> / 
                    <span className="text-purple-600 font-medium mx-1">{emp.summary.leaveAvailed}</span> / 
                    <span className="text-orange-600 font-medium ml-1">{emp.summary.lateCount}</span>
                  </td>
                  {days.map(day => {
                    const dateStr = format(day, 'yyyy-MM-dd');
                    const att = emp.attendance[dateStr];
                    const status = att?.status || '-';
                    const isLate = att?.isLate || false;
                    
                    return (
                      <td key={dateStr} className="px-1 py-2 border-l border-neutral-100 text-center">
                        <button
                          onClick={() => att && setSelectedCell({ employeeId: emp.employeeId, date: dateStr, details: att, empDetails: emp })}
                          className={`w-full h-8 rounded flex items-center justify-center font-medium text-xs transition-transform hover:scale-105 ${getStatusColor(status, isLate)} ${!att ? 'cursor-default' : 'cursor-pointer'}`}
                          title={att ? `${status} ${isLate ? '(LATE)' : ''}` : 'No Data'}
                        >
                          {getStatusAbbr(status)}
                        </button>
                      </td>
                    );
                  })}
                </tr>
              ))}
              {Object.keys(data).length === 0 && !loading && (
                <tr>
                  <td colSpan={days.length + 2} className="px-4 py-8 text-center text-neutral-500">
                    No finalized attendance data found for this period.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </GlassCard>

      {/* Detail Drawer Modal */}
      {selectedCell && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={() => setSelectedCell(null)} />
          <div className="w-full max-w-md bg-white h-full shadow-2xl relative z-10 animate-in slide-in-from-right duration-300 flex flex-col">
            <div className="p-6 border-b border-neutral-100">
              <h2 className="text-xl font-bold text-neutral-900">Attendance Breakdown</h2>
              <p className="text-neutral-500 mt-1">{format(new Date(selectedCell.date), 'dd MMMM yyyy')}</p>
            </div>
            
            <div className="p-6 flex-1 overflow-y-auto space-y-6">
              <div>
                <h3 className="text-sm font-medium text-neutral-500 uppercase tracking-wider mb-3">Employee</h3>
                <div className="bg-neutral-50 p-4 rounded-xl">
                  <p className="font-semibold text-neutral-900">{selectedCell.empDetails.name}</p>
                  <div className="flex gap-4 mt-2 text-sm text-neutral-600">
                    <p>ID: <span className="font-medium text-neutral-900">{selectedCell.empDetails.employeeId}</span></p>
                    <p>Code: <span className="font-medium text-neutral-900">{selectedCell.empDetails.employeeCode || 'N/A'}</span></p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-neutral-500 uppercase tracking-wider mb-3">Status</h3>
                <div className="bg-neutral-50 p-4 rounded-xl space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-neutral-600">Final Status</span>
                    <span className={`px-2.5 py-1 rounded-md text-xs font-semibold uppercase tracking-wider ${getStatusColor(selectedCell.details.status, false)}`}>
                      {selectedCell.details.status}
                    </span>
                  </div>
                  
                  {selectedCell.details.isLate && (
                    <div className="flex justify-between items-center">
                      <span className="text-neutral-600">Late Information</span>
                      <span className="flex items-center gap-1 text-orange-600 font-medium bg-orange-50 px-2 py-1 rounded">
                        <Clock className="w-4 h-4" />
                        Late by {selectedCell.details.lateMinutes} mins
                      </span>
                    </div>
                  )}

                  {selectedCell.details.leaveType && (
                    <div className="flex justify-between items-center">
                      <span className="text-neutral-600">Leave Type</span>
                      <span className="font-medium text-neutral-900">{selectedCell.details.leaveType}</span>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-neutral-500 uppercase tracking-wider mb-3">Shift & Punches</h3>
                <div className="bg-neutral-50 p-4 rounded-xl space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-neutral-600">Shift</span>
                    <span className="font-medium text-neutral-900">{selectedCell.details.shiftCode || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-neutral-600">Schedule Type</span>
                    <span className="font-medium text-neutral-900">{selectedCell.details.scheduleType || 'WORKING'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-neutral-600">Shift Times</span>
                    <span className="font-medium text-neutral-900">
                      {selectedCell.details.actualStartTime || '-'} to {selectedCell.details.actualEndTime || '-'}
                    </span>
                  </div>
                  <div className="border-t border-neutral-200 my-2 pt-2"></div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-neutral-600 font-medium">IN</span>
                    <span className="font-mono bg-white px-2 py-1 rounded border border-neutral-200">
                      {selectedCell.details.inTime ? format(new Date(selectedCell.details.inTime), 'HH:mm:ss') : 'Missing'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-neutral-600 font-medium">OUT</span>
                    <span className="font-mono bg-white px-2 py-1 rounded border border-neutral-200">
                      {selectedCell.details.outTime ? format(new Date(selectedCell.details.outTime), 'HH:mm:ss') : 'Missing'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="p-4 border-t border-neutral-100 flex justify-end">
              <button 
                onClick={() => setSelectedCell(null)}
                className="px-4 py-2 bg-neutral-100 text-neutral-700 rounded-lg hover:bg-neutral-200 font-medium transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default AdminAttendanceMonitor;
