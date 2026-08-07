import React, { useState, useEffect } from 'react';
import { GlassCard, AnimatedButton, Input, Select, StatusBadge } from '../../../components/ui';
import { organizationApi } from '../../../services/organization.api';
import { employeeApi } from '../../../services/employeeApi';
import { recalculateAttendance, RecalculateRequestPayload, RecalculateResponse } from '../../../services/attendanceService';
import { toast } from 'react-hot-toast';
import { Calendar, RefreshCcw, Activity, CheckCircle, AlertTriangle } from 'lucide-react';
import { format, subDays, startOfMonth, subMonths, endOfMonth } from 'date-fns';

export default function ManualRecalculation() {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<RecalculateRequestPayload>({
    fromDate: format(subDays(new Date(), 7), 'yyyy-MM-dd'),
    toDate: format(new Date(), 'yyyy-MM-dd'),
    force: true
  });
  
  const [result, setResult] = useState<RecalculateResponse | null>(null);



  const handleShortcut = (shortcut: string) => {
    const today = new Date();
    let from = today;
    let to = today;

    switch (shortcut) {
      case 'today':
        break;
      case 'yesterday':
        from = subDays(today, 1);
        to = subDays(today, 1);
        break;
      case 'last7':
        from = subDays(today, 7);
        break;
      case 'last30':
        from = subDays(today, 30);
        break;
      case 'currentMonth':
        from = startOfMonth(today);
        to = endOfMonth(today);
        break;
      case 'previousMonth':
        const prev = subMonths(today, 1);
        from = startOfMonth(prev);
        to = endOfMonth(prev);
        break;
    }
    
    setFormData(prev => ({
      ...prev,
      fromDate: format(from, 'yyyy-MM-dd'),
      toDate: format(to, 'yyyy-MM-dd')
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.fromDate > formData.toDate) {
      toast.error('From Date cannot be after To Date');
      return;
    }
    
    setLoading(true);
    setResult(null);
    try {
      // Clean payload
      const payload: RecalculateRequestPayload = {
        fromDate: formData.fromDate,
        toDate: formData.toDate,
        force: formData.force
      };
      
      const res = await recalculateAttendance(payload);
      const data = res?.data || res;
      setResult(data as RecalculateResponse);
      
      if (data.success) {
        toast.success('Recalculation completed successfully!');
      } else {
        toast.error('Recalculation completed with errors.');
      }
      
    } catch (error: any) {
      toast.error(error.message || 'Failed to recalculate attendance');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 flex items-center gap-2">
            <RefreshCcw className="w-6 h-6 text-brand-600" />
            Manual Attendance Recalculation (V2)
          </h1>
          <p className="text-neutral-500 mt-1">Orchestrate the V2 Attendance Engine over a specific period</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassCard className="p-6 lg:col-span-2">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="bg-blue-50 text-blue-800 p-4 rounded-lg flex items-start gap-3 border border-blue-100">
              <Calendar className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <div className="text-sm">
                <p className="font-semibold mb-1">Quick Actions</p>
                <div className="flex flex-wrap gap-2 mt-2">
                  <button type="button" onClick={() => handleShortcut('today')} className="px-3 py-1 bg-white border border-blue-200 rounded-md hover:bg-blue-100 transition-colors">Today</button>
                  <button type="button" onClick={() => handleShortcut('yesterday')} className="px-3 py-1 bg-white border border-blue-200 rounded-md hover:bg-blue-100 transition-colors">Yesterday</button>
                  <button type="button" onClick={() => handleShortcut('last7')} className="px-3 py-1 bg-white border border-blue-200 rounded-md hover:bg-blue-100 transition-colors">Last 7 Days</button>
                  <button type="button" onClick={() => handleShortcut('last30')} className="px-3 py-1 bg-white border border-blue-200 rounded-md hover:bg-blue-100 transition-colors">Last 30 Days</button>
                  <button type="button" onClick={() => handleShortcut('currentMonth')} className="px-3 py-1 bg-white border border-blue-200 rounded-md hover:bg-blue-100 transition-colors">Current Month</button>
                  <button type="button" onClick={() => handleShortcut('previousMonth')} className="px-3 py-1 bg-white border border-blue-200 rounded-md hover:bg-blue-100 transition-colors">Previous Month</button>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="From Date"
                type="date"
                required
                value={formData.fromDate}
                onChange={(e) => setFormData({...formData, fromDate: e.target.value})}
              />
              <Input
                label="To Date"
                type="date"
                required
                value={formData.toDate}
                onChange={(e) => setFormData({...formData, toDate: e.target.value})}
              />
            </div>
            
            <div className="flex items-center gap-3 p-4 bg-neutral-50 rounded-lg border border-neutral-200">
              <input 
                type="checkbox" 
                id="forceMode"
                checked={formData.force}
                onChange={(e) => setFormData({...formData, force: e.target.checked})}
                className="w-5 h-5 text-brand-600 rounded border-neutral-300 focus:ring-brand-500"
              />
              <div>
                <label htmlFor="forceMode" className="font-semibold text-neutral-900 block cursor-pointer">
                  Force Recalculation
                </label>
                <p className="text-xs text-neutral-500 mt-0.5">
                  If checked, existing snapshots will be overwritten. If unchecked, only missing dates will be processed.
                </p>
              </div>
            </div>

            <div className="flex justify-end pt-4 border-t border-neutral-100">
              <AnimatedButton 
                type="submit"
                disabled={loading}
                className="w-full md:w-auto px-8"
              >
                {loading ? 'Recalculating...' : 'Trigger Recalculation Pipeline'}
              </AnimatedButton>
            </div>
          </form>
        </GlassCard>

        <div className="space-y-6">
          <GlassCard className="p-6 bg-gradient-to-br from-neutral-900 to-neutral-800 text-white">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-white/10 rounded-lg">
                <Activity className="w-5 h-5 text-brand-300" />
              </div>
              <h3 className="font-semibold text-lg">Execution Engine</h3>
            </div>
            <p className="text-sm text-neutral-300 mb-6">
              This API uses the canonical V2 Pipeline:
              <br/><br/>
              <span className="font-mono bg-black/30 px-2 py-1 rounded text-xs">AttendanceProcessor</span><br/>
              <span className="text-neutral-500 ml-4">↓</span><br/>
              <span className="font-mono bg-black/30 px-2 py-1 rounded text-xs">AttendanceContextResolver</span><br/>
              <span className="text-neutral-500 ml-4">↓</span><br/>
              <span className="font-mono bg-black/30 px-2 py-1 rounded text-xs">PolicyEngine</span><br/>
              <span className="text-neutral-500 ml-4">↓</span><br/>
              <span className="font-mono bg-black/30 px-2 py-1 rounded text-xs">MongoDB Snapshot</span>
            </p>
          </GlassCard>
          
          {result && (
            <GlassCard className="p-6 border-l-4 border-l-brand-500">
              <h3 className="font-bold text-neutral-900 mb-4 flex items-center gap-2">
                {result.success ? <CheckCircle className="text-green-500 w-5 h-5" /> : <AlertTriangle className="text-amber-500 w-5 h-5" />}
                Processing Summary
              </h3>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-neutral-50 p-3 rounded-lg">
                  <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Duration</p>
                  <p className="text-lg font-semibold text-neutral-900">{result.durationMs} ms</p>
                </div>
                <div className="bg-neutral-50 p-3 rounded-lg">
                  <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Engine</p>
                  <p className="text-lg font-semibold text-neutral-900 uppercase">{result.engineVersion}</p>
                </div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between py-2 border-b border-neutral-100">
                  <span className="text-neutral-600">Employees Processed</span>
                  <span className="font-semibold">{result.employeesProcessed}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-neutral-100">
                  <span className="text-neutral-600">Total Days Analyzed</span>
                  <span className="font-semibold">{result.daysProcessed}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-neutral-100">
                  <span className="text-neutral-600">Records Created</span>
                  <span className="font-semibold text-green-600">{result.attendanceRecordsCreated}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-neutral-100">
                  <span className="text-neutral-600">Records Updated</span>
                  <span className="font-semibold text-blue-600">{result.attendanceRecordsUpdated}</span>
                </div>
              </div>
              
              {result.errors && result.errors.length > 0 && (
                <div className="mt-4 p-3 bg-red-50 border border-red-100 rounded-lg text-sm text-red-800">
                  <p className="font-semibold mb-2">Errors encountered:</p>
                  <ul className="list-disc pl-4 space-y-1">
                    {result.errors.map((err, i) => (
                      <li key={i}>Emp {err.employeeId}: {err.error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </GlassCard>
          )}
        </div>
      </div>
    </div>
  );
}
