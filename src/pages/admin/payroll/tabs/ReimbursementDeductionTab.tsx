import React, { useEffect, useState } from 'react';
import { api } from '../../../../lib/api';
import { Loader2, Receipt, FileSpreadsheet } from 'lucide-react';

interface Props {
  cycleId: string;
  companyId: string;
  branchId: string;
}

const ReimbursementDeductionTab: React.FC<Props> = ({ cycleId, companyId, branchId }) => {
  const [reimbursements, setReimbursements] = useState<any[]>([]);
  const [deductions, setDeductions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showDeductionModal, setShowDeductionModal] = useState(false);
  const [employees, setEmployees] = useState<any[]>([]);
  
  // Deduction form state
  const [dEmpId, setDEmpId] = useState('');
  const [dType, setDType] = useState('');
  const [dAmount, setDAmount] = useState('');
  const [dDesc, setDDesc] = useState('');

  const fetchData = async () => {
    if (!cycleId || !companyId) return;
    setLoading(true);
    try {
      const urlBase = `?cycleId=${cycleId}&companyId=${companyId}` + (branchId ? `&branchId=${branchId}` : '');
      const [rRes, dRes, eRes] = await Promise.all([
        api.get(`/v2/payroll/admin/reimbursements${urlBase}`),
        api.get(`/v2/payroll/admin/deductions${urlBase}`),
        // We need an endpoint for active employees, let's just fetch them or rely on typing?
        // Let's assume we can fetch them for the modal, but if not we will just type the employee ID for now.
        // Or wait, we can just fetch from `/v2/organizations/${companyId}/employees` or similar? 
        // For now, let's leave it as a text input if we don't have the employees list readily available.
      ]);
      setReimbursements(rRes.data);
      setDeductions(dRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [cycleId, companyId, branchId]);

  const handleAddDeduction = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post(`/v2/payroll/admin/deductions`, {
        companyId,
        branchId: branchId || undefined,
        employeeId: dEmpId,
        payrollCycleId: cycleId,
        deductionType: dType,
        amount: Number(dAmount),
        description: dDesc
      });
      setShowDeductionModal(false);
      fetchData();
      setDEmpId('');
      setDType('');
      setDAmount('');
      setDDesc('');
    } catch (err: any) {
      alert("Failed to add deduction: " + (err.response?.data?.detail || err.message));
    }
  };

  const tripSheets = reimbursements.filter(r => r.claimType === 'TripSheet');
  const cashVouchers = reimbursements.filter(r => r.claimType === 'CashVoucher');

  if (loading) return <div className="p-8 flex justify-center"><Loader2 className="w-6 h-6 animate-spin text-indigo-500" /></div>;

  return (
    <div className="space-y-8">
      {/* Reimb: Trip Sheets */}
      <section>
        <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <FileSpreadsheet className="w-5 h-5 text-slate-500" /> Trip Sheets
        </h3>
        {tripSheets.length === 0 ? (
          <div className="text-slate-500 bg-slate-50 p-4 rounded-lg text-sm">No approved trip sheets found for this cycle.</div>
        ) : (
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
            <table className="min-w-full divide-y divide-slate-300">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase">Employee</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase">Date</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase">Route</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-500 uppercase">Dist (km)</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-500 uppercase">Rate/km</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-500 uppercase">Calculated</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-500 uppercase">Claimed</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200 text-sm">
                {tripSheets.map(r => (
                  <tr key={r._id}>
                    <td className="px-3 py-3">
                      <div className="font-medium text-slate-900">{r.employeeName}</div>
                      <div className="text-xs text-slate-500">{r.employeeCode}</div>
                    </td>
                    <td className="px-3 py-3 text-slate-600">{r.tripSheet?.tripDate}</td>
                    <td className="px-3 py-3 text-slate-600">{r.tripSheet?.fromLocation} → {r.tripSheet?.toLocation}</td>
                    <td className="px-3 py-3 text-right font-medium text-slate-900">{r.tripSheet?.calculatedDistance}</td>
                    <td className="px-3 py-3 text-right text-slate-500">₹{r.tripSheet?.ratePerKm}</td>
                    <td className="px-3 py-3 text-right text-indigo-600 font-medium">₹{r.tripSheet?.calculatedAmount}</td>
                    <td className="px-3 py-3 text-right font-bold text-slate-900">₹{r.claimedAmount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Reimb: Cash Vouchers */}
      <section>
        <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Receipt className="w-5 h-5 text-slate-500" /> Cash Vouchers
        </h3>
        {cashVouchers.length === 0 ? (
          <div className="text-slate-500 bg-slate-50 p-4 rounded-lg text-sm">No approved cash vouchers found for this cycle.</div>
        ) : (
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
            <table className="min-w-full divide-y divide-slate-300">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase">Employee</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase">Expense Date</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase">Description</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-500 uppercase">Claimed Amount</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200 text-sm">
                {cashVouchers.map(r => (
                  <tr key={r._id}>
                    <td className="px-3 py-3">
                      <div className="font-medium text-slate-900">{r.employeeName}</div>
                      <div className="text-xs text-slate-500">{r.employeeCode}</div>
                    </td>
                    <td className="px-3 py-3 text-slate-600">{r.cashVoucher?.expenseDate}</td>
                    <td className="px-3 py-3 text-slate-600 max-w-md truncate" title={r.description}>{r.description}</td>
                    <td className="px-3 py-3 text-right font-bold text-slate-900">₹{r.claimedAmount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Deductions */}
      <section>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
             Manual Deductions
          </h3>
          <button 
            onClick={() => setShowDeductionModal(true)}
            className="px-3 py-1.5 text-sm bg-slate-800 text-white rounded-md hover:bg-slate-700"
          >
            Add Deduction
          </button>
        </div>
        {deductions.length === 0 ? (
          <div className="text-slate-500 bg-slate-50 p-4 rounded-lg text-sm">No manual deductions applied for this cycle.</div>
        ) : (
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
            <table className="min-w-full divide-y divide-slate-300">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase">Employee</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase">Type</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase">Description</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-500 uppercase">Amount</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200 text-sm">
                {deductions.map(d => (
                  <tr key={d._id}>
                    <td className="px-3 py-3">
                      <div className="font-medium text-slate-900">{d.employeeName}</div>
                      <div className="text-xs text-slate-500">{d.employeeCode}</div>
                    </td>
                    <td className="px-3 py-3 font-medium text-amber-700">{d.deductionType}</td>
                    <td className="px-3 py-3 text-slate-600">{d.description}</td>
                    <td className="px-3 py-3 text-right font-bold text-red-600">-₹{d.amount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {showDeductionModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Add Manual Deduction</h3>
            <form onSubmit={handleAddDeduction} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Employee ID (6-digit)</label>
                <input required type="text" value={dEmpId} onChange={e => setDEmpId(e.target.value)} className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Deduction Type</label>
                <input required type="text" placeholder="e.g. Loan Repayment, Loss of Asset" value={dType} onChange={e => setDType(e.target.value)} className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Amount</label>
                <input required type="number" min="1" step="0.01" value={dAmount} onChange={e => setDAmount(e.target.value)} className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Description (Optional)</label>
                <input type="text" value={dDesc} onChange={e => setDDesc(e.target.value)} className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500" />
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button type="button" onClick={() => setShowDeductionModal(false)} className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Add Deduction</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default ReimbursementDeductionTab;
