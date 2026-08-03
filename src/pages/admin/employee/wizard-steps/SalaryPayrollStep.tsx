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
  const [allComponents, setAllComponents] = useState<any[]>([]);
  const [preview, setPreview] = useState<any>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      const [structRes, compRes] = await Promise.all([
        organizationApi.getSalaryStructures(),
        organizationApi.getSalaryComponents()
      ]);
      setStructures(structRes?.data || structRes || []);
      setAllComponents(compRes?.data || compRes || []);
    } catch (e) {
      console.error(e);
    }
  };

  // Extract the specific components for the currently selected structure
  const currentStructure = structures.find(s => (s._id || s.id) === data.salaryStructureId);
  const structureComponentIds = currentStructure?.componentIds || [];
  const activeComponents = allComponents.filter(c => structureComponentIds.includes(c._id || c.id));
  
  // Separate into Flat and Others
  const flatComponents = activeComponents.filter(c => c.calculationMethod === 'Flat');
  const otherComponents = activeComponents.filter(c => c.calculationMethod !== 'Flat');

  // When structure changes, we want to prefill customComponents with default flat amounts if they aren't set
  useEffect(() => {
    if (data.salaryStructureId && currentStructure) {
      const newCustomComps = { ...(data.customComponents || {}) };
      let changed = false;
      flatComponents.forEach(c => {
        const cid = c._id || c.id;
        if (newCustomComps[cid] === undefined) {
          newCustomComps[cid] = c.monthlyAmount || c.amount || 0;
          changed = true;
        }
      });
      if (changed) {
        onChange({ ...data, customComponents: newCustomComps, isSalaryPreviewCalculated: false });
        setPreview(null);
      }
    }
  }, [data.salaryStructureId, currentStructure, flatComponents]);

  // When input changes, reset preview calculation
  useEffect(() => {
    if (data.isSalaryPreviewCalculated) {
      onChange({ ...data, isSalaryPreviewCalculated: false });
      setPreview(null);
    }
  }, [data.salaryStructureId, data.basicSalary, data.pfOption, data.esiOption, data.ptState, data.customComponents]);

  const handleChange = (field: string, value: any) => {
    onChange({ ...data, [field]: value, isSalaryPreviewCalculated: false });
    setPreview(null);
  };

  const handleCustomComponentChange = (cid: string, value: number) => {
    const newCustomComps = { ...(data.customComponents || {}), [cid]: value };
    onChange({ ...data, customComponents: newCustomComps, isSalaryPreviewCalculated: false });
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
        ptState: data.ptState || 'None',
        customComponents: data.customComponents || {}
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
          
          <div className="p-4 bg-brand-50 border border-brand-200 rounded-lg space-y-4">
            <h4 className="text-sm font-semibold text-brand-900 border-b border-brand-200 pb-2">Master Input</h4>
            <Input
              label="Basic Salary (₹)"
              type="number"
              value={data.basicSalary || ''}
              onChange={(e) => handleChange('basicSalary', Number(e.target.value))}
              error={errors.basicSalary}
              required
            />
          </div>

          {currentStructure && flatComponents.length > 0 && (
            <div className="p-4 bg-white border border-neutral-200 shadow-sm rounded-lg space-y-4">
              <h4 className="text-sm font-semibold text-neutral-800 border-b border-neutral-100 pb-2">Flat Components (Editable)</h4>
              {flatComponents.map((c) => {
                const cid = c._id || c.id;
                return (
                  <Input
                    key={cid}
                    label={`${c.name} (₹)`}
                    type="number"
                    value={data.customComponents?.[cid] ?? (c.monthlyAmount || c.amount || '')}
                    onChange={(e) => handleCustomComponentChange(cid, Number(e.target.value))}
                  />
                );
              })}
            </div>
          )}

          {currentStructure && otherComponents.length > 0 && (
            <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-lg space-y-3">
              <h4 className="text-sm font-semibold text-neutral-700 border-b border-neutral-200 pb-2">Calculated Components (Read-only)</h4>
              <div className="flex flex-wrap gap-2">
                {otherComponents.map((c) => (
                  <span key={c._id || c.id} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-neutral-200 text-neutral-800">
                    {c.name} ({c.calculationMethod})
                  </span>
                ))}
              </div>
              <p className="text-xs text-neutral-500 italic mt-2">These will be automatically calculated when you click Calculate.</p>
            </div>
          )}

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
            className="w-full flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-neutral-200 disabled:text-neutral-400 focus:ring-green-500 font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
          >
            <Calculator className="w-5 h-5 mr-2" />
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
