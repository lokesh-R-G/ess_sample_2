export interface LoginResponse {
  accessToken: string;
  tokenType: string;
  empId: string;
  employeeId?: string | null;
  employeeCode?: string | null;
  role: 'Employee' | 'Admin';
  firstLogin: boolean;
  mustChangePassword: boolean;
}

export interface UserPermissions {
  canEditMobile?: boolean;
  canEditAddress?: boolean;
  canEditBank?: boolean;
  canEditEmergencyContact?: boolean;
  canEditEmployment?: boolean;
  [key: string]: boolean | string[] | undefined;
}

export interface UserProfile {
  personal?: {
    employeeId?: string;
    employeeCode?: string;
    firstName?: string;
    lastName?: string;
    dob?: string;
    gender?: string;
    bloodGroup?: string;
    maritalStatus?: string;
  };
  contact?: {
    mobilePhone?: string;
    personalEmail?: string;
    workEmail?: string;
  };
  address?: {
    currentAddressLine1?: string;
    currentCity?: string;
    currentState?: string;
    currentCountry?: string;
    currentPincode?: string;
  };
  emergencyContact?: {
    name?: string;
    relationship?: string;
    phone?: string;
  };
  bank?: {
    bankName?: string;
    accountNumber?: string;
    ifscCode?: string;
    accountType?: string;
  };
  employment?: {
    dateOfJoining?: string;
    organization?: string;
    branch?: string;
    department?: string;
    designation?: string;
    reportingManager?: string;
    employmentType?: string;
    status?: string;
  };
  permissions?: UserPermissions;
  empId?: string;
  employeeId?: string;
  employeeCode?: string;
  role?: string;
  roleId?: string;
  firstLogin?: boolean;
}
