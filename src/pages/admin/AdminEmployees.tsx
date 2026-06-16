import React, { useState, useEffect } from 'react';
import { GlassCard, AnimatedButton, Input, DataTable, StatusBadge } from '../../components/ui';
import { DashboardLayout } from '../../components/layout';
import { api } from '../../lib/api';

export const AdminEmployees: React.FC = () => {
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchEmployees = async () => {
    setLoading(true);
    try {
      const data = await api.get<any[]>('/admin/employees');
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
      await api.put(`/admin/employees/${empId}/status`, { status: currentStatus === 'active' ? 'inactive' : 'active' });
      fetchEmployees();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <GlassCard className="p-6 flex justify-between items-center">
          <h2 className="text-xl font-bold text-neutral-900">Manage Employees</h2>
          <AnimatedButton onClick={() => alert('Create user modal would open here')}>Create User</AnimatedButton>
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
    </DashboardLayout>
  );
};

export default AdminEmployees;
