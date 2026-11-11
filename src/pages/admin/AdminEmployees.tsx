import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GlassCard, AnimatedButton, StatusBadge } from '../../components/ui';
import { api } from '../../lib/api';
import { toast } from 'react-hot-toast';
import { InviteESSDialog } from '../../components/admin/InviteESSDialog';
import type { DirectoryEmployee } from '../../components/admin/InviteESSDialog';
import { Edit, UserPlus, KeyRound, CheckCircle2, XCircle } from 'lucide-react';

export const AdminEmployees: React.FC = () => {
  const navigate = useNavigate();
  const [employees, setEmployees] = useState<DirectoryEmployee[]>([]);
  const [loading, setLoading] = useState(false);
  const [isInviteOpen, setIsInviteOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<DirectoryEmployee | null>(null);
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

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

  const handleToggleStatus = async (emp: DirectoryEmployee) => {
    const isCurrentlyActive = (emp.status || 'Active').toLowerCase() === 'active';
    const newStatus = isCurrentlyActive ? 'Inactive' : 'Active';
    
    const confirmMessage = isCurrentlyActive
      ? `Are you sure you want to deactivate ${emp.firstName || ''} ${emp.lastName || ''}?\n\n• ESS portal access will be disabled immediately.\n• The employee will remain eligible for attendance & payroll through the end of the current calendar month.\n• Historical payroll, attendance, and business records will remain preserved.`
      : `Reactivate ${emp.firstName || ''} ${emp.lastName || ''}?`;

    if (!window.confirm(confirmMessage)) {
      return;
    }

    setActionLoadingId(emp.employeeId);
    try {
      await api.patch(`/v2/employee/employees/${emp.employeeId}/status`, { status: newStatus });
      toast.success(`Employee successfully marked as ${newStatus}`);
      await fetchEmployees();
    } catch (err: any) {
      console.error(err);
      toast.error(err.response?.data?.detail || `Failed to update status`);
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleAdminResetPassword = async (emp: DirectoryEmployee) => {
    if (!window.confirm(`Send password reset OTP to ${emp.firstName || ''} ${emp.lastName || ''}'s registered personal email?`)) {
      return;
    }
    setActionLoadingId(emp.employeeId);
    try {
      const res: any = await api.post(`/v1/admin/employees/${emp.employeeId}/reset-password`);
      toast.success(res.message || 'Password reset OTP sent to employee');
    } catch (err: any) {
      console.error(err);
      toast.error(err.response?.data?.detail || 'Failed to initiate password reset');
    } finally {
      setActionLoadingId(null);
    }
  };

  return (
    <>
      <div className="space-y-6">
        <GlassCard className="p-6 flex justify-between items-center">
          <div>
            <h2 className="text-xl font-bold text-neutral-900">Manage Employees</h2>
            <p className="text-sm text-neutral-500 mt-1">Manage employee master profiles, ESS invites, and lifecycle statuses.</p>
          </div>
          <AnimatedButton onClick={() => navigate('/admin/employees/new')}>
            Create Employee (Wizard)
          </AnimatedButton>
        </GlassCard>

        <GlassCard className="p-6 overflow-x-auto">
          {loading ? (
            <p className="text-neutral-500 py-4">Loading employees...</p>
          ) : (
            <table className="w-full text-left border-collapse min-w-[1100px]">
              <thead>
                <tr className="border-b border-neutral-200 text-xs font-semibold uppercase tracking-wider text-neutral-500">
                  <th className="py-3 px-4">Emp Code</th>
                  <th className="py-3 px-4">Machine ID</th>
                  <th className="py-3 px-4">Name</th>
                  <th className="py-3 px-4">Company</th>
                  <th className="py-3 px-4">Department</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">ESS Status</th>
                  <th className="py-3 px-4 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {employees.map((emp) => {
                  const isActive = (emp.status || 'Active').toLowerCase() === 'active';
                  const isProcessing = actionLoadingId === emp.employeeId;

                  return (
                    <tr key={emp.employeeId} className="hover:bg-neutral-50/50 transition-colors">
                      <td className="py-3 px-4 font-mono text-sm font-medium text-neutral-900">
                        {emp.employeeCode || <span className="text-neutral-400 italic">Not Assigned</span>}
                      </td>
                      <td className="py-3 px-4 font-mono text-sm text-neutral-600">
                        {emp.machineId ? (
                          <span className="px-2 py-0.5 rounded bg-neutral-100 border border-neutral-200">
                            {emp.machineId}
                          </span>
                        ) : (
                          <span className="text-neutral-400 italic text-xs">Unassigned</span>
                        )}
                      </td>
                      <td className="py-3 px-4 font-medium text-neutral-900">
                        {`${emp.firstName || ''} ${emp.lastName || ''}`.trim() || 'No Name'}
                      </td>
                      <td className="py-3 px-4 text-sm text-neutral-600">
                        {emp.companyName || '-'}
                      </td>
                      <td className="py-3 px-4 text-sm text-neutral-600">
                        {emp.departmentName || '-'}
                      </td>
                      <td className="py-3 px-4">
                        <StatusBadge
                          status={isActive ? 'success' : 'error'}
                          label={emp.status?.toUpperCase() || 'UNKNOWN'}
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
                      <td className="py-3 px-4">
                        <div className="flex items-center justify-center gap-2">
                          {/* 1. Manage Employee Action */}
                          <button
                            type="button"
                            title="Manage Employee"
                            onClick={() => navigate(`/admin/employees/edit/${emp.employeeId}`)}
                            className="p-1.5 rounded-lg border border-neutral-200 hover:bg-neutral-100 text-neutral-700 transition-colors"
                          >
                            <Edit className="w-4 h-4" />
                          </button>

                          {/* 2. Invite to ESS Action */}
                          {!emp.authUserId && isActive && (
                            <button
                              type="button"
                              title="Invite to ESS"
                              onClick={() => handleOpenInvite(emp)}
                              className="p-1.5 rounded-lg border border-brand-200 bg-brand-50 hover:bg-brand-100 text-brand-700 transition-colors"
                            >
                              <UserPlus className="w-4 h-4" />
                            </button>
                          )}

                          {/* Reset Password Action for ESS Users */}
                          {emp.authUserId && isActive && (
                            <button
                              type="button"
                              title="Reset Password (OTP via Email)"
                              disabled={isProcessing}
                              onClick={() => handleAdminResetPassword(emp)}
                              className="p-1.5 rounded-lg border border-amber-200 bg-amber-50 hover:bg-amber-100 text-amber-700 transition-colors disabled:opacity-50"
                            >
                              <KeyRound className="w-4 h-4" />
                            </button>
                          )}

                          {/* 3. Active / Inactive Lifecycle Toggle Action */}
                          <button
                            type="button"
                            disabled={isProcessing}
                            title={isActive ? 'Deactivate Employee' : 'Reactivate Employee'}
                            onClick={() => handleToggleStatus(emp)}
                            className={`p-1.5 rounded-lg border transition-colors disabled:opacity-50 ${
                              isActive
                                ? 'border-red-200 bg-red-50 hover:bg-red-100 text-red-600'
                                : 'border-green-200 bg-green-50 hover:bg-green-100 text-green-700'
                            }`}
                          >
                            {isActive ? <XCircle className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
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
