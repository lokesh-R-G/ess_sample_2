import React, { useEffect, useState } from 'react';
import { DashboardLayout } from '../../components/layout';
import { GlassCard, AnimatedButton, Input, Select, StatusBadge } from '../../components/ui';
import { Plus, Save, Trash2, Edit } from 'lucide-react';
import { getLeavePoliciesV2, createLeavePolicyV2, LeavePolicyV2, LeaveTypeConfig } from '../../services/leavePolicyService';

export const LeavePolicySettings: React.FC = () => {
  const [policies, setPolicies] = useState<LeavePolicyV2[]>([]);
  const [activePolicy, setActivePolicy] = useState<LeavePolicyV2 | null>(null);
  
  const [formData, setFormData] = useState<Partial<LeavePolicyV2>>({
    policyCode: 'NEW_POLICY',
    name: '',
    effectiveFrom: new Date().toISOString().split('T')[0],
    leaveTypes: []
  });

  const loadPolicies = async () => {
    try {
      const data = await getLeavePoliciesV2();
      setPolicies(data?.data || data || []);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadPolicies();
  }, []);

  const handleAddLeaveType = () => {
    const newLt: LeaveTypeConfig = {
      code: 'NEW',
      name: 'New Leave Type',
      enabled: true,
      annualEntitlement: 12,
      carryForwardEnabled: false,
      carryForwardLimit: 0,
      carryForwardType: 'FLAT',
      expiryEnabled: true,
      expiryRule: 'YEAR_END',
      joiningYearProrationEnabled: true,
      prorationRule: 'MONTHLY_REDUCTION',
      anniversaryEligibilityEnabled: true,
      zeroBalanceApprovalAllowed: true,
      lopEnabled: true
    };
    setFormData({ ...formData, leaveTypes: [...(formData.leaveTypes || []), newLt] });
  };

  const handleUpdateLeaveType = (index: number, field: string, value: any) => {
    const updated = [...(formData.leaveTypes || [])];
    updated[index] = { ...updated[index], [field]: value };
    setFormData({ ...formData, leaveTypes: updated });
  };

  const handleRemoveLeaveType = (index: number) => {
    const updated = [...(formData.leaveTypes || [])];
    updated.splice(index, 1);
    setFormData({ ...formData, leaveTypes: updated });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createLeavePolicyV2(formData as LeavePolicyV2);
      await loadPolicies();
      alert("Leave Policy Saved Successfully");
    } catch (e) {
      alert("Error saving policy");
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-neutral-900">Leave Policy Settings</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-6">
            <GlassCard className="p-6">
              <h3 className="text-lg font-semibold mb-4">Historical Policies</h3>
              <div className="space-y-2">
                {policies.map(p => (
                  <div key={p.id} className="p-3 border rounded cursor-pointer hover:bg-neutral-50" onClick={() => setFormData(p)}>
                    <div className="flex justify-between">
                      <span className="font-medium">{p.name} (v{p.version})</span>
                      <StatusBadge status={p.status === 'Active' ? 'success' : 'default'} label={p.status || ''} size="sm" />
                    </div>
                    <div className="text-xs text-neutral-500">Effective: {new Date(p.effectiveFrom).toLocaleDateString()}</div>
                  </div>
                ))}
              </div>
            </GlassCard>
          </div>

          <div className="lg:col-span-2">
            <GlassCard className="p-6">
              <h3 className="text-lg font-semibold mb-4">Policy Configuration</h3>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <Input label="Policy Code" value={formData.policyCode || ''} onChange={e => setFormData({...formData, policyCode: e.target.value})} required />
                  <Input label="Policy Name" value={formData.name || ''} onChange={e => setFormData({...formData, name: e.target.value})} required />
                </div>
                <Input label="Effective From" type="date" value={formData.effectiveFrom?.split('T')[0] || ''} onChange={e => setFormData({...formData, effectiveFrom: e.target.value})} required />

                <div className="flex justify-between items-center mt-6 mb-4">
                  <h4 className="font-semibold text-neutral-800">Leave Types</h4>
                  <AnimatedButton type="button" size="sm" icon={Plus} onClick={handleAddLeaveType}>Add Leave Type</AnimatedButton>
                </div>

                <div className="space-y-4">
                  {formData.leaveTypes?.map((lt, index) => (
                    <div key={index} className="p-4 border border-neutral-200 rounded-xl space-y-4 bg-neutral-50 relative">
                      <button type="button" onClick={() => handleRemoveLeaveType(index)} className="absolute top-4 right-4 text-red-500 hover:text-red-700">
                        <Trash2 className="w-4 h-4" />
                      </button>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <Input label="Code" value={lt.code} onChange={e => handleUpdateLeaveType(index, 'code', e.target.value)} required />
                        <Input label="Name" value={lt.name} onChange={e => handleUpdateLeaveType(index, 'name', e.target.value)} required />
                        <Input label="Annual Entitlement" type="number" value={lt.annualEntitlement} onChange={e => handleUpdateLeaveType(index, 'annualEntitlement', parseFloat(e.target.value))} required />
                        <Select label="Enabled" value={lt.enabled ? 'true' : 'false'} onChange={e => handleUpdateLeaveType(index, 'enabled', e.target.value === 'true')} options={[{value: 'true', label: 'Yes'}, {value: 'false', label: 'No'}]} />
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <Select label="Carry Forward" value={lt.carryForwardEnabled ? 'true' : 'false'} onChange={e => handleUpdateLeaveType(index, 'carryForwardEnabled', e.target.value === 'true')} options={[{value: 'true', label: 'Yes'}, {value: 'false', label: 'No'}]} />
                        {lt.carryForwardEnabled && <Input label="Max Limit (0=Unlimited)" type="number" value={lt.carryForwardLimit} onChange={e => handleUpdateLeaveType(index, 'carryForwardLimit', parseFloat(e.target.value))} />}
                        <Select label="Proration (Join Year)" value={lt.joiningYearProrationEnabled ? 'true' : 'false'} onChange={e => handleUpdateLeaveType(index, 'joiningYearProrationEnabled', e.target.value === 'true')} options={[{value: 'true', label: 'Yes'}, {value: 'false', label: 'No'}]} />
                        <Select label="Anniversary 1-yr Wait" value={lt.anniversaryEligibilityEnabled ? 'true' : 'false'} onChange={e => handleUpdateLeaveType(index, 'anniversaryEligibilityEnabled', e.target.value === 'true')} options={[{value: 'true', label: 'Yes'}, {value: 'false', label: 'No'}]} />
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <Select label="Zero Balance LOP Allow" value={lt.zeroBalanceApprovalAllowed ? 'true' : 'false'} onChange={e => handleUpdateLeaveType(index, 'zeroBalanceApprovalAllowed', e.target.value === 'true')} options={[{value: 'true', label: 'Yes'}, {value: 'false', label: 'No'}]} />
                        <Select label="Expiry at Year End" value={lt.expiryEnabled ? 'true' : 'false'} onChange={e => handleUpdateLeaveType(index, 'expiryEnabled', e.target.value === 'true')} options={[{value: 'true', label: 'Yes'}, {value: 'false', label: 'No'}]} />
                      </div>
                    </div>
                  ))}
                  {formData.leaveTypes?.length === 0 && (
                    <div className="text-center p-6 text-neutral-500 border border-dashed rounded-xl">No leave types configured.</div>
                  )}
                </div>

                <div className="flex justify-end pt-4">
                  <AnimatedButton type="submit" variant="primary" icon={Save}>Save Policy</AnimatedButton>
                </div>
              </form>
            </GlassCard>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default LeavePolicySettings;
