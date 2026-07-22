import React, { useState, useEffect } from 'react';
import { GlassCard, AnimatedButton, Input, Select } from '../../components/ui';
import { organizationApi } from '../../services/organization.api';
import { api } from '../../lib/api';

export const AdminOrganization: React.FC = () => {
  const [orgData, setOrgData] = useState({ companies: [] as any[], branches: [] as any[], departments: [] as any[], designations: [] as any[] });
  
  const [companyName, setCompanyName] = useState('');
  const [branchName, setBranchName] = useState('');
  const [branchCompanyId, setBranchCompanyId] = useState('');
  const [deptName, setDeptName] = useState('');
  const [deptCompanyId, setDeptCompanyId] = useState('');
  const [desigName, setDesigName] = useState('');
  const [desigCompanyId, setDesigCompanyId] = useState('');

  const loadData = async () => {
    try {
      const [companies, branches, departments, designations] = await Promise.all([
        organizationApi.getCompanies(),
        organizationApi.getBranches(),
        organizationApi.getDepartments(),
        organizationApi.getDesignations()
      ]);
      setOrgData({ 
        companies: companies || [], 
        branches: branches || [], 
        departments: departments || [], 
        designations: designations || [] 
      });
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleCreateCompany = async () => {
    await api.post('/organization/companies', { name: companyName });
    setCompanyName(''); loadData();
  };
  const handleCreateBranch = async () => {
    await api.post('/organization/branches', { name: branchName, companyId: branchCompanyId });
    setBranchName(''); loadData();
  };
  const handleCreateDept = async () => {
    await api.post('/organization/departments', { name: deptName, companyId: deptCompanyId });
    setDeptName(''); loadData();
  };
  const handleCreateDesig = async () => {
    await api.post('/organization/designations', { name: desigName, companyId: desigCompanyId });
    setDesigName(''); loadData();
  };

  const companyOptions = (orgData.companies || []).map(c => ({value: c._id, label: c.name}));

  return (
    <div className="space-y-6">
      <GlassCard className="p-6">
        <h2 className="text-xl font-bold mb-4">Organization Master Data</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="space-y-3 p-4 border border-neutral-200 rounded-lg">
            <h3 className="font-semibold">Companies ({(orgData.companies || []).length})</h3>
            <Input label="Name" value={companyName} onChange={e => setCompanyName(e.target.value)} />
            <AnimatedButton size="sm" onClick={handleCreateCompany}>Add Company</AnimatedButton>
          </div>

          <div className="space-y-3 p-4 border border-neutral-200 rounded-lg">
            <h3 className="font-semibold">Branches ({(orgData.branches || []).length})</h3>
            <Select label="Company" options={companyOptions} value={branchCompanyId} onChange={e => setBranchCompanyId(e.target.value)} />
            <Input label="Name" value={branchName} onChange={e => setBranchName(e.target.value)} />
            <AnimatedButton size="sm" onClick={handleCreateBranch}>Add Branch</AnimatedButton>
          </div>

          <div className="space-y-3 p-4 border border-neutral-200 rounded-lg">
            <h3 className="font-semibold">Departments ({(orgData.departments || []).length})</h3>
            <Select label="Company" options={companyOptions} value={deptCompanyId} onChange={e => setDeptCompanyId(e.target.value)} />
            <Input label="Name" value={deptName} onChange={e => setDeptName(e.target.value)} />
            <AnimatedButton size="sm" onClick={handleCreateDept}>Add Dept</AnimatedButton>
          </div>

          <div className="space-y-3 p-4 border border-neutral-200 rounded-lg">
            <h3 className="font-semibold">Designations ({(orgData.designations || []).length})</h3>
            <Select label="Company" options={companyOptions} value={desigCompanyId} onChange={e => setDesigCompanyId(e.target.value)} />
            <Input label="Name" value={desigName} onChange={e => setDesigName(e.target.value)} />
            <AnimatedButton size="sm" onClick={handleCreateDesig}>Add Desig</AnimatedButton>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};
export default AdminOrganization;
