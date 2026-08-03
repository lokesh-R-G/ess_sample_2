// Types
export interface EmployeePersonalUI {
  firstName?: string;
  lastName?: string;
  middleName?: string;
  dob?: string;
  gender?: string;
  bloodGroup?: string;
  maritalStatus?: string;
  nationality?: string;
  religion?: string;
  [key: string]: any;
}

export interface EmployeeContactUI {
  workEmail?: string;
  mobilePhone?: string;
  personalEmail?: string;
  personalMobile?: string;
  emergencyContactName?: string;
  emergencyContactNumber?: string;
  emergencyContactRelation?: string;
  [key: string]: any;
}

export interface EmploymentHistoryUI {
  companyId?: string;
  branchId?: string;
  departmentId?: string;
  designationId?: string;
  effectiveFrom?: string;
  employmentType?: string;
  shiftId?: string;
  noticePeriodDays?: number;
  probationPeriodDays?: number;
  [key: string]: any;
}

export interface EmployeePayrollConfigUI {
  salaryStructureId?: string;
  monthlyGross?: number;
  pfOption?: string;
  esiOption?: string;
  ptState?: string;
  [key: string]: any;
}

// Mappers
export const contactMapper = {
  toBackend: (data: EmployeeContactUI) => {
    return {
      ...data,
      officialEmail: data.workEmail,
      officialMobile: data.mobilePhone,
      workEmail: undefined,
      mobilePhone: undefined
    };
  },
  fromBackend: (data: any): EmployeeContactUI => {
    if (!data) return {};
    return {
      ...data,
      workEmail: data.officialEmail || '',
      mobilePhone: data.officialMobile || '',
      officialEmail: undefined,
      officialMobile: undefined
    };
  }
};

export const employmentMapper = {
  toBackend: (data: EmploymentHistoryUI) => {
    return {
      ...data,
      dateOfJoining: data.effectiveFrom,
      effectiveFrom: data.effectiveFrom, // Preserve as versioning field
    };
  },
  fromBackend: (data: any): EmploymentHistoryUI => {
    if (!data) return {};
    return {
      ...data,
      effectiveFrom: data.effectiveFrom || data.dateOfJoining || '',
    };
  }
};

export const payrollConfigMapper = {
  toBackend: (data: EmployeePayrollConfigUI) => {
    let pfEnabled = true;
    let wantsPf = true;
    let pfCalculationMethod = 'Default';
    
    if (data.pfOption === 'OptOut') {
      wantsPf = false;
    } else if (data.pfOption === 'Ceiling') {
      pfCalculationMethod = 'Ceiling';
    } else if (data.pfOption === 'Actual') {
      pfCalculationMethod = 'Actual';
    }
    
    let esiEnabled = true;
    if (data.esiOption === 'PhysicalDisability') {
      esiEnabled = false; 
    }
    
    return {
      ...data,
      pfEnabled,
      wantsPf,
      pfCalculationMethod,
      esiEnabled,
      ptState: data.ptState === 'None' ? null : (data.ptState || null),
      pfOption: undefined,
      esiOption: undefined
    };
  },
  fromBackend: (data: any): EmployeePayrollConfigUI => {
    if (!data) return {};
    let pfOption = 'Default';
    if (!data.wantsPf) {
      pfOption = 'OptOut';
    } else if (data.pfCalculationMethod === 'Ceiling') {
      pfOption = 'Ceiling';
    } else if (data.pfCalculationMethod === 'Actual') {
      pfOption = 'Actual';
    }

    let esiOption = 'Default';
    if (!data.esiEnabled) {
      esiOption = 'PhysicalDisability';
    }

    return {
      ...data,
      pfOption,
      esiOption,
      ptState: data.ptState || 'None',
      pfEnabled: undefined,
      wantsPf: undefined,
      pfCalculationMethod: undefined,
      esiEnabled: undefined
    };
  }
};
