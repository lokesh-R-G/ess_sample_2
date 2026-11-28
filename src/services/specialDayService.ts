import { api } from '../lib/api';

export interface SpecialDay {
  id?: string;
  _id?: string;
  specialDayId?: string;
  scopeType?: 'GLOBAL' | 'SELECTED_COMPANIES' | 'SINGLE_COMPANY';
  companyId?: string | null;
  companyIds?: string[];
  companyNames?: string[];
  eventName: string;
  date: string; // YYYY-MM-DD
  dayType: 'Sudden Holiday' | 'Sudden Shift Change' | 'Sudden Cutoff';
  applicability: 'All Branches' | 'Selected Branches';
  selectedBranchIds: string[];
  selectedBranchNames?: string[];
  
  // Shift timing fields for Sudden Shift Change
  shiftId?: string | null;
  shiftCode?: string | null;
  startTime?: string | null;
  endTime?: string | null;
  expectedWorkingHours?: number | null;
  isCrossMidnight?: boolean;
  breakStartTime?: string | null;
  breakEndTime?: string | null;

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
  dayType: 'Sudden Holiday' | 'Sudden Shift Change' | 'Sudden Cutoff';
  scopeType?: 'GLOBAL' | 'SELECTED_COMPANIES' | 'SINGLE_COMPANY';
  companyId?: string | null;
  companyIds?: string[];
  applicability: 'All Branches' | 'Selected Branches';
  selectedBranchIds?: string[];
  shiftId?: string | null;
  shiftCode?: string | null;
  startTime?: string | null;
  endTime?: string | null;
  expectedWorkingHours?: number | null;
  isCrossMidnight?: boolean;
  breakStartTime?: string | null;
  breakEndTime?: string | null;
  reason?: string | null;
}

export async function getSpecialDays(filters?: { date?: string; branchId?: string; status?: string; companyId?: string; scopeType?: string }) {
  const params = new URLSearchParams();
  if (filters?.date) params.append('date', filters.date);
  if (filters?.branchId) params.append('branchId', filters.branchId);
  if (filters?.status) params.append('status', filters.status);
  if (filters?.companyId) params.append('companyId', filters.companyId);
  if (filters?.scopeType) params.append('scopeType', filters.scopeType);

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
