import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Download, Printer, Calendar, Building2, CreditCard, User, ChevronRight } from 'lucide-react';
import { GlassCard, AnimatedButton, StatusBadge } from '../../components/ui';
import { DashboardLayout } from '../../components/layout';
import { payslipData, previousPayslips } from '../../data/mockData';

export const Payslip: React.FC = () => {
  const [selectedPayslip, setSelectedPayslip] = useState(payslipData);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Previous Payslips */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <GlassCard className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-neutral-900">Payslip History</h3>
              <AnimatedButton variant="secondary" size="sm" icon={Download}>Export All</AnimatedButton>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {previousPayslips.map((payslip, index) => (
                <motion.button key={payslip.month} onClick={() => setSelectedPayslip({ ...payslipData, month: payslip.month, netPay: payslip.netPay })} className={`p-4 rounded-xl border transition-all text-left ${selectedPayslip.month === payslip.month ? 'bg-primary-50 border-primary-500' : 'bg-neutral-50 border-neutral-200 hover:border-primary-300'}`} initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: index * 0.05 }} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar className="w-4 h-4 text-primary-500" />
                    <span className="text-xs font-medium text-neutral-900 truncate">{payslip.month}</span>
                  </div>
                  <p className="text-lg font-bold text-neutral-900">{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(payslip.netPay)}</p>
                  <StatusBadge status="success" label={payslip.status} size="sm" dot={false} />
                </motion.button>
              ))}
            </div>
          </GlassCard>
        </motion.div>

        {/* Main Payslip */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <GlassCard className="overflow-hidden">
            {/* Header */}
            <div className="bg-primary-500 p-8">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-2xl bg-white flex items-center justify-center shadow-lg">
                    <span className="text-primary-500 font-bold text-xl">IDS</span>
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-white">Salary Payslip</h1>
                    <p className="text-white/90">{selectedPayslip.month}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <AnimatedButton variant="secondary" size="sm" icon={Download}><span className="text-primary-600">Download PDF</span></AnimatedButton>
                  <AnimatedButton variant="secondary" size="sm" icon={Printer}><span className="text-primary-600">Print</span></AnimatedButton>
                </div>
              </div>
            </div>

            {/* Payslip Content */}
            <div className="p-6 lg:p-8 space-y-6">
              {/* Employee Information */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-sm font-semibold text-primary-600 uppercase tracking-wider flex items-center gap-2"><User className="w-4 h-4" />Employee Details</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { label: 'Name', value: selectedPayslip.employee.name },
                      { label: 'Employee ID', value: selectedPayslip.employee.employeeId },
                      { label: 'Designation', value: selectedPayslip.employee.designation },
                      { label: 'Department', value: selectedPayslip.employee.department },
                    ].map((item) => (
                      <div key={item.label} className="p-3 rounded-lg bg-neutral-50 border border-neutral-200">
                        <p className="text-xs text-neutral-500 mb-1">{item.label}</p>
                        <p className="text-sm font-medium text-neutral-900">{item.value}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="space-y-4">
                  <h3 className="text-sm font-semibold text-primary-600 uppercase tracking-wider flex items-center gap-2"><Building2 className="w-4 h-4" />Organization Details</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { label: 'Branch', value: selectedPayslip.employee.branch },
                      { label: 'PAN', value: selectedPayslip.employee.pan },
                      { label: 'UAN', value: selectedPayslip.employee.uan },
                      { label: 'Bank A/C', value: selectedPayslip.employee.bankAccount },
                    ].map((item) => (
                      <div key={item.label} className="p-3 rounded-lg bg-neutral-50 border border-neutral-200">
                        <p className="text-xs text-neutral-500 mb-1">{item.label}</p>
                        <p className="text-sm font-medium text-neutral-900">{item.value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Attendance Summary */}
              <div className="p-4 rounded-xl bg-primary-50 border border-primary-200">
                <h3 className="text-sm font-semibold text-primary-600 uppercase tracking-wider mb-3">Attendance Summary</h3>
                <div className="grid grid-cols-3 sm:grid-cols-4 gap-4">
                  {[
                    { label: 'Present Days', value: selectedPayslip.attendance.presentDays },
                    { label: 'Paid Days', value: selectedPayslip.attendance.paidDays },
                    { label: 'Loss of Pay', value: selectedPayslip.attendance.lossOfPay },
                  ].map((item) => (
                    <div key={item.label} className="text-center">
                      <p className="text-2xl font-bold text-neutral-900">{item.value}</p>
                      <p className="text-xs text-neutral-500">{item.label}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Earnings & Deductions */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                  <h3 className="text-sm font-semibold text-emerald-700 uppercase tracking-wider mb-4 flex items-center gap-2"><ChevronRight className="w-4 h-4" />Earnings</h3>
                  <div className="space-y-3">
                    {Object.entries(selectedPayslip.earnings).filter(([key]) => key !== 'gross').map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between py-2 border-b border-emerald-200 last:border-0">
                        <span className="text-sm text-neutral-600 capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                        <span className="text-sm font-medium text-neutral-900">{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value as number)}</span>
                      </div>
                    ))}
                    <div className="flex items-center justify-between pt-3 border-t-2 border-emerald-300">
                      <span className="text-sm font-semibold text-emerald-700">Gross Earnings</span>
                      <span className="text-lg font-bold text-emerald-700">{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(selectedPayslip.earnings.gross)}</span>
                    </div>
                  </div>
                </div>
                <div className="p-4 rounded-xl bg-red-50 border border-red-200">
                  <h3 className="text-sm font-semibold text-red-700 uppercase tracking-wider mb-4 flex items-center gap-2"><ChevronRight className="w-4 h-4" />Deductions</h3>
                  <div className="space-y-3">
                    {Object.entries(selectedPayslip.deductions).filter(([key]) => key !== 'total').map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between py-2 border-b border-red-200 last:border-0">
                        <span className="text-sm text-neutral-600 capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                        <span className="text-sm font-medium text-neutral-900">{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value as number)}</span>
                      </div>
                    ))}
                    <div className="flex items-center justify-between pt-3 border-t-2 border-red-300">
                      <span className="text-sm font-semibold text-red-700">Total Deductions</span>
                      <span className="text-lg font-bold text-red-700">{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(selectedPayslip.deductions.total)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Net Pay */}
              <motion.div className="p-6 rounded-xl bg-primary-500" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3 }}>
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div>
                    <p className="text-sm text-white/80 mb-1">Net Salary</p>
                    <p className="text-4xl font-bold text-white">{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(selectedPayslip.netPay)}</p>
                    <p className="text-xs text-white/70 mt-1 italic">{selectedPayslip.netPayWords}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <p className="text-xs text-white/70">Paid Days</p>
                      <p className="text-xl font-bold text-white">{selectedPayslip.attendance.paidDays}</p>
                    </div>
                    <div className="w-px h-12 bg-white/30" />
                    <div className="text-right">
                      <p className="text-xs text-white/70">Per Day</p>
                      <p className="text-xl font-bold text-white">{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(selectedPayslip.netPay / selectedPayslip.attendance.paidDays)}</p>
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Footer */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-neutral-200">
                <p className="text-xs text-neutral-500">This is a computer generated document. Generated on {new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-neutral-500">Powered by</span>
                  <span className="text-sm font-semibold text-primary-600">IDS HRMS</span>
                </div>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </DashboardLayout>
  );
};

export default Payslip;
