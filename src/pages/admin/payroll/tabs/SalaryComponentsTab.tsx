import React from 'react';
import { GenericCRUDPage } from '../../../../components/ui';

export default function SalaryComponentsTab() {
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
}
