import React, { useEffect, useState } from 'react';
import { api } from '../../../../lib/api';
import { FileText, Loader2 } from 'lucide-react';

interface Props {
  cycleId: string;
  companyId: string;
  branchId: string;
}

const LeaveBalanceTab: React.FC<Props> = ({ cycleId, companyId, branchId }) => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [leaveTypes, setLeaveTypes] = useState<string[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      if (!cycleId || !companyId) return;
      setLoading(true);
      try {
        const url = `/v2/payroll/admin/leave-balances?cycleId=${cycleId}&companyId=${companyId}` + (branchId ? `&branchId=${branchId}` : '');
        const res = await api.get(url);
        setData(res.data);

        // Extract dynamic leave types
        const types = new Set<string>();
        res.data.forEach((emp: any) => {
          Object.keys(emp.breakdown || {}).forEach(k => types.add(k));
        });
        setLeaveTypes(Array.from(types).sort());

      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [cycleId, companyId, branchId]);

  if (loading) return <div className="p-8 flex justify-center"><Loader2 className="w-6 h-6 animate-spin text-indigo-500" /></div>;

  if (data.length === 0) return <div className="p-8 text-center text-slate-500">No leave balance data available for the selected criteria.</div>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Employee</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">LOP</th>
            {leaveTypes.map(lt => (
              <th key={lt} className="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase tracking-wider" colSpan={3}>
                {lt} (Cr / Av / Bal)
              </th>
            ))}
            <th className="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase tracking-wider" colSpan={3}>
              Total (Cr / Av / Bal)
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-slate-200 text-sm">
          {data.map(emp => (
            <tr key={emp.employeeId} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 whitespace-nowrap">
                <div className="font-medium text-slate-900">{emp.employeeName}</div>
                <div className="text-xs text-slate-500">{emp.employeeCode}</div>
              </td>
              <td className="px-4 py-3 whitespace-nowrap font-medium text-red-600">{emp.lopDays}</td>
              
              {leaveTypes.map(lt => {
                const ldata = emp.breakdown?.[lt] || { credited: 0, availed: 0, balance: 0 };
                return (
                  <React.Fragment key={lt}>
                    <td className="px-4 py-3 text-center text-green-600">{ldata.credited}</td>
                    <td className="px-4 py-3 text-center text-amber-600">{ldata.availed}</td>
                    <td className="px-4 py-3 text-center font-medium text-indigo-600">{ldata.balance}</td>
                  </React.Fragment>
                );
              })}
              
              <td className="px-4 py-3 text-center text-green-600 font-semibold bg-slate-50/50 border-l border-slate-100">{emp.totalCredited}</td>
              <td className="px-4 py-3 text-center text-amber-600 font-semibold bg-slate-50/50">{emp.totalAvailed}</td>
              <td className="px-4 py-3 text-center text-indigo-700 font-bold bg-slate-50/50">{emp.totalBalance}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
export default LeaveBalanceTab;
