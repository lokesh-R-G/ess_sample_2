import { api } from '../lib/api';

export interface Branch {
  _id?: string;
  companyId?: string;
  name: string;
  code?: string;
  location?: string;
  holidayCalendarId?: string;
  weeklyOffPolicyId?: string;
  status?: string;
}

export async function getBranches() {
  return api.get<Branch[]>('/v2/organization/branches/');
}

export async function createBranch(branch: Branch) {
  return api.post<Branch>('/v2/organization/branches/', branch);
}

export async function updateBranch(id: string, branch: Branch) {
  return api.put<Branch>(`/v2/organization/branches/${id}`, branch);
}

export async function deleteBranch(id: string) {
  return api.delete(`/v2/organization/branches/${id}`);
}
