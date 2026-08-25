import { api } from '../lib/api';

export interface PayrollCycle {
  id: string;
  companyId: string;
  name: string;
  startDate: string;
  endDate: string;
  processingStatus: string;
}

export const payrollCycleApi = {
  getCycles: async (): Promise<PayrollCycle[]> => {
    return api.get<PayrollCycle[]>('/v2/payroll/cycles');
  },
  
  createCycle: async (data: any): Promise<PayrollCycle> => {
    return api.post<PayrollCycle>('/v2/payroll/cycles', data);
  },
  
  updateStatus: async (cycleId: string, status: string): Promise<PayrollCycle> => {
    return api.patch<PayrollCycle>(`/v2/payroll/cycles/${cycleId}/status`, { status });
  },

  calculatePayroll: async (cycleId: string): Promise<any> => {
    return api.post<any>(`/v2/payroll/cycles/${cycleId}/calculate`, {});
  },
  
  publishCycle: async (cycleId: string): Promise<any> => {
    return api.post<any>(`/v2/payroll/cycles/${cycleId}/publish`, {});
  },
  
  recalculateEmployee: async (cycleId: string, employeeId: string, reason: string): Promise<any> => {
    return api.post<any>(`/v2/payroll/cycles/${cycleId}/employees/${employeeId}/recalculate?reason=${reason}`);
  },

  exportCsv: async (cycleId: string): Promise<any> => {
    const res = await api.get<{csv: string}>(`/v2/payroll/cycles/${cycleId}/export/csv`);
    return res.csv;
  }
};
