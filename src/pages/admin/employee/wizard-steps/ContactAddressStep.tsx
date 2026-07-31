import React from 'react';
import { Input, Select } from '../../../../components/ui';

interface ContactAddressStepProps {
  data: any;
  onChange: (data: any) => void;
  errors?: Record<string, string>;
}

export default function ContactAddressStep({ data, onChange, errors = {} }: ContactAddressStepProps) {
  const handleChange = (field: string, value: any) => {
    onChange({ ...data, [field]: value });
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-bold text-neutral-900 mb-4">Contact & Address</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="Work Email"
          type="email"
          value={data.workEmail || ''}
          onChange={(e) => handleChange('workEmail', e.target.value)}
          error={errors.workEmail}
          required
        />
        <Input
          label="Personal Email"
          type="email"
          value={data.personalEmail || ''}
          onChange={(e) => handleChange('personalEmail', e.target.value)}
          error={errors.personalEmail}
        />
        <Input
          label="Mobile Phone"
          type="tel"
          value={data.mobilePhone || ''}
          onChange={(e) => handleChange('mobilePhone', e.target.value)}
          error={errors.mobilePhone}
          required
        />
        <Input
          label="Emergency Contact Name"
          value={data.emergencyContactName || ''}
          onChange={(e) => handleChange('emergencyContactName', e.target.value)}
        />
        <Input
          label="Emergency Contact Number"
          type="tel"
          value={data.emergencyContactNumber || ''}
          onChange={(e) => handleChange('emergencyContactNumber', e.target.value)}
        />
        <Select
          label="Emergency Contact Relation"
          value={data.emergencyContactRelation || ''}
          onChange={(e) => handleChange('emergencyContactRelation', e.target.value)}
          options={[
            { value: '', label: 'Select Relation' },
            { value: 'Spouse', label: 'Spouse' },
            { value: 'Parent', label: 'Parent' },
            { value: 'Sibling', label: 'Sibling' },
            { value: 'Friend', label: 'Friend' }
          ]}
        />
      </div>

      <div className="mt-8 border-t border-neutral-200 pt-6">
        <h4 className="text-md font-bold text-neutral-800 mb-4">Current Address</h4>
        <div className="grid grid-cols-1 gap-6">
          <Input
            label="Street Address"
            value={data.currentAddressLine1 || ''}
            onChange={(e) => handleChange('currentAddressLine1', e.target.value)}
            error={errors.currentAddressLine1}
            required
          />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Input
              label="City"
              value={data.currentCity || ''}
              onChange={(e) => handleChange('currentCity', e.target.value)}
              error={errors.currentCity}
              required
            />
            <Input
              label="State"
              value={data.currentState || ''}
              onChange={(e) => handleChange('currentState', e.target.value)}
              error={errors.currentState}
              required
            />
            <Input
              label="Pincode"
              value={data.currentPincode || ''}
              onChange={(e) => handleChange('currentPincode', e.target.value)}
              error={errors.currentPincode}
              required
            />
          </div>
        </div>
      </div>
      
      <div className="mt-4 flex items-center space-x-2">
        <input 
          type="checkbox" 
          checked={data.sameAsCurrentAddress || false}
          onChange={(e) => handleChange('sameAsCurrentAddress', e.target.checked)}
          className="rounded border-neutral-300 text-brand-600 focus:ring-brand-500 w-4 h-4"
        />
        <span className="text-sm font-medium text-neutral-700">Permanent address is same as current address</span>
      </div>

      {!data.sameAsCurrentAddress && (
        <div className="mt-6">
          <h4 className="text-md font-bold text-neutral-800 mb-4">Permanent Address</h4>
          <div className="grid grid-cols-1 gap-6">
            <Input
              label="Street Address"
              value={data.permanentAddressLine1 || ''}
              onChange={(e) => handleChange('permanentAddressLine1', e.target.value)}
            />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Input
                label="City"
                value={data.permanentCity || ''}
                onChange={(e) => handleChange('permanentCity', e.target.value)}
              />
              <Input
                label="State"
                value={data.permanentState || ''}
                onChange={(e) => handleChange('permanentState', e.target.value)}
              />
              <Input
                label="Pincode"
                value={data.permanentPincode || ''}
                onChange={(e) => handleChange('permanentPincode', e.target.value)}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
