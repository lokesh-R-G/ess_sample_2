import React, { useEffect, useState, useCallback } from 'react';
import { Input, Select } from '../../../../components/ui';
import { organizationApi } from '../../../../services/organization.api';
import { employeeApi } from '../../../../services/employeeApi';
import { toast } from 'react-hot-toast';

interface SalaryPayrollStepProps {
  data: any;
  onChange: (data: any) => void;
  errors?: Record<string, string>;
}

export default function SalaryPayrollStep({ data, onChange, errors = {} }: SalaryPayrollStepProps) {
  const [structures, setStructures] = useState<any[]>([]);
  const [preview, setPreview] = useState<any>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);

  useEffect(() => {
    fetchStructures();
  }, []);

  const fetchStructures = async () => {
    try {
      const res = await organizationApi.getSalaryStructures();
      setStructures(res?.data || res || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleChange = (field: string, value: any) => {
    onChange({ ...data, [field]: value });
  };

  const generatePreview = useCallback(async () => {
    if (!data.salaryStructureId || !data.monthlyGross) return;
    
    setLoadingPreview(true);
    try {
      // Create a mock payload to the engine
      const res = await employeeApi.calculatePayslipPreview({
        salaryStructureId: data.salaryStructureId,
        gross: Number(data.monthlyGross),
        pfOption: data.pfOption || 'Default',
        esiOption: data.esiOption || 'Default',
        ptState: data.ptState || 'None'
      });
      setPreview(res?.data || res || null);
    } catch (e) {
      console.error("Preview failed", e);
    } finally {
      setLoadingPreview(false);
    }
  }, [data]);

  // Whenever key fields change, trigger a preview
  useEffect(() => {
    const timer = setTimeout(() => {
      generatePreview();
    }, 500);
    return () => clearTimeout(timer);
  }, [data.salaryStructureId, data.monthlyGross, data.pfOption, data.esiOption, data.ptState, generatePreview]);

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-bold text-neutral-900 mb-4">Salary & Payroll</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Left Side: Input Form */}
        <div className="space-y-6">
          <Select
            label="Salary Structure"
            value={data.salaryStructureId || ''}
            onChange={(e) => handleChange('salaryStructureId', e.target.value)}
            error={errors.salaryStructureId}
            options={[
              { value: '', label: 'Select Structure' },
              ...structures.map(s => ({ value: s._id || s.id, label: s.name }))
            ]}
            required
          />
          
          <Input
            label="Monthly Gross Salary (₹)"
            type="number"
            value={data.monthlyGross || ''}
            onChange={(e) => handleChange('monthlyGross', Number(e.target.value))}
            error={errors.monthlyGross}
            required
          />

          <Select
            label="PF Calculation Option"
            value={data.pfOption || 'Default'}
            onChange={(e) => handleChange('pfOption', e.target.value)}
            options={[
              { value: 'Default', label: 'Use Global Rule Default' },
              { value: 'Ceiling', label: 'Calculate on Ceiling Only' },
              { value: 'Actual', label: 'Calculate on Actual Gross' },
              { value: 'OptOut', label: 'Opt-Out (If Allowed)' }
            ]}
          />

          <Select
            label="ESI Option"
            value={data.esiOption || 'Default'}
            onChange={(e) => handleChange('esiOption', e.target.value)}
            options={[
              { value: 'Default', label: 'Calculate if eligible' },
              { value: 'PhysicalDisability', label: 'Physical Disability Exception' }
            ]}
          />

          <Select
            label="Professional Tax State"
            value={data.ptState || 'None'}
            onChange={(e) => handleChange('ptState', e.target.value)}
            options={[
              { value: 'None', label: 'Not Applicable' },
              { value: 'Karnataka', label: 'Karnataka' },
              { value: 'Maharashtra', label: 'Maharashtra' },
              { value: 'Telangana', label: 'Telangana' }
            ]}
          />
        </div>

        {/* Right Side: Payslip Preview */}
        <div className="bg-neutral-50 rounded-lg p-6 border border-neutral-200">
          <h4 className="text-md font-bold text-neutral-800 mb-4 flex items-center justify-between">
            <span>Payslip Preview</span>
            {loadingPreview && <span className="text-xs text-brand-600 font-normal animate-pulse">Calculating...</span>}
          </h4>
          
          {!preview && !loadingPreview && (
            <div className="text-center text-neutral-400 py-10 text-sm">
              Enter Salary Structure and Gross to generate preview.
            </div>
          )}

          {preview && (
            <div className="space-y-4">
              <div className="bg-white p-4 rounded border border-neutral-200">
                <h5 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2">Earnings</h5>
                {preview.earnings?.map((e: any, i: number) => (
                  <div key={i} className="flex justify-between text-sm py-1">
                    <span className="text-neutral-700">{e.name}</span>
                    <span className="font-medium text-neutral-900">₹{e.amount?.toFixed(2)}</span>
                  </div>
                ))}
                <div className="flex justify-between text-sm py-2 mt-2 border-t border-neutral-100 font-bold">
                  <span>Total Earnings</span>
                  <span className="text-green-600">₹{preview.totalEarnings?.toFixed(2)}</span>
                </div>
              </div>

              <div className="bg-white p-4 rounded border border-neutral-200">
                <h5 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2">Deductions</h5>
                {preview.deductions?.map((d: any, i: number) => (
                  <div key={i} className="flex justify-between text-sm py-1">
                    <span className="text-neutral-700">{d.name}</span>
                    <span className="font-medium text-neutral-900">₹{d.amount?.toFixed(2)}</span>
                  </div>
                ))}
                <div className="flex justify-between text-sm py-2 mt-2 border-t border-neutral-100 font-bold">
                  <span>Total Deductions</span>
                  <span className="text-red-500">₹{preview.totalDeductions?.toFixed(2)}</span>
                </div>
              </div>

              <div className="bg-brand-50 p-4 rounded border border-brand-200 flex justify-between items-center">
                <span className="text-brand-900 font-bold">Net Payable</span>
                <span className="text-brand-700 font-black text-lg">₹{preview.netPay?.toFixed(2)}</span>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
