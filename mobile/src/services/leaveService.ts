import { api } from '../api/client';
import { LeaveBalanceItem, LeaveApplication, CreateLeaveRequest } from '../types/leave';

export async function getLeaveData(): Promise<{ balances: LeaveBalanceItem[]; applications: LeaveApplication[] }> {
  const [balances, applications] = await Promise.all([
    api.get<LeaveBalanceItem[]>('/v2/leave/my-balances/').catch(() => []),
    api.get<LeaveApplication[]>('/v2/leave/my-applications/').catch(() => [])
  ]);
  return { balances, applications };
}

export async function createLeaveRequest(data: CreateLeaveRequest): Promise<LeaveApplication> {
  return api.post<LeaveApplication>('/v2/leave/applications/', data);
}
