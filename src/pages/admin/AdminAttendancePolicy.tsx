import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Settings, Save, Clock, AlertTriangle, Plus, Trash2, Edit2 } from 'lucide-react';
import { GlassCard, AnimatedButton, Input, StatusBadge } from '../../components/ui';
import { AttendancePolicyV2, getAttendancePoliciesV2, createAttendancePolicyV2, updateAttendancePolicyV2, deleteAttendancePolicyV2 } from '../../services/policyService';

export const AdminAttendancePolicy: React.FC = () => {
  const [policies, setPolicies] = useState<AttendancePolicyV2[]>([]);
  const [editingPolicy, setEditingPolicy] = useState<AttendancePolicyV2 | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [selectedCodeHistory, setSelectedCodeHistory] = useState<AttendancePolicyV2[]>([]);

  useEffect(() => {
    loadPolicies();
  }, []);

  const loadPolicies = async () => {
    try {
      const data = await getAttendancePoliciesV2();
      setPolicies(data);
    } catch (err) {
      console.error('Failed to load policies', err);
    }
  };

  const handleCreateNew = () => {
    setEditingPolicy({
      attendancePolicyCode: '',
      name: 'New Policy',
      description: '',
      graceInMinutes: 0,
      graceOutMinutes: 0,
      minHoursForFullDay: 8.0,
      minHoursForHalfDay: 4.0,
      absentHoursThreshold: 2.0,
      lopHalfDayHours: 4.0,
      lopFullDayHours: 8.0,
      lateInThresholdMinutes: 15,
      earlyOutThresholdMinutes: 15,
      lateIncrementThreshold: 3,
      lateHalfDayThreshold: 3,
      lateFullDayThreshold: 6,
      permissionMinutes: 60,
      permissionPerMonth: 2,
      monthlyPermissionHours: 1.0,
      permissionExcessCarryForward: true,
      permissionLopThresholdMinutes: 240,
      permissionLopValue: 0.5,
    });
  };

  const handleSave = async () => {
    if (!editingPolicy) return;
    try {
      setIsSaving(true);
      if (editingPolicy._id) {
        await updateAttendancePolicyV2(editingPolicy._id, editingPolicy);
      } else {
        if (!editingPolicy.attendancePolicyCode) {
            alert("Code is required");
            setIsSaving(false);
            return;
        }
        await createAttendancePolicyV2(editingPolicy);
      }
      setEditingPolicy(null);
      await loadPolicies();
    } catch (err: any) {
      alert(err.message || 'Failed to save policy');
      console.error('Failed to save policy', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure?')) return;
    try {
      await deleteAttendancePolicyV2(id);
      await loadPolicies();
    } catch (err) {
      console.error(err);
    }
  };

  const handleChange = (field: keyof AttendancePolicyV2, value: any) => {
    if (!editingPolicy) return;
    setEditingPolicy({ ...editingPolicy, [field]: value });
  };

  const handleOpenHistory = async (code: string) => {
    try {
      const token = localStorage.getItem('token');
      // Fetch history for this code
      const res = await fetch(`/api/v2/attendance-policy/attendancePolicys/history/${code}`, {
          headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
          const data = await res.json();
          setSelectedCodeHistory(data || []);
          setHistoryModalOpen(true);
      } else {
          // Fallback if history endpoint is missing
          alert("Could not fetch history");
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Attendance Policies</h1>
          <p className="text-sm text-neutral-500">Manage reusable attendance rules (grace periods, minimum hours).</p>
        </div>
        {!editingPolicy && (
          <AnimatedButton icon={Plus} onClick={handleCreateNew}>New Policy</AnimatedButton>
        )}
      </div>

      {!editingPolicy ? (
        <div className="grid grid-cols-1 gap-4">
          {policies.filter(p => p.isCurrent !== false).map(p => (
            <GlassCard key={p._id} className="p-4 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-sm bg-neutral-100 px-2 py-0.5 rounded">{p.attendancePolicyCode}</span>
                  <StatusBadge status="Active" label={`v${p.version || 1}`} />
                  {p.isCurrent !== false && <StatusBadge status="success" label="Current" />}
                </div>
                <h3 className="font-medium text-lg">{p.name}</h3>
                <p className="text-sm text-neutral-500">{p.description || 'No description'}</p>
                <div className="mt-2 flex gap-2">
                  <StatusBadge status="info" label={`Grace In: ${p.graceInMinutes}m`} />
                  <StatusBadge status="warning" label={`Late: ${p.lateInThresholdMinutes}m`} />
                  <StatusBadge status="success" label={`Min Full Day: ${p.minHoursForFullDay}h`} />
                </div>
              </div>
              <div className="flex gap-2">
                <AnimatedButton variant="secondary" onClick={() => handleOpenHistory(p.attendancePolicyCode || '')}>History</AnimatedButton>
                <AnimatedButton variant="secondary" icon={Edit2} onClick={() => setEditingPolicy(p)}>Edit</AnimatedButton>
                {p._id && <AnimatedButton variant="danger" icon={Trash2} onClick={() => handleDelete(p._id!)}>Delete</AnimatedButton>}
              </div>
            </GlassCard>
          ))}
        </div>
      ) : (
        <GlassCard className="p-6 space-y-6">
          <div className="flex justify-between items-center border-b pb-4">
            <h2 className="text-xl font-bold">{editingPolicy._id ? 'Edit Policy' : 'Create Policy'}</h2>
            <div className="flex gap-2">
              <AnimatedButton variant="secondary" onClick={() => setEditingPolicy(null)}>Cancel</AnimatedButton>
              <AnimatedButton icon={Save} onClick={handleSave} loading={isSaving}>Save Policy</AnimatedButton>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            <Input label="Policy Code" value={editingPolicy.attendancePolicyCode || ''} onChange={e => handleChange('attendancePolicyCode', e.target.value)} disabled={!!editingPolicy._id} required />
            <Input label="Policy Name" value={editingPolicy.name} onChange={e => handleChange('name', e.target.value)} />
            <Input label="Description" value={editingPolicy.description || ''} onChange={e => handleChange('description', e.target.value)} />
          </div>

          <h3 className="text-lg font-semibold flex items-center gap-2 mt-4"><Clock className="w-5 h-5 text-blue-500"/> Grace Rules</h3>
          <div className="grid grid-cols-2 gap-4">
            <Input type="number" label="Grace In (Minutes)" value={editingPolicy.graceInMinutes} onChange={e => handleChange('graceInMinutes', Number(e.target.value))} />
            <Input type="number" label="Grace Out (Minutes)" value={editingPolicy.graceOutMinutes} onChange={e => handleChange('graceOutMinutes', Number(e.target.value))} />
          </div>

          <h3 className="text-lg font-semibold flex items-center gap-2 mt-4"><AlertTriangle className="w-5 h-5 text-amber-500"/> Penalties</h3>
          <div className="grid grid-cols-2 gap-4">
            <Input type="number" label="Late In Threshold (Minutes)" value={editingPolicy.lateInThresholdMinutes} onChange={e => handleChange('lateInThresholdMinutes', Number(e.target.value))} />
            <Input type="number" label="Early Out Threshold (Minutes)" value={editingPolicy.earlyOutThresholdMinutes} onChange={e => handleChange('earlyOutThresholdMinutes', Number(e.target.value))} />
          </div>

          <h3 className="text-lg font-semibold flex items-center gap-2 mt-4"><AlertTriangle className="w-5 h-5 text-red-500"/> Monthly Late Rules</h3>
          <div className="grid grid-cols-3 gap-4">
            <Input type="number" min="1" label="Late Increment Threshold" value={editingPolicy.lateIncrementThreshold} onChange={e => handleChange('lateIncrementThreshold', Number(e.target.value))} />
            <Input type="number" min="1" label="Late Half Day Threshold" value={editingPolicy.lateHalfDayThreshold} onChange={e => handleChange('lateHalfDayThreshold', Number(e.target.value))} />
            <Input type="number" min="1" label="Late Full Day Threshold" value={editingPolicy.lateFullDayThreshold} onChange={e => handleChange('lateFullDayThreshold', Number(e.target.value))} />
          </div>

          <h3 className="text-lg font-semibold flex items-center gap-2 mt-4"><Settings className="w-5 h-5 text-purple-500"/> Hour Thresholds</h3>
          <div className="grid grid-cols-3 gap-4">
            <Input type="number" step="0.5" label="Min Hours (Full Day)" value={editingPolicy.minHoursForFullDay} onChange={e => handleChange('minHoursForFullDay', Number(e.target.value))} />
            <Input type="number" step="0.5" label="Min Hours (Half Day)" value={editingPolicy.minHoursForHalfDay} onChange={e => handleChange('minHoursForHalfDay', Number(e.target.value))} />
            <Input type="number" step="0.5" label="Absent Hours Threshold" value={editingPolicy.absentHoursThreshold} onChange={e => handleChange('absentHoursThreshold', Number(e.target.value))} />
            <Input type="number" step="0.5" label="LOP Half Day Hours" value={editingPolicy.lopHalfDayHours} onChange={e => handleChange('lopHalfDayHours', Number(e.target.value))} />
            <Input type="number" step="0.5" label="LOP Full Day Hours" value={editingPolicy.lopFullDayHours} onChange={e => handleChange('lopFullDayHours', Number(e.target.value))} />
          </div>

          <h3 className="text-lg font-semibold flex items-center gap-2 mt-4"><Clock className="w-5 h-5 text-indigo-500"/> Permission Rules</h3>
          <div className="grid grid-cols-3 gap-4">
            <Input type="number" label="Max Mins per Request" value={editingPolicy.permissionMinutes || 60} onChange={e => handleChange('permissionMinutes', Number(e.target.value))} />
            <Input type="number" label="Max Count per Month" value={editingPolicy.permissionPerMonth || 2} onChange={e => handleChange('permissionPerMonth', Number(e.target.value))} />
            <Input type="number" step="0.5" label="Free Monthly Hours" value={editingPolicy.monthlyPermissionHours || 1.0} onChange={e => handleChange('monthlyPermissionHours', Number(e.target.value))} />
            <Input type="number" label="LOP Threshold (Mins)" value={editingPolicy.permissionLopThresholdMinutes || 240} onChange={e => handleChange('permissionLopThresholdMinutes', Number(e.target.value))} />
            <Input type="number" step="0.5" label="LOP Value (Days)" value={editingPolicy.permissionLopValue || 0.5} onChange={e => handleChange('permissionLopValue', Number(e.target.value))} />
            <div className="flex items-center gap-2 pt-8">
              <input type="checkbox" id="carryForward" className="w-4 h-4" checked={editingPolicy.permissionExcessCarryForward !== false} onChange={e => handleChange('permissionExcessCarryForward', e.target.checked)} />
              <label htmlFor="carryForward" className="text-sm font-medium">Enable Excess Carry-Forward</label>
            </div>
          </div>
        </GlassCard>
      )}

      {historyModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl overflow-hidden">
            <div className="px-6 py-4 border-b flex justify-between items-center">
              <h3 className="text-lg font-semibold">Version History</h3>
              <button onClick={() => setHistoryModalOpen(false)} className="text-gray-500 hover:text-gray-700">Close</button>
            </div>
            <div className="p-6">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b text-sm text-neutral-500">
                    <th className="py-2">Version</th>
                    <th className="py-2">Status</th>
                    <th className="py-2">Effective From</th>
                    <th className="py-2">Effective To</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedCodeHistory.map(v => (
                    <tr key={v._id} className="border-b last:border-0 text-sm">
                      <td className="py-3">v{v.version}</td>
                      <td className="py-3">
                        {v.isCurrent ? <StatusBadge status="success" label="Current" /> : <StatusBadge status="neutral" label="Historical" />}
                      </td>
                      <td className="py-3">{v.effectiveFrom ? new Date(v.effectiveFrom).toLocaleDateString() : '-'}</td>
                      <td className="py-3">{v.effectiveTo ? new Date(v.effectiveTo).toLocaleDateString() : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminAttendancePolicy;
