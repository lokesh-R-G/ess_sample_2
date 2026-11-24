import React, { useState, useEffect } from 'react';
import { GlassCard } from '../../../components/ui';
import { api } from '../../../lib/api';
import { format, startOfMonth, endOfMonth, addMonths, subMonths } from 'date-fns';
import { ChevronLeft, ChevronRight, AlertCircle, Clock, Smartphone, Download, FileText, Loader2 } from 'lucide-react';
import { AdminPunchDetailMap } from '../../../components/attendance/AdminPunchDetailMap';
import { downloadMasterAttendancePdf, downloadEmployeeAttendancePdf } from '../../../services/attendanceService';

export const AdminAttendanceMonitor: React.FC = () => {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [data, setData] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [exportingMaster, setExportingMaster] = useState(false);
  const [exportingEmpId, setExportingEmpId] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);

  const [selectedCell, setSelectedCell] = useState<{employeeId: string, date: string, details: any, empDetails: any} | null>(null);
  const [manualStatus, setManualStatus] = useState('PRESENT');
  const [manualLopHours, setManualLopHours] = useState('');
  const [manualHalf, setManualHalf] = useState('Full Day');
  const [savingManual, setSavingManual] = useState(false);

  useEffect(() => {
    if (selectedCell) {
      const current = selectedCell.details.status?.toUpperCase() || 'PRESENT';
      setManualStatus(current === 'LOP' ? 'LOP' : current === 'ABSENT' ? 'ABSENT' : 'PRESENT');
      setManualLopHours(selectedCell.details.lopHours?.toString() || '');
      setManualHalf('Full Day');
    }
  }, [selectedCell]);

  const handleSaveManual = async () => {
    if (!selectedCell) return;
    try {
      setSavingManual(true);
      const payload: any = { status: manualStatus };
      if (manualStatus === 'LOP') {
        payload.lopHours = parseFloat(manualLopHours);
      } else if (manualHalf !== 'Full Day') {
        payload.half = manualHalf;
      }
      await api.patch(`/v2/attendance/monitor/${selectedCell.employeeId}/${selectedCell.date}/manual`, payload);
      await fetchData();
      setSelectedCell(null); // Close modal
    } catch (err: any) {
      alert(err.message || 'Failed to save manual attendance');
    } finally {
      setSavingManual(false);
    }
  };

  const triggerDownload = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleExportMaster = async () => {
    if (exportingMaster) return;
    setExportingMaster(true);
    setExportError(null);
    try {
      const from = format(startOfMonth(currentMonth), 'yyyy-MM-dd');
      const to = format(endOfMonth(currentMonth), 'yyyy-MM-dd');
      const { blob, filename } = await downloadMasterAttendancePdf(from, to);
      triggerDownload(blob, filename);
    } catch (err: any) {
      console.error('Master export failed:', err);
      setExportError(err.message || 'Failed to generate Master Attendance PDF');
    } finally {
      setExportingMaster(false);
    }
  };

  const handleExportEmployee = async (e: React.MouseEvent, emp: any) => {
    e.stopPropagation();
    const empId = emp.employeeId || emp.employeeCode;
    if (exportingEmpId) return;
    setExportingEmpId(empId);
    setExportError(null);
    try {
      const from = format(startOfMonth(currentMonth), 'yyyy-MM-dd');
      const to = format(endOfMonth(currentMonth), 'yyyy-MM-dd');
      const { blob, filename } = await downloadEmployeeAttendancePdf(empId, from, to);
      triggerDownload(blob, filename);
    } catch (err: any) {
      console.error(`Export failed for employee ${empId}:`, err);
      setExportError(err.message || `Failed to generate PDF for ${emp.name || empId}`);
    } finally {
      setExportingEmpId(null);
    }
  };


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

  const getStatusColor = (status: string, isLate: boolean = false) => {
    switch (status) {
      case 'Present': return 'bg-green-100 text-green-800 border border-green-200';
      case 'Half Day': return 'bg-yellow-100 text-yellow-800 border border-yellow-300';
      case 'On Duty': return 'bg-yellow-100 text-yellow-800';
      case 'Absent': return 'bg-red-100 text-red-800';
      case 'Leave': return 'bg-purple-100 text-purple-800';
      case 'Holiday': return 'bg-blue-100 text-blue-800';
      case 'Week Off': return 'bg-gray-100 text-gray-800';
      case 'LOP': return 'bg-rose-100 text-rose-800';
      case 'PRESENT': return 'bg-green-100 text-green-800 border border-green-200';
      case 'ABSENT': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-50 text-gray-400';
    }
  };

  const formatLeaveTypeAbbr = (leaveType?: string) => {
    if (!leaveType) return 'L';
    const clean = leaveType.replace(/_TEST$/i, '').trim();
    return clean || 'L';
  };

  const getStatusAbbr = (status: string, leaveType?: string) => {
    switch (status) {
      case 'Present': return 'P';
      case 'Half Day': return 'HD';
      case 'Absent': return 'A';
      case 'Leave': return formatLeaveTypeAbbr(leaveType);
      case 'Holiday': return 'H';
      case 'Week Off': return 'WO';
      case 'LOP': return 'LOP';
      case 'PRESENT': return 'MP';
      case 'ABSENT': return 'MA';
      case 'On Duty': return 'OD';
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
          <div className="flex items-center bg-white border border-neutral-200 rounded-xl p-1 shadow-sm">
            <button 
              onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
              className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
              title="Previous Month"
            >
              <ChevronLeft className="w-5 h-5 text-neutral-600" />
            </button>
            <span className="text-base font-semibold text-neutral-800 w-36 text-center select-none">
              {format(currentMonth, 'MMMM yyyy')}
            </span>
            <button 
              onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
              className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
              title="Next Month"
            >
              <ChevronRight className="w-5 h-5 text-neutral-600" />
            </button>
          </div>

          <button
            onClick={handleExportMaster}
            disabled={exportingMaster || loading}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all shadow-sm ${
              exportingMaster || loading
                ? 'bg-neutral-100 text-neutral-400 border border-neutral-200 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95 shadow-blue-500/10'
            }`}
            title="Export consolidated monthly attendance report for all authorized employees"
          >
            {exportingMaster ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                <span>Exporting...</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>Master Export</span>
              </>
            )}
          </button>
        </div>
      </div>

      {exportError && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl flex items-center justify-between gap-3 animate-in fade-in">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
            <p className="text-sm font-medium">{exportError}</p>
          </div>
          <button 
            onClick={() => setExportError(null)}
            className="text-xs text-rose-600 hover:text-rose-800 font-semibold px-2 py-1 rounded hover:bg-rose-100"
          >
            Dismiss
          </button>
        </div>
      )}

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
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="font-medium text-neutral-900">{emp.name}</div>
                        <div className="text-xs text-neutral-500">{emp.employeeCode || emp.employeeId}</div>
                      </div>
                      <button
                        onClick={(e) => handleExportEmployee(e, emp)}
                        disabled={exportingEmpId === (emp.employeeId || emp.employeeCode)}
                        className="p-1.5 rounded-lg text-neutral-400 hover:text-blue-600 hover:bg-blue-50 transition-colors border border-transparent hover:border-blue-200"
                        title={`Export monthly attendance report for ${emp.name}`}
                      >
                        {exportingEmpId === (emp.employeeId || emp.employeeCode) ? (
                          <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                        ) : (
                          <FileText className="w-4 h-4" />
                        )}
                      </button>
                    </div>
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
                      <td key={dateStr} className="px-1 py-2 border-l border-neutral-100 text-center relative">
                        <button
                          onClick={() => att && setSelectedCell({ employeeId: emp.employeeId, date: dateStr, details: att, empDetails: emp })}
                          className={`w-full h-8 rounded flex items-center justify-center font-medium text-xs transition-transform hover:scale-105 relative ${getStatusColor(status, isLate)} ${!att ? 'cursor-default' : 'cursor-pointer'}`}
                          title={att ? `${status === 'Leave' && att?.leaveType ? `Leave (${att.leaveType})` : status} ${isLate ? `(LATE: ${att.lateMinutes}m)` : ''}` : 'No Data'}
                        >
                          {getStatusAbbr(status, att?.leaveType)}
                          {isLate && (
                            <span 
                              className="absolute top-0.5 right-0.5 w-2 h-2 rounded-full bg-orange-500 ring-1 ring-white" 
                              title={`Late by ${att?.lateMinutes || 0} mins`} 
                            />
                          )}
                        </button>
                        {att?.sources?.includes('MOBILE') && (
                          <div className="absolute -top-1 -right-1 bg-white rounded-full p-0.5 shadow-sm border border-neutral-200">
                            <Smartphone className="w-3 h-3 text-blue-600" />
                          </div>
                        )}
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
                <div className="bg-neutral-50 p-4 rounded-xl space-y-3 mb-6">
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

                <h3 className="text-sm font-medium text-neutral-500 uppercase tracking-wider mb-3">Raw Punches</h3>
                <AdminPunchDetailMap 
                  empCode={selectedCell.empDetails.employeeCode || selectedCell.empDetails.employeeId} 
                  date={selectedCell.date} 
                  companyId={selectedCell.empDetails.companyId}
                />
              </div>
            </div>
            
            <div className="p-6 border-t border-neutral-100 bg-neutral-50 flex flex-col gap-4">
              <div>
                <h3 className="text-sm font-bold text-neutral-900 mb-2">Manual Correction (Admin)</h3>
                <div className="flex gap-2 mb-3">
                  <select 
                    value={manualStatus} 
                    onChange={e => setManualStatus(e.target.value)}
                    className="border border-neutral-300 rounded px-3 py-2 text-sm bg-white flex-1"
                  >
                    <option value="PRESENT">PRESENT</option>
                    <option value="ABSENT">ABSENT</option>
                    <option value="LOP">LOP</option>
                  </select>
                  {manualStatus === 'LOP' && (
                    <input 
                      type="number" 
                      min="0" step="0.5"
                      placeholder="LOP Hrs" 
                      value={manualLopHours}
                      onChange={e => setManualLopHours(e.target.value)}
                      className="border border-neutral-300 rounded px-3 py-2 text-sm bg-white w-24"
                    />
                  )}
                  {manualStatus !== 'LOP' && (
                    <select
                      value={manualHalf}
                      onChange={e => setManualHalf(e.target.value)}
                      className="border border-neutral-300 rounded px-3 py-2 text-sm bg-white flex-1"
                    >
                      <option value="Full Day">Full Day</option>
                      <option value="First Half">First Half</option>
                      <option value="Second Half">Second Half</option>
                    </select>
                  )}
                </div>
              </div>
              <div className="flex justify-end gap-3">
                <button 
                  onClick={() => setSelectedCell(null)}
                  className="px-4 py-2 bg-neutral-200 text-neutral-700 rounded-lg hover:bg-neutral-300 font-medium transition-colors"
                >
                  Close
                </button>
                <button 
                  onClick={handleSaveManual}
                  disabled={savingManual}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors flex items-center"
                >
                  {savingManual ? 'Saving...' : 'Save Manual'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default AdminAttendanceMonitor;
