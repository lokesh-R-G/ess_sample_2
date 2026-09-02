import React, { useState, useEffect } from 'react';
import { GlassCard, AnimatedButton, Input, StatusBadge } from '../../../components/ui';
import { api } from '../../../lib/api';

interface CorrectionLog {
  id: string;
  correctionCode: string;
  entityType: string;
  entityCode: string;
  originalVersion: number;
  correctionVersion: number;
  effectiveFrom: string;
  effectiveTo?: string;
  reason: string;
  createdAt: string;
}

export default function HistoricalCorrections() {
  const [logs, setLogs] = useState<CorrectionLog[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedEntityType, setSelectedEntityType] = useState('AttendancePolicy');
  const [entityCode, setEntityCode] = useState('');
  const [originalVersion, setOriginalVersion] = useState(1);
  const [changedFieldsJson, setChangedFieldsJson] = useState('{\n  "graceInMinutes": 15\n}');
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await api.get<{ data: CorrectionLog[] }>('/v2/attendance/correction-logs/');
      setLogs(data.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      let changedFields = {};
      try {
        changedFields = JSON.parse(changedFieldsJson);
      } catch (e) {
        alert("Invalid JSON for changed fields");
        return;
      }
      
      const payload = {
        entityType: selectedEntityType,
        entityCode,
        originalVersion: parseInt(originalVersion.toString(), 10),
        effectiveFrom: new Date().toISOString(), // In a real system, query the original version for its dates or let user pick if allowed
        changedFields,
        reason
      };

      await api.post<CorrectionLog>('/v2/attendance/correction-logs/apply', payload);
      alert('Correction applied successfully and recalculation queued.');
      setIsModalOpen(false);
      fetchLogs();
    } catch (error) {
      console.error(error);
      alert('An error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Historical Corrections</h2>
          <p className="text-muted-foreground">Manage and view historical configuration corrections.</p>
        </div>
        <AnimatedButton onClick={() => setIsModalOpen(true)}>New Correction</AnimatedButton>
      </div>

      <GlassCard className="p-6">
        <h3 className="text-lg font-semibold mb-4">Correction Logs</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b">
                <th className="py-2 px-4 font-medium text-sm text-neutral-500">Code</th>
                <th className="py-2 px-4 font-medium text-sm text-neutral-500">Entity</th>
                <th className="py-2 px-4 font-medium text-sm text-neutral-500">Target Code</th>
                <th className="py-2 px-4 font-medium text-sm text-neutral-500">Orig Ver</th>
                <th className="py-2 px-4 font-medium text-sm text-neutral-500">New Ver</th>
                <th className="py-2 px-4 font-medium text-sm text-neutral-500">Reason</th>
                <th className="py-2 px-4 font-medium text-sm text-neutral-500">Date</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="border-b last:border-0 hover:bg-neutral-50">
                  <td className="py-2 px-4 font-mono text-xs">{log.correctionCode}</td>
                  <td className="py-2 px-4"><StatusBadge status="Active" label={log.entityType} /></td>
                  <td className="py-2 px-4 text-sm">{log.entityCode}</td>
                  <td className="py-2 px-4 text-sm">v{log.originalVersion}</td>
                  <td className="py-2 px-4 text-sm">v{log.correctionVersion}</td>
                  <td className="py-2 px-4 text-sm max-w-[200px] truncate">{log.reason}</td>
                  <td className="py-2 px-4 text-sm">{new Date(log.createdAt).toLocaleDateString()}</td>
                </tr>
              ))}
              {logs.length === 0 && !loading && (
                <tr>
                  <td colSpan={7} className="text-center py-6 text-muted-foreground">
                    No historical corrections found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </GlassCard>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-lg overflow-hidden">
            <div className="px-6 py-4 border-b">
              <h3 className="text-lg font-semibold">Apply Historical Correction</h3>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="px-6 py-4 space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Entity Type</label>
                  <select 
                    value={selectedEntityType} 
                    onChange={e => setSelectedEntityType(e.target.value)}
                    className="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm"
                  >
                    <option value="AttendancePolicy">Attendance Policy</option>
                    <option value="WeeklyOffPolicy">Weekly Off Policy</option>
                    <option value="Shift">Shift</option>
                    <option value="HolidayCalendar">Holiday Calendar</option>
                    <option value="Holiday">Holiday</option>
                  </select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Entity Code</label>
                  <Input 
                    value={entityCode} 
                    onChange={e => setEntityCode(e.target.value)} 
                    placeholder="e.g. TESTPOLICY001" 
                    required 
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Original Version to Override</label>
                  <Input 
                    type="number" 
                    value={originalVersion} 
                    onChange={e => setOriginalVersion(parseInt(e.target.value))} 
                    required 
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Changed Fields (JSON)</label>
                  <textarea 
                    className="w-full h-32 rounded-md border border-input bg-transparent px-3 py-2 text-sm"
                    value={changedFieldsJson}
                    onChange={e => setChangedFieldsJson(e.target.value)}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Reason for Correction</label>
                  <Input 
                    value={reason} 
                    onChange={e => setReason(e.target.value)} 
                    placeholder="e.g. Discovered error in past configuration" 
                    required 
                  />
                </div>
              </div>
              
              <div className="px-6 py-4 border-t flex justify-end space-x-2 bg-gray-50">
                <button type="button" className="px-4 py-2 text-sm border rounded-md" onClick={() => setIsModalOpen(false)}>Cancel</button>
                <button type="submit" disabled={submitting} className="px-4 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50">
                  {submitting ? 'Applying...' : 'Apply Correction'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
