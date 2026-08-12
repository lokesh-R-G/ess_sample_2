import { api } from '../lib/api';

export interface LeaveBalanceItem { total: number; used: number; balance: number; }

export interface LeaveApplication {
  id?: string;
  _id?: string;
  employeeId: string;
  approvalType: 'Leave';
  requestData: {
    leaveType: string;
    fromDate: string;
    toDate: string;
    reason: string;
  };
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'CANCELLED';
  createdAt?: string;
}

export interface LeaveResponse {
  leaveBalance: Record<string, LeaveBalanceItem>;
  requests: LeaveApplication[];
  leaveAnalysisData: number[];
}

export async function getLeaveData() {
  // Fetch balances from new V2 endpoint
  const balancesRes = await api.get<Record<string, LeaveBalanceItem>>('/v2/leave/balances');
  
  // Fetch requests from V2 Approval inbox endpoint (employee requests)
  const allRequests = await api.get<LeaveApplication[]>('/v2/approval/inbox/employee/me');
  const requestsRes = allRequests.filter(r => r.approvalType === 'Leave');
  
  // Calculate analysis data (just a mock or derived from requests)
  const pendingCount = requestsRes.filter(r => r.status === 'PENDING').length;
  const approvedCount = requestsRes.filter(r => r.status === 'APPROVED').length;
  const rejectedCount = requestsRes.filter(r => r.status === 'REJECTED').length;
  
  return {
    leaveBalance: balancesRes,
    requests: requestsRes,
    leaveAnalysisData: [approvedCount, pendingCount, rejectedCount]
  };
}

export async function createLeaveRequest(payload: {
  requestType: 'leave' | 'od';
  leaveType: string;
  fromDate: string;
  toDate: string;
  reason: string;
  odLocation?: string;
}) {
  return api.post<{ _id: string }>('/v2/approval/', {
    approvalType: 'Leave',
    requestData: {
      leaveType: payload.leaveType,
      fromDate: payload.fromDate,
      toDate: payload.toDate,
      reason: payload.reason
    }
  });
}
