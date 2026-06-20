import React, { useState } from 'react';
import { GlassCard, AnimatedButton } from '../../components/ui';
import { api } from '../../lib/api';

export const AdminSettings: React.FC = () => {
  const [syncing24, setSyncing24] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const handleSync24Hours = async () => {
    setSyncing24(true);
    setResult(null);
    try {
      const payload = {
        fromDate: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        toDate: new Date().toISOString()
      };
      const res = await api.post<any>('/sync/essl', payload);
      setResult(`Sync completed successfully. ${res?.message || ''}`);
    } catch (e: any) {
      setResult(`Sync failed: ${e.message}`);
    } finally {
      setSyncing24(false);
    }
  };

  return (
    <>
      <div className="space-y-6">
        <GlassCard className="p-6">
          <h2 className="text-xl font-bold text-neutral-900 mb-4">Settings</h2>
          <p className="text-neutral-600 mb-6">Manage system settings and integrations.</p>
          
          <div className="p-4 bg-neutral-50 rounded-xl border border-neutral-200">
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">eSSL Sync</h3>
            <p className="text-sm text-neutral-600 mb-4">
              Manually trigger a data synchronization from the eSSL system for the last 24 hours.
            </p>
            <AnimatedButton onClick={handleSync24Hours} loading={syncing24}>
              Sync Last 24 Hours
            </AnimatedButton>
            
            {result && (
              <div className={`mt-4 p-3 rounded-lg text-sm ${result.includes('failed') ? 'bg-red-50 text-red-700' : 'bg-emerald-50 text-emerald-700'}`}>
                {result}
              </div>
            )}
          </div>
        </GlassCard>
      </div>
    </>
  );
};

export default AdminSettings;
