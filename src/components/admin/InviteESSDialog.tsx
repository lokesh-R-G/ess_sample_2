import React, { useState, useEffect } from 'react';
import { Modal, Input, Select, AnimatedButton } from '../ui';
import { api } from '../../lib/api';
import { toast } from 'react-hot-toast';

export interface DirectoryEmployee {
  employeeId: string;
  employeeCode?: string | null;
  firstName?: string;
  lastName?: string;
  personalEmail?: string | null;
  companyId?: string;
  companyName?: string;
  departmentId?: string;
  departmentName?: string;
  designationId?: string;
  designationName?: string;
  essStatus?: string;
  authUserId?: string | null;
}

interface InviteESSDialogProps {
  employee: DirectoryEmployee | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface FormState {
  employeeCode: string;
  email: string;
  role: 'Employee' | 'Manager' | 'Admin';
}

interface FormErrors {
  employeeCode?: string;
  email?: string;
}

const ROLE_OPTIONS = [
  { value: 'Employee', label: 'Employee' },
  { value: 'Manager', label: 'Manager' },
  { value: 'Admin', label: 'Administrator' },
];

export const InviteESSDialog: React.FC<InviteESSDialogProps> = ({
  employee,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [form, setForm] = useState<FormState>({
    employeeCode: '',
    email: '',
    role: 'Employee',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);

  // Pre-populate fields from the employee record when the dialog opens
  useEffect(() => {
    if (employee && isOpen) {
      setForm({
        employeeCode: employee.employeeCode || '',
        email: employee.personalEmail || '',
        role: 'Employee',
      });
      setErrors({});
    }
  }, [employee, isOpen]);

  const employeeName = employee
    ? `${employee.firstName || ''} ${employee.lastName || ''}`.trim() || 'Unknown'
    : '';

  // Employee Code is read-only once it has already been assigned
  const isCodeLocked = Boolean(employee?.employeeCode);

  const validate = (): boolean => {
    const newErrors: FormErrors = {};
    if (!form.employeeCode.trim()) {
      newErrors.employeeCode = 'Employee Code is required';
    }
    if (!form.email.trim()) {
      newErrors.email = 'Personal email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!employee || !validate()) return;
    setLoading(true);
    try {
      await api.post('/v1/admin/invite-employee/', {
        employeeId: employee.employeeId,
        employeeCode: form.employeeCode.trim(),
        email: form.email.trim().toLowerCase(),
        role: form.role,
      });
      toast.success(`ESS invitation sent to ${employeeName}`);
      onSuccess();
      onClose();
    } catch (e: any) {
      const detail = e?.response?.data?.detail || e?.message || 'Failed to invite employee';
      toast.error(detail);
    } finally {
      setLoading(false);
    }
  };

  if (!employee) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Invite to ESS"
    >
      <div className="space-y-5 px-1">

        {/* Employee Information (read-only) */}
        <div className="bg-neutral-50 border border-neutral-200 rounded-xl p-4 space-y-1">
          <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2">Employee Information</p>
          <p className="text-sm font-semibold text-neutral-900">{employeeName}</p>
          <p className="text-xs text-neutral-500 font-mono">{employee.employeeId}</p>
          
          <div className="mt-3 pt-3 border-t border-neutral-200 grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-neutral-500 text-xs uppercase">Company</span>
              <p className="font-medium">{employee.companyName || 'Not Assigned'}</p>
            </div>
            <div>
              <span className="text-neutral-500 text-xs uppercase">Department</span>
              <p className="font-medium">{employee.departmentName || 'Not Assigned'}</p>
            </div>
            <div className="col-span-2 mt-1">
              <span className="text-neutral-500 text-xs uppercase">Designation</span>
              <p className="font-medium">{employee.designationName || 'Not Assigned'}</p>
            </div>
          </div>
        </div>

        {/* Identity Section */}
        <div className="space-y-3">
          <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">Identity</p>

          <div>
            <Input
              id="invite-employee-code"
              label="Employee Code"
              value={form.employeeCode}
              onChange={(e) => {
                if (!isCodeLocked) {
                  setForm({ ...form, employeeCode: e.target.value });
                  if (errors.employeeCode) setErrors({ ...errors, employeeCode: undefined });
                }
              }}
              placeholder="e.g. EMP000123"
              disabled={isCodeLocked}
            />
            {isCodeLocked && (
              <p className="text-xs text-neutral-400 mt-1">
                🔒 Employee Code is locked after assignment
              </p>
            )}
            {errors.employeeCode && (
              <p className="text-xs text-red-500 mt-1">{errors.employeeCode}</p>
            )}
          </div>

          <div>
            <Input
              id="invite-username"
              label="Username"
              value={form.employeeCode || '—'}
              disabled
              placeholder="Auto-set to Employee Code"
            />
            <p className="text-xs text-neutral-400 mt-1">Username is automatically set to the Employee Code</p>
          </div>
        </div>

        {/* Contact Section */}
        <div className="space-y-3">
          <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">Contact</p>
          <div>
            <Input
              id="invite-email"
              label="Personal Email"
              type="email"
              value={form.email}
              onChange={(e) => {
                setForm({ ...form, email: e.target.value });
                if (errors.email) setErrors({ ...errors, email: undefined });
              }}
              placeholder="employee@example.com"
            />
            {errors.email && (
              <p className="text-xs text-red-500 mt-1">{errors.email}</p>
            )}
            <p className="text-xs text-neutral-400 mt-1">
              Welcome email with temporary password will be sent here
            </p>
          </div>
        </div>

        {/* Role Section */}
        <Select
          id="invite-role"
          label="System Role"
          options={ROLE_OPTIONS}
          value={form.role}
          onChange={(e) => setForm({ ...form, role: e.target.value as FormState['role'] })}
        />

        {/* Security notice */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800">
          🔐 A cryptographically secure temporary password will be generated by the server and sent to the employee's email. The employee must change it on first login.
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-2 border-t border-neutral-100">
          <AnimatedButton variant="secondary" onClick={onClose} disabled={loading}>
            Cancel
          </AnimatedButton>
          <AnimatedButton
            id="invite-submit"
            onClick={handleSubmit}
            loading={loading}
            disabled={!form.employeeCode || !form.email}
          >
            Send Invitation
          </AnimatedButton>
        </div>
      </div>
    </Modal>
  );
};

export default InviteESSDialog;
