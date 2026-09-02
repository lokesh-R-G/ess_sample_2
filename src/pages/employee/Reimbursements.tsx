import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Clock, CheckCircle, XCircle, FileText, AlertCircle, Receipt } from 'lucide-react';
import { GlassCard, AnimatedButton, StatusBadge } from '../../components/ui';
import { DashboardLayout } from '../../components/layout';
import { reimbursementApi, ReimbursementClaimResponse } from '../../services/reimbursement.api';
import NewTripSheetModal from './NewTripSheetModal';
import { format } from 'date-fns';
import { Modal } from '../../components/ui';


export default function Reimbursements() {
  const [claims, setClaims] = useState<ReimbursementClaimResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isNewTripModalOpen, setIsNewTripModalOpen] = useState(false);
  const [viewAttachmentModal, setViewAttachmentModal] = useState<{isOpen: boolean, url: string | null}>({isOpen: false, url: null});

  useEffect(() => {
    fetchClaims();
  }, []);

  const fetchClaims = async () => {
    try {
      setIsLoading(true);
      const data = await reimbursementApi.getMyClaims();
      setClaims(data);
    } catch (err) {
      console.error('Failed to fetch claims:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewAttachment = async (attachmentId: string) => {
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
    <DashboardLayout>
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-neutral-900">Reimbursements & Claims</h1>
            <p className="text-neutral-500 mt-1">Manage your trip sheets and cash vouchers</p>
          </div>
          <AnimatedButton
            onClick={() => setIsNewTripModalOpen(true)}
            icon={Plus}
          >
            New Trip Sheet
          </AnimatedButton>
        </div>

        {/* List of Claims */}
        <GlassCard className="overflow-hidden">
          <div className="p-5 border-b border-white/10 bg-white/5">
            <h3 className="font-semibold text-neutral-900">My Claims</h3>
          </div>
          
          {isLoading ? (
            <div className="p-8 text-center text-neutral-500">Loading claims...</div>
          ) : claims.length === 0 ? (
            <div className="p-12 text-center flex flex-col items-center">
              <div className="w-12 h-12 bg-neutral-100 rounded-full flex items-center justify-center mb-3">
                <Receipt className="w-6 h-6 text-neutral-400" />
              </div>
              <h3 className="text-neutral-900 font-medium mb-1">No claims found</h3>
              <p className="text-neutral-500 text-sm">You haven't submitted any reimbursement claims yet.</p>
            </div>
          ) : (
            <div className="divide-y divide-neutral-100">
              {claims.map((claim) => (
                <div key={claim.id} className="p-5 hover:bg-neutral-50/50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-3 mb-1">
                        <span className="font-semibold text-neutral-900">{claim.claimType}</span>
                        <StatusBadge status={claim.status} />
                      </div>
                      <p className="text-sm text-neutral-500">{claim.description}</p>
                      
                      {claim.claimType === 'TripSheet' && claim.tripSheet && (
                        <div className="mt-3 flex items-center gap-6 text-sm text-neutral-600">
                          <div><span className="text-neutral-400">Date:</span> {claim.tripSheet.tripDate}</div>
                          <div><span className="text-neutral-400">Route:</span> {claim.tripSheet.fromLocation} → {claim.tripSheet.toLocation}</div>
                          <div><span className="text-neutral-400">Distance:</span> {claim.tripSheet.calculatedDistance} km</div>
                        </div>
                      )}

                      {claim.hodRejectionReason && (
                        <div className="mt-3 p-3 bg-red-50 rounded-lg flex items-start gap-2 text-sm text-red-800">
                          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                          <div>
                            <span className="font-medium">Rejection Reason: </span>
                            {claim.hodRejectionReason}
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="text-right">
                      <div className="text-lg font-bold text-neutral-900">
                        ₹{claim.calculatedAmount.toLocaleString('en-IN')}
                      </div>
                      <div className="text-xs text-neutral-400 mt-1">
                        Submitted: {format(new Date(claim.createdAt), 'dd MMM yyyy')}
                      </div>
                      {claim.attachments && claim.attachments.length > 0 && (
                        <div className="mt-3 flex gap-2">
                          {claim.attachments.map(att => (
                            <button
                              key={att.id}
                              onClick={() => handleViewAttachment(att.id)}
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-lg text-xs font-medium transition-colors border border-neutral-200"
                            >
                              <FileText className="w-3.5 h-3.5" />
                              {att.fileName}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </GlassCard>
      </div>

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

      <NewTripSheetModal
        isOpen={isNewTripModalOpen}
        onClose={() => setIsNewTripModalOpen(false)}
        onSuccess={() => {
          setIsNewTripModalOpen(false);
          fetchClaims();
        }}
      />
    </DashboardLayout>
  );
}

// Ensure Receipt is imported if used (Wait, Receipt is not imported in lucide-react above. I'll fix it.)
