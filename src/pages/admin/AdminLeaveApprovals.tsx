import React, { useState, useEffect } from 'react';
import { GlassCard, AnimatedButton, StatusBadge, Modal, Input } from '../../components/ui';
import { approvalService } from '../../services/approvalService';

export const AdminLeaveApprovals: React.FC = () => {
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionModal, setActionModal] = useState<{isOpen: boolean, wfId: string, action: 'APPROVE'|'REJECT', remarks: string}>({isOpen: false, wfId: '', action: 'APPROVE', remarks: ''});

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const data = await approvalService.getManagerInbox();
      setRequests(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const submitAction = async () => {
    try {
      await approvalService.executeAction(actionModal.wfId, actionModal.action, actionModal.remarks);
      setActionModal({isOpen: false, wfId: '', action: 'APPROVE', remarks: ''});
      fetchRequests();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <>
      <div className="space-y-6">
        <GlassCard className="p-6">
          <h2 className="text-xl font-bold text-neutral-900 mb-4">Pending Approvals</h2>
          {loading ? (
            <p>Loading requests...</p>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-neutral-200 text-sm text-neutral-500">
                  <th className="py-3 px-4">Employee Code</th>
                  <th className="py-3 px-4">Request Type</th>
                  <th className="py-3 px-4">Details</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {requests.map((req) => (
                  <tr key={req.id} className="border-b border-neutral-100 text-sm">
                    <td className="py-3 px-4">
                      <div className="font-medium text-neutral-900">{req.employeeCode || req.employeeId}</div>
                      {req.employeeName && req.employeeName !== req.employeeCode && (
                        <div className="text-xs text-neutral-500">{req.employeeName}</div>
                      )}
                    </td>
                    <td className="py-3 px-4 font-medium text-neutral-700">
                      {req.approvalType}
                    </td>
                    <td className="py-3 px-4 text-neutral-600">
                      {req.requestData ? (
                        <>
                          <div className="font-medium">
                            {req.requestData.date || req.requestData.fromDate || ''} 
                            {req.requestData.toDate && req.requestData.toDate !== req.requestData.fromDate ? ` to ${req.requestData.toDate}` : ''}
                          </div>
                          {req.requestData.leaveType && (
                             <div className="text-xs font-semibold text-primary-600">{req.requestData.leaveType}</div>
                          )}
                          {req.requestData.punchTime && (
                             <div className="text-xs">Punch Time: {new Date(req.requestData.punchTime).toLocaleString()}</div>
                          )}
                          {req.requestData.fromTime && (
                             <div className="text-xs">Time: {req.requestData.fromTime} to {req.requestData.toTime}</div>
                          )}
                          <div className="text-xs italic">"{req.remarks || req.requestData.reason || ''}"</div>
                        </>
                      ) : (
                        'N/A'
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge 
                        status={req.status === 'APPROVED' ? 'success' : req.status === 'REJECTED' ? 'error' : 'warning'} 
                        label={req.status} 
                      />
                    </td>
                    <td className="py-3 px-4 flex gap-2">
                      <AnimatedButton size="sm" onClick={() => setActionModal({isOpen: true, wfId: req.id, action: 'APPROVE', remarks: ''})}>Approve</AnimatedButton>
                      <AnimatedButton variant="secondary" size="sm" onClick={() => setActionModal({isOpen: true, wfId: req.id, action: 'REJECT', remarks: ''})}>Reject</AnimatedButton>
                    </td>
                  </tr>
                ))}
                {requests.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-4 text-center text-neutral-500">No requests found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </GlassCard>
      </div>
      
      <Modal 
        isOpen={actionModal.isOpen} 
        onClose={() => setActionModal(prev => ({...prev, isOpen: false}))} 
        title={`${actionModal.action === 'APPROVE' ? 'Approve' : 'Reject'} Request`}
      >
        <div className="space-y-4">
          <Input 
            label="Remarks (Optional)" 
            placeholder="Enter any comments..." 
            value={actionModal.remarks} 
            onChange={(e) => setActionModal(prev => ({...prev, remarks: e.target.value}))} 
          />
          <div className="flex gap-2 justify-end mt-4">
            <AnimatedButton variant="secondary" onClick={() => setActionModal(prev => ({...prev, isOpen: false}))}>Cancel</AnimatedButton>
            <AnimatedButton onClick={submitAction} className={actionModal.action === 'APPROVE' ? 'bg-emerald-600 hover:bg-emerald-700 text-white' : 'bg-red-600 hover:bg-red-700 text-white'}>Confirm</AnimatedButton>
          </div>
        </div>
      </Modal>
    </>
  );
};

export default AdminLeaveApprovals;

