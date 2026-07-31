import React, { useEffect, useState } from 'react';
import { Input, Select } from '../../../../components/ui';
import { organizationApi } from '../../../../services/organization.api';

interface EmploymentStepProps {
  data: any;
  onChange: (data: any) => void;
  errors?: Record<string, string>;
}

export default function EmploymentStep({ data, onChange, errors = {} }: EmploymentStepProps) {
  const [companies, setCompanies] = useState<any[]>([]);
  const [branches, setBranches] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [designations, setDesignations] = useState<any[]>([]);
  const [shifts, setShifts] = useState<any[]>([]);

  useEffect(() => {
    fetchMasters();
  }, []);

  const fetchMasters = async () => {
    try {
      const [compRes, branchRes, deptRes, desigRes, shiftRes] = await Promise.all([
        organizationApi.getCompanies(),
        organizationApi.getBranches(),
        organizationApi.getDepartments(),
        organizationApi.getDesignations(),
        organizationApi.getShifts()
      ]);
      setCompanies(compRes.data);
      setBranches(branchRes.data);
      setDepartments(deptRes.data);
      setDesignations(desigRes.data);
      setShifts(shiftRes.data);
    } catch (e) {
      console.error("Failed to load organization masters", e);
    }
  };

  const handleChange = (field: string, value: any) => {
    onChange({ ...data, [field]: value });
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-bold text-neutral-900 mb-4">Organization & Employment</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Select
          label="Company"
          value={data.companyId || ''}
          onChange={(e) => handleChange('companyId', e.target.value)}
          error={errors.companyId}
          options={[
            { value: '', label: 'Select Company' },
            ...companies.map(c => ({ value: c._id || c.id, label: c.name }))
          ]}
          required
        />
        <Select
          label="Branch"
          value={data.branchId || ''}
          onChange={(e) => handleChange('branchId', e.target.value)}
          error={errors.branchId}
          options={[
            { value: '', label: 'Select Branch' },
            ...branches.filter(b => b.companyId === data.companyId).map(b => ({ value: b._id || b.id, label: b.name }))
          ]}
          required
        />
        <Select
          label="Department"
          value={data.departmentId || ''}
          onChange={(e) => handleChange('departmentId', e.target.value)}
          error={errors.departmentId}
          options={[
            { value: '', label: 'Select Department' },
            ...departments.filter(d => d.companyId === data.companyId).map(d => ({ value: d._id || d.id, label: d.name }))
          ]}
          required
        />
        <Select
          label="Designation"
          value={data.designationId || ''}
          onChange={(e) => handleChange('designationId', e.target.value)}
          error={errors.designationId}
          options={[
            { value: '', label: 'Select Designation' },
            ...designations.filter(d => d.departmentId === data.departmentId).map(d => ({ value: d._id || d.id, label: d.name }))
          ]}
          required
        />
        
        <Input
          label="Date of Joining"
          type="date"
          value={data.effectiveFrom || ''}
          onChange={(e) => handleChange('effectiveFrom', e.target.value)}
          error={errors.effectiveFrom}
          required
        />
        
        <Select
          label="Employment Type"
          value={data.employmentType || ''}
          onChange={(e) => handleChange('employmentType', e.target.value)}
          error={errors.employmentType}
          options={[
            { value: '', label: 'Select Type' },
            { value: 'Full-Time', label: 'Full-Time' },
            { value: 'Part-Time', label: 'Part-Time' },
            { value: 'Contract', label: 'Contract' },
            { value: 'Internship', label: 'Internship' }
          ]}
          required
        />
        
        <Select
          label="Shift Assignment"
          value={data.shiftId || ''}
          onChange={(e) => handleChange('shiftId', e.target.value)}
          options={[
            { value: '', label: 'Select Shift' },
            ...shifts.map(s => ({ value: s._id || s.id, label: s.name }))
          ]}
        />

        <Input
          label="Notice Period (Days)"
          type="number"
          value={data.noticePeriodDays || 30}
          onChange={(e) => handleChange('noticePeriodDays', Number(e.target.value))}
        />
        
        <Input
          label="Probation Period (Days)"
          type="number"
          value={data.probationPeriodDays || 90}
          onChange={(e) => handleChange('probationPeriodDays', Number(e.target.value))}
        />
      </div>
    </div>
  );
}
