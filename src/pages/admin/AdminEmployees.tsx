import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GlassCard, AnimatedButton, Input, StatusBadge, Modal, Select } from '../../components/ui';
import { api } from '../../lib/api';
import { organizationApi } from '../../services/organization.api';

export const AdminEmployees: React.FC = () => {
  const navigate = useNavigate();
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Create User State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ 
    empId: '', name: '', empType: '', joiningDate: '', 
    managerId: '', companyId: '', branchId: '', departmentId: '', designationId: '',
    address: '', phone: '', email: '', force: false 
  });
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');

  // Update User State
  const [isUpdateModalOpen, setIsUpdateModalOpen] = useState(false);
  const [updateData, setUpdateData] = useState({ 
    empId: '', name: '', phone: '', address: '',
    designation: '', branch: '', department: '',
    bankName: '', accountNumber: '', ifscCode: ''
  });
  const [updateLoading, setUpdateLoading] = useState(false);
  const [updateError, setUpdateError] = useState('');
  const [updateSuccess, setUpdateSuccess] = useState('');

  const [orgData, setOrgData] = useState({
    companies: [] as any[], branches: [] as any[], departments: [] as any[], designations: [] as any[]
  });

  const fetchEmployees = async () => {
    setLoading(true);
    try {
      const data = await api.get<any[]>('/v1/admin/users/');
      setEmployees(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchOrgData = async () => {
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

  useEffect(() => {
    fetchEmployees();
    fetchOrgData();
  }, []);

  const handleToggleStatus = async (empId: string, currentStatus: string) => {
    try {
      await api.put(`/v1/admin/users/${empId}/status/`, { status: currentStatus === 'active' ? 'inactive' : 'active' });
      fetchEmployees();
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateUser = async () => {
    setFormLoading(true);
    setFormError('');
    setFormSuccess('');

    if (!formData.empId) {
      setFormError('Required field missing: empId');
      setFormLoading(false);
      return;
    }

    try {
      await api.post('/v1/admin/create-user/', formData);
      setFormSuccess('User created successfully!');
      fetchEmployees();
      setTimeout(() => {
        setIsModalOpen(false);
        setFormData({ empId: '', name: '', empType: '', joiningDate: '', managerId: '', companyId: '', branchId: '', departmentId: '', designationId: '', address: '', phone: '', email: '', force: false });
        setFormSuccess('');
      }, 1500);
    } catch (e: any) {
      setFormError(e.response?.data?.detail || e.message || 'Failed to create user');
    } finally {
      setFormLoading(false);
    }
  };

  const openUpdateModal = (emp: any) => {
    setUpdateData({ 
      empId: emp.empId, 
      name: emp.name || '', 
      phone: emp.phone || '', 
      address: emp.address || '',
      designation: emp.designation || '',
      branch: emp.branch || '',
      department: emp.department || '',
      bankName: emp.bankDetails?.bankName || '',
      accountNumber: emp.bankDetails?.accountNumber || '',
      ifscCode: emp.bankDetails?.ifscCode || ''
    });
    setUpdateError('');
    setUpdateSuccess('');
    setIsUpdateModalOpen(true);
  };

  const handleUpdateUser = async () => {
    setUpdateLoading(true);
    setUpdateError('');
    setUpdateSuccess('');
    try {
      const payload = {
        name: updateData.name,
        phone: updateData.phone,
        address: updateData.address,
        designation: updateData.designation,
        branch: updateData.branch,
        department: updateData.department,
        bankDetails: {
          bankName: updateData.bankName,
          accountNumber: updateData.accountNumber,
          ifscCode: updateData.ifscCode
        }
      };
      await api.put(`/v1/profile/${updateData.empId}/`, payload);
      setUpdateSuccess('User updated successfully!');
      fetchEmployees();
      setTimeout(() => {
        setIsUpdateModalOpen(false);
        setUpdateSuccess('');
      }, 1500);
    } catch (e: any) {
      setUpdateError(e.response?.data?.detail || e.message || 'Failed to update user');
    } finally {
      setUpdateLoading(false);
    }
  };

  return (
    <>
      <div className="space-y-6">
        <GlassCard className="p-6 flex justify-between items-center">
          <h2 className="text-xl font-bold text-neutral-900">Manage Employees</h2>
          <AnimatedButton onClick={() => navigate('/admin/employees/new')}>Create Employee (Wizard)</AnimatedButton>
        </GlassCard>

        <GlassCard className="p-6 overflow-x-auto">
          {loading ? (
            <p>Loading employees...</p>
          ) : (
            <table className="w-full text-left border-collapse min-w-[600px]">
              <thead>
                <tr className="border-b border-neutral-200">
                  <th className="py-3 px-4">Emp ID</th>
                  <th className="py-3 px-4">Name</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {employees.map((emp) => (
                  <tr key={emp.empId} className="border-b border-neutral-100">
                    <td className="py-3 px-4">{emp.empId}</td>
                    <td className="py-3 px-4">{emp.name}</td>
                    <td className="py-3 px-4">
                      <StatusBadge 
                        status={emp.status === 'active' ? 'success' : 'error'} 
                        label={emp.status?.toUpperCase()} 
                      />
                    </td>
                    <td className="py-3 px-4 flex gap-2">
                      <AnimatedButton variant="secondary" size="sm" onClick={() => handleToggleStatus(emp.empId, emp.status)}>
                        {emp.status === 'active' ? 'Deactivate' : 'Activate'}
                      </AnimatedButton>
                      <AnimatedButton variant="secondary" size="sm" onClick={() => openUpdateModal(emp)}>Update</AnimatedButton>
                    </td>
                  </tr>
                ))}
                {employees.length === 0 && (
                  <tr>
                    <td colSpan={4} className="py-4 text-center text-neutral-500">No employees found or API not connected.</td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </GlassCard>
      </div>

      {/* Create User Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create User">
        <div className="space-y-4 max-h-[70vh] overflow-y-auto px-1">
          {formError && <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">{formError}</div>}
          {formSuccess && <div className="p-3 bg-emerald-50 text-emerald-700 rounded-lg text-sm">{formSuccess}</div>}
          
          <Input label="Employee ID *" value={formData.empId} onChange={(e) => setFormData({ ...formData, empId: e.target.value })} placeholder="e.g. EMP001" />
          <Input label="Full Name" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="e.g. John Doe" />
          
          <div className="grid grid-cols-2 gap-2">
            <Select 
              label="Company" 
              options={(orgData.companies || []).map(c => ({value: c._id, label: c.name}))} 
              value={formData.companyId} 
              onChange={e => setFormData({...formData, companyId: e.target.value})} 
            />
            <Select 
              label="Branch" 
              options={(orgData.branches || []).map(b => ({value: b._id, label: b.name}))} 
              value={formData.branchId} 
              onChange={e => setFormData({...formData, branchId: e.target.value})} 
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <Select 
              label="Department" 
              options={(orgData.departments || []).map(d => ({value: d._id, label: d.name}))} 
              value={formData.departmentId} 
              onChange={e => setFormData({...formData, departmentId: e.target.value})} 
            />
            <Select 
              label="Designation" 
              options={(orgData.designations || []).map(d => ({value: d._id, label: d.name}))} 
              value={formData.designationId} 
              onChange={e => setFormData({...formData, designationId: e.target.value})} 
            />
          </div>
          
          <Input label="Manager ID (Approver)" value={formData.managerId} onChange={(e) => setFormData({ ...formData, managerId: e.target.value })} placeholder="Manager Employee ID" />
          
          <Input label="Employee Type" value={formData.empType} onChange={(e) => setFormData({ ...formData, empType: e.target.value })} placeholder="e.g. Full Time" />
          <Input label="Joining Date" value={formData.joiningDate} onChange={(e) => setFormData({ ...formData, joiningDate: e.target.value })} placeholder="YYYY-MM-DD" type="date" />
          <Input label="Address" value={formData.address} onChange={(e) => setFormData({ ...formData, address: e.target.value })} placeholder="Full Address" />
          
          <div className="grid grid-cols-2 gap-2">
            <Input label="Phone (Optional)" value={formData.phone} onChange={(e) => setFormData({ ...formData, phone: e.target.value })} placeholder="Phone Number" />
            <Input label="Email (Optional)" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} placeholder="Email Address" type="email" />
          </div>
          
          <label className="flex items-center gap-2 cursor-pointer mt-2">
            <input 
              type="checkbox" 
              className="w-4 h-4 text-primary-600 rounded border-neutral-300"
              checked={formData.force}
              onChange={(e) => setFormData({ ...formData, force: e.target.checked })}
            />
            <span className="text-sm text-neutral-700">Force Create (Bypass eSSL check)</span>
          </label>
          
          <div className="flex justify-end gap-3 pt-4">
            <AnimatedButton variant="secondary" onClick={() => setIsModalOpen(false)}>Cancel</AnimatedButton>
            <AnimatedButton onClick={handleCreateUser} loading={formLoading} disabled={!formData.empId}>Create</AnimatedButton>
          </div>
        </div>
      </Modal>

      {/* Update User Modal */}
      <Modal isOpen={isUpdateModalOpen} onClose={() => setIsUpdateModalOpen(false)} title={`Update User: ${updateData.empId}`}>
        <div className="space-y-4 max-h-[70vh] overflow-y-auto px-1">
          {updateError && <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">{updateError}</div>}
          {updateSuccess && <div className="p-3 bg-emerald-50 text-emerald-700 rounded-lg text-sm">{updateSuccess}</div>}
          
          <Input label="Full Name" value={updateData.name} onChange={(e) => setUpdateData({ ...updateData, name: e.target.value })} />
          <Input label="Phone Number" value={updateData.phone} onChange={(e) => setUpdateData({ ...updateData, phone: e.target.value })} />
          <Input label="Address" value={updateData.address} onChange={(e) => setUpdateData({ ...updateData, address: e.target.value })} />
          <Input label="Designation" value={updateData.designation} onChange={(e) => setUpdateData({ ...updateData, designation: e.target.value })} />
          <Input label="Department" value={updateData.department} onChange={(e) => setUpdateData({ ...updateData, department: e.target.value })} />
          <Input label="Branch" value={updateData.branch} onChange={(e) => setUpdateData({ ...updateData, branch: e.target.value })} />
          
          <h4 className="text-sm font-semibold mt-4">Bank Details</h4>
          <Input label="Bank Name" value={updateData.bankName} onChange={(e) => setUpdateData({ ...updateData, bankName: e.target.value })} />
          <Input label="Account Number" value={updateData.accountNumber} onChange={(e) => setUpdateData({ ...updateData, accountNumber: e.target.value })} />
          <Input label="IFSC Code" value={updateData.ifscCode} onChange={(e) => setUpdateData({ ...updateData, ifscCode: e.target.value })} />
          
          <div className="flex justify-end gap-3 pt-4">
            <AnimatedButton variant="secondary" onClick={() => setIsUpdateModalOpen(false)}>Cancel</AnimatedButton>
            <AnimatedButton onClick={handleUpdateUser} loading={updateLoading}>Update</AnimatedButton>
          </div>
        </div>
      </Modal>

    </>
  );
};

export default AdminEmployees;
