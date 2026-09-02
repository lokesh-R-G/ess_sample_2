import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GlassCard, AnimatedButton, StatusBadge } from '../../components/ui';
import { api } from '../../lib/api';
import { organizationApi } from '../../services/organization.api';
import { toast } from 'react-hot-toast';
import { InviteESSDialog } from '../../components/admin/InviteESSDialog';
import type { DirectoryEmployee } from '../../components/admin/InviteESSDialog';

export const AdminEmployees: React.FC = () => {
  const navigate = useNavigate();
  const [employees, setEmployees] = useState<DirectoryEmployee[]>([]);
  const [loading, setLoading] = useState(false);
  const [orgData, setOrgData] = useState({
    companies: [] as any[],
    branches: [] as any[],
    departments: [] as any[],
    designations: [] as any[],
  });

  const [isInviteOpen, setIsInviteOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<DirectoryEmployee | null>(null);

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

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleOpenInvite = (emp: DirectoryEmployee) => {
    setSelectedEmployee(emp);
    setIsInviteOpen(true);
  };

  return (
    <>
      <div className="space-y-6">
        <GlassCard className="p-6 flex justify-between items-center">
          <h2 className="text-xl font-bold text-neutral-900">Manage Employees</h2>
          <AnimatedButton onClick={() => navigate('/admin/employees/new')}>
            Create Employee (Wizard)
          </AnimatedButton>
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
                    <td className="py-3 px-4 font-mono text-sm">
                      {emp.employeeCode || <span className="text-neutral-400 italic">Not Assigned</span>}
                    </td>
                    <td className="py-3 px-4 font-medium">
                      {`${emp.firstName || ''} ${emp.lastName || ''}`.trim() || 'No Name'}
                    </td>
                    <td className="py-3 px-4 text-sm">
                      {(emp as any).companyName || '-'}
                    </td>
                    <td className="py-3 px-4 text-sm">
                      {(emp as any).departmentName || '-'}
                    </td>
                    <td className="py-3 px-4 text-sm">
                      {(emp as any).designationName || '-'}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge
                        status={(emp as any).status === 'Active' ? 'success' : 'error'}
                        label={(emp as any).status?.toUpperCase() || 'UNKNOWN'}
                      />
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`text-xs px-2 py-1 rounded-full font-medium ${
                          emp.essStatus === 'Active'
                            ? 'bg-green-100 text-green-700'
                            : emp.essStatus === 'Invited'
                            ? 'bg-amber-100 text-amber-700'
                            : 'bg-neutral-100 text-neutral-600'
                        }`}
                      >
                        {emp.essStatus || 'Not Invited'}
                      </span>
                    </td>
                    <td className="py-3 px-4 flex gap-2">
                      {!emp.authUserId ? (
                        <AnimatedButton
                          variant="secondary"
                          size="sm"
                          onClick={() => handleOpenInvite(emp)}
                        >
                          Invite to ESS
                        </AnimatedButton>
                      ) : (
                        <AnimatedButton variant="secondary" size="sm" disabled>
                          Manage ESS
                        </AnimatedButton>
                      )}
                    </td>
                  </tr>
                ))}
                {employees.length === 0 && (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-neutral-500">
                      No employees found. Create an employee to get started.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </GlassCard>
      </div>

      <InviteESSDialog
        employee={selectedEmployee}
        isOpen={isInviteOpen}
        onClose={() => setIsInviteOpen(false)}
        onSuccess={fetchEmployees}
      />
    </>
  );
};

export default AdminEmployees;
