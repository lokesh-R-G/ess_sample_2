import React, { useEffect, useState } from 'react';
import { api } from '../../../../lib/api';
import { Loader2 } from 'lucide-react';

interface Props {
  cycleId: string;
  companyId: string;
  branchId: string; // If 'All Branches' is selected, this is empty
}

const BranchSummaryTab: React.FC<Props> = ({ cycleId, companyId, branchId }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      if (!cycleId || !companyId) return;
      setLoading(true);
      try {
        const url = `/v2/payroll/admin/reports/branch-summary/${cycleId}?companyId=${companyId}` + (branchId ? `&branchId=${branchId}` : '');
        const res = await api.get(url);
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [cycleId, companyId, branchId]);

  if (loading) return <div className="p-8 flex justify-center"><Loader2 className="w-6 h-6 animate-spin text-indigo-500" /></div>;
  if (!data) return <div className="p-8 text-center text-slate-500">No branch summary available.</div>;

  const branches = data.branches || [];
  const total = data.companyTotal || {};

  return (
    <div className="space-y-6">
      <div className="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 rounded-lg">
        <table className="min-w-full divide-y divide-slate-300">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Branch</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Employees</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Gross</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Reimb</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">PF</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">ESI</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">TDS</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Other Ded.</th>
              <th className="px-4 py-3 text-right text-xs font-bold text-slate-900 uppercase bg-slate-100">Net Pay</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-200 text-sm">
            {branches.map((b: any) => (
              <tr key={b.branchId} className="hover:bg-slate-50">
                <td className="px-4 py-3 whitespace-nowrap font-medium text-slate-900">{b.branchName}</td>
                <td className="px-4 py-3 whitespace-nowrap text-right text-slate-600">{b.employeeCount}</td>
                <td className="px-4 py-3 whitespace-nowrap text-right text-slate-600">₹{b.gross}</td>
                <td className="px-4 py-3 whitespace-nowrap text-right text-slate-600">₹{b.reimbursement}</td>
                <td className="px-4 py-3 whitespace-nowrap text-right text-red-600">₹{b.pf}</td>
                <td className="px-4 py-3 whitespace-nowrap text-right text-red-600">₹{b.esi}</td>
                <td className="px-4 py-3 whitespace-nowrap text-right text-red-600">₹{b.tds}</td>
                <td className="px-4 py-3 whitespace-nowrap text-right text-red-600">₹{b.otherDeductions}</td>
                <td className="px-4 py-3 whitespace-nowrap text-right font-bold text-slate-900 bg-slate-50/50">₹{b.netPay}</td>
              </tr>
            ))}
          </tbody>
          <tfoot className="bg-slate-100">
            <tr>
              <td className="px-4 py-3 font-bold text-slate-900 uppercase">COMPANY TOTAL</td>
              <td className="px-4 py-3 text-right font-bold text-slate-900">{total.employeeCount}</td>
              <td className="px-4 py-3 text-right font-bold text-slate-900">₹{total.gross}</td>
              <td className="px-4 py-3 text-right font-bold text-slate-900">₹{total.reimbursement}</td>
              <td className="px-4 py-3 text-right font-bold text-red-600">₹{total.pf}</td>
              <td className="px-4 py-3 text-right font-bold text-red-600">₹{total.esi}</td>
              <td className="px-4 py-3 text-right font-bold text-red-600">₹{total.tds}</td>
              <td className="px-4 py-3 text-right font-bold text-red-600">₹{total.otherDeductions}</td>
              <td className="px-4 py-3 text-right font-extrabold text-slate-900">₹{total.netPay}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
};
export default BranchSummaryTab;
