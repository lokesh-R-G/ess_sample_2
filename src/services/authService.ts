import { api, clearAuthStorage, setAuthStorage } from '../lib/api';

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

export interface UserProfile {
  personal: {
    employeeId?: string;
    employeeCode?: string;
    firstName?: string;
    lastName?: string;
    dob?: string;
    gender?: string;
    bloodGroup?: string;
    maritalStatus?: string;
  };
  contact: {
    mobilePhone?: string;
    personalEmail?: string;
    workEmail?: string;
  };
  address: {
    currentAddressLine1?: string;
    currentCity?: string;
    currentState?: string;
    currentCountry?: string;
    currentPincode?: string;
  };
  emergencyContact: {
    name?: string;
    relationship?: string;
    phone?: string;
  };
  bank: {
    bankName?: string;
    accountNumber?: string;
    ifscCode?: string;
    accountType?: string;
  };
  employment: {
    dateOfJoining?: string;
    organization?: string;
    branch?: string;
    department?: string;
    designation?: string;
    reportingManager?: string;
    employmentType?: string;
    status?: string;
  };
  permissions: {
    canEditMobile: boolean;
    canEditAddress: boolean;
    canEditBank: boolean;
    canEditEmergencyContact?: boolean;
    canEditEmployment?: boolean;
    [key: string]: boolean | string[] | undefined;
  };
  empId?: string;
  employeeId?: string;
  employeeCode?: string;
  role?: string;
  roleId?: string;
  firstLogin?: boolean;
}

export async function login(empId: string, password: string) {
  const response = await api.post<LoginResponse>('/v1/auth/login/', { empId, password });
  setAuthStorage(response.accessToken, response);
  return response;
}

export async function changePassword(currentPassword: string, newPassword: string) {
  return api.post<{ success?: boolean }>('/v1/auth/change-password/', { currentPassword, newPassword });
}

export async function getCurrentUser() {
  return api.get<UserProfile>('/v1/auth/me/');
}

export async function getProfile() {
  return api.get<UserProfile>('/v2/employees/me/profile/');
}

export async function updateProfile(data: any) {
  return api.patch<UserProfile>('/v2/employees/me/profile/', data);
}

export function logout() {
  clearAuthStorage();
}

export const authApi = {
  forgotPassword: (employeeCode: string, email: string) => 
    api.post<{ message: string }>('/v1/auth/forgot-password/', { employeeCode, email }),
    
  verifyResetOtp: (employeeCode: string, email: string, otp: string) =>
    api.post<{ message: string; resetToken: string }>('/v1/auth/verify-reset-otp/', { employeeCode, email, otp }),
    
  resetPassword: (employeeCode: string, resetToken: string, newPassword: string, confirmPassword: string) =>
    api.post<{ message: string }>('/v1/auth/reset-password/', { employeeCode, resetToken, newPassword, confirmPassword }),
};
