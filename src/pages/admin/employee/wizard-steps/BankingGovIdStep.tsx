import React from 'react';
import { Input, Select } from '../../../../components/ui';

interface BankingGovIdStepProps {
  data: any;
  onChange: (data: any) => void;
  errors?: Record<string, string>;
}

export default function BankingGovIdStep({ data, onChange, errors = {} }: BankingGovIdStepProps) {
  const handleChange = (field: string, value: any) => {
    onChange({ ...data, [field]: value });
  };

  return (
    <div className="space-y-6">
      
      <div className="mb-8">
        <h3 className="text-lg font-bold text-neutral-900 mb-4">Banking Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input
            label="Name as per Bank"
            value={data.nameAsPerBank || ''}
            onChange={(e) => handleChange('nameAsPerBank', e.target.value)}
          />
          <Input
            label="Bank Name"
            value={data.bankName || ''}
            onChange={(e) => handleChange('bankName', e.target.value)}
          />
          <Input
            label="Branch Name"
            value={data.branchName || ''}
            onChange={(e) => handleChange('branchName', e.target.value)}
          />
          <Input
            label="Account Number"
            value={data.accountNumber || ''}
            onChange={(e) => handleChange('accountNumber', e.target.value)}
          />
          <Input
            label="IFSC Code"
            value={data.ifscCode || ''}
            onChange={(e) => handleChange('ifscCode', e.target.value)}
          />
          <Select
            label="Account Type"
            value={data.accountType || ''}
            onChange={(e) => handleChange('accountType', e.target.value)}
            options={[
              { value: '', label: 'Select Type' },
              { value: 'Savings', label: 'Savings' },
              { value: 'Current', label: 'Current' },
              { value: 'Salary', label: 'Salary' }
            ]}
          />
        </div>
      </div>

      <div className="border-t border-neutral-200 pt-6">
        <h3 className="text-lg font-bold text-neutral-900 mb-4">Government IDs</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input
            label="PAN Number"
            value={data.panNumber || ''}
            onChange={(e) => handleChange('panNumber', e.target.value)}
            error={errors.panNumber}
          />
          <Input
            label="Aadhar Number"
            value={data.aadharNumber || ''}
            onChange={(e) => handleChange('aadharNumber', e.target.value)}
            error={errors.aadharNumber}
          />
          <Input
            label="UAN Number (PF)"
            value={data.uanNumber || ''}
            onChange={(e) => handleChange('uanNumber', e.target.value)}
          />
          <Input
            label="ESI Number"
            value={data.esiNumber || ''}
            onChange={(e) => handleChange('esiNumber', e.target.value)}
          />
          <Input
            label="Passport Number"
            value={data.passportNumber || ''}
            onChange={(e) => handleChange('passportNumber', e.target.value)}
          />
        </div>
      </div>
      
    </div>
  );
}
