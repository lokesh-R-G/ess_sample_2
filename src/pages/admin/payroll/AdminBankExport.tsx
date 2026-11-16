

import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { GlassCard, AnimatedButton } from '../../../components/ui';
import { payrollCycleApi } from '../../../services/payrollCycleApi';
import { toast } from 'react-hot-toast';
import { useAuth } from '../../../context/AuthContext';
import { Building2, AlertTriangle, FileSpreadsheet, Archive } from 'lucide-react';

export default function AdminBankExport() {
  const { cycleId } = useParams<{ cycleId: string }>();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(true);
  const [previewData, setPreviewData] = useState<any>(null);

  useEffect(() => {
    if (cycleId && user?.companyId) {
      loadPreview();
    }
  }, [cycleId, user?.companyId]);

  const loadPreview = async () => {
    try {
      setPreviewLoading(true);
      const data = await payrollCycleApi.getExportPreview(cycleId!, user!.companyId);
      setPreviewData(data);
    } catch (err: any) {
      console.error('Failed to load export preview:', err);
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      if (!user?.companyId) {
        toast.error('Company context is required for export');
        return;
      }
      setLoading(true);
      const { blob, filename } = await payrollCycleApi.exportCsv(cycleId!, user.companyId);
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toast.success(`Export downloaded: ${filename}`);
      loadPreview();
    } catch (error: any) {
      toast.error(error.message || 'Failed to export bank file. Verify cycle is FINALIZED or PUBLISHED.');
    } finally {
      setLoading(false);
    }
  };

  const hasUnmapped = previewData?.unmappedEmployees && previewData.unmappedEmployees.length > 0;
  const accountsWithData = previewData?.accountSummaries?.filter((a: any) => a.employeeCount > 0) || [];
  const isMultiFile = accountsWithData.length > 1;

  return (
    <div className="space-y-6 max-w-4xl mx-auto p-4 sm:p-6 lg:p-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Admin Bank Export</h1>
          <p className="text-sm text-neutral-500 mt-1">
            Generate branch-mapped corporate salary transfer files for bank execution.
          </p>
        </div>
      </div>

      {/* Validation Warnings */}
      {hasUnmapped && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-semibold text-red-900">Unmapped Branches Detected</h3>
              <p className="text-xs text-red-700 mt-1">
                The following employees are in branches without a configured company salary bank account. 
                Bank export cannot proceed until all branches are mapped in <strong>Company Salary Bank Accounts</strong>.
              </p>
              <div className="mt-3 overflow-x-auto max-h-40">
                <table className="min-w-full text-xs text-left text-red-800">
                  <thead className="bg-red-100">
                    <tr>
                      <th className="px-2 py-1">Employee Code</th>
                      <th className="px-2 py-1">Branch</th>
                      <th className="px-2 py-1">Branch ID</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-red-200">
                    {previewData.unmappedEmployees.map((emp: any, i: number) => (
                      <tr key={i}>
                        <td className="px-2 py-1 font-mono">{emp.employeeCode}</td>
                        <td className="px-2 py-1 font-medium">{emp.branchName}</td>
                        <td className="px-2 py-1 font-mono">{emp.branchId || 'None'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Pre-export Account Summary */}
      {accountsWithData.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-neutral-200 overflow-hidden">
          <div className="px-6 py-4 bg-neutral-50 border-b border-neutral-200 flex justify-between items-center">
            <h2 className="text-sm font-semibold text-neutral-800 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-brand-600" />
              Source Bank Account Distribution
            </h2>
            <span className="text-xs text-neutral-500 font-medium">
              {accountsWithData.length} account{accountsWithData.length > 1 ? 's' : ''} ({isMultiFile ? 'Will download ZIP package' : 'Will download single CSV'})
            </span>
          </div>
          <table className="w-full text-left text-sm">
            <thead className="bg-neutral-50/50 text-neutral-600 text-xs border-b border-neutral-200">
              <tr>
                <th className="px-6 py-3 font-medium">Source Bank & Account</th>
                <th className="px-6 py-3 font-medium">Mapped Branches</th>
                <th className="px-6 py-3 font-medium text-center">Employees</th>
                <th className="px-6 py-3 font-medium text-right">Total Net Pay</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200">
              {accountsWithData.map((acc: any) => (
                <tr key={acc.sourceAccountId} className="hover:bg-neutral-50/80">
                  <td className="px-6 py-3">
                    <div className="font-medium text-neutral-900">{acc.bankName}</div>
                    <div className="text-xs text-neutral-500 font-mono">Acc: {acc.accountNumber}</div>
                  </td>
                  <td className="px-6 py-3">
                    <div className="flex flex-wrap gap-1">
                      {acc.branchesRepresented.map((b: string) => (
                        <span key={b} className="px-2 py-0.5 rounded-full text-xs bg-brand-50 text-brand-700 font-medium">
                          {b}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-3 text-center font-medium text-neutral-700">
                    {acc.employeeCount}
                  </td>
                  <td className="px-6 py-3 text-right font-semibold text-neutral-900">
                    ₹{acc.totalNetPay.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      <GlassCard className="p-8 flex flex-col items-center justify-center text-center">
        <div className="w-16 h-16 bg-brand-50 rounded-full flex items-center justify-center mb-4">
          {isMultiFile ? (
            <Archive className="w-8 h-8 text-brand-600" />
          ) : (
            <FileSpreadsheet className="w-8 h-8 text-brand-600" />
          )}
        </div>
        <h3 className="text-xl font-bold text-neutral-900 mb-2">
          {isMultiFile ? 'Generate Multi-Account Bank Export (ZIP)' : 'Generate Bank Export (CSV)'}
        </h3>
        <p className="text-neutral-500 max-w-md mb-8 text-sm">
          {isMultiFile
            ? 'Transfers span multiple corporate bank accounts based on branch mapping. A ZIP bundle with individual bank CSVs and a summary manifest will be generated.'
            : 'All employee transfers map to a single corporate salary bank account. A single formatted bank CSV file will be downloaded.'}
        </p>
        
        <AnimatedButton 
          onClick={handleExportCSV} 
          disabled={loading || hasUnmapped}
        >
          {loading ? 'Generating...' : hasUnmapped ? 'Resolve Unmapped Branches to Export' : isMultiFile ? 'Download ZIP Package' : 'Download CSV Format'}
        </AnimatedButton>
      </GlassCard>
    </div>
  );
}
