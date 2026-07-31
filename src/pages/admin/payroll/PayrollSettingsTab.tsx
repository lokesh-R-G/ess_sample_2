import React, { useEffect, useState } from 'react';
import { GlassCard, Input, Select, AnimatedButton } from '../../../components/ui';
import { payrollRulesApi } from '../../../services/payrollRulesApi';
import { toast } from 'react-hot-toast';

const defaultSettings = {
  payrollFrequency: 'Monthly',
  financialYear: 'April-March',
  currency: 'INR',
  roundOffMethod: 'Nearest Rupee',
  payrollStartDate: 1,
  payrollEndDate: 31,
  lockPayrollAfterProcessing: true,
  allowRetroPayroll: false,
  defaultSalaryCalculationMethod: 'Calendar Days',
  effectiveFrom: new Date().toISOString().split('T')[0]
};

export default function PayrollSettingsTab() {
  const [settings, setSettings] = useState<any>(defaultSettings);
  const [loading, setLoading] = useState(true);
  const [isConfigured, setIsConfigured] = useState(true);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await payrollRulesApi.getPayrollSettings();
      if (response.data && response.data.length > 0) {
        setSettings(response.data[0]);
        setIsConfigured(true);
      } else {
        setSettings(defaultSettings);
        setIsConfigured(false);
      }
    } catch (error: any) {
      if (error.response && error.response.status === 404) {
        setSettings(defaultSettings);
        setIsConfigured(false);
      } else {
        toast.error('Failed to load payroll settings');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: any) => {
    setSettings((prev: any) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    try {
      if (settings._id || settings.id) {
        await payrollRulesApi.updatePayrollSettings(settings._id || settings.id, settings);
      } else {
        await payrollRulesApi.createPayrollSettings(settings);
      }
      toast.success('Payroll settings saved successfully');
      fetchSettings();
    } catch (error) {
      toast.error('Failed to save payroll settings');
    }
  };

  if (loading) return <div className="p-6 text-center text-neutral-500">Loading Payroll Settings...</div>;

  if (!isConfigured) {
    return (
      <div className="space-y-6">
        <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 bg-brand-50 rounded-full flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-brand-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-neutral-900 mb-2">Payroll Settings have not been configured yet</h3>
          <p className="text-neutral-500 max-w-md mb-6">Initialize the payroll rule engine with standard statutory defaults to begin processing payroll.</p>
          <AnimatedButton onClick={() => setIsConfigured(true)}>Initialize Payroll Settings</AnimatedButton>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <GlassCard className="p-6">
        <h3 className="text-lg font-bold text-neutral-900 mb-4">General Payroll Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Select
            label="Payroll Frequency"
            value={settings.payrollFrequency}
            onChange={(e) => handleChange('payrollFrequency', e.target.value)}
            options={[
              { value: 'Monthly', label: 'Monthly' },
              { value: 'Bi-Weekly', label: 'Bi-Weekly' },
              { value: 'Weekly', label: 'Weekly' }
            ]}
          />
          <Input
            label="Financial Year"
            value={settings.financialYear}
            onChange={(e) => handleChange('financialYear', e.target.value)}
          />
          <Select
            label="Round Off Method"
            value={settings.roundOffMethod}
            onChange={(e) => handleChange('roundOffMethod', e.target.value)}
            options={[
              { value: 'Nearest Rupee', label: 'Nearest Rupee' },
              { value: 'Nearest 10', label: 'Nearest 10' },
              { value: 'None', label: 'None' }
            ]}
          />
          <Select
            label="Default Salary Calculation Method"
            value={settings.defaultSalaryCalculationMethod}
            onChange={(e) => handleChange('defaultSalaryCalculationMethod', e.target.value)}
            options={[
              { value: 'Calendar Days', label: 'Calendar Days' },
              { value: 'Working Days', label: 'Working Days' },
              { value: 'Attendance Based', label: 'Attendance Based' },
              { value: 'Fixed 30 Days', label: 'Fixed 30 Days' }
            ]}
          />
          <Input
            label="Payroll Start Date"
            type="number"
            min="1"
            max="31"
            value={settings.payrollStartDate}
            onChange={(e) => handleChange('payrollStartDate', Number(e.target.value))}
          />
          <Input
            label="Payroll End Date"
            type="number"
            min="1"
            max="31"
            value={settings.payrollEndDate}
            onChange={(e) => handleChange('payrollEndDate', Number(e.target.value))}
          />
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={settings.lockPayrollAfterProcessing}
              onChange={(e) => handleChange('lockPayrollAfterProcessing', e.target.checked)}
              className="rounded border-neutral-300 text-brand-600 focus:ring-brand-500"
            />
            <span className="text-sm font-medium text-neutral-700">Lock Payroll After Processing</span>
          </label>
        </div>
        <div className="mt-6 flex justify-end">
          <AnimatedButton onClick={handleSave}>Save Settings</AnimatedButton>
        </div>
      </GlassCard>
    </div>
  );
}
