import React, { useEffect, useState } from 'react';
import { api } from '../../../../lib/api';
import { Loader2 } from 'lucide-react';

interface Props {
  cycleId: string;
  companyId: string;
  branchId: string;
}

const SalaryBreakdownTab: React.FC<Props> = ({ cycleId, companyId, branchId }) => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [columns, setColumns] = useState<string[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      if (!cycleId || !companyId) return;
      setLoading(true);
      try {
        const url = `/v2/payroll/admin/reports/salary/${cycleId}?companyId=${companyId}` + (branchId ? `&branchId=${branchId}` : '');
        const res = await api.get(url);
        setData(res.data);

        // Extract dynamic columns
        const cols = new Set<string>();
        res.data.forEach((emp: any) => {
          (emp.lineItems || []).forEach((li: any) => {
            cols.add(li.description || li.componentId);
          });
        });
        setColumns(Array.from(cols));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [cycleId, companyId, branchId]);

  if (loading) return <div className="p-8 flex justify-center"><Loader2 className="w-6 h-6 animate-spin text-indigo-500" /></div>;

  if (data.length === 0) return <div className="p-8 text-center text-slate-500">No salary data available. Click Calculate Payroll to generate.</div>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Employee</th>
            {columns.map(c => (
              <th key={c} className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">{c}</th>
            ))}
            <th className="px-4 py-3 text-right text-xs font-medium text-slate-900 uppercase tracking-wider bg-slate-100">Net Pay</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-slate-200 text-sm">
          {data.map(emp => (
            <tr key={emp.employeeId} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 whitespace-nowrap">
                <div className="font-medium text-slate-900">{emp.employeeName}</div>
                <div className="text-xs text-slate-500">{emp.employeeCode}</div>
              </td>
              {columns.map(c => {
                const li = (emp.lineItems || []).find((l: any) => l.description === c || l.componentId === c);
                const isDeduction = li?.type === 'DEDUCTION';
                return (
                  <td key={c} className={`px-4 py-3 text-right ${isDeduction ? 'text-red-600' : 'text-slate-700'}`}>
                    {li ? `₹${li.amount}` : '-'}
                  </td>
                );
              })}
              <td className="px-4 py-3 text-right font-bold text-slate-900 bg-slate-50/50">
                ₹{emp.netPay}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
export default SalaryBreakdownTab;
