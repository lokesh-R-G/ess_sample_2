import { api } from '../lib/api';

export interface PayrollRecord {
  _id: string;
  cycleId: string;
  employeeId: string;
  employeeCode?: string;
  employeeName?: string;
  grossEarnings: number;
  grossDeductions: number;
  netPay: number;
  status: string;
  version: number;
  isActive: boolean;
  previousVersionId?: string;
  recalculatedBy?: string;
  recalculationReason?: string;
  payloadSnapshot: any;
}

export const payrollReviewApi = {
  getPayrollsForCycle: async (cycleId: string, companyId?: string): Promise<PayrollRecord[]> => {
    const params = companyId ? `?companyId=${encodeURIComponent(companyId)}` : '';
    return api.get<PayrollRecord[]>(`/v2/payroll/cycles/${cycleId}/payrolls${params}`);
  }
};
