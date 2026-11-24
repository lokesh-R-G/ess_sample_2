import { api } from '../lib/api';

export interface SpecialDay {
  id?: string;
  _id?: string;
  specialDayId?: string;
  companyId?: string;
  eventName: string;
  date: string; // YYYY-MM-DD
  dayType: 'Sudden Holiday' | 'Sudden Cutoff';
  applicability: 'All Branches' | 'Selected Branches';
  selectedBranchIds: string[];
  selectedBranchNames?: string[];
  expectedWorkingHours?: number | null;
  reason?: string | null;
  status: 'Active' | 'Cancelled';
  createdBy?: string;
  createdAt?: string;
  updatedBy?: string;
  updatedAt?: string;
  cancelledBy?: string;
  cancelledAt?: string;
}

export interface SpecialDayPayload {
  eventName: string;
  date: string;
  dayType: 'Sudden Holiday' | 'Sudden Cutoff';
  applicability: 'All Branches' | 'Selected Branches';
  selectedBranchIds?: string[];
  expectedWorkingHours?: number | null;
  reason?: string | null;
}

export async function getSpecialDays(filters?: { date?: string; branchId?: string; status?: string; companyId?: string }) {
  const params = new URLSearchParams();
  if (filters?.date) params.append('date', filters.date);
  if (filters?.branchId) params.append('branchId', filters.branchId);
  if (filters?.status) params.append('status', filters.status);
  if (filters?.companyId) params.append('companyId', filters.companyId);

  const queryStr = params.toString() ? `?${params.toString()}` : '';
  const res = await api.get<any>(`/v2/holiday/special-days/${queryStr}`);
  return res?.data || res || [];
}

export async function createSpecialDay(data: SpecialDayPayload, companyId?: string) {
  const queryStr = companyId ? `?companyId=${encodeURIComponent(companyId)}` : '';
  return api.post<SpecialDay>(`/v2/holiday/special-days/${queryStr}`, data);
}

export async function updateSpecialDay(id: string, data: Partial<SpecialDayPayload> & { status?: string }) {
  return api.put<SpecialDay>(`/v2/holiday/special-days/${id}`, data);
}

export async function cancelSpecialDay(id: string) {
  return api.post<SpecialDay>(`/v2/holiday/special-days/${id}/cancel`, {});
}
