import React, { useEffect, useState } from 'react';
import { Settings, Save, Plus, Trash2, Edit2 } from 'lucide-react';
import { GlassCard, AnimatedButton, Input, StatusBadge } from '../../components/ui';
import { WeeklyOffPolicy, getWeeklyOffPolicies, createWeeklyOffPolicy, updateWeeklyOffPolicy, deleteWeeklyOffPolicy } from '../../services/weeklyOffService';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

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
      name: 'New Weekly Off Policy',
      description: '',
      rules: [{ dayOfWeek: 6, weekNumbers: [1, 2, 3, 4, 5] }], // default Sunday every week
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
      console.error('Failed to save policy');
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

  const addRule = () => {
    if (!editingPolicy) return;
    setEditingPolicy({
      ...editingPolicy,
      rules: [...editingPolicy.rules, { dayOfWeek: 5, weekNumbers: [1, 3] }]
    });
  };

  const removeRule = (idx: number) => {
    if (!editingPolicy) return;
    const newRules = [...editingPolicy.rules];
    newRules.splice(idx, 1);
    setEditingPolicy({ ...editingPolicy, rules: newRules });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Weekly Off Policies</h1>
          <p className="text-sm text-neutral-500">Manage rules for weekends (e.g. all Sundays, 1st/3rd Saturdays).</p>
        </div>
        {!editingPolicy && (
          <AnimatedButton icon={Plus} onClick={handleCreateNew}>New Policy</AnimatedButton>
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
                  {p.rules.map((r, i) => (
                    <StatusBadge key={i} status="info" label={`${DAYS[r.dayOfWeek]} (Weeks: ${r.weekNumbers.join(',')})`} />
                  ))}
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
            <h2 className="text-xl font-bold">{editingPolicy._id ? 'Edit Policy' : 'Create Policy'}</h2>
            <div className="flex gap-2">
              <AnimatedButton variant="secondary" onClick={() => setEditingPolicy(null)}>Cancel</AnimatedButton>
              <AnimatedButton icon={Save} onClick={handleSave} loading={isSaving}>Save Policy</AnimatedButton>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <Input label="Policy Name" value={editingPolicy.name} onChange={e => setEditingPolicy({...editingPolicy, name: e.target.value})} />
            <Input label="Description" value={editingPolicy.description || ''} onChange={e => setEditingPolicy({...editingPolicy, description: e.target.value})} />
          </div>

          <div className="mt-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2"><Settings className="w-5 h-5 text-purple-500"/> Day Rules</h3>
              <AnimatedButton variant="secondary" size="sm" icon={Plus} onClick={addRule}>Add Rule</AnimatedButton>
            </div>
            <div className="space-y-3">
              {editingPolicy.rules.map((rule, idx) => (
                <div key={idx} className="flex items-end gap-4 p-3 bg-neutral-50 rounded-lg border">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-neutral-700 mb-1">Day of Week</label>
                    <select 
                      className="w-full px-4 py-2 bg-white border border-neutral-300 rounded-lg"
                      value={rule.dayOfWeek}
                      onChange={e => {
                        const newRules = [...editingPolicy.rules];
                        newRules[idx].dayOfWeek = parseInt(e.target.value);
                        setEditingPolicy({...editingPolicy, rules: newRules});
                      }}
                    >
                      {DAYS.map((d, i) => <option key={i} value={i}>{d}</option>)}
                    </select>
                  </div>
                  <div className="flex-1">
                    <Input 
                      label="Weeks (comma separated, e.g. 1,2,3,4,5)" 
                      value={rule.weekNumbers.join(',')} 
                      onChange={e => {
                        const newRules = [...editingPolicy.rules];
                        newRules[idx].weekNumbers = e.target.value.split(',').map(v => parseInt(v.trim())).filter(v => !isNaN(v));
                        setEditingPolicy({...editingPolicy, rules: newRules});
                      }}
                    />
                  </div>
                  <AnimatedButton variant="danger" icon={Trash2} onClick={() => removeRule(idx)}>Remove</AnimatedButton>
                </div>
              ))}
              {editingPolicy.rules.length === 0 && (
                <p className="text-sm text-neutral-500 italic">No rules defined. This means 0 weekly offs.</p>
              )}
            </div>
          </div>
        </GlassCard>
      )}
    </div>
  );
};

export default AdminWeeklyOffPolicy;
