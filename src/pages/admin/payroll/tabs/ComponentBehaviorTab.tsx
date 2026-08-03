import React, { useEffect, useState } from 'react';
import { GlassCard, AnimatedButton } from '../../../../components/ui';
import { payrollRulesApi } from '../../../../services/payrollRulesApi';
import { toast } from 'react-hot-toast';

export default function ComponentBehaviorTab() {
  const [components, setComponents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchComponents();
  }, []);

  const fetchComponents = async () => {
    try {
      const response = await payrollRulesApi.getSalaryComponents();
      const data = response?.data || response || [];
      if (data && data.length > 0) {
        setComponents(data);
      }
    } catch (error) {
      toast.error('Failed to load salary components');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFlag = async (compId: string, flagName: string, value: boolean) => {
    try {
      const comp = components.find(c => (c._id || c.id) === compId);
      if (!comp) return;

      const updatedComp = { ...comp, [flagName]: value };
      
      // Optimistic update
      setComponents(components.map(c => (c._id || c.id) === compId ? updatedComp : c));

      await payrollRulesApi.updateSalaryComponent(compId, updatedComp);
      toast.success(`Updated ${comp.name}`);
    } catch (error) {
      toast.error('Failed to update component');
      // Revert optimistic update
      fetchComponents();
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <GlassCard className="p-6">
        <h3 className="text-lg font-bold text-neutral-900 mb-4">Salary Component Behaviour Flags</h3>
        <p className="text-sm text-neutral-500 mb-6">Manage how each salary component affects payroll calculations.</p>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-neutral-200">
            <thead className="bg-neutral-100">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Component</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-neutral-500 uppercase tracking-wider">Is Earning?</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-neutral-500 uppercase tracking-wider">Include in Gross?</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Attendance Dependent?
                  <div className="text-[10px] text-neutral-400 normal-case">(LOP Applicable)</div>
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-neutral-500 uppercase tracking-wider">Taxable?</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-neutral-500 uppercase tracking-wider">PF Applicable?</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-neutral-500 uppercase tracking-wider">ESI Applicable?</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-neutral-500 uppercase tracking-wider">PT Applicable?</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-neutral-200">
              {components.map((comp) => {
                const id = comp._id || comp.id;
                return (
                  <tr key={id} className="hover:bg-neutral-50 transition-colors">
                    <td className="px-4 py-3 text-sm font-medium text-neutral-900">{comp.name}</td>
                    <td className="px-4 py-3 text-center">
                      <input
                        type="checkbox"
                        checked={comp.isEarning}
                        onChange={(e) => handleToggleFlag(id, 'isEarning', e.target.checked)}
                        className="rounded border-neutral-300 text-brand-600 focus:ring-brand-500 w-4 h-4"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <input
                        type="checkbox"
                        checked={comp.includeInGross}
                        onChange={(e) => handleToggleFlag(id, 'includeInGross', e.target.checked)}
                        className="rounded border-neutral-300 text-brand-600 focus:ring-brand-500 w-4 h-4"
                      />
                    </td>
                    <td className="px-4 py-3 text-center" title="If enabled, this component will be proportionally adjusted based on the employee's earned gross during payroll processing. If disabled, the component remains constant regardless of attendance.">
                      <input
                        type="checkbox"
                        checked={comp.attendanceDependent ?? true}
                        onChange={(e) => handleToggleFlag(id, 'attendanceDependent', e.target.checked)}
                        className="rounded border-neutral-300 text-brand-600 focus:ring-brand-500 w-4 h-4"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <input
                        type="checkbox"
                        checked={comp.taxable ?? comp.isTaxable}
                        onChange={(e) => handleToggleFlag(id, 'isTaxable', e.target.checked)}
                        className="rounded border-neutral-300 text-brand-600 focus:ring-brand-500 w-4 h-4"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <input
                        type="checkbox"
                        checked={comp.pfApplicable}
                        onChange={(e) => handleToggleFlag(id, 'pfApplicable', e.target.checked)}
                        className="rounded border-neutral-300 text-brand-600 focus:ring-brand-500 w-4 h-4"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <input
                        type="checkbox"
                        checked={comp.esiApplicable}
                        onChange={(e) => handleToggleFlag(id, 'esiApplicable', e.target.checked)}
                        className="rounded border-neutral-300 text-brand-600 focus:ring-brand-500 w-4 h-4"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <input
                        type="checkbox"
                        checked={comp.ptApplicable}
                        onChange={(e) => handleToggleFlag(id, 'ptApplicable', e.target.checked)}
                        className="rounded border-neutral-300 text-brand-600 focus:ring-brand-500 w-4 h-4"
                      />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
