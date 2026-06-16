import React, { useState } from 'react';
import { GlassCard, AnimatedButton } from '../../components/ui';
import { DashboardLayout } from '../../components/layout';
import { api } from '../../lib/api';

export const AdminSync: React.FC = () => {
  const [syncing, setSyncing] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const handleSync = async () => {
    setSyncing(true);
    setResult(null);
    try {
      const res = await api.post<any>('/sync/essl');
      setResult(`Sync completed successfully. ${res?.message || ''}`);
    } catch (e: any) {
      setResult(`Sync failed: ${e.message}`);
    } finally {
      setSyncing(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <GlassCard className="p-6 text-center">
          <h2 className="text-xl font-bold text-neutral-900 mb-4">Sync ESSL Data</h2>
          <p className="text-neutral-600 mb-6">
            Click the button below to manually trigger a sync of all users from the ESSL system.
          </p>
          <AnimatedButton onClick={handleSync} isLoading={syncing} className="mx-auto">
            Sync All Users
          </AnimatedButton>
          
          {result && (
            <div className={`mt-6 p-4 rounded-lg ${result.includes('failed') ? 'bg-red-50 text-red-700' : 'bg-emerald-50 text-emerald-700'}`}>
              {result}
            </div>
          )}
        </GlassCard>
      </div>
    </DashboardLayout>
  );
};

export default AdminSync;
