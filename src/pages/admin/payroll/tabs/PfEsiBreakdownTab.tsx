import React, { useEffect, useState } from 'react';
import { api } from '../../../../lib/api';
import { Loader2 } from 'lucide-react';

interface Props {
  type: 'pf' | 'esi';
  cycleId: string;
  companyId: string;
  branchId: string;
}

const PfEsiBreakdownTab: React.FC<Props> = ({ type, cycleId, companyId, branchId }) => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [columns, setColumns] = useState<string[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      if (!cycleId || !companyId) return;
      setLoading(true);
      try {
        const url = `/v2/payroll/admin/reports/${type}/${cycleId}?companyId=${companyId}` + (branchId ? `&branchId=${branchId}` : '');
        const res = await api.get(url);
        setData(res.data);

        // Extract dynamic columns from the first record
        if (res.data.length > 0) {
          const keys = Object.keys(res.data[0]).filter(k => 
            !['employeeId', 'employeeName', 'employeeCode', 'branchId', 'companyId'].includes(k)
          );
          setColumns(keys);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [type, cycleId, companyId, branchId]);

  if (loading) return <div className="p-8 flex justify-center"><Loader2 className="w-6 h-6 animate-spin text-indigo-500" /></div>;

  if (data.length === 0) return <div className="p-8 text-center text-slate-500">No {type.toUpperCase()} data available.</div>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Employee</th>
            {columns.map(c => (
              <th key={c} className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
                {c.replace(/([A-Z])/g, ' $1').trim()}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-slate-200 text-sm">
          {data.map(emp => (
            <tr key={emp.employeeId} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 whitespace-nowrap">
                <div className="font-medium text-slate-900">{emp.employeeName}</div>
                <div className="text-xs text-slate-500">{emp.employeeCode}</div>
              </td>
              {columns.map(c => (
                <td key={c} className="px-4 py-3 text-right text-slate-700">
                  {typeof emp[c] === 'number' ? `₹${emp[c]}` : emp[c] || '-'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
export default PfEsiBreakdownTab;
