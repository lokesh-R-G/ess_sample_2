import React, { useState } from 'react';
import { GlassCard, AnimatedButton } from '../../components/ui';
import { api } from '../../lib/api';

export const AdminSync: React.FC = () => {
  const [syncing, setSyncing] = useState(false);
  const [syncing24, setSyncing24] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const handleSync = async () => {
    setSyncing(true);
    setResult(null);
    try {
      const res = await api.post<any>('/v1/sync/essl/');
      setResult(`Sync completed successfully. ${res?.message || ''}`);
    } catch (e: any) {
      setResult(`Sync failed: ${e.message}`);
    } finally {
      setSyncing(false);
    }
  };

  const handleSync24Hours = async () => {
    setSyncing24(true);
    setResult(null);
    try {
      const payload = {
        fromDate: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        toDate: new Date().toISOString()
      };
      const res = await api.post<any>('/v1/sync/essl/', payload);
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
        <GlassCard className="p-6 text-center">
          <h2 className="text-xl font-bold text-neutral-900 mb-4">Sync ESSL Data</h2>
          <p className="text-neutral-600 mb-6">
            Click the button below to manually trigger a sync of all users from the ESSL system.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <AnimatedButton onClick={handleSync} loading={syncing}>
              Sync All Users
            </AnimatedButton>
            <AnimatedButton onClick={handleSync24Hours} loading={syncing24} variant="secondary">
              Sync Last 24 Hours
            </AnimatedButton>
          </div>
          
          {result && (
            <div className={`mt-6 p-4 rounded-lg ${result.includes('failed') ? 'bg-red-50 text-red-700' : 'bg-emerald-50 text-emerald-700'}`}>
              {result}
            </div>
          )}
        </GlassCard>
      </div>
    </>
  );
};

export default AdminSync;

