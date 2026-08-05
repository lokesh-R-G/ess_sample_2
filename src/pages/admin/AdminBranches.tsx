import React, { useEffect, useState } from 'react';
import { Plus, Save, Trash2, Edit2, Building2 } from 'lucide-react';
import { GlassCard, AnimatedButton, Input } from '../../components/ui';
import { Branch, getBranches, createBranch, updateBranch, deleteBranch } from '../../services/branchService';
import { HolidayCalendar, getHolidayCalendars } from '../../services/holidayCalendarService';
import { WeeklyOffPolicy, getWeeklyOffPolicies } from '../../services/weeklyOffService';

export const AdminBranches: React.FC = () => {
  const [branches, setBranches] = useState<Branch[]>([]);
  const [calendars, setCalendars] = useState<HolidayCalendar[]>([]);
  const [weeklyOffs, setWeeklyOffs] = useState<WeeklyOffPolicy[]>([]);
  
  const [editingBranch, setEditingBranch] = useState<Branch | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [b, c, w] = await Promise.all([
        getBranches(),
        getHolidayCalendars(),
        getWeeklyOffPolicies()
      ]);
      setBranches(b);
      setCalendars(c);
      setWeeklyOffs(w);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSave = async () => {
    if (!editingBranch) return;
    try {
      setIsSaving(true);
      if (editingBranch._id) {
        await updateBranch(editingBranch._id, editingBranch);
      } else {
        await createBranch(editingBranch);
      }
      setEditingBranch(null);
      await loadData();
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure?')) return;
    try {
      await deleteBranch(id);
      await loadData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Branches</h1>
          <p className="text-sm text-neutral-500">Manage organizational branches and assign policies.</p>
        </div>
        {!editingBranch && (
          <AnimatedButton icon={Plus} onClick={() => setEditingBranch({ name: '' })}>New Branch</AnimatedButton>
        )}
      </div>

      {!editingBranch ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {branches.map(b => (
            <GlassCard key={b._id} className="p-4 flex flex-col justify-between h-full">
              <div>
                <h3 className="font-semibold text-lg flex items-center gap-2"><Building2 className="w-5 h-5 text-blue-500"/> {b.name}</h3>
                <p className="text-sm text-neutral-500 mb-4">{b.location || 'No location specified'}</p>
                
                <div className="space-y-2 mb-4">
                  <div className="text-sm border-l-2 pl-2 border-primary-500 bg-neutral-50 p-2 rounded">
                    <span className="font-medium">Holiday Calendar:</span> {b.holidayCalendarId ? calendars.find(c => c._id === b.holidayCalendarId)?.name : <span className="text-red-500">Unassigned</span>}
                  </div>
                  <div className="text-sm border-l-2 pl-2 border-purple-500 bg-neutral-50 p-2 rounded">
                    <span className="font-medium">Weekly Off Policy:</span> {b.weeklyOffPolicyId ? weeklyOffs.find(w => w._id === b.weeklyOffPolicyId)?.name : <span className="text-red-500">Unassigned</span>}
                  </div>
                </div>
              </div>
              <div className="flex justify-end gap-2 mt-auto">
                <AnimatedButton variant="secondary" size="sm" icon={Edit2} onClick={() => setEditingBranch(b)}>Edit</AnimatedButton>
                {b._id && <AnimatedButton variant="danger" size="sm" icon={Trash2} onClick={() => handleDelete(b._id!)}>Delete</AnimatedButton>}
              </div>
            </GlassCard>
          ))}
        </div>
      ) : (
        <GlassCard className="p-6">
          <h2 className="text-xl font-bold mb-4">{editingBranch._id ? 'Edit Branch' : 'Create Branch'}</h2>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
            <Input label="Branch Name" value={editingBranch.name} onChange={e => setEditingBranch({...editingBranch, name: e.target.value})} />
            <Input label="Branch Code" value={editingBranch.code || ''} onChange={e => setEditingBranch({...editingBranch, code: e.target.value})} />
            <Input label="Location" value={editingBranch.location || ''} onChange={e => setEditingBranch({...editingBranch, location: e.target.value})} />
          </div>

          <h3 className="text-lg font-semibold border-b pb-2 mb-4">Assignments (Policy Resolvers)</h3>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Holiday Calendar</label>
              <select 
                className="w-full px-4 py-2 bg-white border border-neutral-300 rounded-lg"
                value={editingBranch.holidayCalendarId || ''}
                onChange={e => setEditingBranch({...editingBranch, holidayCalendarId: e.target.value})}
              >
                <option value="">-- Select Calendar --</option>
                {calendars.map(c => <option key={c._id} value={c._id}>{c.name} ({c.year})</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Weekly Off Policy</label>
              <select 
                className="w-full px-4 py-2 bg-white border border-neutral-300 rounded-lg"
                value={editingBranch.weeklyOffPolicyId || ''}
                onChange={e => setEditingBranch({...editingBranch, weeklyOffPolicyId: e.target.value})}
              >
                <option value="">-- Select Weekly Off Policy --</option>
                {weeklyOffs.map(w => <option key={w._id} value={w._id}>{w.name}</option>)}
              </select>
            </div>
          </div>

          <div className="flex gap-2 justify-end">
            <AnimatedButton variant="secondary" onClick={() => setEditingBranch(null)}>Cancel</AnimatedButton>
            <AnimatedButton icon={Save} loading={isSaving} onClick={handleSave}>Save Branch</AnimatedButton>
          </div>
        </GlassCard>
      )}
    </div>
  );
};

export default AdminBranches;
