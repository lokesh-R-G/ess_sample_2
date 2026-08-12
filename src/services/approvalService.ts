import { api, getStoredUser } from '../lib/api';

export interface PolicyLimits {
  permissionMinutes: number;
  permissionPerMonth: number;
  monthlyPermissionHours: number;
  permissionExcessCarryForward: boolean;
  permissionLopThresholdMinutes: number;
  permissionLopValue: number;
}

export interface PermissionLedger {
  employeeId: string;
  month: string;
  freeAllowanceMinutes: number;
  consumedMinutes: number;
  currentExcessMinutes: number;
  previousCarriedMinutes: number;
  accumulatedExcessMinutes: number;
  lopGenerated: number;
  remainingCarriedMinutes: number;
  policyLimits: PolicyLimits;
}

export interface ApprovalSubmitPayload {
  employeeId: string;
  reportingManagerEmployeeId?: string;
  approvalType: string;
  requestData: Record<string, any>;
  remarks?: string;
}

export interface ApprovalResponse {
  id: string;
  employeeId: string;
  employeeCode?: string;
  employeeName?: string;
  reportingManagerEmployeeId?: string;
  approvalType: string;
  status: string;
  requestData: Record<string, any>;
  remarks?: string;
  createdAt?: string;
  approvedAt?: string;
  approvedBy?: string;
}

export const approvalService = {
  getPermissionLedger: async (): Promise<PermissionLedger> => {
    return api.get<PermissionLedger>('/v2/attendance/permission-ledger/me');
  },

  submitApproval: async (payload: ApprovalSubmitPayload): Promise<ApprovalResponse> => {
    return api.post<ApprovalResponse>('/v2/approval/', payload);
  },

  getMyRequests: async (empId: string, status?: string): Promise<ApprovalResponse[]> => {
    const params = status ? `?status=${status}` : '';
    return api.get<ApprovalResponse[]>(`/v2/approval/inbox/employee/${empId}${params}`);
  },

  getManagerInbox: async (status?: string): Promise<ApprovalResponse[]> => {
    const params = status ? `?status=${status}` : '';
    return api.get<ApprovalResponse[]>(`/v2/approval/inbox/manager/me${params}`);
  },

  executeAction: async (approvalId: string, action: 'APPROVE' | 'REJECT' | 'CANCEL', remarks?: string): Promise<ApprovalResponse> => {
    const user = getStoredUser<{ employeeId?: string, empId?: string }>();
    const actedBy = user?.employeeId || user?.empId || 'unknown';
    return api.post<ApprovalResponse>(`/v2/approval/${approvalId}/action`, { action, remarks, actedBy });
  }
};
