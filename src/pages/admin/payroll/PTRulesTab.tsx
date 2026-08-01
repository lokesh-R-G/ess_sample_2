import React, { useEffect, useState } from 'react';
import { GlassCard, Input, AnimatedButton } from '../../../components/ui';
import { payrollRulesApi } from '../../../services/payrollRulesApi';
import { toast } from 'react-hot-toast';
import { Plus, Trash2 } from 'lucide-react';

const defaultRule = {
  ptEnabled: true,
  states: [],
  effectiveFrom: new Date().toISOString().split('T')[0]
};

export default function PTRulesTab() {
  const [rule, setRule] = useState<any>(defaultRule);
  const [loading, setLoading] = useState(true);
  const [isConfigured, setIsConfigured] = useState(true);

  useEffect(() => {
    fetchRule();
  }, []);

  const fetchRule = async () => {
    try {
      const response = await payrollRulesApi.getPTRules();
      const data = response?.data || response || [];
      if (data && data.length > 0) {
        setRule(data[0]);
        setIsConfigured(true);
      } else {
        setRule(defaultRule);
        setIsConfigured(false);
      }
    } catch (error: any) {
      if (error.response && error.response.status === 404) {
        setRule(defaultRule);
        setIsConfigured(false);
      } else {
        toast.error('Failed to load PT rules');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      if (rule._id || rule.id) {
        await payrollRulesApi.updatePTRule(rule._id || rule.id, rule);
      } else {
        await payrollRulesApi.createPTRule(rule);
      }
      toast.success('PT Rule saved successfully');
      fetchRule();
    } catch (error) {
      toast.error('Failed to save PT Rule');
    }
  };

  const addState = () => {
    setRule((prev: any) => ({
      ...prev,
      states: [...prev.states, { stateName: 'New State', isActive: true, slabs: [] }]
    }));
  };

  const updateStateName = (index: number, name: string) => {
    const newStates = [...rule.states];
    newStates[index].stateName = name;
    setRule({ ...rule, states: newStates });
  };

  const removeState = (index: number) => {
    const newStates = [...rule.states];
    newStates.splice(index, 1);
    setRule({ ...rule, states: newStates });
  };

  const addSlab = (stateIndex: number) => {
    const newStates = [...rule.states];
    newStates[stateIndex].slabs.push({ gender: 'Any', minIncome: 0, maxIncome: 999999, taxAmount: 0 });
    setRule({ ...rule, states: newStates });
  };

  const updateSlab = (stateIndex: number, slabIndex: number, field: string, value: any) => {
    const newStates = [...rule.states];
    newStates[stateIndex].slabs[slabIndex][field] = value;
    setRule({ ...rule, states: newStates });
  };

  const removeSlab = (stateIndex: number, slabIndex: number) => {
    const newStates = [...rule.states];
    newStates[stateIndex].slabs.splice(slabIndex, 1);
    setRule({ ...rule, states: newStates });
  };

  if (loading) return <div className="p-6 text-center text-neutral-500">Loading PT Rules...</div>;

  if (!isConfigured) {
    return (
      <div className="space-y-6">
        <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 bg-brand-50 rounded-full flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-brand-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2zM10 8.5a.5.5 0 11-1 0 .5.5 0 011 0zm5 5a.5.5 0 11-1 0 .5.5 0 011 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-neutral-900 mb-2">PT Rules have not been configured yet</h3>
          <p className="text-neutral-500 max-w-md mb-6">Initialize Professional Tax rules to manage state-wise tax slabs.</p>
          <AnimatedButton onClick={() => setIsConfigured(true)}>Initialize PT Rules</AnimatedButton>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <GlassCard className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-neutral-900">Professional Tax (PT) Rule</h3>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={rule.ptEnabled}
              onChange={(e) => setRule({ ...rule, ptEnabled: e.target.checked })}
              className="rounded border-neutral-300 text-brand-600 focus:ring-brand-500 w-5 h-5"
            />
            <span className="text-sm font-medium text-neutral-900">Enable PT Calculation</span>
          </label>
        </div>

        {rule.ptEnabled && (
          <div className="mt-4 space-y-6">
            {rule.states.map((stateInfo: any, stateIndex: number) => (
              <div key={stateIndex} className="border border-neutral-200 rounded-lg p-4 bg-neutral-50/50">
                <div className="flex justify-between items-center mb-4">
                  <div className="flex-1 max-w-xs">
                    <Input
                      label="State Name"
                      value={stateInfo.stateName}
                      onChange={(e) => updateStateName(stateIndex, e.target.value)}
                    />
                  </div>
                  <button onClick={() => removeState(stateIndex)} className="text-red-500 hover:text-red-700 p-2">
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-neutral-200">
                    <thead className="bg-neutral-100">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Gender</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Min Income</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Max Income</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Tax Amount (₹)</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-neutral-200">
                      {stateInfo.slabs.map((slab: any, slabIndex: number) => (
                        <tr key={slabIndex}>
                          <td className="px-4 py-2">
                            <select
                              value={slab.gender}
                              onChange={(e) => updateSlab(stateIndex, slabIndex, 'gender', e.target.value)}
                              className="block w-full border-neutral-300 rounded-md text-sm shadow-sm focus:border-brand-500 focus:ring-brand-500 bg-white"
                            >
                              <option value="Any">Any</option>
                              <option value="Male">Male</option>
                              <option value="Female">Female</option>
                            </select>
                          </td>
                          <td className="px-4 py-2">
                            <input
                              type="number"
                              value={slab.minIncome}
                              onChange={(e) => updateSlab(stateIndex, slabIndex, 'minIncome', Number(e.target.value))}
                              className="block w-full border-neutral-300 rounded-md text-sm shadow-sm focus:border-brand-500 focus:ring-brand-500"
                            />
                          </td>
                          <td className="px-4 py-2">
                            <input
                              type="number"
                              value={slab.maxIncome}
                              onChange={(e) => updateSlab(stateIndex, slabIndex, 'maxIncome', Number(e.target.value))}
                              className="block w-full border-neutral-300 rounded-md text-sm shadow-sm focus:border-brand-500 focus:ring-brand-500"
                            />
                          </td>
                          <td className="px-4 py-2">
                            <input
                              type="number"
                              value={slab.taxAmount}
                              onChange={(e) => updateSlab(stateIndex, slabIndex, 'taxAmount', Number(e.target.value))}
                              className="block w-full border-neutral-300 rounded-md text-sm shadow-sm focus:border-brand-500 focus:ring-brand-500"
                            />
                          </td>
                          <td className="px-4 py-2 text-right">
                            <button onClick={() => removeSlab(stateIndex, slabIndex)} className="text-red-500 hover:text-red-700">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="mt-4">
                  <button onClick={() => addSlab(stateIndex)} className="text-brand-600 hover:text-brand-700 text-sm font-medium flex items-center space-x-1">
                    <Plus className="w-4 h-4" />
                    <span>Add Slab</span>
                  </button>
                </div>
              </div>
            ))}

            <button onClick={addState} className="text-brand-600 hover:text-brand-700 font-medium flex items-center space-x-1">
              <Plus className="w-5 h-5" />
              <span>Add State Configuration</span>
            </button>
          </div>
        )}

        <div className="mt-6 flex justify-end pt-4 border-t border-neutral-200">
          <AnimatedButton onClick={handleSave}>Save PT Rule</AnimatedButton>
        </div>
      </GlassCard>
    </div>
  );
}
