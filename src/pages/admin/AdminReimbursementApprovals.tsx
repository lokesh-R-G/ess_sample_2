import React, { useState, useEffect } from 'react';
import { GlassCard, AnimatedButton, StatusBadge, Modal, Input } from '../../components/ui';
import { reimbursementApi, ReimbursementClaimResponse } from '../../services/reimbursement.api';
import { FileText, CheckCircle, XCircle } from 'lucide-react';
import { api } from '../../lib/api';

export default function AdminReimbursementApprovals() {
  const [activeTab, setActiveTab] = useState<'HOD' | 'ACCOUNTS'>('HOD');
  const [requests, setRequests] = useState<ReimbursementClaimResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionModal, setActionModal] = useState<{isOpen: boolean, claimId: string, action: 'APPROVE'|'REJECT', reason: string}>({isOpen: false, claimId: '', action: 'APPROVE', reason: ''});
  const [viewAttachmentModal, setViewAttachmentModal] = useState<{isOpen: boolean, url: string | null}>({isOpen: false, url: null});

  const fetchRequests = async () => {
    setLoading(true);
    try {
      let data = [];
      if (activeTab === 'HOD') {
        data = await reimbursementApi.getPendingHodClaims();
      } else {
        data = await reimbursementApi.getPendingAccountsClaims();
      }
      setRequests(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, [activeTab]);

  const submitAction = async () => {
    try {
      if (activeTab === 'HOD') {
        await reimbursementApi.processHodAction(actionModal.claimId, actionModal.action, actionModal.reason);
      } else {
        await reimbursementApi.processAccountsAction(actionModal.claimId, actionModal.action, actionModal.reason);
      }
      setActionModal({isOpen: false, claimId: '', action: 'APPROVE', reason: ''});
      fetchRequests();
    } catch (e: any) {
      alert(e.response?.data?.detail || e.message || 'Failed to process claim');
    }
  };

  const handleViewAttachment = async (attachmentId: string) => {
    // Construct the authenticated URL for the file viewer
    const token = localStorage.getItem('ess_auth_token');
    const url = `http://127.0.0.1:8000/api/reimbursement/attachments/${attachmentId}`;
    
    try {
      const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
      if (!res.ok) throw new Error("Failed to fetch attachment");
      const blob = await res.blob();
      const objectUrl = URL.createObjectURL(blob);
      setViewAttachmentModal({ isOpen: true, url: objectUrl });
    } catch (err) {
      alert("Error loading attachment");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-neutral-900">Reimbursement Approvals</h1>
      </div>
      
      {/* Tabs */}
      <div className="flex border-b border-neutral-200 gap-6">
        <button 
          className={`pb-3 font-medium transition-colors ${activeTab === 'HOD' ? 'border-b-2 border-primary-600 text-primary-600' : 'text-neutral-500 hover:text-neutral-700'}`}
          onClick={() => setActiveTab('HOD')}
        >
          HOD Approvals
        </button>
        <button 
          className={`pb-3 font-medium transition-colors ${activeTab === 'ACCOUNTS' ? 'border-b-2 border-primary-600 text-primary-600' : 'text-neutral-500 hover:text-neutral-700'}`}
          onClick={() => setActiveTab('ACCOUNTS')}
        >
          Accounts Review
        </button>
      </div>

      <GlassCard className="p-6">
        {loading ? (
          <p className="text-neutral-500">Loading claims...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-neutral-200 text-sm text-neutral-500">
                  <th className="py-3 px-4">Employee</th>
                  <th className="py-3 px-4">Claim Type</th>
                  <th className="py-3 px-4">Details</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {requests.map((req) => (
                  <tr key={req.id} className="border-b border-neutral-100 text-sm hover:bg-neutral-50 transition-colors">
                    <td className="py-4 px-4">
                      <div className="font-medium text-neutral-900">{req.employeeId}</div>
                    </td>
                    <td className="py-4 px-4 font-medium text-neutral-700">
                      {req.claimType}
                    </td>
                    <td className="py-4 px-4 text-neutral-600">
                      <div className="mb-1">{req.description}</div>
                      {req.tripSheet && (
                        <div className="text-xs space-y-1">
                          <div className="text-neutral-500">Date: {req.tripSheet.tripDate}</div>
                          <div><span className="text-neutral-500">Route:</span> {req.tripSheet.fromLocation} → {req.tripSheet.toLocation}</div>
                          <div><span className="text-neutral-500">Distance:</span> {req.tripSheet.calculatedDistance} km</div>
                          
                          {req.attachments && req.attachments.length > 0 && (
                            <div className="mt-2">
                              {req.attachments.map(att => (
                                <button 
                                  key={att.id}
                                  onClick={() => handleViewAttachment(att.id)} 
                                  className="text-primary-600 hover:underline flex items-center gap-1 mt-1"
                                >
                                  <FileText className="w-3 h-3" /> View {att.fileName}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </td>
                    <td className="py-4 px-4">
                      <div className="font-bold text-neutral-900">₹{req.calculatedAmount.toLocaleString('en-IN')}</div>
                    </td>
                    <td className="py-4 px-4">
                      <StatusBadge status="warning" label={req.status.replace('_', ' ')} />
                    </td>
                    <td className="py-4 px-4 flex justify-end gap-2">
                      <AnimatedButton 
                        onClick={() => setActionModal({isOpen: true, claimId: req.id, action: 'APPROVE', reason: ''})}
                      >
                        Approve
                      </AnimatedButton>
                      <AnimatedButton 
                        variant="secondary" 
                        onClick={() => setActionModal({isOpen: true, claimId: req.id, action: 'REJECT', reason: ''})}
                      >
                        Reject
                      </AnimatedButton>
                    </td>
                  </tr>
                ))}
                {requests.length === 0 && (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-neutral-500">
                      No pending reimbursement claims require your approval.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>

      <Modal
        isOpen={actionModal.isOpen}
        onClose={() => setActionModal(prev => ({...prev, isOpen: false}))}
        title={actionModal.action === 'APPROVE' ? 'Approve Claim' : 'Reject Claim'}
      >
        <div className="p-6 space-y-4">
          <p className="text-sm text-neutral-600">
            Are you sure you want to {actionModal.action.toLowerCase()} this claim?
          </p>
          
          {actionModal.action === 'REJECT' && (
            <Input
              label="Rejection Reason"
              value={actionModal.reason}
              onChange={(e) => setActionModal(prev => ({...prev, reason: e.target.value}))}
              required
              placeholder="Please provide a reason for rejection..."
            />
          )}

          <div className="flex justify-end gap-3 pt-4">
            <AnimatedButton variant="secondary" onClick={() => setActionModal(prev => ({...prev, isOpen: false}))}>
              Cancel
            </AnimatedButton>
            <AnimatedButton onClick={submitAction} disabled={actionModal.action === 'REJECT' && !actionModal.reason}>
              Confirm
            </AnimatedButton>
          </div>
        </div>
      </Modal>

      <Modal
        isOpen={viewAttachmentModal.isOpen}
        onClose={() => {
          setViewAttachmentModal({isOpen: false, url: null});
          if (viewAttachmentModal.url) URL.revokeObjectURL(viewAttachmentModal.url);
        }}
        title="View Attachment"
        size="lg"
      >
        <div className="p-6 flex justify-center">
          {viewAttachmentModal.url ? (
            <iframe src={viewAttachmentModal.url} className="w-full h-[600px] border-0 rounded" title="Attachment Viewer" />
          ) : (
            <p className="text-neutral-500">Loading attachment...</p>
          )}
        </div>
      </Modal>
    </div>
  );
}
