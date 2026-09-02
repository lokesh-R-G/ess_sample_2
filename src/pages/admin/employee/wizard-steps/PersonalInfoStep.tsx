import React from 'react';
import { Input, Select } from '../../../../components/ui';

interface PersonalInfoStepProps {
  data: any;
  onChange: (data: any) => void;
  errors?: Record<string, string>;
}

export default function PersonalInfoStep({ data, onChange, errors = {} }: PersonalInfoStepProps) {
  const handleChange = (field: string, value: any) => {
    onChange({ ...data, [field]: value });
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-bold text-neutral-900 mb-4">Personal Information</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="Employee Code (ESSL ID)"
          value={data.employeeCode || ''}
          onChange={(e) => handleChange('employeeCode', e.target.value)}
          error={errors.employeeCode}
          required
        />
        <Input
          label="First Name"
          value={data.firstName || ''}
          onChange={(e) => handleChange('firstName', e.target.value)}
          error={errors.firstName}
          required
        />
        <Input
          label="Last Name"
          value={data.lastName || ''}
          onChange={(e) => handleChange('lastName', e.target.value)}
          error={errors.lastName}
          required
        />
        <Input
          label="Date of Birth"
          type="date"
          value={data.dob || ''}
          onChange={(e) => handleChange('dob', e.target.value)}
          error={errors.dob}
          required
        />
        <Select
          label="Gender"
          value={data.gender || ''}
          onChange={(e) => handleChange('gender', e.target.value)}
          error={errors.gender}
          options={[
            { value: '', label: 'Select Gender' },
            { value: 'Male', label: 'Male' },
            { value: 'Female', label: 'Female' },
            { value: 'Other', label: 'Other' }
          ]}
          required
        />
        <Select
          label="Marital Status"
          value={data.maritalStatus || ''}
          onChange={(e) => handleChange('maritalStatus', e.target.value)}
          error={errors.maritalStatus}
          options={[
            { value: '', label: 'Select Status' },
            { value: 'Single', label: 'Single' },
            { value: 'Married', label: 'Married' },
            { value: 'Divorced', label: 'Divorced' },
            { value: 'Widowed', label: 'Widowed' }
          ]}
        />
        <Select
          label="Blood Group"
          value={data.bloodGroup || ''}
          onChange={(e) => handleChange('bloodGroup', e.target.value)}
          error={errors.bloodGroup}
          options={[
            { value: '', label: 'Select Blood Group' },
            { value: 'A+', label: 'A+' },
            { value: 'A-', label: 'A-' },
            { value: 'B+', label: 'B+' },
            { value: 'B-', label: 'B-' },
            { value: 'O+', label: 'O+' },
            { value: 'O-', label: 'O-' },
            { value: 'AB+', label: 'AB+' },
            { value: 'AB-', label: 'AB-' }
          ]}
        />
      </div>
    </div>
  );
}
