import { api } from '../lib/api';

export interface TripSheetRequest {
  tripDate: string;
  fromLocation: string;
  toLocation: string;
  tripType: string;
  startOdometer: number;
  endOdometer: number;
  claimedDistance: number;
  description: string;
  attachmentIds: string[];
}

export interface ReimbursementClaimResponse {
  id: string;
  employeeId: string;
  companyId: string;
  claimType: string;
  description: string;
  status: string;
  calculatedAmount: number;
  approvedAmount: number;
  hodStatus: string | null;
  hodRejectionReason: string | null;
  accountsStatus: string | null;
  accountsRejectionReason: string | null;
  createdAt: string;
  tripSheet?: any;
  attachments: any[];
}

export const reimbursementApi = {
  getMyClaims: async (): Promise<ReimbursementClaimResponse[]> => {
    return await api.get<ReimbursementClaimResponse[]>('/v2/reimbursement/my-claims');
  },
  submitTripSheet: async (data: TripSheetRequest) => {
    return await api.post('/v2/reimbursement/trip-sheet', data);
  },
  getPendingHodClaims: async (): Promise<ReimbursementClaimResponse[]> => {
    return await api.get<ReimbursementClaimResponse[]>('/v2/reimbursement/approvals/pending');
  },
  processHodAction: async (claimId: string, action: 'APPROVE' | 'REJECT', reason?: string) => {
    return await api.post(`/v2/reimbursement/approvals/${claimId}/action`, { action, reason });
  },
  getPendingAccountsClaims: async (): Promise<ReimbursementClaimResponse[]> => {
    return await api.get<ReimbursementClaimResponse[]>('/v2/reimbursement/accounts/pending');
  },
  processAccountsAction: async (claimId: string, action: 'APPROVE' | 'REJECT', reason?: string) => {
    return await api.post(`/v2/reimbursement/accounts/${claimId}/action`, { action, reason });
  },
  uploadAttachment: async (file: File): Promise<{id: string, fileName: string}> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = async () => {
        try {
          const base64String = (reader.result as string).split(',')[1];
          const res = await api.post<{id: string, fileName: string}>('/v2/reimbursement/upload-attachment', {
            fileName: file.name,
            mimeType: file.type,
            dataBase64: base64String
          });
          resolve(res);
        } catch (err) {
          reject(err);
        }
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  },
  
  // Admin: Trip Allowance Policy API
  getTripAllowancePolicies: async (companyId?: string) => {
    return await api.get('/v2/reimbursement-policy/trip-allowance' + (companyId ? `?companyId=${companyId}` : ''));
  },
  createTripAllowancePolicy: async (policyData: any) => {
    return await api.post('/v2/reimbursement-policy/trip-allowance', policyData);
  },
  updateTripAllowancePolicy: async (policyId: string, updateData: any) => {
    return await api.patch(`/v2/reimbursement-policy/trip-allowance/${policyId}`, updateData);
  }
};
