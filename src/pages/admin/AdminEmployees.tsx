import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GlassCard, AnimatedButton, Input, StatusBadge, Modal, Select } from '../../components/ui';
import { api } from '../../lib/api';
import { organizationApi } from '../../services/organization.api';
import { toast } from 'react-hot-toast';

export const AdminEmployees: React.FC = () => {
  const navigate = useNavigate();
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [orgData, setOrgData] = useState({ companies: [] as any[], branches: [] as any[], departments: [] as any[], designations: [] as any[] });

  // Invite User State
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<any>(null);
  const [inviteData, setInviteData] = useState({
    employeeCode: '',
    username: '',
    role: 'Employee',
    personalEmail: '',
    temporaryPassword: '',
    sendWelcomeMail: true,
    forcePasswordChange: true
  });
  const [inviteLoading, setInviteLoading] = useState(false);

  const fetchEmployees = async () => {
    setLoading(true);
    try {
      const data: any = await api.get('/v2/employee/employees/directory/');
      setEmployees(data.data || []);
    } catch (e) {
      console.error(e);
      toast.error('Failed to load employees');
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
        companies: companies?.data || companies || [], 
        branches: branches?.data || branches || [], 
        departments: departments?.data || departments || [], 
        designations: designations?.data || designations || [] 
      });
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchEmployees();
    fetchOrgData();
  }, []);

  const getEntityName = (list: any[], id: string) => {
    if (!id) return '-';
    const found = list.find((i: any) => i._id === id || i.id === id);
    return found ? found.name : id;
  };

  const handleOpenInvite = (emp: any) => {
    setSelectedEmployee(emp);
    setInviteData({
      employeeCode: emp.employeeCode || '',
      username: '',
      role: 'Employee',
      personalEmail: '',
      temporaryPassword: Math.random().toString(36).slice(-8),
      sendWelcomeMail: true,
      forcePasswordChange: true
    });
    setIsInviteModalOpen(true);
  };

  const handleInviteUser = async () => {
    setInviteLoading(true);
    try {
      // 1. Create User via V1 Auth endpoints
      const userPayload = {
        empId: selectedEmployee.employeeId,
        name: `${selectedEmployee.firstName || ''} ${selectedEmployee.lastName || ''}`.trim(),
        role: inviteData.role,
        email: inviteData.personalEmail,
        password: inviteData.temporaryPassword,
        companyId: selectedEmployee.companyId,
        branchId: selectedEmployee.branchId,
        departmentId: selectedEmployee.departmentId,
        designationId: selectedEmployee.designationId
      };
      
      const userRes: any = await api.post('/v1/admin/create-user/', userPayload);
      
      // 2. Update Employee Auth Status via V2 Employee endpoints
      await api.put(`/v2/employee/employees/${selectedEmployee.employeeId}`, {
        employeeCode: inviteData.employeeCode,
        systemAccessEnabled: true,
        essStatus: 'Invitation Pending',
        authUserId: userRes.empId || selectedEmployee.employeeId
      });
      
      toast.success('ESS User created and employee updated successfully!');
      fetchEmployees();
      setIsInviteModalOpen(false);
    } catch (e: any) {
      toast.error(e.message || 'Failed to invite user');
    } finally {
      setInviteLoading(false);
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
            <table className="w-full text-left border-collapse min-w-[1000px]">
              <thead>
                <tr className="border-b border-neutral-200">
                  <th className="py-3 px-4">Emp Code</th>
                  <th className="py-3 px-4">Name</th>
                  <th className="py-3 px-4">Company</th>
                  <th className="py-3 px-4">Department</th>
                  <th className="py-3 px-4">Designation</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">ESS Status</th>
                  <th className="py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {employees.map((emp) => (
                  <tr key={emp.employeeId} className="border-b border-neutral-100 hover:bg-neutral-50/50">
                    <td className="py-3 px-4 font-mono text-sm">{emp.employeeCode || '-'}</td>
                    <td className="py-3 px-4 font-medium">{`${emp.firstName || ''} ${emp.lastName || ''}`.trim() || 'No Name'}</td>
                    <td className="py-3 px-4 text-sm">{getEntityName(orgData.companies, emp.companyId)}</td>
                    <td className="py-3 px-4 text-sm">{getEntityName(orgData.departments, emp.departmentId)}</td>
                    <td className="py-3 px-4 text-sm">{getEntityName(orgData.designations, emp.designationId)}</td>
                    <td className="py-3 px-4">
                      <StatusBadge status={emp.status === 'Active' ? 'success' : 'error'} label={emp.status?.toUpperCase() || 'UNKNOWN'} />
                    </td>
                    <td className="py-3 px-4">
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                        emp.essStatus === 'Active' ? 'bg-green-100 text-green-700' :
                        emp.essStatus === 'Not Invited' ? 'bg-neutral-100 text-neutral-600' :
                        'bg-amber-100 text-amber-700'
                      }`}>
                        {emp.essStatus || 'Not Invited'}
                      </span>
                    </td>
                    <td className="py-3 px-4 flex gap-2">
                      {!emp.authUserId && (
                        <AnimatedButton variant="secondary" size="sm" onClick={() => handleOpenInvite(emp)}>
                          Invite to ESS
                        </AnimatedButton>
                      )}
                      {emp.authUserId && (
                        <AnimatedButton variant="secondary" size="sm" disabled>
                          Manage ESS
                        </AnimatedButton>
                      )}
                    </td>
                  </tr>
                ))}
                {employees.length === 0 && (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-neutral-500">No employees found. Create an employee to get started.</td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </GlassCard>
      </div>

      {/* Invite ESS Modal */}
      <Modal isOpen={isInviteModalOpen} onClose={() => setIsInviteModalOpen(false)} title={`Invite to ESS: ${selectedEmployee?.firstName || ''}`}>
        <div className="space-y-4 px-1">
          <Input 
            label="Employee Code" 
            value={inviteData.employeeCode} 
            onChange={(e) => setInviteData({ ...inviteData, employeeCode: e.target.value })} 
            placeholder="Assign Employee Code" 
          />
          <Input 
            label="Username" 
            value={inviteData.username} 
            onChange={(e) => setInviteData({ ...inviteData, username: e.target.value })} 
            placeholder="System Username" 
          />
          <Input 
            label="Personal Email" 
            value={inviteData.personalEmail} 
            onChange={(e) => setInviteData({ ...inviteData, personalEmail: e.target.value })} 
            type="email" 
          />
          <Input 
            label="Temporary Password" 
            value={inviteData.temporaryPassword} 
            onChange={(e) => setInviteData({ ...inviteData, temporaryPassword: e.target.value })} 
          />
          
          <Select 
            label="System Role" 
            options={[
              { value: 'Employee', label: 'Employee' },
              { value: 'Manager', label: 'Manager' },
              { value: 'Admin', label: 'Administrator' }
            ]}
            value={inviteData.role} 
            onChange={e => setInviteData({...inviteData, role: e.target.value})} 
          />

          <label className="flex items-center gap-2 cursor-pointer mt-2">
            <input 
              type="checkbox" 
              className="w-4 h-4 text-primary-600 rounded border-neutral-300"
              checked={inviteData.sendWelcomeMail}
              onChange={(e) => setInviteData({ ...inviteData, sendWelcomeMail: e.target.checked })}
            />
            <span className="text-sm text-neutral-700">Send Welcome Email</span>
          </label>
          
          <label className="flex items-center gap-2 cursor-pointer mt-2">
            <input 
              type="checkbox" 
              className="w-4 h-4 text-primary-600 rounded border-neutral-300"
              checked={inviteData.forcePasswordChange}
              onChange={(e) => setInviteData({ ...inviteData, forcePasswordChange: e.target.checked })}
            />
            <span className="text-sm text-neutral-700">Force Password Change on first login</span>
          </label>
          
          <div className="flex justify-end gap-3 pt-4 border-t border-neutral-100">
            <AnimatedButton variant="secondary" onClick={() => setIsInviteModalOpen(false)}>Cancel</AnimatedButton>
            <AnimatedButton onClick={handleInviteUser} loading={inviteLoading} disabled={!inviteData.employeeCode || !inviteData.personalEmail}>Create ESS User</AnimatedButton>
          </div>
        </div>
      </Modal>
    </>
  );
};

export default AdminEmployees;
