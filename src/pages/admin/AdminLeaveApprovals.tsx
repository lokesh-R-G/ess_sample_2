import React, { useState, useEffect } from 'react';
import { GlassCard, AnimatedButton, StatusBadge } from '../../components/ui';
import { api } from '../../lib/api';

export const AdminLeaveApprovals: React.FC = () => {
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const data = await api.get<any[]>('/leave/pending');
      setRequests(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleAction = async (id: string, action: 'approve' | 'reject') => {
    try {
      await api.post(`/leave/${id}/${action}`);
      fetchRequests();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <>
      <div className="space-y-6">
        <GlassCard className="p-6">
          <h2 className="text-xl font-bold text-neutral-900 mb-4">Leave & OD Approvals</h2>
          {loading ? (
            <p>Loading requests...</p>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-neutral-200">
                  <th className="py-3 px-4">Emp ID</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Dates</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {requests.map((req) => (
                  <tr key={req.id} className="border-b border-neutral-100">
                    <td className="py-3 px-4">{req.empId}</td>
                    <td className="py-3 px-4 uppercase">{req.requestType} {req.leaveType ? `(${req.leaveType})` : ''}</td>
                    <td className="py-3 px-4">{req.fromDate} to {req.toDate}</td>
                    <td className="py-3 px-4">
                      <StatusBadge 
                        status={req.status === 'approved' ? 'success' : req.status === 'rejected' ? 'error' : 'warning'} 
                        label={req.status?.toUpperCase()} 
                      />
                    </td>
                    <td className="py-3 px-4 flex gap-2">
                      <AnimatedButton size="sm" onClick={() => handleAction(req.id, 'approve')} disabled={req.status !== 'pending'}>Approve</AnimatedButton>
                      <AnimatedButton variant="secondary" size="sm" onClick={() => handleAction(req.id, 'reject')} disabled={req.status !== 'pending'}>Reject</AnimatedButton>
                    </td>
                  </tr>
                ))}
                {requests.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-4 text-center text-neutral-500">No requests found or API not connected.</td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </GlassCard>
      </div>
    </>
  );
};

export default AdminLeaveApprovals;

