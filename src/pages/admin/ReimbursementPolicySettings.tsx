import React, { useState, useEffect } from 'react';
import { GlassCard, AnimatedButton, Input } from '../../components/ui';
import { reimbursementApi } from '../../services/reimbursement.api';
import { organizationApi } from '../../services/organization.api';

interface TripAllowancePolicy {
  _id?: string;
  companyId: string;
  allowedTripTypes: string[];
  ratePerKm: number;
  effectiveFrom: string;
  effectiveTo?: string;
  isActive: boolean;
}

export default function ReimbursementPolicySettings() {
  const [loading, setLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [companies, setCompanies] = useState<any[]>([]);
  const [policies, setPolicies] = useState<TripAllowancePolicy[]>([]);
  
  const [policy, setPolicy] = useState<TripAllowancePolicy>({
    companyId: '',
    allowedTripTypes: ['One Way', 'Round Trip'],
    ratePerKm: 10.0,
    effectiveFrom: new Date().toISOString().split('T')[0],
    isActive: true
  });

  const fetchData = async () => {
    setInitialLoad(true);
    setFetchError(null);
    try {
      const [compRes, polRes] = await Promise.all([
        organizationApi.getCompanies(),
        reimbursementApi.getTripAllowancePolicies()
      ]);
      
      // organizationApi.getCompanies() returns { data: [...] } due to pagination wrapper
      const compData = (compRes as any)?.data || (Array.isArray(compRes) ? compRes : []);
      const polData = Array.isArray(polRes) ? polRes : [];
      
      setCompanies(compData);
      setPolicies(polData);
      
      if (compData.length > 0 && !policy.companyId) {
        setPolicy(prev => ({ ...prev, companyId: compData[0]._id }));
      }
    } catch (err: any) {
      console.error('Failed to load data:', err);
      setFetchError(err.message || 'Unable to load companies and policies.');
    } finally {
      setInitialLoad(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSave = async () => {
    if (!policy.companyId) {
      alert('Please select a company.');
      return;
    }
    
    setLoading(true);
    try {
      await reimbursementApi.createTripAllowancePolicy(policy);
      alert('Trip Allowance Policy saved successfully.');
      fetchData(); // Refresh policies list
    } catch (err) {
      console.error(err);
      alert('Failed to save policy. Ensure valid date range and parameters.');
    } finally {
      setLoading(false);
    }
  };

  const getCompanyName = (companyId: string) => {
    const comp = companies.find(c => c._id === companyId);
    return comp ? comp.name : 'Unknown Company';
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-neutral-900">Reimbursement Policy Settings</h1>
      </div>
      
      <GlassCard className="p-6">
        <h2 className="text-lg font-semibold text-neutral-800 mb-4">Create Trip Allowance Policy</h2>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">Company</label>
            {initialLoad ? (
              <div className="w-full rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-2.5 text-sm text-neutral-500">
                Loading companies...
              </div>
            ) : fetchError ? (
              <div className="flex items-center gap-2">
                <div className="text-red-500 text-sm">Unable to load companies.</div>
                <button onClick={fetchData} className="text-xs text-primary-600 font-medium hover:underline">Retry</button>
              </div>
            ) : companies.length === 0 ? (
              <div className="w-full rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-2.5 text-sm text-neutral-500">
                No companies available
              </div>
            ) : (
              <select
                className="w-full rounded-xl border border-neutral-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
                value={policy.companyId}
                onChange={(e) => setPolicy({ ...policy, companyId: e.target.value })}
              >
                <option value="" disabled>Select Company</option>
                {companies.map(c => (
                  <option key={c._id} value={c._id}>{c.name}</option>
                ))}
              </select>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">Rate Per KM (₹)</label>
            <Input 
              type="number"
              step="0.5"
              value={policy.ratePerKm} 
              onChange={e => setPolicy({...policy, ratePerKm: parseFloat(e.target.value)})} 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">Effective From</label>
            <Input 
              type="date"
              value={policy.effectiveFrom} 
              onChange={e => setPolicy({...policy, effectiveFrom: e.target.value})} 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">Allowed Trip Types</label>
            <Input 
              value={policy.allowedTripTypes.join(', ')} 
              onChange={e => setPolicy({...policy, allowedTripTypes: e.target.value.split(',').map(s => s.trim())})} 
              placeholder="e.g. One Way, Round Trip"
            />
          </div>
        </div>
        
        <div className="mt-6 flex justify-end">
          <AnimatedButton onClick={handleSave} disabled={loading || !policy.companyId}>
            {loading ? 'Saving...' : 'Save Policy'}
          </AnimatedButton>
        </div>
      </GlassCard>

      <GlassCard className="p-6">
        <h2 className="text-lg font-semibold text-neutral-800 mb-4">Existing Policies</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-neutral-500 uppercase bg-neutral-50/50">
              <tr>
                <th className="px-4 py-3">Company</th>
                <th className="px-4 py-3">Rate</th>
                <th className="px-4 py-3">Effective From</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {policies.map(p => (
                <tr key={p._id} className="border-b border-neutral-100 last:border-0 hover:bg-neutral-50/50 transition-colors">
                  <td className="px-4 py-3 font-medium text-neutral-900">{getCompanyName(p.companyId)}</td>
                  <td className="px-4 py-3 text-neutral-600">₹{p.ratePerKm.toFixed(2)}/km</td>
                  <td className="px-4 py-3 text-neutral-600">{p.effectiveFrom}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${p.isActive ? 'bg-green-100 text-green-700' : 'bg-neutral-100 text-neutral-700'}`}>
                      {p.isActive ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                </tr>
              ))}
              {policies.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-neutral-500">
                    No trip allowance policies configured yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
