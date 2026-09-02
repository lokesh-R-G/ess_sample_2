import React, { useState } from 'react';
import { GenericCRUDPage } from '../../components/ui/GenericCRUDPage';
import { AdminShifts } from './AdminShifts';
import { AdminHolidays } from './AdminHolidays';
export const AdminOrganization: React.FC = () => {
  const [activeTab, setActiveTab] = useState('Organization');

  const tabs = [
    'Organization', 'Company', 'Branch', 'Department', 'Designation',
    'Shift', 'Holiday', 'eSSL Machine', 'Salary Component', 'Salary Structure'
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'Company':
        return (
          <GenericCRUDPage
            title="Companies"
            endpoint="/v2/organization/companies/"
            columns={[
              { key: 'code', label: 'Company Code' },
              { key: 'name', label: 'Company Name' },
              { key: 'status', label: 'Status' }
            ]}
            formFields={[
              { key: 'code', label: 'Company Code', type: 'text', required: true },
              { key: 'name', label: 'Company Name', type: 'text', required: true }
            ]}
          />
        );
      case 'Branch':
        return (
          <GenericCRUDPage
            title="Branches"
            endpoint="/v2/organization/branches/"
            columns={[
              { key: 'companyId', label: 'Company', labelField: 'companyName' },
              { key: 'code', label: 'Branch Code' },
              { key: 'name', label: 'Branch Name' },
              { key: 'esslMachineId', label: 'eSSL Machine', render: (val, row) => row.esslMachine?.serialNumber || val || '-' }
            ]}
            formFields={[
              { key: 'companyId', label: 'Company', type: 'lookup', entity: 'Company', required: true },
              { key: 'code', label: 'Branch Code', type: 'text', required: true },
              { key: 'name', label: 'Branch Name', type: 'text', required: true },
              { key: 'address', label: 'Address', type: 'text' },
              { key: 'city', label: 'City', type: 'text' },
              { key: 'state', label: 'State', type: 'text' },
              { key: 'country', label: 'Country', type: 'text' },
              { key: 'pincode', label: 'Pincode', type: 'text' },
              { key: 'esslMachineId', label: 'eSSL Machine (optional)', type: 'essl-machine' },
              { key: 'attendanceEnabled', label: 'Attendance Enabled', type: 'checkbox' }
            ]}
          />
        );
      case 'Department':
        return (
          <GenericCRUDPage
            title="Departments"
            endpoint="/v2/organization/departments/"
            columns={[
              { key: 'companyId', label: 'Company', labelField: 'companyName' },
              { key: 'code', label: 'Department Code' },
              { key: 'name', label: 'Department Name' }
            ]}
            formFields={[
              { key: 'companyId', label: 'Company', type: 'lookup', entity: 'Company', required: true },
              { key: 'code', label: 'Department Code', type: 'text', required: true },
              { key: 'name', label: 'Department Name', type: 'text', required: true }
            ]}
          />
        );
      case 'Designation':
        return (
          <GenericCRUDPage
            title="Designations"
            endpoint="/v2/organization/designations/"
            columns={[
              { key: 'departmentId', label: 'Department', labelField: 'departmentName' },
              { key: 'code', label: 'Designation Code' },
              { key: 'name', label: 'Designation Name' }
            ]}
            formFields={[
              { key: 'companyId', label: 'Company', type: 'lookup', entity: 'Company', required: true },
              { key: 'departmentId', label: 'Department', type: 'lookup', entity: 'Department', required: true },
              { key: 'code', label: 'Designation Code', type: 'text', required: true },
              { key: 'name', label: 'Designation Name', type: 'text', required: true }
            ]}
          />
        );
      case 'Shift':
        return <AdminShifts />;
      case 'Holiday':
        return <AdminHolidays />;
      case 'eSSL Machine':
        return (
          <GenericCRUDPage
            title="eSSL Machines"
            endpoint="/v2/organization/essl-machines/"
            columns={[
              { key: 'serialNumber', label: 'Serial Number' },
              { key: 'ipAddress', label: 'IP Address' },
              { key: 'status', label: 'Status' }
            ]}
            formFields={[
              { key: 'serialNumber', label: 'Serial Number', type: 'text', required: true },
              { key: 'ipAddress', label: 'IP Address', type: 'text' },
              { key: 'status', label: 'Status', type: 'select', options: [
                { value: 'Active', label: 'Active' },
                { value: 'Offline', label: 'Offline' },
                { value: 'Maintenance', label: 'Maintenance' }
              ], required: true }
            ]}
          />
        );
      case 'Salary Component':
        return (
          <GenericCRUDPage
            title="Salary Components"
            endpoint="/v2/organization/salary-components/"
            columns={[
              { key: 'name', label: 'Component Name' },
              { key: 'componentType', label: 'Type' },
              { key: 'calculationMethod', label: 'Method' }
            ]}
            formFields={[
              { key: 'name', label: 'Component Name', type: 'text', required: true },
              { key: 'componentType', label: 'Type', type: 'select', options: [
                { value: 'Earning', label: 'Earning' },
                { value: 'Deduction', label: 'Deduction' }
              ], required: true },
              { key: 'calculationMethod', label: 'Calculation Method', type: 'select', options: [
                { value: 'Flat', label: 'Flat' },
                { value: 'Percentage', label: 'Percentage' },
                { value: 'Formula', label: 'Formula' }
              ], required: true },
              { key: 'percentageValue', label: 'Percentage Value (%)', type: 'number' },
              { key: 'percentageDerivedFromComponentId', label: 'Derived From Component', type: 'lookup', entity: 'SalaryComponent' },
              { key: 'isBasicComponent', label: 'Is Basic Component', type: 'checkbox' },
              { key: 'isTaxable', label: 'Taxable', type: 'checkbox' },
              { key: 'pfApplicable', label: 'PF Applicable', type: 'checkbox' },
              { key: 'esiApplicable', label: 'ESI Applicable', type: 'checkbox' }
            ]}
          />
        );
      case 'Salary Structure':
        return (
          <GenericCRUDPage
            title="Salary Structures"
            endpoint="/v2/organization/salary-structures/"
            columns={[
              { key: 'name', label: 'Structure Name' },
              { key: 'description', label: 'Description' },
              {
                key: 'components',
                label: 'Components',
                render: (val, row) => {
                  const comps = row.components || [];
                  if (comps.length === 0) return <span className="text-neutral-400 text-xs">None</span>;
                  return (
                    <span className="text-xs text-neutral-700">
                      {comps.slice(0, 2).map((c: any) => c.name).join(', ')}
                      {comps.length > 2 ? ` +${comps.length - 2} more` : ''}
                    </span>
                  );
                }
              }
            ]}
            formFields={[
              { key: 'name', label: 'Structure Name', type: 'text', required: true },
              { key: 'description', label: 'Description', type: 'text' },
              { key: 'componentIds', label: 'Salary Components', type: 'component-multiselect' }
            ]}
          />
        );
      case 'Organization':
      default:
        return (
          <GenericCRUDPage
            title="Organizations"
            endpoint="/v2/organization/organizations/"
            columns={[
              { key: 'name', label: 'Organization Name' },
              { key: 'domain', label: 'Domain' }
            ]}
            formFields={[
              { key: 'name', label: 'Organization Name', type: 'text', required: true },
              { key: 'domain', label: 'Domain', type: 'text', required: true }
            ]}
          />
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex space-x-2 overflow-x-auto pb-2 border-b border-neutral-200">
        {tabs.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              activeTab === tab ? 'bg-primary-500 text-white' : 'text-neutral-600 hover:bg-neutral-100'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>
      <div>
        {renderTabContent()}
      </div>
    </div>
  );
};

export default AdminOrganization;
