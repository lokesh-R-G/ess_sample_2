import React, { useEffect, useState } from 'react';
import { Download, Printer, Calendar } from 'lucide-react';
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
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [payslip, setPayslip] = useState<IPayslip | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');

  useEffect(() => {
    fetchPayslip();
  }, [selectedMonth, selectedYear]);

  const fetchPayslip = async () => {
    setLoading(true);
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
      setLoading(false);
    }
  };

  const handleDownload = () => {
    // Stub for PDF download
    window.print();
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
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

        {loading ? (
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
                    <div className="flex justify-between border-t pt-2 mt-4 font-bold">
                      <span>Total Earnings</span>
                      <span>{payslip.payloadSnapshot?.grossEarnings?.toFixed(2)}</span>
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
      </div>
    </DashboardLayout>
  );
};

export default Payslip;
