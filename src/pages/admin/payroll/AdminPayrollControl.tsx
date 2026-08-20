import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calculator, CheckCircle, Save, Settings, Users, Building2, Calendar as CalendarIcon, FileText, FileSpreadsheet } from 'lucide-react';
import { api } from '../../../lib/api';
import { useAuth } from '../../../context/AuthContext';
import LeaveBalanceTab from './tabs/LeaveBalanceTab';
import ReimbursementDeductionTab from './tabs/ReimbursementDeductionTab';
import SalaryBreakdownTab from './tabs/SalaryBreakdownTab';
import PfEsiBreakdownTab from './tabs/PfEsiBreakdownTab';
import BranchSummaryTab from './tabs/BranchSummaryTab';

const AdminPayrollControl: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'leave' | 'reimbursements' | 'salary' | 'pf' | 'esi' | 'summary'>('reimbursements');
  
  const [companies, setCompanies] = useState<any[]>([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>('');
  const [branches, setBranches] = useState<any[]>([]);
  const [branchId, setBranchId] = useState<string>('');
  
  const [cycles, setCycles] = useState<any[]>([]);
  const [cycleId, setCycleId] = useState<string>('');
  const [month, setMonth] = useState<string>('');

  // Fetch Companies
  useEffect(() => {
    const fetchCompanies = async () => {
      try {
        const res = await api.get('/v2/organizations/companies');
        setCompanies(res.data);
        if (res.data.length > 0) {
          const cid = user?.companyId || res.data[0].companyId;
          setSelectedCompanyId(cid);
        }
      } catch (err) {
        console.error("Failed to fetch companies", err);
      }
    };
    fetchCompanies();
  }, [user]);

  // Fetch Branches & Cycles when Company changes
  useEffect(() => {
    const fetchBranchesAndCycles = async () => {
      if (!selectedCompanyId) return;
      try {
        const [bRes, cRes] = await Promise.all([
          api.get(`/v2/organizations/${selectedCompanyId}/branches`),
          api.get(`/v2/payroll/cycles?companyId=${selectedCompanyId}`)
        ]);
        
        setBranches(bRes.data);
        if (bRes.data.length > 0) {
          setBranchId(bRes.data[0].branchId);
        }

        setCycles(cRes.data);
        if (cRes.data.length > 0) {
          setCycleId(cRes.data[0].id);
          setMonth(cRes.data[0].period || '');
        } else {
          setCycleId('');
          setMonth('');
        }
      } catch (err) {
        console.error("Failed to fetch branches/cycles", err);
      }
    };
    fetchBranchesAndCycles();
  }, [selectedCompanyId]);

  const handleCalculate = async () => {
    try {
      if (!selectedCompanyId || !cycleId) return;
      alert("Calculating Payroll... Please wait.");
      const res = await api.post(`/v2/payroll/admin/calculate/${cycleId}`, {
        company_id: selectedCompanyId,
        branch_id: branchId || undefined
      });
      alert(`Successfully calculated payroll for ${(res as any).success} employees.`);
      setActiveTab('salary');
    } catch (e: any) {
      alert("Failed to calculate payroll: " + (e.response?.data?.detail || e.message));
    }
  };

  const handlePublish = async () => {
    try {
      if (!selectedCompanyId || !cycleId) return;
      if (!window.confirm("Are you sure you want to publish payslips and send emails?")) return;
      
      const res = await api.post(`/v2/payroll/admin/publish/${cycleId}`, {
        company_id: selectedCompanyId
      });
      alert(`Successfully published ${(res as any).success} payslips.`);
    } catch (e: any) {
      alert("Failed to publish: " + (e.response?.data?.detail || e.message));
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Payroll Control Center</h1>
          <p className="text-slate-500 mt-1">Pre-calculation review and payroll generation</p>
        </div>
        
        <div className="flex items-center space-x-4 bg-white p-2 rounded-xl shadow-sm border border-slate-200">
          
          {user?.role === 'Super Admin' && (
            <div className="flex items-center space-x-2 px-3 border-r border-slate-200">
              <Building2 className="w-4 h-4 text-slate-400" />
              <select 
                value={selectedCompanyId}
                onChange={(e) => setSelectedCompanyId(e.target.value)}
                className="text-sm border-none bg-transparent focus:ring-0 text-slate-700 font-medium cursor-pointer"
              >
                {companies.map(c => (
                  <option key={c.companyId} value={c.companyId}>{c.name}</option>
                ))}
              </select>
            </div>
          )}

          <div className="flex items-center space-x-2 px-3 border-r border-slate-200">
            <Building2 className="w-4 h-4 text-slate-400" />
            <select 
              value={branchId}
              onChange={(e) => setBranchId(e.target.value)}
              className="text-sm border-none bg-transparent focus:ring-0 text-slate-700 font-medium cursor-pointer"
            >
              <option value="">All Branches</option>
              {branches.map(b => (
                <option key={b.branchId} value={b.branchId}>{b.name}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-center space-x-2 px-3">
            <CalendarIcon className="w-4 h-4 text-slate-400" />
            <select 
              value={cycleId}
              onChange={(e) => {
                setCycleId(e.target.value);
                const c = cycles.find(cyc => cyc.id === e.target.value);
                if (c) setMonth(c.period);
              }}
              className="text-sm border-none bg-transparent focus:ring-0 text-slate-700 font-medium cursor-pointer"
            >
              <option value="" disabled>Select Cycle</option>
              {cycles.map(c => (
                <option key={c.id} value={c.id}>{c.name} ({c.period})</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="flex items-center justify-between px-2 bg-slate-50/80 border-b border-slate-200 overflow-x-auto">
          <div className="flex space-x-1 p-2">
            {[
              { id: 'leave', label: 'Leave Balances', icon: FileText },
              { id: 'reimbursements', label: 'Inputs & Deductions', icon: FileSpreadsheet },
              { id: 'salary', label: 'Salary Breakdown', icon: Calculator },
              { id: 'pf', label: 'PF Report', icon: Settings },
              { id: 'esi', label: 'ESI Report', icon: Settings },
              { id: 'summary', label: 'Branch Summary', icon: Building2 },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === tab.id 
                    ? 'bg-white text-indigo-600 shadow-sm ring-1 ring-slate-200' 
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                <tab.icon className={`w-4 h-4 ${activeTab === tab.id ? 'text-indigo-600' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
          
          <div className="flex items-center space-x-3 pr-4">
            <button 
              onClick={handleCalculate}
              className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium transition-colors"
            >
              <Calculator className="w-4 h-4" />
              <span>Calculate Payroll</span>
            </button>
            <button 
              onClick={handlePublish}
              className="flex items-center space-x-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 text-sm font-medium transition-colors"
            >
              <CheckCircle className="w-4 h-4" />
              <span>Publish Payslips</span>
            </button>
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'leave' && <LeaveBalanceTab cycleId={cycleId} companyId={selectedCompanyId} branchId={branchId} />}
          {activeTab === 'reimbursements' && <ReimbursementDeductionTab companyId={selectedCompanyId} branchId={branchId} cycleId={cycleId} />}
          {activeTab === 'salary' && <SalaryBreakdownTab cycleId={cycleId} companyId={selectedCompanyId} branchId={branchId} />}
          {activeTab === 'pf' && <PfEsiBreakdownTab type="pf" cycleId={cycleId} companyId={selectedCompanyId} branchId={branchId} />}
          {activeTab === 'esi' && <PfEsiBreakdownTab type="esi" cycleId={cycleId} companyId={selectedCompanyId} branchId={branchId} />}
          {activeTab === 'summary' && <BranchSummaryTab cycleId={cycleId} companyId={selectedCompanyId} branchId={branchId} />}
        </div>
      </div>
    </div>
  );
};

export default AdminPayrollControl;
