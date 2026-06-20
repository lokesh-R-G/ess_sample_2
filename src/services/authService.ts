import { api, clearAuthStorage, setAuthStorage } from '../lib/api';

export interface LoginResponse {
  accessToken: string;
  tokenType: string;
  empId: string;
  role: 'Employee' | 'Admin';
  firstLogin: boolean;
  mustChangePassword: boolean;
}

export interface UserProfile {
  empId: string;
  role: 'Employee' | 'Admin';
  firstLogin: boolean;
  name?: string;
  designation?: string;
  department?: string;
  branch?: string;
  email?: string;
  phone?: string;
  joiningDate?: string;
  employeeType?: string;
  reportingTo?: string;
  address?: string;
  bankDetails?: {
    bankName?: string;
    accountNumber?: string;
    ifscCode?: string;
  };
  emergencyContact?: {
    name?: string;
    relationship?: string;
    phone?: string;
  };
}

export async function login(empId: string, password: string) {
  const response = await api.post<LoginResponse>('/auth/login', { empId, password });
  setAuthStorage(response.accessToken, response);
  return response;
}

export async function changePassword(currentPassword: string, newPassword: string) {
  return api.post<{ success?: boolean }>('/auth/change-password', { currentPassword, newPassword });
}

export async function getCurrentUser() {
  return api.get<UserProfile>('/auth/me');
}

export async function getProfile() {
  return api.get<UserProfile>('/profile/me');
}

export async function updateProfile(data: any) {
  return api.put<UserProfile>('/profile/me', data);
}

export function logout() {
  clearAuthStorage();
}
