import React, { useEffect, useState } from 'react';
import { Input, Select } from '../../../../components/ui';
import { organizationApi } from '../../../../services/organization.api';
import { employeeApi } from '../../../../services/employeeApi';
import { Calculator } from 'lucide-react';

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

  // When input changes, reset preview calculation
  useEffect(() => {
    if (data.isSalaryPreviewCalculated) {
      onChange({ ...data, isSalaryPreviewCalculated: false });
      setPreview(null);
    }
  }, [data.salaryStructureId, data.basicSalary, data.pfOption, data.esiOption, data.ptState]);

  const fetchStructures = async () => {
    try {
      const res = await organizationApi.getSalaryStructures();
      setStructures(res?.data || res || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleChange = (field: string, value: any) => {
    onChange({ ...data, [field]: value, isSalaryPreviewCalculated: false });
    setPreview(null);
  };

  const generatePreview = async () => {
    if (!data.salaryStructureId || !data.basicSalary) return;
    
    setLoadingPreview(true);
    try {
      const res = await employeeApi.calculatePayslipPreview({
        salaryStructureId: data.salaryStructureId,
        basicSalary: Number(data.basicSalary),
        pfOption: data.pfOption || 'Default',
        esiOption: data.esiOption || 'Default',
        ptState: data.ptState || 'None'
      });
      setPreview(res?.data || res || null);
      onChange({ ...data, isSalaryPreviewCalculated: true });
    } catch (e) {
      console.error("Preview failed", e);
    } finally {
      setLoadingPreview(false);
    }
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-bold text-neutral-900 mb-4">Salary & Payroll</h3>
      
      {errors.general && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {errors.general}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
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
            label="Basic Salary (₹)"
            type="number"
            value={data.basicSalary || ''}
            onChange={(e) => handleChange('basicSalary', Number(e.target.value))}
            error={errors.basicSalary}
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
              { value: 'PhysicalDisability', label: 'Physical Disability Exception' },
              { value: 'OptOut', label: 'Opt-Out' }
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

          <button
            onClick={(e) => { e.preventDefault(); generatePreview(); }}
            disabled={loadingPreview || !data.salaryStructureId || !data.basicSalary}
            className="w-full flex items-center justify-center px-4 py-3 bg-brand-600 text-white rounded hover:bg-brand-700 disabled:opacity-50 text-sm font-medium transition-colors"
          >
            <Calculator className="w-4 h-4 mr-2" />
            {loadingPreview ? 'Calculating...' : 'Calculate'}
          </button>
        </div>

        {/* Right Side: Payslip Preview */}
        <div className="bg-neutral-50 rounded-lg p-6 border border-neutral-200">
          <h4 className="text-md font-bold text-neutral-800 mb-4 pb-2 border-b border-neutral-200">
            Salary Preview
          </h4>
          
          {!preview && !loadingPreview && (
            <div className="text-center text-neutral-400 py-10 text-sm">
              Enter Basic Salary and config, then click Calculate.
            </div>
          )}

          {preview && (
            <div className="space-y-6">
              
              {/* Earnings */}
              <div className="bg-white p-4 rounded shadow-sm border border-neutral-200">
                <h5 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">Earnings</h5>
                {preview.earnings?.map((e: any, i: number) => (
                  <div key={i} className="flex justify-between items-center text-sm py-1 border-b border-neutral-50 last:border-0">
                    <div>
                        <span className="text-neutral-700 block">{e.name}</span>
                        <span className="text-[10px] text-brand-600 bg-brand-50 px-1 rounded">{e.formula}</span>
                    </div>
                    <span className="font-medium text-neutral-900">₹{e.amount?.toFixed(2)}</span>
                  </div>
                ))}
              </div>

              {/* Salary Distribution Snapshot */}
              <div className="bg-white p-4 rounded shadow-sm border border-neutral-200">
                <h5 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">Salary Distribution</h5>
                {preview.distribution?.map((d: any, i: number) => (
                  <div key={i} className="flex justify-between items-center text-sm py-1.5 border-b border-neutral-50 last:border-0">
                    <span className="text-neutral-700">
                      {d.name}
                    </span>
                    <div className="text-right flex items-center space-x-4">
                      <span className="font-medium text-neutral-900 w-20 text-right">₹{d.amount?.toFixed(2)}</span>
                      <span className="text-xs text-neutral-500 w-16 text-right">{d.distributionPercentage?.toFixed(2)}%</span>
                    </div>
                  </div>
                ))}
                <div className="flex justify-between items-center text-sm py-2 border-t border-neutral-200 mt-2 font-bold text-neutral-900">
                  <span>Gross</span>
                  <div className="text-right flex items-center space-x-4">
                      <span className="w-20 text-right">₹{preview.summary?.grossSalary?.toFixed(2)}</span>
                      <span className="w-16 text-right">100%</span>
                  </div>
                </div>
              </div>

              {/* PF Calculation */}
              <div className="bg-white p-4 rounded shadow-sm border border-neutral-200">
                <h5 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">PF Calculation</h5>
                <div className="mb-3 p-2 bg-neutral-50 rounded text-xs text-neutral-600 space-y-1">
                  <div className="flex justify-between"><span>PF Gross:</span> <span>₹{preview.statutory?.pf?.pfGross?.toFixed(2)}</span></div>
                  <div className="flex justify-between"><span>Ceiling Applied:</span> <span>{preview.statutory?.pf?.ceilingApplied ? 'Yes' : 'No'}</span></div>
                  <div className="flex justify-between"><span>PF Wage Used:</span> <span>₹{preview.statutory?.pf?.pfWageUsed?.toFixed(2)}</span></div>
                </div>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between"><span className="text-neutral-700">Employee PF</span><span className="font-medium text-red-600">-₹{preview.statutory?.pf?.employeeContribution?.toFixed(2)}</span></div>
                  <div className="flex justify-between"><span className="text-neutral-700">Employer PF</span><span className="font-medium">₹{preview.statutory?.pf?.employerPf?.toFixed(2)}</span></div>
                  <div className="flex justify-between"><span className="text-neutral-700">Employer Pension</span><span className="font-medium">₹{preview.statutory?.pf?.employerPension?.toFixed(2)}</span></div>
                  <div className="flex justify-between"><span className="text-neutral-700">EDLI</span><span className="font-medium">₹{preview.statutory?.pf?.edli?.toFixed(2) || '0.00'}</span></div>
                  <div className="flex justify-between"><span className="text-neutral-700">EPF Admin Charges</span><span className="font-medium">₹{preview.statutory?.pf?.adminCharges?.toFixed(2) || '0.00'}</span></div>
                </div>
              </div>

              {/* ESI Calculation */}
              <div className="bg-white p-4 rounded shadow-sm border border-neutral-200">
                <h5 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">ESI Calculation</h5>
                <div className="mb-3 p-2 bg-neutral-50 rounded text-xs text-neutral-600 flex justify-between">
                  <span>ESI Gross:</span> <span>₹{preview.statutory?.esi?.esiGross?.toFixed(2)}</span>
                </div>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between"><span className="text-neutral-700">Employee ESI</span><span className="font-medium text-red-600">-₹{preview.statutory?.esi?.employeeContribution?.toFixed(2)}</span></div>
                  <div className="flex justify-between"><span className="text-neutral-700">Employer ESI</span><span className="font-medium">₹{preview.statutory?.esi?.employerContribution?.toFixed(2)}</span></div>
                </div>
              </div>

              {/* Employee Deductions */}
              <div className="bg-white p-4 rounded shadow-sm border border-neutral-200">
                <h5 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">Employee Deductions</h5>
                {preview.deductions?.length > 0 ? preview.deductions.map((d: any, i: number) => (
                  <div key={i} className="flex justify-between text-sm py-1">
                    <span className="text-neutral-700">{d.name}</span>
                    <span className="font-medium text-red-600">-₹{d.amount?.toFixed(2)}</span>
                  </div>
                )) : <div className="text-sm text-neutral-400 italic py-1">No deductions</div>}
              </div>

              {/* Employer Contributions */}
              <div className="bg-white p-4 rounded shadow-sm border border-neutral-200">
                <h5 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">Employer Contributions</h5>
                {preview.employerContributions?.length > 0 ? preview.employerContributions.map((ec: any, i: number) => (
                  <div key={i} className="flex justify-between text-sm py-1">
                    <span className="text-neutral-700">{ec.name}</span>
                    <span className="font-medium text-neutral-900">₹{ec.amount?.toFixed(2)}</span>
                  </div>
                )) : <div className="text-sm text-neutral-400 italic py-1">No employer contributions</div>}
              </div>

              {/* Final Summary */}
              <div className="bg-gradient-to-br from-brand-50 to-brand-100 p-5 rounded-xl border border-brand-200 shadow-sm space-y-3">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-brand-800 font-semibold">Gross Salary</span>
                  <span className="text-brand-900 font-bold">₹{preview.summary?.grossSalary?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-brand-900 font-bold">Take Home Salary</span>
                  <span className="text-brand-700 font-black text-2xl">₹{preview.summary?.takeHome?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center text-sm border-t border-brand-200/50 pt-2">
                  <span className="text-brand-800 font-semibold">Employer Contribution</span>
                  <span className="text-brand-900 font-bold">₹{preview.summary?.employerContribution?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center pt-2 text-sm">
                  <span className="text-brand-800">Monthly CTC</span>
                  <span className="font-semibold text-brand-900">₹{preview.summary?.monthlyCtc?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-brand-800">Annual CTC</span>
                  <span className="font-bold text-brand-900 text-lg">₹{preview.summary?.annualCtc?.toFixed(2)}</span>
                </div>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  );
}
