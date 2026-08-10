import React, { useState, useEffect } from 'react';
import { GlassCard, AnimatedButton } from '../../components/ui';
import { api } from '../../lib/api';
import { AlertCircle, Calendar, RefreshCw, Settings, CheckCircle2, Clock, Play, Save } from 'lucide-react';
import { format, subDays } from 'date-fns';

export const AdminAttendance: React.FC = () => {
  const [fromDate, setFromDate] = useState(format(subDays(new Date(), 7), 'yyyy-MM-dd'));
  const [toDate, setToDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  
  const [syncing, setSyncing] = useState(false);
  const [recalculating, setRecalculating] = useState(false);
  const [combining, setCombining] = useState(false);
  const [savingConfig, setSavingConfig] = useState(false);
  const [loadingConfig, setLoadingConfig] = useState(true);
  
  const [syncResult, setSyncResult] = useState<any>(null);
  const [recalcResult, setRecalcResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  const [schedulerConfigs, setSchedulerConfigs] = useState<any[]>([]);
  const [configSuccess, setConfigSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetchSchedulerConfigs();
  }, []);

  const fetchSchedulerConfigs = async () => {
    setLoadingConfig(true);
    try {
      const data = await api.get<any[]>('/v2/scheduler/config');
      setSchedulerConfigs(data || []);
    } catch (e: any) {
      console.error("Failed to load scheduler configs", e);
    } finally {
      setLoadingConfig(false);
    }
  };

  const handleConfigChange = (jobKey: string, field: string, value: any) => {
    setSchedulerConfigs(configs => configs.map(c => 
      c.jobKey === jobKey ? { ...c, [field]: value } : c
    ));
  };

  const saveConfig = async (jobKey: string) => {
    setSavingConfig(true);
    setConfigSuccess(null);
    setError(null);
    
    const config = schedulerConfigs.find(c => c.jobKey === jobKey);
    if (!config) return;

    try {
      await api.put(`/v2/scheduler/config/${jobKey}`, {
        enabled: config.enabled,
        frequencyMinutes: Number(config.frequencyMinutes),
        lookbackDays: Number(config.lookbackDays)
      });
      setConfigSuccess(`${jobKey} configuration saved successfully!`);
      await fetchSchedulerConfigs(); // reload from backend to confirm
    } catch (e: any) {
      setError(`Failed to save configuration: ${e.message}`);
    } finally {
      setSavingConfig(false);
      setTimeout(() => setConfigSuccess(null), 3000);
    }
  };

  const handleSync = async () => {
    if (syncing || recalculating || combining) return;
    setSyncing(true);
    setSyncResult(null);
    setRecalcResult(null);
    setError(null);
    
    try {
      const res = await api.post<any>('/v1/sync/essl/', { fromDate, toDate });
      setSyncResult(res);
    } catch (e: any) {
      setError(`Sync failed: ${e.message}`);
    } finally {
      setSyncing(false);
    }
  };

  const handleRecalculate = async () => {
    if (syncing || recalculating || combining) return;
    setRecalculating(true);
    setSyncResult(null);
    setRecalcResult(null);
    setError(null);
    
    try {
      const res = await api.post<any>('/v2/attendance/attendance/recalculate', { fromDate, toDate, force: true });
      setRecalcResult(res);
    } catch (e: any) {
      setError(`Recalculation failed: ${e.message}`);
    } finally {
      setRecalculating(false);
    }
  };

  const handleCombined = async () => {
    if (syncing || recalculating || combining) return;
    setCombining(true);
    setSyncResult(null);
    setRecalcResult(null);
    setError(null);
    
    try {
      // Step 1: Sync
      const sRes = await api.post<any>('/v1/sync/essl/', { fromDate, toDate });
      setSyncResult(sRes);
      
      // Step 2: Recalculate
      const rRes = await api.post<any>('/v2/attendance/attendance/recalculate', { fromDate, toDate, force: true });
      setRecalcResult(rRes);
    } catch (e: any) {
      setError(`Combined operation failed: ${e.message}`);
    } finally {
      setCombining(false);
    }
  };

  const renderConfigRow = (jobKey: string, title: string, description: string) => {
    const config = schedulerConfigs.find(c => c.jobKey === jobKey);
    if (!config) return null;

    return (
      <div key={jobKey} className="flex flex-col md:flex-row md:items-center justify-between p-4 rounded-lg border border-neutral-200 bg-neutral-50/50 gap-4">
        <div className="flex-1">
          <h4 className="font-medium text-neutral-900">{title}</h4>
          <p className="text-sm text-neutral-500 mb-2">{description}</p>
          <div className="flex items-center gap-2 text-xs text-neutral-400">
            <span>Last Updated: {config.updatedAt ? new Date(config.updatedAt).toLocaleString() : 'Never'}</span>
          </div>
        </div>
        
        <div className="flex flex-wrap items-end gap-3 flex-1 md:justify-end">
          <div className="flex flex-col">
            <label className="text-xs font-medium text-neutral-600 mb-1">Enabled</label>
            <select 
              value={config.enabled ? 'true' : 'false'} 
              onChange={(e) => handleConfigChange(jobKey, 'enabled', e.target.value === 'true')}
              className="px-2 py-1.5 text-sm border border-neutral-300 rounded focus:ring-blue-500 focus:border-blue-500 bg-white"
            >
              <option value="true">ON</option>
              <option value="false">OFF</option>
            </select>
          </div>
          <div className="flex flex-col w-24">
            <label className="text-xs font-medium text-neutral-600 mb-1">Freq (mins)</label>
            <input 
              type="number" 
              min="1"
              value={config.frequencyMinutes}
              onChange={(e) => handleConfigChange(jobKey, 'frequencyMinutes', e.target.value)}
              className="px-2 py-1.5 text-sm border border-neutral-300 rounded focus:ring-blue-500 focus:border-blue-500 w-full"
            />
          </div>
          <div className="flex flex-col w-24">
            <label className="text-xs font-medium text-neutral-600 mb-1">Lookback (days)</label>
            <input 
              type="number" 
              min="0"
              value={config.lookbackDays}
              onChange={(e) => handleConfigChange(jobKey, 'lookbackDays', e.target.value)}
              className="px-2 py-1.5 text-sm border border-neutral-300 rounded focus:ring-blue-500 focus:border-blue-500 w-full"
            />
          </div>
          <button
            onClick={() => saveConfig(jobKey)}
            disabled={savingConfig}
            className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded transition-colors"
          >
            <Save className="w-4 h-4" /> Save
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold text-neutral-900">Attendance Operations Hub</h2>
          <p className="text-neutral-500 mt-1">Manage eSSL syncs, trigger V2 attendance recalculations, and configure automation.</p>
        </div>
      </div>

      <GlassCard className="p-6 border-blue-100 bg-blue-50/30">
        <div className="flex items-center gap-2 mb-4 text-blue-800">
          <Calendar className="w-5 h-5" />
          <h3 className="font-semibold text-lg">Target Date Range</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">From Date</label>
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="w-full px-3 py-2 bg-white border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">To Date</label>
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="w-full px-3 py-2 bg-white border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </GlassCard>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Manual eSSL Sync */}
        <GlassCard className="p-6 flex flex-col h-full">
          <div className="flex items-center gap-2 mb-2 text-neutral-900">
            <RefreshCw className="w-5 h-5 text-emerald-600" />
            <h3 className="font-semibold">Manual eSSL Sync</h3>
          </div>
          <p className="text-sm text-neutral-500 mb-6 flex-grow">
            Pull raw device logs directly from the biometric system for all employees.
          </p>
          <AnimatedButton onClick={handleSync} loading={syncing} disabled={recalculating || combining} className="w-full bg-emerald-600 hover:bg-emerald-700 text-white">
            <div className="flex items-center justify-center gap-2">
              <RefreshCw className="w-4 h-4" />
              Sync eSSL
            </div>
          </AnimatedButton>
        </GlassCard>

        {/* Manual Recalculate */}
        <GlassCard className="p-6 flex flex-col h-full">
          <div className="flex items-center gap-2 mb-2 text-neutral-900">
            <Play className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold">Recalculate Attendance</h3>
          </div>
          <p className="text-sm text-neutral-500 mb-6 flex-grow">
            Trigger the V2 Attendance Engine to rebuild snapshots for all active employees.
          </p>
          <AnimatedButton onClick={handleRecalculate} loading={recalculating} disabled={syncing || combining} className="w-full">
            <div className="flex items-center justify-center gap-2">
              <Play className="w-4 h-4" />
              Recalculate Attendance
            </div>
          </AnimatedButton>
        </GlassCard>

        {/* Combined */}
        <GlassCard className="p-6 flex flex-col h-full bg-gradient-to-br from-indigo-50 to-purple-50 border-indigo-100">
          <div className="flex items-center gap-2 mb-2 text-indigo-900">
            <Clock className="w-5 h-5 text-indigo-600" />
            <h3 className="font-semibold">Combined Operation</h3>
          </div>
          <p className="text-sm text-indigo-700/70 mb-6 flex-grow">
            Execute a full sync immediately followed by a complete V2 recalculation.
          </p>
          <AnimatedButton onClick={handleCombined} loading={combining} disabled={syncing || recalculating} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white">
            <div className="flex items-center justify-center gap-2">
              <Clock className="w-4 h-4" />
              Sync & Recalculate
            </div>
          </AnimatedButton>
        </GlassCard>
      </div>

      {/* Results Section */}
      {(error || syncResult || recalcResult || configSuccess) && (
        <GlassCard className="p-6">
          <h3 className="font-semibold text-lg mb-4 text-neutral-900">Execution Results</h3>
          
          {error && (
            <div className="mb-4 p-4 rounded-lg bg-red-50 text-red-700 flex gap-3 items-start border border-red-100">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">Operation Failed</p>
                <p className="text-sm opacity-90">{error}</p>
              </div>
            </div>
          )}
          
          {configSuccess && (
            <div className="mb-4 p-4 rounded-lg bg-emerald-50 text-emerald-700 flex gap-3 items-start border border-emerald-100">
              <CheckCircle2 className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">{configSuccess}</p>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {syncResult && (
              <div className="p-4 rounded-lg bg-emerald-50 border border-emerald-100">
                <div className="flex items-center gap-2 text-emerald-800 font-semibold mb-3">
                  <CheckCircle2 className="w-5 h-5" />
                  eSSL Sync Completed
                </div>
                <div className="space-y-2 text-sm text-emerald-900/80">
                  <div className="flex justify-between">
                    <span>Date Range</span>
                    <span className="font-medium">{syncResult.dateRange?.fromDate?.split('T')[0]} to {syncResult.dateRange?.toDate?.split('T')[0]}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Raw Logs Inserted</span>
                    <span className="font-medium">{syncResult.rawInserted || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Raw Logs Updated</span>
                    <span className="font-medium">{syncResult.rawUpdated || 0}</span>
                  </div>
                </div>
              </div>
            )}

            {recalcResult && (
              <div className="p-4 rounded-lg bg-blue-50 border border-blue-100">
                <div className="flex items-center gap-2 text-blue-800 font-semibold mb-3">
                  {recalcResult.success ? <CheckCircle2 className="w-5 h-5" /> : <AlertCircle className="w-5 h-5 text-amber-600" />}
                  V2 Recalculation {recalcResult.success ? 'Completed' : 'Completed with Errors'}
                </div>
                <div className="space-y-2 text-sm text-blue-900/80">
                  <div className="flex justify-between">
                    <span>Date Range</span>
                    <span className="font-medium">{recalcResult.fromDate} to {recalcResult.toDate}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Employees Processed</span>
                    <span className="font-medium">{recalcResult.employeesProcessed || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Days Evaluated</span>
                    <span className="font-medium">{recalcResult.daysProcessed || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Snapshots Created</span>
                    <span className="font-medium">{recalcResult.attendanceRecordsCreated || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Snapshots Updated</span>
                    <span className="font-medium">{recalcResult.attendanceRecordsUpdated || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Engine Version</span>
                    <span className="font-medium uppercase">{recalcResult.engineVersion}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Duration</span>
                    <span className="font-medium">{recalcResult.durationMs} ms</span>
                  </div>
                </div>
                
                {recalcResult.errors && recalcResult.errors.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-blue-200">
                    <p className="text-xs font-semibold text-red-700 mb-2">Encountered Errors ({recalcResult.errors.length}):</p>
                    <div className="max-h-32 overflow-y-auto space-y-1">
                      {recalcResult.errors.map((err: any, idx: number) => (
                        <div key={idx} className="text-xs text-red-600 bg-red-50 p-1.5 rounded">
                          [{err.employeeCode}] {err.error}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </GlassCard>
      )}

      {/* Scheduler UI Real Implementation */}
      <GlassCard className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2 text-neutral-900">
            <Settings className="w-5 h-5" />
            <h3 className="font-semibold text-lg">Automation / Scheduler Configuration</h3>
          </div>
          <button 
            onClick={fetchSchedulerConfigs}
            disabled={loadingConfig}
            className="text-sm flex items-center gap-1 text-blue-600 hover:text-blue-800"
          >
            <RefreshCw className={`w-4 h-4 ${loadingConfig ? 'animate-spin' : ''}`} /> Reload
          </button>
        </div>

        {loadingConfig && schedulerConfigs.length === 0 ? (
          <div className="text-sm text-neutral-500 py-4">Loading configurations from backend...</div>
        ) : (
          <div className="space-y-4">
            {renderConfigRow('ESSL_SHORT_SYNC', 'eSSL Short Sync', 'Syncs recent logs automatically.')}
            {renderConfigRow('ESSL_RECOVERY_SYNC', 'eSSL Recovery Sync', 'Deep sync for missed transactions over a longer period.')}
            {renderConfigRow('ATTENDANCE_CALCULATION', 'Attendance Calculation Job', 'Background task for evaluating new syncs and dirty queues via V2.')}
          </div>
        )}
      </GlassCard>
    </div>
  );
};

export default AdminAttendance;
