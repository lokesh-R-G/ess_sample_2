import React, { useState, useEffect } from 'react';
import { Input, Select } from '../../../components/ui';
import { organizationApi } from '../../../services/organization.api';
import { employeeApi } from '../../../services/employeeApi';
import { Calculator } from 'lucide-react';
import GlassCard from '../../../components/ui/GlassCard';

export default function SalaryPreviewPage() {
  const [structures, setStructures] = useState<any[]>([]);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [preview, setPreview] = useState<any>(null);

  const [data, setData] = useState({
    salaryStructureId: '',
    basicSalary: '',
    pfOption: 'Default',
    esiOption: 'Default',
    ptState: 'None'
  });

  useEffect(() => {
    const fetchStructures = async () => {
      try {
        const res = await organizationApi.getSalaryStructures();
        setStructures(res?.data || res || []);
      } catch (e) {
        console.error(e);
      }
    };
    fetchStructures();
  }, []);

  const handleChange = (field: string, value: any) => {
    setData(prev => ({ ...prev, [field]: value }));
  };

  const generatePreview = async () => {
    if (!data.salaryStructureId || !data.basicSalary) return;
    
    setLoadingPreview(true);
    try {
      const res = await employeeApi.calculatePayslipPreview({
        salaryStructureId: data.salaryStructureId,
        basicSalary: Number(data.basicSalary),
        pfOption: data.pfOption,
        esiOption: data.esiOption,
        ptState: data.ptState
      });
      setPreview(res?.data || res || null);
    } catch (e) {
      console.error("Preview failed", e);
    } finally {
      setLoadingPreview(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 flex items-center">
            <Calculator className="w-6 h-6 mr-2 text-brand-600" />
            Salary Preview Calculator
          </h1>
          <p className="text-neutral-500 mt-1">Simulate exact payroll calculations without saving any employee data.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Side: Input Form */}
        <div className="col-span-1 space-y-6">
          <GlassCard className="p-6 space-y-6">
            <Select
              label="Salary Structure"
              value={data.salaryStructureId}
              onChange={(e) => handleChange('salaryStructureId', e.target.value)}
              options={[
                { value: '', label: 'Select Structure' },
                ...structures.map(s => ({ value: s._id || s.id, label: s.name }))
              ]}
              required
            />
            
            <Input
              label="Basic Salary (₹)"
              type="number"
              value={data.basicSalary}
              onChange={(e) => handleChange('basicSalary', e.target.value)}
              required
            />

            <Select
              label="PF Calculation Option"
              value={data.pfOption}
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
              value={data.esiOption}
              onChange={(e) => handleChange('esiOption', e.target.value)}
              options={[
                { value: 'Default', label: 'Calculate if eligible' },
                { value: 'OptOut', label: 'Opt-Out' }
              ]}
            />

            <Select
              label="Professional Tax State"
              value={data.ptState}
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
              className="w-full px-4 py-2 bg-brand-600 text-white rounded hover:bg-brand-700 disabled:opacity-50 text-sm font-medium"
            >
              {loadingPreview ? 'Calculating...' : 'Calculate Preview'}
            </button>
          </GlassCard>
        </div>

        {/* Right Side: Payslip Preview */}
        <div className="col-span-1 lg:col-span-2">
          <GlassCard className="p-6 bg-neutral-50 border border-neutral-200">
            <h4 className="text-lg font-bold text-neutral-800 mb-6">Calculation Results</h4>
            
            {!preview && !loadingPreview && (
              <div className="text-center text-neutral-400 py-20 text-sm">
                Enter parameters and click Calculate to view the full simulation.
              </div>
            )}

            {preview && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-6">
                  {/* Earnings */}
                  <div className="bg-white p-4 rounded shadow-sm border border-neutral-200">
                    <h5 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">Earnings & Formula</h5>
                    {preview.earnings?.map((e: any, i: number) => (
                      <div key={i} className="flex justify-between items-center text-sm py-1.5 border-b border-neutral-50 last:border-0">
                        <div>
                           <span className="text-neutral-700 block">{e.name}</span>
                           <span className="text-[10px] text-brand-600 bg-brand-50 px-1 rounded">{e.formula}</span>
                        </div>
                        <span className="font-medium text-neutral-900">₹{e.amount?.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>

                  {/* Distribution Snapshot */}
                  <div className="bg-white p-4 rounded shadow-sm border border-neutral-200">
                    <h5 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">Salary Distribution Snapshot</h5>
                    {preview.distribution?.map((d: any, i: number) => (
                      <div key={i} className="flex justify-between items-center text-sm py-1.5 border-b border-neutral-50 last:border-0">
                        <span className="text-neutral-700">
                          {d.name} <span className="text-[10px] text-neutral-400">({d.attendanceDependent ? 'LOP' : 'Fixed'})</span>
                        </span>
                        <div className="text-right">
                          <span className="font-medium text-neutral-900 block">₹{d.amount?.toFixed(2)}</span>
                          <span className="text-[10px] text-green-600 bg-green-50 px-1 rounded">{d.distributionPercentage?.toFixed(2)}% of Gross</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-6">
                  {/* Statutory & Deductions */}
                  <div className="bg-white p-4 rounded shadow-sm border border-neutral-200">
                    <h5 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">Statutory & Deductions</h5>
                    
                    <div className="mb-3 p-2 bg-neutral-50 rounded text-xs text-neutral-600 space-y-1">
                      <div className="font-semibold text-neutral-800">PF Breakup</div>
                      <div className="flex justify-between"><span>PF Gross:</span> <span>₹{preview.statutory?.pf?.pfGross?.toFixed(2)}</span></div>
                      <div className="flex justify-between"><span>Ceiling Applied:</span> <span>{preview.statutory?.pf?.ceilingApplied ? 'Yes' : 'No'}</span></div>
                      <div className="flex justify-between"><span>PF Wage Used:</span> <span>₹{preview.statutory?.pf?.pfWageUsed?.toFixed(2)}</span></div>
                    </div>

                    {preview.deductions?.map((d: any, i: number) => (
                      <div key={i} className="flex justify-between text-sm py-1">
                        <span className="text-neutral-700">{d.name}</span>
                        <span className="font-medium text-red-600">-₹{d.amount?.toFixed(2)}</span>
                      </div>
                    ))}
                    <div className="flex justify-between text-sm py-2 mt-2 border-t border-neutral-100 font-bold">
                      <span>Total Employee Deductions</span>
                      <span className="text-red-600">₹{preview.summary?.totalDeductions?.toFixed(2)}</span>
                    </div>
                  </div>

                  {/* Employer Contributions */}
                  <div className="bg-white p-4 rounded shadow-sm border border-neutral-200">
                    <h5 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">Employer Contributions</h5>
                    {preview.employerContributions?.map((ec: any, i: number) => (
                      <div key={i} className="flex justify-between text-sm py-1">
                        <span className="text-neutral-700">{ec.name}</span>
                        <span className="font-medium text-neutral-900">₹{ec.amount?.toFixed(2)}</span>
                      </div>
                    ))}
                    <div className="flex justify-between text-sm py-2 mt-2 border-t border-neutral-100 font-bold">
                      <span>Total Contribution</span>
                      <span className="text-neutral-700">₹{preview.summary?.employerContribution?.toFixed(2)}</span>
                    </div>
                  </div>

                  {/* Summary */}
                  <div className="bg-gradient-to-br from-brand-50 to-brand-100 p-5 rounded-xl border border-brand-200 shadow-sm space-y-3">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-brand-800 font-semibold">Gross Salary</span>
                      <span className="text-brand-900 font-bold">₹{preview.summary?.grossSalary?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-brand-900 font-bold">Net Take Home</span>
                      <span className="text-brand-700 font-black text-2xl">₹{preview.summary?.takeHome?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center pt-3 border-t border-brand-200/50 text-sm">
                      <span className="text-brand-800">Monthly CTC</span>
                      <span className="font-semibold text-brand-900">₹{preview.summary?.monthlyCtc?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-brand-800">Annual CTC</span>
                      <span className="font-bold text-brand-900 text-lg">₹{preview.summary?.annualCtc?.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

              </div>
            )}
          </GlassCard>
        </div>

      </div>
    </div>
  );
}
