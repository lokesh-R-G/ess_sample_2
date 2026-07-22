import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Settings, Save, Clock, AlertTriangle } from 'lucide-react';
import { GlassCard, AnimatedButton, Input } from '../../components/ui';
import { AttendancePolicy, getAttendancePolicy, updateAttendancePolicy } from '../../services/policyService';

export const AdminAttendancePolicy: React.FC = () => {
  const [policy, setPolicy] = useState<AttendancePolicy | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    loadPolicy();
  }, []);

  const loadPolicy = async () => {
    try {
      const data = await getAttendancePolicy();
      setPolicy(data);
    } catch (err) {
      setError('Failed to load policy');
    }
  };

  const handleSave = async () => {
    if (!policy) return;
    try {
      setIsSaving(true);
      setMessage('');
      setError('');
      await updateAttendancePolicy(policy);
      setMessage('Policy updated successfully');
    } catch (err) {
      setError('Failed to save policy');
    } finally {
      setIsSaving(false);
    }
  };

  const handleChange = (field: keyof AttendancePolicy, value: string | number) => {
    if (!policy) return;
    setPolicy({ ...policy, [field]: value });
  };

  if (!policy) {
    return (
      <>
        <div className="p-6">Loading policy...</div>
      </>
    );
  }

  return (
    <>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-neutral-900">Attendance Policy Config</h1>
            <p className="text-sm text-neutral-500">Configure global shift timings, late marks, and permission rules in IST.</p>
          </div>
          <AnimatedButton icon={Save} onClick={handleSave} loading={isSaving}>Save Changes</AnimatedButton>
        </div>

        {message && <div className="p-4 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg">{message}</div>}
        {error && <div className="p-4 bg-red-50 text-red-700 border border-red-200 rounded-lg">{error}</div>}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <GlassCard className="p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-primary-500" /> Shift Timings (IST)
              </h3>
              <div className="space-y-4">
                <Input type="time" step="1" label="Shift Start Time" value={policy.shiftStartTime} onChange={(e) => handleChange('shiftStartTime', e.target.value)} />
                <Input type="time" step="1" label="Shift End Time (Mon-Fri)" value={policy.shiftEndTime} onChange={(e) => handleChange('shiftEndTime', e.target.value)} />
                <Input type="time" step="1" label="Saturday Shift End Time" value={policy.saturdayShiftEndTime} onChange={(e) => handleChange('saturdayShiftEndTime', e.target.value)} />
                <Input type="time" step="1" label="Half Day Cutoff Time" value={policy.halfDayCutoffTime} onChange={(e) => handleChange('halfDayCutoffTime', e.target.value)} />
              </div>
            </GlassCard>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <GlassCard className="p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-500" /> Late & Grace Rules
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <Input type="number" label="Grace Minutes" value={policy.graceMinutes} onChange={(e) => handleChange('graceMinutes', Number(e.target.value))} />
                <Input type="number" label="Late Start Minute" value={policy.lateStartMinute} onChange={(e) => handleChange('lateStartMinute', Number(e.target.value))} />
                <Input type="number" label="Late End Minute" value={policy.lateEndMinute} onChange={(e) => handleChange('lateEndMinute', Number(e.target.value))} />
                <Input type="number" label="Late Perm. Start Min" value={policy.latePermissionStartMinute} onChange={(e) => handleChange('latePermissionStartMinute', Number(e.target.value))} />
                <Input type="number" label="Late Perm. End Min" value={policy.latePermissionEndMinute} onChange={(e) => handleChange('latePermissionEndMinute', Number(e.target.value))} />
              </div>
            </GlassCard>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <GlassCard className="p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                <Settings className="w-5 h-5 text-purple-500" /> Monthly & LOP Rules
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <Input type="number" step="0.5" label="Monthly Permission (Hrs)" value={policy.monthlyPermissionHours} onChange={(e) => handleChange('monthlyPermissionHours', Number(e.target.value))} />
                <Input type="number" label="Late Threshold (Half Day)" value={policy.lateHalfDayThreshold} onChange={(e) => handleChange('lateHalfDayThreshold', Number(e.target.value))} />
                <Input type="number" label="Late Threshold (Full Day)" value={policy.lateFullDayThreshold} onChange={(e) => handleChange('lateFullDayThreshold', Number(e.target.value))} />
                <Input type="number" label="Late Increment Threshold" value={policy.lateIncrementThreshold} onChange={(e) => handleChange('lateIncrementThreshold', Number(e.target.value))} />
                <Input type="number" step="0.5" label="LOP Trigger (Half Day Hrs)" value={policy.lopHalfDayHours} onChange={(e) => handleChange('lopHalfDayHours', Number(e.target.value))} />
                <Input type="number" step="0.5" label="LOP Trigger (Full Day Hrs)" value={policy.lopFullDayHours} onChange={(e) => handleChange('lopFullDayHours', Number(e.target.value))} />
              </div>
            </GlassCard>
          </motion.div>
        </div>
      </div>
    </>
  );
};

export default AdminAttendancePolicy;
