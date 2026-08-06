import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Clock, Save, Edit2, Trash2, Plus, Calendar } from 'lucide-react';
import { GlassCard, AnimatedButton, Input, StatusBadge } from '../../components/ui';
import { ShiftV2, getShiftsV2, createShiftV2, updateShiftV2, deleteShiftV2 } from '../../services/shiftService';
import { AttendancePolicyV2, getAttendancePoliciesV2 } from '../../services/policyService';

export const AdminShifts: React.FC = () => {
  const [shifts, setShifts] = useState<ShiftV2[]>([]);
  const [policies, setPolicies] = useState<AttendancePolicyV2[]>([]);
  const [editingShift, setEditingShift] = useState<ShiftV2 | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [shiftsData, policiesData] = await Promise.all([
        getShiftsV2(),
        getAttendancePoliciesV2()
      ]);
      setShifts(shiftsData);
      setPolicies(policiesData);
    } catch (err) {
      console.error('Failed to load data', err);
    }
  };

  const handleCreateNew = () => {
    setEditingShift({
      shiftCode: '',
      name: '',
      description: '',
      attendancePolicyId: '',
      startTime: '10:00:00',
      endTime: '18:30:00',
      autoPunchLunchOut: false,
      autoPunchLunchIn: false,
      isCrossMidnight: false,
    });
  };

  const handleSave = async () => {
    if (!editingShift) return;
    try {
      setIsSaving(true);
      console.log("Saving Shift Payload:", JSON.stringify(editingShift, null, 2));
      const shiftId = (editingShift as any).id || editingShift._id;
      if (shiftId) {
        await updateShiftV2(shiftId, editingShift);
      } else {
        await createShiftV2(editingShift);
      }
      setEditingShift(null);
      await loadData();
    } catch (err) {
      console.error('Failed to save shift', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure?')) return;
    try {
      await deleteShiftV2(id);
      await loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleChange = (field: keyof ShiftV2, value: any) => {
    if (!editingShift) return;
    setEditingShift({ ...editingShift, [field]: value });
  };

  return (
    <div className="space-y-4 mt-4">
      <div className="flex items-center justify-end">
        {!editingShift && (
          <AnimatedButton icon={Plus} onClick={handleCreateNew}>New Shift</AnimatedButton>
        )}
      </div>

      {!editingShift ? (
        <div className="grid grid-cols-1 gap-4">
          {shifts.map(s => (
            <GlassCard key={(s as any).id || s._id} className="p-4 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-medium text-lg">{s.name}</h3>
                  <StatusBadge status="info" label={s.shiftCode} />
                  <StatusBadge 
                    status="success" 
                    label={policies.find(p => ((p as any).id || p._id) === s.attendancePolicyId)?.name || 'Unknown Policy'} 
                  />
                </div>
                <p className="text-sm text-neutral-500">{s.startTime} - {s.endTime}</p>
                <div className="mt-2 flex gap-2">
                  <StatusBadge status={s.isCrossMidnight ? 'warning' : 'success'} label={s.isCrossMidnight ? 'Cross Midnight' : 'Same Day'} />
                  {s.autoPunchLunchOut && <StatusBadge status="info" label="Auto Lunch" />}
                </div>
              </div>
              <div className="flex gap-2">
                <AnimatedButton variant="secondary" icon={Edit2} onClick={() => setEditingShift(s)}>Edit</AnimatedButton>
                {((s as any).id || s._id) && <AnimatedButton variant="danger" icon={Trash2} onClick={() => handleDelete((s as any).id || s._id)}>Delete</AnimatedButton>}
              </div>
            </GlassCard>
          ))}
        </div>
      ) : (
        <GlassCard className="p-6 space-y-6">
          <div className="flex justify-between items-center border-b pb-4">
            <h2 className="text-xl font-bold">{((editingShift as any).id || editingShift._id) ? 'Edit Shift' : 'Create Shift'}</h2>
            <div className="flex gap-2">
              <AnimatedButton variant="secondary" onClick={() => setEditingShift(null)}>Cancel</AnimatedButton>
              <AnimatedButton icon={Save} onClick={handleSave} loading={isSaving}>Save Shift</AnimatedButton>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <Input label="Shift Code" value={editingShift.shiftCode} onChange={e => handleChange('shiftCode', e.target.value)} />
            <Input label="Name" value={editingShift.name} onChange={e => handleChange('name', e.target.value)} />
            <Input label="Description" value={editingShift.description || ''} onChange={e => handleChange('description', e.target.value)} />
            
            <div className="space-y-1">
              <label className="block text-sm font-medium text-neutral-700">Attendance Policy</label>
              <select
                className="w-full rounded-lg border-neutral-300 bg-white/50 focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                value={editingShift.attendancePolicyId}
                onChange={e => handleChange('attendancePolicyId', e.target.value)}
              >
                <option value="">Select a Policy</option>
                {policies.map(p => {
                  const policyId = (p as any).id || p._id;
                  return <option key={policyId} value={policyId}>{p.name}</option>;
                })}
              </select>
            </div>
          </div>

          <h3 className="text-lg font-semibold flex items-center gap-2 mt-4"><Clock className="w-5 h-5 text-blue-500"/> Shift Timings</h3>
          <div className="grid grid-cols-3 gap-4">
            <Input type="time" step="1" label="Start Time" value={editingShift.startTime} onChange={e => handleChange('startTime', e.target.value)} />
            <Input type="time" step="1" label="End Time" value={editingShift.endTime} onChange={e => handleChange('endTime', e.target.value)} />
            
            <div className="flex items-center gap-2 mt-6">
              <input type="checkbox" id="crossMidnight" checked={editingShift.isCrossMidnight} onChange={e => handleChange('isCrossMidnight', e.target.checked)} />
              <label htmlFor="crossMidnight" className="text-sm font-medium">Cross Midnight Shift</label>
            </div>
          </div>

          <h3 className="text-lg font-semibold flex items-center gap-2 mt-4"><Calendar className="w-5 h-5 text-amber-500"/> Break Rules</h3>
          <div className="grid grid-cols-2 gap-4">
            <Input type="time" step="1" label="Break Start Time" value={editingShift.breakStartTime || ''} onChange={e => handleChange('breakStartTime', e.target.value)} />
            <Input type="time" step="1" label="Break End Time" value={editingShift.breakEndTime || ''} onChange={e => handleChange('breakEndTime', e.target.value)} />
            
            <div className="flex items-center gap-4 mt-2 col-span-2">
              <label className="flex items-center gap-2 text-sm font-medium">
                <input type="checkbox" checked={editingShift.autoPunchLunchOut} onChange={e => handleChange('autoPunchLunchOut', e.target.checked)} />
                Auto Punch Lunch Out
              </label>
              <label className="flex items-center gap-2 text-sm font-medium">
                <input type="checkbox" checked={editingShift.autoPunchLunchIn} onChange={e => handleChange('autoPunchLunchIn', e.target.checked)} />
                Auto Punch Lunch In
              </label>
            </div>
          </div>
        </GlassCard>
      )}
    </div>
  );
};

export default AdminShifts;
