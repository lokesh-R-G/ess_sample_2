import React, { useState, useEffect } from 'react';
import { GlassCard, AnimatedButton, Input, StatusBadge, Modal } from '../../components/ui';
import { DashboardLayout } from '../../components/layout';
import { api } from '../../lib/api';

export const AdminEmployees: React.FC = () => {
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ empId: '', name: '', force: false });
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');

  const fetchEmployees = async () => {
    setLoading(true);
    try {
      const data = await api.get<any[]>('/admin/users');
      setEmployees(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleToggleStatus = async (empId: string, currentStatus: string) => {
    try {
      await api.put(`/admin/users/${empId}/status`, { status: currentStatus === 'active' ? 'inactive' : 'active' });
      fetchEmployees();
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateUser = async () => {
    setFormLoading(true);
    setFormError('');
    setFormSuccess('');
    try {
      await api.post('/admin/create-user', formData);
      setFormSuccess('User created successfully!');
      fetchEmployees();
      setTimeout(() => {
        setIsModalOpen(false);
        setFormData({ empId: '', name: '', force: false });
        setFormSuccess('');
      }, 1500);
    } catch (e: any) {
      setFormError(e.response?.data?.detail || e.message || 'Failed to create user');
    } finally {
      setFormLoading(false);
    }
  };

  return (
    <DashboardLayout isAdmin>
      <div className="space-y-6">
        <GlassCard className="p-6 flex justify-between items-center">
          <h2 className="text-xl font-bold text-neutral-900">Manage Employees</h2>
          <AnimatedButton onClick={() => setIsModalOpen(true)}>Create User</AnimatedButton>
        </GlassCard>

        <GlassCard className="p-6">
          {loading ? (
            <p>Loading employees...</p>
          ) : (
            <table className="w-full text-left border-collapse">
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
                      <AnimatedButton variant="secondary" size="sm" onClick={() => alert('Update user modal')}>Update</AnimatedButton>
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

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create User">
        <div className="space-y-4">
          {formError && <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">{formError}</div>}
          {formSuccess && <div className="p-3 bg-emerald-50 text-emerald-700 rounded-lg text-sm">{formSuccess}</div>}
          
          <Input 
            label="Employee ID *" 
            value={formData.empId} 
            onChange={(e) => setFormData({ ...formData, empId: e.target.value })} 
            placeholder="e.g. EMP001" 
          />
          <Input 
            label="Full Name" 
            value={formData.name} 
            onChange={(e) => setFormData({ ...formData, name: e.target.value })} 
            placeholder="e.g. John Doe" 
          />
          
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
            <AnimatedButton onClick={handleCreateUser} loading={formLoading} disabled={!formData.empId}>Create User</AnimatedButton>
          </div>
        </div>
      </Modal>

    </DashboardLayout>
  );
};

export default AdminEmployees;
