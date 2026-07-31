import React, { useEffect, useState } from 'react';
import { GlassCard, Input, AnimatedButton } from '../../../components/ui';
import { payrollRulesApi } from '../../../services/payrollRulesApi';
import { toast } from 'react-hot-toast';

const defaultRule = {
  esiEnabled: true,
  wageThreshold: 21000,
  employeeEsiPercent: 0.75,
  employerEsiPercent: 3.25,
  allowPhysicalDisabilityException: true,
  physicalDisabilityWageThreshold: 25000,
  effectiveFrom: new Date().toISOString().split('T')[0]
};

export default function ESIRulesTab() {
  const [rule, setRule] = useState<any>(defaultRule);
  const [loading, setLoading] = useState(true);
  const [isConfigured, setIsConfigured] = useState(true);

  useEffect(() => {
    fetchRule();
  }, []);

  const fetchRule = async () => {
    try {
      const response = await payrollRulesApi.getESIRules();
      if (response.data && response.data.length > 0) {
        setRule(response.data[0]);
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
        toast.error('Failed to load ESI rules');
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
        await payrollRulesApi.updateESIRule(rule._id || rule.id, rule);
      } else {
        await payrollRulesApi.createESIRule(rule);
      }
      toast.success('ESI Rule saved successfully');
      fetchRule();
    } catch (error) {
      toast.error('Failed to save ESI Rule');
    }
  };

  if (loading) return <div className="p-6 text-center text-neutral-500">Loading ESI Rules...</div>;

  if (!isConfigured) {
    return (
      <div className="space-y-6">
        <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 bg-brand-50 rounded-full flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-brand-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-neutral-900 mb-2">ESI Rules have not been configured yet</h3>
          <p className="text-neutral-500 max-w-md mb-6">Initialize Employee State Insurance rules with standard statutory defaults.</p>
          <AnimatedButton onClick={() => setIsConfigured(true)}>Initialize ESI Rules</AnimatedButton>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <GlassCard className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-neutral-900">Employee State Insurance (ESI) Rule</h3>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={rule.esiEnabled}
              onChange={(e) => handleChange('esiEnabled', e.target.checked)}
              className="rounded border-neutral-300 text-brand-600 focus:ring-brand-500 w-5 h-5"
            />
            <span className="text-sm font-medium text-neutral-900">Enable ESI Calculation</span>
          </label>
        </div>

        {rule.esiEnabled && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4 border-t border-neutral-200 pt-4">
            <Input
              label="Standard Wage Threshold (₹)"
              type="number"
              value={rule.wageThreshold}
              onChange={(e) => handleChange('wageThreshold', Number(e.target.value))}
            />
            <Input
              label="Employee ESI Contribution (%)"
              type="number"
              step="0.01"
              value={rule.employeeEsiPercent}
              onChange={(e) => handleChange('employeeEsiPercent', Number(e.target.value))}
            />
            <Input
              label="Employer ESI Contribution (%)"
              type="number"
              step="0.01"
              value={rule.employerEsiPercent}
              onChange={(e) => handleChange('employerEsiPercent', Number(e.target.value))}
            />
            
            <div className="col-span-1 md:col-span-2">
              <label className="flex items-center space-x-2 mt-4">
                <input
                  type="checkbox"
                  checked={rule.allowPhysicalDisabilityException}
                  onChange={(e) => handleChange('allowPhysicalDisabilityException', e.target.checked)}
                  className="rounded border-neutral-300 text-brand-600 focus:ring-brand-500"
                />
                <span className="text-sm font-medium text-neutral-700">Allow Physical Disability Exception</span>
              </label>
            </div>
            {rule.allowPhysicalDisabilityException && (
              <Input
                label="Physical Disability Wage Threshold (₹)"
                type="number"
                value={rule.physicalDisabilityWageThreshold}
                onChange={(e) => handleChange('physicalDisabilityWageThreshold', Number(e.target.value))}
              />
            )}
          </div>
        )}
        <div className="mt-6 flex justify-end">
          <AnimatedButton onClick={handleSave}>Save ESI Rule</AnimatedButton>
        </div>
      </GlassCard>
    </div>
  );
}
