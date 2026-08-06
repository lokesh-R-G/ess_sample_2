import React, { useEffect, useState } from 'react';
import { Save, Plus, Trash2, Edit2, Calendar } from 'lucide-react';
import { GlassCard, AnimatedButton, Input, StatusBadge } from '../../components/ui';
import { WeeklyOffPolicy, DaySchedule, getWeeklyOffPolicies, createWeeklyOffPolicy, updateWeeklyOffPolicy, deleteWeeklyOffPolicy } from '../../services/weeklyOffService';

const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] as const;

const defaultDay: DaySchedule = {
  enabled: true,
  dayType: 'WORKING'
};

const defaultWeekOff: DaySchedule = {
  enabled: true,
  dayType: 'WEEKOFF'
};

export const AdminWeeklyOffPolicy: React.FC = () => {
  const [policies, setPolicies] = useState<WeeklyOffPolicy[]>([]);
  const [editingPolicy, setEditingPolicy] = useState<WeeklyOffPolicy | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadPolicies();
  }, []);

  const loadPolicies = async () => {
    try {
      const data = await getWeeklyOffPolicies();
      setPolicies(data);
    } catch (err) {
      console.error('Failed to load policies', err);
    }
  };

  const handleCreateNew = () => {
    setEditingPolicy({
      name: 'New Weekly Schedule',
      description: '',
      monday: { ...defaultDay },
      tuesday: { ...defaultDay },
      wednesday: { ...defaultDay },
      thursday: { ...defaultDay },
      friday: { ...defaultDay },
      saturday: { ...defaultDay },
      sunday: { ...defaultWeekOff },
    });
  };

  const handleSave = async () => {
    if (!editingPolicy) return;
    try {
      setIsSaving(true);
      if (editingPolicy._id) {
        await updateWeeklyOffPolicy(editingPolicy._id, editingPolicy);
      } else {
        await createWeeklyOffPolicy(editingPolicy);
      }
      setEditingPolicy(null);
      await loadPolicies();
    } catch (err) {
      console.error('Failed to save policy', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure?')) return;
    try {
      await deleteWeeklyOffPolicy(id);
      await loadPolicies();
    } catch (err) {
      console.error(err);
    }
  };

  const updateDay = (day: typeof DAYS[number], data: Partial<DaySchedule>) => {
    if (!editingPolicy) return;
    const current = editingPolicy[day] || { ...defaultDay };
    setEditingPolicy({
      ...editingPolicy,
      [day]: { ...current, ...data }
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Weekly Schedules</h1>
          <p className="text-sm text-neutral-500">Manage 7-day schedule configurations.</p>
        </div>
        {!editingPolicy && (
          <AnimatedButton icon={Plus} onClick={handleCreateNew}>New Schedule</AnimatedButton>
        )}
      </div>

      {!editingPolicy ? (
        <div className="grid grid-cols-1 gap-4">
          {policies.map(p => (
            <GlassCard key={p._id} className="p-4 flex items-center justify-between">
              <div>
                <h3 className="font-medium text-lg">{p.name}</h3>
                <p className="text-sm text-neutral-500">{p.description || 'No description'}</p>
                <div className="mt-2 flex gap-2 flex-wrap">
                  {DAYS.map(d => {
                    const sched = p[d] as DaySchedule | undefined;
                    if (!sched || !sched.enabled || sched.dayType === 'WORKING') return null;
                    return (
                      <StatusBadge 
                        key={d} 
                        status={sched.dayType === 'WEEKOFF' ? 'danger' : 'warning'} 
                        label={`${d.charAt(0).toUpperCase() + d.slice(1)}: ${sched.dayType}`} 
                      />
                    );
                  })}
                </div>
              </div>
              <div className="flex gap-2">
                <AnimatedButton variant="secondary" icon={Edit2} onClick={() => setEditingPolicy(p)}>Edit</AnimatedButton>
                {p._id && <AnimatedButton variant="danger" icon={Trash2} onClick={() => handleDelete(p._id!)}>Delete</AnimatedButton>}
              </div>
            </GlassCard>
          ))}
        </div>
      ) : (
        <GlassCard className="p-6 space-y-6">
          <div className="flex justify-between items-center border-b pb-4">
            <h2 className="text-xl font-bold">{editingPolicy._id ? 'Edit Schedule' : 'Create Schedule'}</h2>
            <div className="flex gap-2">
              <AnimatedButton variant="secondary" onClick={() => setEditingPolicy(null)}>Cancel</AnimatedButton>
              <AnimatedButton icon={Save} onClick={handleSave} loading={isSaving}>Save</AnimatedButton>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <Input label="Schedule Name" value={editingPolicy.name} onChange={e => setEditingPolicy({...editingPolicy, name: e.target.value})} />
            <Input label="Description" value={editingPolicy.description || ''} onChange={e => setEditingPolicy({...editingPolicy, description: e.target.value})} />
          </div>

          <div className="mt-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2"><Calendar className="w-5 h-5 text-purple-500"/> 7-Day Configuration</h3>
            </div>
            <div className="space-y-4">
              {DAYS.map(day => {
                const sched = editingPolicy[day] || { ...defaultDay };
                return (
                  <div key={day} className="flex flex-col md:flex-row items-center gap-4 p-4 bg-neutral-50 rounded-lg border border-neutral-200">
                    <div className="w-32 font-medium capitalize text-neutral-800">
                      {day}
                    </div>
                    <div className="flex-1 w-full grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <label className="block text-xs font-medium text-neutral-500 mb-1">Day Type</label>
                        <select 
                          className="w-full px-3 py-2 bg-white border border-neutral-300 rounded-lg text-sm"
                          value={sched.dayType}
                          onChange={e => updateDay(day, { dayType: e.target.value as any, startTime: '', endTime: '' })}
                        >
                          <option value="WORKING">Working</option>
                          <option value="WEEKOFF">Week Off</option>
                          <option value="CUTOFF">Cut Off</option>
                        </select>
                      </div>
                      
                      {sched.dayType === 'CUTOFF' && (
                        <>
                          <div>
                            <Input type="time" label="Start Time" value={sched.startTime || ''} onChange={e => updateDay(day, { startTime: e.target.value })} />
                          </div>
                          <div>
                            <Input type="time" label="End Time" value={sched.endTime || ''} onChange={e => updateDay(day, { endTime: e.target.value })} />
                          </div>
                        </>
                      )}
                      
                      <div className={sched.dayType === 'CUTOFF' ? 'col-span-1' : 'col-span-3'}>
                        <Input label="Remarks (Optional)" value={sched.remarks || ''} onChange={e => updateDay(day, { remarks: e.target.value })} />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </GlassCard>
      )}
    </div>
  );
};

export default AdminWeeklyOffPolicy;
