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
    const response = await api.post('/miss-punch/', data);
    return response.data;
  },
  getMyRequests: async () => {
    const response = await api.get('/miss-punch/me');
    return response.data;
  },
  getPendingWorkflows: async () => {
    const response = await api.get('/workflows/pending');
    return response.data;
  },
  processWorkflowAction: async (workflowId: string, action: 'APPROVED' | 'REJECTED' | 'RETURNED', remarks?: string) => {
    const response = await api.post(`/workflows/${workflowId}/action`, { action, remarks });
    return response.data;
  }
};
