import { api } from '../lib/api';

export interface Payslip {
  id: string;
  employeeId: string;
  cycleId: string;
  payrollId: string;
  generatedDate: string;
  status: string;
  payloadSnapshot: any;
}

export const payslipService = {
  getMyPayslip: async (year: number, month: number): Promise<any> => {
    return api.get<any>(`/payslips/me/${year}/${month}`);
  },
  
  getEarningsPreview: async (from: string, to: string): Promise<any> => {
    return api.get<any>(`/v2/payroll/preview?from=${from}&to=${to}`);
  },

  calculateCycle: async (cycleId: string): Promise<any> => {
    return api.post<any>(`/v2/payroll/cycles/${cycleId}/calculate`);
  },

  publishPayslips: async (cycleId: string): Promise<any> => {
    return api.post<any>(`/v2/payroll/cycles/${cycleId}/publish`);
  }
};

