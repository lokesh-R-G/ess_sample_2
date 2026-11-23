import { api } from '../api/client';
import { ReimbursementClaim, AppNotification, AdminSummaryStats } from '../types/common';

export async function getMyReimbursements(): Promise<ReimbursementClaim[]> {
  return api.get<ReimbursementClaim[]>('/v1/reimbursements/my-claims/').catch(() => []);
}

export async function submitReimbursement(data: { category: string; title: string; amount: number; description?: string }): Promise<ReimbursementClaim> {
  return api.post<ReimbursementClaim>('/v1/reimbursements/claims/', data);
}

export async function getNotifications(): Promise<AppNotification[]> {
  return api.get<AppNotification[]>('/v1/notifications/').catch(() => []);
}

export async function getAdminSummary(): Promise<AdminSummaryStats> {
  return api.get<AdminSummaryStats>('/v2/admin/dashboard/summary/').catch(() => ({
    totalEmployees: 0,
    presentToday: 0,
    absentToday: 0,
    onLeaveToday: 0,
    pendingLeaveApprovals: 0,
    pendingReimbursements: 0,
  }));
}

export async function getAdminPendingLeaves(): Promise<any[]> {
  return api.get<any[]>('/v2/leave/pending-approvals/').catch(() => []);
}

export async function approveOrRejectLeave(id: string, action: 'APPROVE' | 'REJECT', remarks?: string): Promise<any> {
  return api.post(`/v2/leave/applications/${id}/action/`, { action, remarks });
}

export async function getAdminEmployees(): Promise<any[]> {
  return api.get<any[]>('/v2/employees/').catch(() => []);
}
