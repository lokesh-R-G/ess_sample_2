import { api, setAuthToken, clearAuthStorage } from '../api/client';
import { LoginResponse, UserProfile } from '../types/auth';

export async function login(empId: string, password: string): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>('/v1/auth/login/', { empId, password });
  await setAuthToken(response.accessToken, response);
  return response;
}

export async function changePassword(currentPassword: string, newPassword: string): Promise<{ success?: boolean }> {
  return api.post<{ success?: boolean }>('/v1/auth/change-password/', { currentPassword, newPassword });
}

export async function getCurrentUser(): Promise<UserProfile> {
  return api.get<UserProfile>('/v1/auth/me/');
}

export async function getProfile(): Promise<UserProfile> {
  return api.get<UserProfile>('/v2/employees/me/profile/');
}

export async function updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
  return api.patch<UserProfile>('/v2/employees/me/profile/', data);
}

export async function logout(): Promise<void> {
  await clearAuthStorage();
}
