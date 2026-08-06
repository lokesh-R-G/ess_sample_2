import React, { useEffect, useState } from 'react';
import { api } from '../../lib/api';

export default function ManagerInbox() {
  const [activeTab, setActiveTab] = useState<'PENDING' | 'APPROVED' | 'REJECTED'>('PENDING');
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Hardcode manager ID for the sake of demo, normally from auth context
  const managerId = "MOCK_MANAGER_ID";

  useEffect(() => {
    fetchRequests();
  }, [activeTab]);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/v2/approval/inbox/manager/${managerId}?status=${activeTab}`);
      setRequests(res.data || res || []);
    } catch (error) {
      console.error("Failed to load approvals", error);
    }
    setLoading(false);
  };

  const handleAction = async (id: string, action: string) => {
    try {
      await api.post(`/v2/approval/${id}/action`, { action, actedBy: managerId });
      fetchRequests(); // Refresh
    } catch (e) {
      console.error("Action failed", e);
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-neutral-900">Manager Inbox</h1>
      </div>

      {/* Tabs */}
      <div className="flex space-x-4 border-b border-neutral-200 mb-6">
        {['PENDING', 'APPROVED', 'REJECTED'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`py-2 px-4 border-b-2 font-medium text-sm ${
              activeTab === tab 
                ? 'border-blue-600 text-blue-600' 
                : 'border-transparent text-neutral-500 hover:text-neutral-700'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Grid */}
      <div className="bg-white rounded-lg shadow border border-neutral-200 overflow-hidden">
        <table className="min-w-full divide-y divide-neutral-200">
          <thead className="bg-neutral-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Employee ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Date Submitted</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Details</th>
              {activeTab === 'PENDING' && (
                <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">Actions</th>
              )}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-neutral-200">
            {loading ? (
              <tr><td colSpan={5} className="text-center py-4 text-neutral-500">Loading...</td></tr>
            ) : requests.length === 0 ? (
              <tr><td colSpan={5} className="text-center py-4 text-neutral-500">No {activeTab.toLowerCase()} requests found.</td></tr>
            ) : (
              requests.map((req, i) => (
                <tr key={i}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-900">{req.employeeId}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-900">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {req.approvalType}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
                    {new Date(req.createdAt).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-neutral-500">
                    {req.remarks || "No remarks"}
                  </td>
                  {activeTab === 'PENDING' && (
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button onClick={() => handleAction(req.id, 'APPROVE')} className="text-green-600 hover:text-green-900 mr-4">Approve</button>
                      <button onClick={() => handleAction(req.id, 'REJECT')} className="text-red-600 hover:text-red-900">Reject</button>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
