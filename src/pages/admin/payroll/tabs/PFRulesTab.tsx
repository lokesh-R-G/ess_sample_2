import React, { useEffect, useState } from 'react';
import { GlassCard, Input, Select, AnimatedButton } from '../../../../components/ui';
import { payrollRulesApi } from '../../../../services/payrollRulesApi';
import { toast } from 'react-hot-toast';

const defaultRule = {
  pfEnabled: true,
  mandatoryBelowGross: 15000,
  optionalAboveGross: 15000,
  defaultMode: 'Ask During Employee Creation',
  pfCeilingAmount: 15000,
  employeePfPercent: 12,
  employerPfPercent: 3.67,
  employerPensionPercent: 8.33,
  maxPensionAmount: 1250,
  allowExistingPensionMember: true,
  effectiveFrom: new Date().toISOString().split('T')[0]
};

export default function PFRulesTab() {
  const [rule, setRule] = useState<any>(defaultRule);
  const [loading, setLoading] = useState(true);
  const [isConfigured, setIsConfigured] = useState(true);

  useEffect(() => {
    fetchRule();
  }, []);

  const fetchRule = async () => {
    try {
      const response = await payrollRulesApi.getPFRules();
      const data = response?.data || response;
      if (data && !Array.isArray(data) && data.id) {
        setRule(data);
        setIsConfigured(true);
      } else if (Array.isArray(data) && data.length > 0) {
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
        toast.error('Failed to load PF rules');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: any) => {
    setRule((prev: any) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    try {
      if (rule._id || rule.id) {
        await payrollRulesApi.updatePFRule(rule._id || rule.id, rule);
      } else {
        await payrollRulesApi.createPFRule(rule);
      }
      toast.success('PF Rule saved successfully');
      fetchRule();
    } catch (error) {
      toast.error('Failed to save PF Rule');
    }
  };

  if (loading) return <div className="p-6 text-center text-neutral-500">Loading PF Rules...</div>;

  if (!isConfigured) {
    return (
      <div className="space-y-6">
        <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 bg-brand-50 rounded-full flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-brand-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-neutral-900 mb-2">PF Rules have not been configured yet</h3>
          <p className="text-neutral-500 max-w-md mb-6">Initialize Provident Fund rules with standard statutory defaults.</p>
          <AnimatedButton onClick={() => setIsConfigured(true)}>Initialize PF Rules</AnimatedButton>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <GlassCard className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-neutral-900">Provident Fund (PF) Rule</h3>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={rule.pfEnabled}
              onChange={(e) => handleChange('pfEnabled', e.target.checked)}
              className="rounded border-neutral-300 text-brand-600 focus:ring-brand-500 w-5 h-5"
            />
            <span className="text-sm font-medium text-neutral-900">Enable PF Calculation</span>
          </label>
        </div>

        {rule.pfEnabled && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4 border-t border-neutral-200 pt-4">
            <Select
              label="Default Setup Mode"
              value={rule.defaultMode}
              onChange={(e) => handleChange('defaultMode', e.target.value)}
              options={[
                { value: 'Ask During Employee Creation', label: 'Ask During Employee Creation' },
                { value: 'Always Ceiling', label: 'Always Ceiling' },
                { value: 'Always Actual Gross', label: 'Always Actual Gross' }
              ]}
            />
            <Input
              label="PF Ceiling Amount (₹)"
              type="number"
              value={rule.pfCeilingAmount}
              onChange={(e) => handleChange('pfCeilingAmount', Number(e.target.value))}
            />
            <Input
              label="Employee PF Contribution (%)"
              type="number"
              step="0.01"
              value={rule.employeePfPercent}
              onChange={(e) => handleChange('employeePfPercent', Number(e.target.value))}
            />
            <Input
              label="Employer PF Contribution (%)"
              type="number"
              step="0.01"
              value={rule.employerPfPercent}
              onChange={(e) => handleChange('employerPfPercent', Number(e.target.value))}
            />
            <Input
              label="Employer Pension Contribution (%)"
              type="number"
              step="0.01"
              value={rule.employerPensionPercent}
              onChange={(e) => handleChange('employerPensionPercent', Number(e.target.value))}
            />
            <Input
              label="Max Pension Amount (₹)"
              type="number"
              value={rule.maxPensionAmount}
              onChange={(e) => handleChange('maxPensionAmount', Number(e.target.value))}
            />
             <label className="flex items-center space-x-2 mt-4">
                <input
                type="checkbox"
                checked={rule.allowExistingPensionMember}
                onChange={(e) => handleChange('allowExistingPensionMember', e.target.checked)}
                className="rounded border-neutral-300 text-brand-600 focus:ring-brand-500"
                />
                <span className="text-sm font-medium text-neutral-700">Allow Existing Pension Member Flag</span>
            </label>
          </div>
        )}
        <div className="mt-6 flex justify-end">
          <AnimatedButton onClick={handleSave}>Save PF Rule</AnimatedButton>
        </div>
      </GlassCard>
    </div>
  );
}
