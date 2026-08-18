import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { GlassCard, AnimatedButton, Input } from '../../../components/ui';
import { payrollReviewApi, PayrollRecord } from '../../../services/payrollReviewApi';
import { payrollCycleApi } from '../../../services/payrollCycleApi';
import { toast } from 'react-hot-toast';

export default function AdminPayrollReview() {
  const { cycleId } = useParams<{ cycleId: string }>();
  const [payrolls, setPayrolls] = useState<PayrollRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPayroll, setSelectedPayroll] = useState<PayrollRecord | null>(null);
  
  // Recalculation modal state
  const [isRecalcOpen, setIsRecalcOpen] = useState(false);
  const [recalcReason, setRecalcReason] = useState('');
  const [recalcEmployeeId, setRecalcEmployeeId] = useState('');

  useEffect(() => {
    if (cycleId) {
      fetchPayrolls();
    }
  }, [cycleId]);

  const fetchPayrolls = async () => {
    try {
      const data = await payrollReviewApi.getPayrollsForCycle(cycleId!);
      setPayrolls(data || []);
    } catch (error) {
      toast.error('Failed to load payroll review data');
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculate = async () => {
    if (!recalcReason) {
      toast.error('Reason is required for audit');
      return;
    }
    try {
      await payrollCycleApi.recalculateEmployee(cycleId!, recalcEmployeeId, recalcReason);
      toast.success('Payroll recalculated. New version created.');
      setIsRecalcOpen(false);
      setRecalcReason('');
      setSelectedPayroll(null);
      fetchPayrolls();
    } catch (error: any) {
      toast.error(error.message || 'Recalculation failed');
    }
  };

  const openRecalcModal = (empId: string) => {
    setRecalcEmployeeId(empId);
    setRecalcReason('');
    setIsRecalcOpen(true);
  };

  if (loading) return <div className="p-6 text-center">Loading Payrolls...</div>;

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
      <h1 className="text-2xl font-bold text-neutral-900">Admin Payroll Review</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <GlassCard className="p-4">
            <h3 className="font-bold mb-4">Calculated Payrolls ({payrolls.length})</h3>
            <div className="space-y-2 max-h-[70vh] overflow-y-auto">
              {payrolls.map(p => (
                <div 
                  key={p._id} 
                  className={`p-3 border rounded cursor-pointer transition-colors ${selectedPayroll?._id === p._id ? 'border-brand-500 bg-brand-50' : 'border-neutral-200 hover:bg-neutral-50'}`}
                  onClick={() => setSelectedPayroll(p)}
                >
                  <div className="font-semibold text-neutral-900">{p.employeeName || p.employeeId}</div>
                  <div className="text-xs text-neutral-500">Net: {p.netPay?.toFixed(2)} | v{p.version}</div>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
        
        <div className="lg:col-span-2">
          {selectedPayroll ? (
            <GlassCard className="p-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-xl font-bold">{selectedPayroll.employeeName || selectedPayroll.employeeId}</h2>
                  <div className="text-sm text-neutral-500">Version: {selectedPayroll.version} (Active)</div>
                  {selectedPayroll.previousVersionId && (
                    <div className="text-xs text-orange-600 mt-1">
                      Recalculated from Version {selectedPayroll.version - 1} | Reason: {selectedPayroll.recalculationReason}
                    </div>
                  )}
                </div>
                <AnimatedButton variant="outline" onClick={() => openRecalcModal(selectedPayroll.employeeId)}>
                  Recalculate
                </AnimatedButton>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-2">Earnings</h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Gross</span>
                      <span className="font-medium">{selectedPayroll.grossEarnings?.toFixed(2)}</span>
                    </div>
                    {/* Render components from snapshot */}
                    {selectedPayroll.payloadSnapshot?.components?.map((c: any) => (
                      <div key={c._id} className="flex justify-between pl-4">
                        <span className="text-neutral-500">{c.name}</span>
                        <span>{c.proratedAmount?.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Deductions</h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Gross Deductions</span>
                      <span className="font-medium">{selectedPayroll.grossDeductions?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between pl-4">
                      <span className="text-neutral-500">PF</span>
                      <span>{selectedPayroll.payloadSnapshot?.pfCalculation?.employeePf?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div className="flex justify-between pl-4">
                      <span className="text-neutral-500">ESI</span>
                      <span>{selectedPayroll.payloadSnapshot?.esiCalculation?.employeeEsi?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div className="flex justify-between pl-4">
                      <span className="text-neutral-500">PT</span>
                      <span>{selectedPayroll.payloadSnapshot?.ptAmount?.toFixed(2) || '0.00'}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-neutral-200">
                <div className="flex justify-between items-center text-lg font-bold">
                  <span>Net Take Home</span>
                  <span className="text-brand-600">{selectedPayroll.netPay?.toFixed(2)}</span>
                </div>
              </div>
              
              <div className="mt-8 p-4 bg-neutral-50 rounded text-sm text-neutral-600">
                <strong>LOP Analysis:</strong> Total LOP Days: {selectedPayroll.payloadSnapshot?.lopBreakdown?.totalLopDays} 
                (Leave: {selectedPayroll.payloadSnapshot?.lopBreakdown?.leaveLopDays}, 
                Permission: {selectedPayroll.payloadSnapshot?.lopBreakdown?.permissionLopDays})
              </div>
            </GlassCard>
          ) : (
            <div className="h-full flex items-center justify-center text-neutral-400 bg-neutral-50 rounded-xl border border-neutral-200 border-dashed">
              Select an employee to view calculation breakdown
            </div>
          )}
        </div>
      </div>

      {isRecalcOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <GlassCard className="p-6 max-w-md w-full">
            <h3 className="text-xl font-bold mb-2">Explicit Recalculation</h3>
            <p className="text-sm text-neutral-500 mb-4">
              Recalculation will create a new payroll version and preserve the existing version for audit.
            </p>
            <Input 
              label="Recalculation Reason (Required for Audit)" 
              value={recalcReason} 
              onChange={e => setRecalcReason(e.target.value)} 
            />
            <div className="mt-6 flex justify-end space-x-3">
              <button className="px-4 py-2 text-neutral-600" onClick={() => setIsRecalcOpen(false)}>Cancel</button>
              <AnimatedButton onClick={handleRecalculate}>Confirm Recalculate</AnimatedButton>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
}
