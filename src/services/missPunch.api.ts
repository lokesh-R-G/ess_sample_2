import { api } from '../lib/api';

export interface MissPunchRequest {
  id?: string;
  employeeId: string;
  attendanceDate: string;
  requestType: 'MISSING_IN' | 'MISSING_OUT';
  requestedTime: string;
  reason: string;
  workflowId?: string;
  status?: string;
  createdAt?: string;
}

export const missPunchApi = {
  createRequest: async (data: MissPunchRequest) => {
    const response = await api.post('/v1/miss-punch/', data);
    return (response as any).data;
  },
  getMyRequests: async () => {
    const response = await api.get('/v1/miss-punch/me/');
    return (response as any).data;
  },
  getPendingWorkflows: async () => {
    const response = await api.get('/v1/workflows/pending/');
    return (response as any).data;
  },
  processWorkflowAction: async (workflowId: string, action: 'APPROVED' | 'REJECTED' | 'RETURNED', remarks?: string) => {
    const response = await api.post(`/v1/workflows/${workflowId}/action/`, { action, remarks });
    return (response as any).data;
  }
};
