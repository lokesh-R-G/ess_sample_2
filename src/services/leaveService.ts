import { api } from '../lib/api';

export interface LeaveBalanceItem { total: number; used: number; balance: number; }

export interface LeaveApplication {
  id?: string;
  _id?: string;
  empId: string;
  requestType: 'leave' | 'od';
  leaveType?: string;
  fromDate: string;
  toDate: string;
  reason: string;
  odLocation?: string;
  status: 'approved' | 'pending' | 'rejected';
  appliedOn: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface LeaveResponse {
  leaveBalance: Record<string, LeaveBalanceItem>;
  requests: LeaveApplication[];
  leaveAnalysisData: number[];
}

export async function getLeaveData() {
  return api.get<LeaveResponse>('/leave/me');
}

export async function createLeaveRequest(payload: {
  requestType: 'leave' | 'od';
  leaveType: string;
  fromDate: string;
  toDate: string;
  reason: string;
  odLocation: string;
}) {
  return api.post<{ success: boolean }>('/leave/me', payload);
}
