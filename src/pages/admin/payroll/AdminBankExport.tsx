import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { GlassCard, AnimatedButton } from '../../../components/ui';
import { payrollCycleApi } from '../../../services/payrollCycleApi';
import { toast } from 'react-hot-toast';
import { useAuth } from '../../../context/AuthContext';

export default function AdminBankExport() {
  const { cycleId } = useParams<{ cycleId: string }>();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);

  const handleExportCSV = async () => {
    try {
      if (!user?.companyId) {
        toast.error('Company context is required for export');
        return;
      }
      setLoading(true);
      const csvContent = await payrollCycleApi.exportCsv(cycleId!, user.companyId);
      
      // Create blob and download
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `bank_export_${cycleId}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast.success('Bank export completed');
    } catch (error: any) {
      toast.error(error.message || 'Failed to export bank file. Verify cycle is FINALIZED or PUBLISHED.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto p-4 sm:p-6 lg:p-8">
      <h1 className="text-2xl font-bold text-neutral-900">Admin Bank Export</h1>
      
      <GlassCard className="p-8 flex flex-col items-center justify-center text-center">
        <div className="w-16 h-16 bg-brand-50 rounded-full flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-brand-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="text-xl font-bold text-neutral-900 mb-2">Generate Bank Export</h3>
        <p className="text-neutral-500 max-w-md mb-8">
          The cycle must be in FINALIZED or PUBLISHED state. 
          Exporting will mark the cycle status as EXPORTED.
        </p>
        
        <AnimatedButton 
          onClick={handleExportCSV} 
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Download CSV Format'}
        </AnimatedButton>
      </GlassCard>
    </div>
  );
}
