import React, { useEffect, useState } from 'react';
import { Input, Select } from '../../../../components/ui';
import { organizationApi } from '../../../../services/organization.api';
import { employeeApi } from '../../../../services/employeeApi';
import { payrollRulesApi } from '../../../../services/payrollRulesApi';
import { Calculator, ArrowRight, CheckCircle2 } from 'lucide-react';

interface SalaryPayrollStepProps {
  data: any;
  onChange: (data: any) => void;
  errors?: Record<string, string>;
}

export default function SalaryPayrollStep({ data, onChange, errors = {} }: SalaryPayrollStepProps) {
  const [structures, setStructures] = useState<any[]>([]);
  const [allComponents, setAllComponents] = useState<any[]>([]);
  const [activePfRule, setActivePfRule] = useState<any>(null);
  const [activeEsiRule, setActiveEsiRule] = useState<any>(null);
  
  const [stage, setStage] = useState<1 | 2>(1);
  const [grossPreview, setGrossPreview] = useState<any>(null);
  const [preview, setPreview] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      const [structRes, compRes, pfRes, esiRes] = await Promise.all([
        organizationApi.getSalaryStructures(),
        organizationApi.getSalaryComponents(),
        payrollRulesApi.getPFRules(),
        payrollRulesApi.getESIRules()
      ]);
      setStructures(structRes?.data || structRes || []);
      setAllComponents(compRes?.data || compRes || []);
      
      const pfRules = pfRes?.data || pfRes || [];
      const esiRules = esiRes?.data || esiRes || [];
      setActivePfRule(pfRules.find((r: any) => r.status === 'Active' || r.isActive) || null);
      setActiveEsiRule(esiRules.find((r: any) => r.status === 'Active' || r.isActive) || null);
    } catch (e) {
      console.error(e);
    }
  };

  const currentStructure = structures.find(s => (s._id || s.id) === data.salaryStructureId);
  const structureComponentIds = currentStructure?.componentIds || [];
  const activeComponents = allComponents.filter(c => structureComponentIds.includes(c._id || c.id));
  
  const flatComponents = activeComponents.filter(c => c.calculationMethod === 'Flat');
  const otherComponents = activeComponents.filter(c => c.calculationMethod !== 'Flat');

  useEffect(() => {
    if (data.salaryStructureId && currentStructure) {
      const newCustomComps = { ...(data.customComponents || {}) };
      let changed = false;
      flatComponents.forEach(c => {
        const cid = c._id || c.id;
        if (newCustomComps[cid] === undefined) {
          newCustomComps[cid] = c.monthlyAmount || 0;
          changed = true;
        }
      });
      if (changed) {
        onChange({ ...data, customComponents: newCustomComps, isSalaryPreviewCalculated: false });
        setStage(1);
        setGrossPreview(null);
        setPreview(null);
      }
    }
  }, [data.salaryStructureId, currentStructure, flatComponents]);

  useEffect(() => {
    if (data.isSalaryPreviewCalculated && stage === 1) {
      onChange({ ...data, isSalaryPreviewCalculated: false });
      setPreview(null);
      setGrossPreview(null);
    }
  }, [data.salaryStructureId, data.basicSalary, data.customComponents]);

  const handleChange = (field: string, value: any) => {
    onChange({ ...data, [field]: value, isSalaryPreviewCalculated: false });
    if (stage === 2 && ['salaryStructureId', 'basicSalary'].includes(field)) {
        setStage(1);
        setGrossPreview(null);
        setPreview(null);
    }
  };

  const handleMultipleChanges = (updates: any) => {
    onChange({ ...data, ...updates, isSalaryPreviewCalculated: false });
    setStage(1);
    setGrossPreview(null);
    setPreview(null);
  };

  const handleCustomComponentChange = (cid: string, value: number) => {
    const newCustomComps = { ...(data.customComponents || {}), [cid]: value };
    onChange({ ...data, customComponents: newCustomComps, isSalaryPreviewCalculated: false });
    setStage(1);
    setGrossPreview(null);
    setPreview(null);
  };

  const generateGross = async () => {
    if (!data.salaryStructureId || !data.basicSalary) return;
    setLoading(true);
    try {
      const res = await employeeApi.calculateGross({
        salaryStructureId: data.salaryStructureId,
        basicSalary: Number(data.basicSalary),
        customComponents: data.customComponents || {}
      });
      setGrossPreview(res?.data || res || null);
      
      // Setup Defaults for Stage 2 only if missing
      onChange({ 
          ...data, 
          isFresher: data.isFresher ?? true, 
          wantsPf: data.wantsPf ?? true, 
          wantsPension: data.wantsPension ?? true, 
          pfCalculationMode: data.pfCalculationMode && data.pfCalculationMode !== 'Default' ? data.pfCalculationMode : 'Actual',
          isExistingPensionMember: data.isExistingPensionMember ?? false,
          isSalaryPreviewCalculated: false
      });
      setPreview(null);
      setStage(2);
    } catch (e) {
      console.error("Gross generation failed", e);
    } finally {
      setLoading(false);
    }
  };

  const generatePreview = async () => {
    if (!data.salaryStructureId || !data.basicSalary) return;
    setLoading(true);
    try {
      const res = await employeeApi.calculatePayslipPreview({
        salaryStructureId: data.salaryStructureId,
        basicSalary: Number(data.basicSalary),
        ptState: data.ptState || 'None',
        customComponents: data.customComponents || {},
        isFresher: data.isFresher ?? true,
        wantsPf: data.wantsPf ?? true,
        wantsPension: data.wantsPension ?? true,
        pfCalculationMode: data.pfCalculationMode && data.pfCalculationMode !== 'Default' ? data.pfCalculationMode : 'Actual',
        isExistingPensionMember: data.isExistingPensionMember ?? false,
        esiEnabled: data.esiEnabled ?? true
      });
      setPreview(res?.data || res || null);
      onChange({ ...data, isSalaryPreviewCalculated: true });
    } catch (e) {
      console.error("Preview failed", e);
    } finally {
      setLoading(false);
    }
  };

  const pfEnabled = activePfRule?.pfEnabled !== false;
  const esiEnabled = activeEsiRule?.esiEnabled !== false;
  const pfCeiling = activePfRule?.pfCeilingAmount || 15000;
  const esiCeiling = activeEsiRule?.eligibilityGross || 21000;
  
  const pfGross = grossPreview?.pfGross || 0;
  const esiGross = grossPreview?.esiGross || 0;
  const isEsiEligible = esiGross <= esiCeiling;
  const isPfBelowCeiling = pfGross <= pfCeiling;

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-bold text-neutral-900 mb-4">Salary & Payroll Calculator</h3>
      
      {errors.general && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {errors.general}
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        
        {/* Left Side: Form */}
        <div className="space-y-6">
          
          {/* Stage 1: Salary Composition */}
          <div className={`p-5 border rounded-xl shadow-sm transition-all ${stage === 1 ? 'border-brand-300 bg-white' : 'border-neutral-200 bg-neutral-50 opacity-70'}`}>
              <h4 className="text-md font-bold text-neutral-800 mb-4 flex items-center">
                  <span className="bg-brand-100 text-brand-700 w-6 h-6 rounded-full inline-flex items-center justify-center text-sm mr-2">1</span>
                  Salary Composition
              </h4>
              
              <div className="space-y-4">
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
                            value={data.customComponents?.[cid] ?? (c.monthlyAmount || '')}
                            onChange={(e) => handleCustomComponentChange(cid, Number(e.target.value))}
                          />
                        );
                      })}
                    </div>
                  )}

                  {currentStructure && otherComponents.length > 0 && (
                    <div className="p-3 bg-neutral-100 border border-neutral-200 rounded-lg">
                      <h4 className="text-xs font-semibold text-neutral-600 mb-2">Calculated Automatically:</h4>
                      <div className="flex flex-wrap gap-2">
                        {otherComponents.map((c) => (
                          <span key={c._id || c.id} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-neutral-200 text-neutral-700">
                            {c.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

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

                  {stage === 1 && (
                      <button
                        onClick={(e) => { e.preventDefault(); generateGross(); }}
                        disabled={loading || !data.salaryStructureId || !data.basicSalary}
                        className="w-full flex items-center justify-center px-4 py-3 bg-neutral-800 text-white rounded-lg hover:bg-neutral-900 disabled:bg-neutral-200 disabled:text-neutral-400 font-semibold transition-colors"
                      >
                        {loading ? 'Calculating...' : 'Generate Gross'}
                        <ArrowRight className="w-5 h-5 ml-2" />
                      </button>
                  )}
              </div>
          </div>

          {/* Stage 2: Statutory Logic */}
          {stage === 2 && grossPreview && (
              <div className="p-5 border border-brand-300 bg-white rounded-xl shadow-sm transition-all space-y-6 animate-in slide-in-from-top-4">
                  <div className="flex justify-between items-center mb-2">
                    <h4 className="text-md font-bold text-neutral-800 flex items-center">
                        <span className="bg-brand-100 text-brand-700 w-6 h-6 rounded-full inline-flex items-center justify-center text-sm mr-2">2</span>
                        Statutory Logic
                    </h4>
                    <div className="text-right text-xs">
                        <div className="font-semibold text-brand-700">Gross: ₹{grossPreview.grossSalary?.toFixed(2)}</div>
                        <div className="text-neutral-500">PF Gross: ₹{grossPreview.pfGross?.toFixed(2)} | ESI Gross: ₹{grossPreview.esiGross?.toFixed(2)}</div>
                    </div>
                  </div>

                  {/* ESI Section */}
                  <div className="p-4 bg-neutral-50 rounded-lg border border-neutral-200">
                      <h5 className="font-semibold text-sm text-neutral-800 mb-2">ESI Calculation</h5>
                      {esiEnabled ? (
                          isEsiEligible ? (
                              <div className="text-sm text-green-700 flex items-center">
                                  <CheckCircle2 className="w-4 h-4 mr-2" />
                                  ESI Gross (₹{esiGross}) is below ceiling (₹{esiCeiling}). ESI will be automatically deducted.
                              </div>
                          ) : (
                              <div className="text-sm text-neutral-500 flex items-center">
                                  <CheckCircle2 className="w-4 h-4 mr-2 text-neutral-400" />
                                  ESI Gross (₹{esiGross}) exceeds ceiling (₹{esiCeiling}). ESI skipped.
                              </div>
                          )
                      ) : (
                          <div className="text-sm text-neutral-500">ESI is globally disabled in rules.</div>
                      )}
                  </div>

                  {/* PF Section */}
                  <div className="p-4 bg-neutral-50 rounded-lg border border-neutral-200 space-y-4">
                      <h5 className="font-semibold text-sm text-neutral-800">PF Calculation</h5>
                      
                      {!pfEnabled ? (
                           <div className="text-sm text-neutral-500">PF is globally disabled in rules.</div>
                      ) : (
                          <>
                              <div className="space-y-2">
                                  <label className="text-sm font-medium text-neutral-700 block">Is Employee a Fresher?</label>
                                  <div className="flex gap-4">
                                      <label className="flex items-center space-x-2 text-sm cursor-pointer">
                                          <input type="radio" checked={data.isFresher === true} onChange={() => handleMultipleChanges({ isFresher: true, wantsPf: true, wantsPension: true, pfCalculationMode: 'Actual', isExistingPensionMember: false })} className="text-brand-600 focus:ring-brand-500" />
                                          <span>Yes</span>
                                      </label>
                                      <label className="flex items-center space-x-2 text-sm cursor-pointer">
                                          <input type="radio" checked={data.isFresher === false} onChange={() => handleChange('isFresher', false)} className="text-brand-600 focus:ring-brand-500" />
                                          <span>No</span>
                                      </label>
                                  </div>
                              </div>

                              {/* Case 1: Fresher */}
                              {data.isFresher === true && (
                                  isPfBelowCeiling ? (
                                      <div className="text-sm text-green-700 p-3 bg-green-50 rounded border border-green-100 flex items-start">
                                          <CheckCircle2 className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                                          <div>PF Gross (₹{pfGross}) is below ceiling (₹{pfCeiling}).<br/><strong>PF + Pension</strong> will be automatically calculated.</div>
                                      </div>
                                  ) : (
                                      <div className="space-y-4 pl-4 border-l-2 border-brand-200">
                                          <div className="text-sm text-neutral-600 mb-2">PF Gross (₹{pfGross}) exceeds ceiling (₹{pfCeiling}).</div>
                                          
                                          <div className="space-y-2">
                                              <label className="text-sm font-medium text-neutral-700 block">Do they want PF?</label>
                                              <div className="flex gap-4">
                                                  <label className="flex items-center space-x-2 text-sm cursor-pointer">
                                                      <input type="radio" checked={data.wantsPf === true} onChange={() => handleChange('wantsPf', true)} className="text-brand-600 focus:ring-brand-500" />
                                                      <span>Yes</span>
                                                  </label>
                                                  <label className="flex items-center space-x-2 text-sm cursor-pointer">
                                                      <input type="radio" checked={data.wantsPf === false} onChange={() => handleMultipleChanges({ wantsPf: false, wantsPension: false })} className="text-brand-600 focus:ring-brand-500" />
                                                      <span>No</span>
                                                  </label>
                                              </div>
                                          </div>

                                          {data.wantsPf && (
                                              <div className="space-y-2">
                                                  <label className="text-sm font-medium text-neutral-700 block">Do they want Pension?</label>
                                                  <div className="flex gap-4">
                                                      <label className="flex items-center space-x-2 text-sm cursor-pointer">
                                                          <input type="radio" checked={data.wantsPension === true} onChange={() => handleMultipleChanges({ wantsPension: true, pfCalculationMode: 'Ceiling' })} className="text-brand-600 focus:ring-brand-500" />
                                                          <span>Yes</span>
                                                      </label>
                                                      <label className="flex items-center space-x-2 text-sm cursor-pointer">
                                                          <input type="radio" checked={data.wantsPension === false} onChange={() => handleChange('wantsPension', false)} className="text-brand-600 focus:ring-brand-500" />
                                                          <span>No</span>
                                                      </label>
                                                  </div>
                                              </div>
                                          )}

                                          {data.wantsPf && data.wantsPension && (
                                              <div className="text-sm text-green-700 p-2 bg-green-50 rounded border border-green-100 flex items-start">
                                                  <CheckCircle2 className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                                                  Ceiling Wage logic will be automatically applied.
                                              </div>
                                          )}

                                          {data.wantsPf && !data.wantsPension && (
                                              <div className="space-y-2">
                                                  <label className="text-sm font-medium text-neutral-700 block">PF Calculation Mode</label>
                                                  <Select
                                                    value={data.pfCalculationMode || 'Actual'}
                                                    onChange={(e) => handleChange('pfCalculationMode', e.target.value)}
                                                    options={[
                                                      { value: 'Ceiling', label: `Ceiling Wage (₹${pfCeiling})` },
                                                      { value: 'Actual', label: `Actual PF Wage (₹${pfGross})` }
                                                    ]}
                                                  />
                                              </div>
                                          )}
                                      </div>
                                  )
                              )}

                              {/* Case 2: Not a Fresher */}
                              {data.isFresher === false && (
                                  <div className="space-y-4 pl-4 border-l-2 border-brand-200">
                                      <div className="space-y-2">
                                          <label className="text-sm font-medium text-neutral-700 block">Already a Pension Member?</label>
                                          <div className="flex gap-4">
                                              <label className="flex items-center space-x-2 text-sm cursor-pointer">
                                                  <input type="radio" checked={data.isExistingPensionMember === true} onChange={() => handleChange('isExistingPensionMember', true)} className="text-brand-600 focus:ring-brand-500" />
                                                  <span>Yes</span>
                                              </label>
                                              <label className="flex items-center space-x-2 text-sm cursor-pointer">
                                                  <input type="radio" checked={data.isExistingPensionMember === false} onChange={() => handleMultipleChanges({ isExistingPensionMember: false, wantsPension: false })} className="text-brand-600 focus:ring-brand-500" />
                                                  <span>No</span>
                                              </label>
                                          </div>
                                      </div>

                                      <div className="space-y-2">
                                          <label className="text-sm font-medium text-neutral-700 block">Do they want PF?</label>
                                          <div className="flex gap-4">
                                              <label className="flex items-center space-x-2 text-sm cursor-pointer">
                                                  <input type="radio" checked={data.wantsPf === true} onChange={() => handleChange('wantsPf', true)} className="text-brand-600 focus:ring-brand-500" />
                                                  <span>Yes</span>
                                              </label>
                                              <label className="flex items-center space-x-2 text-sm cursor-pointer">
                                                  <input type="radio" checked={data.wantsPf === false} onChange={() => handleMultipleChanges({ wantsPf: false, wantsPension: false })} className="text-brand-600 focus:ring-brand-500" />
                                                  <span>No</span>
                                              </label>
                                          </div>
                                      </div>

                                      {data.wantsPf && data.isExistingPensionMember && (
                                          <div className="space-y-2">
                                              <label className="text-sm font-medium text-neutral-700 block">Do they want Pension?</label>
                                              <div className="flex gap-4">
                                                  <label className="flex items-center space-x-2 text-sm cursor-pointer">
                                                      <input type="radio" checked={data.wantsPension === true} onChange={() => handleMultipleChanges({ wantsPension: true, pfCalculationMode: 'Ceiling' })} className="text-brand-600 focus:ring-brand-500" />
                                                      <span>Yes</span>
                                                  </label>
                                                  <label className="flex items-center space-x-2 text-sm cursor-pointer">
                                                      <input type="radio" checked={data.wantsPension === false} onChange={() => handleChange('wantsPension', false)} className="text-brand-600 focus:ring-brand-500" />
                                                  <span>No</span>
                                                  </label>
                                              </div>
                                          </div>
                                      )}

                                      {data.wantsPf && data.isExistingPensionMember && data.wantsPension && (
                                          <div className="text-sm text-green-700 p-2 bg-green-50 rounded border border-green-100 flex items-start">
                                              <CheckCircle2 className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                                              Ceiling Wage logic will be automatically applied.
                                          </div>
                                      )}

                                      {data.wantsPf && (!data.isExistingPensionMember || !data.wantsPension) && (
                                          <div className="space-y-2">
                                              <label className="text-sm font-medium text-neutral-700 block">PF Calculation Mode</label>
                                              <Select
                                                value={data.pfCalculationMode || 'Actual'}
                                                onChange={(e) => handleChange('pfCalculationMode', e.target.value)}
                                                options={[
                                                  { value: 'Ceiling', label: `Ceiling Wage (₹${pfCeiling})` },
                                                  { value: 'Actual', label: `Actual PF Wage (₹${pfGross})` }
                                                ]}
                                              />
                                              {!data.isExistingPensionMember && <div className="text-xs text-neutral-500 mt-1">Entire employer contribution goes to EPF. No Pension.</div>}
                                          </div>
                                      )}
                                  </div>
                              )}
                          </>
                      )}
                  </div>

                  <button
                    onClick={(e) => { e.preventDefault(); generatePreview(); }}
                    disabled={loading || !data.salaryStructureId || !data.basicSalary}
                    className="w-full flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-neutral-200 disabled:text-neutral-400 focus:ring-green-500 font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
                  >
                    <Calculator className="w-5 h-5 mr-2" />
                    {loading ? 'Calculating Final Salary...' : 'Calculate Final Salary'}
                  </button>
              </div>
          )}

        </div>

        {/* Right Side: Payslip Preview */}
        <div className="bg-neutral-50 rounded-lg p-6 border border-neutral-200">
          <h4 className="text-md font-bold text-neutral-800 mb-4 pb-2 border-b border-neutral-200">
            Final Salary Preview
          </h4>
          
          {!preview && !loading && (
            <div className="text-center text-neutral-400 py-10 text-sm">
              Complete the Statutory Logic section and click Calculate.
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
                  <div className="flex justify-between"><span className="text-neutral-700">Employee PF</span><span className="font-medium text-red-600">-₹{preview.statutory?.pf?.employeePf?.toFixed(2)}</span></div>
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
                  <div className="flex justify-between"><span className="text-neutral-700">Employee ESI</span><span className="font-medium text-red-600">-₹{preview.statutory?.esi?.employeeEsi?.toFixed(2)}</span></div>
                  <div className="flex justify-between"><span className="text-neutral-700">Employer ESI</span><span className="font-medium">₹{preview.statutory?.esi?.employerEsi?.toFixed(2)}</span></div>
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
