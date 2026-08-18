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
  
  publishPayslips: async (cycleId: string): Promise<any> => {
    return api.post<any>(`/payslips/publish/${cycleId}`);
  }
};

