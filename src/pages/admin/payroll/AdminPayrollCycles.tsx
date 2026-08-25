import React, { useEffect, useState } from 'react';
import { GlassCard, AnimatedButton, Input } from '../../../components/ui';
import { payrollCycleApi, PayrollCycle } from '../../../services/payrollCycleApi';
import { toast } from 'react-hot-toast';
import { useAuth } from '../../../context/AuthContext';

export default function AdminPayrollCycles() {
  const { hasPermission } = useAuth();
  const [cycles, setCycles] = useState<PayrollCycle[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [newCycle, setNewCycle] = useState({ name: '', startDate: '', endDate: '' });
  const [calculatingCycle, setCalculatingCycle] = useState<string | null>(null);
  const [confirmCalcModal, setConfirmCalcModal] = useState<PayrollCycle | null>(null);

  useEffect(() => {
    fetchCycles();
  }, []);

  const fetchCycles = async () => {
    try {
      const data = await payrollCycleApi.getCycles();
      setCycles(data || []);
    } catch (error) {
      toast.error('Failed to load payroll cycles');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await payrollCycleApi.createCycle(newCycle);
      toast.success('Cycle created successfully');
      setIsCreating(false);
      setNewCycle({ name: '', startDate: '', endDate: '' });
      fetchCycles();
    } catch (error) {
      toast.error('Failed to create cycle');
    }
  };

  const handleStatusChange = async (cycleId: string, newStatus: string) => {
    try {
      await payrollCycleApi.updateStatus(cycleId, newStatus);
      toast.success(`Cycle transitioned to ${newStatus}`);
      fetchCycles();
    } catch (error: any) {
      toast.error(error.message || 'Failed to update cycle status');
    }
  };

  const handleCalculatePayroll = async () => {
    if (!confirmCalcModal) return;
    setCalculatingCycle(confirmCalcModal.id);
    setConfirmCalcModal(null);
    try {
      const summary = await payrollCycleApi.calculatePayroll(confirmCalcModal.id);
      if (summary.failed > 0) {
        toast.error(`Calculation finished with ${summary.failed} errors.`);
      } else {
        toast.success(`Payroll calculated successfully for ${summary.successfullyCalculated} employees.`);
      }
      fetchCycles();
    } catch (error: any) {
      toast.error(error.message || 'Failed to calculate payroll');
    } finally {
      setCalculatingCycle(null);
    }
  };

  const handlePublish = async (cycleId: string) => {
    try {
      const res = await payrollCycleApi.publishCycle(cycleId);
      toast.success(`Published payslips! Dispatched ${res.publishedPayslips} emails.`);
      fetchCycles();
    } catch (error: any) {
      toast.error(error.message || 'Failed to publish payslips');
    }
  };

  if (loading) return <div className="p-6 text-center text-neutral-500">Loading Cycles...</div>;

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-neutral-900">Payroll Cycles (V2)</h1>
        {hasPermission('payroll.cycle.manage') && (
          <AnimatedButton onClick={() => setIsCreating(true)}>Create Cycle</AnimatedButton>
        )}
      </div>

      {isCreating && (
        <GlassCard className="p-6">
          <h3 className="text-lg font-bold mb-4">Create New Cycle</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input label="Name (e.g. August 2026)" value={newCycle.name} onChange={e => setNewCycle({...newCycle, name: e.target.value})} />
            <Input label="Start Date" type="date" value={newCycle.startDate} onChange={e => setNewCycle({...newCycle, startDate: e.target.value})} />
            <Input label="End Date" type="date" value={newCycle.endDate} onChange={e => setNewCycle({...newCycle, endDate: e.target.value})} />
          </div>
          <div className="mt-4 flex justify-end space-x-2">
            <button className="px-4 py-2 text-sm text-neutral-600" onClick={() => setIsCreating(false)}>Cancel</button>
            <AnimatedButton onClick={handleCreate}>Save Cycle</AnimatedButton>
          </div>
        </GlassCard>
      )}

      <div className="grid grid-cols-1 gap-6">
        {cycles.map(cycle => (
          <GlassCard key={cycle.id} className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-xl font-bold text-neutral-900">{cycle.name}</h3>
                <p className="text-sm text-neutral-500">{new Date(cycle.startDate).toDateString()} - {new Date(cycle.endDate).toDateString()}</p>
                <div className="mt-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-brand-100 text-brand-800">
                  {cycle.processingStatus}
                </div>
              </div>
              <div className="flex flex-col items-end space-y-2">
                {hasPermission('payroll.cycle.manage') && (
                  <>
                    {cycle.processingStatus === 'DRAFT' && (
                      <AnimatedButton onClick={() => handleStatusChange(cycle.id, 'OPEN')}>Open Cycle</AnimatedButton>
                    )}
                    {cycle.processingStatus === 'OPEN' && (
                      <AnimatedButton onClick={() => handleStatusChange(cycle.id, 'APPROVAL_PENDING')}>Request Approvals</AnimatedButton>
                    )}
                    {cycle.processingStatus === 'APPROVAL_PENDING' && (
                      <AnimatedButton onClick={() => handleStatusChange(cycle.id, 'APPROVAL_LOCKED')}>Lock Approvals</AnimatedButton>
                    )}
                    {cycle.processingStatus === 'APPROVAL_LOCKED' && (
                      <AnimatedButton onClick={() => handleStatusChange(cycle.id, 'ATTENDANCE_FINALIZED')}>Finalize Attendance</AnimatedButton>
                    )}
                    {cycle.processingStatus === 'ATTENDANCE_FINALIZED' && (
                      <AnimatedButton 
                        onClick={() => setConfirmCalcModal(cycle)}
                        disabled={calculatingCycle === cycle.id}
                      >
                        {calculatingCycle === cycle.id ? 'Calculating...' : 'Calculate Payroll'}
                      </AnimatedButton>
                    )}
                    {cycle.processingStatus === 'PROCESSING' && (
                      <div className="text-sm text-amber-600 font-medium">Processing or Failed</div>
                    )}
                    {cycle.processingStatus === 'CALCULATED' && (
                      <AnimatedButton onClick={() => handleStatusChange(cycle.id, 'ADMIN_REVIEW')}>Send to Admin Review</AnimatedButton>
                    )}
                    {cycle.processingStatus === 'ADMIN_REVIEW' && (
                      <>
                        <AnimatedButton onClick={() => handleStatusChange(cycle.id, 'FINALIZED')}>Finalize Payroll</AnimatedButton>
                        {/* Note: Recalculate happens in AdminPayrollReview */}
                      </>
                    )}
                    {cycle.processingStatus === 'FINALIZED' && (
                      <AnimatedButton onClick={() => handlePublish(cycle.id)}>Publish Payslips</AnimatedButton>
                    )}
                    {['FINALIZED', 'PUBLISHED'].includes(cycle.processingStatus) && (
                      <AnimatedButton variant="secondary" onClick={() => window.location.href = `/admin/payroll/export/${cycle.id}`}>Bank Export</AnimatedButton>
                    )}
                    {['PUBLISHED', 'EXPORTED'].includes(cycle.processingStatus) && (
                      <AnimatedButton onClick={() => handleStatusChange(cycle.id, 'CLOSED')}>Close Cycle</AnimatedButton>
                    )}
                  </>
                )}
                
                {/* Link to Review UI */}
                {['CALCULATED', 'ADMIN_REVIEW', 'FINALIZED', 'PUBLISHED', 'EXPORTED', 'CLOSED'].includes(cycle.processingStatus) && (
                  <AnimatedButton variant="outline" onClick={() => window.location.href = `/admin/payroll/review/${cycle.id}`}>View Payrolls</AnimatedButton>
                )}
              </div>
            </div>
          </GlassCard>
        ))}
        {cycles.length === 0 && !loading && (
          <div className="text-center text-neutral-500 py-12">No payroll cycles found. Create one above.</div>
        )}
      </div>

      {/* Confirmation Modal */}
      {confirmCalcModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <GlassCard className="p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-neutral-900 mb-4">Calculate payroll for {confirmCalcModal.name}?</h3>
            <div className="space-y-2 mb-6 text-sm text-neutral-600">
              <p>• Employee count will be determined automatically.</p>
              <p>• Make sure attendance is completely finalized.</p>
              <p>• Make sure there are no pending approvals.</p>
              <p>Current cycle state: <span className="font-semibold">{confirmCalcModal.processingStatus}</span></p>
            </div>
            <div className="flex justify-end space-x-3">
              <button 
                className="px-4 py-2 text-sm text-neutral-600 hover:text-neutral-900 transition-colors"
                onClick={() => setConfirmCalcModal(null)}
              >
                Cancel
              </button>
              <AnimatedButton onClick={handleCalculatePayroll}>
                Confirm Calculation
              </AnimatedButton>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
}
