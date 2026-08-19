import React, { useEffect, useState } from 'react';
import { Download, Printer, Calendar, RefreshCw } from 'lucide-react';
import { GlassCard, AnimatedButton, Select } from '../../components/ui';
import { DashboardLayout } from '../../components/layout';
import { payslipService, Payslip as IPayslip } from '../../services/payslipService';

const MONTHS = [
  { value: '1', label: 'January' }, { value: '2', label: 'February' },
  { value: '3', label: 'March' }, { value: '4', label: 'April' },
  { value: '5', label: 'May' }, { value: '6', label: 'June' },
  { value: '7', label: 'July' }, { value: '8', label: 'August' },
  { value: '9', label: 'September' }, { value: '10', label: 'October' },
  { value: '11', label: 'November' }, { value: '12', label: 'December' }
];

const YEARS = [2026, 2025, 2024];

export const Payslip = () => {
  const [activeTab, setActiveTab] = useState<'historical' | 'preview'>('historical');

  // Historical state
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [payslip, setPayslip] = useState<IPayslip | null>(null);
  const [historicalLoading, setHistoricalLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');

  // Preview state
  const today = new Date();
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
  
  const formatLocal = (d: Date) => {
    const pad = (n: number) => n.toString().padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  };

  const [previewFrom, setPreviewFrom] = useState(formatLocal(firstDay));
  const [previewTo, setPreviewTo] = useState(formatLocal(today));
  const [previewData, setPreviewData] = useState<any>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState('');

  useEffect(() => {
    if (activeTab === 'historical') {
      fetchPayslip();
    }
  }, [selectedMonth, selectedYear, activeTab]);

  const fetchPayslip = async () => {
    setHistoricalLoading(true);
    setStatusMsg('');
    setPayslip(null);
    try {
      const data = await payslipService.getMyPayslip(selectedYear, selectedMonth);
      if (data && data.status === 'NOT_PROCESSED') {
        setStatusMsg(data.message || 'Payroll has not been processed for this month.');
      } else if (data && data.status === 'UNPUBLISHED') {
        setStatusMsg('Payslip is not yet published.');
      } else if (data && data.payloadSnapshot) {
        setPayslip(data);
      } else {
        setStatusMsg('No payslip found.');
      }
    } catch (error) {
      setStatusMsg('Failed to load payslip data.');
    } finally {
      setHistoricalLoading(false);
    }
  };

  const fetchPreview = async () => {
    setPreviewLoading(true);
    setPreviewError('');
    setPreviewData(null);
    try {
      const res = await payslipService.getEarningsPreview(previewFrom, previewTo);
      if (res && res.preview) {
        setPreviewData(res.preview);
      } else {
        setPreviewError('Failed to generate preview.');
      }
    } catch (error: any) {
      setPreviewError(error.response?.data?.detail || 'Failed to generate preview.');
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleDownload = () => {
    window.print();
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <GlassCard className="p-4 flex gap-4">
          <button 
            onClick={() => setActiveTab('historical')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'historical' ? 'bg-brand-600 text-white' : 'text-neutral-600 hover:bg-neutral-100'}`}
          >
            Historical Payslips
          </button>
          <button 
            onClick={() => setActiveTab('preview')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'preview' ? 'bg-brand-600 text-white' : 'text-neutral-600 hover:bg-neutral-100'}`}
          >
            Earnings Preview
          </button>
        </GlassCard>

        {activeTab === 'historical' && (
          <>
            <GlassCard className="p-6">
              <div className="flex flex-col sm:flex-row items-center justify-between mb-4 gap-4">
                <h3 className="text-lg font-semibold text-neutral-900">Historical Payslips</h3>
                <div className="flex gap-4">
                  <Select 
                    label="" 
                    options={MONTHS} 
                    value={String(selectedMonth)} 
                    onChange={(e) => setSelectedMonth(Number(e.target.value))} 
                  />
                  <Select 
                    label="" 
                    options={YEARS.map(y => ({ value: String(y), label: String(y) }))} 
                    value={String(selectedYear)} 
                    onChange={(e) => setSelectedYear(Number(e.target.value))} 
                  />
                </div>
              </div>
            </GlassCard>

            {historicalLoading ? (
              <GlassCard className="p-12 text-center text-neutral-500">Loading Payslip...</GlassCard>
            ) : payslip ? (
              <GlassCard className="overflow-hidden">
                <div className="bg-brand-600 p-8">
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 rounded-2xl bg-white flex items-center justify-center shadow-lg">
                        <span className="text-brand-600 font-bold text-xl">ESS</span>
                      </div>
                      <div>
                        <h1 className="text-2xl font-bold text-white">Salary Payslip</h1>
                        <p className="text-white/90">{MONTHS.find(m => m.value === selectedMonth)?.label} {selectedYear}</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <AnimatedButton variant="secondary" size="sm" icon={Download} onClick={handleDownload}>
                        <span className="text-brand-600">Download PDF</span>
                      </AnimatedButton>
                      <AnimatedButton variant="secondary" size="sm" icon={Printer} onClick={() => window.print()}>
                        <span className="text-brand-600">Print</span>
                      </AnimatedButton>
                    </div>
                  </div>
                </div>

                <div className="p-6 lg:p-8 space-y-6">
                  <div className="flex justify-between items-center bg-neutral-50 p-4 rounded-lg">
                    <div className="text-sm text-neutral-500">
                      Version: {payslip.payloadSnapshot?.version || 1} <br/>
                      Generated: {new Date(payslip.generatedDate).toLocaleDateString()}
                    </div>
                    <div className="text-right">
                      <span className="text-sm text-neutral-500">Net Pay</span>
                      <p className="text-2xl font-bold text-brand-600">
                        {new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(payslip.payloadSnapshot?.netPay || 0)}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Earnings */}
                    <div>
                      <h3 className="font-bold border-b pb-2 mb-4 text-neutral-700">Earnings</h3>
                      <div className="space-y-3 text-sm">
                        {payslip.payloadSnapshot?.components?.map((c: any) => (
                          <div key={c._id} className="flex justify-between">
                            <span className="text-neutral-600">{c.name}</span>
                            <span className="font-medium text-neutral-900">{c.proratedAmount?.toFixed(2)}</span>
                          </div>
                        ))}
                        {payslip.payloadSnapshot?.reimbursementsTotal > 0 && (
                          <div className="flex justify-between">
                            <span className="text-neutral-600">Reimbursements</span>
                            <span className="font-medium text-neutral-900">{payslip.payloadSnapshot.reimbursementsTotal?.toFixed(2)}</span>
                          </div>
                        )}
                        <div className="flex justify-between border-t pt-2 mt-4 font-bold">
                          <span>Total Earnings</span>
                          <span>{(payslip.payloadSnapshot?.grossEarnings + (payslip.payloadSnapshot?.reimbursementsTotal || 0))?.toFixed(2)}</span>
                        </div>
                      </div>
                    </div>

                    {/* Deductions */}
                    <div>
                      <h3 className="font-bold border-b pb-2 mb-4 text-neutral-700">Deductions</h3>
                      <div className="space-y-3 text-sm">
                        <div className="flex justify-between">
                          <span className="text-neutral-600">Provident Fund (PF)</span>
                          <span className="font-medium text-neutral-900">{payslip.payloadSnapshot?.pfCalculation?.employeePf?.toFixed(2) || '0.00'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-neutral-600">ESI</span>
                          <span className="font-medium text-neutral-900">{payslip.payloadSnapshot?.esiCalculation?.employeeEsi?.toFixed(2) || '0.00'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-neutral-600">Professional Tax (PT)</span>
                          <span className="font-medium text-neutral-900">{payslip.payloadSnapshot?.ptAmount?.toFixed(2) || '0.00'}</span>
                        </div>
                        <div className="flex justify-between border-t pt-2 mt-4 font-bold">
                          <span>Total Deductions</span>
                          <span>{payslip.payloadSnapshot?.grossDeductions?.toFixed(2)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-neutral-50 p-4 rounded mt-6 text-sm text-neutral-600">
                    <strong>Attendance & LOP Summary:</strong> Working Days: {payslip.payloadSnapshot?.workingDays} | 
                    Total LOP: {payslip.payloadSnapshot?.lopBreakdown?.totalLopDays} days
                  </div>
                </div>
              </GlassCard>
            ) : (
              <GlassCard className="p-12 text-center border-dashed border-2 border-neutral-200">
                <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Calendar className="w-8 h-8 text-neutral-400" />
                </div>
                <h3 className="text-lg font-bold text-neutral-900 mb-2">No Payslip Available</h3>
                <p className="text-neutral-500">{statusMsg}</p>
              </GlassCard>
            )}
          </>
        )}

        {activeTab === 'preview' && (
          <>
            <GlassCard className="p-6">
              <div className="flex flex-col sm:flex-row items-end gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-neutral-700 mb-1">From Date</label>
                  <input 
                    type="date"
                    value={previewFrom}
                    onChange={e => setPreviewFrom(e.target.value)}
                    className="w-full rounded-lg border-neutral-300 shadow-sm focus:border-brand-500 focus:ring-brand-500"
                  />
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-medium text-neutral-700 mb-1">To Date</label>
                  <input 
                    type="date"
                    value={previewTo}
                    onChange={e => setPreviewTo(e.target.value)}
                    className="w-full rounded-lg border-neutral-300 shadow-sm focus:border-brand-500 focus:ring-brand-500"
                  />
                </div>
                <AnimatedButton onClick={fetchPreview} icon={RefreshCw} disabled={previewLoading}>
                  {previewLoading ? 'Calculating...' : 'Calculate Preview'}
                </AnimatedButton>
              </div>
              {previewError && (
                <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md text-sm border border-red-200">
                  {previewError}
                </div>
              )}
            </GlassCard>

            {previewData && (
              <GlassCard className="overflow-hidden border-2 border-brand-200 shadow-lg">
                <div className="bg-gradient-to-r from-brand-600 to-brand-800 p-6 flex justify-between items-center text-white">
                  <div>
                    <h2 className="text-xl font-bold flex items-center gap-2">
                      <RefreshCw className="w-5 h-5" /> Estimated Earnings Preview
                    </h2>
                    <p className="text-brand-100 text-sm">This is an estimation and has not been finalized.</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-brand-100">Estimated Net Pay</div>
                    <div className="text-3xl font-bold">
                      {new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(previewData.netPay || 0)}
                    </div>
                  </div>
                </div>

                <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div>
                    <h3 className="font-bold border-b pb-2 mb-4 text-neutral-700">Estimated Earnings</h3>
                    <div className="space-y-3 text-sm">
                      {previewData.components?.map((c: any) => (
                        <div key={c._id} className="flex justify-between">
                          <span className="text-neutral-600">{c.name}</span>
                          <span className="font-medium text-neutral-900">{c.proratedAmount?.toFixed(2)}</span>
                        </div>
                      ))}
                      {previewData.reimbursementsTotal > 0 && (
                        <div className="flex justify-between">
                          <span className="text-neutral-600">Eligible Reimbursements</span>
                          <span className="font-medium text-neutral-900">{previewData.reimbursementsTotal?.toFixed(2)}</span>
                        </div>
                      )}
                      <div className="flex justify-between border-t pt-2 mt-4 font-bold">
                        <span>Gross Earnings + Reimb.</span>
                        <span>{(previewData.grossEarnings + (previewData.reimbursementsTotal || 0))?.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-bold border-b pb-2 mb-4 text-neutral-700">Estimated Deductions</h3>
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-neutral-600">Provident Fund (PF)</span>
                        <span className="font-medium text-neutral-900">{previewData.pfCalculation?.employeePf?.toFixed(2) || '0.00'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-neutral-600">ESI</span>
                        <span className="font-medium text-neutral-900">{previewData.esiCalculation?.employeeEsi?.toFixed(2) || '0.00'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-neutral-600">Professional Tax (PT)</span>
                        <span className="font-medium text-neutral-900">{previewData.ptAmount?.toFixed(2) || '0.00'}</span>
                      </div>
                      <div className="flex justify-between border-t pt-2 mt-4 font-bold">
                        <span>Total Deductions</span>
                        <span>{previewData.grossDeductions?.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-neutral-50 p-4 border-t text-sm text-neutral-600">
                  <strong>Attendance Used:</strong> {previewData.workingDays} working days, {previewData.lopBreakdown?.totalLopDays} LOP days.
                  <br />
                  <span className="text-xs text-neutral-400">Note: Actual payout may vary if attendance is modified before finalization.</span>
                </div>
              </GlassCard>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
};

export default Payslip;
